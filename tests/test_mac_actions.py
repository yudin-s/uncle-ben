import unittest
from unittest.mock import patch

from uncle_ben.mac_actions import MacActionExecutor
from uncle_ben.models import ActionCommand


class MacActionExecutorWindowSwitchTests(unittest.TestCase):
    @patch("uncle_ben.mac_actions.pyautogui.hotkey")
    def test_switch_next_window(self, hotkey_mock) -> None:
        executor = MacActionExecutor()

        result = executor.execute(ActionCommand(action="switch_window", payload={"direction": "next"}))

        self.assertTrue(result.success)
        hotkey_mock.assert_called_once_with("command", "tab")

    @patch("uncle_ben.mac_actions.pyautogui.hotkey")
    def test_switch_previous_window(self, hotkey_mock) -> None:
        executor = MacActionExecutor()

        result = executor.execute(ActionCommand(action="switch_window", payload={"direction": "previous"}))

        self.assertTrue(result.success)
        hotkey_mock.assert_called_once_with("command", "shift", "tab")


if __name__ == "__main__":
    unittest.main()
