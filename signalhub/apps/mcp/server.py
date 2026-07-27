"""Minimal MCP stdio server (JSON-RPC 2.0).

Business logic is delegated to Orchestrator / CapabilityRegistry.
This module only speaks MCP protocol.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Mapping, TextIO

from signalhub import __version__
from signalhub.apps.mcp.tool_publisher import tools_from_capabilities
from signalhub.bootstrap import build_container
from signalhub.core.orchestrator.service import Orchestrator
from signalhub.core.registry.container import ServiceContainer


PROTOCOL_VERSION = "2024-11-05"


class McpServer:
    def __init__(self, container: ServiceContainer | None = None) -> None:
        self.container = container or build_container()
        self.orchestrator = self.container.resolve(Orchestrator)

    def handle(self, message: Mapping[str, Any]) -> dict[str, Any] | None:
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params") or {}

        if method == "notifications/initialized":
            return None

        if method == "initialize":
            return self._result(
                msg_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "signalhub",
                        "version": __version__,
                    },
                },
            )

        if method == "tools/list":
            tools = tools_from_capabilities(self.container.capabilities)
            return self._result(msg_id, {"tools": tools})

        if method == "tools/call":
            name = str(params.get("name") or "")
            arguments = params.get("arguments") or {}
            try:
                handler = self.container.capabilities.get_by_tool_name(name)
                result = self.orchestrator.execute_capability(
                    handler.capability().id,
                    arguments if isinstance(arguments, Mapping) else {},
                )
                payload = json.dumps(result.to_dict(), ensure_ascii=False)
                return self._result(
                    msg_id,
                    {
                        "content": [{"type": "text", "text": payload}],
                        "isError": result.status.startswith("error"),
                    },
                )
            except KeyError as exc:
                return self._result(
                    msg_id,
                    {
                        "content": [{"type": "text", "text": str(exc)}],
                        "isError": True,
                    },
                )

        if method == "ping":
            return self._result(msg_id, {})

        if msg_id is None:
            return None
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    @staticmethod
    def _result(msg_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def run_stdio_server(
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
) -> None:
    """Read newline-delimited JSON-RPC from stdin; write responses to stdout."""
    server = McpServer()
    inn = stdin or sys.stdin
    out = stdout or sys.stdout
    for line in inn:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            err = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
            out.write(json.dumps(err) + "\n")
            out.flush()
            continue
        response = server.handle(message)
        if response is not None:
            out.write(json.dumps(response, ensure_ascii=False) + "\n")
            out.flush()


if __name__ == "__main__":
    run_stdio_server()
