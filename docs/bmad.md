# BMAD (Build–Measure–Analyze–Decide)

## Cycle 1 (MVP)
### Build
- Реализован end-to-end pipeline с базовыми командами.

### Measure
- Собирать метрики latency, wake detections, command success/failure.

### Analyze
- Анализировать ложные wake detections и ошибки intent parser.

### Decide
- Подкрутить prompt и пороги VAD.
- При необходимости перейти на реальную diarization.

## Cycle 2 (Hardening)
### Build
- Добавить pyannote/whisperx diarization.
- Добавить confirmation mode для рискованных команд.

### Measure
- Сравнить precision/recall по wake и intents до/после.

### Analyze
- Найти топ-10 провалов в логах.

### Decide
- Обновить action grammar.
- Внедрить пользовательские профили голоса.
