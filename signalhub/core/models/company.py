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
