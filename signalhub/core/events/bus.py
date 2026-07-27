from __future__ import annotations

from collections import defaultdict
from typing import Callable

from .types import DomainEvent, EventType

Handler = Callable[[DomainEvent], None]


class InProcessEventBus:
    """Phase-1 event bus. Swap for broker later without changing publishers."""

    def __init__(self) -> None:
        self._handlers: dict[EventType | None, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: EventType | None, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in list(self._handlers.get(event.type, [])):
            handler(event)
        for handler in list(self._handlers.get(None, [])):
            handler(event)
