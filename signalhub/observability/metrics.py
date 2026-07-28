"""Métricas internas da plataforma (sem Prometheus)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class InMemoryMetrics:
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    timings_ms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    _lock: Lock = field(default_factory=Lock, repr=False)

    def incr(self, name: str, value: float = 1.0) -> None:
        with self._lock:
            self.counters[name] += value

    def timing(self, name: str, ms: float) -> None:
        with self._lock:
            self.timings_ms[name].append(float(ms))

    def reset(self) -> None:
        with self._lock:
            self.counters.clear()
            self.timings_ms.clear()

    def avg_ms(self, name: str) -> float | None:
        with self._lock:
            vals = self.timings_ms.get(name) or []
            if not vals:
                return None
            return round(sum(vals) / len(vals), 4)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            counters = {k: float(v) for k, v in self.counters.items()}
            avgs = {
                k: round(sum(v) / len(v), 4) if v else None
                for k, v in self.timings_ms.items()
            }
        provider_avgs = {
            k.replace("provider_latency_ms:", ""): v
            for k, v in avgs.items()
            if k.startswith("provider_latency_ms:") and v is not None
        }
        return {
            "signals_produced": int(counters.get("signals_produced", 0)),
            "signals_discarded": int(counters.get("signals_discarded", 0)),
            "signals_duplicated": int(counters.get("signals_duplicated", 0)),
            "signals_invalid": int(counters.get("signals_invalid", 0)),
            "rules_applied": int(counters.get("rules_applied", 0)),
            "rule_engine_avg_ms": avgs.get("rule_engine_ms"),
            "score_engine_avg_ms": avgs.get("score_engine_ms"),
            "provider_avg_ms": provider_avgs,
            "counters": counters,
            "timings_avg_ms": {k: v for k, v in avgs.items() if v is not None},
        }


_PLATFORM = InMemoryMetrics()


def platform_metrics() -> InMemoryMetrics:
    return _PLATFORM
