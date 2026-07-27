"""SDK — Consumers react to Signals (CRM, webhook, email, …)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

from signalhub.core.models import Signal


class SignalConsumer(ABC):
    """Downstream sink. Capabilities may call consumers; Core does not hardcode them."""

    @abstractmethod
    def consumer_id(self) -> str:
        ...

    @abstractmethod
    def consume(self, signals: Sequence[Signal]) -> Mapping[str, Any]:
        ...
