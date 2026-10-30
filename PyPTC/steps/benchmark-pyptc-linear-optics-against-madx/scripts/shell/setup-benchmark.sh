#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
step_dir=$(cd "$script_dir/../.." && pwd -P)
repo_root=$(cd "$step_dir/../.." && pwd -P)
requirements="$step_dir/iteration-0005/requirements.txt"
venv_dir="$step_dir/.venv"
mkdir -p "$step_dir/.mplconfig"

if [[ ! -x "$venv_dir/bin/python" ]]; then
    python3 -m venv "$venv_dir"
fi
"$venv_dir/bin/python" -m pip install --disable-pip-version-check -r "$requirements"
(cd "$repo_root" && BUILD_DIR="$repo_root/build_pyptc" PYTHON="$venv_dir/bin/python" ./build/build_ptc.sh)
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

library = repo_root / "build_pyptc" / "libpyptc.so"
if not library.is_file():
    raise SystemExit(f"Current PyPTC build is missing: {library}")
ptc = PTC(library)
if ptc.api_level() < 5:
    raise SystemExit(f"PyPTC EFIELD API level 5 is required; found {ptc.api_level()}")
print(json.dumps({
    "python": sys.version.split()[0],
    "numpy": numpy.__version__,
    "matplotlib": matplotlib.__version__,
    "pyptc_api_level": ptc.api_level(),
    "library": str(library),
}, indent=2))
PY
printf 'Benchmark environment ready.\n'
printf 'Skill snapshot: iteration-0005/SKILL.md (SHA-256 b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae)\n'
printf 'Run from the step directory with: ./scripts/shell/benchmark-pyptc-attempt.sh\n'
