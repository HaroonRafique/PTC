#!/usr/bin/env bash
set -euo pipefail

pyptc_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${pyptc_dir}"

python3 examples/00_generate_flat_file.py
python3 examples/01_plot_bare_twiss_closed_orbit.py
python3 examples/02_track_bunch_dashboard.py
python3 examples/03_track_bunch_with_apertures.py
python3 examples/04_single_element_misalignment.py
python3 examples/05_full_error_table_orbit_comparison.py

required=(
  "test_outputs/01_plot_bare_twiss_closed_orbit/bare_twiss_closed_orbit.png"
  "test_outputs/02_track_bunch_dashboard/bunch_initial_dashboard.png"
  "test_outputs/02_track_bunch_dashboard/bunch_final_dashboard.png"
  "test_outputs/03_track_bunch_with_apertures/aperture_vs_design.png"
  "test_outputs/03_track_bunch_with_apertures/loss_map.png"
  "test_outputs/03_track_bunch_with_apertures/aperture_at_peak_loss_node.png"
  "test_outputs/04_single_element_misalignment/single_element_orbit_response.png"
  "test_outputs/05_full_error_table_orbit_comparison/full_error_table_pyptc_orbit.png"
  "test_outputs/05_full_error_table_orbit_comparison/madx_vs_pyptc_closed_orbit_comparison.png"
)

for path in "${required[@]}"; do
  if [[ ! -s "${path}" ]]; then
    printf 'missing required example output: %s\n' "${path}" >&2
    exit 1
  fi
done

printf 'PyPTC examples completed; outputs are under test_outputs/.\n'
