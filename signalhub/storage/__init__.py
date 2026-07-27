from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.storage import LeadStore, VectorStore
from signalhub.core.models import Lead, Signal
from signalhub.core.models.common import EntityId


class InMemorySignalStore:
    def __init__(self) -> None:
        self._items: dict[str, Signal] = {}

    def upsert(self, signals: Sequence[Signal]) -> int:
        for signal in signals:
            self._items[str(signal.id)] = signal
        return len(signals)

    def get(self, signal_id: EntityId | str) -> Signal | None:
        return self._items.get(str(signal_id))

    def list_recent(self, *, limit: int = 50, category: str | None = None) -> list[Signal]:
        items = list(self._items.values())
        if category:
            items = [s for s in items if (s.category or "") == category]
        items.sort(key=lambda s: s.collected_at, reverse=True)
        return items[: max(0, limit)]

    def clear(self) -> None:
        self._items.clear()


# Shared default store for process-local Core
DEFAULT_SIGNAL_STORE = InMemorySignalStore()


class InMemoryLeadStore(LeadStore):
    def __init__(self) -> None:
        self._items: dict[str, Lead] = {}

    def upsert(self, leads: Sequence[Lead]) -> int:
        for lead in leads:
            self._items[str(lead.id)] = lead
        return len(leads)

    def get(self, lead_id: EntityId) -> Lead | None:
        return self._items.get(str(lead_id))


class NullVectorStore(VectorStore):
    def upsert_embeddings(
        self,
        ids: Sequence[str],
        vectors: Sequence[Sequence[float]],
    ) -> int:
        _ = (ids, vectors)
        return 0
