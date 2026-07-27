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
