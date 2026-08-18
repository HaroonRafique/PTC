#!/usr/bin/env bash
set -euo pipefail

pyptc_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
repo_root="$(cd "${pyptc_dir}/.." && pwd)"

bash "${pyptc_dir}/build/build_ptc.sh"
python3 "${pyptc_dir}/workflows/madx/run_generated_flatfile_smoke.py" "$@"
