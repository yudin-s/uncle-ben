# Architecture Overview

## Purpose

`Uncle Ben` — локальный голосовой контроллер для macOS, ориентированный на безопасное выполнение пользовательских команд через voice-интерфейс.

## Runtime Flow

1. Захват аудио из системного устройства ввода.
2. Выделение речевых фрагментов (`VAD`).
3. Транскрибация в текст (`faster-whisper`).
4. Проверка wake-word и состояния control-session.
5. Классификация/интерпретация команды (`IntentRouter` + Ollama).
6. Валидация политики безопасности (рискованные действия требуют подтверждения).
7. Исполнение действия в macOS (`MacActionExecutor`).
8. Логирование в `logs/events.jsonl`.

## Main Components

- `audio.py` — аудиозахват и поток чанков.
- `transcriber.py` — настройка и вызов Whisper-модели.
- `controller.py` — orchestration цикла обработки.
- `intent_router.py` — сопоставление текста с intent/action.
- `safety.py` — правила подтверждения рискованных операций.
- `mac_actions.py` — действие на уровне OS (мышь, окна, приложения, ввод).
- `dictation.py` — голосовой режим ввода текста.
- `voice_feedback.py` — обратная связь через macOS `say`.
- `logging_utils.py` — структурированные event-логи.

## Data and State

- Конфигурация: `.env` → `AppConfig` (`src/uncle_ben/config.py`).
- Краткоживущие состояния:
  - активный контрольный таймер (`ACTIVE_CONTROL_SECONDS`);
  - pending confirmation (`CONFIRMATION_TTL_SECONDS`);
  - флаг режима диктовки.
- Персистентный артефакт: `logs/events.jsonl`.

## Safety Model

- Действия из `RISKY_ACTIONS` не исполняются немедленно.
- Для исполнения требуется подтверждение фразой из `CONFIRM_WORDS`.
- Отмена — фразы из `CANCEL_WORDS`.
- При истечении TTL команда сбрасывается.

## External Dependencies

- `faster-whisper` — STT.
- `Ollama` — локальная LLM для intent parsing.
- `pyautogui` + системные утилиты — OS actions.
- Опционально: `whisperx` + `HF_TOKEN` для diarization.

## Known Limitations

- Основной сценарий оптимизирован под русский язык.
- Полная multi-speaker diarization выключена по умолчанию.
- Качество выполнения действий зависит от выданных macOS разрешений.

## Related Documents

- ADR: `docs/adr/0001-system-architecture.md`
- Decision log: `docs/decision-log.md`
- Product docs: `docs/a3.md`, `docs/fma.md`, `docs/bmad.md`
