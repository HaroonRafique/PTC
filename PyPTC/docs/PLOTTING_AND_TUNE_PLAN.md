# PyPTC Plotting And Exact Tune Diagnostics

## Summary

Update `PyPTC` to produce publication-quality static PNG/PDF plots for the standalone ISIS RCS PTC experiment: Twiss functions, bare vs misaligned closed orbit, orbit difference, and before/after bunch dashboards. Per-particle tune diagnostics should use turn-by-turn phase advance and carry action/survival metadata alongside bunch coordinates.

Status: the first tune/action/survival implementation is present in
`PTC.particle_diagnostics(...)` and `run_misalignment_experiment.py
--with-tunes`.

Status update: all tests and smoke workflows should default to the generated
simplified flat file at
`PyPTC/workflows/madx/outputs/simplified/PTC-PyORBIT_flat_file.flt`. The legacy
`ptc_standalone_readiness` flat file has a different sliced fibre structure and
must only be used by explicit override.

## Key Changes

- Add a `PyPTC/plotting.py` module using the style of `isis_2024` and `pyorbit_examples`: white figures, dotted grids, mm/mrad phase-space units, shared `s [m]` axes, superperiod tick marks from circumference/10, and compact multi-panel dashboards.
- Keep `DEFAULT_LATTICE` and test defaults on the generated simplified flat
  file, regenerating it when missing.
- Replace the minimal `plot_results()` in `run_misalignment_experiment.py` with calls that write:
  - `twiss_bare.png/.pdf`: `beta_x`, `beta_y`, `D_x`, `D'_x` vs `s`.
  - `closed_orbit_bare_vs_misaligned.png/.pdf`: horizontal and vertical closed orbit in mm, both cases overlaid.
  - `closed_orbit_difference.png/.pdf`: `misaligned - bare` in x/y, in mm.
  - `bunch_dashboard_initial.png/.pdf`, `bunch_dashboard_bare_final.png/.pdf`, `bunch_dashboard_misaligned_final.png/.pdf`: `x-xp`, `y-yp`, `x-y`, `z-dE` density plots with marginal histograms or clear scatter fallback for small particle counts.
  - `bunch_before_after_comparison.png/.pdf`: initial, bare final, and misaligned final overlays in transverse phase space.
- Expose `PTC.particle_diagnostics(...)`:
  - For each input particle, track for `--tune-turns`, transform to entrance
    Twiss-normalized coordinates, accumulate unwrapped phase advance, and
    return `qx`, `qy`, `jx`, `jy`, plus survival/loss flags.
  - Write enriched `*_bunch_diagnostics.csv`, optional `*_tune_footprint.csv`,
    and tune footprint/action/dashboard plots when `--with-tunes` is passed.
- Add a short `PyPTC/docs/PTC_CAPABILITIES.md` documenting:
  - what is exposed cleanly in Python now,
  - what exists only through `ptc_script_`,
  - what remains unexposed and would need future shims.

## CLI Defaults

- Keep the current default experiment: first `SP0_QF`, `dx=0.003`, `particles=100`, `turns=1`.
- Add:
  - `--formats png,pdf`
  - `--with-tunes`
  - `--tune-turns 256`
  - `--min-tune-turns 16`
  - `--tune-case misaligned`, with choices `bare`, `misaligned`, `both`
- If `--with-tunes` is omitted, no tune work is run; the rest of the dashboard still completes.

## Test Plan

- Run `python3 -m py_compile PyPTC/pyptc/*.py PyPTC/scripts/run_misalignment_experiment.py`.
- Run `python3 -m pytest PyPTC/tests/test_aperture_parsers.py PyPTC/tests/test_particle_diagnostics.py -q`.
- Run `python3 PyPTC/tests/test_pyptc_shims.py --particles 1000` and confirm
  Jan26 table application resolves to 38 fibre applications, not 88.
- Run the default experiment and confirm all Twiss/orbit/bunch PNG/PDF outputs are created.
- Run `python3 PyPTC/scripts/run_misalignment_experiment.py --particles 20 --turns 1 --with-tunes --tune-turns 32` as a fast smoke test for exact PTC tune output.
- Confirm `summary.json` records plot paths, tune settings, tune means/stds, and any lost/failed tune particles.

## Assumptions

- Static PNG/PDF is the required output mode.
- New Python-facing Fortran exports, if later needed, belong under
  `PyPTC/fortran/pyptc_api.f90`; do not modify parent `interface/ptcinterface.f90`
  for PyPTC-only APIs.
- Per-particle tune spread means PTC-normalized phase-advance tunes from tracked particles over multiple turns, not FFT-estimated tunes.
- PTC node-level Twiss/orbit remains the plotting source; original element-level orbit is not available unless a separate element metadata export is added later.
