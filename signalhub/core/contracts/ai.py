"""AI ports — isolated from Providers. Implementations live under signalhub.ai."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class LLMPort(ABC):
    @abstractmethod
    def complete(self, prompt: str, *, options: Mapping[str, Any] | None = None) -> str:
        ...


class EmbeddingsPort(ABC):
    @abstractmethod
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        ...


class RerankingPort(ABC):
    @abstractmethod
    def rerank(self, query: str, documents: Sequence[str]) -> Sequence[int]:
        ...


class SummariesPort(ABC):
    @abstractmethod
    def summarize(self, text: str, *, options: Mapping[str, Any] | None = None) -> str:
        ...


class ClassificationPort(ABC):
    @abstractmethod
    def classify(self, text: str, labels: Sequence[str]) -> Mapping[str, float]:
        ...


class ProposalGeneratorPort(ABC):
    @abstractmethod
    def generate_proposal(self, context: Mapping[str, Any]) -> str:
        ...


class ReportGeneratorPort(ABC):
    @abstractmethod
    def generate_report(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        ...
