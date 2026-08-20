# PyPTC Example Workflow And Output Refactor

## Summary

Refactor PyPTC so the repo has clear agent rules, no `artifacts/` grouping,
top-level build/test output directories, and numbered user-runnable example
scripts. The examples will build on each other: generate the flat file, plot
bare optics, track a 1000-particle bunch, add apertures/losses, add a single
misalignment, then apply the full Jan26 error table and compare to the existing
`survey_to_lattice` MAD-X Twiss.

## Key Changes

- Add `AGENTS.md` at the PyPTC root with the current rules:
  - Always work from `/home/hr/Codes/PTC/PyPTC`.
  - Do not run normal validation into `/tmp`.
  - Use top-level `build_pyptc/` for the shared library and top-level
    `test_outputs/` for standard generated outputs.
  - User-facing physics checks must be runnable as scripts and produce named PNG
    outputs where plotting is relevant.
  - Use commit style `<type>[<scope>] message`.
  - Preserve unrelated dirty/generated files unless explicitly told otherwise.

- Move generated directories:
  - `artifacts/build-pyptc/` -> `build_pyptc/`.
  - `artifacts/test_outputs/` -> `test_outputs/`.
  - Update `pyptc.DEFAULT_LIBRARY`, build scripts, workflow scripts, README/docs,
    and tests to reference `build_pyptc/libpyptc.so`.
  - Update `.gitignore` so build products remain ignored but curated
    `test_outputs/` PNG/CSV/JSON outputs can be stored consistently.

- Create numbered example scripts under `examples/`:
  - `00_generate_flat_file.py`: generate/update the simplified flat file. No plot
    required.
  - `01_plot_bare_twiss_closed_orbit.py`: load the flat file and plot bare Twiss
    plus bare closed orbit.
  - `02_track_bunch_dashboard.py`: load the flat file, create a 1000-particle
    PyParticleBunch bunch, track it, and write separate before/after dashboard
    PNGs with identical axis limits.
  - `03_track_bunch_with_apertures.py`: copy `02`, add aperture
    loading/comparison, plot PyPTC aperture vs design aperture, track
    deliberately losable particles, and write loss-map plus peak-loss-node
    aperture PNGs.
  - `04_single_element_misalignment.py`: copy `03`, add one deterministic
    single-element misalignment, and write the resulting orbit comparison PNG.
  - `05_full_error_table_orbit_comparison.py`: copy `04`, apply the full Jan26
    error table, plot the PyPTC orbit, and compare against
    `/home/hr/Repositories/survey_to_lattice/03_Standalone/synchrotron_madx_twiss.tfs`.

- Update plotting behavior:
  - Replace the current combined before/after bunch overlay with two separate
    dashboard plots using shared fixed limits.
  - Fold tune footprint and tune-vs-action panels into the 1000-particle
    dashboard output when tune diagnostics are enabled.
  - Stop writing separate tune footprint/tune-vs-action PNGs by default; keep
    CSV tune/action data in the bunch diagnostics.

- Add a top-level runner:
  - `run_examples.sh` runs all numbered examples from the PyPTC root.
  - Each example writes to `test_outputs/<numbered_example_name>/`.
  - The runner fails if required PNGs/JSON/CSV outputs are missing.

## Standard Outputs

- `test_outputs/00_generate_flat_file/`: flat-file generation summary and
  generated flat file copy or manifest.
- `test_outputs/01_plot_bare_twiss_closed_orbit/bare_twiss_closed_orbit.png`.
- `test_outputs/02_track_bunch_dashboard/bunch_initial_dashboard.png`.
- `test_outputs/02_track_bunch_dashboard/bunch_final_dashboard.png`.
- `test_outputs/03_track_bunch_with_apertures/aperture_vs_design.png`.
- `test_outputs/03_track_bunch_with_apertures/loss_map.png`.
- `test_outputs/03_track_bunch_with_apertures/aperture_at_peak_loss_node.png`.
- `test_outputs/04_single_element_misalignment/single_element_orbit_response.png`.
- `test_outputs/05_full_error_table_orbit_comparison/full_error_table_pyptc_orbit.png`.
- `test_outputs/05_full_error_table_orbit_comparison/madx_vs_pyptc_closed_orbit_comparison.png`.

## Test Plan

- Run from PyPTC root:
  - `python3 -m py_compile pyptc/*.py ptc.py scripts/*.py tests/*.py workflows/madx/*.py examples/*.py`
  - `python3 -m pytest tests/test_aperture_parsers.py tests/test_default_lattice.py tests/test_particle_diagnostics.py -q`
  - `bash build/build_ptc.sh`
  - `bash run_examples.sh`

- Validate:
  - `build_pyptc/libpyptc.so` exists and exports expected `pyptc_*` symbols.
  - All examples complete without `/tmp` output paths.
  - `test_outputs/` contains the standard PNGs listed above.
  - Full error-table application uses 38 Jan26 records, not the old sliced
    88-application behavior.
  - The full-error-table comparison uses the selected
    `survey_to_lattice/03_Standalone/synchrotron_madx_twiss.tfs` reference by
    default.

## Assumptions

- Use exact top-level names `build_pyptc/` and `test_outputs/`.
- Put user-facing scripts in `examples/`.
- Keep the generated simplified flat file as the default lattice source;
  examples regenerate it if missing.
- Use `/home/hr/Repositories/survey_to_lattice/03_Standalone/synchrotron_madx_twiss.tfs`
  as the external MAD-X orbit/Twiss reference for the full-error-table
  comparison.
- Keep parser/helper pytest tests, but workflow validation should be through the
  example scripts and their stored PNG outputs.
