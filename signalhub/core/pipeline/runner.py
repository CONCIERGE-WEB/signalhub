from __future__ import annotations

from signalhub.core.contracts.pipeline import PipelineContext, PipelineStage
from signalhub.observability.tracing import ExecutionTrace


class PipelineRunner:
    def __init__(self, stages: list[PipelineStage] | None = None) -> None:
        self.stages = list(stages or [])

    def run(self, ctx: PipelineContext, *, trace: ExecutionTrace | None = None) -> PipelineContext:
        current = ctx
        for stage in self.stages:
            span = None
            if trace is not None:
                span = trace.start_span(f"pipeline.{stage.name}")
            try:
                current = stage.process(current)
            except Exception as exc:  # noqa: BLE001 — surface in context, don't invent data
                current.errors.append(f"{stage.name}: {exc}")
                if span is not None:
                    span.fail(str(exc))
                raise
            else:
                if span is not None:
                    span.ok()
        return current
