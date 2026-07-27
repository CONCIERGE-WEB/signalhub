from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class LinkedInProvider(BaseProvider):
    provider_id = "linkedin"
    provider_name = "LinkedIn"
    description = "Public professional signals stub — ToS-gated when implemented."
    capability_ids = ("discover_signals", "search_companies")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
