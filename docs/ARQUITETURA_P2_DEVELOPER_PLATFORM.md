# P2 — Developer Platform

**Status:** delivered (foundation)  
**Date:** 2026-07-27

## Goal

Allow any developer to create Providers, Capabilities, Adapters, Consumers, and Rulesets **without modifying Core**.

## Delivered

| Piece | Location |
|-------|----------|
| SDK | `signalhub/sdk/` |
| Plugin manifest + loader | `signalhub/plugins/` |
| Scaffold CLI | `signalhub create …` |
| validate / doctor / contract-check | CLI |
| Example plugins | `plugins/example_*` |
| Docs | `docs/developers/`, `docs/MARKETPLACE.md` |

## Non-goals (this phase)

- Real Discovery Engine / Dork Engine wiring
- LLM features
- Publishing to a public package index (roadmap)

## Stability

Core + RFC-0001 are the stable surface. Plugins are the extension surface.
