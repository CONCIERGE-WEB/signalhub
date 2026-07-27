from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True, frozen=True)
class Provenance:
    """Origin of every fact — RFC-0001 audit trail."""

    provider_id: str
    collected_at: datetime = field(default_factory=_utcnow)
    source_url: str | None = None
    source_kind: str = "public"
    origin: str | None = None
    content_hash: str | None = None
    pipeline_version: str = "signalhub-0.2.0+contract-1.0.0"
    rules_executed: Sequence[str] = ()
    operator_config_ref: str | None = None
    raw_fingerprint: str | None = None
    extras: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "collected_at": self.collected_at.isoformat(),
            "source_url": self.source_url,
            "source_kind": self.source_kind,
            "origin": self.origin,
            "content_hash": self.content_hash,
            "pipeline_version": self.pipeline_version,
            "rules_executed": list(self.rules_executed),
            "operator_config_ref": self.operator_config_ref,
            "raw_fingerprint": self.raw_fingerprint or self.content_hash,
            "extras": dict(self.extras),
        }
