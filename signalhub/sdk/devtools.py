"""Developer tooling — validate plugins, doctor, contract-check."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from signalhub import __version__
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION
from signalhub.plugins.loader import PluginLoader
from signalhub.plugins.manifest import load_manifest, validate_manifest
from signalhub.sdk.testing import contract_check_provider, make_sample_signal, contract_check_signal
from signalhub.validation import SignalValidator


def validate_plugin(plugin_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(plugin_dir)
    issues = validate_manifest(manifest)
    loaded = PluginLoader(search_dirs=[]).load_one(plugin_dir)
    issues.extend(loaded.errors)
    provider_reports = []
    for provider in loaded.providers:
        provider_reports.append(contract_check_provider(provider))
        if not provider_reports[-1]["ok"]:
            issues.extend(provider_reports[-1]["issues"])
    return {
        "plugin": manifest.name,
        "path": str(plugin_dir),
        "ok": not issues,
        "issues": issues,
        "providers": provider_reports,
        "contract_version": SIGNAL_CONTRACT_VERSION,
    }


def doctor() -> dict[str, Any]:
    sample_issues = contract_check_signal(make_sample_signal())
    loader = PluginLoader()
    report = loader.load_all()
    plugins = []
    for p in report.loaded:
        plugins.append(
            {
                "name": p.manifest.name,
                "version": p.manifest.version,
                "ok": p.ok,
                "errors": p.errors,
                "providers": len(p.providers),
                "capabilities": len(p.capabilities),
                "adapters": len(p.adapters),
                "consumers": len(p.consumers),
            }
        )
    return {
        "signalhub_version": __version__,
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "core_sample_signal_ok": not sample_issues,
        "core_sample_issues": sample_issues,
        "plugin_dirs": [str(d) for d in loader.search_dirs],
        "plugins": plugins,
        "ok": not sample_issues and all(p["ok"] for p in plugins if plugins),
        "positioning": (
            "SignalHub is a signal-processing framework. "
            "Source integrations are independent plugins under each platform's ToS."
        ),
    }


def contract_check() -> dict[str, Any]:
    validator = SignalValidator()
    sample = make_sample_signal()
    result = validator.validate(sample)
    loader = PluginLoader()
    report = loader.load_all()
    provider_checks = []
    for plugin in report.loaded:
        if not plugin.ok:
            continue
        for provider in plugin.providers:
            provider_checks.append(contract_check_provider(provider))
    return {
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "core_ok": result.ok,
        "core_issues": result.reasons,
        "providers": provider_checks,
        "ok": result.ok and all(p["ok"] for p in provider_checks),
    }
