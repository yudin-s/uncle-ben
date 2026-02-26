# ADR-0001: Event-driven Voice Control Pipeline

## Status
Accepted

## Context
Нужен локальный macOS voice assistant с wake-word, whisper ASR, role-aware control и lightweight LLM.

## Decision
Используем event-driven архитектуру:

1. `AudioCapture` снимает PCM чанки
2. `VADSegmenter` формирует речевые сегменты
3. `WhisperTranscriber` делает ASR
4. `RoleResolver` назначает speaker-role (MVP fallback)
5. `ControlFSM` фиксирует ownership управления
6. `IntentRouter` вызывает lightweight LLM (streaming)
7. `MacActionExecutor` исполняет разрешенные действия
8. `EventLogger` пишет единый JSONL журнал

## Consequences
### Positive
- Чёткие границы модулей
- Легко тестировать по отдельности
- Можно заменять ASR/LLM/Executor независимо

### Negative
- MVP diarization неполная
- Нужны системные разрешения macOS

## Alternatives Considered
- Монолитный callback без явной FSM — отклонено (сложно отлаживать)
- Облачные STT/LLM — отклонено (privacy/offline)
