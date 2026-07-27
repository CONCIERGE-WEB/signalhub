from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class GoogleProvider(BaseProvider):
    provider_id = "google"
    provider_name = "Google"
    description = "Public web discovery stub — respects ToS when implemented."
    capability_ids = ("discover_signals", "search_companies")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
