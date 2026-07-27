from __future__ import annotations

from signalhub.core.contracts.pipeline import PipelineContext, PipelineStage
from signalhub.core.models import ProcessingStep
from signalhub.core.models.signal import SignalStatus
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
        for signal in ctx.signals:
            key = signal.url or str(signal.id)
            if key in seen:
                continue
            seen.add(key)
            signal.transition(
                SignalStatus.DEDUPLICATED,
                stage="deduplicator",
                detail=f"key={key}",
            )
            unique.append(signal)
        ctx.signals = unique
        return ctx


class RuleAndScoreStage(PipelineStage):
    name = "rule_score"

    def __init__(self, score_engine: ScoreEngine | None = None) -> None:
        self.score_engine = score_engine or ScoreEngine()

    def process(self, ctx: PipelineContext) -> PipelineContext:
        ctx.signals = [self.score_engine.score(s) for s in ctx.signals]
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
