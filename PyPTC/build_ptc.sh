#!/usr/bin/env bash
set -euo pipefail

pyptc_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
build_dir="${BUILD_DIR:-${pyptc_dir}/build-pyptc}"
python_cmd="${PYTHON:-python3}"

log() {
  printf '[pyptc] %s\n' "$*"
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
  log "Reconfiguring PyPTC build at ${build_dir}"
  meson setup "${build_dir}" "${pyptc_dir}" --reconfigure
else
  log "Configuring PyPTC build at ${build_dir}"
  meson setup "${build_dir}" "${pyptc_dir}"
fi

log "Compiling libpyptc"
meson compile -C "${build_dir}"

library="${build_dir}/libpyptc.so"
if [ ! -f "${library}" ]; then
  printf 'Expected shared library was not produced: %s\n' "${library}" >&2
  exit 1
fi

log "Checking exported symbols"
nm_output="$(nm -D "${library}")"
for symbol in \
  ptc_init_ \
  ptc_get_ini_params_ \
  ptc_get_syncpart_ \
  ptc_get_twiss_for_node_ \
  ptc_track_particle_ \
  ptc_synchronous_set_ \
  ptc_synchronous_after_ \
  ptc_update_twiss_ \
  pyptc_get_api_level \
  pyptc_get_tunes \
  pyptc_get_chromaticities \
  pyptc_set_misalignment \
  pyptc_set_madx_misalignment \
  pyptc_set_one_aperture \
  pyptc_turn_off_one_aperture \
  pyptc_set_absolute_aperture \
  pyptc_get_absolute_aperture \
  pyptc_track_particle_ring_loss \
  pyptc_set_acceleration \
  pyptc_set_ramping \
  pyptc_set_modulation \
  pyptc_set_cavity \
  pyptc_store_orbit_state \
  pyptc_use_orbit_state \
  pyptc_set_all_ramp \
  pyptc_energize_lattice \
  pyptc_set_orbit_time \
  pyptc_initialize_cavity \
  pyptc_close_cavity_ring \
  pyptc_power_cavity \
  pyptc_cavity_totalpath \
  pyptc_configure_ac_magnet \
  pyptc_configure_ramp_magnet
do
  if ! printf '%s\n' "${nm_output}" | grep -q "[[:space:]]${symbol}$"; then
    printf 'Expected symbol not found in %s: %s\n' "${library}" "${symbol}" >&2
    printf 'Meson compiler info: %s\n' "$(meson introspect "${build_dir}" --compilers 2>/dev/null || true)" >&2
    printf 'Available exported ptc_* symbols:\n' >&2
    printf '%s\n' "${nm_output}" | awk '$3 ~ /^ptc_/ { print "  " $3 }' | sort >&2
    printf 'Available exported pyptc_* symbols:\n' >&2
    printf '%s\n' "${nm_output}" | awk '$3 ~ /^pyptc_/ { print "  " $3 }' | sort >&2
    exit 1
  fi
done

log "Running ctypes smoke import"
"${python_cmd}" - "${library}" <<'PY'
import ctypes
import sys

library = sys.argv[1]
lib = ctypes.CDLL(library)
for name in (
    "ptc_init_",
    "ptc_get_ini_params_",
    "ptc_get_syncpart_",
    "ptc_get_twiss_for_node_",
    "ptc_track_particle_",
    "ptc_synchronous_set_",
    "ptc_synchronous_after_",
    "ptc_update_twiss_",
    "pyptc_get_api_level",
    "pyptc_get_tunes",
    "pyptc_get_chromaticities",
    "pyptc_set_misalignment",
    "pyptc_set_madx_misalignment",
    "pyptc_set_one_aperture",
    "pyptc_turn_off_one_aperture",
    "pyptc_set_absolute_aperture",
    "pyptc_get_absolute_aperture",
    "pyptc_track_particle_ring_loss",
    "pyptc_set_acceleration",
    "pyptc_set_ramping",
    "pyptc_set_modulation",
    "pyptc_set_cavity",
    "pyptc_store_orbit_state",
    "pyptc_use_orbit_state",
    "pyptc_set_all_ramp",
    "pyptc_energize_lattice",
    "pyptc_set_orbit_time",
    "pyptc_initialize_cavity",
    "pyptc_close_cavity_ring",
    "pyptc_power_cavity",
    "pyptc_cavity_totalpath",
    "pyptc_configure_ac_magnet",
    "pyptc_configure_ramp_magnet",
):
    getattr(lib, name)
print(f"PTC ctypes smoke check passed: {library}")
PY

log "Build ready: ${library}"
