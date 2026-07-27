from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.sdk import ProviderPlugin


class ExampleRssProvider(ProviderPlugin):
    """Public-feed style Provider scaffold.

    SignalHub is a signal-processing framework. This plugin is an independent
    extension — wire only sources allowed by your operator config and ToS.
    """

    provider_id = "example_rss"
    provider_name = "Example RSS"
    description = "Didactic provider — returns empty until a lawful public feed is configured."
    capability_ids = ("discover_signals",)

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
