# RFC-0001 — Especificação oficial do Signal

| Campo | Valor |
|-------|--------|
| **RFC** | 0001 |
| **Título** | Signal Specification |
| **Status** | Aceito |
| **Versão do contrato** | `1.0.0` |
| **Data** | 2026-07-27 |
| **Repo** | `06-SignalHub` (oficial) |
| **Implementação** | `signalhub.core.models.signal` · `signalhub.validation` |

---

## 1. Definição formal

Um **Signal** é a unidade fundamental do SignalHub: uma **evidência pública observável**, normalizada e auditável.

- Todo **Provider** produz Signals (via `RawHit` → normalização).
- Toda **Capability** consome Signals (consulta / deriva — **não** muta o objeto).
- REST, CLI, Dashboard, Telegram e MCP trabalham **exclusivamente** sobre o modelo canônico Signal.
- **Lead** não é entidade principal: é apenas uma **interpretação opcional** de um Signal (`Lead.from_signal`).

O SignalHub **não** é um sistema de IA. Score e classificação vêm de regras determinísticas.

---

## 2. Ciclo de vida (estados)

```
DISCOVERED
    ↓
NORMALIZED
    ↓
DEDUPLICATED
    ↓
CLASSIFIED
    ↓
SCORED
    ↓
STORED
    ↓
CONSUMED
    ↓
ARCHIVED
```

| Estado | Significado |
|--------|-------------|
| `discovered` | Emitido pelo Provider (ainda não passou no Validator do Core) |
| `normalized` | Campos canônicos preenchidos pelo Signal Normalizer do Core |
| `deduplicated` | Sobreviveu ao Deduplicator |
| `classified` | Rule Engine atribuiu categoria / tags de regra |
| `scored` | Score Engine calculou score, confidence e prioridade |
| `stored` | Persistido no storage do Core |
| `consumed` | Entregue a um consumidor (Telegram, Capability, MCP, Dashboard) |
| `archived` | Fora da janela ativa; só leitura histórica |

**Regra:** cada transição registra um `ProcessingStep` em `history` com `at` (timestamp UTC ISO-8601) e `to_status`.

Estados inválidos / rejeitados pelo Validator **não entram** no pipeline (descartados com motivo em observabilidade — não inventar Signal).

---

## 3. Modelo canônico — campos

### 3.1 Obrigatórios no contrato `1.0.0`

| Campo | Tipo | Notas |
|-------|------|--------|
| `id` | string | Estável; preferir `{provider}:{external_id}` |
| `provider` | string | Id do Provider de origem |
| `source` | string | Canal/origem humana (ex.: `reddit`, `gov.br`) |
| `category` | string \| null | Pode ser null até `classified` |
| `title` | string | Não vazio após `normalized` |
| `summary` | string | Pode ser `""` |
| `url` | string \| null | Se presente, deve ser URL http(s) válida |
| `occurred_at` | datetime \| null | Quando o fato público ocorreu (se conhecido) |
| `collected_at` | datetime | Quando o Provider coletou |
| `score` | number \| null | Null até `scored`; depois ∈ `[0, 100]` (ver §5) |
| `priority` | enum | `low` \| `normal` \| `high` \| `urgent` |
| `confidence` | number \| null | Null até `scored`; depois ∈ `[0, 1]` |
| `rules_applied` | string[] | Explicações humanas das regras (§6) |
| `history` | ProcessingStep[] | Auditoria de estágios |
| `metadata` | object | **Único** lugar para campos específicos de Provider/vertical |
| `provenance` | Provenance | Auditoria de origem (§4) |
| `status` | enum | Ver §2 |
| `version` | string | Versão do **documento** Signal (semântica de imutabilidade §7) |

Constante de implementação: `SIGNAL_CONTRACT_VERSION = "1.0.0"` (versão do **schema**).

### 3.2 Campos proibidos no objeto principal

Nenhum Provider pode acrescentar chaves arbitrárias ao objeto principal além das listadas.

Tudo que for específico (HTML bruto, ids internos, geo, company_id, stack, etc.) vai em **`metadata`**.

Extensões futuras (sem quebrar o núcleo):

| Família (em `metadata.signal_family`) | Uso |
|--------------------------------------|-----|
| `geo` | GeoSignals |
| `company` | CompanySignals |
| `legal` | LegalSignals |
| `consumer` | ConsumerSignals |
| `market` | MarketSignals |
| `technology` | TechnologySignals |
| `reputation` | ReputationSignals |

`signal_type` (enum de tipagem fina) permanece como campo de classificação auxiliar alinhado ao RFC, serializado no canônico; famílias acima vivem em `metadata`.

### 3.3 Campos opcionais / derivados

| Campo | Notas |
|-------|--------|
| `score_breakdown` | Componentes numéricos + justificativas (alimenta UI) |
| `parent_id` / `supersedes` | Quando `version` incrementa (§7) |

---

## 4. Provenance

Toda evidência registra:

| Campo | Obrigatório |
|-------|-------------|
| `provider_id` | sim |
| `source_url` | quando houver URL |
| `collected_at` | sim |
| `content_hash` | quando houver corpo/texto hashável |
| `pipeline_version` | sim (ex.: `signalhub-0.2.0+contract-1.0.0`) |
| `rules_executed` | lista (preenchida após Rule/Score) |
| `source_kind` | default `public` |
| `origin` | alias legível da origem (opcional; espelha `source` do Signal) |

Isso permite auditoria completa ponta a ponta.

---

## 5. Score, confidence e priority

- **Score:** número ≥ 0; convenção operacional atual: tipicamente 0–100 (pesos das regras). Valores fora de `[0, 100]` são rejeitados pelo Validator **após** `scored` (ou clamp documentado — nesta RFC: **rejeitar** no Validator se `status` ≥ scored e score ∉ [0, 100]).
- **Confidence:** ∈ [0, 1] — confiança do **algoritmo de regras**, não de um LLM.
- **Priority:** apenas `low|normal|high|urgent`.

---

## 6. Rule Engine — explicações

Toda regra aplicada gera uma string em `rules_applied` no formato legível, por exemplo:

```text
keyword: advogado
categoria: voo
origem: Reddit
recência: 12 horas
```

Essas strings alimentam Dashboard, Telegram, REST e MCP — **sem caixa-preta**.

Telegram deve renderizar `rules_applied` com marcadores (ex.: `✔`), não apenas um score numérico.

---

## 7. Imutabilidade e Capabilities

- **Capabilities não modificam** um Signal existente.
- Podem: consumir, consultar, derivar (ex.: Lead, notificação).
- Se o Core precisar alterar estado/score de forma material, cria-se **nova versão** do Signal (`version` incrementada; `supersedes` / `parent_id` em metadata ou campos dedicados).
- Providers **nunca** escrevem direto no storage pulando Validator + Normalizer do Core.

---

## 8. Pipeline canônico (Core)

```
Provider (RawHit)
    ↓
Provider.normalize → Signal(status=discovered)
    ↓
Signal Validator      ← rejeita inválidos
    ↓
Signal Normalizer     ← canônico + status=normalized
    ↓
Deduplicator          → deduplicated
    ↓
Rule Engine           → classified
    ↓
Score Engine          → scored
    ↓
Storage               → stored
    ↓
Capabilities / REST / CLI / Dashboard / Telegram / MCP
                      → consumed (no consumidor)
```

O **Signal Validator** garante que nenhum Provider (incluindo terceiros futuros) injete Signal inválido:

- campos obrigatórios presentes;
- URL válida (se houver);
- datas coerentes (`occurred_at` ≤ `collected_at` + tolerância);
- categoria conhecida **ou** null (desconhecida só até classified);
- priority no enum;
- score/confidence nos intervalos quando já scored;
- `version` / contrato compatível.

---

## 9. MCP / REST

- Tools MCP retornam **somente** o modelo canônico (`Signal.to_dict()` conforme este RFC).
- Nenhuma Tool devolve estruturas internas de Provider.
- MCP **não** executa scraping; só chama Capabilities do Core.

---

## 10. Versionamento e compatibilidade

| Tipo | Política |
|------|----------|
| `SIGNAL_CONTRACT_VERSION` | SemVer do schema; breaking change → RFC nova |
| `Signal.version` | Versão da **instância** (imutabilidade §7) |
| Campos novos | Só opcionais ou em `metadata` sem quebrar leitores 1.0.0 |
| Remoção de campo | Proibida em 1.x; só em major via novo RFC |

Providers futuros (Discovery Engine, Dork Engine, Google, GitHub, Scout kiryano, Websites, …) **devem** implementar exatamente este contrato. Quebrar o canônico = violação do Core.

---

## 11. Referências de código

| Artefato | Path |
|----------|------|
| Modelo | `signalhub/core/models/signal.py` |
| Provenance | `signalhub/core/models/provenance.py` |
| Validator | `signalhub/validation/signal_validator.py` |
| Normalizer Core | `signalhub/core/pipeline/stages.py` (`SignalNormalizerStage`) |
| Rules | `signalhub/rules/` |
| Score | `signalhub/scoring/` |
| Telegram | `signalhub/notifications/` |

---

## 12. Critério de aceite desta RFC

1. Documento versionado em `docs/RFC/0001_SIGNAL_SPECIFICATION.md`.
2. Modelo e Validator alinhados aos campos e estados.
3. Pipeline na ordem §8.
4. Testes cobrindo validação, ciclo de vida e serialização canônica.
5. **Nenhum** Provider real (Discovery Engine / Dork / Source Providers) ligado até este contrato estar verde.
