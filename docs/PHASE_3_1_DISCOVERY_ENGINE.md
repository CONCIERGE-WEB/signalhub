# PHASE 3.1 — First Certified Discovery Engine

| Campo | Valor |
|-------|--------|
| **Nome** | First Certified Discovery Engine |
| **Status** | Concluída (contrato + adapter) — 2026-07-29 |
| **Provider certificado** | **Discovery Engine (Dorking)** · `dork_signals` / `dorking` |
| **Core** | Intocado (RFC / Capabilities / contrato intactos) |

---

## Decisão

O Dorking já existente (`engine` + YAML multi-fonte) **é** o Discovery Engine.
Não criar Scout, Google plugin, nem dez Source Providers agora.

Cobertura via dorks/`site:` + Reddit/HN/RSS: Reddit, Reclame Aqui, TikTok,
Instagram, Facebook, YouTube, GitHub, websites, fóruns, páginas indexadas.

---

## O que foi entregue

1. Adapter `plugins/dork_signals/` → `RawHit` → `Signal` RFC-0001 (nunca Lead).
2. Bridge reutiliza `DorkScanner` (sem duplicar dorks).
3. Live opcional: `SIGNALHUB_DORKING_LIVE=1` + `SIGNALHUB_DORKS_CONFIG`.
4. Sem live: **vazio explícito** (métricas zeradas — sem inventar).
5. Certification Level 1 no health + `admin_snapshot.discovery_engine`.
6. Telegram Notification Adapter: categoria, origem, score, prioridade, rules, link, resumo, justificativa.
7. Dashboard `/discovery-engine` (nova tela; dashboard existente intacto).

---

## Fila atualizada

1. **Discovery Engine (Dorking)** — Certified Level 1  
2. Próximos Source Providers oficiais (APIs) — só quando fizer sentido  
3. Scout (kiryano) — terceiros MIT, depois  

Prospector permanece Cliente Zero de marca; **não** é o primeiro certificado nesta fase.
