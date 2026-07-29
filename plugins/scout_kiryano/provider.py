from __future__ import annotations

import os
import time
from typing import Sequence

from signalhub.core.contracts.provider import HealthStatus, ProviderQuery, RawHit
from signalhub.sdk import ProviderPlugin

from scout_kiryano.adapter import PRODUCT_NAME, profiles_to_raw_hits
from scout_kiryano.connectors import SUPPORTED, scrape


def live_enabled() -> bool:
    return (os.environ.get("SIGNALHUB_SCOUT_KIRYANO_LIVE") or "").strip() in (
        "1",
        "true",
        "yes",
    )


class ScoutKiryanoProvider(ProviderPlugin):
    """Source Provider — Prospecção | Tiago A. Rocha (kiryano/Scout MIT).

    Live network: SIGNALHUB_SCOUT_KIRYANO_LIVE=1.
    Query extras: platform=youtube|linktree|github; terms = handles.
    GitHub profiles are rejected by B2B gate (B2C-only).
    Never invents contacts. Rate-limit → empty hit, process continues.
    """

    provider_id = "scout_kiryano"
    provider_name = PRODUCT_NAME
    version = "0.2.0"
    description = (
        f"{PRODUCT_NAME}: Source Provider (kiryano/Scout MIT) com 9 categorias "
        "oficiais B2C, quality gate anti-B2B e trava de privacidade família."
    )
    capability_ids = (
        "discover_signals",
        "search_companies",
        "search_signals",
    )

    def healthcheck(self) -> HealthStatus:
        live = live_enabled()
        detail = (
            f"{PRODUCT_NAME} — platforms={','.join(SUPPORTED)}; "
            f"live={'on' if live else 'off (empty explicit until SIGNALHUB_SCOUT_KIRYANO_LIVE=1)'}"
        )
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail=detail,
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        if not live_enabled():
            return ()

        extras = dict(query.extras or {})
        platform = str(extras.get("platform") or "youtube").strip().lower()
        targets = [str(t).strip().lstrip("@") for t in (query.terms or ()) if str(t).strip()]
        if not targets and extras.get("target"):
            targets = [str(extras["target"]).strip().lstrip("@")]
        if not targets:
            return ()

        profiles: list[dict] = []
        t0 = time.perf_counter()
        for target in targets[: max(1, query.limit)]:
            try:
                profile = scrape(platform, target)
            except Exception as exc:  # noqa: BLE001
                _ = exc
                continue
            if profile:
                profiles.append(profile)
        _ = t0
        return profiles_to_raw_hits(profiles, limit=max(1, query.limit))
