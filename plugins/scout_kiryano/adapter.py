"""Map scout_kiryano profile → RFC-0001 RawHit. Never invent fields."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from signalhub.core.contracts.provider import RawHit
from signalhub.core.models import Provenance

from scout_kiryano.quality import evaluate

PROVIDER_ID = "scout_kiryano"


def profile_to_raw_hit(
    profile: Mapping[str, Any],
    *,
    provider_id: str = PROVIDER_ID,
    include_rejected: bool = False,
) -> RawHit | None:
    gate = evaluate(profile)
    if gate["status"] != "accepted" and not include_rejected:
        return None
    if gate["status"] == "rejected_empty":
        return None

    p = gate["profile"] or {}
    url = (p.get("profile_url") or "").strip() or None
    if not url:
        return None

    title = (p.get("full_name") or p.get("username") or url)[:200]
    bio = str(p.get("bio") or "")
    snippet = bio[:800] if bio else f"{p.get('platform', '')} @{p.get('username', '')}"
    platform = str(p.get("platform") or "websites")
    external_seed = f"{url}|{platform}|{p.get('username', '')}"
    external_id = hashlib.sha256(external_seed.encode("utf-8")).hexdigest()[:24]
    content_hash = hashlib.sha256(
        f"{title}\n{snippet}\n{url}".encode("utf-8")
    ).hexdigest()

    raw = {
        "username": p.get("username"),
        "full_name": p.get("full_name"),
        "email": p.get("email") or "",
        "phone": p.get("phone") or "",
        "website": p.get("website") or "",
        "platform": platform,
        "follower_count": p.get("follower_count"),
        "quality_status": gate["status"],
        "quality_score": gate["score"],
        "quality_reasons": gate["reasons"],
        "contact_ok": gate["contact_ok"],
    }
    # Only pass through real socials if present — never fabricate.
    if isinstance(p.get("socials"), dict) and p["socials"]:
        raw["socials"] = p["socials"]

    return RawHit(
        external_id=external_id,
        title=str(title),
        url=url,
        snippet=snippet,
        signal_type="public_profile",
        category="consumer",
        source=platform,
        raw=raw,
        provenance=Provenance(
            provider_id=provider_id,
            source_url=url,
            origin=platform,
            content_hash=content_hash,
            source_kind="public",
            extras={
                "collected_via": "scout_kiryano",
                "upstream": "kiryano/Scout",
                "license": "MIT",
                "quality_status": gate["status"],
                "quality_score": gate["score"],
            },
        ),
    )


def profiles_to_raw_hits(
    profiles: list[Mapping[str, Any]],
    *,
    limit: int = 40,
    include_rejected: bool = False,
) -> list[RawHit]:
    out: list[RawHit] = []
    seen: set[str] = set()
    for profile in profiles:
        hit = profile_to_raw_hit(profile, include_rejected=include_rejected)
        if hit is None or not hit.url or hit.url in seen:
            continue
        seen.add(hit.url)
        out.append(hit)
        if len(out) >= max(1, limit):
            break
    return out
