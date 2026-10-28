#!/usr/bin/env bash
set -euo pipefail

iteration_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
step_dir=$(cd "$iteration_dir/.." && pwd -P)
repo_root=$(cd "$step_dir/../.." && pwd -P)
venv_dir="$step_dir/.venv"
mkdir -p "$step_dir/.mplconfig"

if [[ ! -x "$venv_dir/bin/python" ]]; then
    python3 -m venv "$venv_dir"
fi
"$venv_dir/bin/python" -m pip install --disable-pip-version-check -r "$iteration_dir/requirements.txt"
MPLCONFIGDIR="$step_dir/.mplconfig" PYTHONPATH="$repo_root${PYTHONPATH:+:$PYTHONPATH}" "$venv_dir/bin/python" - "$repo_root" "$step_dir" <<'PY'
import json
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
step_dir = Path(sys.argv[2])
sys.path.insert(0, str(repo_root))
import matplotlib
import numpy
from pyptc import PTC

library = step_dir / "admission_basis-accepted-attempt-20261027T194128Z" / "bootstrap" / "libpyptc.so"
if not library.is_file():
    raise SystemExit(f"Accepted PyPTC library is missing: {library}")
ptc = PTC(library)
print(json.dumps({
    "python": sys.version.split()[0],
    "numpy": numpy.__version__,
    "matplotlib": matplotlib.__version__,
    "pyptc_api_level": ptc.api_level(),
    "library": str(library),
}, indent=2))
PY
printf 'Benchmark environment ready.\n'
printf 'Run from the step directory with: ./iteration-0002/run_benchmark.py\n'
