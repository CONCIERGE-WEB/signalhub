"""Telegram as Notification Adapter — RFC-0001 rules_applied explanations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from signalhub.core.models import Signal, SignalPriority, SignalType
from signalhub.core.models.signal import SignalStatus


@dataclass(slots=True)
class NotificationAction:
    id: str
    label: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "label": self.label}


@dataclass(slots=True)
class SignalNotification:
    signal_type: str
    origin: str
    score: float | None
    confidence: float | None
    justification: Sequence[str]
    rules_applied: Sequence[str]
    category: str | None
    priority: str
    title: str
    url: str | None = None
    signal_id: str | None = None
    status: str | None = None
    summary: str | None = None
    actions: Sequence[NotificationAction] = ()
    aggregated_count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "origin": self.origin,
            "score": self.score,
            "confidence": self.confidence,
            "justification": list(self.justification),
            "rules_applied": list(self.rules_applied),
            "category": self.category,
            "priority": self.priority,
            "title": self.title,
            "summary": self.summary or self.title,
            "url": self.url,
            "signal_id": self.signal_id,
            "status": self.status,
            "actions": [a.to_dict() for a in self.actions],
            "aggregated_count": self.aggregated_count,
        }

    def format_text(self) -> str:
        rules = list(self.rules_applied) or list(self.justification)
        rule_lines = [f"✔ {r}" for r in rules[:12]] or ["✔ (sem regras)"]
        resumo = (self.summary or self.title or "—")[:280]
        lines = [
            f"[SignalHub] Prioridade: {self.priority.upper()}",
            f"Categoria: {self.category or '—'}",
            f"Origem: {self.origin}",
            f"Score: {self.score if self.score is not None else '—'}",
            f"Confiança do algoritmo: {self.confidence if self.confidence is not None else '—'}",
            f"Tipo: {self.signal_type}",
            f"Título: {self.title}",
            f"Resumo: {resumo}",
            "Rules Applied / Regras:",
            *rule_lines,
            "Justificativa do Score:",
            *[f"• {j}" for j in (list(self.justification)[:8] or ["—"])],
        ]
        if self.url:
            lines.append(f"Link: {self.url}")
        if self.aggregated_count > 1:
            lines.append(f"Agregado: {self.aggregated_count} sinais similares")
        if self.actions:
            lines.append("Ações: " + ", ".join(a.label for a in self.actions))
        return "\n".join(lines)


DEFAULT_ACTIONS: tuple[NotificationAction, ...] = (
    NotificationAction("open", "Abrir origem"),
    NotificationAction("snooze", "Adiar"),
    NotificationAction("dismiss", "Descartar"),
)


class TelegramNotificationAdapter:
    """Formats and optionally aggregates Signal notifications. Does not scrape."""

    def __init__(
        self,
        *,
        min_score: float = 5.0,
        min_priority: SignalPriority = SignalPriority.NORMAL,
        aggregate_window_seconds: float = 300.0,
    ) -> None:
        self.min_score = min_score
        self.min_priority = min_priority
        self.aggregate_window_seconds = aggregate_window_seconds
        self._buffer: list[tuple[datetime, SignalNotification]] = []
        self._sent: list[SignalNotification] = []

    def from_signal(self, signal: Signal) -> SignalNotification | None:
        if signal.score is not None and signal.score < self.min_score:
            return None
        priority = (
            signal.priority
            if isinstance(signal.priority, SignalPriority)
            else SignalPriority(str(signal.priority))
        )
        order = [
            SignalPriority.LOW,
            SignalPriority.NORMAL,
            SignalPriority.HIGH,
            SignalPriority.URGENT,
        ]
        if order.index(priority) < order.index(self.min_priority):
            return None

        st = (
            signal.signal_type.value
            if isinstance(signal.signal_type, SignalType)
            else str(signal.signal_type)
        )
        origin = signal.source or signal.provider
        just = list(signal.rules_applied)
        if signal.score_breakdown:
            just = list(signal.rules_applied) or list(signal.score_breakdown.justification)

        signal.transition(
            SignalStatus.CONSUMED,
            stage="telegram_notify",
            detail="notification",
        )

        return SignalNotification(
            signal_type=st,
            origin=origin,
            score=signal.score,
            confidence=signal.confidence,
            justification=just,
            rules_applied=list(signal.rules_applied),
            category=signal.category,
            priority=priority.value,
            title=signal.title,
            url=signal.url,
            signal_id=str(signal.id),
            status=signal.status_value,
            summary=signal.summary or signal.title,
            actions=DEFAULT_ACTIONS,
        )

    def enqueue(self, signal: Signal) -> SignalNotification | None:
        note = self.from_signal(signal)
        if note is None:
            return None
        now = datetime.now(timezone.utc)
        self._buffer.append((now, note))
        return note

    def flush_aggregated(self) -> list[SignalNotification]:
        if not self._buffer:
            return []
        now = datetime.now(timezone.utc)
        due: list[SignalNotification] = []
        keep: list[tuple[datetime, SignalNotification]] = []
        groups: dict[tuple[str, str], list[SignalNotification]] = {}

        for ts, note in self._buffer:
            age = (now - ts).total_seconds()
            if age < self.aggregate_window_seconds:
                keep.append((ts, note))
                continue
            key = (note.category or "", note.origin)
            groups.setdefault(key, []).append(note)

        self._buffer = keep
        for items in groups.values():
            if len(items) == 1:
                due.append(items[0])
            else:
                base = items[0]
                base.aggregated_count = len(items)
                base.title = f"{base.title} (+{len(items) - 1} similares)"
                due.append(base)

        self._sent.extend(due)
        return due

    def preview_batch(self, signals: Sequence[Signal]) -> list[Mapping[str, Any]]:
        out: list[Mapping[str, Any]] = []
        for signal in signals:
            note = self.from_signal(signal)
            if note:
                out.append(note.to_dict())
        return out
