# PyPTC

PyPTC is a standalone Python-facing wrapper around this repository's PTC
Fortran source.  It is intentionally kept under `PyPTC/` so the parent PTC
source and existing PyORBIT-facing interface can remain unchanged.

The current build creates `libpyptc.so` from the existing PTC sources plus an
additive shim file, `PyPTC/fortran/pyptc_api.f90`.  Python calls the library
through `ctypes` in `PyPTC/pyptc/`.

## What Is Implemented

- Standalone build script: `./PyPTC/build_ptc.sh`
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
  - per-fibre aperture setup/disable
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
bash PyPTC/build_ptc.sh
```

Run the current smoke/physics test and generate diagnostic plots:

```bash
python3 PyPTC/tests/test_pyptc_shims.py --output-dir PyPTC/test_outputs/shims
```

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

ptc.set_aperture(fibre_index, kind=2, x=0.005, y=0.005)
ptc.set_absolute_aperture(0.005)
coords, loss = ptc.track_particle_ptc_with_loss([0.004, 0, 0, 0, 0, 0], turns=1)
```

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

The dashboard follows the layout used in
`/home/hr/Repositories/pyorbit_examples/03_PTC_PyORBIT_Examples/.../pyorbit_bunch_dashplotter.py`.
PyPTC does not yet expose per-particle tune footprints, so the tune panels use
the lattice tune marker and action correlations for now.

## Notes And Current Limits

- Name-based lattice edits are resolved in Python from the PTC flat file, then
  applied through index-based Fortran shims.  This avoids fragile Fortran C
  string handling in the first implementation.
- The tune getter currently returns useful transverse 4D/no-cavity tunes for
  the ISIS RCS case.  Synchrotron tune is returned as `0.0` unless the PTC
  normal form provides it.
- Loss-aware tracking reports losses from PTC stability/aperture state and
  from the exposed absolute-aperture check.
- Per-particle phase/tune attributes like PyORBIT's `ParticlePhaseAttributes`
  are not exposed yet.

## Planned Next Work

- Per-particle phase advance and tune-footprint/tune-spread tracking.
- Direct element metadata from PTC rather than flat-file parsing.
- Family and knob controls for tune/chromaticity matching.
- Direct normal-form and one-turn-map access.
- Richer aperture model export, including element-specific shape metadata.
- Survey/layout transforms.
- Normalized aperture and tune-smear scans.

