#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  echo "[warn] .venv not found. Create it and install dependencies first."
fi

echo "[1/3] Compile check"
python3 -m compileall src

echo "[2/3] Unit tests"
PYTHONPATH=src python3 -m unittest discover -s tests -v

echo "[3/3] Voice smoke test (macOS say)"
say -v "Milena" -r 180 "Проверка озвучивания завершена"

echo "All checks passed"
