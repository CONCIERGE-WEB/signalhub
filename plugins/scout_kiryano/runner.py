"""Dry-run / live scrape orchestration — no main-DB persistence."""

from __future__ import annotations

import logging
from typing import Any

from scout_kiryano.adapter import profile_to_raw_hit
from scout_kiryano.connectors import SUPPORTED, scrape
from scout_kiryano.quality import evaluate

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
        # Explicit: dry-run never writes to SignalHub main storage.
        report["note"] = "dry-run — preview only; nothing written to main DB"

    try:
        profile = scrape(platform, target)
    except ValueError as exc:
        report["ok"] = False
        report["error"] = str(exc)
        return report
    except Exception as exc:  # noqa: BLE001 — keep queue/CLI alive
        logger.warning("scout_kiryano scrape failed: %s", exc)
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
            "raw": dict(hit.raw),
        }
    # Persistence intentionally omitted in dry-run and in v0.1 live path
    # (operator must wire storage separately — no silent DB write).
    report["persisted"] = False
    return report
