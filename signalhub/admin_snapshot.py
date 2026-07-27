"""Admin snapshot — Lex Rocha dashboard consumes this (no Lex logic here)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from signalhub import __version__
from signalhub.core.registry.container import ServiceContainer
from signalhub.security.policy import SecurityPolicy


def build_admin_snapshot(
    container: ServiceContainer,
    *,
    policy: SecurityPolicy | None = None,
) -> dict[str, Any]:
    pol = policy or SecurityPolicy()
    providers_out: list[dict[str, Any]] = []
    for meta in container.providers.list_metadata():
        pid = meta.provider_id
        provider = container.providers.get(pid)
        health = provider.healthcheck()
        providers_out.append(
            {
                "id": pid,
                "name": meta.name,
                "version": meta.version,
                "description": meta.description,
                "capabilities": list(meta.capabilities),
                "enabled": pol.is_provider_allowed(pid),
                "health": {
                    "ok": health.ok,
                    "detail": health.detail,
                    "latency_ms": health.latency_ms,
                },
            }
        )

    capabilities = []
    mcp_tools = []
    for cap in container.capabilities.list_capabilities():
        capabilities.append(
            {
                "id": cap.id,
                "name": cap.name,
                "description": cap.description,
                "provider_ids": list(cap.provider_ids),
                "enabled": pol.is_capability_allowed(cap.id),
                "tool_name": cap.tool_name,
            }
        )
        mcp_tools.append(
            {
                "name": cap.tool_name,
                "capability_id": cap.id,
                "description": cap.description,
            }
        )

    return {
        "product": "signalhub",
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
        "identity": {
            "kind": "deterministic_signal_platform",
            "ai_inside_core": False,
            "primary_object": "Signal",
            "lead_is": "optional_interpretation",
        },
        "providers": providers_out,
        "providers_enabled": [p["id"] for p in providers_out if p["enabled"]],
        "feature_flags": {
            "human_in_the_loop": pol.human_in_the_loop,
            "require_public_source": pol.require_public_source,
            "ai_in_core": False,
            "rule_engine": True,
            "score_engine": True,
            "signal_validator": True,
            "rfc_0001": True,
            "developer_platform": True,
            "plugin_loader": True,
            "p1_identity_signals": True,
            "p1_scout_dorking_real": False,
            "p2_sdk": True,
            "client_zero_scout": True,
            "client_zero_dorking": True,
        },
        "capabilities": capabilities,
        "mcp_tools": mcp_tools,
        "jobs": [],
        "recent_executions": [],
        "logs": [],
        "metrics": {
            "providers_total": len(providers_out),
            "providers_healthy": sum(1 for p in providers_out if p["health"]["ok"]),
            "capabilities_total": len(capabilities),
            "mcp_tools_total": len(mcp_tools),
        },
        "observability": {
            "tracing": "in_process",
            "metrics": "in_memory",
            "logs": "structured_json",
            "signal_history": "ProcessingStep",
        },
        "security": {
            "disabled_providers": sorted(pol.disabled_providers),
            "disabled_capabilities": sorted(pol.disabled_capabilities),
            "human_in_the_loop": pol.human_in_the_loop,
            "require_public_source": pol.require_public_source,
        },
        "config": {
            "note": (
                "SignalHub is AI-free Core. Optional AI consumers call Capabilities/MCP/REST."
            ),
        },
    }
