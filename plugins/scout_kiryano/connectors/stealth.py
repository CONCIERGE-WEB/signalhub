"""
Stealth helpers — adapted from kiryano/Scout (MIT).
Copyright (c) 2026 Scout — see third_party/kiryano_scout/LICENSE

Simplified: optional SCOUT_PROXY / SCOUT_PROXY_FILE only.
No free-proxy dependency (avoids third-party noise in SignalHub).
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def random_delay(min_seconds: float = 1.5, max_seconds: float = 4.5) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))


def get_proxy() -> Optional[str]:
    proxy = os.environ.get("SCOUT_PROXY")
    if proxy:
        return proxy
    proxy_file = os.environ.get("SCOUT_PROXY_FILE")
    if proxy_file and os.path.exists(proxy_file):
        with open(proxy_file, encoding="utf-8") as f:
            proxies = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
        if proxies:
            return random.choice(proxies)
    return None


def get_requests_proxies() -> Optional[dict[str, str]]:
    proxy = get_proxy()
    if not proxy:
        return None
    if not proxy.startswith("http"):
        proxy = f"http://{proxy}"
    return {"http": proxy, "https": proxy}


def proxy_status() -> str:
    if os.environ.get("SCOUT_PROXY"):
        return "custom"
    if os.environ.get("SCOUT_PROXY_FILE"):
        return "file"
    return "none"


def retry_request(max_retries: int = 3, delay: float = 2.0) -> Callable:
    """Decorator to retry failed requests (timeout / connection / proxy)."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                import requests
            except ImportError:
                logger.error("requests not installed — pip install requests")
                return None
            last_error: Exception | None = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.ProxyError as e:
                    last_error = e
                    logger.warning("Proxy error (attempt %s/%s)", attempt + 1, max_retries)
                except requests.exceptions.Timeout as e:
                    last_error = e
                    logger.warning("Timeout (attempt %s/%s)", attempt + 1, max_retries)
                except requests.exceptions.ConnectionError as e:
                    last_error = e
                    logger.warning("Connection error (attempt %s/%s)", attempt + 1, max_retries)
                if attempt < max_retries - 1:
                    time.sleep(delay)
            logger.error("All %s attempts failed: %s", max_retries, last_error)
            return None

        return wrapper

    return decorator
