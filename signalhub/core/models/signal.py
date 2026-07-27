from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence

from .common import EntityId
from .provenance import Provenance

SIGNAL_CONTRACT_VERSION = "1.0.0"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SignalStatus(str, Enum):
    DISCOVERED = "discovered"
    NORMALIZED = "normalized"
    DEDUPLICATED = "deduplicated"
    CLASSIFIED = "classified"
    SCORED = "scored"
    STORED = "stored"
    CONSUMED = "consumed"
    ARCHIVED = "archived"


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


# Known categories (null allowed until classified). Unknown after classify → reject.
KNOWN_CATEGORIES: frozenset[str] = frozenset(
    {
        "legal",
        "complaint",
        "supplier_search",
        "commercial_opportunity",
        "consumer",
        "tech",
        "reputation",
        "market",
        "other",
    }
)


@dataclass(slots=True, frozen=True)
class ProcessingStep:
    stage: str
    detail: str = ""
    rules_applied: Sequence[str] = ()
    to_status: str | None = None
    at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "detail": self.detail,
            "rules_applied": list(self.rules_applied),
            "to_status": self.to_status,
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
    """Canonical public evidence — RFC-0001 primary domain object."""

    id: EntityId
    provider: str
    title: str
    source: str = ""
    summary: str = ""
    url: str | None = None
    category: str | None = None
    signal_type: SignalType | str = SignalType.OTHER
    priority: SignalPriority | str = SignalPriority.NORMAL
    score: float | None = None
    confidence: float | None = None
    score_breakdown: ScoreBreakdown | None = None
    rules_applied: Sequence[str] = ()
    history: Sequence[ProcessingStep] = ()
    provenance: Provenance | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    status: SignalStatus | str = SignalStatus.DISCOVERED
    version: str = "1"
    contract_version: str = SIGNAL_CONTRACT_VERSION
    occurred_at: datetime | None = None
    collected_at: datetime = field(default_factory=_utcnow)
    parent_id: EntityId | None = None

    # Legacy alias used in early scaffolds
    @property
    def attributes(self) -> Mapping[str, Any]:
        return self.metadata

    def transition(
        self,
        status: SignalStatus,
        *,
        stage: str,
        detail: str = "",
        rules: Sequence[str] = (),
    ) -> Signal:
        self.status = status
        return self.with_step(
            ProcessingStep(
                stage=stage,
                detail=detail,
                rules_applied=rules,
                to_status=status.value,
            )
        )

    def with_step(self, step: ProcessingStep) -> Signal:
        self.history = (*self.history, step)
        if step.rules_applied:
            self.rules_applied = tuple(
                dict.fromkeys([*self.rules_applied, *step.rules_applied])
            )
        return self

    def bump_version(self, *, reason: str) -> Signal:
        """Create a new logical version marker (Capabilities must not silently mutate)."""
        try:
            n = int(self.version)
            self.version = str(n + 1)
        except ValueError:
            self.version = f"{self.version}.1"
        self.with_step(
            ProcessingStep(stage="version_bump", detail=reason, to_status=str(self.status_value))
        )
        return self

    @property
    def status_value(self) -> str:
        return self.status.value if isinstance(self.status, SignalStatus) else str(self.status)

    def to_dict(self) -> dict[str, Any]:
        """Canonical serialization — RFC-0001. MCP/REST/Telegram use this only."""
        st = (
            self.signal_type.value
            if isinstance(self.signal_type, SignalType)
            else str(self.signal_type)
        )
        pr = (
            self.priority.value
            if isinstance(self.priority, SignalPriority)
            else str(self.priority)
        )
        return {
            "id": str(self.id),
            "provider": self.provider,
            "source": self.source,
            "category": self.category,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "collected_at": self.collected_at.isoformat(),
            "score": self.score,
            "priority": pr,
            "confidence": self.confidence,
            "rules_applied": list(self.rules_applied),
            "history": [h.to_dict() for h in self.history],
            "metadata": dict(self.metadata),
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "status": self.status_value,
            "version": self.version,
            "contract_version": self.contract_version,
            "signal_type": st,
            "score_breakdown": self.score_breakdown.to_dict() if self.score_breakdown else None,
            "parent_id": str(self.parent_id) if self.parent_id else None,
        }


PublicSignal = Signal
