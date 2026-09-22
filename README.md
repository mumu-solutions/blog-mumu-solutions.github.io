# Blog MUMU Solutions

Blog estático servido via GitHub Pages em [blog.mumu.solutions](https://blog.mumu.solutions).
Markdown na fonte, HTML no destino, sem build step no cliente, sem dependências. Mesmo
espírito do site institucional ([mumu-solutions.github.io](https://github.com/mumu-solutions/mumu-solutions.github.io)),
adaptado para múltiplas páginas — ver `.specify/` para o porquê de cada decisão.

## Escrever um post

```
posts/<ano>/<mês>/<slug>/
  index.pt.md    obrigatório — o português é a fonte
  index.en.md    opcional — sem ele, o post mostra um aviso em inglês
  images/        assets exclusivos deste post
```

Front matter mínimo em cada `.md`:

```
---
title: Título do post
date: AAAA-MM-DD
description: Uma frase para <meta description> e og:description.
tags: tag-um, tag-dois
image: /posts/<ano>/<mês>/<slug>/images/arquivo.png
---
```

Depois de escrever:

```bash
python3 build.py            # gera o(s) index.html
python3 build.py --check    # confere que o HTML commitado bate com a fonte — roda no CI
```

Suba `VERSION` no mesmo PR se o post é novo (MINOR) ou muda a URL de um post existente
(MAJOR) — ver a tabela na [constituição](.specify/constitution.md#artigo-vii--versionamento-e-publicação-automática).
Um push em `main` que muda `VERSION` cria e publica a tag `v<VERSION>` automaticamente.

## Governança

- [`.specify/constitution.md`](.specify/constitution.md) — regras não negociáveis.
- [`.specify/specs/`](.specify/specs) — o que este site é e não é.
- [`.specify/adr/`](.specify/adr) — por que cada decisão estrutural foi tomada.

## Layout

```
build.py            gerador Markdown -> HTML, stdlib only
blog.css / blog.js  chrome do site — externos de propósito, ver ADR 0003
VERSION              semver do site; fonte da tag automática
CNAME                domínio customizado (blog.mumu.solutions)
posts/                um post por pasta, ver ADR 0005
images/mumia/         favicons e assets de marca, copiados sob demanda de mumu-mumia
.github/workflows/deploy.yml   gate -> tag se VERSION mudou -> deploy
```

## Handoffs pendentes

- `blog.mumu.solutions` já está configurado no GitHub Pages deste repositório, mas
  aparece como domínio não verificado — falta o DNS apontar para ele (fora do escopo
  deste repositório).
