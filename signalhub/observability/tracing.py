from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class Span:
    name: str
    started_at: float = field(default_factory=time.perf_counter)
    ended_at: float | None = None
    status: str = "running"
    detail: str = ""

    def ok(self) -> None:
        self.ended_at = time.perf_counter()
        self.status = "ok"

    def fail(self, detail: str) -> None:
        self.ended_at = time.perf_counter()
        self.status = "error"
        self.detail = detail

    @property
    def duration_ms(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000.0


@dataclass
class ExecutionTrace:
    operation: str
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    spans: list[Span] = field(default_factory=list)
    _started: float = field(default_factory=time.perf_counter)
    _ended: float | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def start_span(self, name: str) -> Span:
        span = Span(name=name)
        self.spans.append(span)
        return span

    def __enter__(self) -> ExecutionTrace:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self._ended = time.perf_counter()
        return None

    @property
    def duration_ms(self) -> float | None:
        end = self._ended if self._ended is not None else time.perf_counter()
        return (end - self._started) * 1000.0
