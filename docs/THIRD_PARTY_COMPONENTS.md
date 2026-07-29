# Third-Party Components

Inventário de software de terceiros relevante ao SignalHub.
Atualizado: **2026-07-29**.

Política: [`OPEN_SOURCE_COMPLIANCE.md`](./OPEN_SOURCE_COMPLIANCE.md) ·
licenças em [`third_party/`](../third_party/).

---

## Componentes previstos ou incorporados

| Projeto | Licença | Uso no SignalHub | Status | Atribuição |
|---------|---------|------------------|--------|------------|
| [kiryano/Scout](https://github.com/kiryano/Scout) | MIT | Source Provider `plugins/scout_kiryano` (GitHub/YouTube/Linktree) | **Incorporado (parcial)** — scrapers públicos; sem enrichment SMTP inventado | [`third_party/kiryano_scout/`](../third_party/kiryano_scout/) |

---

## Runtime do Core (`signalhub/` pacote)

O Core em `pyproject.toml` declara `dependencies = []` (stdlib + SDK interno).
Não há FastAPI / Typer / Pydantic obrigatórios no pacote Core nesta versão.

Quando dependências de terceiros forem adicionadas ao Core ou aos apps,
elas **devem** ser listadas nesta tabela com SPDX e path de NOTICE.

| Projeto | Licença | Uso | Status |
|---------|---------|-----|--------|
| *(nenhuma dependência de terceiros no Core 0.4.0)* | — | — | — |

---

## Legado comercial (`bot/`, `web/`, `engine/`)

O produto comercial legado pode usar stack própria (Python bot, Next.js, etc.).
A lista acima cobre o **OS Core + plugins de discovery**. Inventário completo
do legado comercial pode ser expandido numa linha própria quando necessário
para distribuição — sem misturar com a Constituição do Core.

---

## Regras

1. **Incorporar código** de terceiros → copiar LICENSE (+ NOTICE) em `third_party/<nome>/` **antes** ou no mesmo PR.
2. **MIT / Apache / BSD** → permitido em produto Business, com atribuição.
3. **GPL / AGPL** → exige análise explícita; não incorporar sem decisão registrada em ADR.
4. Código de terceiros entra como **plugin**, nunca como alteração do Core.
5. Nome de produto de terceiros (ex.: Scout) **não** substitui Discovery Engine / Prospector na arquitetura.

---

## Como citar o kiryano/Scout (quando integrar)

Manter no artefato distribuído (ou no repositório):

```text
This product includes software from kiryano/Scout
https://github.com/kiryano/Scout
Copyright (c) 2026 Scout
Licensed under the MIT License — see third_party/kiryano_scout/LICENSE
```
