# Arquitetura P1 — SignalHub como plataforma de sinais (sem IA)

**Status:** consolidado  
**Versão pacote:** 0.2.0  
**Data:** 2026-07-27  
**Repo oficial:** `06-SignalHub`  
**Consumidor:** Lex Rocha via adapter (`docs/INTEGRACAO_LEXROCHA_SIGNALHUB.md` no Lex)

---

## Identidade

O SignalHub **não** é um sistema de IA.

- Sem LLMs no Core
- Sem dependência de OpenAI / Claude / Gemini
- Motor **determinístico** em Python
- IA, se existir, é **consumidor opcional** (REST/MCP/CLI) — nunca Provider

## Objeto principal: `Signal`

Evidência pública observável (pedido de ajuda, reclamação, oportunidade, publicação jurídica, tendência, reputação, …).

`Lead` = interpretação opcional de um `Signal` (`Lead.from_signal`).

## Pipeline

```
Provider → Signal → Normalizer → Deduplicator
  → Rule Engine → Score Engine → Storage
  → Capabilities → REST / CLI / Dashboard / Telegram / MCP
```

## Rule Engine + Score Engine

Camada `signalhub/rules/` — palavras-chave, origem, recência, reputação da fonte.  
`signalhub/scoring/` agrega pesos em score + confiança do algoritmo + justificativa.

Nenhuma decisão crítica depende de LLM.

## Telegram

`signalhub/notifications/` — **Notification Adapter** (não Provider de descoberta).

Cada notificação: tipo, origem, score, confiança, justificativa, categoria, prioridade, ações.  
Agregação anti-spam por janela.

## MCP

Tools projetadas das Capabilities. MCP **não** faz scraping — só chama Core:

`discover_signals`, `search_signals`, `search_by_category`, `list_sources`,  
`get_provider_status`, `get_metrics`, `get_recent_signals`,  
`search_companies`, `search_law_topics`, `analyze_signal`  
(+ alias legado `discover_leads`).

## Observabilidade do Signal

Cada Signal carrega: provider (provenance), timestamp, fonte, URL, categoria,  
regras aplicadas, score, `history` (`ProcessingStep`).

## Próximo passo (ainda não iniciado)

Integração **real** Discovery Engine / Dork Engine atrás do contrato Provider — feature flag  
`p1_scout_dorking_real=false` até lá.
