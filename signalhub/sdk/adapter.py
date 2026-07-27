"""SDK — Adapters push notifications (Telegram, Discord, Slack, …)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

from signalhub.core.models import Signal


class NotificationAdapterPort(ABC):
    """Outbound channel. Does not discover Signals. Does not scrape."""

    @abstractmethod
    def adapter_id(self) -> str:
        ...

    @abstractmethod
    def notify(self, signals: Sequence[Signal]) -> Mapping[str, Any]:
        """Return delivery receipt — never invent Signals."""
        ...
