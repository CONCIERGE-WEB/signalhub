"""DEPRECATED in Core — Dorking is Cliente Zero plugin.

Use: plugins/dork_signals (provider_id=\"dorking\").
"""
from __future__ import annotations


class DorkingProvider:  # noqa: D101
    def __init__(self) -> None:
        raise ImportError(
            "Dorking left the Core. Load plugin plugins/dork_signals "
            "(Cliente Zero #2). Do not import signalhub.providers.dorking."
        )
