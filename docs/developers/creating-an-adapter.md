# Creating an Adapter

1. `python -m signalhub.apps.cli create adapter discord_alerts`
2. Implement `NotificationAdapterPort.notify(signals)`
3. Prefer formatting with `signal.rules_applied` (no black-box scores)

Adapters are outbound only — never discovery Providers.
