"""Developer Platform — SDK surfaces for third-party extensions.

Core stays stable. Extend via Providers, Capabilities, Adapters, Consumers, Rulesets.
SignalHub is a signal-processing framework — source integrations are independent plugins
subject to each platform's terms of use.
"""
from __future__ import annotations

from signalhub.sdk.adapter import NotificationAdapterPort
from signalhub.sdk.capability import (
    Capability,
    CapabilityHandler,
    CapabilityPlugin,
    CapabilityResult,
)
from signalhub.sdk.consumer import SignalConsumer
from signalhub.sdk.provider import BaseProvider, ProviderPlugin
from signalhub.sdk.ruleset import RulesetPlugin

__all__ = [
    "BaseProvider",
    "Capability",
    "CapabilityHandler",
    "CapabilityPlugin",
    "CapabilityResult",
    "NotificationAdapterPort",
    "ProviderPlugin",
    "RulesetPlugin",
    "SignalConsumer",
]
