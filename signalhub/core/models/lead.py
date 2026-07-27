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
