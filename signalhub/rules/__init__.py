"""Deterministic rule engine — RFC-0001 explanations. No AI."""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence

from signalhub.core.models import ProcessingStep, Signal
from signalhub.core.models.signal import SignalStatus


@dataclass(slots=True, frozen=True)
class RuleHit:
    rule_id: str
    category: str | None = None
    weight: float = 0.0
    reason: str = ""  # human-readable for rules_applied / Telegram


class Rule(ABC):
    rule_id: str = "rule"

    @abstractmethod
    def evaluate(self, signal: Signal) -> RuleHit | None:
        ...


@dataclass
class KeywordCategoryRule(Rule):
    rule_id: str = "keyword_category"
    mapping: dict[str, tuple[str, float]] = field(default_factory=dict)

    def evaluate(self, signal: Signal) -> RuleHit | None:
        text = f"{signal.title} {signal.summary}".lower()
        best: RuleHit | None = None
        for keyword, (category, weight) in self.mapping.items():
            if keyword.lower() in text:
                hit = RuleHit(
                    rule_id=self.rule_id,
                    category=category,
                    weight=weight,
                    reason=f'keyword: "{keyword}"',
                )
                if best is None or hit.weight > best.weight:
                    best = hit
        if best and best.category:
            # second explanation line for category
            return RuleHit(
                rule_id=best.rule_id,
                category=best.category,
                weight=best.weight,
                reason=best.reason,
            )
        return best


@dataclass
class SourceReputationRule(Rule):
    rule_id: str = "source_reputation"
    source_weights: dict[str, float] = field(default_factory=dict)

    def evaluate(self, signal: Signal) -> RuleHit | None:
        src = (signal.source or "").strip()
        if not src:
            return None
        src_l = src.lower()
        for key, weight in self.source_weights.items():
            if key.lower() in src_l:
                return RuleHit(
                    rule_id=self.rule_id,
                    weight=weight,
                    reason=f"origem: {src}",
                )
        return None


@dataclass
class RecencyRule(Rule):
    rule_id: str = "recency"
    half_life_hours: float = 72.0
    max_weight: float = 10.0

    def evaluate(self, signal: Signal) -> RuleHit | None:
        now = datetime.now(timezone.utc)
        collected = signal.collected_at
        if collected.tzinfo is None:
            collected = collected.replace(tzinfo=timezone.utc)
        age_h = max(0.0, (now - collected).total_seconds() / 3600.0)
        weight = self.max_weight * math.pow(0.5, age_h / max(self.half_life_hours, 1e-6))
        hours = int(round(age_h))
        return RuleHit(
            rule_id=self.rule_id,
            weight=round(weight, 4),
            reason=f"recência: {hours} horas",
        )


@dataclass
class OriginProviderRule(Rule):
    rule_id: str = "origin_provider"
    provider_weights: dict[str, float] = field(default_factory=dict)

    def evaluate(self, signal: Signal) -> RuleHit | None:
        pid = signal.provider or (
            signal.provenance.provider_id if signal.provenance else ""
        )
        if not pid:
            return None
        weight = self.provider_weights.get(pid, 0.0)
        if weight == 0.0 and pid not in self.provider_weights:
            return None
        return RuleHit(
            rule_id=self.rule_id,
            weight=weight,
            reason=f"provider: {pid}",
        )


@dataclass
class ExplicitHelpRule(Rule):
    rule_id: str = "explicit_help"
    phrases: tuple[str, ...] = ("preciso de", "alguém indica", "pedido de ajuda", "me ajud")

    def evaluate(self, signal: Signal) -> RuleHit | None:
        text = f"{signal.title} {signal.summary}".lower()
        for phrase in self.phrases:
            if phrase in text:
                return RuleHit(
                    rule_id=self.rule_id,
                    weight=4.0,
                    reason="pedido explícito de ajuda",
                )
        return None


class RuleEngine:
    def __init__(self, rules: Sequence[Rule] | None = None) -> None:
        self.rules = list(rules or default_rules())

    def apply(self, signal: Signal) -> tuple[Signal, list[RuleHit]]:
        hits: list[RuleHit] = []
        explanations: list[str] = []
        for rule in self.rules:
            hit = rule.evaluate(signal)
            if hit is None:
                continue
            hits.append(hit)
            if hit.reason:
                explanations.append(hit.reason)
            if hit.category and not signal.category:
                signal.category = hit.category
                explanations.append(f"categoria: {hit.category}")

        signal.rules_applied = tuple(dict.fromkeys([*signal.rules_applied, *explanations]))
        signal.transition(
            SignalStatus.CLASSIFIED,
            stage="rule_engine",
            detail=f"{len(hits)} regras",
            rules=explanations,
        )
        return signal, hits


def default_rules() -> list[Rule]:
    return [
        KeywordCategoryRule(
            mapping={
                "advogado": ("legal", 8.0),
                "processo": ("legal", 6.0),
                "reclam": ("complaint", 7.0),
                "fornecedor": ("supplier_search", 7.0),
                "urgente": ("commercial_opportunity", 5.0),
                "voo": ("consumer", 6.0),
                "voo cancelado": ("consumer", 8.0),
                "negativ": ("consumer", 6.0),
            }
        ),
        ExplicitHelpRule(),
        SourceReputationRule(
            source_weights={
                "gov.br": 5.0,
                "jusbrasil": 3.0,
                "reddit": 2.0,
            }
        ),
        OriginProviderRule(
            provider_weights={
                "scout": 3.0,
                "dorking": 2.5,
                "google": 2.0,
                "websites": 2.0,
                "linkedin": 1.5,
                "github": 1.0,
                "manual": 1.0,
            }
        ),
        RecencyRule(),
    ]
