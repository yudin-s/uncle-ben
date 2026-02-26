from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re


@dataclass
class ControlState:
    active_speaker: str | None = None
    active_until: datetime | None = None


class WakeWordController:
    def __init__(self, wake_words: list[str], active_seconds: int) -> None:
        self.wake_words = [word.lower().strip() for word in wake_words]
        self.active_seconds = active_seconds
        self.state = ControlState()

    def process(self, speaker: str, text: str, now: datetime) -> tuple[bool, str]:
        original = " ".join(text.split())
        normalized = self._normalize_for_match(original)
        has_wake = any(self._contains_phrase(normalized, self._normalize_for_match(word)) for word in self.wake_words)

        if has_wake:
            self.state.active_speaker = speaker
            self.state.active_until = now + timedelta(seconds=self.active_seconds)
            clean_text = original
            for word in self.wake_words:
                clean_text = self._remove_phrase(clean_text, word)
            clean_text = re.sub(r"^[\W_]+", "", clean_text, flags=re.UNICODE)
            return True, clean_text.strip()

        if (
            self.state.active_speaker == speaker
            and self.state.active_until is not None
            and now <= self.state.active_until
        ):
            return True, original

        return False, ""

    def _normalize_for_match(self, text: str) -> str:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
        return " ".join(cleaned.split())

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        if not text or not phrase:
            return False
        pattern = rf"(?:^|\s){re.escape(phrase)}(?:$|\s)"
        return re.search(pattern, text, flags=re.UNICODE) is not None

    def _remove_phrase(self, text: str, phrase: str) -> str:
        phrase_tokens = [token for token in self._normalize_for_match(phrase).split() if token]
        if not phrase_tokens:
            return text
        pattern = r"\b" + r"\W+".join(re.escape(token) for token in phrase_tokens) + r"\b"
        result = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.UNICODE)
        return " ".join(result.split())
