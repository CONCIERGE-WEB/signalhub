"""P2 platform hardening — stability, doctor --full, version negotiation."""
from __future__ import annotations

import os
from pathlib import Path

from signalhub.bootstrap import build_container
from signalhub.plugins.loader import PluginLoader
from signalhub.plugins.version_negotiation import (
    negotiate_plugin_versions,
    satisfies_constraint,
)
from signalhub.sdk.devtools import contract_check, doctor


ROOT = Path(__file__).resolve().parents[2]
PLUGINS = ROOT / "plugins"


def test_semver_constraints():
    assert satisfies_constraint("0.4.0", ">=0.3.0")
    assert not satisfies_constraint("0.2.0", ">=0.3.0")
    assert satisfies_constraint("0.4.0", "==0.4.0")
    assert not satisfies_constraint("0.4.1", "==0.4.0")


def test_negotiate_refuses_incompatible_core():
    issues = negotiate_plugin_versions(
        signalhub_version=">=99.0.0",
        contract_version="1.0.0",
        core_version="0.4.0",
    )
    assert issues
    assert "não carregado" in issues[0]


def test_negotiate_refuses_contract_major_mismatch():
    issues = negotiate_plugin_versions(
        signalhub_version=">=0.1.0",
        contract_version="2.0.0",
        core_version="0.4.0",
        core_contract="1.0.0",
    )
    assert issues


def test_loader_skips_incompatible_plugin(tmp_path: Path):
    plugin = tmp_path / "bad_plugin"
    plugin.mkdir()
    (plugin / "plugin.yaml").write_text(
        "\n".join(
            [
                "name: bad_plugin",
                "version: 0.0.1",
                'signalhub_version: ">=99.0.0"',
                'contract_version: "1.0.0"',
                "permissions:",
                "  - none",
                "providers:",
                "  - module: missing.mod",
                "    class: Missing",
            ]
        ),
        encoding="utf-8",
    )
    loaded = PluginLoader(search_dirs=[tmp_path]).load_one(plugin)
    assert not loaded.ok
    assert loaded.providers == []
    assert any("version negotiation" in e for e in loaded.errors)


def test_doctor_full_and_contract_suite():
    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        d = doctor(full=True)
        assert d["full"] is True
        assert d["contract_version"] == "1.0.0"
        assert "health" in d
        assert "contracts" in d
        assert "surfaces" in d
        assert d["surfaces"]["mcp"] is True
        assert d["surfaces"]["rest"] is True
        assert d["ok"], d
        cc = contract_check()
        assert cc["ok"], cc
        assert "suite" in cc
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)


def test_admin_snapshot_integrity_and_explorer():
    from signalhub.admin_snapshot import build_admin_snapshot

    snap = build_admin_snapshot(build_container(load_plugins=True))
    assert "integrity" in snap
    assert "capability_explorer" in snap
    assert snap["feature_flags"].get("p2_platform_hardening") is True
    assert isinstance(snap["capability_explorer"], list)
    assert snap["capability_explorer"]
    first = snap["capability_explorer"][0]
    assert "rest_example" in first
    assert "mcp_example" in first
    assert "python_example" in first
