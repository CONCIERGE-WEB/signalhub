# Creating a Ruleset

1. `python -m signalhub.apps.cli create ruleset legaltech`
2. Return `Sequence[Rule]` from `rules()` — explanations must be human-readable
3. Rules feed Telegram / Dashboard / MCP via `rules_applied`

No AI inside rulesets.
