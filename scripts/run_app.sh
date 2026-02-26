#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${1:-.env.test}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[error] Env file not found: $ENV_FILE"
  echo "Usage: bash scripts/run_app.sh [.env | .env.test]"
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
  echo "Install them first: make setup"
  exit 1
fi

echo "[info] Starting Uncle Ben... (Ctrl+C to stop)"
PYTHONPATH=src python3 -m uncle_ben.main
