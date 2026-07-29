"""
Link-in-bio scraper — adapted from kiryano/Scout (MIT).
Copyright (c) 2026 Scout — see third_party/kiryano_scout/LICENSE
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from scout_kiryano.connectors.stealth import random_user_agent
from scout_kiryano.connectors.utils import extract_email

logger = logging.getLogger(__name__)

PLATFORMS = {
    "linktree": "https://linktr.ee/{username}",
    "stan": "https://stan.store/{username}",
    "linkr": "https://linkr.bio/{username}",
    "biolink": "https://bio.link/{username}",
}


def scrape_linktree(username: str) -> Optional[dict[str, Any]]:
    return _scrape_profile(username, "linktree")


def scrape_all(username: str) -> Optional[dict[str, Any]]:
    for platform in PLATFORMS:
        result = _scrape_profile(username, platform)
        if result:
            return result
    return None


def _scrape_profile(username: str, platform: str) -> Optional[dict[str, Any]]:
    try:
        import requests
    except ImportError:
        logger.error("requests not installed — pip install requests")
        return None

    username = username.lstrip("@").strip().lower()
    if platform not in PLATFORMS:
        return None
    url = PLATFORMS[platform].format(username=username)
    headers = {
        "User-Agent": random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 404:
            return None
        if r.status_code in (403, 429):
            logger.warning(
                "%s block/rate-limit HTTP %s for %s", platform, r.status_code, username
            )
            return None
        if r.status_code != 200:
            logger.warning("%s HTTP %s for %s", platform, r.status_code, username)
            return None
        if platform == "linktree":
            return _parse_linktree(r.text, username)
        if platform == "stan":
            return _parse_stan(r.text, username)
        return _parse_generic(r.text, username, platform)
    except requests.exceptions.Timeout:
        logger.warning("Timeout %s %s", platform, username)
        return None
    except requests.exceptions.RequestException as exc:
        logger.warning("%s request error %s: %s", platform, username, exc)
        return None


def _parse_linktree(html: str, username: str) -> Optional[dict[str, Any]]:
    data_match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not data_match:
        return _parse_generic(html, username, "linktree")
    try:
        data = json.loads(data_match.group(1))
        account = data.get("props", {}).get("pageProps", {}).get("account", {})
        if not account:
            return None
        links = []
        for link in account.get("links", []):
            if link.get("url"):
                links.append({"title": link.get("title", ""), "url": link.get("url", "")})
        bio = account.get("description", "") or ""
        return {
            "username": username,
            "full_name": account.get("pageTitle", "") or "",
            "bio": bio,
            "email": _email_from_links(links) or extract_email(bio),
            "phone": "",
            "follower_count": 0,
            "website": _website_from_links(links),
            "links": links,
            "socials": _socials_from_links(links),
            "platform": "linktree",
            "profile_url": f"https://linktr.ee/{username}",
        }
    except json.JSONDecodeError:
        return _parse_generic(html, username, "linktree")


def _parse_stan(html: str, username: str) -> Optional[dict[str, Any]]:
    links = []
    for url in re.findall(r'href="(https?://[^"]+)"', html):
        if "stan.store" not in url and url.startswith("http"):
            links.append({"title": "", "url": url})
    name_match = re.search(r'"name":"([^"]+)"', html)
    bio_match = re.search(r'"description":"([^"]*)"', html)
    full_name = name_match.group(1) if name_match else ""
    bio = bio_match.group(1) if bio_match else ""
    if not full_name and not links:
        return None
    return {
        "username": username,
        "full_name": full_name,
        "bio": bio,
        "email": _email_from_links(links) or extract_email(bio),
        "phone": "",
        "follower_count": 0,
        "website": _website_from_links(links),
        "links": links[:20],
        "socials": _socials_from_links(links),
        "platform": "stan",
        "profile_url": f"https://stan.store/{username}",
    }


def _parse_generic(
    html: str, username: str, platform: str
) -> Optional[dict[str, Any]]:
    links = []
    seen: set[str] = set()
    for url in re.findall(r'href="(https?://[^"]+)"', html):
        if url in seen:
            continue
        if any(skip in url for skip in ("favicon", "static", "assets", ".css", ".js")):
            continue
        links.append({"title": "", "url": url})
        seen.add(url)
    title_match = re.search(r"<title>([^<]+)</title>", html)
    full_name = title_match.group(1).strip() if title_match else ""
    bio = ""
    meta_desc = re.search(
        r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html
    )
    if meta_desc:
        bio = meta_desc.group(1)
    if not links:
        return None
    base_url = PLATFORMS.get(platform, "").format(username=username)
    return {
        "username": username,
        "full_name": full_name,
        "bio": bio,
        "email": _email_from_links(links) or extract_email(bio),
        "phone": "",
        "follower_count": 0,
        "website": _website_from_links(links),
        "links": links[:20],
        "socials": _socials_from_links(links),
        "platform": platform,
        "profile_url": base_url,
    }


def _socials_from_links(links: list[dict[str, str]]) -> dict[str, str]:
    socials: dict[str, str] = {}
    patterns = {
        "instagram": r"instagram\.com/([^/?]+)",
        "twitter": r"(?:twitter|x)\.com/([^/?]+)",
        "tiktok": r"tiktok\.com/@?([^/?]+)",
        "youtube": r"youtube\.com/(?:@|c/|channel/)?([^/?]+)",
        "github": r"github\.com/([^/?]+)",
        "linkedin": r"linkedin\.com/in/([^/?]+)",
    }
    for link in links:
        url = link.get("url", "")
        for platform, pattern in patterns.items():
            if platform not in socials:
                match = re.search(pattern, url, re.IGNORECASE)
                if match:
                    socials[platform] = match.group(1)
    return socials


def _website_from_links(links: list[dict[str, str]]) -> str:
    social_domains = (
        "instagram.com",
        "twitter.com",
        "x.com",
        "tiktok.com",
        "youtube.com",
        "github.com",
        "linkedin.com",
        "discord.gg",
        "discord.com",
        "spotify.com",
        "stan.store",
        "linktr.ee",
        "linkr.bio",
        "bio.link",
        "facebook.com",
    )
    for link in links:
        url = link.get("url", "")
        if url.startswith("http") and not url.startswith("mailto:"):
            if not any(d in url.lower() for d in social_domains):
                return url
    return ""


def _email_from_links(links: list[dict[str, str]]) -> str:
    for link in links:
        url = link.get("url", "")
        if url.startswith("mailto:"):
            return url.replace("mailto:", "").split("?")[0]
    return ""
