from __future__ import annotations

import hashlib
from typing import Sequence

from signalhub.core.contracts.provider import (
    HealthStatus,
    Provider,
    ProviderMetadata,
    ProviderQuery,
    RawHit,
)
from signalhub.core.models import ProcessingStep, Provenance, Signal, SignalType
from signalhub.core.models.common import EntityId
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION, SignalStatus


class BaseProvider(Provider):
    """Shared helpers — subclasses implement search. Never calls AI. RFC-0001."""

    provider_id: str = "base"
    provider_name: str = "Base"
    version: str = "0.2.0"
    capability_ids: tuple[str, ...] = ()
    description: str = ""

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id=self.provider_id,
            name=self.provider_name,
            version=self.version,
            capabilities=self.capability_ids,
            description=self.description,
            enabled_by_default=False,
        )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(ok=True, provider_id=self.provider_id, detail="scaffold")

    def collect(self, hits: Sequence[RawHit]) -> Sequence[RawHit]:
        return list(hits)

    def normalize(self, hits: Sequence[RawHit]) -> Sequence[Signal]:
        signals: list[Signal] = []
        for hit in hits:
            body = f"{hit.title}\n{hit.snippet}\n{hit.url or ''}"
            content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
            prov = hit.provenance or Provenance(
                provider_id=self.provider_id,
                source_url=hit.url,
                origin=hit.source or self.provider_id,
                content_hash=content_hash,
            )
            try:
                st = SignalType(hit.signal_type)
            except ValueError:
                st = SignalType.OTHER
            # Provider-specific extras only in metadata (RFC-0001)
            meta = dict(hit.raw)
            signal = Signal(
                id=EntityId(f"{self.provider_id}:{hit.external_id}"),
                provider=self.provider_id,
                title=hit.title or "(sem título)",
                summary=hit.snippet,
                url=hit.url,
                category=hit.category,
                source=hit.source or self.provider_id,
                signal_type=st,
                provenance=prov,
                metadata=meta,
                status=SignalStatus.DISCOVERED,
                version="1",
                contract_version=SIGNAL_CONTRACT_VERSION,
            )
            signal.with_step(
                ProcessingStep(
                    stage="provider_normalize",
                    detail=f"provider={self.provider_id}",
                    to_status=SignalStatus.DISCOVERED.value,
                )
            )
            signals.append(signal)
        return signals

    def validate(self, signals: Sequence[Signal]) -> Sequence[Signal]:
        """Provider-local precheck — Core SignalValidator is authoritative."""
        out: list[Signal] = []
        for signal in signals:
            if not (signal.url or signal.id):
                continue
            out.append(signal)
        return out

    def enrich(self, signals: Sequence[Signal]) -> Sequence[Signal]:
        for signal in signals:
            if not signal.source:
                signal.source = self.provider_id
            signal.with_step(ProcessingStep(stage="provider_enrich", detail="non_ai"))
        return list(signals)

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
