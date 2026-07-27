from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


class EventType(str, Enum):
    LEAD_FOUND = "lead.found"
    LEAD_ENRICHED = "lead.enriched"
    LEAD_SCORED = "lead.scored"
    LEAD_STORED = "lead.stored"
    PROVIDER_FAILED = "provider.failed"
    CAPABILITY_EXECUTED = "capability.executed"
    AUDIT = "audit"


@dataclass(slots=True, frozen=True)
class DomainEvent:
    type: EventType
    payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
