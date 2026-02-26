# FMA (Failure Mode Analysis) — Uncle Ben

## Pipeline
Audio Capture → VAD → ASR (Whisper) → Speaker Role → Wake/Control FSM → LLM Intent → Action Executor

## Failure Modes

1. **False wake word**
- Причина: фоновые разговоры похожи на `Эй Бэн`
- Митигация: требовать подтверждение от того же speaker в течение TTL, добавить confidence threshold

2. **Missed wake word**
- Причина: акцент/шум
- Митигация: несколько вариантов wake-фразы, адаптация через пользовательские aliases

3. **Wrong intent extraction**
- Причина: LLM hallucination
- Митигация: строгий JSON-схема контракт + allowlist action types

4. **Unsafe action execution**
- Причина: слишком свободный executor
- Митигация: только поддерживаемые команды, no-shell policy, параметры с ограничениями

5. **Speaker attribution errors**
- Причина: diarization недоступна/ошибается
- Митигация: fallback single speaker, возможность включить pyannote/whisperx позже

6. **Realtime lag**
- Причина: тяжелая модель whisper/LLM
- Митигация: меньшая модель (`small/base`), batching сегментов, локальная lightweight LLM

## Recovery Strategy
- Любая ошибка NLU/Executor не должна падать весь сервис.
- Ошибки пишутся в `events.jsonl`.
- FSM остается работоспособным после исключений.
