# PyPTC Capability Surface

## Current Python APIs

- `pyptc.PTC`: loads `PyPTC/build-pyptc/libpyptc.so`.
- Lattice initialization from a PTC flat file.
- Machine summary: node count, harmonic number, circumference, transition gamma, mass, charge, kinetic energy.
- Synchronous-particle scalars: `omega`, `p0c`, `beta0`, kinetic energy through the legacy scalar functions.
- Node-level Twiss and closed orbit through `ptc_get_twiss_for_node_`.
- Particle and bunch tracking using the same coordinate convention as PyORBIT3:
  - Python/PyParticleBunch: `x, xp, y, yp, z, dE`.
  - PTC call: `x, xp, y, yp, pt=dE/p0c, ct=-z/beta0`.
- `pyptc.generate_matched_gaussian_4d`: bunch generation through the existing `/home/hr/Codes/pyparticlebunch` repo.

## Current Build Model

- `PyPTC/meson.build` is a PyPTC-local overlay build.
- It compiles parent `source/*.f90` and `interface/ptcinterface.f90` read-only.
- New additive Python-facing Fortran exports live under `PyPTC/fortran/`.
- `PyPTC/build_ptc.sh` builds `PyPTC/build-pyptc/libpyptc.so` and verifies both legacy `ptc_*` and new `pyptc_*` symbols.

## PTC Functionality Present Internally But Not Yet Cleanly Exposed

These features exist in PTC internals and/or the `read_ptc_command` script-command surface, but still need explicit `pyptc_*` Fortran ABI wrappers before they are first-class Python APIs:

- Exact tune and chromaticity getters.
- Normal-form and map access.
- Element and integration-node metadata beyond the current node Twiss table.
- Direct lattice editing: multipoles, misalignments, fringe flags, flat-file import/export.
- Family and knob controls.
- Aperture, loss, and lost-particle reporting.
- Beam allocation/statistics tools from PTC's internal beam machinery.
- Ramp, AC magnet, cavity, acceleration, and timing controls.
- Survey, layout translation, layout rotation, and patch transforms.
- Normalized aperture and tune-smear tracking.

## Implementation Rule

Do not expose new features by generating temporary PTC script files as the main interface. Add focused `pyptc_*` ABI routines in `PyPTC/fortran/`, wrap them in `PyPTC/pyptc/`, and keep parent repo files unchanged unless explicitly approved.
