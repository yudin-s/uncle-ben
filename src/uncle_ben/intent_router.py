from __future__ import annotations

import json
import re
from typing import Any

import requests

from .models import ActionCommand


class IntentRouter:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def route(self, text: str) -> ActionCommand:
        prompt = self._build_prompt(text)
        result = self._chat_stream(prompt)
        payload = self._parse_json(result)

        action = str(payload.get("action", "none"))
        data = payload.get("payload", {})
        confidence = float(payload.get("confidence", 0.0) or 0.0)

        if not isinstance(data, dict):
            data = {}

        return ActionCommand(action=action, payload=data, confidence=confidence)

    def _chat_stream(self, prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        body = {
            "model": self.model,
            "stream": True,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты NLU роутер для голосового ассистента macOS. "
                        "Ответь СТРОГО JSON-объектом вида "
                        "{\"action\": string, \"payload\": object, \"confidence\": number}. "
                        "Разрешённые action: none, dictate_text, move_mouse, switch_window, open_app. "
                        "Для switch_window используй payload.direction=next|previous, "
                        "а для переключения на конкретное приложение используй payload.app."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(url, json=body, timeout=30, stream=True)
        response.raise_for_status()

        chunks: list[str] = []
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            event = json.loads(line)
            message = event.get("message", {})
            content = message.get("content", "")
            if content:
                chunks.append(content)
        return "".join(chunks).strip()

    def _parse_json(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned).strip()
            cleaned = cleaned.rstrip("`").strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        return {"action": "none", "payload": {}, "confidence": 0.0}

    def _build_prompt(self, text: str) -> str:
        return (
            "Преобразуй голосовую команду в action JSON. "
            "Если просят следующее окно — switch_window c payload.direction=next. "
            "Если просят предыдущее окно — switch_window c payload.direction=previous. "
            "Если это обычная диктовка — action=dictate_text и payload.text. "
            "Команда: "
            f"{text}"
        )
