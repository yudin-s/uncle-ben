from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any


class EventLogger:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def emit(self, event_type: str, payload: Any) -> None:
        now = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
        data = asdict(payload) if is_dataclass(payload) else payload
        record = {
            "ts": now,
            "event": event_type,
            "payload": data,
        }
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
