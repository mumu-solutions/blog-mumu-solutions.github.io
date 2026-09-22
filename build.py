#!/usr/bin/env python3
"""Blog generator. Stdlib only — no pip install, ever.

Reads posts/YYYY/MM/slug/index.{pt,en}.md, writes index.html next to each
source, and writes the blog homepage + sitemap.xml at the repo root.

    python3 build.py            rebuild everything
    python3 build.py --check    rebuild to a temp dir and diff against what
                                 is committed; exits 1 on any mismatch

See .specify/adr/0001-md-to-html-stdlib.md for why there is no dependency,
and 0002-committed-html-output.md for why --check exists at all.
"""
import argparse
import difflib
import filecmp
import html
import pathlib
import re
import shutil
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
SITE_URL = "https://blog.mumu.solutions"
SITE_NAME_PT = "Blog MUMU Solutions"
SITE_NAME_EN = "MUMU Solutions Blog"
LANGS = ("pt", "en")

CHROME = {
    "home": {"pt": "Início", "en": "Home"},
    "back_to_site": {"pt": "mumu.solutions", "en": "mumu.solutions"},
    "posts_title": {"pt": "Posts", "en": "Posts"},
    "read_more": {"pt": "Ler mais", "en": "Read more"},
    "theme_label": {"pt": "Alternar tema claro e escuro", "en": "Toggle light and dark theme"},
    "lang_label": {"pt": "Switch to English", "en": "Mudar para português"},
    "footer": {
        "pt": "MUMU Solutions — conteúdo publicado em Markdown, convertido para HTML por build.py.",
        "en": "MUMU Solutions — content published in Markdown, converted to HTML by build.py.",
    },
    "stub_notice": {
        "pt": "",
        "en": "This post is only available in Portuguese right now. Machine translation is "
        "deliberately not used — see the description above for the gist, or come back later.",
    },
}


# --------------------------------------------------------------------------- front matter

def parse_front_matter(text):
    """Minimal `key: value` front matter between --- fences. No nesting, no
    YAML types — a list is `tags: a, b, c`. This is deliberately not YAML;
    see the ADR for why."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing --- front matter block")
    raw, body = m.group(1), m.group(2)
    meta = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body.strip("\n")


# --------------------------------------------------------------------------- markdown -> html

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def png_dimensions(path):
    """Read width/height straight out of the IHDR chunk. PNG-only — it is
    the only format posts use; anything else just ships without a size
    attribute (a layout-shift warning, not a broken page)."""
    try:
        with open(path, "rb") as f:
            header = f.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n" or len(header) < 24:
            return None
        width, height = struct.unpack(">II", header[16:24])
        return width, height
    except OSError:
        return None


def render_inline(text, base_dir=None):
    text = html.escape(text, quote=False)

    def img_tag(m):
        alt, src = m.group(1), m.group(2)
        dims = ""
        if base_dir is not None and not re.match(r"^https?://|^/", src):
            wh = png_dimensions(base_dir / src)
            if wh:
                dims = f' width="{wh[0]}" height="{wh[1]}"'
        return f'<img src="{src}" alt="{alt}" loading="lazy"{dims}>'

    text = IMAGE.sub(img_tag, text)
    text = LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    text = ITALIC.sub(r"<em>\1</em>", text)
    text = INLINE_CODE.sub(r"<code>\1</code>", text)
    return text


def render_markdown(md, base_dir=None):
    """Supported subset: #/##/### headings, paragraphs, - / * / 1. lists
    (one level), > blockquotes, ``` fenced code, --- rules, and the inline
    forms above. Anything else passes through as an escaped paragraph."""
    lines = md.splitlines()
    out = []
    i = 0
    n = len(lines)

    def flush_list(buf, tag):
        if buf:
            out.append(f"<{tag}>")
            for item in buf:
                out.append(f"<li>{render_inline(item, base_dir)}</li>")
            out.append(f"</{tag}>")
            buf.clear()

    para = []

    def flush_para():
        if para:
            out.append(f"<p>{render_inline(' '.join(para), base_dir)}</p>")
            para.clear()

    while i < n:
        line = lines[i]

        if line.strip() == "":
            flush_para()
            i += 1
            continue

        if line.startswith("```"):
            flush_para()
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            code = html.escape("\n".join(code_lines))
            out.append(f"<pre><code{cls}>{code}</code></pre>")
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1)) + 1  # h1 reserved for the post title
            out.append(f"<h{level}>{render_inline(m.group(2), base_dir)}</h{level}>")
            i += 1
            continue

        if line.strip() == "---":
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        if line.startswith(">"):
            flush_para()
            quote_lines = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(lines[i].lstrip(">").strip())
                i += 1
            out.append(f"<blockquote><p>{render_inline(' '.join(quote_lines), base_dir)}</p></blockquote>")
            continue

        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            flush_para()
            buf = []
            while i < n and re.match(r"^[-*]\s+(.*)$", lines[i]):
                buf.append(re.match(r"^[-*]\s+(.*)$", lines[i]).group(1))
                i += 1
            flush_list(buf, "ul")
            continue

        m = re.match(r"^\d+\.\s+(.*)$", line)
        if m:
            flush_para()
            buf = []
            while i < n and re.match(r"^\d+\.\s+(.*)$", lines[i]):
                buf.append(re.match(r"^\d+\.\s+(.*)$", lines[i]).group(1))
                i += 1
            flush_list(buf, "ol")
            continue

        para.append(line.strip())
        i += 1

    flush_para()
    return "\n".join(out)


# --------------------------------------------------------------------------- templates

def page_shell(*, canonical, title, description, og_image, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark" data-language="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; base-uri 'self'; object-src 'none'; form-action 'self'; img-src 'self'; font-src 'self'; style-src 'self'; script-src 'self'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="author" content="MUMU Solutions">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="color-scheme" content="dark light">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/images/mumia/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/images/mumia/favicon-32x32.png">
<link rel="apple-touch-icon" href="/images/mumia/apple-touch-icon.png">
<link rel="stylesheet" href="/blog.css?v={VERSION}">
{extra_head}</head>
<body>
<header class="site-header">
  <div class="container header-row">
    <a class="brand" href="/">
      <img src="/images/mumia/favicon-32x32.png" alt="MUMia" width="28" height="28">
      <span data-lang="pt" class="on">{SITE_NAME_PT}</span>
      <span data-lang="en">{SITE_NAME_EN}</span>
    </a>
    <nav class="site-nav">
      <a href="https://mumu.solutions/"><span data-lang="pt" class="on">{CHROME['back_to_site']['pt']}</span><span data-lang="en">{CHROME['back_to_site']['en']}</span></a>
      <button type="button" class="icon-btn" id="themeBtn" aria-label="{CHROME['theme_label']['pt']}">◐</button>
      <button type="button" class="icon-btn" id="langBtn" aria-label="{CHROME['lang_label']['pt']}">PT/EN</button>
    </nav>
  </div>
</header>
<main class="container">
{body}
</main>
<footer class="site-footer">
  <div class="container">
    <p><span data-lang="pt" class="on">{CHROME['footer']['pt']}</span><span data-lang="en">{CHROME['footer']['en']}</span></p>
  </div>
</footer>
<script src="/blog.js?v={VERSION}"></script>
</body>
</html>
"""


def render_post_lang(meta, body_html, lang, is_stub):
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    tags_html = ""
    if tags:
        chips = "".join(f'<li class="tag">{html.escape(t)}</li>' for t in tags)
        tags_html = f'<ul class="tag-list">{chips}</ul>'
    stub_html = f'<p class="stub-notice">{CHROME["stub_notice"][lang]}</p>' if is_stub else ""
    cls = "on" if lang == "pt" else ""
    return f"""<article data-lang="{lang}" class="{cls}">
  <p class="post-date">{meta.get('date', '')}</p>
  <h1>{html.escape(meta.get('title', ''))}</h1>
  {tags_html}
  {stub_html}
  {body_html}
</article>"""


def build_post(post_dir):
    slug = post_dir.name
    pt_path = post_dir / "index.pt.md"
    en_path = post_dir / "index.en.md"
    if not pt_path.exists():
        raise SystemExit(f"{post_dir}: index.pt.md is required (PT is the source language)")

    pt_meta, pt_body_md = parse_front_matter(pt_path.read_text())
    pt_html = render_post_lang(pt_meta, render_markdown(pt_body_md, post_dir), "pt", is_stub=False)

    if en_path.exists():
        en_meta, en_body_md = parse_front_matter(en_path.read_text())
        en_html = render_post_lang(en_meta, render_markdown(en_body_md, post_dir), "en", is_stub=False)
        en_title = en_meta.get("title", pt_meta.get("title", ""))
        en_description = en_meta.get("description", pt_meta.get("description", ""))
    else:
        en_html = render_post_lang(pt_meta, "", "en", is_stub=True)
        en_title = pt_meta.get("title", "")
        en_description = pt_meta.get("description", "")

    rel = post_dir.relative_to(ROOT / "posts")
    canonical = f"{SITE_URL}/posts/{rel.as_posix()}/"
    image = pt_meta.get("image", "/images/mumia/social-light-white.png")
    og_image = image if image.startswith("http") else f"{SITE_URL}{image}"

    body = pt_html + "\n" + en_html
    out = page_shell(
        canonical=canonical,
        title=pt_meta.get("title", slug),
        description=pt_meta.get("description", ""),
        og_image=og_image,
        body=body,
    )
    (post_dir / "index.html").write_text(out)

    return {
        "slug": slug,
        "rel": rel.as_posix(),
        "date": pt_meta.get("date", ""),
        "title_pt": pt_meta.get("title", slug),
        "title_en": en_title or pt_meta.get("title", slug),
        "description_pt": pt_meta.get("description", ""),
        "description_en": en_description,
        "canonical": canonical,
    }


def build_index(posts):
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    items_pt = []
    items_en = []
    for p in posts_sorted:
        items_pt.append(
            f'<li class="post-card"><a href="/posts/{p["rel"]}/">'
            f'<span class="post-date">{p["date"]}</span>'
            f'<span class="post-title">{html.escape(p["title_pt"])}</span>'
            f'<span class="post-desc">{html.escape(p["description_pt"])}</span>'
            f'</a></li>'
        )
        items_en.append(
            f'<li class="post-card"><a href="/posts/{p["rel"]}/">'
            f'<span class="post-date">{p["date"]}</span>'
            f'<span class="post-title">{html.escape(p["title_en"])}</span>'
            f'<span class="post-desc">{html.escape(p["description_en"])}</span>'
            f'</a></li>'
        )
    body = f"""<section data-lang="pt" class="on">
  <h1>{CHROME['posts_title']['pt']}</h1>
  <ul class="post-list">{''.join(items_pt)}</ul>
</section>
<section data-lang="en">
  <h1>{CHROME['posts_title']['en']}</h1>
  <ul class="post-list">{''.join(items_en)}</ul>
</section>"""
    out = page_shell(
        canonical=f"{SITE_URL}/",
        title=SITE_NAME_PT,
        description="Posts da MUMU Solutions sobre tecnologia, automação e o mascote MUMia — em português e inglês.",
        og_image=f"{SITE_URL}/images/mumia/social-light-white.png",
        body=body,
    )
    (ROOT / "index.html").write_text(out)


def build_sitemap(posts):
    # lastmod comes from each post's own front-matter `date` — never wall-clock
    # `datetime.now()`, which would make two runs on different days disagree
    # about a page that did not change and break `--check`'s reproducibility.
    latest = max((p["date"] for p in posts), default="")
    entries = [f"  <url><loc>{SITE_URL}/</loc><lastmod>{latest}</lastmod></url>"]
    entries += [
        f'  <url><loc>{SITE_URL}/posts/{p["rel"]}/</loc><lastmod>{p["date"]}</lastmod></url>'
        for p in posts
    ]
    entries = "\n".join(entries)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml)


VERSION = (ROOT / "VERSION").read_text().strip()


def discover_posts():
    return sorted((ROOT / "posts").glob("*/*/*/"))


def build_all():
    """Returns (posts, written) — `written` is the exact set of post
    index.html paths this run produced, relative to ROOT. `check()` uses it
    to catch a stale generated file left behind by a deleted or renamed post
    bundle, which a plain content diff cannot see (an untouched file always
    matches itself)."""
    posts = [build_post(d) for d in discover_posts() if d.is_dir()]
    build_index(posts)
    build_sitemap(posts)
    written = {f'posts/{p["rel"]}/index.html' for p in posts}
    return posts, written


def check():
    """Rebuild into a temp copy of the tree and diff every generated file
    against what is committed. Fails loudly on any drift, including a
    leftover index.html whose source post was deleted or renamed."""
    global ROOT
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        shadow = tmp / "repo"
        shutil.copytree(ROOT, shadow, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        real_root = ROOT
        ROOT = shadow
        try:
            _, written = build_all()
        finally:
            ROOT = real_root

        mismatches = []
        for path in shadow.rglob("*"):
            if path.is_dir() or ".git" in path.parts:
                continue
            rel = path.relative_to(shadow)
            real = real_root / rel
            if not real.exists() or not filecmp.cmp(path, real, shallow=False):
                mismatches.append(rel.as_posix())

        on_disk = {
            p.relative_to(real_root).as_posix()
            for p in real_root.glob("posts/*/*/*/index.html")
        }
        orphans = sorted(on_disk - written)
        if orphans:
            print("orphaned post output — no source bundle produces these anymore:")
            for rel in orphans:
                print(f"  {rel}")
            mismatches.extend(orphans)

        if mismatches:
            print("build drift — committed HTML does not match `python3 build.py`:")
            for rel in mismatches:
                print(f"  {rel}")
                real = real_root / rel
                if real.exists() and (shadow / rel).exists() and real.suffix in (".html", ".xml"):
                    diff = difflib.unified_diff(
                        real.read_text().splitlines(keepends=True),
                        (shadow / rel).read_text().splitlines(keepends=True),
                        fromfile=f"committed/{rel}",
                        tofile=f"generated/{rel}",
                    )
                    sys.stdout.writelines(diff)
            return 1
        print("build.py --check: committed output matches the source. OK.")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        sys.exit(check())
    build_all()
    print("build.py: wrote index.html, sitemap.xml, and each post's index.html")
