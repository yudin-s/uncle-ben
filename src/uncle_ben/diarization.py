from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import numpy as np


class SpeakerRoleResolver:
    def __init__(self, enabled: bool, hf_token: str = "", device: str = "cpu") -> None:
        self.enabled = enabled
        self.hf_token = hf_token
        self.device = device
        self._pipeline = None

        if self.enabled:
            try:
                import whisperx  # type: ignore

                self._pipeline = whisperx.DiarizationPipeline(
                    use_auth_token=hf_token,
                    device=device,
                )
            except Exception:
                self._pipeline = None
                self.enabled = False

    def resolve(self, pcm_bytes: bytes, sample_rate: int) -> str:
        if not self.enabled or self._pipeline is None:
            return "SPEAKER_00"

        wav_path = self._to_wav_file(pcm_bytes, sample_rate)
        try:
            segments = self._pipeline(str(wav_path))
            if segments is None or len(segments) == 0:
                return "SPEAKER_00"

            durations: dict[str, float] = {}
            for _, row in segments.iterrows():
                speaker = str(row.get("speaker", "SPEAKER_00"))
                start = float(row.get("start", 0.0) or 0.0)
                end = float(row.get("end", 0.0) or 0.0)
                durations[speaker] = durations.get(speaker, 0.0) + max(0.0, end - start)

            if not durations:
                return "SPEAKER_00"
            return max(durations, key=durations.get)
        except Exception:
            return "SPEAKER_00"
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except Exception:
                pass

    def _to_wav_file(self, pcm_bytes: bytes, sample_rate: int) -> Path:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            path = Path(handle.name)

        audio = np.frombuffer(pcm_bytes, dtype=np.int16)
        with wave.open(str(path), "wb") as wav_handle:
            wav_handle.setnchannels(1)
            wav_handle.setsampwidth(2)
            wav_handle.setframerate(sample_rate)
            wav_handle.writeframes(audio.tobytes())

        return path
