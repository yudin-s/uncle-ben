from __future__ import annotations

import re


class DictationController:
    def __init__(self, enable_phrases: list[str], disable_phrases: list[str]) -> None:
        self.enable_phrases = [phrase.strip().lower() for phrase in enable_phrases if phrase.strip()]
        self.disable_phrases = [phrase.strip().lower() for phrase in disable_phrases if phrase.strip()]
        self.active_speaker: str | None = None

    def is_active_for(self, speaker: str) -> bool:
        return self.active_speaker == speaker

    def activate(self, speaker: str) -> None:
        self.active_speaker = speaker

    def deactivate(self) -> None:
        self.active_speaker = None

    def should_enable(self, text: str) -> bool:
        return any(self._contains_phrase(text, phrase) for phrase in self.enable_phrases)

    def should_disable(self, text: str) -> bool:
        return any(self._contains_phrase(text, phrase) for phrase in self.disable_phrases)

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        text_tokens = self._tokenize(text)
        phrase_tokens = self._tokenize(phrase)
        if not text_tokens or not phrase_tokens or len(text_tokens) < len(phrase_tokens):
            return False

        phrase_len = len(phrase_tokens)
        for index in range(0, len(text_tokens) - phrase_len + 1):
            if text_tokens[index : index + phrase_len] == phrase_tokens:
                return True
        return False

    def _tokenize(self, text: str) -> list[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
        return [token for token in cleaned.split() if token]
