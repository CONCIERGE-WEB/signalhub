"""SDK — Rulesets plug into the Rule Engine without editing Core defaults."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from signalhub.rules import Rule


class RulesetPlugin(ABC):
    @abstractmethod
    def ruleset_id(self) -> str:
        ...

    @abstractmethod
    def rules(self) -> Sequence[Rule]:
        ...
