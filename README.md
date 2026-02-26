# Uncle Ben

[![Tests](https://github.com/OWNER/uncle-ben/actions/workflows/tests.yml/badge.svg)](https://github.com/OWNER/uncle-ben/actions/workflows/tests.yml)
[![Lint](https://github.com/OWNER/uncle-ben/actions/workflows/lint.yml/badge.svg)](https://github.com/OWNER/uncle-ben/actions/workflows/lint.yml)

> Замените `OWNER` на ваш GitHub user/org после настройки `origin`.

Локальный голосовой ассистент для macOS с wake-word «Эй Бэн», транскрибацией через `faster-whisper`, интерпретацией интентов через локальную LLM (`Ollama`) и безопасным выполнением системных команд.

Проект ориентирован на приватный локальный запуск (MVP), без обязательной облачной зависимости.

English version: `README.en.md`.

## Что это умеет

- Непрерывно слушает микрофон и режет поток на речевые сегменты (VAD).
- Преобразует речь в текст (`faster-whisper`).
- Активирует контроль по wake-word и держит ownership по спикеру с TTL.
- Парсит намерения в структурированный JSON (`action`, `payload`, `confidence`) через Ollama.
- Выполняет allowlist-действия: `dictate_text`, `move_mouse`, `switch_window`, `open_app`.
- Требует подтверждение для рискованных действий (`RISKY_ACTIONS`).
- Поддерживает режим непрерывной диктовки (voice on/off).
- Логирует события в `logs/events.jsonl`.

## Карта артефактов репозитория

| Путь | Назначение |
|---|---|
| `src/uncle_ben/main.py` | Главный runtime-цикл ассистента |
| `src/uncle_ben/config.py` | Загрузка и валидация конфигурации из `.env` |
| `src/uncle_ben/audio.py` | Аудиозахват и VAD-сегментация |
| `src/uncle_ben/transcriber.py` | Интеграция с `faster-whisper` |
| `src/uncle_ben/controller.py` | Wake-word FSM и ownership управления |
| `src/uncle_ben/intent_router.py` | Вызов Ollama и парсинг JSON-команд |
| `src/uncle_ben/safety.py` | Guard подтверждения рискованных действий |
| `src/uncle_ben/mac_actions.py` | Исполнение действий в macOS |
| `src/uncle_ben/dictation.py` | Управление режимом диктовки |
| `src/uncle_ben/diarization.py` | Опциональная diarization через `whisperx` |
| `src/uncle_ben/voice_feedback.py` | Голосовой feedback через `say` |
| `tests/` | Unit-тесты FSM, safety, dictation, window-switch |
| `scripts/run_app.sh` | Запуск приложения с проверкой окружения |
| `scripts/run_tests.sh` | Compile + unit + voice smoke |
| `scripts/run_e2e_manual.sh` | Пошаговый ручной E2E сценарий |
| `docs/` | Проектные артефакты (A3/FMA/BMAD/ADR/decision log) |
| `models/piper/` | Локальные TTS-артефакты (сейчас не используются в runtime по умолчанию) |

## Архитектура (кратко)

`AudioCapture → VADSegmenter → WhisperTranscriber → SpeakerRoleResolver → WakeWordController → IntentRouter → ConfirmationGuard → MacActionExecutor → EventLogger`

- Event-driven цикл реализован в `main.py`.
- При `USE_DIARIZATION=false` используется fallback `SPEAKER_00`.
- Для `action=none` команды не исполняются и `"Готово"` не озвучивается.

Подробные документы:

- `docs/architecture-overview.md`
- `docs/adr/0001-system-architecture.md`

## Системные требования

- macOS (целевая платформа).
- Python 3.11+.
- Установленный `Ollama`.
- Доступы в macOS:
	- `Microphone`
	- `Accessibility` (для управления клавиатурой/мышью/окнами).

## Установка и запуск

### Вариант 1: через Makefile (рекомендуется)

```bash
make setup
make run
```

### Вариант 2: вручную

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

## Проверка работоспособности

```bash
make test
```

Дополнительно:

```bash
make unit
make e2e
```

`make e2e` запускает интерактивный ручной сценарий с ожидаемыми голосовыми шагами.

## Конфигурация (`.env`)

Источник примера: `.env.example`.

Ключевые группы переменных:

- Whisper: `WHISPER_*` (включая `WHISPER_INITIAL_PROMPT`).
- Язык и wake-word: `LANGUAGE`, `WAKE_WORDS`, `ACTIVE_CONTROL_SECONDS`.
- LLM: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.
- Safety: `RISKY_ACTIONS`, `CONFIRM_WORDS`, `CANCEL_WORDS`, `CONFIRMATION_TTL_SECONDS`.
- Dictation: `DICTATION_ENABLE_PHRASES`, `DICTATION_DISABLE_PHRASES`.
- Voice feedback: `VOICE_FEEDBACK_ENABLED`, `VOICE_FEEDBACK_VOICE`, `VOICE_FEEDBACK_RATE`.
- Audio/VAD: `INPUT_DEVICE`, `SAMPLE_RATE`, `FRAME_MS`, `VAD_AGGRESSIVENESS`, `MIN_SEGMENT_MS`, `MAX_SEGMENT_MS`, `SILENCE_PADDING_MS`.
- Логи: `LOG_LEVEL`, `EVENTS_LOG_PATH`.

## Наблюдаемость

- Все runtime-события пишутся в `logs/events.jsonl` в формате JSONL.
- Типовые события: `transcript`, `intent`, `confirmation`, `action_result`, `dictation`, `control_granted`.

## Безопасность

- Команды из `RISKY_ACTIONS` требуют подтверждения от того же спикера.
- Таймаут подтверждения настраивается через `CONFIRMATION_TTL_SECONDS`.
- Executor ограничен allowlist-экшенами; произвольный shell не используется.

Подробнее: `SECURITY.md`.

## Ограничения MVP

- Проект сфокусирован на macOS и русском голосовом UX.
- Качество зависит от микрофона, шума и выбранной Whisper-модели.
- Полная diarization опциональна и отключена по умолчанию.
- В `models/piper` лежат артефакты, но дефолтный TTS в проекте — системный `say`.

## Документы проекта

- `docs/a3.md` — постановка задачи и контрмеры.
- `docs/fma.md` — анализ отказов.
- `docs/bmad.md` — цикл улучшений.
- `docs/decision-log.md` — журнал инженерных решений.
- `docs/adr/0001-system-architecture.md` — архитектурное решение.

## Open Source

- Лицензия: GPL-3.0-only (`LICENSE`).
- Вклад в проект: `CONTRIBUTING.md`.
- Политика безопасности: `SECURITY.md`.

## Дисклеймер

Проект распространяется «как есть», без гарантий пригодности для конкретной цели. Проверяйте голосовые команды перед использованием на рабочей системе.
