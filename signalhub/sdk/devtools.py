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
        "plugin_version": manifest.version,
        "core_version": __version__,
        "declared_contract_version": manifest.contract_version,
        "declared_signalhub_version": manifest.signalhub_version,
    }


def doctor(*, full: bool = False) -> dict[str, Any]:
    sample_issues = contract_check_signal(make_sample_signal())
    loader = PluginLoader()
    report = loader.load_all()
    plugins = []
    for p in report.loaded:
        plugins.append(
            {
                "name": p.manifest.name,
                "version": p.manifest.version,
                "contract_version": p.manifest.contract_version,
                "signalhub_version": p.manifest.signalhub_version,
                "ok": p.ok,
                "errors": p.errors,
                "providers": len(p.providers),
                "capabilities": len(p.capabilities),
                "adapters": len(p.adapters),
                "consumers": len(p.consumers),
            }
        )
    out: dict[str, Any] = {
        "signalhub_version": __version__,
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "core_sample_signal_ok": not sample_issues,
        "core_sample_issues": sample_issues,
        "plugin_dirs": [str(d) for d in loader.search_dirs],
        "plugins": plugins,
        "ok": not sample_issues and all(p["ok"] for p in plugins if plugins),
        "full": full,
        "positioning": (
            "SignalHub is a signal-processing framework. "
            "Source integrations are independent plugins under each platform's ToS."
        ),
    }
    if not full:
        return out

    from signalhub.bootstrap import build_container
    from signalhub.observability.metrics import platform_metrics
    from signalhub.platform.compatibility import run_contract_suite
    from signalhub.platform.health import run_all_health_checks

    container = build_container(load_plugins=True)
    health = run_all_health_checks(container)
    contracts = run_contract_suite(container)
    out["health"] = health
    out["contracts"] = contracts
    out["metrics"] = platform_metrics().snapshot()
    out["surfaces"] = {
        "contract": contracts.get("ok"),
        "providers": next(
            (c["ok"] for c in health["checks"] if c["component"] == "providers"), False
        ),
        "adapters": next(
            (c["ok"] for c in health["checks"] if c["component"] == "adapters"), False
        ),
        "capabilities": next(
            (c["ok"] for c in health["checks"] if c["component"] == "capabilities"), False
        ),
        "storage": next(
            (c["ok"] for c in health["checks"] if c["component"] == "storage"), False
        ),
        "configuration": True,
        "plugins": next(
            (c["ok"] for c in health["checks"] if c["component"] == "plugins"), False
        ),
        "mcp": next((c["ok"] for c in health["checks"] if c["component"] == "mcp"), False),
        "rest": next((c["ok"] for c in health["checks"] if c["component"] == "rest"), False),
        "telegram": next(
            (c["ok"] for c in health["checks"] if c["component"] == "telegram"), False
        ),
    }
    out["ok"] = bool(out["ok"] and health.get("ok") and contracts.get("ok"))
    return out


def contract_check() -> dict[str, Any]:
    validator = SignalValidator()
    sample = make_sample_signal()
    result = validator.validate(sample)
    from signalhub.bootstrap import build_container
    from signalhub.platform.compatibility import run_contract_suite

    container = build_container(load_plugins=True)
    suite = run_contract_suite(container)
    provider_checks = []
    for meta in container.providers.list_metadata():
        provider_checks.append(contract_check_provider(container.providers.get(meta.provider_id)))
    return {
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "core_ok": result.ok,
        "core_issues": result.reasons,
        "providers": provider_checks,
        "suite": suite,
        "ok": result.ok and suite["ok"] and all(p["ok"] for p in provider_checks),
    }
