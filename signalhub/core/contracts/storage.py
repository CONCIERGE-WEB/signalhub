from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from signalhub.core.models import Lead
from signalhub.core.models.common import EntityId


class LeadStore(ABC):
    @abstractmethod
    def upsert(self, leads: Sequence[Lead]) -> int:
        ...

    @abstractmethod
    def get(self, lead_id: EntityId) -> Lead | None:
        ...


class VectorStore(ABC):
    @abstractmethod
    def upsert_embeddings(
        self,
        ids: Sequence[str],
        vectors: Sequence[Sequence[float]],
    ) -> int:
        ...
