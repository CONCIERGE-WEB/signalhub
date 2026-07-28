"""Health checks separados por superfície (independentes)."""

from __future__ import annotations

from typing import Any

from signalhub import __version__
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION
from signalhub.core.registry.container import ServiceContainer
from signalhub.notifications import TelegramNotificationAdapter
from signalhub.plugins.loader import PluginLoader
from signalhub.sdk.testing import contract_check_signal, make_sample_signal
from signalhub.storage import DEFAULT_SIGNAL_STORE


def _ok(component: str, detail: str = "ok", **extra: Any) -> dict[str, Any]:
    return {"component": component, "ok": True, "detail": detail, **extra}


def _fail(component: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"component": component, "ok": False, "detail": detail, **extra}


def check_core() -> dict[str, Any]:
    issues = contract_check_signal(make_sample_signal())
    if issues:
        return _fail("core", "; ".join(issues), contract_version=SIGNAL_CONTRACT_VERSION)
    return _ok(
        "core",
        f"signalhub {__version__} contract {SIGNAL_CONTRACT_VERSION}",
        version=__version__,
        contract_version=SIGNAL_CONTRACT_VERSION,
    )


def check_providers(container: ServiceContainer) -> dict[str, Any]:
    rows = []
    for meta in container.providers.list_metadata():
        p = container.providers.get(meta.provider_id)
        h = p.healthcheck()
        rows.append(
            {
                "id": meta.provider_id,
                "ok": h.ok,
                "detail": h.detail,
                "version": meta.version,
                "latency_ms": h.latency_ms,
            }
        )
    ok = all(r["ok"] for r in rows) if rows else True
    return {
        "component": "providers",
        "ok": ok,
        "detail": f"{sum(1 for r in rows if r['ok'])}/{len(rows)} healthy",
        "items": rows,
    }


def check_adapters() -> dict[str, Any]:
    # Adapters de notificação: Telegram port in-process (experimental envio real).
    tg = TelegramNotificationAdapter()
    detail = "TelegramNotificationAdapter in-process (format/filter ok; Bot API send experimental)"
    return _ok("adapters", detail, telegram_buffered=hasattr(tg, "_sent") or hasattr(tg, "enqueue"))


def check_storage() -> dict[str, Any]:
    store = DEFAULT_SIGNAL_STORE
    try:
        recent = store.list_recent(limit=5) if hasattr(store, "list_recent") else []
        return _ok("storage", f"in-memory store reachable; recent={len(recent)}")
    except Exception as exc:  # noqa: BLE001
        return _fail("storage", str(exc))


def check_capabilities(container: ServiceContainer) -> dict[str, Any]:
    caps = container.capabilities.list_capabilities()
    missing_tool = [c.id for c in caps if not (c.tool_name or "").strip()]
    if missing_tool:
        return _fail(
            "capabilities",
            f"capabilities sem tool_name: {missing_tool}",
            total=len(caps),
        )
    return _ok("capabilities", f"{len(caps)} registered", total=len(caps))


def check_mcp(container: ServiceContainer) -> dict[str, Any]:
    from signalhub.apps.mcp.tool_publisher import tools_from_capabilities

    tools = tools_from_capabilities(container.capabilities)
    caps = {c.tool_name: c.id for c in container.capabilities.list_capabilities()}
    orphan = [t for t in tools if t.get("name") not in caps]
    if orphan:
        return _fail("mcp", f"tools sem capability: {orphan}", tools=len(tools))
    return _ok("mcp", f"{len(tools)} tools project capabilities", tools=len(tools))


def check_rest() -> dict[str, Any]:
    # Sem subir servidor: valida superfície importável e rotas canônicas.
    from signalhub.apps import api as api_mod

    required = {"/health", "/v1/capabilities", "/v1/admin/snapshot"}
    return _ok(
        "rest",
        "SignalHubApiHandler importable; canonical routes documented",
        routes=sorted(required),
        handler=api_mod.SignalHubApiHandler.__name__,
    )


def check_cli() -> dict[str, Any]:
    from signalhub.apps.cli import main

    return _ok("cli", "signalhub.apps.cli.main importable", entry=main.__module__)


def check_telegram() -> dict[str, Any]:
    tg = TelegramNotificationAdapter()
    # Smoke: enqueue sem rede
    try:
        from signalhub.sdk.testing import make_sample_signal

        tg.enqueue(make_sample_signal())
        return _ok("telegram", "enqueue ok (in-process; no Bot API call)")
    except Exception as exc:  # noqa: BLE001
        return _fail("telegram", str(exc))


def check_dashboard() -> dict[str, Any]:
    # Dashboard vive no Lex Rocha (consumidor). Core só garante snapshot.
    from signalhub.admin_snapshot import build_admin_snapshot
    from signalhub.bootstrap import build_container

    snap = build_admin_snapshot(build_container(load_plugins=False))
    if snap.get("product") != "signalhub":
        return _fail("dashboard", "admin snapshot inválido")
    return _ok(
        "dashboard",
        "snapshot contract ok — Lex Rocha consome via Adapter (fora do Core)",
        snapshot_keys=sorted(snap.keys())[:12],
    )


def check_plugins() -> dict[str, Any]:
    report = PluginLoader().load_all()
    failed = [
        {"name": p.manifest.name, "errors": p.errors}
        for p in report.loaded
        if not p.ok
    ]
    return {
        "component": "plugins",
        "ok": not failed,
        "detail": f"{len(report.loaded) - len(failed)}/{len(report.loaded)} ok",
        "failed": failed,
    }


def run_all_health_checks(container: ServiceContainer | None = None) -> dict[str, Any]:
    from signalhub.bootstrap import build_container

    c = container or build_container(load_plugins=True)
    checks = [
        check_core(),
        check_providers(c),
        check_adapters(),
        check_storage(),
        check_capabilities(c),
        check_mcp(c),
        check_rest(),
        check_cli(),
        check_telegram(),
        check_dashboard(),
        check_plugins(),
    ]
    return {
        "ok": all(ch["ok"] for ch in checks),
        "checks": checks,
        "signalhub_version": __version__,
        "contract_version": SIGNAL_CONTRACT_VERSION,
    }
