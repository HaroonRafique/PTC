#!/usr/bin/env bash
set -euo pipefail

STEP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ITERATION_DIR="${STEP_DIR}/iteration-0001"
VENV_DIR="${STEP_DIR}/.venv"

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r "${ITERATION_DIR}/requirements.txt"

printf 'Benchmark environment ready.\n'
printf 'Python: '
"${VENV_DIR}/bin/python" --version
printf 'Activate with: source %q\n' "${VENV_DIR}/bin/activate"
