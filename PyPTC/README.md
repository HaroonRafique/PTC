# PyPTC

PyPTC is a standalone Python-facing wrapper around this repository's PTC
Fortran source.  It is intentionally kept under `PyPTC/` so the parent PTC
source and existing PyORBIT-facing interface can remain unchanged.

The current build creates `libpyptc.so` from the existing PTC sources plus an
additive shim file, `PyPTC/fortran/pyptc_api.f90`.  Python calls the library
through `ctypes` in `PyPTC/pyptc/`.

## Directory Layout

- `pyptc/`: importable Python package.
- `fortran/`: additive Fortran C-ABI shim source.
- `build/`: build commands and helpers.
- `scripts/`: standalone user-facing Python scripts.
- `tests/`: smoke and regression tests.
- `workflows/madx/`: MAD-X binaries, lattice inputs, flat-file generation, and
  MAD-X/PyPTC comparison scripts.
- `docs/`: planning notes and capability summaries.
- `artifacts/`: ignored generated builds, plots, CSV files, and test outputs.

## What Is Implemented

- Standalone build script: `./PyPTC/build/build_ptc.sh`
- Python package entry point: `PyPTC/pyptc/`
- Backward-compatible import shim: `PyPTC/ptc.py`
- ISIS RCS default flat-file lattice support
- Bunch generation through `/home/hr/Codes/pyparticlebunch`
- Existing PyORBIT-style PTC tracking wrappers:
  - initialise lattice
  - read/run PTC command files
  - read machine summary
  - read node Twiss/orbit values
  - track particles and bunch arrays
- New direct PyPTC ABI shims:
  - `tunes()`
  - `chromaticities()`
  - deterministic fibre misalignment by index or name/occurrence
  - MAD-X `ESAVE`/`EFIELD` error-table parsing and application
  - per-fibre aperture setup/disable
  - MAD-X rectangular aperture-file parsing, full-lattice aperture application,
    and per-fibre PTC aperture readback
  - global absolute aperture getter/setter
  - loss-aware ring tracking
  - acceleration, ramping, modulation, and cavity state toggles
  - orbit state store/use
  - orbit time and lattice energisation
  - cavity table, cavity power, and cavity totalpath controls
  - AC magnet and ramp magnet configuration hooks

The ABI shims use the active PTC lattice loaded by `ptc_init_`; no script files
are required for these new calls.

## Basic Usage

Build the standalone shared library:

```bash
bash PyPTC/build/build_ptc.sh
```

Run the current smoke/physics test and generate diagnostic plots:

```bash
python3 PyPTC/tests/test_pyptc_shims.py --output-dir PyPTC/artifacts/test_outputs/shims
```

Generate a fresh ISIS RCS simplified-lattice PTC flat file with the bundled
MAD-X binary, then run the repeatable PyPTC smoke comparison:

```bash
python3 PyPTC/workflows/madx/generate_flat_file.py
python3 PyPTC/workflows/madx/run_generated_flatfile_smoke.py
```

Or run the full build/generate/test sequence:

```bash
bash PyPTC/workflows/madx/run_all.sh
```

Compare MAD-X and PyPTC closed orbits after applying the same bundled
misalignment table to the simplified lattice:

```bash
python3 PyPTC/workflows/madx/compare_madx_pyptc_closed_orbits.py
```

Scan each MAD-X error-table component independently, including raw PTC and
PyPTC-only sign-flip checks:

```bash
python3 PyPTC/workflows/madx/scan_misalignment_components.py
```

Regenerate the ISIS RCS aperture lattice, apply `ISIS.aperture` through PyPTC,
query the stored PTC aperture state, and compare design JVT, MAD-X, and PyPTC
half apertures:

```bash
python3 PyPTC/workflows/madx/compare_isis_apertures.py
```

The MAD-X workflow writes generated files and plots under
`PyPTC/workflows/madx/outputs/`; the main comparison uses
`simplified_closed_orbit_comparison/`, and the component/sign scan uses
`cscan/`.  The aperture comparison uses `aperture_comparison/` and writes
`isis_rcs_aperture_overlay.png`. The bundled MAD-X binaries are intentionally
tracked in git so a new checkout can reproduce the flat-file generation without
finding an external MAD-X installation.

Use from Python:

```python
from pyptc import DEFAULT_LATTICE, PTC

ptc = PTC()
ptc.init_lattice(DEFAULT_LATTICE)

print(ptc.machine_summary())
print(ptc.tunes())
print(ptc.chromaticities())

fibre_index = ptc.set_misalignment_by_name("SP0_QF", occurrence=1, dx=0.003)
ptc.update_twiss()

applied = ptc.apply_madx_error_table(
    "PyPTC/workflows/madx/reference_errors/jan26_survey_corrected.tfs"
)
ptc.update_twiss()

ptc.set_aperture(fibre_index, kind=2, x=0.005, y=0.005)
ptc.set_absolute_aperture(0.005)
coords, loss = ptc.track_particle_ptc_with_loss([0.004, 0, 0, 0, 0, 0], turns=1)

applied_apertures = ptc.apply_madx_aperture_file(
    "PyPTC/workflows/madx/lattices/02_Aperture_Lattice/ISIS.aperture"
)
queried_apertures = ptc.all_fibre_apertures()
```

For reproducible offline studies, `PyPTC/scripts/flatfile_misalign.py` can also
write a copied flat file containing either one manual six-degree-of-freedom
misalignment or every nonzero row from a MAD-X error table.  The old
`PyPTC/flatfile_misalign.py` path remains as a small compatibility wrapper.

```bash
python3 PyPTC/scripts/flatfile_misalign.py \
  --input ptc_standalone_readiness/inputs/PTC-PyORBIT_flat_file.madx.flt \
  --output PyPTC/artifacts/outputs/isis_with_jan26_survey_errors.flt \
  --madx-error-table PyPTC/workflows/madx/reference_errors/jan26_survey_corrected.tfs
```

## MAD-X Flat-File Generation

`PyPTC/workflows/madx/` contains the reproducible ISIS RCS flat-file generation
strand:

- `bin/` contains the committed ISIS MAD-X binaries; the default is
  `madx-linux64_v5_02_00`, matching the PyORBIT flat-file-generation example.
  The newer 5.06 binary is included for comparisons, but its generated flat
  file is not currently accepted by the PTC reader used here.
- `lattices/00_Simplified_Lattice/` is copied from
  `/home/hr/Repositories/isis_2024/Lattice_Files/00_Simplified_Lattice`.
- `ptc_scripts/` is copied from the PyORBIT MAD-X flat-file example.
- `scripts/Create_PTC_flat_file.madx` is the PyPTC-adapted flat-file generator.
- `reference_errors/jan26_survey_corrected.tfs` is copied from the latest
  survey-to-lattice reference output.

The repeatable smoke script regenerates `PTC-PyORBIT_flat_file.flt`, loads it
through PyPTC, applies the full reference MAD-X error table, and asserts that
the bare orbit is near zero while the misaligned orbit response is measurable.
The comparison script also runs a native MAD-X bare/misaligned `TWISS` pair and
writes `madx_vs_pyptc_closed_orbit_comparison.png`.

## Diagnostic Plots

The shim smoke test writes PNGs and CSVs under its output directory.  The plots
currently include:

- `01_ptc_twiss_orbit_tunes_chroma.png`
  - beta, alpha, dispersion, closed orbit, tunes, and chromaticities
- `02_closed_orbits_bare_vs_misaligned.png`
  - bare and single-quad-misaligned closed orbits
- `03_bunch_dashboard_before_after_tracking.png`
  - PyORBIT-style bunch dashboard
- `04_aperture_loss_map.png`
  - lost-particle count versus lattice position `s`
- `05_aperture_at_peak_loss_node.png`
  - rectangular aperture and particle positions at the node with most losses
- `06_madx_error_table_misalignments.png`
  - translations and rotations from the latest survey-to-lattice MAD-X table
- `07_closed_orbit_bare_vs_madx_error_table.png`
  - bare closed orbit compared with the orbit after applying the full table
- `workflows/madx/outputs/aperture_comparison/isis_rcs_aperture_overlay.png`
  - design JVT, MAD-X, and queried PyPTC rectangular half apertures

The dashboard follows the layout used in
`/home/hr/Repositories/pyorbit_examples/03_PTC_PyORBIT_Examples/.../pyorbit_bunch_dashplotter.py`.
PyPTC does not yet expose per-particle tune footprints, so the tune panels use
the lattice tune marker and action correlations for now.

## Notes And Current Limits

- Name-based lattice edits are resolved in Python from the PTC flat file, then
  applied through index-based Fortran shims.  This avoids fragile Fortran C
  string handling in the first implementation.
- MAD-X error-table support reads the same `NAME, DX, DY, DS, DPHI, DTHETA,
  DPSI` columns used by `READMYTABLE`/`SETERR`; values are passed to PyPTC in
  MAD-X units, metres and radians.
- The tune getter currently returns useful transverse 4D/no-cavity tunes for
  the ISIS RCS case.  Synchrotron tune is returned as `0.0` unless the PTC
  normal form provides it.
- Loss-aware tracking reports losses from PTC stability/aperture state and
  from the exposed absolute-aperture check.
- Per-particle phase/tune attributes like PyORBIT's `ParticlePhaseAttributes`
  are not exposed yet.
- The full MAD-X `APERTURE` command was too slow for the repeatable full-ring
  aperture overlay, so `compare_isis_apertures.py` writes the MAD-X comparison
  table from `TWISS` columns `APER_1/APER_2`.

## Planned Next Work

- Per-particle phase advance and tune-footprint/tune-spread tracking.
- Direct element metadata from PTC rather than flat-file parsing.
- Family and knob controls for tune/chromaticity matching.
- Direct normal-form and one-turn-map access.
- Richer aperture model export beyond the current rectangular/conformal ISIS
  workflow, including element-specific shape metadata for other aperture types.
- Survey/layout transforms.
- Normalized aperture and tune-smear scans.
