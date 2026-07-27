from __future__ import annotations

from typing import Any

from signalhub.core.contracts.capability import Capability
from signalhub.core.registry.capabilities import CapabilityRegistry


def tools_from_capabilities(registry: CapabilityRegistry) -> list[dict[str, Any]]:
    """Project capabilities into MCP tool descriptors — zero business logic."""
    tools: list[dict[str, Any]] = []
    for cap in registry.list_capabilities():
        tools.append(_capability_to_tool(cap))
    return tools


def _capability_to_tool(cap: Capability) -> dict[str, Any]:
    return {
        "name": cap.tool_name,
        "description": cap.description,
        "inputSchema": dict(cap.input_schema),
    }
