# PTC Standalone Readiness Tests

This directory contains the standalone build and runtime checks for the PTC
Fortran library. The tests do not import PyORBIT3 and do not exercise the
future PyORBIT3 `Bunch` wrapper.

## Files

- `inputs/PTC-PyORBIT_flat_file.madx.flt`: MAD-X generated flat file verified
  with this PTC reader.
- `scripts/build_and_smoke_test.sh`: builds `libptc_orbit.so`, checks exported
  symbols, and loads it through Python `ctypes`.
- `scripts/run_clean_ptc_lattice_test.sh`: clears generated outputs, rebuilds,
  initializes PTC with the bundled flat file, samples node/Twiss data, tracks a
  small deterministic particle set through direct Fortran entry points, and
  writes CSV/JSON/PNG outputs.
- `tests/`: Python helpers used by the scripts.

## Quick Run

From the repository root:

```console
python3 -m venv .venv-ptc
source .venv-ptc/bin/activate
python -m pip install -r ptc_standalone_readiness/requirements.txt
ptc_standalone_readiness/scripts/run_clean_ptc_lattice_test.sh
```

Outputs are written to:

```text
ptc_standalone_readiness/outputs/PTC_standalone_outputs/
```

Expected final status:

```json
{
  "build_and_symbol_smoke": "passed",
  "functional_tracking": "passed",
  "normalized_input_exit_code": -1,
  "original_input_exit_code": 0
}
```
