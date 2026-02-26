from __future__ import annotations

import subprocess
from typing import Any

import pyautogui

from .models import ActionCommand, ActionResult


class MacActionExecutor:
    def __init__(self) -> None:
        pyautogui.FAILSAFE = False

    def execute(self, command: ActionCommand) -> ActionResult:
        action = command.action
        payload = command.payload

        try:
            if action == "none":
                return ActionResult(success=True, message="no-op")
            if action == "dictate_text":
                return self._dictate(payload)
            if action == "move_mouse":
                return self._move_mouse(payload)
            if action == "switch_window":
                return self._switch_window(payload)
            if action == "open_app":
                return self._open_app(payload)
            return ActionResult(success=False, message=f"unsupported action: {action}")
        except Exception as error:
            return ActionResult(success=False, message=str(error))

    def _dictate(self, payload: dict[str, Any]) -> ActionResult:
        text = str(payload.get("text", "")).strip()
        if not text:
            return ActionResult(success=False, message="empty text")
        try:
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            pyautogui.hotkey("command", "v")
            return ActionResult(success=True, message="text pasted")
        except Exception:
            pyautogui.write(text, interval=0.01)
            return ActionResult(success=True, message="text typed")

    def _move_mouse(self, payload: dict[str, Any]) -> ActionResult:
        mode = str(payload.get("mode", "relative"))
        duration = float(payload.get("duration", 0.2) or 0.2)

        if mode == "absolute":
            x = int(payload.get("x", 0) or 0)
            y = int(payload.get("y", 0) or 0)
            pyautogui.moveTo(x, y, duration=duration)
            return ActionResult(success=True, message=f"mouse moved to ({x},{y})")

        dx = int(payload.get("dx", 0) or 0)
        dy = int(payload.get("dy", 0) or 0)
        pyautogui.moveRel(dx, dy, duration=duration)
        return ActionResult(success=True, message=f"mouse moved by ({dx},{dy})")

    def _switch_window(self, payload: dict[str, Any]) -> ActionResult:
        app_name = str(payload.get("app", "")).strip()
        if app_name:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(["osascript", "-e", script], check=True)
            return ActionResult(success=True, message=f"switched to {app_name}")

        direction = str(payload.get("direction", "next")).strip().lower()
        if direction in {"previous", "prev", "back", "назад", "предыдущее"}:
            pyautogui.hotkey("command", "shift", "tab")
            return ActionResult(success=True, message="switched to previous window via cmd+shift+tab")

        pyautogui.hotkey("command", "tab")
        return ActionResult(success=True, message="switched to next window via cmd+tab")

    def _open_app(self, payload: dict[str, Any]) -> ActionResult:
        app_name = str(payload.get("app", "")).strip()
        if not app_name:
            return ActionResult(success=False, message="missing app name")
        subprocess.run(["open", "-a", app_name], check=True)
        return ActionResult(success=True, message=f"opened app: {app_name}")
