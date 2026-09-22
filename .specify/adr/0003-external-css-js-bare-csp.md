# ADR 0003 — CSS/JS externos com CSP simples, não hash por página

Status: aceito · 2026-09-22

## Contexto

`mumu-solutions.github.io` inlina `<style>` e `<script>` em `index.html` e hasheia os
dois blocos na CSP (`tools/check_csp_hashes.py`), porque é **uma** página. Este blog
gera **N páginas** (uma por post, mais o índice) a partir dos mesmos templates.

## Decisão

`blog.css` e `blog.js` são arquivos externos, referenciados com `?v=<VERSION>` (mesmo
padrão de cache-busting das páginas de erro do site institucional). Toda página carrega
`style-src 'self'; script-src 'self'` — sem `'unsafe-inline'`, sem hash, porque não há
`<style>`/`<script>` inline para hashear.

## Por quê

O padrão do site institucional (hash por bloco inline) presume um único arquivo com um
único `<style>` e um único `<script>`. Com N páginas geradas pelo mesmo template, todas
compartilhariam o mesmo hash — mas qualquer edição de `blog.css`/`blog.js` exigiria
recalcular e reescrever o hash em toda página gerada, e nenhuma ferramenta neste
repositório faz isso automaticamente (a de `mumu-solutions.github.io` lê só
`index.html`). Copiar aquela ferramenta para operar sobre N arquivos é mais superfície
para manter do que simplesmente não ter nada inline para hashear.

O próprio CLAUDE.md do site institucional já documenta esse raciocínio para as páginas
de erro: "the moment one of them gains an inline block, it acquires a hash that no tool
regenerates and no gate checks." Aqui isso vale para toda página, não só as de erro.

## Consequências

- `'self'` para style-src/script-src é suficiente e nunca precisa de manutenção quando
  o CSS ou o JS mudam.
- Dois arquivos a mais por deploy (`blog.css`, `blog.js`), cacheáveis por muito tempo
  graças ao `?v=`.
- Nenhum `style="..."` ou `onclick=` pode aparecer em template ou post — mesma regra do
  site institucional, pelo mesmo motivo (CSP fecharia `'unsafe-inline'` para permitir).
