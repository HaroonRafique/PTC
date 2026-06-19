#!/usr/bin/env bash
set -euo pipefail

readiness_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "${readiness_dir}/.." && pwd)"
input_file="${1:-${readiness_dir}/inputs/PTC-PyORBIT_flat_file.madx.flt}"
build_dir="${BUILD_DIR:-${repo_root}/build-standalone}"
output_dir="${OUTPUT_DIR:-${readiness_dir}/outputs/PTC_standalone_outputs}"
python_cmd="${PYTHON:-python3}"

if [ ! -f "${input_file}" ]; then
  printf 'PTC input file not found: %s\n' "${input_file}" >&2
  exit 1
fi

rm -rf "${build_dir}" "${output_dir}"
mkdir -p "${output_dir}"

{
  printf '[ptc] repo: %s\n' "${repo_root}"
  printf '[ptc] input: %s\n' "${input_file}"
  printf '[ptc] build_dir: %s\n' "${build_dir}"
  printf '[ptc] output_dir: %s\n' "${output_dir}"
  printf '[ptc] python: %s\n' "$("${python_cmd}" --version)"

  BUILD_DIR="${build_dir}" PYTHON="${python_cmd}" "${readiness_dir}/scripts/build_and_smoke_test.sh"

  printf '[ptc] attempting functional test with original input\n'
  set +e
  pushd "${output_dir}" >/dev/null
  MPLCONFIGDIR="${output_dir}/matplotlib-cache" "${python_cmd}" "${readiness_dir}/tests/functional_ptc_lattice.py" \
    --library "${build_dir}/libptc_orbit.so" \
    --ptc-input "${input_file}" \
    --output-dir "${output_dir}/original_input"
  original_rc=$?
  popd >/dev/null
  set -e
  printf '%s\n' "${original_rc}" > "${output_dir}/original_input_exit_code.txt"

  normalized_rc=-1
  if [ "${original_rc}" -ne 0 ]; then
    printf '[ptc] original input failed with exit code %s; creating normalized compatibility copy\n' "${original_rc}"
    normalized_input="${output_dir}/PTC-PyORBIT_flat_file.normalized.flt"
    "${python_cmd}" "${readiness_dir}/tests/normalize_ptc_flat_file.py" \
      "${input_file}" \
      "${normalized_input}" \
      --report "${output_dir}/normalization_report.json"

    printf '[ptc] attempting functional test with normalized input\n'
    set +e
    pushd "${output_dir}" >/dev/null
    MPLCONFIGDIR="${output_dir}/matplotlib-cache" "${python_cmd}" "${readiness_dir}/tests/functional_ptc_lattice.py" \
      --library "${build_dir}/libptc_orbit.so" \
      --ptc-input "${normalized_input}" \
      --output-dir "${output_dir}/normalized_input"
    normalized_rc=$?
    popd >/dev/null
    set -e
    printf '%s\n' "${normalized_rc}" > "${output_dir}/normalized_input_exit_code.txt"
  fi

  "${python_cmd}" - "${output_dir}/status.json" "${original_rc}" "${normalized_rc}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
status = {
    "build_and_symbol_smoke": "passed",
    "original_input_exit_code": int(sys.argv[2]),
    "normalized_input_exit_code": int(sys.argv[3]),
    "functional_tracking": "passed" if int(sys.argv[2]) == 0 or int(sys.argv[3]) == 0 else "failed_before_tracking",
}
path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(status, indent=2, sort_keys=True))
PY

  printf '[ptc] output files:\n'
  find "${output_dir}" -maxdepth 2 -type f | sort
} 2>&1 | tee "${output_dir}/run.log"
