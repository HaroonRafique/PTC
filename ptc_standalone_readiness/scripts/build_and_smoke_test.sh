#!/usr/bin/env bash
set -euo pipefail

readiness_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "${readiness_dir}/.." && pwd)"
build_dir="${BUILD_DIR:-${repo_root}/build-standalone}"
python_cmd="${PYTHON:-python3}"

log() {
  printf '[ptc] %s\n' "$*"
}

if ! command -v meson >/dev/null 2>&1; then
  printf 'meson is required but was not found on PATH.\n' >&2
  exit 1
fi

if ! command -v nm >/dev/null 2>&1; then
  printf 'nm is required but was not found on PATH.\n' >&2
  exit 1
fi

if [ -f "${build_dir}/build.ninja" ]; then
  log "Reconfiguring existing Meson build at ${build_dir}"
  meson setup "${build_dir}" "${repo_root}" --reconfigure
else
  log "Configuring Meson build at ${build_dir}"
  meson setup "${build_dir}" "${repo_root}"
fi

log "Compiling libptc_orbit"
meson compile -C "${build_dir}"

library="${build_dir}/libptc_orbit.so"
if [ ! -f "${library}" ]; then
  printf 'Expected shared library was not produced: %s\n' "${library}" >&2
  exit 1
fi

log "Checking exported symbols"
for symbol in \
  ptc_init_ \
  ptc_get_ini_params_ \
  ptc_get_syncpart_ \
  ptc_track_particle_ \
  ptc_synchronous_set_ \
  ptc_synchronous_after_ \
  ptc_update_twiss_
do
  if ! nm -D "${library}" | grep -q "[[:space:]]${symbol}$"; then
    printf 'Expected symbol not found in %s: %s\n' "${library}" "${symbol}" >&2
    exit 1
  fi
done

log "Running Python ctypes smoke test"
"${python_cmd}" "${readiness_dir}/tests/smoke_load_ptc.py" --library "${library}" "$@"
