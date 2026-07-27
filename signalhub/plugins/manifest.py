"""Plugin manifest (plugin.yaml / plugin.json) — RFC-compatible extensions."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(slots=True, frozen=True)
class PluginEntry:
    module: str
    class_name: str


@dataclass(slots=True, frozen=True)
class PluginManifest:
    name: str
    version: str
    author: str = ""
    description: str = ""
    signalhub_version: str = ">=0.2.0"
    permissions: Sequence[str] = ()
    providers: Sequence[PluginEntry] = ()
    capabilities: Sequence[PluginEntry] = ()
    adapters: Sequence[PluginEntry] = ()
    consumers: Sequence[PluginEntry] = ()
    rulesets: Sequence[PluginEntry] = ()
    path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        def ents(items: Sequence[PluginEntry]) -> list[dict[str, str]]:
            return [{"module": e.module, "class": e.class_name} for e in items]

        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "signalhub_version": self.signalhub_version,
            "permissions": list(self.permissions),
            "providers": ents(self.providers),
            "capabilities": ents(self.capabilities),
            "adapters": ents(self.adapters),
            "consumers": ents(self.consumers),
            "rulesets": ents(self.rulesets),
        }


def load_manifest(plugin_dir: Path) -> PluginManifest:
    yaml_path = plugin_dir / "plugin.yaml"
    json_path = plugin_dir / "plugin.json"
    if yaml_path.is_file():
        raw = _parse_simple_yaml(yaml_path.read_text(encoding="utf-8"))
    elif json_path.is_file():
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    else:
        raise FileNotFoundError(f"plugin.yaml/json ausente em {plugin_dir}")
    return _from_mapping(raw, path=plugin_dir)


def validate_manifest(manifest: PluginManifest) -> list[str]:
    issues: list[str] = []
    if not manifest.name or not re.match(r"^[a-z0-9][a-z0-9_\-]*$", manifest.name):
        issues.append("name inválido (use snake/kebab lowercase)")
    if not manifest.version:
        issues.append("version obrigatória")
    if not any(
        [
            manifest.providers,
            manifest.capabilities,
            manifest.adapters,
            manifest.consumers,
            manifest.rulesets,
        ]
    ):
        issues.append("plugin sem providers/capabilities/adapters/consumers/rulesets")
    allowed_perm = {"network", "filesystem", "notify", "storage", "none"}
    for p in manifest.permissions:
        if p not in allowed_perm:
            issues.append(f"permission desconhecida: {p}")
    return issues


def _from_mapping(raw: Mapping[str, Any], *, path: Path | None) -> PluginManifest:
    def entries(key: str) -> tuple[PluginEntry, ...]:
        items = raw.get(key) or []
        out: list[PluginEntry] = []
        for item in items:
            if isinstance(item, str):
                mod, _, cls = item.partition(":")
                out.append(PluginEntry(module=mod, class_name=cls or mod.split(".")[-1]))
            else:
                out.append(
                    PluginEntry(
                        module=str(item.get("module") or ""),
                        class_name=str(item.get("class") or item.get("class_name") or ""),
                    )
                )
        return tuple(out)

    return PluginManifest(
        name=str(raw.get("name") or ""),
        version=str(raw.get("version") or ""),
        author=str(raw.get("author") or ""),
        description=str(raw.get("description") or ""),
        signalhub_version=str(raw.get("signalhub_version") or ">=0.2.0"),
        permissions=tuple(raw.get("permissions") or ()),
        providers=entries("providers"),
        capabilities=entries("capabilities"),
        adapters=entries("adapters"),
        consumers=entries("consumers"),
        rulesets=entries("rulesets"),
        path=path,
    )


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Minimal YAML subset for plugin manifests (no full YAML dependency)."""
    root: dict[str, Any] = {}
    current_list: str | None = None
    current_list_item: dict[str, str] | None = None

    def flush_item() -> None:
        nonlocal current_list_item
        if current_list and current_list_item is not None:
            root.setdefault(current_list, []).append(current_list_item)
            current_list_item = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        # list item under a key
        if re.match(r"^  - ", raw_line) or re.match(r"^\t- ", raw_line):
            flush_item()
            rest = raw_line.strip()[1:].strip()
            if ":" in rest and not rest.startswith("{"):
                # inline "module: x" style start of mapping item
                k, _, v = rest.partition(":")
                current_list_item = {k.strip(): v.strip().strip('"').strip("'")}
            else:
                root.setdefault(current_list or "_", []).append(rest.strip('"').strip("'"))
            continue
        if re.match(r"^    \w", raw_line) and current_list:
            # nested field of list mapping
            if current_list_item is None:
                current_list_item = {}
            k, _, v = raw_line.strip().partition(":")
            current_list_item[k.strip()] = v.strip().strip('"').strip("'")
            continue
        flush_item()
        if ":" not in raw_line:
            continue
        key, _, val = raw_line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            current_list = key
            root[key] = []
            continue
        current_list = None
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            root[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
        else:
            root[key] = val.strip('"').strip("'")
    flush_item()
    return root
