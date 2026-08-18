# Standalone PyPTC Python Library Plan

## Summary

Build a clean Python-level `PyPTC` library that is independent of PyORBIT3, uses `/home/hr/Codes/pyparticlebunch` for bunch generation, and calls PTC through explicit Python APIs. Parent PTC sources are compiled read-only by a PyPTC-local overlay build; all new source files live under `PyPTC`.

## Implemented Foundation

- `PyPTC/meson.build` compiles `libpyptc.so` from parent PTC sources plus PyPTC-owned Fortran API shims.
- `PyPTC/fortran/pyptc_api.f90` contains the first additive `pyptc_*` C ABI symbol.
- `PyPTC/pyptc/` is the new package namespace.
- `PyPTC/pyptc/bunch.py` imports `/home/hr/Codes/pyparticlebunch/src` by default and can be redirected with `PYPARTICLEBUNCH_SRC`.
- `PyPTC/scripts/run_misalignment_experiment.py` now generates bunches through the `pyptc` package and records the PyParticleBunch source path in `summary.json`.

## Next API Phases

- Optics: exact tunes, chromaticity, closed-orbit vector, one-turn map matrix, normal-form data.
- Metadata: element count, element names/types/lengths/positions, node-to-element mapping.
- Lattice control: direct misalignment, multipole, fringe, survey, translate, rotate, and flat-file export APIs.
- Families/knobs: create families, assign multipole knobs, apply tune/chromaticity fitting controls.
- Diagnostics: loss reporting, aperture scans, beam statistics, normalized aperture, tune-smear tracking.
- Benchmarking: PyPTC vs PTC-PyORBIT3 and PyPTC vs MAD-X comparison scripts.

## Validation Commands

- `bash PyPTC/build/build_ptc.sh`
- `python3 -m py_compile PyPTC/*.py PyPTC/pyptc/*.py`
- `python3 PyPTC/scripts/run_misalignment_experiment.py --particles 20 --turns 1 --output-dir PyPTC/artifacts/outputs/pyptc_package_smoke`
