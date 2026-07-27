from __future__ import annotations

from signalhub.core.contracts.provider import Provider, ProviderMetadata


class ProviderRegistry:
    """Register / load / discover providers. No provider knows another."""

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider, *, replace: bool = False) -> None:
        meta = provider.metadata()
        key = meta.provider_id.strip().lower()
        if not key:
            raise ValueError("provider_id vazio")
        if key in self._providers and not replace:
            raise KeyError(f"provider já registrado: {key}")
        self._providers[key] = provider

    def get(self, provider_id: str) -> Provider:
        key = provider_id.strip().lower()
        if key not in self._providers:
            raise KeyError(
                f"provider '{provider_id}' não registrado. "
                f"Disponíveis: {sorted(self._providers)}"
            )
        return self._providers[key]

    def list_ids(self) -> list[str]:
        return sorted(self._providers)

    def list_metadata(self) -> list[ProviderMetadata]:
        return [p.metadata() for p in self._providers.values()]

    def enabled(self, allowed: set[str] | None = None) -> list[Provider]:
        if allowed is None:
            return list(self._providers.values())
        allow = {a.strip().lower() for a in allowed}
        return [p for pid, p in self._providers.items() if pid in allow]
