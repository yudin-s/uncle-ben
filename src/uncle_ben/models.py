from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TranscriptEvent:
    speaker: str
    text: str
    language: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActionCommand:
    action: str
    payload: dict[str, Any]
    confidence: float = 0.0


@dataclass
class ActionResult:
    success: bool
    message: str
