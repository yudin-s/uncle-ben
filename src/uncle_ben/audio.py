from __future__ import annotations

from collections import deque
from queue import Empty, Queue
from threading import Event
from typing import Optional

import numpy as np
import sounddevice as sd
import webrtcvad


class AudioCapture:
    def __init__(
        self,
        sample_rate: int,
        frame_ms: int,
        input_device: str = "",
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_samples = int(sample_rate * frame_ms / 1000)
        self.frame_bytes = self.frame_samples * 2
        self.input_device = input_device or None
        self.queue: Queue[bytes] = Queue(maxsize=512)
        self._stream: Optional[sd.InputStream] = None
        self._stopped = Event()

    def start(self) -> None:
        def callback(indata: np.ndarray, frames: int, _time, status) -> None:
            if status:
                return
            if frames != self.frame_samples:
                return
            chunk = indata[:, 0].astype(np.int16).tobytes()
            if not self.queue.full():
                self.queue.put_nowait(chunk)

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.frame_samples,
            device=self.input_device,
            callback=callback,
        )
        self._stream.start()

    def stop(self) -> None:
        self._stopped.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()


class VADSegmenter:
    def __init__(
        self,
        source_queue: Queue[bytes],
        sample_rate: int,
        frame_ms: int,
        aggressiveness: int,
        min_segment_ms: int,
        max_segment_ms: int,
        silence_padding_ms: int,
    ) -> None:
        self.source_queue = source_queue
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.min_frames = max(1, min_segment_ms // frame_ms)
        self.max_frames = max(1, max_segment_ms // frame_ms)
        self.silence_frames = max(1, silence_padding_ms // frame_ms)
        self.vad = webrtcvad.Vad(aggressiveness)

        self._segment: list[bytes] = []
        self._in_speech = False
        self._silence_counter = 0
        self._pre_roll: deque[bytes] = deque(maxlen=max(1, 200 // frame_ms))

    def next_segment(self, timeout: float = 0.5) -> Optional[bytes]:
        while True:
            try:
                frame = self.source_queue.get(timeout=timeout)
            except Empty:
                return None

            is_speech = self.vad.is_speech(frame, self.sample_rate)
            self._pre_roll.append(frame)

            if not self._in_speech:
                if is_speech:
                    self._in_speech = True
                    self._segment = list(self._pre_roll)
                    self._silence_counter = 0
                continue

            self._segment.append(frame)
            if is_speech:
                self._silence_counter = 0
            else:
                self._silence_counter += 1

            if len(self._segment) >= self.max_frames:
                return self._flush_segment()

            if self._silence_counter >= self.silence_frames:
                if len(self._segment) >= self.min_frames:
                    return self._flush_segment()
                self._reset()

    def _flush_segment(self) -> bytes:
        chunk = b"".join(self._segment)
        self._reset()
        return chunk

    def _reset(self) -> None:
        self._segment = []
        self._in_speech = False
        self._silence_counter = 0
