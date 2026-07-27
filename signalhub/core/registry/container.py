from __future__ import annotations

from typing import Any, Callable, TypeVar

from .capabilities import CapabilityRegistry
from .providers import ProviderRegistry

T = TypeVar("T")


class ServiceContainer:
    """Minimal DI — constructors receive explicit deps; container wires them."""

    def __init__(self) -> None:
        self.providers = ProviderRegistry()
        self.capabilities = CapabilityRegistry()
        self._singletons: dict[type[Any], Any] = {}
        self._factories: dict[type[Any], Callable[[ServiceContainer], Any]] = {}

    def register_singleton(self, iface: type[T], instance: T) -> None:
        self._singletons[iface] = instance

    def register_factory(
        self,
        iface: type[T],
        factory: Callable[[ServiceContainer], T],
    ) -> None:
        self._factories[iface] = factory

    def resolve(self, iface: type[T]) -> T:
        if iface in self._singletons:
            return self._singletons[iface]  # type: ignore[return-value]
        factory = self._factories.get(iface)
        if factory is None:
            raise KeyError(f"serviço não registrado: {iface!r}")
        instance = factory(self)
        self._singletons[iface] = instance
        return instance  # type: ignore[return-value]
