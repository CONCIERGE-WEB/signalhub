"""
YouTube channel scraper — adapted from kiryano/Scout (MIT).
Copyright (c) 2026 Scout — see third_party/kiryano_scout/LICENSE
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional
from urllib.parse import unquote

from scout_kiryano.connectors.stealth import get_requests_proxies, random_user_agent
from scout_kiryano.connectors.utils import extract_email, parse_abbreviated_number

logger = logging.getLogger(__name__)


def scrape_channel(channel_identifier: str) -> Optional[dict[str, Any]]:
    """Fetch public YouTube channel page. None on miss / block."""
    try:
        import requests
    except ImportError:
        logger.error("requests not installed — pip install requests")
        return None

    if channel_identifier.startswith("@"):
        url = f"https://www.youtube.com/{channel_identifier}"
    elif channel_identifier.startswith("UC") and len(channel_identifier) == 24:
        url = f"https://www.youtube.com/channel/{channel_identifier}"
    else:
        url = f"https://www.youtube.com/@{channel_identifier}"

    headers = {
        "User-Agent": random_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    }
    cookies = {"CONSENT": "PENDING+999"}

    try:
        r = requests.get(
            url,
            headers=headers,
            cookies=cookies,
            timeout=20,
            proxies=get_requests_proxies(),
        )
        if r.status_code == 404:
            logger.info("YouTube channel %s not found", channel_identifier)
            return None
        if r.status_code in (403, 429):
            logger.warning(
                "YouTube block/rate-limit HTTP %s for %s",
                r.status_code,
                channel_identifier,
            )
            return None
        if r.status_code != 200:
            logger.warning("YouTube HTTP %s for %s", r.status_code, channel_identifier)
            return None
        result = _extract_channel_data(r.text, channel_identifier)
        return result
    except requests.exceptions.Timeout:
        logger.warning("Timeout YouTube %s", channel_identifier)
        return None
    except requests.exceptions.RequestException as exc:
        logger.warning("YouTube request error %s: %s", channel_identifier, exc)
        return None


def _extract_channel_data(html: str, identifier: str) -> Optional[dict[str, Any]]:
    results: dict[str, Any] = {}

    name_match = re.search(r'"channelMetadataRenderer":\{"title":"([^"]+)"', html)
    if name_match:
        results["channel_name"] = name_match.group(1)

    desc_match = re.search(r'"description":"([^"]*)"', html)
    if desc_match:
        try:
            results["description"] = (
                desc_match.group(1).encode("utf-8").decode("unicode_escape")
            )
        except (UnicodeDecodeError, UnicodeEncodeError):
            results["description"] = desc_match.group(1)

    for pattern in (
        r'"subscriberCountText":\{"simpleText":"([\d.,]+[KMB]?) subscribers?"',
        r'"subscriberCountText":\{"accessibility":\{"accessibilityData":\{"label":"([\d.,]+[KMB]?) subscribers?"',
    ):
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            results["subscriber_count"] = parse_abbreviated_number(match.group(1))
            break

    handle_match = re.search(
        r'"canonicalChannelUrl":"https://www\.youtube\.com/@([^"]+)"', html
    )
    if handle_match:
        results["handle"] = handle_match.group(1)

    channel_id_match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]{22})"', html)
    if channel_id_match:
        results["channel_id"] = channel_id_match.group(1)

    email_match = re.search(r'"businessEmailLabel":\{"content":"([^"]+)"', html)
    if email_match:
        results["business_email"] = email_match.group(1)
    else:
        results["business_email"] = extract_email(results.get("description", ""))

    links: list[str] = []
    for match in re.finditer(r'"urlEndpoint":\{"url":"(https?://[^"]+)"', html):
        link = match.group(1)
        if "youtube.com" not in link and "google.com" not in link:
            clean = _clean_redirect_url(link)
            if clean and clean not in links:
                links.append(clean)
    results["links"] = links[:5]

    if "channel_name" not in results:
        return None

    handle = results.get("handle", identifier.lstrip("@"))
    return {
        "username": handle,
        "full_name": results.get("channel_name", ""),
        "bio": results.get("description", ""),
        "email": results.get("business_email", "") or "",
        "phone": "",
        "follower_count": int(results.get("subscriber_count") or 0),
        "website": links[0] if links else "",
        "links": links,
        "channel_id": results.get("channel_id", ""),
        "platform": "youtube",
        "profile_url": f"https://www.youtube.com/@{handle}",
    }


def _clean_redirect_url(url: str) -> str:
    if "youtube.com/redirect" in url:
        q_match = re.search(r"[?&]q=([^&]+)", url)
        if q_match:
            return unquote(q_match.group(1))
    return url
