# SignalHub — Stability Guarantee

| Campo | Valor |
|-------|--------|
| **Status** | Ativo |
| **Contrato Signal** | `1.0.0` (RFC-0001) |
| **Core** | `signalhub` ≥ `0.4.0` |
| **Escopo** | Plataforma estável para terceiros — **sem** IA no Core |

Este documento fixa o que integradores (Lex Rocha e futuros) podem tratar como estável
antes de ligar Providers reais (Scout/Dork Engine).

---

## 1. Módulos estáveis (não quebrar sem major)

| Superfície | Path / contrato | Garantia |
|------------|-----------------|----------|
| **Signal RFC-0001** | `docs/RFC/0001_SIGNAL_SPECIFICATION.md` · `SIGNAL_CONTRACT_VERSION` | Schema canônico; breaking → nova RFC + major do contrato |
| **Signal Validator** | `signalhub.validation` | Rejeita Signals inválidos; nunca inventa campos |
| **Provider ABC** | `signalhub.core.contracts.provider` | `metadata` / `healthcheck` / `search` / `normalize` … |
| **Capability ABC** | `signalhub.core.contracts.capability` | Query/derive — não muta Signal armazenado |
| **Plugin manifest** | `plugin.yaml` · `signalhub.plugins.manifest` | `name`, `version`, `signalhub_version`, `contract_version` |
| **SDK público** | `signalhub.sdk` | Superfície de extensão; Core não importa app Lex |
| **CLI doctor / validate / contract-check** | `signalhub.apps.cli` | Exit 0 = verde; JSON estável em chaves documentadas |
| **Admin snapshot** | `signalhub.admin_snapshot` | Consumido pelo Adapter Lex; sem regras de negócio do Lex |
| **MCP tool projection** | `signalhub.apps.mcp` | Tools = projeção de Capabilities (sem scraping no MCP) |
| **REST skeleton** | `signalhub.apps.api` | `/health`, `/v1/capabilities`, `/v1/admin/snapshot` |

Integradores **devem** consumir o Core via Adapter / REST / MCP / CLI — **não** copiar regras.

---

## 2. Experimentais (podem mudar sem major do contrato Signal)

| Item | Nota |
|------|------|
| Providers scaffold (`google`, `websites`, …) | Stubs; health ok, search vazio explícito |
| Plugins Cliente Zero (`prospector_tiagorocha`, `dork_signals`) | Contrato ok; discovery **não** wired |
| `InMemoryMetrics` / platform metrics | Internas; sem Prometheus |
| Telegram adapter in-process | Formata/filtra; envio Bot API real = experimental |
| Jobs / recent_executions / logs no snapshot | Reservados |
| Feature flag `p1_scout_dorking_real` | `false` até Providers reais |

Experimentais **não** devem ser usados como SLA de produção.

---

## 3. Política de versionamento

| Artefato | Esquema | Breaking |
|----------|---------|----------|
| `SIGNAL_CONTRACT_VERSION` | SemVer do **schema** Signal | Major → RFC nova; Core rejeita Signals fora de `SUPPORTED_CONTRACTS` |
| `signalhub.__version__` | SemVer do **pacote** Core | Minor/patch: compatível com plugins sob `signalhub_version` |
| `plugin.yaml` → `version` | SemVer do plugin | Independente do Core |
| `plugin.yaml` → `signalhub_version` | Constraint (`>=0.3.0`, `==0.4.0`, …) | Loader **não carrega** se Core não satisfizer |
| `plugin.yaml` → `contract_version` | SemVer do contrato Signal esperado | Loader **não carrega** se major ≠ major do Core |

**Regra de ouro:** Provider real novo = plugin. Core permanece intacto.

---

## 4. Compatibilidade entre versões

1. **Mesma major do contrato Signal** (`1.x`) → Signals e Validators compatíveis.
2. **Plugin vs Core:** `signalhub_version` negociado no load; falha = plugin `ok: false` + errors (providers **não** registrados).
3. **Capability / MCP / REST:** toda Capability habilitada deve aparecer em REST `/v1/capabilities` e como tool MCP (`tool_name`).
4. **Dashboard (Lex):** só lê snapshot via Adapter; incompatibilidade de Adapter = status `unavailable` / `degraded`, nunca inventar Providers.

Comandos de blindagem:

```text
python -m signalhub.apps.cli doctor
python -m signalhub.apps.cli doctor --full
python -m signalhub.apps.cli contract-check
python -m signalhub.apps.cli validate plugins/prospector_tiagorocha
```

---

## 5. O que esta garantia **não** cobre

- Qualidade ou volume de coleta de Providers reais (fase seguinte).
- ToS / rate-limit / compliance de canais externos (vivem no plugin).
- Disponibilidade de Telegram Bot API ou rede de terceiros.
- Lex Rocha B2C (pagamentos, corpus, motores de tribunal).

---

## 6. Próximo passo (fora desta garantia)

Só após `doctor --full` verde de forma sustentável: ligar Scout / Dork Engine **reais** como plugins, sem alterar o Core.
