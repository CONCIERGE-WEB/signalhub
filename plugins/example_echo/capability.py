from __future__ import annotations

from typing import Any, Mapping

from signalhub.sdk import Capability, CapabilityPlugin, CapabilityResult


class ExampleEchoCapability(CapabilityPlugin):
    """Consumes nothing from Providers — returns empty stub (didactic)."""

    def capability(self) -> Capability:
        return Capability(
            id="example_echo",
            name="Example Echo",
            description="Didactic capability — demonstrates plugin MCP tool registration.",
            input_schema={"type": "object", "properties": {"note": {"type": "string"}}},
            mcp_tool_name="example_echo",
        )

    def execute(self, arguments: Mapping[str, Any]) -> CapabilityResult:
        return CapabilityResult(
            capability_id="example_echo",
            status="ok_stub",
            items=[],
            meta={"ai": False, "note": arguments.get("note"), "plugin": "example_echo"},
        )
