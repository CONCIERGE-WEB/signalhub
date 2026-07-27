from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(slots=True, frozen=True)
class RateLimit:
    requests_per_minute: int = 30
    burst: int = 5


@dataclass
class SecurityPolicy:
    """Operator-controlled gates — disable providers, rate-limit, audit."""

    enabled_providers: set[str] | None = None  # None = all registered
    disabled_providers: set[str] = field(default_factory=set)
    enabled_capabilities: set[str] | None = None
    disabled_capabilities: set[str] = field(default_factory=set)
    rate_limits: Mapping[str, RateLimit] = field(default_factory=dict)
    require_public_source: bool = True
    human_in_the_loop: bool = True

    def is_provider_allowed(self, provider_id: str) -> bool:
        pid = provider_id.strip().lower()
        if pid in {d.lower() for d in self.disabled_providers}:
            return False
        if self.enabled_providers is None:
            return True
        return pid in {e.lower() for e in self.enabled_providers}

    def is_capability_allowed(self, capability_id: str) -> bool:
        cid = capability_id.strip().lower()
        if cid in {d.lower() for d in self.disabled_capabilities}:
            return False
        if self.enabled_capabilities is None:
            return True
        return cid in {e.lower() for e in self.enabled_capabilities}

    def rate_limit_for(self, provider_id: str) -> RateLimit:
        return self.rate_limits.get(provider_id, RateLimit())
