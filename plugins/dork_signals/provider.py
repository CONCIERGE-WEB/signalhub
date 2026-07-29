from __future__ import annotations

import time
from typing import Sequence

from signalhub.core.contracts.provider import HealthStatus, ProviderQuery, RawHit
from signalhub.sdk import ProviderPlugin

from dork_signals.adapter import posts_to_raw_hits
from dork_signals.certification import certification_scorecard
from dork_signals.engine_bridge import live_enabled, resolve_dorks_config, scan_sync
from dork_signals.metrics import ENGINE_METRICS


class DorkSignalsProvider(ProviderPlugin):
    """Discovery Engine — Dorking multi-source (Cliente Zero #2).

    Reuses engine DorkScanner + YAML dorks (Reddit, Reclame Aqui, social site:,
    GitHub, websites, forums…). Emits **Signal** only via RawHit → normalize.
    Never invents hits. Live network: SIGNALHUB_DORKING_LIVE=1.
    """

    provider_id = "dorking"
    provider_name = "Discovery Engine (Dorking)"
    version = "1.0.0"
    description = (
        "Certified Discovery Engine: multi-source public discovery via existing "
        "Dorking (YAML + DDGS + Reddit/HN/RSS). Rate-limit and ToS live in this "
        "plugin — Core only orchestrates Signals."
    )
    capability_ids = (
        "discover_signals",
        "search_law_topics",
        "search_signals",
    )

    def healthcheck(self) -> HealthStatus:
        cfg = resolve_dorks_config()
        live = live_enabled()
        ENGINE_METRICS.live_enabled = live
        ENGINE_METRICS.config_path = str(cfg) if cfg else None
        card = certification_scorecard(
            live=live, config_ok=cfg is not None, adapter_ok=True
        )
        if card["status"] == "certified":
            detail = (
                f"Discovery Engine — {card['label']}; "
                f"live={'on' if live else 'off (empty explicit until SIGNALHUB_DORKING_LIVE=1)'}"
            )
        else:
            detail = f"Discovery Engine — {card['label']}"
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail=detail,
            latency_ms=ENGINE_METRICS.avg_ms,
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        cfg = resolve_dorks_config()
        live = live_enabled()
        ENGINE_METRICS.live_enabled = live
        ENGINE_METRICS.config_path = str(cfg) if cfg else None

        if not live or cfg is None:
            # Empty explicit — certified path idle until operator enables live scan.
            return ()

        t0 = time.perf_counter()
        error: str | None = None
        posts: list = []
        try:
            # Optional batch size from extras (operator); default small for safety.
            limite = None
            extras = dict(query.extras or {})
            if "dork_limit" in extras:
                try:
                    limite = int(extras["dork_limit"])
                except (TypeError, ValueError):
                    limite = None
            posts = scan_sync(limite=limite)
        except Exception as exc:  # noqa: BLE001 — surface as empty + metric; no fake hits
            error = str(exc)
            posts = []

        hits = posts_to_raw_hits(posts, limit=max(1, query.limit))
        # Dedup metric: posts with URL vs unique hits
        urls = [p.get("link") or p.get("url") for p in posts if p.get("link") or p.get("url")]
        duplicated = max(0, len(urls) - len({u for u in urls if u}))
        discarded = max(0, len(posts) - len(hits))
        categories: dict[str, int] = {}
        origins: dict[str, int] = {}
        for h in hits:
            if h.category:
                categories[h.category] = categories.get(h.category, 0) + 1
            if h.source:
                origins[h.source] = origins.get(h.source, 0) + 1

        ENGINE_METRICS.record_run(
            duration_ms=(time.perf_counter() - t0) * 1000.0,
            pages=len(posts),
            produced=len(hits),
            discarded=discarded,
            duplicated=duplicated,
            categories=categories,
            origins=origins,
            error=error,
        )
        return hits

    def certification(self) -> dict:
        return certification_scorecard(
            live=live_enabled(),
            config_ok=resolve_dorks_config() is not None,
            adapter_ok=True,
        )
