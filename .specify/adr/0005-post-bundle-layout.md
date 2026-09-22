# ADR 0005 — Um post, uma pasta particionada por data

Status: aceito · 2026-09-22

## Contexto

O pedido pede posts "numa pasta organizada em estrutura" (partição por data, ao estilo
de um data lake particionado) em vez de todo o conteúdo solto num único diretório
`posts/`.

Opções consideradas:

1. `posts/<slug>.md` — um arquivo por post, sem pasta.
2. `posts/<ano>/<mês>/<slug>/index.{pt,en}.md` — bundle por post, particionado por data.
3. `posts/year=<ano>/month=<mês>/<slug>/...` — partição estilo Hive.

## Decisão

Opção 2. Cada post é uma pasta `posts/<ano>/<mês>/<slug>/`, contendo `index.pt.md`,
`index.en.md` opcional, uma subpasta `images/` com os assets exclusivos daquele post, e
o `index.html` gerado. A URL pública correspondente é
`https://blog.mumu.solutions/posts/<ano>/<mês>/<slug>/`.

## Por quê

- **Bundle, não arquivo solto.** Um post quase sempre precisa de pelo menos uma imagem;
  a opção 1 obrigaria uma convenção separada de "onde ficam as imagens deste post"
  (pasta paralela, prefixo de nome). A pasta resolve isso: tudo que o post usa mora
  junto com ele.
- **Partição por data, não por Hive.** `year=2026/month=09/` é mais literal como
  partição, mas produz URLs feias e uma profundidade extra sem benefício — ninguém
  consulta este diretório com uma engine de partição, é só uma organização visual no
  git. `2026/09/` entrega a mesma navegabilidade cronológica com URLs limpas.
- Consistente com o padrão de bundle de página do `institutional-site-builder`/Hugo:
  cada unidade de conteúdo é uma pasta autocontida.

## Consequências

- Mover um post de mês (correção de data) muda sua URL — conta como MAJOR pela
  constituição (Artigo VII), então é uma decisão deliberada, não um refactor casual.
- `build.py` descobre posts com um glob de profundidade fixa
  (`posts/*/*/*/`) — um post fora dessa profundidade não é encontrado, o que é
  intencional: a estrutura é a validação.
