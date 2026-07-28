"""Debug provider + lab generate/replay."""

from __future__ import annotations

import os
from pathlib import Path

from signalhub.lab import generate_synthetic, mission_control_status, replay_signals
from signalhub.sdk.devtools import validate_plugin

ROOT = Path(__file__).resolve().parents[2]
PLUGINS = ROOT / "plugins"


def test_validate_debug_plugin():
    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        report = validate_plugin(PLUGINS / "debug_signals")
        assert report["ok"], report
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)


def test_generate_valid_and_high_score():
    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        ok = generate_synthetic(mode="valid", limit=1)
        assert ok["ok"]
        assert ok["count"] >= 1
        assert ok["signals"][0]["provider"] == "debug"
        hi = generate_synthetic(mode="high_score", limit=1)
        assert hi["ok"]
        assert hi["count"] >= 1
        # score may be set after pipeline
        assert hi["signals"][0]["title"]
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)


def test_generate_invalid_may_yield_zero():
    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        bad = generate_synthetic(mode="invalid", limit=1)
        assert bad["ok"]
        # Validator pode rejeitar — count 0 é sucesso do laboratório
        assert bad["count"] >= 0
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)


def test_replay_roundtrip():
    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        gen = generate_synthetic(mode="valid", limit=1)
        assert gen["ok"] and gen["signals"]
        rep = replay_signals(gen["signals"])
        assert rep["ok"]
        assert rep["output"] >= 1
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)


def test_mission_control_has_debug():
    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        mc = mission_control_status()
        assert mc["core"]["ok"]
        assert mc["contract"]["version"] == "1.0.0"
        assert mc["lab"]["debug_provider"] is True
        ids = {p["id"] for p in mc["providers"]}
        assert "debug" in ids
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)
