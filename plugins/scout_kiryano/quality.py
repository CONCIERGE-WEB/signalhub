"""
Quality gate for scout_kiryano profiles.

BrandBook / SignalHub: never invent contact fields.
Reject incomplete leads that lack minimum contact or relevance.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)
_EMAIL_BLACKLIST = (
    "example.com",
    "test.com",
    "email.com",
    "youremail.com",
    "sentry.io",
    "noreply",
    "no-reply",
)


def _valid_email(value: str) -> bool:
    email = (value or "").strip().lower()
    if not email or not _EMAIL_RE.match(email):
        return False
    return not any(b in email for b in _EMAIL_BLACKLIST)


def _valid_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value or "")
    return len(digits) >= 10


def relevance_score(profile: Mapping[str, Any]) -> int:
    """0–100 from real public fields only. Never invents missing data."""
    score = 0
    if (profile.get("profile_url") or "").strip():
        score += 20
    if (profile.get("full_name") or "").strip():
        score += 10
    bio = (profile.get("bio") or "").strip()
    if len(bio) >= 20:
        score += 15
    elif bio:
        score += 5
    if _valid_email(str(profile.get("email") or "")):
        score += 30
    if _valid_phone(str(profile.get("phone") or "")):
        score += 20
    website = (profile.get("website") or "").strip()
    if website.startswith("http"):
        score += 15
    followers = int(profile.get("follower_count") or 0)
    if followers >= 1000:
        score += 10
    elif followers >= 100:
        score += 5
    socials = profile.get("socials") or {}
    if isinstance(socials, dict) and socials:
        score += min(10, 2 * len(socials))
    return min(100, score)


def evaluate(profile: Mapping[str, Any] | None) -> dict[str, Any]:
    """
    Return gate result:
      status: accepted | rejected_incomplete | rejected_empty
      score, reasons, contact_ok
    """
    if not profile:
        return {
            "status": "rejected_empty",
            "score": 0,
            "contact_ok": False,
            "reasons": ["no_profile"],
            "profile": None,
        }

    email = str(profile.get("email") or "").strip()
    phone = str(profile.get("phone") or "").strip()
    website = str(profile.get("website") or "").strip()
    url = str(profile.get("profile_url") or "").strip()

    contact_ok = (
        _valid_email(email)
        or _valid_phone(phone)
        or (website.startswith("http") and len(website) > 8)
    )
    score = relevance_score(profile)
    reasons: list[str] = []

    if not url:
        reasons.append("missing_profile_url")
    if not contact_ok:
        reasons.append("missing_valid_contact")
    if score < 25:
        reasons.append("low_relevance_score")

    # Accept if contact OK and score decent, OR strong public profile (url+bio+score).
    accepted = contact_ok and score >= 25 and bool(url)
    if not accepted and contact_ok is False and score >= 40 and url and (
        profile.get("full_name") or bio_ok(profile)
    ):
        # Public handle with substance but no email — still incomplete for lead CRM.
        reasons.append("public_profile_without_contact")
        status = "rejected_incomplete"
    elif accepted:
        status = "accepted"
        reasons = ["ok"]
    else:
        status = "rejected_incomplete"

    return {
        "status": status,
        "score": score,
        "contact_ok": contact_ok,
        "reasons": reasons,
        "profile": dict(profile),
    }


def bio_ok(profile: Mapping[str, Any]) -> bool:
    return len(str(profile.get("bio") or "").strip()) >= 20
