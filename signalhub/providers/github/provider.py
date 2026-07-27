from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class GitHubProvider(BaseProvider):
    provider_id = "github"
    provider_name = "GitHub"
    description = "Public repo / org signals stub."
    capability_ids = ("search_companies", "discover_signals")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
