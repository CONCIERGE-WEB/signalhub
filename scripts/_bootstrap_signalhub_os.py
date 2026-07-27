"""One-shot bootstrap for signalhub/ OS package. Safe to re-run (overwrite)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "signalhub"


def w(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    if not content.endswith("\n"):
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


def main() -> None:
    files: dict[str, str] = {}

    files["__init__.py"] = '''\
"""SignalHub — Operating System for Commercial Intelligence.

MCP, REST, CLI and Dashboard are interfaces over the same Core.
Business rules live in Core + Capabilities — never in the MCP layer.
"""
from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]
'''

    files["py.typed"] = ""

    files["core/__init__.py"] = '"""Core — orchestrator, registry, contracts, pipeline, events."""\n'

    files["core/models/__init__.py"] = '''\
"""Canonical domain models — single source of truth across interfaces."""
from .common import EntityId, GeoHint, VerticalId
from .company import Company
from .lead import Lead, LeadStatus
from .provenance import Provenance
from .signal import PublicSignal

__all__ = [
    "Company",
    "EntityId",
    "GeoHint",
    "Lead",
    "LeadStatus",
    "Provenance",
    "PublicSignal",
    "VerticalId",
]
'''

    files["core/models/common.py"] = '''\
from __future__ import annotations

from typing import NewType

EntityId = NewType("EntityId", str)
VerticalId = NewType("VerticalId", str)
GeoHint = NewType("GeoHint", str)
'''

    files["core/models/provenance.py"] = '''\
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True, frozen=True)
class Provenance:
    """Origin of every fact — required for audit and compliance."""

    provider_id: str
    collected_at: datetime = field(default_factory=_utcnow)
    source_url: str | None = None
    source_kind: str = "public"
    operator_config_ref: str | None = None
    raw_fingerprint: str | None = None
    extras: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "collected_at": self.collected_at.isoformat(),
            "source_url": self.source_url,
            "source_kind": self.source_kind,
            "operator_config_ref": self.operator_config_ref,
            "raw_fingerprint": self.raw_fingerprint,
            "extras": dict(self.extras),
        }
'''

    files["core/models/lead.py"] = '''\
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .common import EntityId, GeoHint, VerticalId
from .provenance import Provenance


class LeadStatus(str, Enum):
    CANDIDATE = "candidate"
    ENRICHED = "enriched"
    SCORED = "scored"
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    STORED = "stored"


@dataclass(slots=True)
class Lead:
    """Canonical lead — all interfaces (MCP/API/CLI/Dashboard) use this model."""

    id: EntityId
    title: str
    status: LeadStatus = LeadStatus.CANDIDATE
    url: str | None = None
    snippet: str = ""
    geo: GeoHint | None = None
    vertical: VerticalId | None = None
    company_id: EntityId | None = None
    score: float | None = None
    tags: Sequence[str] = ()
    provenance: Sequence[Provenance] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "status": self.status.value,
            "url": self.url,
            "snippet": self.snippet,
            "geo": str(self.geo) if self.geo else None,
            "vertical": str(self.vertical) if self.vertical else None,
            "company_id": str(self.company_id) if self.company_id else None,
            "score": self.score,
            "tags": list(self.tags),
            "provenance": [p.to_dict() for p in self.provenance],
            "attributes": dict(self.attributes),
        }
'''

    files["core/models/company.py"] = '''\
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .common import EntityId, GeoHint
from .provenance import Provenance


@dataclass(slots=True)
class Company:
    id: EntityId
    name: str
    domain: str | None = None
    geo: GeoHint | None = None
    tech_stack: Sequence[str] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    provenance: Sequence[Provenance] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "domain": self.domain,
            "geo": str(self.geo) if self.geo else None,
            "tech_stack": list(self.tech_stack),
            "attributes": dict(self.attributes),
            "provenance": [p.to_dict() for p in self.provenance],
        }
'''

    files["core/models/signal.py"] = '''\
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .common import EntityId
from .provenance import Provenance


@dataclass(slots=True)
class PublicSignal:
    """Public market/social/legal signal — never private account data."""

    id: EntityId
    kind: str
    summary: str
    url: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)
    provenance: Provenance | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "kind": self.kind,
            "summary": self.summary,
            "url": self.url,
            "attributes": dict(self.attributes),
            "provenance": self.provenance.to_dict() if self.provenance else None,
        }
'''

    # contracts
    files["core/contracts/__init__.py"] = '''\
"""Interfaces — Providers, Capabilities, Pipeline, AI, Storage."""
from .ai import (
    ClassificationPort,
    EmbeddingsPort,
    LLMPort,
    ProposalGeneratorPort,
    RerankingPort,
    ReportGeneratorPort,
    SummariesPort,
)
from .capability import Capability, CapabilityHandler, CapabilityResult
from .pipeline import PipelineContext, PipelineStage
from .provider import (
    HealthStatus,
    Provider,
    ProviderMetadata,
    ProviderQuery,
    RawHit,
)
from .storage import LeadStore, VectorStore

__all__ = [
    "Capability",
    "CapabilityHandler",
    "CapabilityResult",
    "ClassificationPort",
    "EmbeddingsPort",
    "HealthStatus",
    "LLMPort",
    "LeadStore",
    "PipelineContext",
    "PipelineStage",
    "ProposalGeneratorPort",
    "Provider",
    "ProviderMetadata",
    "ProviderQuery",
    "RawHit",
    "RerankingPort",
    "ReportGeneratorPort",
    "SummariesPort",
    "VectorStore",
]
'''

    files["core/contracts/provider.py"] = '''\
"""Provider contract — no provider knows another provider."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from signalhub.core.models import Lead, Provenance


@dataclass(slots=True, frozen=True)
class ProviderQuery:
    """Discovery request shared by all providers."""

    capability_id: str
    terms: Sequence[str] = ()
    geo: str | None = None
    limit: int = 40
    extras: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RawHit:
    """Pre-canonical hit from a provider source."""

    external_id: str
    title: str = ""
    url: str | None = None
    snippet: str = ""
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
    """Every channel implements this interface.

    Communication with other providers is forbidden — Core orchestrates.
    Providers must NOT call LLMs directly (use Core AI ports via enrichment).
    """

    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        ...

    @abstractmethod
    def healthcheck(self) -> HealthStatus:
        ...

    @abstractmethod
    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        """Locate public references / candidates."""

    @abstractmethod
    def collect(self, hits: Sequence[RawHit]) -> Sequence[RawHit]:
        """Fetch or expand hits without inventing data."""

    @abstractmethod
    def normalize(self, hits: Sequence[RawHit]) -> Sequence[Lead]:
        """Map to canonical Lead model."""

    @abstractmethod
    def validate(self, leads: Sequence[Lead]) -> Sequence[Lead]:
        """Compliance / public-source / schema filters."""

    @abstractmethod
    def enrich(self, leads: Sequence[Lead]) -> Sequence[Lead]:
        """Provider-local light enrichment only — heavy AI stays in Core."""
'''

    files["core/contracts/capability.py"] = '''\
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(slots=True, frozen=True)
class Capability:
    """A product capability exposed uniformly to Dashboard/REST/MCP/SDK."""

    id: str
    name: str
    description: str
    input_schema: Mapping[str, Any]
    provider_ids: Sequence[str] = ()
    enabled: bool = True
    mcp_tool_name: str | None = None

    @property
    def tool_name(self) -> str:
        return self.mcp_tool_name or self.id


@dataclass(slots=True)
class CapabilityResult:
    capability_id: str
    status: str
    items: Sequence[Mapping[str, Any]] = ()
    meta: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "status": self.status,
            "count": len(self.items),
            "items": list(self.items),
            "meta": dict(self.meta),
        }


class CapabilityHandler(ABC):
    """Executes a capability via Core (never via MCP layer logic)."""

    @abstractmethod
    def capability(self) -> Capability:
        ...

    @abstractmethod
    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        ...
'''

    files["core/contracts/pipeline.py"] = '''\
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping, Sequence

from signalhub.core.models import Lead


@dataclass
class PipelineContext:
    capability_id: str
    leads: list[Lead] = field(default_factory=list)
    attributes: MutableMapping[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def snapshot(self) -> Mapping[str, Any]:
        return {
            "capability_id": self.capability_id,
            "lead_count": len(self.leads),
            "attributes": dict(self.attributes),
            "errors": list(self.errors),
        }


class PipelineStage(ABC):
    """One stage in: Provider → … → Storage → Embeddings → Knowledge Graph."""

    name: str = "stage"

    @abstractmethod
    def process(self, ctx: PipelineContext) -> PipelineContext:
        ...
'''

    files["core/contracts/ai.py"] = '''\
"""AI ports — isolated from Providers. Implementations live under signalhub.ai."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class LLMPort(ABC):
    @abstractmethod
    def complete(self, prompt: str, *, options: Mapping[str, Any] | None = None) -> str:
        ...


class EmbeddingsPort(ABC):
    @abstractmethod
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        ...


class RerankingPort(ABC):
    @abstractmethod
    def rerank(self, query: str, documents: Sequence[str]) -> Sequence[int]:
        ...


class SummariesPort(ABC):
    @abstractmethod
    def summarize(self, text: str, *, options: Mapping[str, Any] | None = None) -> str:
        ...


class ClassificationPort(ABC):
    @abstractmethod
    def classify(self, text: str, labels: Sequence[str]) -> Mapping[str, float]:
        ...


class ProposalGeneratorPort(ABC):
    @abstractmethod
    def generate(self, context: Mapping[str, Any]) -> str:
        ...


class ReportGeneratorPort(ABC):
    @abstractmethod
    def generate(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        ...
'''

    files["core/contracts/storage.py"] = '''\
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from signalhub.core.models import Lead
from signalhub.core.models.common import EntityId


class LeadStore(ABC):
    @abstractmethod
    def upsert(self, leads: Sequence[Lead]) -> int:
        ...

    @abstractmethod
    def get(self, lead_id: EntityId) -> Lead | None:
        ...


class VectorStore(ABC):
    @abstractmethod
    def upsert_embeddings(
        self,
        ids: Sequence[str],
        vectors: Sequence[Sequence[float]],
    ) -> int:
        ...
'''

    for rel, content in files.items():
        w(rel, content)
    print(f"phase1: {len(files)} files -> {ROOT}")


if __name__ == "__main__":
    main()
