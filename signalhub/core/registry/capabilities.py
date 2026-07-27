from __future__ import annotations

from signalhub.core.contracts.capability import Capability, CapabilityHandler


class CapabilityRegistry:
    """Capabilities are the product surface — MCP tools are projections."""

    def __init__(self) -> None:
        self._handlers: dict[str, CapabilityHandler] = {}

    def register(self, handler: CapabilityHandler, *, replace: bool = False) -> None:
        cap = handler.capability()
        key = cap.id.strip().lower()
        if not key:
            raise ValueError("capability id vazio")
        if key in self._handlers and not replace:
            raise KeyError(f"capability já registrada: {key}")
        if not cap.enabled:
            return
        self._handlers[key] = handler

    def get(self, capability_id: str) -> CapabilityHandler:
        key = capability_id.strip().lower()
        if key not in self._handlers:
            raise KeyError(
                f"capability '{capability_id}' não registrada. "
                f"Disponíveis: {sorted(self._handlers)}"
            )
        return self._handlers[key]

    def get_by_tool_name(self, tool_name: str) -> CapabilityHandler:
        name = tool_name.strip().lower()
        for handler in self._handlers.values():
            if handler.capability().tool_name.lower() == name:
                return handler
        raise KeyError(f"tool MCP '{tool_name}' sem capability")

    def list_capabilities(self) -> list[Capability]:
        return [h.capability() for h in self._handlers.values()]

    def list_tool_names(self) -> list[str]:
        return sorted(c.tool_name for c in self.list_capabilities())
