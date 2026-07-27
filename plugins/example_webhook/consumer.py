from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.models import Signal
from signalhub.sdk import SignalConsumer


class ExampleWebhookConsumer(SignalConsumer):
    def consumer_id(self) -> str:
        return "example_webhook"

    def consume(self, signals: Sequence[Signal]) -> Mapping[str, Any]:
        return {
            "consumer": "example_webhook",
            "count": len(signals),
            "status": "ok_stub",
            "ids": [str(s.id) for s in signals[:20]],
        }
