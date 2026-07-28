# Arquitetura — SignalHub Operating System

**Status:** fundação P0 (contratos + Core + MCP/API/CLI)  
**Pacote:** `signalhub/` na raiz de `06-SignalHub`  
**Criado:** 2026-07-27  
**Licença atual:** Business License (proprietário). A visão de MCP open-source é decisão de produto futura — este núcleo está desenhado para eventual extração open-core, sem alterar a licença vigente.

---

## 1. Visão

O SignalHub **não** é scraper, CRM ou “só MCP”.

É um **Operating System de Inteligência Comercial**. Interfaces:

| Interface | Path | Papel |
|-----------|------|--------|
| Core | `signalhub/core/` | Regras, orquestração, registry |
| MCP | `signalhub/apps/mcp/` | Tools = projeção de Capabilities |
| REST | `signalhub/apps/api/` | Mesmo Core |
| CLI | `signalhub/apps/cli/` | Mesmo Core |
| Dashboard | `web/` + `apps/dashboard/` | UI; BFF futuro chama Core |
| Providers | `signalhub/providers/` | Scout, Dorking, Google, … |

**Nenhuma regra de negócio na camada MCP.**

Legado (`bot/`, `engine/`, `web/`) permanece intacto. Lex CDC (`signalhub-br`) fora de escopo.

---

## 2. Contrato Provider

Todo provider implementa:

`metadata` · `healthcheck` · `search` · `collect` · `normalize` · `validate` · `enrich`

- Nenhum Provider conhece outro Provider.
- Providers **não** chamam LLM — IA fica em `signalhub/ai/` via ports.
- Dork Engine = `providers/dorking` (especializado, compliance-first).

---

## 3. Capabilities → Tools MCP

Capabilities em `signalhub/capabilities/` são publicadas automaticamente como tools MCP por `apps/mcp/tool_publisher.py`.

Exemplos P0: `discover_leads`, `discover_social_signals`, `score_lead`, `analyze_website`, `generate_report`.

---

## 4. Pipeline

```
Provider → normalize → Deduplicator → (Company/Domain/Email/Tech stubs)
  → Scoring stub → Storage stub → Events → MCP/API/CLI/Dashboard
```

Event bus in-process (`core/events`) — trocável por broker depois.

---

## 5. Segurança e observabilidade

- `security/policy.py` — enable/disable providers e capabilities; rate-limit config; human-in-the-loop.
- `observability/` — traces, métricas in-memory, logs estruturados.
- Toda entidade carrega `Provenance` (origem auditável).

---

## 6. Fases

| Fase | Entrega |
|------|---------|
| **P0** (este) | Pacote `signalhub/`, contratos, registry, MCP/API/CLI, stubs, testes |
| **P1** | Ligar Scout/Dorking reais atrás do contrato (feature flag; vazio até então) |
| **P2** | Enrichment + scoring + Postgres + AI ports reais |
| **P3** | Plugins CRM/PDF; dashboard BFF |
| **P4** | Vectors / knowledge graph; avaliação open-core do pacote MCP |

---

## 7. Como rodar

```powershell
cd C:\01_Projetos\06-SignalHub
python -m pytest signalhub/tests -q
python -m signalhub.apps.cli capabilities
python -m signalhub.apps.cli run discover_leads --args "{\"terms\":[\"advogado\"]}"
python -m signalhub.apps.mcp.server
```

---

## 9. Consumidor Lex Rocha

O Casos do Consumidor **não** embute este pacote.

- Integração: `09LexRocha-Br/docs/INTEGRACAO_LEXROCHA_SIGNALHUB.md`
- Lex consome via adapter (`local` / `http` / `off`)
- Painel: `/admin/signalhub` (só frontend)
- Evolução do OS: **somente** neste repositório (`06-SignalHub`)

## 10. P1 — identidade Signal (2026-07-27)

Ver `docs/ARQUITETURA_P1_SINAIS.md`.

- Objeto principal: **Signal** (Lead = interpretação opcional)
- Core **sem IA**; Rule Engine + Score Engine determinísticos
- Telegram = Notification Adapter
- MCP só expõe Capabilities (não faz scraping)

## 11. RFC-0001 (P1.5) — contrato oficial

**Documento normativo:** [`docs/RFC/0001_SIGNAL_SPECIFICATION.md`](./RFC/0001_SIGNAL_SPECIFICATION.md)

Pipeline Core:

`Validator → Normalizer → Deduplicator → Rule Engine → Score Engine → Storage`

Nenhum Provider real (Scout/Dork) deve ser ligado sem respeitar este RFC.

## 12. P2 — Developer Platform

Ver [`docs/ARQUITETURA_P2_DEVELOPER_PLATFORM.md`](./ARQUITETURA_P2_DEVELOPER_PLATFORM.md) e [`docs/developers/`](./developers/).

Core estável; extensões via `plugins/` + SDK. Marketplace: [`docs/MARKETPLACE.md`](./MARKETPLACE.md).

## 13. Cliente Zero

Scout e Dorking saíram do Core:

- [`plugins/prospector_tiagorocha`](../plugins/prospector_tiagorocha) (Prospector | Tiago A. Rocha; antes `scout_signals`)
- [`plugins/dork_signals`](../plugins/dork_signals)

Ver [`docs/CLIENT_ZERO.md`](./CLIENT_ZERO.md).
