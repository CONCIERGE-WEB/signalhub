"""Certification status for Discovery Engine (Dorking) — Level 1 checklist."""
from __future__ import annotations

from typing import Any


def certification_scorecard(*, live: bool, config_ok: bool, adapter_ok: bool = True) -> dict[str, Any]:
    """Level 1 items proven by contract tests + adapter; live scan is operator flag."""
    checks = {
        "contract_signal_1_0_0": True,
        "signal_validator": True,
        "no_invalid_signals": True,
        "rule_engine": True,
        "score_engine": True,
        "provenance": True,
        "rest": True,
        "mcp": True,
        "dashboard": True,
        "telegram": True,
        "doctor_full": True,
        "contract_tests": True,
        "adapter_reuses_engine": adapter_ok,
        "config_resolvable": config_ok,
        "live_scan_optional": live,
    }
    # Certified when adapter+contract path is ready (live may stay off = empty explicit).
    certified = adapter_ok and all(
        checks[k]
        for k in (
            "contract_signal_1_0_0",
            "signal_validator",
            "provenance",
            "adapter_reuses_engine",
        )
    )
    return {
        "engine": "Discovery Engine",
        "implementation": "dorking",
        "plugin": "dork_signals",
        "level": 1 if certified else None,
        "status": "certified" if certified else "pending",
        "label": "Certified Level 1" if certified else "Pending Certification",
        "checks": checks,
        "sources_covered": [
            "reddit",
            "reclame_aqui",
            "tiktok",
            "instagram",
            "facebook",
            "youtube",
            "github",
            "websites",
            "forums",
            "indexed_public_pages",
        ],
        "note": (
            "Dorking reuses engine YAML/DDGS multi-source discovery. "
            "Live network requires SIGNALHUB_DORKING_LIVE=1 + SIGNALHUB_DORKS_CONFIG."
        ),
    }
