# Discovery Engine (Dorking)

Plugin ID: `dork_signals` · provider_id: `dorking`

**Papel oficial:** Discovery Engine certificado do SignalHub (PHASE 3.1).

Reutiliza o motor legado (`engine/core/sources/DorkScanner` + YAML de dorks)
que já cobre Reddit, Reclame Aqui, TikTok/Instagram/Facebook/YouTube/GitHub
(via `site:`), websites e fóruns indexados.

- Emite **somente Signal** (RFC-0001) — nunca Lead.
- Sem live: `search()` → vazio explícito.
- Live: `SIGNALHUB_DORKING_LIVE=1` + `SIGNALHUB_DORKS_CONFIG=path/to/dorks.yaml`.

Ver: `docs/PROVIDER_CERTIFICATION_PROGRAM.md` · `docs/PHASE_3_1_DISCOVERY_ENGINE.md`.
