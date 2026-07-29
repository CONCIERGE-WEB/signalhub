"""
Connectors package — adapted scrapers from kiryano/Scout (MIT).
Copyright (c) 2026 Scout — see third_party/kiryano_scout/LICENSE

Only public-profile extractors. No SMTP email guessing / pattern invention.
"""

from __future__ import annotations

from typing import Any, Callable

from scout_kiryano.connectors import github, linktree, youtube

PLATFORMS: dict[str, Callable[[str], dict[str, Any] | None]] = {
    "github": github.scrape_profile,
    "youtube": youtube.scrape_channel,
    "linktree": linktree.scrape_linktree,
}

SUPPORTED = tuple(PLATFORMS.keys())


def scrape(platform: str, target: str) -> dict[str, Any] | None:
    """Run one connector. Returns profile dict or None (not found / blocked)."""
    key = (platform or "").strip().lower()
    fn = PLATFORMS.get(key)
    if fn is None:
        raise ValueError(f"unsupported platform: {platform!r}; choose {SUPPORTED}")
    target = (target or "").strip().lstrip("@")
    if not target:
        return None
    return fn(target)
