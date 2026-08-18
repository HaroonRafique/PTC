# PyPTC ISIS RCS Aperture Implementation Plan

## Summary

Add a reproducible PyPTC aperture workflow using the ISIS `02_Aperture_Lattice`
and the existing PyORBIT aperture example as references. The goal is to assign
rectangular, conformal ISIS RCS apertures directly in PTC from Python, query the
resulting PTC state, and compare it against the design JVT aperture and MAD-X
aperture output.

The final diagnostic should be one overlay plot with two subplots:

- Horizontal half aperture vs `s`
- Vertical half aperture vs `s`

Each subplot should overlay:

- Design JVT aperture
- MAD-X aperture output
- PyPTC queried aperture

## Key Changes

- Copy the aperture lattice/data into `PyPTC/workflows/madx/` only:
  - Copy `/home/hr/Repositories/isis_2024/Lattice_Files/02_Aperture_Lattice`
    into `PyPTC/workflows/madx/lattices/02_Aperture_Lattice`.
  - Copy or reference the design aperture CSV from
    `/home/hr/Repositories/isis_2024/Methods/Aperture/jvt_synch_aperture.csv`.
  - Generate fresh MAD-X aperture output from the copied lattice rather than
    relying only on stale reference files.
- Extend flat-file generation:
  - Add a `--lattice aperture` option to `PyPTC/workflows/madx/generate_flat_file.py`.
  - Use an aperture-aware MAD-X script that calls `ISIS.aperture`, writes a
    `madx_aperture.tfs` table containing `APER_1/APER_2`, and generates the
    PTC flat file.
- Add PyPTC aperture APIs:
  - Parse MAD-X aperture assignment files containing
    `APERTYPE=RECTANGLE, APERTURE={half_x, half_y}`.
  - Apply all rectangular apertures to PTC with `kind=2`, `x=half_x`,
    `y=half_y`, `dx=0`, and `dy=0`.
  - Add a Fortran/C shim to query per-fibre aperture metadata from PTC so the
    comparison uses actual PTC state, not just the requested input table.
  - Add Python methods such as `get_aperture(fibre_index)`,
    `all_node_apertures()`, and `apply_madx_aperture_file(path)`.

## Drift Behavior

MAD-X appears not to allow aperture definitions directly on drifts, but PTC's
low-level `assign_one_aperture` routine accepts a fibre index and does not
obviously special-case drifts. The implementation should include a drift probe:

- Assign a deliberately tight rectangular aperture to a drift fibre.
- Query PTC to confirm the aperture metadata is stored.
- Track boundary particles through that drift or around the ring to verify
  whether PTC enforces the drift aperture in tracking.

If PTC accepts and enforces drift apertures, apply apertures to every drift as
well. If PTC stores but does not enforce drift apertures, document that behavior
and still expose the queried metadata. Do not skip drifts in PyPTC unless the
PTC tracking check proves they are not meaningful.

## Comparison Script

Add a repeatable script under `PyPTC/workflows/madx/`, for example
`compare_isis_apertures.py`. It should:

- Generate or load the aperture lattice flat file.
- Run MAD-X with the aperture lattice and parse `APER_1` and `APER_2`.
- Parse the design JVT CSV using `Semi_Ap_H` and `Semi_Ap_V`, converting mm to m.
- Apply `ISIS.aperture` to every matching PTC fibre.
- Query PTC aperture state for every fibre and write `pyptc_apertures.csv`.
- Save `isis_rcs_aperture_overlay.png`.

Name matching should normalize case and strip MAD-X occurrence suffixes such as
`:1`. Missing aperture assignments for PTC fibres should be reported in a CSV
summary.

Implementation note: the first full-ring attempt using the MAD-X `APERTURE`
command was much slower than needed for this comparison. The implemented
workflow writes `madx_aperture.tfs` from a MAD-X `TWISS` table containing
`APER_1/APER_2`, which gives the same rectangular aperture half-widths needed
for the overlay and keeps the test repeatable.

## Test Plan

- Run the existing PyPTC shim tests to check for regressions.
- Add parser coverage for `ISIS.aperture` rectangle lines.
- Add a PTC set/get test for one quadrupole and one drift.
- Add a full-lattice application test asserting matched PTC fibres receive
  `kind=2` rectangular apertures.
- Add a drift probe test using a deliberately tight drift aperture and boundary
  particles.
- Add an end-to-end comparison script test that creates:
  - `madx_aperture.tfs`
  - `pyptc_apertures.csv`
  - `isis_rcs_aperture_overlay.png`

## Acceptance Criteria

- PyPTC queried apertures agree with the applied MAD-X aperture file to
  numerical precision for matched elements.
- MAD-X and design aperture curves are plotted on the same `s` scale.
- Any missing or unmatched elements are listed explicitly.
- Rectangular apertures are plotted as half-widths, not rotated polygons or
  ellipse proxies.

## Assumptions

- Use `02_Aperture_Lattice` as the authoritative lattice for this task because
  it contains the split elements and aperture assignments.
- Use PTC `kind=2` as the rectangular aperture model.
- Treat aperture values as half apertures in metres inside PyPTC.
- Keep all new files and copied references under `PyPTC/`; do not modify
  `isis_2024`, `pyorbit_examples`, or other repository directories.
