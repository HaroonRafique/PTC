# Feedback 0005: user-run build symbol check failure

## Attempt identity and outcome

The user ran `./.venv/bin/python ./run_admission.py` from the admission step
directory. The no-argument launcher selected iteration 0002. Attempt
`attempt-20261026T221115Z` is a **user-run failed attempt**, but it did not
reach either lattice engine. The harness tests passed 10/10, the Fortran
library compiled and linked, then `build/build_ptc.sh` stopped while checking
for exported symbol `ptc_init_`. The same build log's symbol inventory includes
`ptc_init_`; no MAD-X reference calculation, PyPTC bootstrap, or lattice smoke
was performed. This is not an admission or physics failure.

The run used the current admission skill `85a897a47b55951552226221dcdbc3b83a8daf71`,
the authorized five-file snapshot at
`1bada6a2ab94edd426c52b7e97a5d335926e0646`, and target checkout commit
`1d872ab`.

| Artifact | SHA-256 |
| --- | --- |
| `report.md` | `7ce4c068325d3b76d750a05f58876c4d0672aba513891a471a4b5f626fe6824e` |
| `result.json` | `487cd3c73bed686fe1f812204b9d1d16eebe1b59141a9d83a08b3cbc4d39824e` |
| `manifest.json` | `dfc7f22228ff6b5f69c3d485f07c9eb6e1759da48c8b17f4a8feda0dde087687` |
| `harness-tests.log` | `8170d02f410c7494e483cd4e380c7943d3b0ce4777fa0c3d4b53dcc11bdf771a` |
| `events.jsonl` | `67ecd57b70af75eb36a59e7bc4d7e51374c4e8afb2b0f818d47e57cebdfe785b` |
| `bootstrap/build.log` | `05c539c54894998bebdecf65212d624043940f798f0b4ca8f129cb68f888e181` |
| source checkout status | `0de8a247d46a968b69d6af0287ad281e892d7e77c524062711ab60cae6565f6a` |

## Diagnosis and fix

The symbol exists in the compiled shared library. The build script searched the
large `nm -D` output by piping `printf` into `grep -q` under `set -o pipefail`.
That check can report failure when the short-circuiting grep closes the pipe
before the producer finishes. Repeated direct runs did not reproduce the false
negative, so the exact timing was not independently reproduced; the build log
does establish that the reported missing symbol was present.

`build/build_ptc.sh` now checks each requested symbol with `awk` over the full
listing, which consumes the complete input. After the change,
`bash build/build_ptc.sh` completed successfully, including all exported-symbol
checks and the ctypes smoke import. The shared library was built, but the
admission attempt was not rerun through MAD-X or PyPTC after this fix.

The review ledger remains `awaiting review` with no acceptance. The older
`attempt-20261026T200601Z` bundle is pruned after its earlier identity and
hashes were recorded in feedback 0003 and its ledger row. Keep the newest three
raw bundles; reassess the next user-run attempt against the current skill.
