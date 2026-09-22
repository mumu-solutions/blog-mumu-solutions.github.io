# Spec 0001 — Blog estático MUMU Solutions

Status: implementado · v1.0.0

## O quê

Um blog estático, servido via GitHub Pages em `blog.mumu.solutions`, com:

- Conteúdo escrito em Markdown, um post por pasta (`posts/<ano>/<mês>/<slug>/`).
- HTML gerado por `build.py` (stdlib Python) e commitado — sem build step no cliente,
  sem servidor.
- Página inicial (`index.html`) listando os posts, mais recente primeiro.
- Suporte bilíngue pt/en por post, com português como fonte obrigatória.
- Deploy automático em `main`, com uma tag semver criada quando `VERSION` muda.

## Por quê

A MUMU Solutions precisa de um canal de conteúdo simples de manter — sem CMS, sem
dependência de terceiros, alinhado ao mesmo padrão do site institucional
(`mumu-solutions.github.io`): estático, rápido, sem build tool, com CSP restritiva. O
mascote MUMia (`mumu-mumia`) é o primeiro assunto porque ele vai aparecer
recorrentemente no conteúdo futuro — faz sentido apresentá-lo primeiro.

## Fora de escopo (v1)

- Comentários, busca, paginação, RSS/Atom — adicionar quando houver posts suficientes
  para justificar.
- Categorias/tags como páginas navegáveis — as tags hoje são só rótulos visuais no post.
- CMS ou editor web — os posts são editados como arquivos, via PR.
- Analytics — decisão de produto separada; quando existir, seguir o padrão do site
  institucional (Cloudflare Web Analytics, sem cookies).

## Critérios de aceite

1. `python3 build.py` reconstrói `index.html`, `sitemap.xml` e o `index.html` de cada
   post a partir das fontes Markdown, sem erro.
2. `python3 build.py --check` falha (exit 1) se o HTML commitado divergir do que as
   fontes Markdown gerariam.
3. Toda página publicada tem CSP `default-src 'none'` com cada recurso nomeado, e
   nenhum `<style>`/`<script>` inline.
4. Todo texto de chrome (nav, rodapé) existe em `data-lang="pt"` e `data-lang="en"`; a
   versão pt está visível sem JavaScript.
5. Um push em `main` que mude `VERSION` produz, no máximo, uma tag `v<VERSION>` nova.

## Primeiro conteúdo

`posts/2026/09/mumu-mumia/` — apresentação do MUMia, mascote e agente da MUMU
Solutions, em pt e en, com a arte de `mumu-mumia` (dist/png/figure, license: mesmo repo).
