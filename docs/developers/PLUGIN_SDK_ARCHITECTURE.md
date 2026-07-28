# Plugin SDK — Architecture (documentation only)

| Campo | Valor |
|-------|--------|
| **Status** | Documentação de arquitetura |
| **Implementação nova nesta fase** | Nenhuma (SDK já existe em `signalhub.sdk`) |
| **Objetivo** | Preparar terceiros sem expandir o Core |

Este arquivo **não** adiciona código. Descreve a arquitetura que o SDK já entrega
e o que um autor de plugin deve respeitar.

---

## 1. Posicionamento

```text
┌─────────────────────────────────────────────────────────┐
│  Apps: REST · CLI · MCP · Telegram · Dashboard (Lex)    │
└───────────────────────────┬─────────────────────────────┘
                            │ Adapter / projection only
┌───────────────────────────▼─────────────────────────────┐
│  Core (determinístico, sem IA)                          │
│  Orchestrator → Pipeline → Storage → Metrics/Health     │
└───────────────────────────┬─────────────────────────────┘
                            │ contracts + registry
┌───────────────────────────▼─────────────────────────────┐
│  Plugin SDK  (signalhub.sdk)                            │
│  Provider · Capability · Adapter · Consumer · Ruleset   │
└───────────────────────────┬─────────────────────────────┘
                            │ plugin.yaml + loader
┌───────────────────────────▼─────────────────────────────┐
│  plugins/*  (Cliente Zero: prospector_tiagorocha, dork_signals) │
└─────────────────────────────────────────────────────────┘
```

- **Core** orquestra Signals. Não conhece Lex Rocha nem ToS de canais.
- **Plugin** declara `signalhub_version` + `contract_version`; o loader negoceia.
- **Lex Rocha** é consumidor via Adapter — zero regras SignalHub no site.

---

## 2. Superfície pública (`signalhub.sdk`)

| Módulo | Papel |
|--------|--------|
| `provider` | `ProviderPlugin` / `BaseProvider` — RawHit → Signal |
| `capability` | Capability derivada/consulta (não muta storage) |
| `adapter` | Notificação outbound (ex.: Telegram port) |
| `consumer` | Consome Signals já canônicos |
| `ruleset` | Regras determinísticas plugáveis |
| `scaffold` | `signalhub create …` |
| `testing` / `devtools` | validate · doctor · contract-check |

Gate de publicação: `validate` + `contract-check` (ver `publishing-plugins.md`).

---

## 3. Ciclo do autor (sem porta dos fundos)

```text
create → implement search/normalize → validate → doctor → contract-check
```

1. Scaffold em `plugins/<name>/`.
2. Implementar só o canal (ToS/rate-limit **no plugin**).
3. `python -m signalhub.apps.cli validate plugins/<name>`
4. `python -m signalhub.apps.cli doctor --full`
5. Nunca editar `signalhub/core` para “liberar” o plugin.

---

## 4. Version Negotiation (obrigatória)

No `plugin.yaml`:

```yaml
name: my_provider
version: 0.1.0
signalhub_version: ">=0.4.0"
contract_version: "1.0.0"
```

- Core não satisfaz `signalhub_version` → plugin **não carrega**.
- `contract_version` major ≠ Core → plugin **não carrega**.
- Signal emitido com `contract_version` fora do suportado → Validator rejeita.

---

## 5. O que o SDK **não** fará nesta fase

- Scraping adicional ou Providers reais wired.
- IA no Core.
- Marketplace runtime.
- Prometheus / OpenTelemetry export.

Quando Providers reais forem ligados, o foco será qualidade da coleta e regras —
**sem** reescrever o núcleo.
