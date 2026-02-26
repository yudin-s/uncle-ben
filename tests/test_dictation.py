import unittest

from uncle_ben.dictation import DictationController


class DictationControllerTests(unittest.TestCase):
    def test_enable_disable_phrases(self) -> None:
        controller = DictationController(
            enable_phrases=["включи диктовку"],
            disable_phrases=["выключи диктовку"],
        )

        self.assertTrue(controller.should_enable("пожалуйста включи диктовку"))
        self.assertTrue(controller.should_disable("сейчас выключи диктовку"))

    def test_does_not_trigger_on_partial_noise(self) -> None:
        controller = DictationController(
            enable_phrases=["включи диктовку"],
            disable_phrases=["выключи диктовку"],
        )

        self.assertFalse(controller.should_enable("вклю диктов"))
        self.assertFalse(controller.should_disable("выкл диктов"))

    def test_active_speaker_tracking(self) -> None:
        controller = DictationController(
            enable_phrases=["включи диктовку"],
            disable_phrases=["выключи диктовку"],
        )

        controller.activate("SPEAKER_01")
        self.assertTrue(controller.is_active_for("SPEAKER_01"))
        self.assertFalse(controller.is_active_for("SPEAKER_02"))

        controller.deactivate()
        self.assertFalse(controller.is_active_for("SPEAKER_01"))


if __name__ == "__main__":
    unittest.main()
