"""Plugin loader — discovers plugins without modifying Core."""
from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from signalhub.core.registry.container import ServiceContainer
from signalhub.plugins.manifest import PluginManifest, load_manifest, validate_manifest
from signalhub.sdk.adapter import NotificationAdapterPort
from signalhub.sdk.capability import CapabilityPlugin
from signalhub.sdk.consumer import SignalConsumer
from signalhub.sdk.provider import ProviderPlugin
from signalhub.sdk.ruleset import RulesetPlugin


@dataclass
class LoadedPlugin:
    manifest: PluginManifest
    providers: list[ProviderPlugin] = field(default_factory=list)
    capabilities: list[CapabilityPlugin] = field(default_factory=list)
    adapters: list[NotificationAdapterPort] = field(default_factory=list)
    consumers: list[SignalConsumer] = field(default_factory=list)
    rulesets: list[RulesetPlugin] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class PluginLoadReport:
    loaded: list[LoadedPlugin] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(p.ok for p in self.loaded)


def default_plugin_dirs() -> list[Path]:
    dirs: list[Path] = []
    env = (os.environ.get("SIGNALHUB_PLUGINS_DIR") or "").strip()
    if env:
        dirs.append(Path(env))
    # Repo convention
    here = Path(__file__).resolve()
    repo_plugins = here.parents[2] / "plugins"
    dirs.append(repo_plugins)
    # Package examples
    dirs.append(here.parent / "examples")
    # CWD ./plugins
    dirs.append(Path.cwd() / "plugins")
    # unique existing
    seen: set[str] = set()
    out: list[Path] = []
    for d in dirs:
        key = str(d.resolve()) if d.exists() else str(d)
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


class PluginLoader:
    def __init__(self, search_dirs: Sequence[Path] | None = None) -> None:
        self.search_dirs = list(search_dirs) if search_dirs is not None else default_plugin_dirs()

    def discover(self) -> list[Path]:
        found: list[Path] = []
        for root in self.search_dirs:
            if not root.is_dir():
                continue
            for child in sorted(root.iterdir()):
                if not child.is_dir():
                    continue
                if (child / "plugin.yaml").is_file() or (child / "plugin.json").is_file():
                    found.append(child)
        return found

    def load_all(self) -> PluginLoadReport:
        report = PluginLoadReport()
        for plugin_dir in self.discover():
            loaded = self.load_one(plugin_dir)
            report.loaded.append(loaded)
        return report

    def load_one(self, plugin_dir: Path) -> LoadedPlugin:
        try:
            manifest = load_manifest(plugin_dir)
        except Exception as exc:  # noqa: BLE001
            return LoadedPlugin(
                manifest=PluginManifest(name=plugin_dir.name, version="0"),
                errors=[f"manifest: {exc}"],
            )
        issues = validate_manifest(manifest)
        loaded = LoadedPlugin(manifest=manifest, errors=list(issues))
        if issues:
            return loaded

        # Make plugin dir importable
        parent = str(plugin_dir.parent.resolve())
        if parent not in sys.path:
            sys.path.insert(0, parent)
        pkg_path = str(plugin_dir.resolve())
        if pkg_path not in sys.path:
            sys.path.insert(0, pkg_path)

        for entry in manifest.providers:
            obj, err = _import_class(entry.module, entry.class_name)
            if err:
                loaded.errors.append(err)
                continue
            try:
                instance = obj() if isinstance(obj, type) else obj
                if not isinstance(instance, ProviderPlugin):
                    # duck-type: must have metadata/search
                    if not hasattr(instance, "metadata") or not hasattr(instance, "search"):
                        loaded.errors.append(f"provider inválido: {entry.module}.{entry.class_name}")
                        continue
                loaded.providers.append(instance)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                loaded.errors.append(f"provider init: {exc}")

        for entry in manifest.capabilities:
            obj, err = _import_class(entry.module, entry.class_name)
            if err:
                loaded.errors.append(err)
                continue
            try:
                # Capabilities that need orchestrator are factory(callables) — skip if needs args
                instance = obj() if isinstance(obj, type) else obj
                loaded.capabilities.append(instance)  # type: ignore[arg-type]
            except TypeError:
                loaded.errors.append(
                    f"capability {entry.class_name} requer DI — use factory no manifesto futuro"
                )
            except Exception as exc:  # noqa: BLE001
                loaded.errors.append(f"capability init: {exc}")

        for entry in manifest.adapters:
            obj, err = _import_class(entry.module, entry.class_name)
            if err:
                loaded.errors.append(err)
                continue
            try:
                instance = obj() if isinstance(obj, type) else obj
                loaded.adapters.append(instance)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                loaded.errors.append(f"adapter init: {exc}")

        for entry in manifest.consumers:
            obj, err = _import_class(entry.module, entry.class_name)
            if err:
                loaded.errors.append(err)
                continue
            try:
                instance = obj() if isinstance(obj, type) else obj
                loaded.consumers.append(instance)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                loaded.errors.append(f"consumer init: {exc}")

        for entry in manifest.rulesets:
            obj, err = _import_class(entry.module, entry.class_name)
            if err:
                loaded.errors.append(err)
                continue
            try:
                instance = obj() if isinstance(obj, type) else obj
                loaded.rulesets.append(instance)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                loaded.errors.append(f"ruleset init: {exc}")

        return loaded

    def apply_to_container(self, container: ServiceContainer, report: PluginLoadReport | None = None) -> PluginLoadReport:
        report = report or self.load_all()
        for plugin in report.loaded:
            if not plugin.ok:
                continue
            for provider in plugin.providers:
                pid = provider.metadata().provider_id
                try:
                    container.providers.register(provider, replace=True)
                except Exception as exc:  # noqa: BLE001
                    plugin.errors.append(f"register provider {pid}: {exc}")
            for cap in plugin.capabilities:
                try:
                    container.capabilities.register(cap, replace=True)
                except Exception as exc:  # noqa: BLE001
                    plugin.errors.append(f"register capability: {exc}")
        return report


def _import_class(module_name: str, class_name: str) -> tuple[Any, str | None]:
    if not module_name or not class_name:
        return None, "module/class vazios"
    try:
        mod = importlib.import_module(module_name)
        obj = getattr(mod, class_name)
        return obj, None
    except Exception as exc:  # noqa: BLE001
        return None, f"import {module_name}.{class_name}: {exc}"
