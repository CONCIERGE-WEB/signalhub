# Creating a Provider

1. `python -m signalhub.apps.cli create provider my_source`
2. Edit `plugins/my_source/provider.py` — implement `search(query) -> Sequence[RawHit]`
3. Put source-specific fields only in `RawHit.raw` → becomes Signal `metadata` (RFC-0001)
4. `python -m signalhub.apps.cli validate plugins/my_source`
5. Restart Core / set `SIGNALHUB_PLUGINS_DIR` — Plugin Loader registers automatically

**Rules**

- No LLM calls inside Providers
- No invented hits — empty tuple when offline / not configured
- Respect platform ToS and operator policy
- Do not add arbitrary fields to the Signal root object
