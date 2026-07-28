"""Admin snapshot — Lex Rocha dashboard consumes this (no Lex logic here)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from signalhub import __version__
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION
from signalhub.core.registry.container import ServiceContainer
from signalhub.observability.metrics import platform_metrics
from signalhub.security.policy import SecurityPolicy


def _capability_explorer(capabilities: list[dict[str, Any]], mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Catálogo estilo Swagger — documentação, sem executar coleta."""
    tools_by_cap = {t["capability_id"]: t for t in mcp_tools}
    out: list[dict[str, Any]] = []
    for cap in capabilities:
        tool = tools_by_cap.get(cap["id"])
        tool_name = cap.get("tool_name") or (tool or {}).get("name") or cap["id"]
        out.append(
            {
                "id": cap["id"],
                "name": cap["name"],
                "description": cap["description"],
                "enabled": cap["enabled"],
                "provider_ids": list(cap.get("provider_ids") or []),
                "contract_version": SIGNAL_CONTRACT_VERSION,
                "permissions": ["public_read"] if cap["enabled"] else ["disabled"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "terms": {"type": "array", "items": {"type": "string"}},
                        "limit": {"type": "integer", "default": 40},
                    },
                },
                "example_input": {"terms": ["exemplo"], "limit": 5},
                "example_output": {
                    "status": "ok",
                    "signals": [],
                    "note": "empty explicit when providers are scaffolds",
                },
                "rest_example": f"POST /v1/capabilities/{cap['id']}/execute",
                "mcp_example": {
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": {"terms": ["exemplo"]}},
                },
                "python_example": (
                    f"from signalhub.bootstrap import build_orchestrator\n"
                    f"r = build_orchestrator().execute_capability("
                    f"{cap['id']!r}, {{'terms': ['exemplo']}})\n"
                    f"print(r.to_dict())"
                ),
            }
        )
    return out


def build_admin_snapshot(
    container: ServiceContainer,
    *,
    policy: SecurityPolicy | None = None,
) -> dict[str, Any]:
    pol = policy or SecurityPolicy()
    providers_out: list[dict[str, Any]] = []
    warnings: list[str] = []
    failures: list[str] = []
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
                "contract_version": SIGNAL_CONTRACT_VERSION,
                "core_version": __version__,
                "plugin_version": meta.version,
                "health": {
                    "ok": health.ok,
                    "detail": health.detail,
                    "latency_ms": health.latency_ms,
                },
            }
        )
        if not health.ok:
            failures.append(f"provider:{pid}:{health.detail}")
        detail = (health.detail or "").lower()
        if "scaffold" in detail or "not wired" in detail or "empty" in detail:
            warnings.append(f"provider:{pid}: experimental/scaffold — {health.detail}")

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

    platform = platform_metrics().snapshot()
    unhealthy = sum(1 for p in providers_out if not p["health"]["ok"])
    status = "ok" if unhealthy == 0 else "degraded"

    integrity = {
        "components_loaded": {
            "providers": len(providers_out),
            "capabilities": len(capabilities),
            "mcp_tools": len(mcp_tools),
        },
        "versions": {
            "core": __version__,
            "contract": SIGNAL_CONTRACT_VERSION,
        },
        "compatibility": {
            "signal_contract": SIGNAL_CONTRACT_VERSION,
            "rfc_0001": True,
        },
        "warnings": warnings,
        "failures": failures,
        "ok": not failures,
    }

    return {
        "product": "signalhub",
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
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
            "p2_platform_hardening": True,
            "client_zero_prospector": True,
            "client_zero_dorking": True,
            "capability_explorer": True,
        },
        "capabilities": capabilities,
        "capability_explorer": _capability_explorer(capabilities, mcp_tools),
        "mcp_tools": mcp_tools,
        "jobs": [],
        "recent_executions": [],
        "logs": [],
        "metrics": {
            "providers_total": len(providers_out),
            "providers_healthy": sum(1 for p in providers_out if p["health"]["ok"]),
            "capabilities_total": len(capabilities),
            "mcp_tools_total": len(mcp_tools),
            "signals_produced": platform["signals_produced"],
            "signals_discarded": platform["signals_discarded"],
            "signals_duplicated": platform["signals_duplicated"],
            "signals_invalid": platform["signals_invalid"],
            "rules_applied": platform["rules_applied"],
        },
        "platform_metrics": platform,
        "integrity": integrity,
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
            "stability_guarantee": "docs/STABILITY_GUARANTEE.md",
        },
    }
