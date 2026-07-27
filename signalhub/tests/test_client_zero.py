"""Cliente Zero — Scout + Dorking as SDK plugins (no Core backdoor)."""
from __future__ import annotations

from pathlib import Path

from signalhub.bootstrap import build_container
from signalhub.plugins import PluginLoader
from signalhub.sdk.devtools import validate_plugin


ROOT = Path(__file__).resolve().parents[2]
PLUGINS = ROOT / "plugins"
SCOUT_PLUGIN = PLUGINS / "scout_signals"
DORK_PLUGIN = PLUGINS / "dork_signals"


def test_scout_plugin_validates():
    report = validate_plugin(SCOUT_PLUGIN)
    assert report["ok"], report["issues"]
    assert report["plugin"] == "scout_signals"


def test_dork_plugin_validates():
    report = validate_plugin(DORK_PLUGIN)
    assert report["ok"], report["issues"]
    assert report["plugin"] == "dork_signals"


def test_scout_and_dork_from_plugins_not_builtins():
    c = build_container(load_plugins=False)
    assert "scout" not in c.providers.list_ids()
    assert "dorking" not in c.providers.list_ids()

    PluginLoader(search_dirs=[PLUGINS]).apply_to_container(c)
    assert "scout" in c.providers.list_ids()
    assert "dorking" in c.providers.list_ids()
    dork_desc = c.providers.get("dorking").metadata().description
    assert "plugin" in dork_desc.lower() or "Cliente Zero" in dork_desc


def test_core_scout_import_blocked():
    try:
        from signalhub.providers.scout.provider import ScoutProvider

        ScoutProvider()
        assert False, "deveria falhar"
    except ImportError as exc:
        assert "scout_signals" in str(exc) or "Cliente Zero" in str(exc)


def test_core_dorking_import_blocked():
    try:
        from signalhub.providers.dorking.provider import DorkingProvider

        DorkingProvider()
        assert False, "deveria falhar"
    except ImportError as exc:
        assert "dork_signals" in str(exc) or "Cliente Zero" in str(exc)
