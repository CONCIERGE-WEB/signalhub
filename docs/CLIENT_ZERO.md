# Cliente Zero — dogfooding the SignalHub SDK

**Status:** active  
**Date:** 2026-07-27  
**Rule:** no Core backdoors

| # | Plugin | provider_id | Role |
|---|--------|-------------|------|
| 1 | `plugins/scout_signals` | `scout` | Scout channel |
| 2 | `plugins/dork_signals` | `dorking` | Dork Engine (public-reference search) |

---

## Why

If Scout or Dorking need a private door into Core, the SDK failed.  
Cliente Zero proves the opposite: production channels are **plugins**, built like any third party.

## Path taken (both)

```text
signalhub create provider <name>
  → implement ProviderPlugin
  → signalhub validate plugins/<name>
  → signalhub doctor
  → remove from bootstrap builtins
  → break legacy Core import on purpose
```

## Isolation

| Concern | Where it lives |
|---------|----------------|
| Signal lifecycle / RFC-0001 | Core |
| Scout discovery | `scout_signals` plugin |
| Dork queries, parsing, rate-limit | `dork_signals` plugin |
| ToS of each public engine | Respective plugin |

## Next candidates

1. Optional AI **consumer** plugin (never inside Providers)  
2. Move remaining stub providers (google/websites/…) the same way when they leave “stub”  
3. Marketplace adapters already exemplified under `plugins/example_*`

## Commands

```powershell
cd C:\01_Projetos\06-SignalHub
$env:SIGNALHUB_PLUGINS_DIR=(Resolve-Path .\plugins).Path
python -m signalhub.apps.cli validate plugins\scout_signals
python -m signalhub.apps.cli validate plugins\dork_signals
python -m signalhub.apps.cli doctor
python -m signalhub.apps.cli plugins
```
