from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import ActionCommand


@dataclass
class PendingConfirmation:
    speaker: str
    command: ActionCommand
    expires_at: datetime


class ConfirmationGuard:
    def __init__(
        self,
        risky_actions: list[str],
        confirm_words: list[str],
        cancel_words: list[str],
        ttl_seconds: int,
    ) -> None:
        self.risky_actions = {action.strip().lower() for action in risky_actions if action.strip()}
        self.confirm_words = [word.strip().lower() for word in confirm_words if word.strip()]
        self.cancel_words = [word.strip().lower() for word in cancel_words if word.strip()]
        self.ttl_seconds = ttl_seconds
        self.pending: PendingConfirmation | None = None

    def handle(self, speaker: str, text: str, command: ActionCommand, now: datetime) -> tuple[ActionCommand | None, str]:
        normalized = " ".join(text.lower().split())

        if self.pending is not None:
            if now > self.pending.expires_at:
                self.pending = None
                return None, "confirmation_timeout"

            if speaker != self.pending.speaker:
                return None, "confirmation_waiting_other_speaker"

            if self._has_any(normalized, self.cancel_words):
                self.pending = None
                return None, "confirmation_cancelled"

            if self._has_any(normalized, self.confirm_words):
                approved = self.pending.command
                self.pending = None
                return approved, "confirmation_approved"

            return None, "confirmation_needed"

        if command.action.lower() in self.risky_actions:
            self.pending = PendingConfirmation(
                speaker=speaker,
                command=command,
                expires_at=now + timedelta(seconds=self.ttl_seconds),
            )
            return None, "confirmation_requested"

        return command, "direct_execute"

    def _has_any(self, text: str, variants: list[str]) -> bool:
        return any(token in text for token in variants)
