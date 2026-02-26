from __future__ import annotations

import subprocess


class VoiceFeedback:
    def __init__(self, enabled: bool = True, voice: str = "Milena", rate: int = 180) -> None:
        self.enabled = enabled
        self.voice = voice
        self.rate = max(120, min(260, int(rate)))

    def speak(self, text: str) -> None:
        if not self.enabled:
            return
        cleaned = " ".join(text.split()).strip()
        if not cleaned:
            return
        if cleaned[-1] not in ".!?…":
            cleaned = f"{cleaned}."
        try:
            subprocess.Popen(["say", "-v", self.voice, "-r", str(self.rate), cleaned])
        except Exception:
            return
