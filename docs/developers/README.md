# SignalHub Developer Guide

**Audience:** developers extending SignalHub without modifying Core.  
**Contract:** [RFC-0001](../RFC/0001_SIGNAL_SPECIFICATION.md)  
**SDK:** `signalhub.sdk`

---

## Positioning

SignalHub is a **deterministic signal-processing framework**.

It is **not** a repository of scrapers. Integrations with public sources are **independent plugins**, each responsible for complying with the terms of use and policies of its source platforms. The Core only processes canonical **Signals**.

---

## Architecture for extenders

```
Your Plugin (plugin.yaml)
        ↓
Plugin Loader
        ↓
Registry (Providers / Capabilities / Adapters / Consumers / Rulesets)
        ↓
Core Pipeline (Validator → … → Storage)
        ↓
REST · CLI · Dashboard · Telegram · MCP
```

**Never edit** `signalhub/core/` to add a source or sink. Use the SDK + plugin manifest.

---

## Quick start

```powershell
cd C:\01_Projetos\06-SignalHub
python -m signalhub.apps.cli create provider my_source
python -m signalhub.apps.cli validate plugins\my_source
python -m signalhub.apps.cli doctor
python -m signalhub.apps.cli contract-check
```

Environment:

```text
SIGNALHUB_PLUGINS_DIR=C:\path\to\plugins
```

---

## Create a Provider

See [creating-a-provider.md](./creating-a-provider.md).

Subclass `signalhub.sdk.ProviderPlugin` (`BaseProvider`). Implement `search()` returning `RawHit`s — Core normalizes to RFC-0001 Signals. Return empty when not configured. **Never invent data.**

## Create a Capability

See [creating-a-capability.md](./creating-a-capability.md).

Capabilities **consume / query / derive**. They must not mutate stored Signals; derive a new version if needed.

## Create an Adapter

See [creating-an-adapter.md](./creating-an-adapter.md).

Outbound notifications (Discord, Slack, …). Use `rules_applied` for human-readable explanations.

## Create a Consumer

CRM, webhook, email, Notion, HubSpot — sinks that receive Signals.

## Create a Ruleset

See [creating-a-ruleset.md](./creating-a-ruleset.md).

Deterministic rules only — no LLMs in Core plugins that claim to be rules.

## Publish a plugin

See [publishing-plugins.md](./publishing-plugins.md).

---

## CLI reference

| Command | Purpose |
|---------|---------|
| `signalhub create provider NAME` | Scaffold provider plugin |
| `signalhub create capability NAME` | Scaffold capability |
| `signalhub create adapter NAME` | Scaffold notification adapter |
| `signalhub create consumer NAME` | Scaffold consumer |
| `signalhub create ruleset NAME` | Scaffold ruleset |
| `signalhub validate PATH` | Manifest + contract checks |
| `signalhub test provider PATH` | Same contract suite |
| `signalhub doctor` | Core + plugins health |
| `signalhub contract-check` | RFC-0001 check |
| `signalhub plugins` | List discovered plugins |

---

## Marketplace vision

See [../MARKETPLACE.md](../MARKETPLACE.md) — capabilities catalog (RSS, alerts, CRM, Discord, …) as **plugins**, not Core modules.
