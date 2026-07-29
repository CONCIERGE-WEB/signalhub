"""In-plugin metrics for Discovery Engine (Dorking) — real counters only."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DiscoveryEngineMetrics:
    last_run_at: str | None = None
    last_duration_ms: float | None = None
    pages_consulted: int = 0
    signals_produced: int = 0
    signals_discarded: int = 0
    signals_duplicated: int = 0
    avg_ms: float | None = None
    categories: dict[str, int] = field(default_factory=dict)
    origins: dict[str, int] = field(default_factory=dict)
    live_enabled: bool = False
    config_path: str | None = None
    last_error: str | None = None
    _runs: int = 0
    _total_ms: float = 0.0

    def record_run(
        self,
        *,
        duration_ms: float,
        pages: int,
        produced: int,
        discarded: int,
        duplicated: int,
        categories: dict[str, int],
        origins: dict[str, int],
        error: str | None = None,
    ) -> None:
        self.last_run_at = datetime.now(timezone.utc).isoformat()
        self.last_duration_ms = duration_ms
        self.pages_consulted = pages
        self.signals_produced += produced
        self.signals_discarded += discarded
        self.signals_duplicated += duplicated
        self._runs += 1
        self._total_ms += duration_ms
        self.avg_ms = self._total_ms / self._runs if self._runs else None
        for k, v in categories.items():
            self.categories[k] = self.categories.get(k, 0) + v
        for k, v in origins.items():
            self.origins[k] = self.origins.get(k, 0) + v
        self.last_error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_run_at": self.last_run_at,
            "last_duration_ms": self.last_duration_ms,
            "pages_consulted": self.pages_consulted,
            "signals_produced": self.signals_produced,
            "signals_discarded": self.signals_discarded,
            "signals_duplicated": self.signals_duplicated,
            "avg_ms": self.avg_ms,
            "categories": dict(self.categories),
            "origins": dict(self.origins),
            "live_enabled": self.live_enabled,
            "config_path": self.config_path,
            "last_error": self.last_error,
        }


# Process-wide singleton for Mission Control / Dashboard (no invented defaults beyond zeros).
ENGINE_METRICS = DiscoveryEngineMetrics()
