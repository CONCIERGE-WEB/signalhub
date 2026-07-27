"""Registries — providers, capabilities, DI container."""
from .capabilities import CapabilityRegistry
from .container import ServiceContainer
from .providers import ProviderRegistry

__all__ = ["CapabilityRegistry", "ProviderRegistry", "ServiceContainer"]
