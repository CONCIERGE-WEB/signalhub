"""
GitHub profile scraper — adapted from kiryano/Scout (MIT).
Copyright (c) 2026 Scout — see third_party/kiryano_scout/LICENSE
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from scout_kiryano.connectors.stealth import get_requests_proxies, random_user_agent
from scout_kiryano.connectors.utils import extract_email

logger = logging.getLogger(__name__)


def scrape_profile(username: str) -> Optional[dict[str, Any]]:
    """Fetch public GitHub user profile via REST API. None on miss / rate-limit."""
    try:
        import requests
    except ImportError:
        logger.error("requests not installed — pip install requests")
        return None

    url = f"https://api.github.com/users/{username}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": random_user_agent(),
    }
    token = (__import__("os").environ.get("GITHUB_TOKEN") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.get(
            url, headers=headers, timeout=15, proxies=get_requests_proxies()
        )
        if r.status_code == 404:
            logger.info("GitHub user @%s not found", username)
            return None
        if r.status_code == 403 or r.status_code == 429:
            logger.warning(
                "GitHub rate-limit/block HTTP %s for @%s — skipping",
                r.status_code,
                username,
            )
            return None
        if r.status_code != 200:
            logger.warning("GitHub HTTP %s for @%s", r.status_code, username)
            return None

        data = r.json()
        bio = data.get("bio") or ""
        if not any(
            [
                data.get("name"),
                data.get("bio"),
                data.get("email"),
                data.get("blog"),
                data.get("company"),
                data.get("twitter_username"),
            ]
        ):
            logger.info("GitHub @%s has no public profile fields", username)
            return None

        return {
            "username": data.get("login", username),
            "full_name": data.get("name") or "",
            "bio": bio,
            "email": data.get("email") or extract_email(bio),
            "phone": "",
            "company": (data.get("company") or "").lstrip("@"),
            "location": data.get("location") or "",
            "website": data.get("blog") or "",
            "twitter": data.get("twitter_username") or "",
            "follower_count": int(data.get("followers") or 0),
            "following_count": int(data.get("following") or 0),
            "public_repos": int(data.get("public_repos") or 0),
            "is_hireable": bool(data.get("hireable") or False),
            "platform": "github",
            "profile_url": data.get("html_url", f"https://github.com/{username}"),
        }
    except requests.exceptions.Timeout:
        logger.warning("Timeout GitHub @%s", username)
        return None
    except requests.exceptions.RequestException as exc:
        logger.warning("GitHub request error @%s: %s", username, exc)
        return None
