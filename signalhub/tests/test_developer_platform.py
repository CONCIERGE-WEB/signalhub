"""P2 Developer Platform tests."""
from __future__ import annotations

from pathlib import Path

from signalhub.bootstrap import build_container
from signalhub.plugins import PluginLoader, load_manifest, validate_manifest
from signalhub.sdk.devtools import contract_check, doctor, validate_plugin
from signalhub.sdk.scaffold import create_component


ROOT = Path(__file__).resolve().parents[2]
PLUGINS = ROOT / "plugins"


def test_example_rss_manifest():
    m = load_manifest(PLUGINS / "example_rss")
    assert m.name == "example_rss"
    assert validate_manifest(m) == []
    assert m.providers[0].class_name == "ExampleRssProvider"


def test_load_example_plugins():
    report = PluginLoader(search_dirs=[PLUGINS]).load_all()
    names = {p.manifest.name for p in report.loaded}
    assert "example_rss" in names
    assert "example_echo" in names
    assert "example_discord" in names
    assert "example_webhook" in names
    assert all(p.ok for p in report.loaded), [p.errors for p in report.loaded if not p.ok]


def test_bootstrap_registers_plugin_provider():
    c = build_container(load_plugins=True)
    # Plugin loader uses default dirs including repo plugins when cwd/path resolves
    report = PluginLoader(search_dirs=[PLUGINS]).apply_to_container(c)
    assert "example_rss" in c.providers.list_ids()
    assert any(cap.id == "example_echo" for cap in c.capabilities.list_capabilities())
    assert report.ok


def test_validate_plugin_rss():
    result = validate_plugin(PLUGINS / "example_rss")
    assert result["ok"], result["issues"]


def test_doctor_and_contract_check():
    # Ensure discovery sees repo plugins
    import os

    os.environ["SIGNALHUB_PLUGINS_DIR"] = str(PLUGINS)
    try:
        d = doctor()
        assert d["contract_version"] == "1.0.0"
        assert d["core_sample_signal_ok"]
        assert "signal-processing framework" in d["positioning"]
        cc = contract_check()
        assert cc["core_ok"]
        assert cc["ok"]
    finally:
        os.environ.pop("SIGNALHUB_PLUGINS_DIR", None)


def test_scaffold_provider(tmp_path: Path):
    path = create_component("provider", "tmp_src", root=tmp_path, author="test")
    assert (path / "plugin.yaml").is_file()
    assert (path / "provider.py").is_file()
    result = validate_plugin(path)
    assert result["ok"], result["issues"]
