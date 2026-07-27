# Creating a Capability

1. `python -m signalhub.apps.cli create capability my_cap`
2. Implement `capability()` + `execute(arguments)`
3. Return `CapabilityResult` with **canonical** `Signal.to_dict()` items when exposing Signals
4. Register via `plugin.yaml` → appears as MCP tool automatically

Capabilities must not scrape and must not mutate stored Signals.
