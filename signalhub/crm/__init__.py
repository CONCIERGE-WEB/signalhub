"""CRM automation plugins — human-in-the-loop sinks only."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.models import Lead


class CrmSink:
    def push(self, leads: Sequence[Lead], *, options: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        _ = options
        return {
            "status": "ok_stub",
            "count": len(leads),
            "nota": "CRM sink stub — sem envio automático.",
        }
