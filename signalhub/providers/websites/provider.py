from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class WebsitesProvider(BaseProvider):
    provider_id = "websites"
    provider_name = "Websites"
    description = "Website analysis stub — public pages only."
    capability_ids = ("search_companies", "discover_signals")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
