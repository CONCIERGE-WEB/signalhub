"""REST API skeleton — same Core as MCP. Local HTTPServer + Vercel WSGI."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from signalhub.apps.api.http_dispatch import app, dispatch, get_state

__all__ = ["SignalHubApiHandler", "app", "create_app_state", "dispatch", "run_api"]


def create_app_state() -> dict[str, Any]:
    return get_state()


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
        code, payload = dispatch("GET", path)
        self._json(code, payload)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        code, payload = dispatch("POST", path, raw)
        self._json(code, payload)


def run_api(host: str = "127.0.0.1", port: int = 8787) -> None:
    SignalHubApiHandler.state = create_app_state()
    server = HTTPServer((host, port), SignalHubApiHandler)
    print(f"SignalHub API on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_api()
