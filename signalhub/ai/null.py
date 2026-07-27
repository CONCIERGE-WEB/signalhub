from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.contracts.ai import (
    ClassificationPort,
    EmbeddingsPort,
    LLMPort,
    ProposalGeneratorPort,
    RerankingPort,
    ReportGeneratorPort,
    SummariesPort,
)


class NullAI(
    LLMPort,
    EmbeddingsPort,
    RerankingPort,
    SummariesPort,
    ClassificationPort,
    ProposalGeneratorPort,
    ReportGeneratorPort,
):
    """Explicit empty AI — no invented completions."""

    def complete(self, prompt: str, *, options: Mapping[str, Any] | None = None) -> str:
        _ = (prompt, options)
        return ""

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return [() for _ in texts]

    def rerank(self, query: str, documents: Sequence[str]) -> Sequence[int]:
        _ = query
        return list(range(len(documents)))

    def summarize(self, text: str, *, options: Mapping[str, Any] | None = None) -> str:
        _ = (text, options)
        return ""

    def classify(self, text: str, labels: Sequence[str]) -> Mapping[str, float]:
        _ = text
        return {label: 0.0 for label in labels}

    def generate_proposal(self, context: Mapping[str, Any]) -> str:
        _ = context
        return ""

    def generate_report(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        _ = context
        return {"status": "ai_null", "content": ""}
