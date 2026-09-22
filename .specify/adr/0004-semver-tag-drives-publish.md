# ADR 0004 — `VERSION` dirige a tag semver e o auto-publish

Status: aceito · 2026-09-22

## Contexto

O pedido original é: "pode subir automaticamente na main desde que commite junto uma
tag com semver". `mumu-solutions.github.io` e `mumu-mumia` já usam git tags (`vX.Y.Z`)
como fonte da verdade de versão; este repo tem, adicionalmente, um arquivo `VERSION`
(como o site institucional) porque o build precisa ler o número em tempo de build para
o `?v=` do CSS/JS.

## Decisão

O workflow de deploy, em todo push em `main`:

1. Roda o gate (`build.py --check`, mais o auditor de site estático).
2. Lê `VERSION`.
3. Se a tag `v<VERSION>` **ainda não existe** no repositório remoto, cria e dá push
   nela.
4. Publica no GitHub Pages.

Um push que não muda `VERSION` faz deploy normalmente, sem criar tag nova — a tag
existente continua apontando para o commit em que a versão foi cravada, git tags não
"seguem" `main`.

## Por quê

- Satisfaz o pedido literal ("commite junto uma tag semver") sem exigir que quem abre o
  PR calcule e empurre a tag manualmente — isso viraria um passo esquecível.
- O guard "só cria se não existe" é obrigatório: sem ele, todo commit de copy/estilo que
  não mude `VERSION` tentaria recriar `v1.0.0` e falharia o workflow inteiro.
- Reaproveita a tabela MAJOR/MINOR/PATCH da constituição (Artigo VII) em vez de inventar
  uma nova — a única mudança em relação ao site institucional é o que conta como
  "contrato público": lá é `<section id>`, aqui é URL de post.

## Consequências

- Quem sobe um post novo (ou corrige um antigo de um jeito que muda a URL) precisa
  lembrar de editar `VERSION` no mesmo PR — não há automação que decida o número por
  eles; é uma decisão humana, documentada na constituição.
- O workflow precisa de `contents: write` (para a tag) além de `pages: write` /
  `id-token: write` (para o deploy).
- Um PR que esquece de bumpar `VERSION` ainda publica — só não gera tag nova. Não é um
  erro fatal, mas quebra a rastreabilidade "toda versão pública tem uma tag"; vale
  revisar no code review.
