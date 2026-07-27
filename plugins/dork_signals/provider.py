from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import HealthStatus, ProviderQuery, RawHit
from signalhub.sdk import ProviderPlugin


class DorkSignalsProvider(ProviderPlugin):
    """Cliente Zero #2 — Dork Engine as a plugin (not Core).

    Public-reference discovery under operator config, rate limits and ToS.
    Parsing / query shaping / backoff stay in this plugin only.
    Until wired: empty explicit — never invent Signals.
    """

    provider_id = "dorking"
    provider_name = "Dork Signals"
    version = "0.1.0"
    description = (
        "Cliente Zero plugin: specialized public-reference discovery (Dork Engine). "
        "Rate-limit, parsing and source ToS live here — Core only orchestrates Signals."
    )
    capability_ids = (
        "discover_signals",
        "search_law_topics",
        "search_signals",
    )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail="plugin_cliente_zero — dork search not wired (empty explicit)",
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
