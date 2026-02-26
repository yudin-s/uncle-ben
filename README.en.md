# Uncle Ben

[![Tests](https://github.com/OWNER/uncle-ben/actions/workflows/tests.yml/badge.svg)](https://github.com/OWNER/uncle-ben/actions/workflows/tests.yml)
[![Lint](https://github.com/OWNER/uncle-ben/actions/workflows/lint.yml/badge.svg)](https://github.com/OWNER/uncle-ben/actions/workflows/lint.yml)

> Replace `OWNER` with your GitHub user/org once `origin` is configured.

Local macOS voice assistant with wake word (“Hey Ben”), speech-to-text via `faster-whisper`, intent routing via local LLM (`Ollama`), and safety-guarded system actions.

This repository is an MVP focused on private/local usage without mandatory cloud dependencies.

## Features

- Continuous microphone listening with VAD segmentation.
- Speech transcription with `faster-whisper`.
- Wake-word activation + speaker ownership with TTL.
- Intent parsing into strict JSON (`action`, `payload`, `confidence`).
- Allowlisted actions: `dictate_text`, `move_mouse`, `switch_window`, `open_app`.
- Confirmation flow for risky actions (`RISKY_ACTIONS`).
- Dictation mode with voice on/off phrases.
- JSONL event logging to `logs/events.jsonl`.

## Repository Map

| Path | Purpose |
|---|---|
| `src/uncle_ben/main.py` | Main runtime loop |
| `src/uncle_ben/config.py` | Environment-based app config |
| `src/uncle_ben/audio.py` | Audio capture + VAD segmentation |
| `src/uncle_ben/transcriber.py` | `faster-whisper` integration |
| `src/uncle_ben/controller.py` | Wake-word FSM / control ownership |
| `src/uncle_ben/intent_router.py` | Ollama integration + JSON parsing |
| `src/uncle_ben/safety.py` | Risky-action confirmation guard |
| `src/uncle_ben/mac_actions.py` | macOS action execution |
| `src/uncle_ben/dictation.py` | Dictation mode state |
| `src/uncle_ben/diarization.py` | Optional diarization (`whisperx`) |
| `src/uncle_ben/voice_feedback.py` | Voice feedback via macOS `say` |
| `tests/` | Unit tests |
| `scripts/` | Run/test/E2E helpers |
| `docs/` | Product and architecture artifacts |

## Architecture (high level)

`AudioCapture → VADSegmenter → WhisperTranscriber → SpeakerRoleResolver → WakeWordController → IntentRouter → ConfirmationGuard → MacActionExecutor → EventLogger`

- Event-driven orchestration lives in `main.py`.
- With `USE_DIARIZATION=false`, speaker fallback is `SPEAKER_00`.
- `action=none` is treated as no-op.

More details:

- `docs/architecture-overview.md`
- `docs/adr/0001-system-architecture.md`

## Requirements

- macOS (target platform).
- Python 3.11+.
- `Ollama` installed and running.
- macOS permissions:
  - Microphone
  - Accessibility

## Setup and Run

### Recommended (Makefile)

```bash
make setup
make run
```

### Manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
brew install ollama
ollama serve
ollama pull qwen2.5:3b-instruct
PYTHONPATH=src python -m uncle_ben.main
```

## Verification

```bash
make test
```

Additional options:

```bash
make unit
make e2e
```

`make e2e` runs an interactive manual voice scenario.

## Configuration

Use `.env.example` as a template.

Key groups:

- Whisper: `WHISPER_*` (including `WHISPER_INITIAL_PROMPT`)
- Language/wake: `LANGUAGE`, `WAKE_WORDS`, `ACTIVE_CONTROL_SECONDS`
- LLM: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- Safety: `RISKY_ACTIONS`, `CONFIRM_WORDS`, `CANCEL_WORDS`, `CONFIRMATION_TTL_SECONDS`
- Dictation: `DICTATION_ENABLE_PHRASES`, `DICTATION_DISABLE_PHRASES`
- Voice feedback: `VOICE_FEEDBACK_ENABLED`, `VOICE_FEEDBACK_VOICE`, `VOICE_FEEDBACK_RATE`
- Audio/VAD: `INPUT_DEVICE`, `SAMPLE_RATE`, `FRAME_MS`, `VAD_AGGRESSIVENESS`, `MIN_SEGMENT_MS`, `MAX_SEGMENT_MS`, `SILENCE_PADDING_MS`
- Logging: `LOG_LEVEL`, `EVENTS_LOG_PATH`

## Security

- Actions from `RISKY_ACTIONS` require explicit confirmation from the same speaker.
- Confirmation timeout is controlled by `CONFIRMATION_TTL_SECONDS`.
- Executor is allowlist-based; no arbitrary shell execution.

See `SECURITY.md` for reporting policy.

## MVP Limitations

- Optimized for macOS and Russian-first voice UX.
- Accuracy depends on microphone, noise conditions, and selected Whisper model.
- Full diarization is optional and disabled by default.
- `models/piper` contains local assets, while default runtime TTS uses macOS `say`.

## Open Source

- License: GPL-3.0-only (`LICENSE`)
- Contribution guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`

## Disclaimer

Provided “as is”, without warranties. Review voice-triggered actions before using on a daily-driver machine.
