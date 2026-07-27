"""Report generation facade — uses AI ReportGeneratorPort."""
from __future__ import annotations

from typing import Any, Mapping

from signalhub.ai.null import NullAI
from signalhub.core.contracts.ai import ReportGeneratorPort


class ReportService:
    def __init__(self, ai: ReportGeneratorPort | None = None) -> None:
        self._ai: ReportGeneratorPort = ai or NullAI()

    def generate(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._ai.generate_report(context)
