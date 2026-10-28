# Benchmark runner layout smoke

Date: 2026-10-28

This bounded diagnostic checked that the current PyPTC orbit-optics adapter
still launches its worker after the adapter modules were moved out of the
iteration folders into `scripts/python/iteration_0003/`.

The smoke loaded the accepted admission flat file with the current API-level-5
library. It produced 804 node-Twiss rows, read 586 fibres, and parsed 804 PTC
printer groups. The worker resolved to
`scripts/python/iteration_0003/ptc_optics_worker.py`.

The outputs under `target/` are retained for path and subprocess evidence.
This did not run MAD-X or compare optics and is not a benchmark attempt,
user-run assessment, or acceptance.

The full attempt-018 diagnostic remains the evidence for 38-case coverage and
the full EFIELD table. Its manifest records the pre-relocation source paths;
the moves preserved the iteration-0003 adapter module contents, and feedback
0017 records the new paths and hashes.
