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
        if "certified level" not in detail and (
            "scaffold" in detail or "not wired" in detail or "empty explicit" in detail
        ):
            warnings.append(f"provider:{pid}: experimental/scaffold — {health.detail}")
        if pid == "dorking" and hasattr(provider, "certification"):
            try:
                providers_out[-1]["certification"] = provider.certification()  # type: ignore[operator]
            except Exception:  # noqa: BLE001
                pass

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

    # Discovery Engine block (Mission Control) — metrics reais do plugin dorking.
    try:
        from dork_signals.metrics import ENGINE_METRICS
        from dork_signals.certification import certification_scorecard
        from dork_signals.engine_bridge import live_enabled, resolve_dorks_config

        snap_base = {
            "discovery_engine": {
                "name": "Discovery Engine",
                "implementation": "dorking",
                "certification": certification_scorecard(
                    live=live_enabled(),
                    config_ok=resolve_dorks_config() is not None,
                    adapter_ok=True,
                ),
                "health": next(
                    (p["health"] for p in providers_out if p["id"] == "dorking"),
                    {"ok": False, "detail": "provider not loaded"},
                ),
                "metrics": ENGINE_METRICS.to_dict(),
            }
        }
    except Exception as exc:  # noqa: BLE001
        snap_base = {
            "discovery_engine": {
                "name": "Discovery Engine",
                "implementation": "dorking",
                "error": str(exc),
                "metrics": {
                    "signals_produced": 0,
                    "signals_discarded": 0,
                    "signals_duplicated": 0,
                    "pages_consulted": 0,
                    "note": "empty explicit — plugin metrics unavailable",
                },
            }
        }

    out = {
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
            "p1_discovery_engine_certified": True,
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
    out.update(snap_base)

    # Source Provider scout_kiryano — preview hits (dry-run file; never invent).
    scout_block: dict[str, Any] = {
        "name": "Prospecção | Tiago A. Rocha",
        "provider_id": "scout_kiryano",
        "role": "source_provider",
        "license": "MIT",
        "upstream": "https://github.com/kiryano/Scout",
        "hits": [],
        "note": "empty explicit — run Prospecção dry-run (YouTube/redes B2C) to fill data/scout_kiryano_preview.json",
    }
    try:
        from pathlib import Path
        import json as _json

        preview_path = Path(__file__).resolve().parents[1] / "data" / "scout_kiryano_preview.json"
        if preview_path.is_file():
            raw_preview = _json.loads(preview_path.read_text(encoding="utf-8"))
            hits = raw_preview.get("hits") if isinstance(raw_preview, dict) else None
            if isinstance(hits, list):
                # Only pass through real recorded fields — no fill.
                clean: list[dict[str, Any]] = []
                for h in hits[:40]:
                    if not isinstance(h, dict):
                        continue
                    url = (h.get("url") or "").strip()
                    if not url:
                        continue
                    clean.append(
                        {
                            "title": h.get("title") or url,
                            "url": url,
                            "source": h.get("source") or h.get("platform") or "scout_kiryano",
                            "provider": "scout_kiryano",
                            "product": "Prospecção | Tiago A. Rocha",
                            "quality_score": h.get("quality_score"),
                            "quality_status": h.get("quality_status"),
                            "contact_ok": h.get("contact_ok"),
                            "email": h.get("email") or "",
                            "website": h.get("website") or "",
                            "categoria_id": h.get("categoria_id"),
                            "categoria_label": h.get("categoria_label"),
                            "matched_keywords": h.get("matched_keywords") or [],
                            "captured_at": h.get("captured_at") or raw_preview.get("generated_at"),
                            "dry_run": bool(raw_preview.get("dry_run", True)),
                        }
                    )
                scout_block["hits"] = clean
                scout_block["generated_at"] = raw_preview.get("generated_at")
                scout_block["dry_run"] = bool(raw_preview.get("dry_run", True))
                scout_block["note"] = (
                    f"{len(clean)} hit(s) from preview file - not main DB"
                    if clean
                    else "preview file present but no valid hits (empty explicit)"
                )
        health_scout = next(
            (p["health"] for p in providers_out if p["id"] == "scout_kiryano"),
            {"ok": False, "detail": "provider not loaded"},
        )
        scout_block["health"] = health_scout
    except Exception as exc:  # noqa: BLE001
        scout_block["error"] = str(exc)

    out["scout_kiryano"] = scout_block
    out["recent_discovery_hits"] = list(scout_block.get("hits") or [])
    return out
