# Constituição do Projeto — Blog MUMU Solutions

Regras **não negociáveis**. Toda spec, ADR, post e PR deve respeitá-las. Quando uma
decisão conflitar com a constituição, a constituição vence — ou a constituição muda
primeiro, por decisão explícita, versionada aqui.

Versão: 1.0.0 • Ratificada em: 2026-09-22

> **Princípio soberano (Artigo I):** este é um repositório **público** que serve um
> site real via GitHub Pages. Tudo que é commitado é publicado. Não existe "arquivo
> interno" aqui — o que não deve ser público não entra neste repositório.

---

## Artigo I — Escopo mínimo publicável

Só entra no repositório o que o site precisa para servir suas páginas: conteúdo,
templates, o gerador, governança leve (constituição/specs/ADR) e o workflow de deploy.
Nada de ferramentas, dependências ou assets "por precaução". Ativos de marca
(`mumu-mumia`, `mumu-branding`) são copiados **arquivo a arquivo, sob demanda de um
post**, nunca a árvore inteira de um repo fonte.

## Artigo II — Markdown é a fonte, HTML é o destino

Todo post é escrito em Markdown (`index.pt.md`, com `index.en.md` opcional) dentro da
sua própria pasta. O HTML publicado é **gerado e commitado** por `build.py` — nunca
editado à mão. `python3 build.py --check` falha o build se o HTML commitado divergir do
que a fonte Markdown produziria. Ver
[ADR 0001](adr/0001-md-to-html-stdlib.md) e [ADR 0002](adr/0002-committed-html-output.md).

## Artigo III — Sem build step, sem dependência

`build.py` usa só a biblioteca padrão do Python. Sem `pip install`, sem bundler, sem
framework de front-end. Ver [ADR 0001](adr/0001-md-to-html-stdlib.md).

## Artigo IV — Segurança por padrão, sem hash de CSP

Toda página publicada carrega uma CSP restritiva (`default-src 'none'`, cada tipo de
recurso nomeado explicitamente) via `<meta>`, com **zero** `<style>`/`<script>` inline —
CSS e JS vivem em `blog.css`/`blog.js`, referenciados com `?v=<VERSION>`. Isso troca o
hash-por-página do site institucional (inviável com N páginas geradas) por "não há nada
para hashear". Ver [ADR 0003](adr/0003-external-css-js-bare-csp.md).

## Artigo V — Bilíngue por design, português como fonte

`index.pt.md` é obrigatório em todo post; `index.en.md` é opcional. Sem tradução, a
versão EN mostra um aviso curto — nunca conteúdo inventado ou traduzido por máquina sem
revisão humana. O chrome do site (nav, rodapé) é sempre bilíngue. Com JavaScript
desligado, a página ainda mostra o português corretamente — o servidor já renderiza o
par `data-lang` correto, o JavaScript só alterna.

## Artigo VI — Estrutura de post

Cada post vive em `posts/<ano>/<mês>/<slug>/`, com seus próprios `index.pt.md`,
`index.en.md` opcional, e uma subpasta `images/` para os assets exclusivos daquele post.
Ver [ADR 0005](adr/0005-post-bundle-layout.md).

## Artigo VII — Versionamento e publicação automática

`VERSION` na raiz é a fonte da verdade do semver do site. Um push em `main` cujo commit
mude `VERSION` para um valor ainda não tageado dispara: gate (`build.py --check`) →
criação e push da tag `v<VERSION>` → deploy. Um push que não mude `VERSION` faz deploy
sem tag nova. Nunca existe uma segunda tag para o mesmo `VERSION`. Ver
[ADR 0004](adr/0004-semver-tag-drives-publish.md).

| Parte | Quando |
|---|---|
| MAJOR | uma URL de post muda ou deixa de existir |
| MINOR | novo post, nova página do site (ex.: índice, tag) |
| PATCH | texto, estilo, ferramentas internas |

## Artigo VIII — Publicação via PR, nunca push direto

Todo trabalho é entregue por pull request revisável, mesmo sendo este processo o que
aciona o auto-deploy ao chegar em `main`. Ninguém — humano ou agente — dá push direto em
`main`.

## Governança

Alterar esta constituição exige um novo commit neste arquivo com a versão e a data de
ratificação atualizadas, mais uma linha em `CHANGELOG.md` (quando existir) explicando o
quê e o porquê.
