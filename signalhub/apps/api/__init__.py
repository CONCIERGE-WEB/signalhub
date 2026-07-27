"""REST API skeleton — same Core as MCP."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from signalhub.admin_snapshot import build_admin_snapshot
from signalhub.bootstrap import build_container
from signalhub.core.orchestrator.service import Orchestrator


def create_app_state() -> dict[str, Any]:
    container = build_container()
    return {
        "container": container,
        "orchestrator": container.resolve(Orchestrator),
    }


class SignalHubApiHandler(BaseHTTPRequestHandler):
    state: dict[str, Any] = {}

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _json(self, code: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        orch: Orchestrator = self.state["orchestrator"]
        container = self.state["container"]
        if path in ("/health", "/"):
            self._json(
                200,
                {
                    "status": "ok",
                    "providers": container.providers.list_ids(),
                    "capabilities": [c.id for c in container.capabilities.list_capabilities()],
                },
            )
            return
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
            self._json(200, {"capabilities": caps})
            return
        if path == "/v1/admin/snapshot":
            self._json(200, build_admin_snapshot(container))
            return
        _ = orch
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return

        if path.startswith("/v1/capabilities/") and path.endswith("/execute"):
            capability_id = path[len("/v1/capabilities/") : -len("/execute")]
            orch: Orchestrator = self.state["orchestrator"]
            result = orch.execute_capability(capability_id, body if isinstance(body, dict) else {})
            self._json(200, result.to_dict())
            return

        self._json(404, {"error": "not_found"})


def run_api(host: str = "127.0.0.1", port: int = 8787) -> None:
    SignalHubApiHandler.state = create_app_state()
    server = HTTPServer((host, port), SignalHubApiHandler)
    print(f"SignalHub API on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_api()
