"""Contract / capability / MCP / REST compatibility checkers."""

from __future__ import annotations

from typing import Any

from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION
from signalhub.core.registry.container import ServiceContainer
from signalhub.plugins.loader import PluginLoader
from signalhub.sdk.testing import contract_check_provider, contract_check_signal, make_sample_signal
from signalhub.validation import SignalValidator


def check_signal_validator() -> dict[str, Any]:
    validator = SignalValidator()
    sample = make_sample_signal()
    result = validator.validate(sample)
    bad = make_sample_signal(title="")
    bad_result = validator.validate(bad)
    return {
        "name": "signal_validator",
        "ok": result.ok and not bad_result.ok,
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "issues": ([] if result.ok else result.reasons)
        + ([] if not bad_result.ok else ["validator aceitou signal inválido"]),
    }


def check_provider_contracts(container: ServiceContainer) -> dict[str, Any]:
    reports = []
    for meta in container.providers.list_metadata():
        reports.append(contract_check_provider(container.providers.get(meta.provider_id)))
    return {
        "name": "provider_contracts",
        "ok": all(r["ok"] for r in reports) if reports else True,
        "providers": reports,
    }


def check_capability_compatibility(container: ServiceContainer) -> dict[str, Any]:
    issues: list[str] = []
    caps = container.capabilities.list_capabilities()
    provider_ids = set(container.providers.list_ids())
    for cap in caps:
        if not cap.id:
            issues.append("capability sem id")
        if not (cap.tool_name or "").strip():
            issues.append(f"{cap.id}: tool_name ausente")
        for pid in cap.provider_ids or ():
            if pid not in provider_ids:
                # Provider referenciado pode ser opcional/scaffold — warning, não hard fail
                issues.append(f"{cap.id}: provider_id não registrado: {pid}")
    # Soft: provider_ids missing = warning list; ok se só tool_name/id ok
    hard = [i for i in issues if "tool_name" in i or "sem id" in i]
    return {
        "name": "capability_compatibility",
        "ok": not hard,
        "issues": issues,
        "capabilities": len(caps),
    }


def check_mcp_compatibility(container: ServiceContainer) -> dict[str, Any]:
    from signalhub.apps.mcp.tool_publisher import tools_from_capabilities

    tools = tools_from_capabilities(container.capabilities)
    caps = {c.id: c for c in container.capabilities.list_capabilities()}
    by_tool = {c.tool_name: c for c in caps.values()}
    issues: list[str] = []
    for t in tools:
        name = t.get("name")
        if name not in by_tool:
            issues.append(f"MCP tool {name} sem capability correspondente")
    for cid, cap in caps.items():
        if not any(t.get("name") == cap.tool_name for t in tools):
            issues.append(f"capability {cid} sem tool MCP")
    return {
        "name": "mcp_compatibility",
        "ok": not issues,
        "issues": issues,
        "tools": len(tools),
    }


def check_rest_compatibility(container: ServiceContainer) -> dict[str, Any]:
    """REST deve espelhar capabilities (mesma fonte do container)."""
    from signalhub.admin_snapshot import build_admin_snapshot

    caps = [c.id for c in container.capabilities.list_capabilities()]
    snap = build_admin_snapshot(container)
    snap_caps = [c["id"] for c in snap.get("capabilities") or []]
    issues: list[str] = []
    if sorted(caps) != sorted(snap_caps):
        issues.append("admin snapshot capabilities ≠ registry")
    # Rotas canônicas documentadas
    expected_routes = ["/health", "/v1/capabilities", "/v1/admin/snapshot"]
    return {
        "name": "rest_compatibility",
        "ok": not issues,
        "issues": issues,
        "routes": expected_routes,
        "capabilities": len(caps),
    }


def check_plugin_loader_contracts() -> dict[str, Any]:
    report = PluginLoader().load_all()
    failed = [p for p in report.loaded if not p.ok]
    return {
        "name": "plugin_loader",
        "ok": not failed,
        "issues": [f"{p.manifest.name}: {p.errors}" for p in failed],
        "loaded": len(report.loaded),
    }


def run_contract_suite(container: ServiceContainer) -> dict[str, Any]:
    parts = [
        check_signal_validator(),
        check_provider_contracts(container),
        check_capability_compatibility(container),
        check_mcp_compatibility(container),
        check_rest_compatibility(container),
        check_plugin_loader_contracts(),
        {
            "name": "contract_checker",
            "ok": not contract_check_signal(make_sample_signal()),
            "issues": contract_check_signal(make_sample_signal()),
        },
    ]
    return {
        "ok": all(p["ok"] for p in parts),
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "checks": parts,
    }
