"""DEPRECATED in Core — Prospector is Cliente Zero plugin.

Use: plugins/prospector_tiagorocha (provider_id=\"prospector_tiagorocha\").
This module remains only so old imports fail loudly with guidance.
"""
from __future__ import annotations


class ScoutProvider:  # noqa: D101
    def __init__(self) -> None:
        raise ImportError(
            "Discovery Engine left the Core. Use plugin plugins/prospector_tiagorocha "
            "(Prospector | Tiago A. Rocha / Cliente Zero). "
            "Do not import signalhub.providers.scout. "
            "kiryano/Scout (MIT) is a future Source Provider — not this module."
        )
