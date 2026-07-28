"""Debug Provider — laboratório permanente. Só sinais sintéticos."""

from __future__ import annotations

import time
from typing import Any, Sequence

from signalhub.core.contracts.provider import (
    HealthStatus,
    ProviderMetadata,
    ProviderQuery,
    RawHit,
)
from signalhub.sdk import ProviderPlugin

MODES = (
    "valid",
    "invalid",
    "high_score",
    "low_score",
    "bad_url",
    "duplicate",
    "huge_metadata",
    "unknown_category",
    "bad_timestamp",
)


def resolve_mode(query: ProviderQuery) -> str:
    extras = dict(query.extras or {})
    raw = str(extras.get("mode") or "").strip().lower()
    if raw in MODES:
        return raw
    for term in query.terms or ():
        t = str(term).strip().lower()
        if t in MODES:
            return t
    return "valid"


class DebugSignalsProvider(ProviderPlugin):
    """Laboratório do SignalHub — nunca remover."""

    provider_id = "debug"
    provider_name = "Debug Lab"
    version = "1.0.0"
    description = (
        "Synthetic signal factory for platform validation. "
        "No network. Modes: " + ", ".join(MODES)
    )
    capability_ids = ("discover_signals", "debug_generate")

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id=self.provider_id,
            name=self.provider_name,
            version=self.version,
            capabilities=self.capability_ids,
            description=self.description,
            requires_network=False,
            respects_robots=True,
            enabled_by_default=True,
        )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail="lab — synthetic only (no network)",
            latency_ms=0.0,
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        mode = resolve_mode(query)
        limit = max(1, min(int(query.limit or 5), 20))
        stamp = int(time.time() * 1000)
        hits: list[RawHit] = []

        def hit(**kwargs: Any) -> RawHit:
            base = {
                "external_id": f"dbg-{mode}-{stamp}-{len(hits)}",
                "title": "Synthetic Signal",
                "url": f"https://lab.signalhub.local/signals/{stamp}-{len(hits)}",
                "snippet": "Laboratório SignalHub — sinal sintético.",
                "signal_type": "other",
                "category": "consumer",
                "source": "debug",
                "raw": {"lab_mode": mode, "synthetic": True},
            }
            base.update(kwargs)
            return RawHit(**base)

        if mode == "valid":
            hits.append(
                hit(
                    title="Synthetic Signal",
                    snippet="Valid synthetic signal for pipeline validation.",
                )
            )
        elif mode == "invalid":
            # Title vazio → Core Validator rejeita
            hits.append(hit(title="", url=None, snippet=""))
        elif mode == "high_score":
            hits.append(
                hit(
                    title="Voo cancelado preciso de ajuda urgente",
                    snippet="Reclamação pública: atraso e bagagem extraviada. Preciso de ajuda.",
                    signal_type="help_request",
                    category="consumer",
                )
            )
        elif mode == "low_score":
            hits.append(
                hit(
                    title="Nota genérica sem palavras-chave",
                    snippet="Texto neutro para score baixo.",
                    category="other",
                )
            )
        elif mode == "bad_url":
            hits.append(hit(url="not-a-url", title="Signal with bad URL"))
        elif mode == "duplicate":
            url = f"https://lab.signalhub.local/dup/{stamp}"
            hits.append(hit(url=url, title="Duplicate A"))
            hits.append(hit(url=url, title="Duplicate B", external_id=f"dbg-dup-b-{stamp}"))
        elif mode == "huge_metadata":
            hits.append(
                hit(
                    title="Huge metadata payload",
                    raw={
                        "lab_mode": mode,
                        "synthetic": True,
                        "blob": "x" * 8000,
                    },
                )
            )
        elif mode == "unknown_category":
            hits.append(
                hit(
                    title="Category that may not classify",
                    category="not_a_real_category_xyz",
                )
            )
        elif mode == "bad_timestamp":
            hits.append(
                hit(
                    title="Odd timestamp metadata",
                    raw={"lab_mode": mode, "occurred_at": "not-a-date"},
                )
            )
        else:
            hits.append(hit())

        return hits[:limit]


__all__ = ["DebugSignalsProvider", "MODES", "resolve_mode"]
