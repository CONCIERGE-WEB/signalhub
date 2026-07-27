"""Provider contract — discovers public RawHits → canonical Signals. No AI."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from signalhub.core.models import Provenance, Signal


@dataclass(slots=True, frozen=True)
class ProviderQuery:
    capability_id: str
    terms: Sequence[str] = ()
    geo: str | None = None
    category: str | None = None
    limit: int = 40
    extras: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RawHit:
    external_id: str
    title: str = ""
    url: str | None = None
    snippet: str = ""
    signal_type: str = "other"
    category: str | None = None
    source: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)
    provenance: Provenance | None = None


@dataclass(slots=True, frozen=True)
class ProviderMetadata:
    provider_id: str
    name: str
    version: str
    capabilities: Sequence[str]
    description: str = ""
    requires_network: bool = True
    respects_robots: bool = True
    enabled_by_default: bool = False


@dataclass(slots=True, frozen=True)
class HealthStatus:
    ok: bool
    provider_id: str
    detail: str = ""
    latency_ms: float | None = None


class Provider(ABC):
    """Channel adapter. Providers MUST NOT call LLMs or any AI API."""

    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        ...

    @abstractmethod
    def healthcheck(self) -> HealthStatus:
        ...

    @abstractmethod
    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        ...

    @abstractmethod
    def collect(self, hits: Sequence[RawHit]) -> Sequence[RawHit]:
        ...

    @abstractmethod
    def normalize(self, hits: Sequence[RawHit]) -> Sequence[Signal]:
        ...

    @abstractmethod
    def validate(self, signals: Sequence[Signal]) -> Sequence[Signal]:
        ...

    @abstractmethod
    def enrich(self, signals: Sequence[Signal]) -> Sequence[Signal]:
        """Non-AI enrichment only (URL normalize, source tag, etc.)."""
