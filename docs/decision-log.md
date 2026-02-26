# Decision Log

## 2026-02-23

1. Выбрана Python-реализация для быстрого MVP и простых интеграций (audio + whisper + automation).
2. ASR: `faster-whisper` как наиболее практичный локальный вариант.
3. Wake-word: текстовый матч в ASR потоке (`эй бэн` и варианты).
4. Управление ownership через `active_speaker + TTL`.
5. NLU: локальная lightweight LLM через Ollama streaming API.
6. Executor ограничен allowlist-командами (без произвольного shell).
7. Диаризация в MVP как fallback single-speaker; архитектура оставляет точку расширения.
8. Для рискованных действий добавлен confirmation guard с TTL и проверкой speaker ownership.
9. Добавлена настройка `DIARIZATION_DEVICE` для более практичной работы на CPU/MPS.
10. Озвучивание реализовано через локальный macOS `say`; `whisper` оставлен только для ASR.
11. Для естественности добавлен параметр `VOICE_FEEDBACK_RATE` и нормализация пунктуации в TTS-ответах.
12. Для тестирования зафиксирован средний пресет `Milena + rate 180`, добавлены unit-тесты FSM/confirmation и smoke-скрипт `scripts/run_tests.sh`.
13. Добавлен `scripts/run_e2e_manual.sh` для ручной проверки сценариев wake-word, confirmation и cancel в реальном микрофонном цикле.
14. Добавлен `Makefile` с командами `setup`, `test`, `unit`, `e2e` для ускорения повторяемых запусков.
15. Добавлен one-command запуск `make run`/`make one` с авто-подготовкой `.venv` и стартом ассистента.
16. Добавлен режим непрерывной диктовки с голосовым `on/off` и выделенным `DictationController`.
17. В `WakeWordController` сохранён оригинальный регистр/текст для диктовки; нормализация оставлена только для распознавания wake/команд.
18. Ввод диктовки переведён с эмуляции клавиш на вставку через `pbcopy` + `Cmd+V` для устойчивой работы с русским Unicode и раскладками.
19. Усилен профиль `faster-whisper`: `medium`, `beam/best_of=5`, `vad_filter=true`, `condition_on_previous_text=true`, настраиваемый `initial_prompt`.
20. Переключение окон расширено направлением `next/previous` (`Cmd+Tab` и `Cmd+Shift+Tab`).
21. Убраны ложные `Готово` на `action=none`; pending-подтверждение обрабатывается с более высоким приоритетом, чем режим диктовки.
