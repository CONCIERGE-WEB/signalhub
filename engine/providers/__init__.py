"""Registry de providers — Scout e stubs futuros."""
from __future__ import annotations

from .base import LeadDiscoveryProvider, LeadSink, LeadCandidate, ProviderQuery
from .scout.provider import ScoutLeadProvider

__all__ = [
    "LeadDiscoveryProvider",
    "LeadSink",
    "LeadCandidate",
    "ProviderQuery",
    "ScoutLeadProvider",
    "get_provider",
]

_REGISTRY: dict[str, type[LeadDiscoveryProvider]] = {
    "scout": ScoutLeadProvider,
}


def get_provider(name: str) -> LeadDiscoveryProvider:
    key = (name or "").strip().lower()
    cls = _REGISTRY.get(key)
    if cls is None:
        raise KeyError(
            f"provider '{name}' não registrado. Disponíveis: {sorted(_REGISTRY)}"
        )
    return cls()
