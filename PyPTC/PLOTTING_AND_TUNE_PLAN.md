# PyPTC Plotting And Exact Tune Diagnostics

## Summary

Update `PyPTC` to produce publication-quality static PNG/PDF plots for the standalone ISIS RCS PTC experiment: Twiss functions, bare vs misaligned closed orbit, orbit difference, and before/after bunch dashboards. Add a small Fortran export so Python can request exact PTC-style per-particle tune diagnostics rather than estimating tunes from FFTs.

## Key Changes

- Add a `PyPTC/plotting.py` module using the style of `isis_2024` and `pyorbit_examples`: white figures, dotted grids, mm/mrad phase-space units, shared `s [m]` axes, superperiod tick marks from circumference/10, and compact multi-panel dashboards.
- Replace the minimal `plot_results()` in `run_misalignment_experiment.py` with calls that write:
  - `twiss_bare.png/.pdf`: `beta_x`, `beta_y`, `D_x`, `D'_x` vs `s`.
  - `closed_orbit_bare_vs_misaligned.png/.pdf`: horizontal and vertical closed orbit in mm, both cases overlaid.
  - `closed_orbit_difference.png/.pdf`: `misaligned - bare` in x/y, in mm.
  - `bunch_dashboard_initial.png/.pdf`, `bunch_dashboard_bare_final.png/.pdf`, `bunch_dashboard_misaligned_final.png/.pdf`: `x-xp`, `y-yp`, `x-y`, `z-dE` density plots with marginal histograms or clear scatter fallback for small particle counts.
  - `bunch_before_after_comparison.png/.pdf`: initial, bare final, and misaligned final overlays in transverse phase space.
- Add a small PTC export in `interface/ptcinterface.f90`, exposed through `ctypes` as `PTC.particle_tunes(...)`:
  - For each input particle, use PTC's existing normal-form/closed-orbit machinery, track for `--tune-turns`, transform to normalized coordinates, accumulate phase advance, and return `qx`, `qy`, plus a lost/failed flag.
  - Write `tune_footprint.csv` and `tune_footprint.png/.pdf` when `--with-tunes` is passed.
- Add a short `PyPTC/PTC_CAPABILITIES.md` documenting:
  - what is exposed cleanly in Python now,
  - what exists only through `ptc_script_`,
  - what remains unexposed and would need future shims.

## CLI Defaults

- Keep the current default experiment: first `SP0_QF`, `dx=0.003`, `particles=100`, `turns=1`.
- Add:
  - `--formats png,pdf`
  - `--with-tunes`
  - `--tune-turns 256`
  - `--tune-case misaligned`, with choices `bare`, `misaligned`, `both`
- If `--with-tunes` is omitted, no tune work is run; the rest of the dashboard still completes.

## Test Plan

- Rebuild with `bash PyPTC/build_ptc.sh` and verify the new exported tune symbol is present.
- Run `python3 -m py_compile PyPTC/*.py`.
- Run the default experiment and confirm all Twiss/orbit/bunch PNG/PDF outputs are created.
- Run `python3 PyPTC/run_misalignment_experiment.py --particles 20 --turns 1 --with-tunes --tune-turns 32` as a fast smoke test for exact PTC tune output.
- Confirm `summary.json` records plot paths, tune settings, tune means/stds, and any lost/failed tune particles.

## Assumptions

- Static PNG/PDF is the required output mode.
- Exact tune diagnostics may modify `interface/ptcinterface.f90`; other unrelated directories remain untouched.
- Per-particle tune spread means PTC-normalized phase-advance tunes from tracked particles over multiple turns, not FFT-estimated tunes.
- PTC node-level Twiss/orbit remains the plotting source; original element-level orbit is not available unless a separate element metadata export is added later.
