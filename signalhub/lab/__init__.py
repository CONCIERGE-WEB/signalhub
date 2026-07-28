"""Lab ops — generate / export / replay com Debug Provider (sem rede)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from signalhub.bootstrap import build_container, build_orchestrator
from signalhub.core.contracts.pipeline import PipelineContext
from signalhub.core.models import Provenance, Signal
from signalhub.core.models.common import EntityId
from signalhub.core.models.signal import (
    SIGNAL_CONTRACT_VERSION,
    SignalPriority,
    SignalStatus,
    SignalType,
)
from signalhub.plugins import PluginLoader
from signalhub.platform.health import run_all_health_checks
from signalhub.observability.metrics import platform_metrics
from signalhub.storage import DEFAULT_SIGNAL_STORE

LAB_MODES = (
    "valid",
    "invalid",
    "high_score",
    "low_score",
    "bad_url",
    "duplicate",
    "huge_metadata",
    "unknown_category",
    "bad_timestamp",
)


def generate_synthetic(*, mode: str = "valid", limit: int = 1) -> dict[str, Any]:
    mode = (mode or "valid").strip().lower()
    if mode not in LAB_MODES:
        return {"ok": False, "error": f"mode inválido: {mode}", "modes": list(LAB_MODES)}
    orch = build_orchestrator(load_plugins=True)
    signals = orch.discover_signals(
        capability_id="discover_signals",
        provider_ids=["debug"],
        terms=(mode,),
        limit=limit,
    )
    return {
        "ok": True,
        "mode": mode,
        "count": len(signals),
        "signals": [s.to_dict() for s in signals],
        "stored_recent": len(DEFAULT_SIGNAL_STORE.list_recent(limit=50)),
    }


def export_signals(*, limit: int = 100) -> dict[str, Any]:
    items = DEFAULT_SIGNAL_STORE.list_recent(limit=limit)
    return {
        "ok": True,
        "count": len(items),
        "signals": [s.to_dict() for s in items],
        "contract_version": SIGNAL_CONTRACT_VERSION,
    }


def export_to_path(path: Path, *, limit: int = 100) -> dict[str, Any]:
    payload = export_signals(limit=limit)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["path"] = str(path)
    return payload


def signal_from_dict(raw: Mapping[str, Any]) -> Signal:
    prov_raw = raw.get("provenance") if isinstance(raw.get("provenance"), dict) else None
    provenance = None
    if prov_raw:
        provenance = Provenance(
            provider_id=str(prov_raw.get("provider_id") or raw.get("provider") or "debug"),
            source_url=prov_raw.get("source_url"),
            origin=str(prov_raw.get("origin") or "replay"),
            content_hash=str(prov_raw.get("content_hash") or ""),
        )
    st = str(raw.get("signal_type") or "other")
    try:
        signal_type = SignalType(st)
    except ValueError:
        signal_type = SignalType.OTHER
    pr = str(raw.get("priority") or "normal")
    try:
        priority = SignalPriority(pr)
    except ValueError:
        priority = SignalPriority.NORMAL
    return Signal(
        id=EntityId(str(raw.get("id") or "replay:unknown")),
        provider=str(raw.get("provider") or "debug"),
        title=str(raw.get("title") or ""),
        source=str(raw.get("source") or "replay"),
        summary=str(raw.get("summary") or ""),
        url=raw.get("url"),
        category=raw.get("category"),
        signal_type=signal_type,
        priority=priority,
        metadata=dict(raw.get("metadata") or {}),
        provenance=provenance,
        status=SignalStatus.DISCOVERED,
        version=str(raw.get("version") or "1"),
        contract_version=str(raw.get("contract_version") or SIGNAL_CONTRACT_VERSION),
    )


def replay_signals(payloads: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    orch = build_orchestrator(load_plugins=True)
    signals = [signal_from_dict(p) for p in payloads]
    ctx = PipelineContext(capability_id="lab_replay", signals=list(signals))
    ctx = orch.pipeline.run(ctx)
    for signal in ctx.signals:
        orch.telegram.enqueue(signal)
    return {
        "ok": True,
        "input": len(payloads),
        "output": len(ctx.signals),
        "errors": list(ctx.errors),
        "signals": [s.to_dict() for s in ctx.signals],
        "attributes": dict(ctx.attributes),
    }


def replay_from_path(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("signals") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return {"ok": False, "error": "JSON deve ter lista 'signals' ou ser uma lista"}
    return replay_signals(items)


def mission_control_status() -> dict[str, Any]:
    from signalhub import __version__

    container = build_container(load_plugins=True)
    health = run_all_health_checks(container)
    by = {c["component"]: c for c in health.get("checks") or []}
    plugin_report = PluginLoader().load_all()
    plugins_loaded = sum(1 for p in plugin_report.loaded if p.ok)

    providers = []
    for meta in container.providers.list_metadata():
        p = container.providers.get(meta.provider_id)
        h = p.healthcheck()
        detail = h.detail or ""
        providers.append(
            {
                "id": meta.provider_id,
                "name": meta.name,
                "ok": h.ok,
                "detail": detail,
                "scaffold": any(
                    x in detail.lower()
                    for x in ("scaffold", "not wired", "empty explicit")
                ),
                "lab": meta.provider_id == "debug",
            }
        )

    metrics = platform_metrics().snapshot()
    avg = metrics.get("provider_avg_ms") or {}
    latency = avg.get("debug")
    if latency is None and avg:
        latency = next(iter(avg.values()), None)

    def surface(key: str, *, running: str = "healthy", down: str = "down") -> dict[str, Any]:
        item = by.get(key) or {}
        ok = bool(item.get("ok"))
        return {"status": running if ok else down, "ok": ok, "detail": item.get("detail")}

    return {
        "product": "signalhub",
        "core": {
            "status": "running" if by.get("core", {}).get("ok") else "down",
            "version": __version__,
            "ok": bool(by.get("core", {}).get("ok")),
        },
        "contract": {"version": SIGNAL_CONTRACT_VERSION, "ok": True},
        "rest": surface("rest"),
        "mcp": {
            **surface("mcp", running="ready", down="disabled"),
            "note": "stdio — use `python -m signalhub.apps.cli mcp`",
        },
        "cli": surface("cli"),
        "dashboard": {
            **surface("dashboard", running="connected", down="unknown"),
            "note": "Web via Adapter",
        },
        "storage": {
            **surface("storage", running="memory", down="down"),
            "backend": "InMemorySignalStore",
            "note": "PostgreSQL é fase futura — lab usa memória",
        },
        "telegram": {
            **surface("telegram", running="active", down="down"),
            "note": "in-process (Bot API send experimental)",
        },
        "plugins": {
            "ok": bool(by.get("plugins", {}).get("ok")),
            "loaded": plugins_loaded,
            "detail": by.get("plugins", {}).get("detail"),
        },
        "providers": providers,
        "metrics": {
            "signals_today": int(metrics.get("signals_produced") or 0),
            "rules": int(metrics.get("rules_applied") or 0),
            "errors": int(metrics.get("signals_invalid") or 0),
            "latency_ms": latency,
        },
        "health": health,
        "lab": {
            "debug_provider": any(p["id"] == "debug" for p in providers),
            "modes": list(LAB_MODES),
        },
    }
