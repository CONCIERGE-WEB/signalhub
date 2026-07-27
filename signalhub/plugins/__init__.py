"""Plugin system — extend SignalHub without modifying Core."""
from __future__ import annotations

from signalhub.plugins.loader import LoadedPlugin, PluginLoadReport, PluginLoader, default_plugin_dirs
from signalhub.plugins.manifest import PluginManifest, load_manifest, validate_manifest

__all__ = [
    "LoadedPlugin",
    "PluginLoadReport",
    "PluginLoader",
    "PluginManifest",
    "default_plugin_dirs",
    "load_manifest",
    "validate_manifest",
]
