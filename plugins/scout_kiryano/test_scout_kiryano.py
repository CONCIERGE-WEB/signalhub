"""Unit tests — scout_kiryano quality + adapter (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGINS = Path(__file__).resolve().parents[2]
if str(PLUGINS) not in sys.path:
    sys.path.insert(0, str(PLUGINS))

from scout_kiryano.adapter import profile_to_raw_hit  # noqa: E402
from scout_kiryano.quality import evaluate, relevance_score  # noqa: E402


def test_reject_empty():
    gate = evaluate(None)
    assert gate["status"] == "rejected_empty"
    assert profile_to_raw_hit(None) is None


def test_reject_incomplete_no_contact():
    profile = {
        "username": "ghost",
        "full_name": "",
        "bio": "hi",
        "email": "",
        "phone": "",
        "website": "",
        "platform": "github",
        "profile_url": "https://github.com/ghost",
        "follower_count": 0,
    }
    gate = evaluate(profile)
    assert gate["status"] == "rejected_incomplete"
    assert gate["contact_ok"] is False
    assert profile_to_raw_hit(profile) is None


def test_accept_with_email_and_url():
    profile = {
        "username": "octocat",
        "full_name": "The Octocat",
        "bio": "GitHub mascot and public test profile for connectors.",
        "email": "octocat@github.com",
        "phone": "",
        "website": "https://github.blog",
        "platform": "github",
        "profile_url": "https://github.com/octocat",
        "follower_count": 5000,
    }
    gate = evaluate(profile)
    assert gate["status"] == "accepted"
    assert gate["contact_ok"] is True
    assert relevance_score(profile) >= 25
    hit = profile_to_raw_hit(profile)
    assert hit is not None
    assert hit.url == "https://github.com/octocat"
    assert hit.raw["email"] == "octocat@github.com"
    assert hit.provenance is not None
    assert hit.provenance.provider_id == "scout_kiryano"


def test_never_invent_email_in_adapter():
    profile = {
        "username": "x",
        "full_name": "X",
        "bio": "enough bio text here for a bit of relevance score bump xx",
        "email": "",
        "phone": "",
        "website": "https://example.org/about",
        "platform": "github",
        "profile_url": "https://github.com/x",
        "follower_count": 50,
    }
    hit = profile_to_raw_hit(profile)
    assert hit is not None
    assert hit.raw.get("email") == ""


def test_provider_idle_without_live(monkeypatch):
    from scout_kiryano.provider import ScoutKiryanoProvider
    from signalhub.core.contracts.provider import ProviderQuery

    monkeypatch.delenv("SIGNALHUB_SCOUT_KIRYANO_LIVE", raising=False)
    p = ScoutKiryanoProvider()
    hits = p.search(ProviderQuery(capability_id="discover_signals", terms=["octocat"]))
    assert hits == ()
