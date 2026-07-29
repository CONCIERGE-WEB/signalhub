"""
Shared scraper utilities — adapted from kiryano/Scout (MIT).
Copyright (c) 2026 Scout — see third_party/kiryano_scout/LICENSE
"""

from __future__ import annotations

import re


def extract_email(text: str) -> str:
    """Extract first email address from text. Empty string if none."""
    if not text:
        return ""
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_phone(text: str) -> str:
    """Extract first phone number (10+ digits) from text."""
    if not text:
        return ""
    patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            phone = re.sub(r"[^\d+]", "", matches[0])
            if len(phone) >= 10:
                return phone
    return ""


def parse_abbreviated_number(s: str) -> int:
    """Parse abbreviated numbers like 11M, 7.5K, 1.2B into integers."""
    s = (s or "").strip().replace(",", "")
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if s.upper().endswith(suffix):
            try:
                return int(float(s[:-1]) * mult)
            except (ValueError, IndexError):
                return 0
    try:
        return int(float(s))
    except ValueError:
        return 0
