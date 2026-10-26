# Admission harness iteration 0002

This attempt harness was reconstructed from the `admit-code-to-isis-rcs`
shared skill at commit `85a897a47b55951552226221dcdbc3b83a8daf71`. It is kept
separate from the earlier harness so this skill application can be reviewed
independently. It reads only the files-only local snapshot described by
`../reference_snapshot/README.md`; it does not require or create a nested Git
repository.

Set up the local, ignored virtual environment once per checkout:

```bash
bash steps/admit-code-to-isis-rcs/setup.sh
```

This creates `steps/admit-code-to-isis-rcs/.venv/` and installs the Python
dependencies. The environment is local and is not committed.

Run focused harness tests with:

```bash
steps/admit-code-to-isis-rcs/.venv/bin/python -m unittest discover \
  -s steps/admit-code-to-isis-rcs/iteration-0002/tests -v
```

Run the attempt with its documented defaults using:

```bash
steps/admit-code-to-isis-rcs/.venv/bin/python \
  steps/admit-code-to-isis-rcs/iteration-0002/run_admission.py
```

The optional flags are:

- `--snapshot-dir`: select the authorized files-only input snapshot.
- `--output-root`: choose where new attempt bundles are created.
- `--library`: select the built `libpyptc.so` shared library.
- `--madx`: select the MAD-X executable.
- `--attempt-id`: set a unique attempt directory name; existing nonempty bundles
  are not overwritten.

Each attempt copies the five inputs
and source status evidence into its own output before the bootstrap or engines
run. It builds PyPTC, records a library-load/API-level bootstrap without an
ISIS lattice, performs the single authorized MAD-X TWISS calculation and flat
file export, then exercises public PyPTC load, machine/readback and one-turn
zero-offset particle APIs. It retains both MAD-X and native PyPTC runtime logs
and summarizes relevant warning classes without treating warning absence as
acceptance. Attempt outputs go to
`test_outputs/admit-code-to-isis-rcs/<attempt-id>/`.
The command prints report, result and manifest paths. It exits `0` for technical
`admitted-snapshot`, `2` for a blocked precondition, and `1` for an execution
failure. The report records the measured values and units where applicable; the
runner does not modify the reviewed ledger.

The runner reports technical success only as `admitted-snapshot`, pending
external review. It never edits or accepts a ledger row. Optics and benchmarking
are outside this step.
