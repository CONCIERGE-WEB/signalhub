"""Map scout_kiryano profile → RFC-0001 RawHit. Never invent fields."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from signalhub.core.contracts.provider import RawHit
from signalhub.core.models import Provenance

from scout_kiryano.quality_gate import evaluate

PROVIDER_ID = "scout_kiryano"
PRODUCT_NAME = "Prospecção | Tiago A. Rocha"


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
    # B2B / privacy / no category never become pipeline hits (even in include_rejected preview
    # for persistence — preview CLI may still show gate separately).
    if gate["status"] in ("rejected_b2b", "rejected_privacy") and not include_rejected:
        return None

    p = gate["profile"] or {}
    url = (p.get("profile_url") or "").strip() or None
    if not url:
        return None

    title = (p.get("full_name") or p.get("username") or url)[:200]
    bio = str(p.get("bio") or "")
    snippet = bio[:800] if bio else f"{p.get('platform', '')} @{p.get('username', '')}"
    platform = str(p.get("platform") or "websites")
    cat_id = gate.get("categoria_id")
    external_seed = f"{url}|{platform}|{p.get('username', '')}|{cat_id or ''}"
    external_id = hashlib.sha256(external_seed.encode("utf-8")).hexdigest()[:24]
    content_hash = hashlib.sha256(
        f"{title}\n{snippet}\n{url}\n{cat_id or ''}".encode("utf-8")
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
        "categoria_id": cat_id,
        "categoria_label": gate.get("categoria_label"),
        "matched_keywords": gate.get("matched_keywords") or [],
        "product": PRODUCT_NAME,
    }
    if isinstance(p.get("socials"), dict) and p["socials"]:
        raw["socials"] = p["socials"]

    return RawHit(
        external_id=external_id,
        title=str(title),
        url=url,
        snippet=snippet,
        signal_type="public_complaint" if cat_id else "public_profile",
        category=str(cat_id) if cat_id else "consumer",
        source=platform,
        raw=raw,
        provenance=Provenance(
            provider_id=provider_id,
            source_url=url,
            origin=platform,
            content_hash=content_hash,
            source_kind="public",
            extras={
                "collected_via": "prospeccao_tiago_a_rocha",
                "product": PRODUCT_NAME,
                "upstream": "kiryano/Scout",
                "license": "MIT",
                "quality_status": gate["status"],
                "quality_score": gate["score"],
                "categoria_id": cat_id,
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
        # Never persist B2B/privacy as accepted pipeline material.
        status = (hit.raw or {}).get("quality_status")
        if status in ("rejected_b2b", "rejected_privacy"):
            continue
        seen.add(hit.url)
        out.append(hit)
        if len(out) >= max(1, limit):
            break
    return out
