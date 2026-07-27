from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class SchedulerPort(ABC):
    @abstractmethod
    def schedule(self, name: str, fn: Callable[[], None], *, every_seconds: float) -> None:
        ...

    @abstractmethod
    def cancel(self, name: str) -> None:
        ...


class NullScheduler(SchedulerPort):
    """Explicit no-op until a real scheduler is wired."""

    def schedule(self, name: str, fn: Callable[[], None], *, every_seconds: float) -> None:
        _ = (name, fn, every_seconds)

    def cancel(self, name: str) -> None:
        _ = name
