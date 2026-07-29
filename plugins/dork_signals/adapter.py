"""Map engine DorkScanner posts → RFC-0001 RawHit (Signal only — never Lead)."""
from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping
from urllib.parse import urlparse

from signalhub.core.contracts.provider import RawHit
from signalhub.core.models import Provenance

PROVIDER_ID = "dorking"

# Infer origin channel from URL / engine tags (reuse existing dork surface coverage).
_ORIGIN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("reddit", re.compile(r"reddit\.com", re.I)),
    ("reclame_aqui", re.compile(r"reclameaqui\.com", re.I)),
    ("tiktok", re.compile(r"tiktok\.com", re.I)),
    ("instagram", re.compile(r"instagram\.com", re.I)),
    ("facebook", re.compile(r"facebook\.com|fb\.com", re.I)),
    ("youtube", re.compile(r"youtube\.com|youtu\.be", re.I)),
    ("github", re.compile(r"github\.com", re.I)),
    ("twitter", re.compile(r"twitter\.com|x\.com", re.I)),
    ("hackernews", re.compile(r"news\.ycombinator\.com", re.I)),
)


def infer_origin(post: Mapping[str, Any]) -> str:
    canal = str(post.get("canal") or "").strip()
    if canal:
        return canal
    fonte = str(post.get("fonte") or "")
    if fonte.startswith("reddit:"):
        return "reddit"
    if fonte.startswith("varredura:"):
        url = str(post.get("link") or post.get("url") or "")
        for name, pat in _ORIGIN_PATTERNS:
            if pat.search(url):
                return name
        return "websites"
    if "hackernews" in fonte.lower() or "hn" in fonte.lower():
        return "hackernews"
    url = str(post.get("link") or post.get("url") or "")
    for name, pat in _ORIGIN_PATTERNS:
        if pat.search(url):
            return name
    host = urlparse(url).netloc.lower()
    return host or "websites"


def post_to_raw_hit(post: Mapping[str, Any], *, provider_id: str = PROVIDER_ID) -> RawHit | None:
    """Convert one engine post dict to RawHit. Skip if no public URL."""
    url = (post.get("link") or post.get("url") or "").strip() or None
    if not url:
        return None
    texto = str(post.get("texto") or post.get("title") or post.get("body") or "").strip()
    title = texto.split("\n", 1)[0][:200] if texto else url
    snippet = texto[:800]
    origin = infer_origin(post)
    dork_id = post.get("dork_id") or ""
    external_seed = f"{url}|{dork_id}|{post.get('autor', '')}"
    external_id = hashlib.sha256(external_seed.encode("utf-8")).hexdigest()[:24]
    content_hash = hashlib.sha256(f"{title}\n{snippet}\n{url}".encode("utf-8")).hexdigest()
    category = post.get("grupo") or post.get("grupo_hint") or post.get("category")
    if category is not None:
        category = str(category)
        # Engine grupos are not always RFC known categories — keep in raw; Signal uses safe bucket.
        signal_category = "consumer" if category else None
    else:
        signal_category = None
    raw = {
        k: v
        for k, v in dict(post).items()
        if k
        in (
            "autor",
            "fonte",
            "dork_id",
            "canal",
            "grupo",
            "grupo_hint",
            "tenant",
        )
    }
    if category:
        raw["engine_grupo"] = category
    return RawHit(
        external_id=external_id,
        title=title,
        url=url,
        snippet=snippet,
        signal_type="public_complaint",
        category=signal_category,
        source=origin,
        raw=raw,
        provenance=Provenance(
            provider_id=provider_id,
            source_url=url,
            origin=origin,
            content_hash=content_hash,
            source_kind="public",
            extras={
                "collected_via": "discovery_engine_dorking",
                "engine_fonte": post.get("fonte"),
            },
        ),
    )


def posts_to_raw_hits(
    posts: list[Mapping[str, Any]],
    *,
    limit: int = 40,
    provider_id: str = PROVIDER_ID,
) -> list[RawHit]:
    out: list[RawHit] = []
    seen: set[str] = set()
    for post in posts:
        hit = post_to_raw_hit(post, provider_id=provider_id)
        if hit is None or not hit.url or hit.url in seen:
            continue
        seen.add(hit.url)
        out.append(hit)
        if len(out) >= max(1, limit):
            break
    return out
