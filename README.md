# PTC library

This repository currently builds the PTC Fortran code as a standalone shared
library. It does not build the PyORBIT3 Python extension by itself because the
C++ wrapper sources in `interface/` depend on PyORBIT3 headers and runtime
types such as `Bunch`, `orbit_mpi`, and `pyORBIT_Object`.

## Standalone build

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

If the original flat file uses `0/1` for the labelled `PERMFRINGE` logical
field, the script preserves the original failure evidence and generates a
normalized copy under the output directory with only those labelled fields
converted to `F/T`.

The most useful currently verified external flat-file baseline from the local
PyORBIT examples is the MAD-X generated file:

```text
/home/hr/Repositories/pyorbit_examples/03_PTC_PyORBIT_Examples/00_Create_PTC_Flat_File/Via_MAD-X/PTC-PyORBIT_flat_file.flt
```

That file is copied into `ptc_standalone_readiness/inputs/` so the readiness
test no longer depends on an external checkout.

This file passes the standalone `ptc_init_`/node sampling/direct ctypes
particle-tracking test in this repository. The local bundled `.flt` is
byte-identical to the `Via_cpymad` example and remains useful as failure
evidence for flat-file parser compatibility, not as the preferred readiness
baseline.

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

## PyORBIT3 integration boundary

The variables `cpp_sources`, `dep_inc_dirs`, and `libptc_orbit_dep` remain in
`meson.build` so a future PyORBIT3 build can consume this project as a Meson
subproject. The PyORBIT3-side integration should build `pylibptc_orbit` there,
where the PyORBIT3 core library, headers, and Python extension modules are
available.
