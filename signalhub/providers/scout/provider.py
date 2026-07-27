"""DEPRECATED in Core — Scout is Cliente Zero plugin.

Use: plugins/scout_signals (provider_id=\"scout\").
This module remains only so old imports fail loudly with guidance.
"""
from __future__ import annotations


class ScoutProvider:  # noqa: D101
    def __init__(self) -> None:
        raise ImportError(
            "Scout left the Core. Install/load plugin plugins/scout_signals "
            "(Cliente Zero). Do not import signalhub.providers.scout."
        )
