"""Bridge to legacy engine DorkScanner — reuse queries/YAML; no Core change."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any


def resolve_dorks_config() -> Path | None:
    """Operator config first; never invent dork lists."""
    env = (os.environ.get("SIGNALHUB_DORKS_CONFIG") or "").strip()
    if env:
        p = Path(env)
        return p if p.is_file() else None
    # Prefer local (gitignored) then example for dry certification paths.
    root = Path(__file__).resolve().parents[2]
    candidates = [
        root / "engine" / "config" / "lex" / "dorks.yaml",
        root / "engine" / "config" / "portugal" / "dorks.yaml",
        root / "engine" / "config" / "zairyx" / "dorks.yaml",
        root / "engine" / "config" / "portugal" / "dorks.yaml.example",
        root / "engine" / "config" / "lex" / "dorks.yaml.example",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def live_enabled() -> bool:
    return (os.environ.get("SIGNALHUB_DORKING_LIVE") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _ensure_engine_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    engine = root / "engine"
    eng_s = str(engine)
    if eng_s not in sys.path:
        sys.path.insert(0, eng_s)
    return engine


async def scan_async(*, offset: int = 0, limite: int | None = None) -> list[dict[str, Any]]:
    cfg = resolve_dorks_config()
    if cfg is None:
        return []
    _ensure_engine_path()
    from core.sources.scanner import DorkScanner  # type: ignore[import-not-found]

    scanner = DorkScanner(cfg)
    return await scanner.scan(offset=offset, limite=limite)


def scan_sync(*, offset: int = 0, limite: int | None = None) -> list[dict[str, Any]]:
    """Sync wrapper for Provider.search (capabilities are sync)."""
    return asyncio.run(scan_async(offset=offset, limite=limite))
