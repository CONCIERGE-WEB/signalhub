from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import HealthStatus, ProviderQuery, RawHit
from signalhub.sdk import ProviderPlugin


class ScoutSignalsProvider(ProviderPlugin):
    """Cliente Zero — Scout as a plugin (not Core).

    Built strictly via SDK: create → validate → doctor.
    No Core backdoor. Real discovery wiring stays inside this plugin only,
    under operator config and source ToS. Until wired: empty explicit.
    """

    # Keep id "scout" so Core capabilities that list provider_ids=("scout", …) resolve.
    provider_id = "scout"
    provider_name = "Scout Signals"
    version = "0.1.0"
    description = (
        "Cliente Zero plugin: public-signal discovery via Scout channel. "
        "Independent plugin — compliance/ToS/rate-limit live here, not in Core."
    )
    capability_ids = ("discover_signals", "search_companies", "search_law_topics")

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail="plugin_cliente_zero — search not wired (empty explicit)",
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        # Cliente Zero dogfood: no invented hits; no Core shortcut.
        _ = query
        return ()
