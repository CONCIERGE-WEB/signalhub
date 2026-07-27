"""Deterministic score engine — RFC-0001. No AI."""
from __future__ import annotations

from dataclasses import replace

from signalhub.core.models import ScoreBreakdown, Signal, SignalPriority
from signalhub.core.models.provenance import Provenance
from signalhub.core.models.signal import SignalStatus
from signalhub.rules import RuleEngine, RuleHit


class ScoreEngine:
    """Aggregates RuleHits into total score + algorithm confidence."""

    def __init__(self, *, rule_engine: RuleEngine | None = None) -> None:
        self.rule_engine = rule_engine or RuleEngine()

    def score(self, signal: Signal) -> Signal:
        signal, hits = self.rule_engine.apply(signal)
        return self.apply_hits(signal, hits)

    def apply_hits(self, signal: Signal, hits: list[RuleHit]) -> Signal:
        components: dict[str, float] = {}
        total = 0.0
        for hit in hits:
            components[hit.rule_id] = components.get(hit.rule_id, 0.0) + hit.weight
            total += hit.weight

        total = min(100.0, max(0.0, round(total, 4)))
        n_rules = len({h.rule_id for h in hits})
        confidence = min(1.0, 0.25 * n_rules) if hits else 0.0
        justification = list(signal.rules_applied)

        breakdown = ScoreBreakdown(
            total=total,
            confidence=round(confidence, 4),
            components=components,
            justification=justification,
        )
        signal.score = breakdown.total
        signal.confidence = breakdown.confidence
        signal.score_breakdown = breakdown
        signal.priority = _priority_from_score(breakdown.total)

        if signal.provenance is not None:
            signal.provenance = replace(
                signal.provenance,
                rules_executed=tuple(justification),
            )

        signal.transition(
            SignalStatus.SCORED,
            stage="score_engine",
            detail=f"score={breakdown.total} confidence={breakdown.confidence}",
            rules=justification,
        )
        return signal


def _priority_from_score(total: float) -> SignalPriority:
    if total >= 25:
        return SignalPriority.URGENT
    if total >= 15:
        return SignalPriority.HIGH
    if total >= 5:
        return SignalPriority.NORMAL
    return SignalPriority.LOW
