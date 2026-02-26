from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel


class WhisperTranscriber:
    def __init__(
        self,
        model_name: str,
        language: str,
        device: str = "auto",
        compute_type: str = "int8",
        beam_size: int = 5,
        best_of: int = 5,
        temperature: float = 0.0,
        vad_filter: bool = True,
        condition_on_previous_text: bool = True,
        initial_prompt: str = "",
    ) -> None:
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
        self.language = language
        self.beam_size = max(1, beam_size)
        self.best_of = max(1, best_of)
        self.temperature = temperature
        self.vad_filter = vad_filter
        self.condition_on_previous_text = condition_on_previous_text
        self.initial_prompt = initial_prompt.strip()

    def transcribe(self, pcm_bytes: bytes) -> tuple[str, str, float]:
        if not pcm_bytes:
            return "", self.language, 0.0

        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        segments, info = self.model.transcribe(
            audio,
            language=self.language,
            beam_size=self.beam_size,
            best_of=self.best_of,
            temperature=self.temperature,
            vad_filter=self.vad_filter,
            condition_on_previous_text=self.condition_on_previous_text,
            initial_prompt=self.initial_prompt or None,
        )
        text_parts: list[str] = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        text = " ".join(part for part in text_parts if part).strip()
        probability = float(getattr(info, "language_probability", 0.0) or 0.0)
        detected_language = getattr(info, "language", self.language) or self.language
        return text, detected_language, probability
