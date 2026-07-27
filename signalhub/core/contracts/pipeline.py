from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, MutableMapping

from signalhub.core.models import Signal


@dataclass
class PipelineContext:
    capability_id: str
    signals: list[Signal] = field(default_factory=list)
    attributes: MutableMapping[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def leads(self) -> list[Signal]:
        """Deprecated alias — prefer .signals."""
        return self.signals

    @leads.setter
    def leads(self, value: list[Signal]) -> None:
        self.signals = value

    def snapshot(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "signal_count": len(self.signals),
            "attributes": dict(self.attributes),
            "errors": list(self.errors),
        }


class PipelineStage(ABC):
    name: str = "stage"

    @abstractmethod
    def process(self, ctx: PipelineContext) -> PipelineContext:
        ...
