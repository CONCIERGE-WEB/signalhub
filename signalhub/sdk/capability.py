"""SDK — Capability plugins consume Signals; never mutate stored instances."""
from __future__ import annotations

from signalhub.core.contracts.capability import Capability, CapabilityHandler, CapabilityResult

CapabilityPlugin = CapabilityHandler

__all__ = ["Capability", "CapabilityHandler", "CapabilityPlugin", "CapabilityResult"]
