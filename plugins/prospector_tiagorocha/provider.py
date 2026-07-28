from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import HealthStatus, ProviderQuery, RawHit
from signalhub.sdk import ProviderPlugin


class ProspectorTiagoRochaProvider(ProviderPlugin):
    """Prospector | Tiago A. Rocha — captação as SDK plugin (not Core).

    Built strictly via SDK: create → validate → doctor.
    No Core backdoor. Real discovery wiring stays inside this plugin only,
    under operator config and source ToS. Until wired: empty explicit.
    """

    provider_id = "prospector_tiagorocha"
    provider_name = "Prospector | Tiago A. Rocha"
    version = "0.1.0"
    description = (
        "Prospector | Tiago A. Rocha: public-signal discovery plugin. "
        "Independent plugin — compliance/ToS/rate-limit live here, not in Core."
    )
    capability_ids = ("discover_signals", "search_companies", "search_law_topics")

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail="plugin_prospector_tiagorocha — search not wired (empty explicit)",
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        # No invented hits; no Core shortcut.
        _ = query
        return ()
