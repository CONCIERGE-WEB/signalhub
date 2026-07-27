"""Bootstrap P1 Signal-centric Core (deterministic, no LLM)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "signalhub"


def w(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


FILES: dict[str, str] = {}

FILES["__init__.py"] = '''\
"""SignalHub — deterministic public-signal intelligence platform.

Not an AI product. No LLMs inside the Core.
APIs, CLI, Dashboard, Telegram and MCP consume the same Core.
"""
from __future__ import annotations

__version__ = "0.2.0"
__all__ = ["__version__"]
'''

FILES["core/models/signal.py"] = '''\
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence

from .common import EntityId
from .provenance import Provenance


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SignalType(str, Enum):
    HELP_REQUEST = "help_request"
    PUBLIC_COMPLAINT = "public_complaint"
    SUPPLIER_SEARCH = "supplier_search"
    LEGAL_PUBLICATION = "legal_publication"
    TECH_CHANGE = "tech_change"
    COMMERCIAL_OPPORTUNITY = "commercial_opportunity"
    TREND = "trend"
    REPUTATION = "reputation"
    OTHER = "other"


class SignalPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(slots=True, frozen=True)
class ProcessingStep:
    stage: str
    detail: str = ""
    rules_applied: Sequence[str] = ()
    at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "detail": self.detail,
            "rules_applied": list(self.rules_applied),
            "at": self.at.isoformat(),
        }


@dataclass(slots=True, frozen=True)
class ScoreBreakdown:
    total: float
    confidence: float
    components: Mapping[str, float] = field(default_factory=dict)
    justification: Sequence[str] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "confidence": self.confidence,
            "components": dict(self.components),
            "justification": list(self.justification),
        }


@dataclass(slots=True)
class Signal:
    """Canonical public evidence — primary domain object of SignalHub."""

    id: EntityId
    signal_type: SignalType | str
    title: str
    summary: str = ""
    url: str | None = None
    category: str | None = None
    source: str | None = None
    priority: SignalPriority | str = SignalPriority.NORMAL
    score: float | None = None
    confidence: float | None = None
    score_breakdown: ScoreBreakdown | None = None
    rules_applied: Sequence[str] = ()
    history: Sequence[ProcessingStep] = ()
    provenance: Provenance | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=_utcnow)

    def with_step(self, step: ProcessingStep) -> Signal:
        self.history = (*self.history, step)
        if step.rules_applied:
            self.rules_applied = tuple(
                dict.fromkeys([*self.rules_applied, *step.rules_applied])
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        st = self.signal_type.value if isinstance(self.signal_type, SignalType) else str(self.signal_type)
        pr = self.priority.value if isinstance(self.priority, SignalPriority) else str(self.priority)
        return {
            "id": str(self.id),
            "signal_type": st,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "category": self.category,
            "source": self.source,
            "priority": pr,
            "score": self.score,
            "confidence": self.confidence,
            "score_breakdown": self.score_breakdown.to_dict() if self.score_breakdown else None,
            "rules_applied": list(self.rules_applied),
            "history": [h.to_dict() for h in self.history],
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "attributes": dict(self.attributes),
            "collected_at": self.collected_at.isoformat(),
        }


# Backward-compatible alias used in early scaffolds
PublicSignal = Signal
'''

FILES["core/models/lead.py"] = '''\
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .common import EntityId, GeoHint, VerticalId
from .provenance import Provenance
from .signal import Signal


class LeadStatus(str, Enum):
    CANDIDATE = "candidate"
    ENRICHED = "enriched"
    SCORED = "scored"
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    STORED = "stored"


@dataclass(slots=True)
class Lead:
    """Optional commercial interpretation of a Signal — not the primary object."""

    id: EntityId
    title: str
    signal_id: EntityId | None = None
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

    @classmethod
    def from_signal(cls, signal: Signal, *, vertical: str | None = None) -> Lead:
        prov = (signal.provenance,) if signal.provenance else ()
        return cls(
            id=EntityId(f"lead:{signal.id}"),
            signal_id=signal.id,
            title=signal.title,
            url=signal.url,
            snippet=signal.summary,
            vertical=VerticalId(vertical) if vertical else None,
            score=signal.score,
            status=LeadStatus.CANDIDATE,
            provenance=prov,
            attributes={
                "signal_type": (
                    signal.signal_type.value
                    if hasattr(signal.signal_type, "value")
                    else str(signal.signal_type)
                ),
                "category": signal.category,
                "from_signal": True,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "signal_id": str(self.signal_id) if self.signal_id else None,
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

FILES["core/models/__init__.py"] = '''\
"""Canonical domain models — Signal is primary; Lead is an interpretation."""
from .common import EntityId, GeoHint, VerticalId
from .company import Company
from .lead import Lead, LeadStatus
from .provenance import Provenance
from .signal import (
    ProcessingStep,
    PublicSignal,
    ScoreBreakdown,
    Signal,
    SignalPriority,
    SignalType,
)

__all__ = [
    "Company",
    "EntityId",
    "GeoHint",
    "Lead",
    "LeadStatus",
    "ProcessingStep",
    "Provenance",
    "PublicSignal",
    "ScoreBreakdown",
    "Signal",
    "SignalPriority",
    "SignalType",
    "VerticalId",
]
'''

for rel, content in FILES.items():
    w(rel, content)
print(f"p1-models: {len(FILES)} files")
