# PyPTC Capability Surface

## Current Python APIs

- `pyptc.PTC`: loads `PyPTC/build_pyptc/libpyptc.so`.
- Lattice initialization from a PTC flat file; `DEFAULT_LATTICE` is the
  generated simplified ISIS file under `workflows/madx/outputs/simplified/`.
- Machine summary: node count, harmonic number, circumference, transition gamma, mass, charge, kinetic energy.
- Synchronous-particle scalars: `omega`, `p0c`, `beta0`, kinetic energy through the legacy scalar functions.
- Node-level Twiss and closed orbit through `ptc_get_twiss_for_node_`.
- Node-level horizontal/vertical phase-advance curves through the additive
  `pyptc_get_node_phase_advances` ABI shim.  They are unwrapped cumulative
  phases in turns, obtained from the normal-form cosine/sine basis with
  `atan2`; their fractional parts agree with `pyptc_get_tunes`.
- Exact tune/chromaticity getters through `pyptc_get_tunes` and
  `pyptc_get_chromaticities`.
- Name-based and index-based misalignment application:
  - raw PTC convention through `set_misalignment(...)`
  - MAD-X convention through `set_madx_misalignment(...)`
  - MAD-X `ESAVE`/`EFIELD` table import through `apply_madx_error_table(...)`:
    alignment fields plus integrated normal/skew magnetic multipoles
    `K0L..K20L` and `K0SL..K20SL`
  - direct integrated multipole additions through `add_madx_multipole_error(...)`
  - unsupported nonzero EFIELD columns are rejected before lattice mutation
- Rectangular aperture and loss tools:
  - set/disable one fibre aperture
  - read MAD-X `APERTYPE=RECTANGLE, APERTURE={half_x, half_y}` files
  - apply a full MAD-X aperture assignment file from Python
  - query per-fibre aperture metadata back from PTC
  - one-particle and bunch tracking with loss flags, turn, and lattice position
- Per-particle tune/action/survival diagnostics:
  - track each particle turn-by-turn through the active PTC lattice
  - compute transverse actions and tunes from entrance Twiss-normalized,
    unwrapped phase advance
  - preserve lost-particle flags and exclude invalid/lost particles from
    survivor tune statistics
  - write enriched bunch diagnostic CSVs and tune-footprint/action plots through
    `run_misalignment_experiment.py --with-tunes`
- Ramp, AC magnet, cavity, acceleration, modulation, timing, and orbit-state
  controls through focused `pyptc_*` ABI wrappers.
- Particle and bunch tracking helpers accept the Python/PyParticleBunch row
  `x, xp, y, yp, z, dE`, where `dE` is total-energy deviation. The helper
  converts it to PTC's default-state relative momentum deviation
  `delta=p/p0-1` using the exact relativistic energy-momentum relation and the
  current synchronous `p0c` and `beta0`; it converts the tracked `delta` back
  to `dE` on return. The longitudinal mapping remains `L=-z/beta0`.
- `track_particle_ptc()` and `track_particle_ptc_with_loss()` are low-level
  interfaces: their six values are passed to PTC without Python/PyParticleBunch
  coordinate conversion. Callers must supply coordinates for the active PTC
  state themselves.
- `pyptc.generate_matched_gaussian_4d`: bunch generation through the existing `/home/hr/Codes/pyparticlebunch` repo.
- ISIS RCS MAD-X interoperability workflows under `PyPTC/workflows/madx/`:
  - regenerate simplified and aperture-lattice PTC flat files with bundled
    MAD-X binaries
  - compare MAD-X and PyPTC closed orbits under the same error table
  - compare design JVT, MAD-X, and queried PyPTC apertures.

## Current Build Model

- `PyPTC/meson.build` is a PyPTC-local overlay build.
- It compiles parent `source/*.f90` and `interface/ptcinterface.f90` read-only.
- New additive Python-facing Fortran exports live under `PyPTC/fortran/`.
- `PyPTC/build/build_ptc.sh` builds `PyPTC/build_pyptc/libpyptc.so` and verifies both legacy `ptc_*` and new `pyptc_*` symbols.
- Tests and smoke scripts generate `workflows/madx/outputs/simplified/PTC-PyORBIT_flat_file.flt`
  when the default lattice is missing.

## PTC Functionality Present Internally But Not Yet Cleanly Exposed

These features exist in PTC internals and/or the `read_ptc_command` script-command surface, but still need explicit `pyptc_*` Fortran ABI wrappers before they are first-class Python APIs:

- Normal-form and map access.
- Element and integration-node metadata beyond the current node Twiss table.
- Direct lattice editing beyond the current misalignment, magnetic multipole,
  and aperture shims: electric/RF multipole data, fringe flags, flat-file
  import/export, element insertion/removal.
- Family and knob controls.
- Beam allocation/statistics tools from PTC's internal beam machinery.
- Survey, layout translation, layout rotation, and patch transforms.
- Normalized aperture scans.

## ISIS RCS Aperture Workflow

`PyPTC/workflows/madx/compare_isis_apertures.py` executes the aperture plan:

- copies are kept under `PyPTC/workflows/madx/lattices/02_Aperture_Lattice`
  and `PyPTC/workflows/madx/reference_apertures`
- `generate_flat_file.py --lattice aperture` runs MAD-X, writes
  `madx_aperture.tfs`, and generates a PTC flat file
- PyPTC reads `ISIS.aperture`, applies each rectangular aperture to matching
  PTC fibres with `kind=2`, `x=half_x`, `y=half_y`
- the new `pyptc_get_one_aperture` shim queries the stored PTC aperture state
- outputs are written below `PyPTC/workflows/madx/outputs/aperture_comparison/`,
  including `isis_rcs_aperture_overlay.png`

The aperture values are rectangular/conformal half apertures in metres inside
PyPTC and are plotted in millimetres for inspection.

## Implementation Rule

Do not expose new features by generating temporary PTC script files as the main interface. Add focused `pyptc_*` ABI routines in `PyPTC/fortran/`, wrap them in `PyPTC/pyptc/`, and keep parent repo files unchanged unless explicitly approved.
