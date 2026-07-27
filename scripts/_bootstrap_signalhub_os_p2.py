"""Bootstrap phase 2 — registry, events, pipeline, orchestrator, security, observability."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "signalhub"


def w(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


FILES: dict[str, str] = {
    "core/registry/__init__.py": '''\
"""Registries — providers, capabilities, DI container."""
from .capabilities import CapabilityRegistry
from .container import ServiceContainer
from .providers import ProviderRegistry

__all__ = ["CapabilityRegistry", "ProviderRegistry", "ServiceContainer"]
''',
    "core/registry/providers.py": '''\
from __future__ import annotations

from signalhub.core.contracts.provider import Provider, ProviderMetadata


class ProviderRegistry:
    """Register / load / discover providers. No provider knows another."""

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider, *, replace: bool = False) -> None:
        meta = provider.metadata()
        key = meta.provider_id.strip().lower()
        if not key:
            raise ValueError("provider_id vazio")
        if key in self._providers and not replace:
            raise KeyError(f"provider já registrado: {key}")
        self._providers[key] = provider

    def get(self, provider_id: str) -> Provider:
        key = provider_id.strip().lower()
        if key not in self._providers:
            raise KeyError(
                f"provider '{provider_id}' não registrado. "
                f"Disponíveis: {sorted(self._providers)}"
            )
        return self._providers[key]

    def list_ids(self) -> list[str]:
        return sorted(self._providers)

    def list_metadata(self) -> list[ProviderMetadata]:
        return [p.metadata() for p in self._providers.values()]

    def enabled(self, allowed: set[str] | None = None) -> list[Provider]:
        if allowed is None:
            return list(self._providers.values())
        allow = {a.strip().lower() for a in allowed}
        return [p for pid, p in self._providers.items() if pid in allow]
''',
    "core/registry/capabilities.py": '''\
from __future__ import annotations

from signalhub.core.contracts.capability import Capability, CapabilityHandler


class CapabilityRegistry:
    """Capabilities are the product surface — MCP tools are projections."""

    def __init__(self) -> None:
        self._handlers: dict[str, CapabilityHandler] = {}

    def register(self, handler: CapabilityHandler, *, replace: bool = False) -> None:
        cap = handler.capability()
        key = cap.id.strip().lower()
        if not key:
            raise ValueError("capability id vazio")
        if key in self._handlers and not replace:
            raise KeyError(f"capability já registrada: {key}")
        if not cap.enabled:
            return
        self._handlers[key] = handler

    def get(self, capability_id: str) -> CapabilityHandler:
        key = capability_id.strip().lower()
        if key not in self._handlers:
            raise KeyError(
                f"capability '{capability_id}' não registrada. "
                f"Disponíveis: {sorted(self._handlers)}"
            )
        return self._handlers[key]

    def get_by_tool_name(self, tool_name: str) -> CapabilityHandler:
        name = tool_name.strip().lower()
        for handler in self._handlers.values():
            if handler.capability().tool_name.lower() == name:
                return handler
        raise KeyError(f"tool MCP '{tool_name}' sem capability")

    def list_capabilities(self) -> list[Capability]:
        return [h.capability() for h in self._handlers.values()]

    def list_tool_names(self) -> list[str]:
        return sorted(c.tool_name for c in self.list_capabilities())
''',
    "core/registry/container.py": '''\
from __future__ import annotations

from typing import Any, Callable, TypeVar

from .capabilities import CapabilityRegistry
from .providers import ProviderRegistry

T = TypeVar("T")


class ServiceContainer:
    """Minimal DI — constructors receive explicit deps; container wires them."""

    def __init__(self) -> None:
        self.providers = ProviderRegistry()
        self.capabilities = CapabilityRegistry()
        self._singletons: dict[type[Any], Any] = {}
        self._factories: dict[type[Any], Callable[[ServiceContainer], Any]] = {}

    def register_singleton(self, iface: type[T], instance: T) -> None:
        self._singletons[iface] = instance

    def register_factory(
        self,
        iface: type[T],
        factory: Callable[[ServiceContainer], T],
    ) -> None:
        self._factories[iface] = factory

    def resolve(self, iface: type[T]) -> T:
        if iface in self._singletons:
            return self._singletons[iface]  # type: ignore[return-value]
        factory = self._factories.get(iface)
        if factory is None:
            raise KeyError(f"serviço não registrado: {iface!r}")
        instance = factory(self)
        self._singletons[iface] = instance
        return instance  # type: ignore[return-value]
''',
    "core/events/__init__.py": '''\
from .bus import InProcessEventBus
from .types import DomainEvent, EventType

__all__ = ["DomainEvent", "EventType", "InProcessEventBus"]
''',
    "core/events/types.py": '''\
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


class EventType(str, Enum):
    LEAD_FOUND = "lead.found"
    LEAD_ENRICHED = "lead.enriched"
    LEAD_SCORED = "lead.scored"
    LEAD_STORED = "lead.stored"
    PROVIDER_FAILED = "provider.failed"
    CAPABILITY_EXECUTED = "capability.executed"
    AUDIT = "audit"


@dataclass(slots=True, frozen=True)
class DomainEvent:
    type: EventType
    payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
'''
,
    "core/events/bus.py": '''\
from __future__ import annotations

from collections import defaultdict
from typing import Callable

from .types import DomainEvent, EventType

Handler = Callable[[DomainEvent], None]


class InProcessEventBus:
    """Phase-1 event bus. Swap for broker later without changing publishers."""

    def __init__(self) -> None:
        self._handlers: dict[EventType | None, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: EventType | None, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in list(self._handlers.get(event.type, [])):
            handler(event)
        for handler in list(self._handlers.get(None, [])):
            handler(event)
''',
    "core/pipeline/__init__.py": '''\
from .runner import PipelineRunner
from .stages import (
    DeduplicatorStage,
    IdentityStage,
    LeadScoringStubStage,
    StorageStubStage,
)

__all__ = [
    "DeduplicatorStage",
    "IdentityStage",
    "LeadScoringStubStage",
    "PipelineRunner",
    "StorageStubStage",
]
''',
    "core/pipeline/stages.py": '''\
from __future__ import annotations

from signalhub.core.contracts.pipeline import PipelineContext, PipelineStage
from signalhub.core.models.lead import LeadStatus


class IdentityStage(PipelineStage):
    """Passthrough — useful as pipeline anchor in tests."""

    name = "identity"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        return ctx


class DeduplicatorStage(PipelineStage):
    name = "deduplicator"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        seen: set[str] = set()
        unique = []
        for lead in ctx.leads:
            key = lead.url or str(lead.id)
            if key in seen:
                continue
            seen.add(key)
            unique.append(lead)
        ctx.leads = unique
        return ctx


class LeadScoringStubStage(PipelineStage):
    """Scoring port reserved — does not invent scores."""

    name = "lead_scoring"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        for lead in ctx.leads:
            if lead.score is None:
                lead.status = LeadStatus.ENRICHED
        return ctx


class StorageStubStage(PipelineStage):
    """Explicit empty store until storage adapter is wired."""

    name = "storage"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        ctx.attributes["stored_count"] = 0
        ctx.attributes["storage"] = "stub_vazio"
        for lead in ctx.leads:
            lead.status = LeadStatus.STORED
        return ctx
''',
    "core/pipeline/runner.py": '''\
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
''',
    "core/orchestrator/__init__.py": '''\
from .service import Orchestrator

__all__ = ["Orchestrator"]
''',
    "core/orchestrator/service.py": '''\
from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.contracts.capability import CapabilityResult
from signalhub.core.contracts.pipeline import PipelineContext
from signalhub.core.contracts.provider import ProviderQuery
from signalhub.core.events.bus import InProcessEventBus
from signalhub.core.events.types import DomainEvent, EventType
from signalhub.core.models import Lead
from signalhub.core.pipeline.runner import PipelineRunner
from signalhub.core.pipeline.stages import (
    DeduplicatorStage,
    LeadScoringStubStage,
    StorageStubStage,
)
from signalhub.core.registry.capabilities import CapabilityRegistry
from signalhub.core.registry.providers import ProviderRegistry
from signalhub.observability.tracing import ExecutionTrace
from signalhub.security.policy import SecurityPolicy


class Orchestrator:
    """Single entry for all interfaces — MCP/API/CLI call this, not Providers."""

    def __init__(
        self,
        providers: ProviderRegistry,
        capabilities: CapabilityRegistry,
        *,
        policy: SecurityPolicy | None = None,
        bus: InProcessEventBus | None = None,
        pipeline: PipelineRunner | None = None,
    ) -> None:
        self.providers = providers
        self.capabilities = capabilities
        self.policy = policy or SecurityPolicy()
        self.bus = bus or InProcessEventBus()
        self.pipeline = pipeline or PipelineRunner(
            [DeduplicatorStage(), LeadScoringStubStage(), StorageStubStage()]
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
            }
            return result

    def discover_via_providers(
        self,
        *,
        capability_id: str,
        provider_ids: Sequence[str],
        terms: Sequence[str],
        geo: str | None = None,
        limit: int = 40,
    ) -> list[Lead]:
        """Core fan-out — providers never call each other."""
        query = ProviderQuery(
            capability_id=capability_id,
            terms=terms,
            geo=geo,
            limit=limit,
        )
        leads: list[Lead] = []
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
            hits = provider.search(query)
            collected = provider.collect(hits)
            normalized = provider.normalize(collected)
            validated = provider.validate(normalized)
            enriched = provider.enrich(validated)
            leads.extend(enriched)

        ctx = PipelineContext(capability_id=capability_id, leads=leads)
        ctx = self.pipeline.run(ctx)
        return ctx.leads
''',
    "core/scheduler/__init__.py": '''\
from .base import SchedulerPort, NullScheduler

__all__ = ["NullScheduler", "SchedulerPort"]
''',
    "core/scheduler/base.py": '''\
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
''',
}

def main() -> None:
    for rel, content in FILES.items():
        w(rel, content)
    print(f"phase2: {len(FILES)} files")


if __name__ == "__main__":
    main()
