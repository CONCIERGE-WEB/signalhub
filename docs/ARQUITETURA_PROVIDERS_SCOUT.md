# Arquitetura — Discovery Engine / Prospector (legado: “Scout”)

> **Nota de naming (2026-07-29):** este arquivo é histórico. O conceito oficial
> de estratégia é **Discovery Engine** (plugin **Prospector**).  
> **Scout (kiryano)** = Source Provider de terceiros — ver
> [`OPEN_SOURCE_COMPLIANCE.md`](./OPEN_SOURCE_COMPLIANCE.md).

**Status:** especificação + scaffold (sem quebrar bot/engine atuais)  
**Alvo:** `C:\01_Projetos\06-SignalHub` (plataforma comercial)  
**Fora de escopo nesta etapa:** `09LexRocha-Br/signalhub-br` (Lex CDC / dorks congelados)  
**Criado:** 2026-07-27  
**Atualizado naming:** 2026-07-29

---

## 1. Objetivo

Absorver o **Scout** como `LeadDiscoveryProvider` sob interface única, mantendo o SignalHub como hub corporativo de inteligência comercial — sem fork paralelo do pipeline existente (`bot/` + `engine/` + `web/`).

---

## 2. Mapa do repositório (pontos de integração)

| Artefato | Path | Papel |
|----------|------|--------|
| README comercial | `README.md` | Produto, módulos, compliance |
| Launcher | `signalhub.ps1` / `signalhub.bat` | Sobe bot/web |
| Env | `.env` / `.env.example` | Credenciais (não no Git) |
| Compliance | `COMPLIANCE.md` | Dados públicos + humano no loop |
| Planos | `PLANOS_E_PRECOS.md` | Comercial |
| Bot | `bot/run_once.py`, `bot/src/`, `bot/config/` | Captação / alerta Telegram |
| Engine | `engine/core/`, `engine/lex/`, `engine/usa/`, … | Regras multi-contexto |
| Web | `web/` (Next.js) | Dashboard / CRM assistido |
| **Providers (novo)** | `engine/providers/` | Scout + futuros canais |

**Nota:** Scout **ainda não existia** no disco (`*scout*` ausente). O módulo `engine/providers/scout/` é o ponto de encaixe; a lógica Scout concreta entra depois sem alterar `bot/run_once.py` até o adapter estar estável.

---

## 3. Padrão Provider (interface única)

```
engine/providers/
  __init__.py
  base.py                 # LeadDiscoveryProvider (ABC)
  scout/
    __init__.py
    provider.py           # ScoutLeadProvider
  linkedin/               # stub futuro
  google_maps/            # stub futuro
  websites/               # stub futuro
```

Contrato (`LeadDiscoveryProvider`):

| Método | Responsabilidade |
|--------|------------------|
| `search(query)` | Descoberta bruta de candidatos |
| `collect(hits)` | Normalização / dedupe |
| `enrich(leads)` | Stack tech, especialidade, sinais |
| `validate(leads)` | LGPD / fontes públicas / score mínimo |
| `export(leads, sink)` | Postgres, CRM, API, automação |

Esteira alvo:

```
Provider (Scout)
  → Enrichment Engine (stack / nível tech / IA)
  → Scoring Engine
  → PostgreSQL
  → Output (Dashboard web, CRM, API REST, automações)
```

O bot Telegram atual continua como **um sink de alerta**, não como único orquestrador.

---

## 4. Verticais (pipelines de uso)

| Vertical | Sinais típicos | Output |
|----------|----------------|--------|
| **LegalTech (Lex Rocha)** | Escritórios, especialidades, volume OAB, UF | Leads B2B + score de fit Lex |
| **Delivery** | Restaurantes, cardápio, presença digital | Potencial de venda / contato |
| **Consultoria IA** | Site + stack tech | Relatório de gaps + proposta (humano no loop) |

Cada vertical = perfil de `enrich()` + `validate()` + template de `export()`, **sem** duplicar o motor.

---

## 5. Fases de implementação

| Fase | Entrega | Critério |
|------|---------|----------|
| **P0** (este PR) | `base.py` + stub Scout + doc | Importável; bot antigo intacto |
| **P1** | Adapter Scout real → `search/collect` | Testes unitários sem Telegram |
| **P2** | Enrichment + scoring + Postgres | Feature flag; humano no loop |
| **P3** | Verticais LegalTech / Delivery / IA | Config YAML por vertical |
| **P4** | Dashboard / API | Sem quebrar `web/` atual |

---

## 6. Regras de não-quebra

1. Não alterar `signalhub-br/` (Lex CDC) nesta fusão.  
2. Não trocar token Telegram do CDC pelo de ops.  
3. Novos providers só entram no engine via feature flag.  
4. Zero envio automático a leads — compliance SignalHub.

---

---

## 8. Decisão frente à proposta “capability platform” (2026-07-27)

Avaliação da proposta de Core desacoplado + EventBus + AI engine + plugins + PgVector:

| Ideia | Veredito | Quando |
|-------|----------|--------|
| Core que só conhece `Provider` | **Adotar** | Já no contrato `LeadDiscoveryProvider` |
| Registry `register/load/discover` | **Adotar** | Evoluir `get_provider` → registry com entry points |
| Pipeline por eventos (`LeadFound`…) | **Adotar em fases** | P2+; hoje esteira síncrona `run()` basta |
| AI engine isolado (`ai/`) | **Adotar** | P2 — sem IA espalhada no Scout |
| Modelo de dados único (`Lead`) | **Adotar já** | Unificar `LeadCandidate` → schema canônico |
| Enrichment em etapas plugáveis | **Adotar** | P2 — flags por etapa |
| Plugins (CRM, WhatsApp, PDF) | **Adotar depois** | P3 — sinks reagem a eventos |
| Banco vetorial (PgVector/Qdrant) | **Preparar** | Schema `embedding` nullable já no P2; motor RAG em P4 |
| Observabilidade (OTel/Sentry) | **Mínimo já** | Logs estruturados + métricas por provider no P1 |

**Não fazer agora:** reescrever `bot/` + `web/` numa monorepo `signalhub/core` completa. Isso trava o produto comercial atual. O caminho seguro é **crescer `engine/providers` + `engine/core` fino** ao lado do bot legado, com feature flag, até o Core absorver o orquestrador.

**Princípio:** Scout é um provider; SignalHub é a plataforma de capacidades. EventBus e vetorial nascem quando houver volume/custo que justifique — não no scaffold vazio.

---

## 9. Atualização — OS Core em `signalhub/` (2026-07-27)

A fundação da plataforma (OS) vive em `signalhub/` (Core + MCP/API/CLI). Ver `docs/ARQUITETURA_OS.md` e `docs/ADR/0001-signalhub-os-core.md`.

`engine/providers/` permanece como scaffold legado até o adapter P1.  
Contrato canônico: `signalhub.core.contracts.provider.Provider` (`search` / `collect` / `normalize` / `validate` / `enrich` / `healthcheck` / `metadata`).

---

## 10. Decisão — Discovery Engine (não “Scout”) como estratégia (2026-07-29)

**Open Source Compliance:** o nome **Scout** deixa de designar a estratégia da plataforma.

| Nome | Papel |
|------|--------|
| **Discovery Engine** | Mecanismo oficial de prospecção (orquestra Source Providers) |
| **Prospector \| Tiago A. Rocha** | Plugin Cliente Zero (`prospector_tiagorocha`) |
| **Scout (kiryano)** | Source Provider de terceiros ([kiryano/Scout](https://github.com/kiryano/Scout), MIT) — futuro |

Arquivo histórico: este documento mantém o título legado; a norma vigente é
[`SIGNALHUB_SPECIFICATION.md`](./SIGNALHUB_SPECIFICATION.md) +
[`OPEN_SOURCE_COMPLIANCE.md`](./OPEN_SOURCE_COMPLIANCE.md).

**Não** ligar Discovery Engine real nem múltiplas fontes em paralelo. Ordem e checklist:
[`PROVIDER_CERTIFICATION_PROGRAM.md`](./PROVIDER_CERTIFICATION_PROGRAM.md).
