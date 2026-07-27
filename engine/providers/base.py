"""Contrato único de descoberta de leads (Provider pattern).

Todo canal (Scout, LinkedIn, Maps, sites) implementa LeadDiscoveryProvider.
O bot Telegram e o painel web consomem leads já validados — não orquestram a busca.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class LeadSink(str, Enum):
    POSTGRES = "postgres"
    DASHBOARD = "dashboard"
    CRM = "crm"
    API_REST = "api_rest"
    TELEGRAM_ALERT = "telegram_alert"
    AUTOMATION = "automation"


@dataclass(slots=True)
class LeadCandidate:
    """Candidato normalizado — sem PII além do necessário à qualificação."""

    source: str
    external_id: str
    title: str = ""
    url: str | None = None
    snippet: str = ""
    geo: str | None = None
    vertical: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)
    score: float | None = None
    enriched: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderQuery:
    """Pedido de descoberta — vertical + termos + limites."""

    vertical: str
    terms: Sequence[str] = ()
    geo: str | None = None
    limit: int = 40
    extras: Mapping[str, Any] = field(default_factory=dict)


class LeadDiscoveryProvider(ABC):
    """Interface única — Scout e futuros canais."""

    name: str = "base"

    @abstractmethod
    def search(self, query: ProviderQuery) -> Sequence[LeadCandidate]:
        """Descoberta bruta na fonte pública do provider."""

    @abstractmethod
    def collect(self, hits: Sequence[LeadCandidate]) -> Sequence[LeadCandidate]:
        """Normalização, dedupe e campos mínimos."""

    @abstractmethod
    def enrich(self, leads: Sequence[LeadCandidate]) -> Sequence[LeadCandidate]:
        """Sinais extras (stack, especialidade, presença digital)."""

    @abstractmethod
    def validate(self, leads: Sequence[LeadCandidate]) -> Sequence[LeadCandidate]:
        """Filtros LGPD / fonte pública / score mínimo."""

    @abstractmethod
    def export(
        self,
        leads: Sequence[LeadCandidate],
        sink: LeadSink,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """Persistência ou entrega — nunca contato automático sem humano."""

    def run(self, query: ProviderQuery, sink: LeadSink = LeadSink.POSTGRES) -> Mapping[str, Any]:
        """Esteira padrão: search → collect → enrich → validate → export."""
        hits = self.search(query)
        collected = self.collect(hits)
        enriched = self.enrich(collected)
        valid = self.validate(enriched)
        return self.export(valid, sink)
