# ADR 0001 — Gerador Markdown → HTML em stdlib, sem framework

Status: aceito · 2026-09-22

## Contexto

O conteúdo precisa ser fácil de escrever (Markdown) mas o site precisa continuar sendo
HTML/CSS/JS estático puro, sem build step client-side, no mesmo espírito do
`mumu-solutions.github.io` ("no build step, no dependencies").

Opções consideradas:

1. Gerador estático de terceiros (Hugo, Eleventy, Jekyll).
2. Biblioteca Python de Markdown (`markdown`, `mistune`) + script próprio.
3. Conversor Markdown → HTML escrito à mão, só com a biblioteca padrão do Python.

## Decisão

Opção 3. `build.py` implementa um subconjunto deliberadamente pequeno de Markdown
(títulos, parágrafos, listas, citação, bloco de código, regras horizontais, e as formas
inline `**negrito**`, `*itálico*`, `` `código` ``, links e imagens) sem nenhuma
dependência externa.

## Por quê

- Um gerador de terceiros traz sua própria árvore de dependências, versão de Node/Ruby/Go
  e convenções — exatamente o tipo de "toolchain que pode se mover" que o site
  institucional evita deliberadamente.
- Uma lib Python de terceiros já resolveria Markdown completo, mas exigiria
  `requirements.txt` + `pip install` no CI só para renderizar texto — desproporcional
  para o volume de posts previsto.
- O subconjunto suportado cobre 100% do que um post de blog precisa. Se um post
  futuro precisar de tabelas ou notas de rodapé, a extensão é local, ao `build.py`, sem
  trocar de gerador.

## Consequências

- `build.py` é ~250 linhas para manter, não uma dependência para atualizar.
- Sintaxe Markdown fora do subconjunto (tabelas, notas de rodapé, Markdown estendido)
  não é suportada — vira parágrafo escapado, visivelmente errado, não silenciosamente
  quebrado.
- `python3 build.py` roda em qualquer máquina com Python 3, sem setup.
