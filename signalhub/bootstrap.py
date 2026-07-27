"""Wire Core builtins + plugins. Scout/Dorking = Cliente Zero plugins."""
from __future__ import annotations

from signalhub.capabilities import (
    AnalyzeSignalHandler,
    DEFAULT_HANDLER_TYPES,
    DiscoverLeadsHandler,
    DiscoverSignalsHandler,
    GetMetricsHandler,
    GetProviderStatusHandler,
    GetRecentSignalsHandler,
    ListSourcesHandler,
    SearchByCategoryHandler,
    SearchCompaniesHandler,
    SearchLawTopicsHandler,
    SearchSignalsHandler,
)
from signalhub.core.orchestrator.service import Orchestrator
from signalhub.core.registry.container import ServiceContainer
from signalhub.plugins import PluginLoader
from signalhub.providers.github.provider import GitHubProvider
from signalhub.providers.google.provider import GoogleProvider
from signalhub.providers.linkedin.provider import LinkedInProvider
from signalhub.providers.websites.provider import WebsitesProvider
from signalhub.security.policy import SecurityPolicy
from signalhub.storage import DEFAULT_SIGNAL_STORE


def build_container(
    *,
    policy: SecurityPolicy | None = None,
    load_plugins: bool = True,
) -> ServiceContainer:
    container = ServiceContainer()
    # Built-in stubs only — Scout/Dorking are Cliente Zero plugins.
    for provider in (
        GoogleProvider(),
        WebsitesProvider(),
        LinkedInProvider(),
        GitHubProvider(),
    ):
        container.providers.register(provider)

    orch = Orchestrator(
        providers=container.providers,
        capabilities=container.capabilities,
        policy=policy or SecurityPolicy(),
        store=DEFAULT_SIGNAL_STORE,
    )
    container.register_singleton(Orchestrator, orch)

    for handler in (
        DiscoverSignalsHandler(orch),
        SearchSignalsHandler(orch),
        SearchByCategoryHandler(orch),
        ListSourcesHandler(orch),
        GetProviderStatusHandler(orch),
        GetMetricsHandler(orch),
        GetRecentSignalsHandler(orch),
        SearchCompaniesHandler(orch),
        SearchLawTopicsHandler(orch),
        AnalyzeSignalHandler(),
        DiscoverLeadsHandler(orch),
    ):
        container.capabilities.register(handler)

    if load_plugins:
        PluginLoader().apply_to_container(container)

    _ = DEFAULT_HANDLER_TYPES
    return container


def build_orchestrator(
    *,
    policy: SecurityPolicy | None = None,
    load_plugins: bool = True,
) -> Orchestrator:
    return build_container(policy=policy, load_plugins=load_plugins).resolve(Orchestrator)
