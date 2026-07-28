"""Vercel Python serverless entry (fallback path `api/index.py`)."""

from signalhub.apps.api.http_dispatch import app

__all__ = ["app"]
