# Blog MUMU Solutions

Blog estático servido via GitHub Pages em [blog.mumu.solutions](https://blog.mumu.solutions).
Markdown na fonte, HTML no destino, sem build step no cliente, sem dependências. Mesmo
espírito do site institucional ([mumu-st-institucional](https://github.com/mumu-solutions/mumu-st-institucional)),
adaptado para múltiplas páginas — ver `.specify/` para o porquê de cada decisão.

## Como escrever e publicar um post novo

Um guia passo a passo para quem nunca escreveu um post aqui.

### 1. Crie a pasta do post

```
posts/<ano>/<mês>/<slug>/
  index.pt.md    obrigatório — o português é a fonte
  index.en.md    opcional — sem ele, o post mostra um aviso em inglês no lugar do texto
  images/        as imagens exclusivas deste post (PNG)
```

`<ano>/<mês>` é a data de publicação (ex.: `2026/09`). `<slug>` é curto, em minúsculas,
com hífen (ex.: `mumu-mumia`, não `Apresentando_o_Mumia`) — vira parte da URL.

### 2. Escreva o front matter + o texto

Todo `.md` começa com um bloco `---` no formato `chave: valor` (sem YAML de verdade —
uma lista é `tag-um, tag-dois`, sem colchetes):

```
---
title: Título do post
date: AAAA-MM-DD
description: Uma frase (50–160 caracteres) para a prévia em buscadores e redes sociais.
tags: tag-um, tag-dois
image: /posts/<ano>/<mês>/<slug>/images/arquivo.png
---

Texto do post em Markdown a partir daqui.
```

Markdown suportado: `#` para títulos de seção (o título do post já é o `<h1>`, então
comece do `#` mesmo — ele vira `<h2>`), parágrafos, `**negrito**`, `*itálico*`,
`` `código` ``, links `[texto](url)`, imagens `![alt](arquivo.png)`, listas com `-` ou
`1.`, `> citação`, blocos ` ``` `. Nada além disso — o gerador é deliberadamente simples
([ADR 0001](.specify/adr/0001-md-to-html-stdlib.md)); se faltar algo (tabela, nota de
rodapé), resolva com uma frase em vez de um recurso novo.

### 3. Escreva como o MUMia falaria

O blog é a voz do MUMia, o mascote da MUMU Solutions — tímido, curioso, especialista em
tecnologia, mas que explica tudo sem soar técnico ou arrogante. Ao escrever (mesmo que o
assunto não seja sobre ele diretamente):

- **Primeira pessoa e tom pessoal**, não um press release. "Eu reparei que..." em vez
  de "Foi observado que...".
- **Sem jargão técnico desnecessário.** Se o post não é sobre código, não precisa de
  termos de código. Explique como explicaria para alguém curioso mas não técnico.
- **Sem detalhes de implementação interna** — nomes de arquivo, de repositório, de
  configuração. Ninguém de fora precisa saber como o site é montado por trás; o post é
  sobre a ideia, não sobre a ferramenta.
- **Foco em personalidade e utilidade real**, não em anunciar uma feature. O que o
  leitor aprende ou resolve depois de ler?
- Curto é melhor que completo. Um post de 400–600 palavras que se lê inteiro vale mais
  que um de 2000 que ninguém termina.

### 4. Gere o HTML e confira

```bash
python3 build.py            # gera/atualiza index.html de cada post e a home
python3 build.py --check    # confere que o HTML commitado bate com a fonte — roda no CI
```

Rode os dois. `build.py` sozinho não é suficiente — commitar sem rodar `--check` depois
é o jeito mais comum de esquecer de regenerar algo.

### 5. Suba a versão

Edite `VERSION` no mesmo commit:

| Mudança | Bump |
|---|---|
| Post novo | MINOR (`1.0.0` → `1.1.0`) |
| Corrigir texto/typo num post existente, sem mudar a URL | PATCH (`1.1.0` → `1.1.1`) |
| Mudar a URL de um post existente (renomear pasta/slug) | MAJOR |

(Tabela completa: [constituição, Artigo VII](.specify/constitution.md#artigo-vii--versionamento-e-publicação-automática).)

### 6. Publique

Um push em `main` que muda `VERSION` para um valor ainda não tageado cria e publica a
tag `v<VERSION>` automaticamente, e o deploy sobe sozinho — não precisa criar a tag à
mão. Ver [ADR 0004](.specify/adr/0004-semver-tag-drives-publish.md).

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
