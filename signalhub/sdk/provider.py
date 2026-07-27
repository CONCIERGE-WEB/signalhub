"""SDK — Provider plugins extend discovery without touching Core."""
from __future__ import annotations

from signalhub.providers.base import BaseProvider

# Public alias — third parties subclass this (RFC-0001 compatible).
ProviderPlugin = BaseProvider

__all__ = ["ProviderPlugin", "BaseProvider"]
