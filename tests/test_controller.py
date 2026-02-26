from datetime import datetime, timedelta
import unittest

from uncle_ben.controller import WakeWordController


class WakeWordControllerTests(unittest.TestCase):
    def test_grants_control_on_wake_word(self) -> None:
        controller = WakeWordController(["эй бэн"], active_seconds=10)
        now = datetime.utcnow()

        is_controller, text = controller.process("SPEAKER_01", "Эй Бэн открой safari", now)

        self.assertTrue(is_controller)
        self.assertEqual(text, "открой safari")
        self.assertEqual(controller.state.active_speaker, "SPEAKER_01")

    def test_preserves_original_casing_for_dictation(self) -> None:
        controller = WakeWordController(["эй бэн"], active_seconds=10)
        now = datetime.utcnow()

        controller.process("SPEAKER_01", "Эй Бэн", now)
        is_controller, text = controller.process("SPEAKER_01", "Привет Мир", now + timedelta(seconds=1))

        self.assertTrue(is_controller)
        self.assertEqual(text, "Привет Мир")

    def test_allows_same_speaker_during_ttl(self) -> None:
        controller = WakeWordController(["эй бэн"], active_seconds=10)
        now = datetime.utcnow()
        controller.process("SPEAKER_01", "эй бэн", now)

        is_controller, text = controller.process("SPEAKER_01", "переключи окно", now + timedelta(seconds=3))

        self.assertTrue(is_controller)
        self.assertEqual(text, "переключи окно")

    def test_wake_word_with_punctuation(self) -> None:
        controller = WakeWordController(["эй бен"], active_seconds=10)
        now = datetime.utcnow()

        is_controller, text = controller.process("SPEAKER_01", "Эй, Бен, включи диктовку.", now)

        self.assertTrue(is_controller)
        self.assertEqual(text, "включи диктовку.")

    def test_denies_other_speaker(self) -> None:
        controller = WakeWordController(["эй бэн"], active_seconds=10)
        now = datetime.utcnow()
        controller.process("SPEAKER_01", "эй бэн", now)

        is_controller, text = controller.process("SPEAKER_02", "открой notes", now + timedelta(seconds=1))

        self.assertFalse(is_controller)
        self.assertEqual(text, "")


if __name__ == "__main__":
    unittest.main()
