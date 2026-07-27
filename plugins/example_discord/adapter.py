from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.models import Signal
from signalhub.sdk import NotificationAdapterPort


class ExampleDiscordAdapter(NotificationAdapterPort):
    def adapter_id(self) -> str:
        return "example_discord"

    def notify(self, signals: Sequence[Signal]) -> Mapping[str, Any]:
        return {
            "adapter": "example_discord",
            "count": len(signals),
            "status": "ok_stub",
            "nota": "Wire Discord webhook later — Core stays unchanged.",
        }
