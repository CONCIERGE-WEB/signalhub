from __future__ import annotations

import time
from typing import Any, Mapping, Sequence

from signalhub.core.contracts.capability import CapabilityResult
from signalhub.core.contracts.pipeline import PipelineContext
from signalhub.core.contracts.provider import ProviderQuery
from signalhub.core.events.bus import InProcessEventBus
from signalhub.core.events.types import DomainEvent, EventType
from signalhub.core.models import Signal
from signalhub.core.pipeline.runner import PipelineRunner
from signalhub.core.pipeline.stages import (
    DeduplicatorStage,
    RuleAndScoreStage,
    SignalNormalizerStage,
    SignalValidatorStage,
    StorageStage,
)
from signalhub.core.registry.capabilities import CapabilityRegistry
from signalhub.core.registry.providers import ProviderRegistry
from signalhub.notifications import TelegramNotificationAdapter
from signalhub.observability.metrics import platform_metrics
from signalhub.observability.tracing import ExecutionTrace
from signalhub.scoring import ScoreEngine
from signalhub.security.policy import SecurityPolicy
from signalhub.storage import DEFAULT_SIGNAL_STORE, InMemorySignalStore


class Orchestrator:
    """Single entry for REST/CLI/Dashboard/MCP/Telegram — never scrape in MCP."""

    def __init__(
        self,
        providers: ProviderRegistry,
        capabilities: CapabilityRegistry,
        *,
        policy: SecurityPolicy | None = None,
        bus: InProcessEventBus | None = None,
        pipeline: PipelineRunner | None = None,
        store: InMemorySignalStore | None = None,
        score_engine: ScoreEngine | None = None,
        telegram: TelegramNotificationAdapter | None = None,
    ) -> None:
        self.providers = providers
        self.capabilities = capabilities
        self.policy = policy or SecurityPolicy()
        self.bus = bus or InProcessEventBus()
        self.store = store or DEFAULT_SIGNAL_STORE
        self.score_engine = score_engine or ScoreEngine()
        self.telegram = telegram or TelegramNotificationAdapter()
        self.pipeline = pipeline or PipelineRunner(
            [
                SignalValidatorStage(),
                SignalNormalizerStage(),
                DeduplicatorStage(),
                RuleAndScoreStage(self.score_engine),
                StorageStage(self.store),
            ]
        )

    def execute_capability(
        self,
        capability_id: str,
        arguments: Mapping[str, Any] | None = None,
    ) -> CapabilityResult:
        args = dict(arguments or {})
        handler = self.capabilities.get(capability_id)
        cap = handler.capability()
        if not self.policy.is_capability_allowed(cap.id):
            return CapabilityResult(
                capability_id=cap.id,
                status="blocked_policy",
                meta={"reason": "capability desabilitada pela política do operador"},
            )

        trace = ExecutionTrace(operation=f"capability:{cap.id}")
        with trace:
            result = handler.execute(args)
            self.bus.publish(
                DomainEvent(
                    type=EventType.CAPABILITY_EXECUTED,
                    payload={"capability_id": cap.id, "status": result.status},
                    correlation_id=trace.trace_id,
                )
            )
            result.meta = {
                **dict(result.meta),
                "trace_id": trace.trace_id,
                "duration_ms": trace.duration_ms,
                "ai": False,
            }
            return result

    def discover_signals(
        self,
        *,
        capability_id: str,
        provider_ids: Sequence[str],
        terms: Sequence[str],
        geo: str | None = None,
        category: str | None = None,
        limit: int = 40,
    ) -> list[Signal]:
        query = ProviderQuery(
            capability_id=capability_id,
            terms=terms,
            geo=geo,
            category=category,
            limit=limit,
        )
        signals: list[Signal] = []
        for pid in provider_ids:
            if not self.policy.is_provider_allowed(pid):
                continue
            provider = self.providers.get(pid)
            health = provider.healthcheck()
            if not health.ok:
                self.bus.publish(
                    DomainEvent(
                        type=EventType.PROVIDER_FAILED,
                        payload={"provider_id": pid, "detail": health.detail},
                    )
                )
                continue
            t0 = time.perf_counter()
            hits = provider.search(query)
            collected = provider.collect(hits)
            normalized = provider.normalize(collected)
            validated = provider.validate(normalized)
            enriched = provider.enrich(validated)
            platform_metrics().timing(
                f"provider_latency_ms:{pid}",
                (time.perf_counter() - t0) * 1000,
            )
            signals.extend(enriched)

        ctx = PipelineContext(capability_id=capability_id, signals=signals)
        ctx = self.pipeline.run(ctx)
        for signal in ctx.signals:
            self.telegram.enqueue(signal)
        return ctx.signals

    # Backward name used by older handlers
    def discover_via_providers(
        self,
        *,
        capability_id: str,
        provider_ids: Sequence[str],
        terms: Sequence[str],
        geo: str | None = None,
        limit: int = 40,
    ) -> list[Signal]:
        return self.discover_signals(
            capability_id=capability_id,
            provider_ids=provider_ids,
            terms=terms,
            geo=geo,
            limit=limit,
        )
