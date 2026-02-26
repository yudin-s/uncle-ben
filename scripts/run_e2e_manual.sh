#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${1:-.env.test}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[error] Env file not found: $ENV_FILE"
  echo "Usage: bash scripts/run_e2e_manual.sh [.env | .env.test]"
  exit 1
fi

if [[ ! -f .env ]]; then
  cp "$ENV_FILE" .env
  echo "[info] Copied $ENV_FILE -> .env"
else
  echo "[info] Existing .env detected, using it as-is"
fi

if ! python3 - <<'PY' >/dev/null 2>&1
import numpy
import sounddevice
import webrtcvad
import requests
from faster_whisper import WhisperModel
PY
then
  echo "[error] Missing Python dependencies."
  echo "Install them first: pip install -r requirements.txt"
  exit 1
fi

echo
cat <<'EOF'
================= Uncle Ben Manual E2E =================
Scenario A (wake + direct command)
  1) Say: "Эй Бэн открой Safari"
  2) Expected:
     - Voice: "Управление активировано"
     - Action: Safari opens
     - Voice: "Готово"

Scenario B (risky action + confirmation)
  1) Say: "Эй Бэн передвинь мышь вправо"
  2) Expected:
     - Voice: "Подтверди выполнение команды"
     - Mouse DOES NOT move yet
  3) Say: "Подтверждаю"
  4) Expected:
     - Mouse moves
     - Voice: "Готово"

Scenario C (risky action + cancel)
  1) Say: "Эй Бэн переключи окно"
  2) Say: "Отмена"
  3) Expected:
     - No window switch
     - Voice: "Команда отменена"

Stop: Ctrl+C
Logs: logs/events.jsonl
=========================================================
EOF

echo
read -r -p "Press Enter to start Uncle Ben..." _

PYTHONPATH=src python3 -m uncle_ben.main
