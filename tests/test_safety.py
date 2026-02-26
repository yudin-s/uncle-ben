from datetime import datetime, timedelta
import unittest

from uncle_ben.models import ActionCommand
from uncle_ben.safety import ConfirmationGuard


class ConfirmationGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = ConfirmationGuard(
            risky_actions=["move_mouse", "switch_window"],
            confirm_words=["да", "подтверждаю"],
            cancel_words=["отмена", "нет"],
            ttl_seconds=5,
        )
        self.now = datetime.utcnow()

    def test_requests_confirmation_for_risky_action(self) -> None:
        command = ActionCommand(action="move_mouse", payload={"dx": 100, "dy": 0})

        approved, status = self.guard.handle("SPEAKER_01", "двинь мышь", command, self.now)

        self.assertIsNone(approved)
        self.assertEqual(status, "confirmation_requested")

    def test_approves_after_confirm_word(self) -> None:
        command = ActionCommand(action="switch_window", payload={})
        self.guard.handle("SPEAKER_01", "переключи окно", command, self.now)

        approved, status = self.guard.handle(
            "SPEAKER_01",
            "да, подтверждаю",
            ActionCommand(action="none", payload={}),
            self.now + timedelta(seconds=1),
        )

        self.assertIsNotNone(approved)
        self.assertEqual(status, "confirmation_approved")
        self.assertEqual(approved.action, "switch_window")

    def test_cancels_after_cancel_word(self) -> None:
        command = ActionCommand(action="move_mouse", payload={"dx": 100, "dy": 0})
        self.guard.handle("SPEAKER_01", "двинь мышь", command, self.now)

        approved, status = self.guard.handle(
            "SPEAKER_01",
            "отмена",
            ActionCommand(action="none", payload={}),
            self.now + timedelta(seconds=1),
        )

        self.assertIsNone(approved)
        self.assertEqual(status, "confirmation_cancelled")

    def test_times_out_pending_confirmation(self) -> None:
        command = ActionCommand(action="move_mouse", payload={"dx": 100, "dy": 0})
        self.guard.handle("SPEAKER_01", "двинь мышь", command, self.now)

        approved, status = self.guard.handle(
            "SPEAKER_01",
            "да",
            ActionCommand(action="none", payload={}),
            self.now + timedelta(seconds=8),
        )

        self.assertIsNone(approved)
        self.assertEqual(status, "confirmation_timeout")


if __name__ == "__main__":
    unittest.main()
