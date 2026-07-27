from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping


class StructuredLogger:
    def __init__(self, name: str = "signalhub") -> None:
        self._log = logging.getLogger(name)

    def info(self, message: str, **fields: Any) -> None:
        self._emit("INFO", message, fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit("ERROR", message, fields)

    def _emit(self, level: str, message: str, fields: Mapping[str, Any]) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **dict(fields),
        }
        line = json.dumps(payload, ensure_ascii=False, default=str)
        if level == "ERROR":
            self._log.error(line)
        else:
            self._log.info(line)
