"""SDK testing helpers — validate plugins against RFC-0001."""
from __future__ import annotations

from typing import Any

from signalhub.core.models import Provenance, Signal
from signalhub.core.models.common import EntityId
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION, SignalStatus
from signalhub.core.contracts.provider import Provider, ProviderQuery, RawHit
from signalhub.validation import SignalValidator


def make_sample_signal(**kwargs: Any) -> Signal:
    data: dict[str, Any] = {
        "id": EntityId("sdk:sample"),
        "provider": "sdk_test",
        "title": "sample signal",
        "source": "sdk_test",
        "summary": "",
        "url": "https://example.com/sample",
        "provenance": Provenance(provider_id="sdk_test", source_url="https://example.com/sample"),
        "status": SignalStatus.DISCOVERED,
        "version": "1",
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "metadata": {},
    }
    data.update(kwargs)
    return Signal(**data)


def contract_check_signal(signal: Signal) -> list[str]:
    result = SignalValidator().validate(signal)
    return [] if result.ok else result.reasons


def contract_check_provider(provider: Provider) -> dict[str, Any]:
    """Smoke: metadata, health, empty search, normalize→validate RFC."""
    meta = provider.metadata()
    health = provider.healthcheck()
    hits = list(provider.search(ProviderQuery(capability_id="discover_signals", terms=("sdk",), limit=1)))
    issues: list[str] = []
    if not meta.provider_id:
        issues.append("metadata.provider_id vazio")
    if not health.ok:
        issues.append(f"healthcheck fail: {health.detail}")
    # If provider returns hits, they must normalize to valid Signals
    if hits:
        signals = provider.normalize(hits)
        for signal in signals:
            issues.extend(contract_check_signal(signal))
    else:
        # Ensure normalize of a synthetic RawHit is RFC-ok
        synthetic = [
            RawHit(
                external_id="sdk-check",
                title="SDK contract check",
                url="https://example.com/sdk-check",
                snippet="deterministic test hit",
            )
        ]
        for signal in provider.normalize(synthetic):
            issues.extend(contract_check_signal(signal))
    return {
        "provider_id": meta.provider_id,
        "ok": not issues,
        "issues": issues,
        "contract_version": SIGNAL_CONTRACT_VERSION,
    }
