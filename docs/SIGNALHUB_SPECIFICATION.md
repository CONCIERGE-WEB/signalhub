# SignalHub Specification

| Campo | Valor |
|-------|--------|
| **Documento** | Constituição do projeto |
| **Não é** | RFC · README · guia de implementação |
| **É** | Definição normativa da identidade do SignalHub |
| **Versão** | 1.0.1 |
| **Data** | 2026-07-29 |
| **Titular** | Tiago A. Rocha |
| **Repo** | `06-SignalHub` |

> Em caso de conflito entre um guia tático e este documento, **prevalece a Specification**.
> RFCs, ADRs e Certification detalham *como*; este texto fixa *o que é*.

---

## 1. Visão

O SignalHub é uma **plataforma modular** para **descoberta, processamento e distribuição de sinais públicos**.

Seu objetivo é fornecer uma **infraestrutura determinística** para aplicações que precisam consumir **evidências públicas** de forma:

- **auditável**
- **extensível**
- **independente de modelos de IA**

O objeto central do sistema é o **Signal** — não o lead, não o chat, não a página web.

### 1.1 Identidade de plataforma (2026-07-29)

O SignalHub **não** é um software de prospecção acoplado a um único produto.
É **infraestrutura**. Lex Rocha, Zairyx, Delivery, CRM ou uma IA são **consumidores** —
não donos do Core.

**Pergunta canônica (plataforma):**

> Como *qualquer* software pode consumir o SignalHub?

**Não** (visão antiga de produto único):

> Como integrar o SignalHub ao Lex?

**Essência (três frases):**

> O SignalHub não coleta dados. Ele organiza evidências.  
> O SignalHub não toma decisões. Ele entrega sinais.  
> O SignalHub não substitui aplicações. Ele conecta aplicações a sinais públicos
> de forma determinística, auditável e extensível.

**Tagline candidata (home / identidade):**

> **Build on Signals, not assumptions.**

```text
Internet
    ↓
Source Providers  (Reddit · Google · GitHub · Websites · Scout kiryano · …)
    ↓
Discovery Engine  (Prospector)
    ↓
SignalHub Core    (determinístico — sem IA)
    ↓
Signals
    ↓
REST · CLI · Dashboard · Telegram · MCP
    ↓
Qualquer aplicação  (Lex · Zairyx · Delivery · CRM · IA plugin · …)
```

**Disciplina de crescimento:** um plugin **excelente** e certificado por vez —
nunca vinte plugins ao mesmo tempo.

---

## 2. O que o SignalHub NÃO é

Isto protege a identidade do projeto:

```text
Não é IA.
Não é CRM.
Não é scraper.
Não é automação de marketing.
Não é um bot do Telegram.
Não é uma LegalTech.
Não é um framework web.
Não é um banco de dados.
```

Pode *integrar-se* a esses mundos via **Providers**, **Consumers** e **Adapters**.  
Nenhum deles redefine o Core.

---

## 3. O que é um Signal

**Signal** = unidade canônica de evidência pública processada pelo Core.

Norma completa: [`docs/RFC/0001_SIGNAL_SPECIFICATION.md`](./RFC/0001_SIGNAL_SPECIFICATION.md) (contrato `1.0.0`).

Resumo (não substitui o RFC):

- Schema versionado e validável
- Provenance obrigatória
- Sem dados inventados; ausência = **vazio explícito**
- Lead é **interpretação opcional** de um Signal — não o objeto principal

---

## 4. Componentes oficiais

| Componente | Papel |
|------------|--------|
| **Core** | Orquestração determinística; **LOCKED** para regras de fonte |
| **Signal** | Objeto canônico (RFC-0001) |
| **Provider** | Produz RawHits / Signals sob contrato |
| **Source Provider** | Provider de **uma** fonte concreta (canal) |
| **Discovery Engine** | Estratégia oficial de **descoberta** (orquestra Source Providers; não é uma fonte) |
| **Prospector** | Implementação Cliente Zero da Discovery Engine (`prospector_tiagorocha`) |
| **Capability** | Operação publicada (CLI / REST / MCP) |
| **Rule Engine** | Regras determinísticas sobre Signals |
| **Score Engine** | Pontuação determinística (sem LLM no Core) |
| **Validator** | Rejeita Signals inválidos; nunca inventa campos |
| **Storage** | Persistência de Signals (contrato estável; backend pode evoluir) |
| **Mission Control** | Visão operacional / status / certificação |
| **Dashboard** | UI de consumo (não embute regras de fonte no Core) |
| **REST** | Interface HTTP do mesmo Core |
| **CLI** | Interface de linha de comando do mesmo Core |
| **MCP** | Tools = projeção de Capabilities (sem scraping no MCP) |
| **Notification Adapter** | Ex.: Telegram — formata/entrega; não é o produto |

Distinção Discovery Engine × Source Providers:
[`PROVIDER_CERTIFICATION_PROGRAM.md`](./PROVIDER_CERTIFICATION_PROGRAM.md) ·
[`OPEN_SOURCE_COMPLIANCE.md`](./OPEN_SOURCE_COMPLIANCE.md).

> **Naming:** “Scout” **não** é conceito da plataforma.  
> **Scout (kiryano)** = Source Provider de terceiros (MIT) quando integrado — ver
> [`THIRD_PARTY_COMPONENTS.md`](./THIRD_PARTY_COMPONENTS.md).

---

## 5. Filosofia

| Princípio | Significado |
|-----------|-------------|
| **Contract First** | Nada entra sem contrato (Signal, Provider, Plugin) |
| **Deterministic First** | Core sem IA; mesmo input → mesmo caminho auditável |
| **Auditability** | Provenance e trilha de processamento observáveis |
| **Explainability** | Regras e scores explicáveis; sem caixa-preta no Core |
| **Compatibility** | Stability Guarantee + SemVer de contrato / Core / plugin |
| **Extensibility** | Extensão = plugin via SDK; Core não recebe “atalhos” |
| **Empty Explicit** | Sem fallback fictício; scaffold e pending = vazio honesto |
| **Human in the Loop** | Contato externo e decisões sensíveis ficam com o operador |
| **One at a Time** | Certificação / wiring de Providers: **nunca dois em paralelo** |

Garantia de estabilidade: [`STABILITY_GUARANTEE.md`](./STABILITY_GUARANTEE.md).

---

## 6. Ecossistema

```text
                 SignalHub
                     │
          ┌──────────┼───────────┐
          │          │           │
     Providers   Consumers   Adapters
          │          │           │
          └──────────┼───────────┘
                  Signals
```

| Papel | Exemplos (ilustrativos) |
|-------|-------------------------|
| **Providers** | Discovery Engine (Prospector) → Source Providers: Dork, Google, GitHub, Scout (kiryano), TikTok, YouTube, Instagram, Facebook, Websites, … |
| **Consumers** | Lex Rocha (via Adapter), futuros produtos, lab/debug |
| **Adapters** | Telegram Notification, REST/MCP gateways, dashboard adapters |

Cliente Zero (dogfooding do SDK): [`CLIENT_ZERO.md`](./CLIENT_ZERO.md).

---

## 7. Especificações oficiais

| Artefato | Onde | Função |
|----------|------|--------|
| **Specification** | este arquivo | Constituição — *o que é* |
| **RFC** | `docs/RFC/` | Contrato normativo (ex.: Signal 1.0.0) |
| **ADR** | `docs/ADR/` | Decisões arquiteturais registradas |
| **Certification** | `docs/PROVIDER_CERTIFICATION_PROGRAM.md` | Quem pode ser Provider oficial |
| **SDK** | `docs/developers/` · `signalhub.sdk` | Como estender sem tocar no Core |
| **Architecture** | `docs/ARQUITETURA_*.md` | Mapas e fases |
| **Examples** | `plugins/example_*` · lab | Didática e laboratório |
| **Test Kit** | `signalhub/tests` · `cli doctor` / `contract-check` / `validate` / `test` | Prova de conformidade |

---

## 8. Roadmap (curto)

```text
Core (LOCKED)
    ↓
Open Source Compliance     ← concluída (2026-07-29)
    ↓
Certification Program
    ↓
First Certified Discovery Engine  ← PHASE 3.1 (Dorking) — concluída
    ↓
Developer SDK (maduro)
    ↓
Marketplace
    ↓
Community
```

**Estado documental (2026-07-29):**

- Core 1.x travado por contrato
- Plataforma web / Mission Control / lab funcionais no ambiente local
- Arquitetura e Stability Guarantee documentadas
- Provider Certification Program definido
- **Specification** publicada (este documento)
- **Open Source Compliance** concluída
- **PHASE 3.1** concluída: Discovery Engine (Dorking) = Certified Level 1
  ([`PHASE_3_1_DISCOVERY_ENGINE.md`](./PHASE_3_1_DISCOVERY_ENGINE.md))

---

## 9. Horizonte — SignalHub Compliance (previsão)

O **Provider Certification Program** certifica Providers.

Com o amadurecimento da plataforma, espera-se um envelope maior:

```text
SignalHub Compliance

Level 1 — Core Compatibility
Level 2 — Provider Compatibility
Level 3 — Capability Compatibility
Level 4 — Production Ready
Level 5 — Official Certified
```

Isto **não** substitui a Specification nem o Certification Program atual.  
Quando nascer formalmente, terá documento próprio; até lá, permanece **previsão** — não norma.

---

## 10. Próximo passo único

Uma única frente de trabalho após este documento:

> **PHASE 3.1 — First Certified Provider**

Objetivo: provar que a arquitetura **suporta uma integração real sem alterar o Core**
(primeiro alvo: **Discovery Engine / Prospector** — não o kiryano/Scout).

Não inventar arquitetura. Não certificar dois Providers. Não ligar Marketplace.
Open Source Compliance já concluída: [`OPEN_SOURCE_COMPLIANCE.md`](./OPEN_SOURCE_COMPLIANCE.md).

Detalhe da fila e checklist: [`PROVIDER_CERTIFICATION_PROGRAM.md`](./PROVIDER_CERTIFICATION_PROGRAM.md).
