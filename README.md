# PTC library

This repository currently supports two separate strands of work around the PTC
Fortran code:

- standalone readiness checks for building/loading PTC and defining the future
  PyORBIT3 integration boundary
- a new standalone Python-level `PyPTC` interface for direct PTC experiments,
  tracking studies, plotting, and benchmarking against PyORBIT3/MADX

It does not build the PyORBIT3 Python extension by itself because the C++
wrapper sources in `interface/` depend on PyORBIT3 headers and runtime types
such as `Bunch`, `orbit_mpi`, and `pyORBIT_Object`.

## Standalone build

Prerequisites: a Fortran compiler supported by Meson, `meson`, and `ninja`.

```console
meson setup build
meson compile -C build
```

This produces:

```text
build/libptc_orbit.so
```

## Standalone smoke test

Run the repo-local readiness script:

```console
ptc_standalone_readiness/scripts/build_and_smoke_test.sh
```

The script configures/compiles the Meson build, checks key exported Fortran
symbols with `nm -D`, and runs a Python `ctypes` smoke test against
the compiled `libptc_orbit.so`. By default it uses `build-standalone/` so it
does not depend on any stale existing `build/` directory.

If a valid PTC lattice/input file is available, pass it through to the smoke
test:

```console
ptc_standalone_readiness/scripts/build_and_smoke_test.sh --ptc-input /path/to/PTC_INPUT
```

Without a real PTC input file, the smoke test deliberately avoids calling
`ptc_init_`; it only proves that the shared library is buildable, loadable from
Python, and exports the symbols expected by a later PyORBIT3 integration.

The exported names are checked with the GNU Fortran naming convention used by
the existing C++ wrapper declarations, for example `ptc_init_`. If this check
fails, inspect what the built library actually exports:

```console
nm -D build-standalone/libptc_orbit.so | grep -i ptc_init
```

If the symbol appears with different decoration, the local Fortran compiler or
flags are not ABI-compatible with the wrapper declarations in `interface/`.

## Clean lattice test with outputs

The repository includes the verified standalone PTC flat file at:

```text
ptc_standalone_readiness/inputs/PTC-PyORBIT_flat_file.madx.flt
```

To clear generated standalone outputs, rebuild from scratch, initialize PTC
with that lattice, sample node/Twiss data, track a small set of direct ctypes
particles, and generate simple plots:

```console
ptc_standalone_readiness/scripts/run_clean_ptc_lattice_test.sh
```

Outputs are written under:

```text
ptc_standalone_readiness/outputs/PTC_standalone_outputs/
```

This is still not PyORBIT3 `Bunch` tracking. It is a standalone readiness test
against the Fortran PTC entry points.
PTC-generated side files, including `Maxwellian_bend_for_ptc.txt`, are also
kept under this output directory.

If the original flat file fails before tracking because a labelled
`PERMFRINGE` logical field uses `0/1`, the script preserves the original
failure evidence and generates a normalized copy under the output directory
with only those labelled fields converted to `F/T`.

## One-directory readiness package

All standalone PTC readiness inputs, scripts, tests, and generated-output
ignore rules live under:

```text
ptc_standalone_readiness/
```

For a clean local run:

```console
python3 -m venv .venv-ptc
source .venv-ptc/bin/activate
python -m pip install -r ptc_standalone_readiness/requirements.txt
ptc_standalone_readiness/scripts/run_clean_ptc_lattice_test.sh
```

Expected final `status.json`:

```json
{
  "build_and_symbol_smoke": "passed",
  "functional_tracking": "passed",
  "normalized_input_exit_code": -1,
  "original_input_exit_code": 0
}
```

## PyPTC standalone Python strand

The `PyPTC/` directory is a separate, additive standalone Python interface to
PTC. It is intended for useful physics studies without PyORBIT3 machinery:
direct PTC tracking, lattice perturbation experiments, plotting diagnostics,
and benchmarking against PTC-PyORBIT3 and MAD-X.

This strand keeps its own Fortran C-ABI shims and Python `ctypes` bindings
under `PyPTC/`; the parent PTC source and the existing PyORBIT3-facing
`interface/` code are not modified.

Build the standalone PyPTC shared library with:

```console
bash PyPTC/build_ptc.sh
```

Run the current shim/API smoke test and plotting workflow with:

```console
python3 PyPTC/tests/test_pyptc_shims.py --output-dir PyPTC/test_outputs/shims
```

The current Python-level API covers:

- machine summary, node Twiss/orbit access, and particle/bunch tracking
- tunes and chromaticities
- deterministic single-element misalignments by lattice index or
  name/occurrence
- aperture/loss-aware tracking
- MAD-X rectangular aperture-file parsing, full ISIS RCS aperture application,
  and queried PTC aperture readback
- initial ramp, cavity, and AC control hooks
- bunch generation through `/home/hr/Codes/pyparticlebunch`

The test workflow writes diagnostic PNG files for Twiss/orbit/tunes/chroma,
bare vs misaligned closed orbit, before/after bunch dashboards, aperture loss
maps, and transverse particle positions at the peak-loss aperture node. The
MAD-X workflow also includes an ISIS RCS aperture comparison that overlays the
design JVT aperture, MAD-X `APER_1/APER_2`, and queried PyPTC per-fibre
apertures in `isis_rcs_aperture_overlay.png`.

Planned extensions for this strand include richer element metadata, normal-form
and map access, family/knob controls, survey/layout transforms, normalized
aperture/tune-smear studies, and per-particle tune-footprint diagnostics where
the underlying PTC state exposes enough information.

See `PyPTC/README.md` for the detailed status, commands, plots, and development
plan.

## PyORBIT3 integration boundary

The variables `cpp_sources`, `dep_inc_dirs`, and `libptc_orbit_dep` remain in
`meson.build` so a future PyORBIT3 build can consume this project as a Meson
subproject. The PyORBIT3-side integration should build `pylibptc_orbit` there,
where the PyORBIT3 core library, headers, and Python extension modules are
available.
