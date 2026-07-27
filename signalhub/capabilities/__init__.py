"""Capability handlers — deterministic Core only. MCP never scrapes."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.contracts.capability import Capability, CapabilityHandler, CapabilityResult
from signalhub.core.models import Lead
from signalhub.core.orchestrator.service import Orchestrator
from signalhub.scoring import ScoreEngine


class DiscoverSignalsHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="discover_signals",
            name="Discover Signals",
            description=(
                "Discover public signals via enabled providers (deterministic). "
                "Empty when providers are not wired — never invents data. No AI."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "terms": {"type": "array", "items": {"type": "string"}},
                    "geo": {"type": "string"},
                    "category": {"type": "string"},
                    "limit": {"type": "integer", "default": 40},
                    "providers": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["terms"],
            },
            provider_ids=("scout", "dorking", "google"),
            mcp_tool_name="discover_signals",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        terms = tuple(arguments.get("terms") or ())
        providers = arguments.get("providers")
        cap = self.capability()
        provider_ids: Sequence[str] = (
            tuple(str(p) for p in providers) if providers else cap.provider_ids
        )
        signals = self._orch.discover_signals(
            capability_id=cap.id,
            provider_ids=provider_ids,
            terms=terms,
            geo=arguments.get("geo"),
            category=arguments.get("category"),
            limit=int(arguments.get("limit") or 40),
        )
        return CapabilityResult(
            capability_id=cap.id,
            status="ok_vazio" if not signals else "ok",
            items=[s.to_dict() for s in signals],
            meta={
                "providers": list(provider_ids),
                "human_in_the_loop": self._orch.policy.human_in_the_loop,
                "ai": False,
            },
        )


class SearchSignalsHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="search_signals",
            name="Search Signals",
            description="Search stored signals by text (deterministic substring).",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 40},
                },
                "required": ["query"],
            },
            mcp_tool_name="search_signals",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        q = str(arguments.get("query") or "").lower()
        limit = int(arguments.get("limit") or 40)
        items = []
        for signal in self._orch.store.list_recent(limit=500):
            blob = f"{signal.title} {signal.summary} {signal.category or ''}".lower()
            if q and q not in blob:
                continue
            items.append(signal.to_dict())
            if len(items) >= limit:
                break
        return CapabilityResult(
            capability_id="search_signals",
            status="ok_vazio" if not items else "ok",
            items=items,
            meta={"ai": False},
        )


class SearchByCategoryHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="search_by_category",
            name="Search By Category",
            description="List stored signals filtered by category.",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "limit": {"type": "integer", "default": 40},
                },
                "required": ["category"],
            },
            mcp_tool_name="search_by_category",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        category = str(arguments.get("category") or "")
        limit = int(arguments.get("limit") or 40)
        items = [s.to_dict() for s in self._orch.store.list_recent(limit=limit, category=category)]
        return CapabilityResult(
            capability_id="search_by_category",
            status="ok_vazio" if not items else "ok",
            items=items,
        )


class ListSourcesHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="list_sources",
            name="List Sources",
            description="List registered providers / sources.",
            input_schema={"type": "object", "properties": {}},
            mcp_tool_name="list_sources",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        _ = arguments
        items = [
            {
                "id": m.provider_id,
                "name": m.name,
                "capabilities": list(m.capabilities),
                "description": m.description,
            }
            for m in self._orch.providers.list_metadata()
        ]
        return CapabilityResult(capability_id="list_sources", status="ok", items=items)


class GetProviderStatusHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="get_provider_status",
            name="Get Provider Status",
            description="Healthcheck of registered providers.",
            input_schema={"type": "object", "properties": {}},
            mcp_tool_name="get_provider_status",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        _ = arguments
        items = []
        for pid in self._orch.providers.list_ids():
            p = self._orch.providers.get(pid)
            h = p.healthcheck()
            items.append(
                {
                    "provider_id": pid,
                    "ok": h.ok,
                    "detail": h.detail,
                    "enabled": self._orch.policy.is_provider_allowed(pid),
                }
            )
        return CapabilityResult(capability_id="get_provider_status", status="ok", items=items)


class GetMetricsHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="get_metrics",
            name="Get Metrics",
            description="Deterministic Core metrics (no AI cost).",
            input_schema={"type": "object", "properties": {}},
            mcp_tool_name="get_metrics",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        _ = arguments
        recent = self._orch.store.list_recent(limit=10_000)
        return CapabilityResult(
            capability_id="get_metrics",
            status="ok",
            items=[
                {
                    "signals_stored": len(recent),
                    "providers": len(self._orch.providers.list_ids()),
                    "capabilities": len(self._orch.capabilities.list_capabilities()),
                    "ai": False,
                }
            ],
        )


class GetRecentSignalsHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="get_recent_signals",
            name="Get Recent Signals",
            description="Recent signals from storage.",
            input_schema={
                "type": "object",
                "properties": {"limit": {"type": "integer", "default": 20}},
            },
            mcp_tool_name="get_recent_signals",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        limit = int(arguments.get("limit") or 20)
        items = [s.to_dict() for s in self._orch.store.list_recent(limit=limit)]
        return CapabilityResult(
            capability_id="get_recent_signals",
            status="ok_vazio" if not items else "ok",
            items=items,
        )


class SearchCompaniesHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="search_companies",
            name="Search Companies",
            description="Discover company-related public signals (scaffold empty).",
            input_schema={
                "type": "object",
                "properties": {
                    "terms": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["terms"],
            },
            provider_ids=("google", "websites", "linkedin"),
            mcp_tool_name="search_companies",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        signals = self._orch.discover_signals(
            capability_id="search_companies",
            provider_ids=self.capability().provider_ids,
            terms=tuple(arguments.get("terms") or ()),
            limit=int(arguments.get("limit") or 20),
        )
        return CapabilityResult(
            capability_id="search_companies",
            status="ok_vazio" if not signals else "ok",
            items=[s.to_dict() for s in signals],
        )


class SearchLawTopicsHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def capability(self) -> Capability:
        return Capability(
            id="search_law_topics",
            name="Search Law Topics",
            description="Public legal-topic signals (deterministic; scaffold empty).",
            input_schema={
                "type": "object",
                "properties": {
                    "terms": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["terms"],
            },
            provider_ids=("dorking", "scout"),
            mcp_tool_name="search_law_topics",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        signals = self._orch.discover_signals(
            capability_id="search_law_topics",
            provider_ids=self.capability().provider_ids,
            terms=tuple(arguments.get("terms") or ()),
            category="legal",
            limit=int(arguments.get("limit") or 20),
        )
        return CapabilityResult(
            capability_id="search_law_topics",
            status="ok_vazio" if not signals else "ok",
            items=[s.to_dict() for s in signals],
        )


class AnalyzeSignalHandler(CapabilityHandler):
    """Rule/score analysis only — never calls an LLM."""

    def capability(self) -> Capability:
        return Capability(
            id="analyze_signal",
            name="Analyze Signal",
            description="Apply Rule Engine + Score Engine to a signal payload (no AI).",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "url": {"type": "string"},
                    "source": {"type": "string"},
                    "signal_type": {"type": "string"},
                },
                "required": ["title"],
            },
            mcp_tool_name="analyze_signal",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        from signalhub.core.models import Provenance, Signal, SignalType
        from signalhub.core.models.common import EntityId
        from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION, SignalStatus
        from signalhub.core.pipeline.runner import PipelineRunner
        from signalhub.core.pipeline.stages import (
            RuleAndScoreStage,
            SignalNormalizerStage,
            SignalValidatorStage,
        )
        from signalhub.core.contracts.pipeline import PipelineContext

        title = str(arguments.get("title") or "")
        try:
            st = SignalType(str(arguments.get("signal_type") or "other"))
        except ValueError:
            st = SignalType.OTHER
        signal = Signal(
            id=EntityId("analyze:adhoc"),
            provider="manual",
            signal_type=st,
            title=title,
            summary=str(arguments.get("summary") or ""),
            url=arguments.get("url"),
            source=str(arguments.get("source") or "manual"),
            provenance=Provenance(
                provider_id="manual",
                source_url=arguments.get("url"),
                origin=str(arguments.get("source") or "manual"),
            ),
            status=SignalStatus.DISCOVERED,
            version="1",
            contract_version=SIGNAL_CONTRACT_VERSION,
            metadata={"adhoc": True},
        )
        # Derive via pipeline stages — does not mutate a stored Signal; returns new scored instance
        ctx = PipelineContext(capability_id="analyze_signal", signals=[signal])
        ctx = PipelineRunner(
            [
                SignalValidatorStage(),
                SignalNormalizerStage(),
                RuleAndScoreStage(ScoreEngine()),
            ]
        ).run(ctx)
        if not ctx.signals:
            return CapabilityResult(
                capability_id="analyze_signal",
                status="error",
                meta={"ai": False, "errors": ctx.errors},
            )
        scored = ctx.signals[0]
        scored.bump_version(reason="analyze_signal_derived")
        return CapabilityResult(
            capability_id="analyze_signal",
            status="ok",
            items=[scored.to_dict()],
            meta={"ai": False, "immutable_capability": True},
        )


# Deprecated alias — Lead as interpretation of discover_signals
class DiscoverLeadsHandler(CapabilityHandler):
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._inner = DiscoverSignalsHandler(orchestrator)

    def capability(self) -> Capability:
        base = self._inner.capability()
        return Capability(
            id="discover_leads",
            name="Discover Leads (alias)",
            description=(
                "Deprecated alias: discovers Signals and returns Lead interpretations. "
                "Prefer discover_signals."
            ),
            input_schema=base.input_schema,
            provider_ids=base.provider_ids,
            mcp_tool_name="discover_leads",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        result = self._inner.execute(arguments)
        leads = []
        for item in result.items:
            # rebuild minimal Lead from signal dict without inventing
            from signalhub.core.models import Signal, SignalType
            from signalhub.core.models.common import EntityId

            try:
                st = SignalType(str(item.get("signal_type") or "other"))
            except ValueError:
                st = SignalType.OTHER
            signal = Signal(
                id=EntityId(str(item.get("id") or "unknown")),
                provider=str(item.get("provider") or "unknown"),
                signal_type=st,
                title=str(item.get("title") or ""),
                summary=str(item.get("summary") or ""),
                url=item.get("url"),
                category=item.get("category"),
                score=item.get("score"),
                source=str(item.get("source") or ""),
            )
            leads.append(Lead.from_signal(signal).to_dict())
        return CapabilityResult(
            capability_id="discover_leads",
            status=result.status,
            items=leads,
            meta={**dict(result.meta), "interpretation": "lead_from_signal"},
        )


DEFAULT_HANDLER_TYPES: tuple[type[CapabilityHandler], ...] = (
    DiscoverSignalsHandler,
    SearchSignalsHandler,
    SearchByCategoryHandler,
    ListSourcesHandler,
    GetProviderStatusHandler,
    GetMetricsHandler,
    GetRecentSignalsHandler,
    SearchCompaniesHandler,
    SearchLawTopicsHandler,
    AnalyzeSignalHandler,
    DiscoverLeadsHandler,
)
