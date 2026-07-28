"""Shared HTTP dispatch for local HTTPServer and Vercel WSGI — no framework dep."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

from signalhub.admin_snapshot import build_admin_snapshot
from signalhub.bootstrap import build_container
from signalhub.core.orchestrator.service import Orchestrator

_STATE: dict[str, Any] | None = None


def get_state() -> dict[str, Any]:
    global _STATE
    if _STATE is None:
        container = build_container(load_plugins=True)
        _STATE = {
            "container": container,
            "orchestrator": container.resolve(Orchestrator),
        }
    return _STATE


def reset_state() -> None:
    """Test helper — força novo bootstrap."""
    global _STATE
    _STATE = None


def dispatch(
    method: str,
    path: str,
    body: bytes | None = None,
) -> tuple[int, dict[str, Any]]:
    """Retorna (http_status, json_payload). Sem inventar dados."""
    method = (method or "GET").upper()
    path = (path or "/").split("?", 1)[0] or "/"
    state = get_state()
    orch: Orchestrator = state["orchestrator"]
    container = state["container"]

    if method == "GET":
        if path in ("/health", "/"):
            return 200, {
                "status": "ok",
                "product": "signalhub",
                "providers": container.providers.list_ids(),
                "capabilities": [
                    c.id for c in container.capabilities.list_capabilities()
                ],
            }
        if path.startswith("/health/"):
            from signalhub.platform import health as health_mod

            name = path[len("/health/") :].strip("/")
            mapping = {
                "core": health_mod.check_core,
                "providers": lambda: health_mod.check_providers(container),
                "adapters": health_mod.check_adapters,
                "storage": health_mod.check_storage,
                "capabilities": lambda: health_mod.check_capabilities(container),
                "mcp": lambda: health_mod.check_mcp(container),
                "rest": health_mod.check_rest,
                "cli": health_mod.check_cli,
                "telegram": health_mod.check_telegram,
                "dashboard": health_mod.check_dashboard,
                "plugins": health_mod.check_plugins,
            }
            if name == "all":
                payload = health_mod.run_all_health_checks(container)
                return (200 if payload.get("ok") else 503), payload
            fn = mapping.get(name)
            if not fn:
                return 404, {"error": "unknown_health_component", "component": name}
            payload = fn()
            return (200 if payload.get("ok") else 503), payload
        if path == "/v1/capabilities":
            caps = [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "tool_name": c.tool_name,
                    "provider_ids": list(c.provider_ids),
                }
                for c in container.capabilities.list_capabilities()
            ]
            return 200, {"capabilities": caps}
        if path == "/v1/admin/snapshot":
            return 200, build_admin_snapshot(container)
        if path == "/v1/lab/mission-control":
            from signalhub.lab import mission_control_status

            return 200, mission_control_status()
        if path == "/v1/lab/export":
            from signalhub.lab import export_signals

            return 200, export_signals()
        return 404, {"error": "not_found"}

    if method == "POST":
        try:
            raw = body.decode("utf-8") if body else "{}"
            parsed = json.loads(raw or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return 400, {"error": "invalid_json"}
        if path.startswith("/v1/capabilities/") and path.endswith("/execute"):
            capability_id = path[len("/v1/capabilities/") : -len("/execute")]
            result = orch.execute_capability(
                capability_id, parsed if isinstance(parsed, dict) else {}
            )
            return 200, result.to_dict()
        if path == "/v1/lab/generate":
            from signalhub.lab import generate_synthetic

            mode = str((parsed or {}).get("mode") or "valid")
            limit = int((parsed or {}).get("limit") or 1)
            out = generate_synthetic(mode=mode, limit=limit)
            return (200 if out.get("ok") else 400), out
        if path == "/v1/lab/replay":
            from signalhub.lab import replay_signals

            items = (parsed or {}).get("signals") if isinstance(parsed, dict) else None
            if not isinstance(items, list):
                return 400, {"ok": False, "error": "body.signals deve ser lista"}
            out = replay_signals(items)
            return 200, out
        return 404, {"error": "not_found"}

    return 405, {"error": "method_not_allowed", "method": method}


def app(environ: dict[str, Any], start_response: Any) -> list[bytes]:
    """WSGI entrypoint — Vercel (`tool.vercel.entrypoint`) e servidores WSGI."""
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO") or "/"
    # Query string disponível se um dia precisarmos; rotas atuais ignoram.
    _ = parse_qs(environ.get("QUERY_STRING") or "")
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""
    status, payload = dispatch(method, path, body)
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    start_response(
        f"{status} {'OK' if status < 400 else 'ERR'}",
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(raw))),
        ],
    )
    return [raw]
