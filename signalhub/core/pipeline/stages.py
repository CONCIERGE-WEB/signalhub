from __future__ import annotations

import time

from signalhub.core.contracts.pipeline import PipelineContext, PipelineStage
from signalhub.core.models import ProcessingStep
from signalhub.core.models.signal import SignalStatus
from signalhub.observability.metrics import platform_metrics
from signalhub.scoring import ScoreEngine
from signalhub.storage import InMemorySignalStore
from signalhub.validation import SignalValidator


class IdentityStage(PipelineStage):
    name = "identity"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        return ctx


class SignalValidatorStage(PipelineStage):
    """RFC-0001 — reject invalid Signals before they enter the Core."""

    name = "signal_validator"

    def __init__(self, validator: SignalValidator | None = None) -> None:
        self.validator = validator or SignalValidator()

    def process(self, ctx: PipelineContext) -> PipelineContext:
        accepted = []
        rejected = 0
        metrics = platform_metrics()
        for signal in ctx.signals:
            result = self.validator.validate(signal)
            if not result.ok:
                rejected += 1
                ctx.errors.append(
                    f"reject {signal.id}: {'; '.join(result.reasons)}"
                )
                continue
            signal.with_step(
                ProcessingStep(
                    stage="signal_validator",
                    detail="ok",
                    to_status=signal.status_value,
                )
            )
            accepted.append(signal)
        ctx.signals = accepted
        ctx.attributes["validator_rejected"] = rejected
        if rejected:
            metrics.incr("signals_invalid", rejected)
        metrics.incr("signals_produced", len(accepted))
        return ctx


class SignalNormalizerStage(PipelineStage):
    """Core normalizer — canonical fields; Providers must not skip this."""

    name = "signal_normalizer"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        for signal in ctx.signals:
            if not signal.source and signal.provider:
                signal.source = signal.provider
            if signal.title:
                signal.title = signal.title.strip()
            if signal.summary:
                signal.summary = signal.summary.strip()
            signal.transition(
                SignalStatus.NORMALIZED,
                stage="signal_normalizer",
                detail="canonical",
            )
        return ctx


class DeduplicatorStage(PipelineStage):
    name = "deduplicator"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        seen: set[str] = set()
        unique = []
        dup = 0
        for signal in ctx.signals:
            key = signal.url or str(signal.id)
            if key in seen:
                dup += 1
                continue
            seen.add(key)
            signal.transition(
                SignalStatus.DEDUPLICATED,
                stage="deduplicator",
                detail=f"key={key}",
            )
            unique.append(signal)
        discarded = len(ctx.signals) - len(unique)
        ctx.signals = unique
        if dup:
            platform_metrics().incr("signals_duplicated", dup)
        if discarded:
            platform_metrics().incr("signals_discarded", discarded)
        return ctx


class RuleAndScoreStage(PipelineStage):
    name = "rule_score"

    def __init__(self, score_engine: ScoreEngine | None = None) -> None:
        self.score_engine = score_engine or ScoreEngine()

    def process(self, ctx: PipelineContext) -> PipelineContext:
        metrics = platform_metrics()
        out = []
        for signal in ctx.signals:
            t0 = time.perf_counter()
            signal, hits = self.score_engine.rule_engine.apply(signal)
            metrics.timing("rule_engine_ms", (time.perf_counter() - t0) * 1000)
            if hits:
                metrics.incr("rules_applied", len(hits))
            t1 = time.perf_counter()
            scored = self.score_engine.apply_hits(signal, hits)
            metrics.timing("score_engine_ms", (time.perf_counter() - t1) * 1000)
            out.append(scored)
        ctx.signals = out
        return ctx


class StorageStage(PipelineStage):
    name = "storage"

    def __init__(self, store: InMemorySignalStore | None = None) -> None:
        self.store = store or InMemorySignalStore()

    def process(self, ctx: PipelineContext) -> PipelineContext:
        for signal in ctx.signals:
            signal.transition(SignalStatus.STORED, stage="storage", detail="upsert")
        n = self.store.upsert(ctx.signals)
        ctx.attributes["stored_count"] = n
        ctx.attributes["storage"] = "memory"
        return ctx


LeadScoringStubStage = RuleAndScoreStage
StorageStubStage = StorageStage
