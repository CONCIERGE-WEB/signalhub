from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class InMemoryMetrics:
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    timings_ms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def incr(self, name: str, value: float = 1.0) -> None:
        self.counters[name] += value

    def timing(self, name: str, ms: float) -> None:
        self.timings_ms[name].append(ms)
