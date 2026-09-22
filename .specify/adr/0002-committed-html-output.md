# ADR 0002 — HTML gerado é commitado, não construído só no deploy

Status: aceito · 2026-09-22

## Contexto

GitHub Pages com `build_type: workflow` pode publicar qualquer artefato que um Actions
job produza — o HTML poderia ser gerado só durante o deploy, sem nunca existir no git.

## Decisão

`index.html` de cada post e da home são **gerados localmente e commitados**, junto com
a fonte Markdown que os produziu. O workflow de deploy roda `build.py --check` (não
`build.py`) — ele falha se o HTML commitado não bater com o que as fontes gerariam, em
vez de simplesmente gerar e publicar o que der.

## Por quê

- **Revisão real em PR.** Um revisor vê o HTML final no diff, não só o Markdown — inclui
  erros do próprio gerador, não só do texto.
- **`.md` publicado também é servido** (é um repositório público, e o arquivo fonte fica
  no histórico do git de qualquer forma) — commitar o HTML ao lado deixa explícito que
  as duas formas do conteúdo coexistem publicamente por escolha, não por acidente.
- **Falha cedo.** "Editei o Markdown e esqueci de rodar `build.py`" é o erro mais
  provável neste fluxo; `--check` transforma isso num gate de CI que falha o PR, não um
  site desatualizado em produção.
- Consistente com o princípio do site institucional de que o que está no repositório é
  exatamente o que é servido — nada é sintetizado só no momento do deploy.

## Consequências

- Todo PR que edita um post tem dois arquivos para revisar (`.md` e `.html`) — o segundo
  é gerado, não escrito à mão, então a revisão real é do primeiro; o segundo é conferência.
- Esquecer de rodar `build.py` antes do commit falha o CI (`--check`), não é
  silenciosamente publicado desatualizado.
