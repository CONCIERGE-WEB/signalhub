"""Dry-run / live scrape — Prospecção | Tiago A. Rocha (sem persistir no DB principal)."""

from __future__ import annotations

import logging
from typing import Any

from scout_kiryano.adapter import PRODUCT_NAME, profile_to_raw_hit
from scout_kiryano.connectors import SUPPORTED, scrape
from scout_kiryano.quality_gate import evaluate

logger = logging.getLogger(__name__)


def run_scrape(
    *,
    platform: str,
    target: str,
    dry_run: bool = True,
    include_rejected: bool = True,
) -> dict[str, Any]:
    """
    Scrape one target and return a preview report.

    dry_run=True (default): never persists — console/CLI preview only.
    Rate-limit / CAPTCHA / timeout → graceful empty + error field.
    """
    report: dict[str, Any] = {
        "ok": True,
        "product": PRODUCT_NAME,
        "dry_run": bool(dry_run),
        "persisted": False,
        "platform": platform,
        "target": target,
        "supported": list(SUPPORTED),
        "gate": None,
        "hit": None,
        "error": None,
    }
    if dry_run:
        report["note"] = (
            f"{PRODUCT_NAME} dry-run — preview only; nothing written to main DB"
        )

    try:
        profile = scrape(platform, target)
    except ValueError as exc:
        report["ok"] = False
        report["error"] = str(exc)
        return report
    except Exception as exc:  # noqa: BLE001 — keep queue/CLI alive
        logger.warning("%s scrape failed: %s", PRODUCT_NAME, exc)
        report["ok"] = False
        report["error"] = f"scrape_error:{exc}"
        return report

    if profile is None:
        report["ok"] = True
        report["error"] = "empty_or_blocked"
        report["gate"] = evaluate(None)
        return report

    gate = evaluate(profile)
    report["gate"] = {
        "status": gate["status"],
        "score": gate["score"],
        "contact_ok": gate["contact_ok"],
        "categoria_id": gate.get("categoria_id"),
        "categoria_label": gate.get("categoria_label"),
        "matched_keywords": gate.get("matched_keywords") or [],
        "reasons": gate["reasons"],
        "profile": gate["profile"],
    }
    hit = profile_to_raw_hit(profile, include_rejected=include_rejected)
    if hit is not None:
        report["hit"] = {
            "external_id": hit.external_id,
            "title": hit.title,
            "url": hit.url,
            "snippet": hit.snippet[:240],
            "source": hit.source,
            "category": hit.category,
            "raw": dict(hit.raw),
        }
    report["persisted"] = False
    return report
