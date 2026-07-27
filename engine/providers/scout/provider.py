"""Scout — LeadDiscoveryProvider (scaffold).

A lógica Scout concreta ainda não está no repositório; este módulo define o
encaixe. Até P1, search/collect retornam vazio explícito (sem inventar leads).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..base import LeadCandidate, LeadDiscoveryProvider, LeadSink, ProviderQuery


class ScoutLeadProvider(LeadDiscoveryProvider):
    name = "scout"

    def search(self, query: ProviderQuery) -> Sequence[LeadCandidate]:
        # P1: plugar Scout real. Até lá — vazio explícito (sem fallback fictício).
        _ = query
        return ()

    def collect(self, hits: Sequence[LeadCandidate]) -> Sequence[LeadCandidate]:
        seen: set[str] = set()
        out: list[LeadCandidate] = []
        for h in hits:
            key = f"{h.source}:{h.external_id}"
            if key in seen:
                continue
            seen.add(key)
            out.append(h)
        return out

    def enrich(self, leads: Sequence[LeadCandidate]) -> Sequence[LeadCandidate]:
        # P2: stack tech / especialidade / sinais de vertical.
        return list(leads)

    def validate(self, leads: Sequence[LeadCandidate]) -> Sequence[LeadCandidate]:
        # Só fontes com URL pública ou id externo; sem score inventado.
        return [L for L in leads if (L.url or L.external_id)]

    def export(
        self,
        leads: Sequence[LeadCandidate],
        sink: LeadSink,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        _ = options
        return {
            "provider": self.name,
            "sink": sink.value,
            "count": len(leads),
            "status": "ok_vazio" if not leads else "ok",
            "nota": (
                "Scaffold Scout — sem inventar leads. "
                "Telegram/CRM só após validate + humano no loop."
            ),
        }
