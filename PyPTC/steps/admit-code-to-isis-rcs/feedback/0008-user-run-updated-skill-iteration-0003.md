# Feedback 0008: user run of admission skill iteration 0003

## Attempt and review state

User-run attempt `attempt-20261027T194128Z` used
`admit-code-to-isis-rcs` skill commit
`97e63b1e4ef93aee07deacf09ad9592a223fffe6` (SHA-256
`11c415652fcb053a8f5a2844ae93619ae37ae6dd74e471e67b8801c7b5dddd59`). Its
technical result is `admitted-snapshot`, with ledger disposition still
`awaiting review`. This note records the assessment and learning; it does not
accept the run or widen the prior snapshot-only scope.

The attempt used the authorized five-file `working-copy-snapshot`,
materialized from `isis_2024` tree
`1bada6a2ab94edd426c52b7e97a5d335926e0646`. It loaded the 2023 strength
overlay, selected `synchrotron`, set `a1=b1=kqtd=kqtf=0`, checked the per-cell
trim values, ran one MAD-X TWISS calculation, exported the flat file, and ran
one zero-offset particle for one turn. Eleven harness tests passed. The
reference momentum, beta, kinetic energy, circumference, finite-coordinate,
and loss checks passed. The report, result, manifest, inventory, raw engine
logs, TFS table, flat file, PyPTC API trace, and copied shared library are
retained in the attempt bundle.

Principal evidence hashes:

| Artifact | SHA-256 |
| --- | --- |
| `report.md` | `919cbcd103f95cd2878607c03363ba18ebc5a120e4c781c66c3cbe455ba647f4` |
| `result.json` and `manifest.json` | `4322b799e784a34f527d33f165d63f75bde32ae24052fa68af143fe7c43d56d3` |
| `artifact_digests.csv` | `41238be41c673a8a590f02aaf753881345749fdff41d9bf1f59c689e3c2396c9` |
| `harness-tests.log` | `affa719053c27ba3f18172404091e1cf710f583eb683b19e9a0c7796cd62a346` |
| `madx_work/madx.log` | `f1e7bb2561a97028d050e91384807e941e8aa0dfd0619bd97a29eb2bc740b18a` |
| `pyptc_runtime.log` | `f2e402da57e44da10e666b7df6a905101001b8cace3df785b0b7ad798dadfca1` |
| `madx_work/reference_twiss.tfs` | `b3e6b8855e223245993853b8f17760ead6800b05e223ad93f5ffffd0a37cb9cf` |
| `madx_work/PTC-PyORBIT_flat_file.flt` | `32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a` |

## Assessment against the skill

The attempt establishes a successful, authorized snapshot load and minimal
smoke. It does not establish clean-checkout admission, optics, or benchmark
agreement. The manifest equals the canonical result; the artifact inventory
covers every retained supporting file and its digests match. Engine and API
logs expose the executed recipe and calls. MAD-X's 302 ignored implicit
redefinition warnings and PyPTC's cavity-localization, `DLMAX > LMAX`, and
`ORBIT_WARNING 11` messages remain visible for review.

The local report does not explain the `PTC.machine_summary()` field
`mass_gev ~= 1.0`. Existing PyPTC campaign evidence identifies this field as
raw AMU rather than rest mass in GeV. In this run the generated flat file
contains mass `0.938272013`, MAD-X reports `0.938272046 GeV`, and the
independent momentum, beta, and kinetic-energy checks agree. This is a
reporting/API-field-semantics caveat, not evidence that the proton failed to
load. Carry the unit/meaning caveat into future admission reports.

The successful harness suite has 11 tests but does not test every updated
skill contract. In particular, strengthen checks for scratch-output isolation,
the report's complete warning/reference identity, and report/manifest/result
links to the raw reference log and dirty-state evidence. The recorded
entrypoint command is the interpreter-expanded argv (`/usr/bin/python3
./run_admission.py`); the user invoked the executable shell path directly.
Retaining the shell-facing command as well would make exact invocation
provenance easier to read.

## Post-run comparison: snapshot and default generator

After the independent attempt was complete, the attempt inputs and outputs
were compared with the repository's default simplified-lattice generator and
`tests/test_default_lattice.py`. Four common files are byte-identical. The
default simplified generator loads only the four base files and does not call
`2023.strength`; the admission recipe explicitly calls the overlay. Its
quadrupole scales are non-unity, whereas the default strength file uses unity
scales. The saved flat files both contain 586 fibres and have the same line
count; 270 aligned order-2 multipole rows differ, consistent with those
quadrupole scales. The recipes also differ in calculation path: the admission
recipe runs one MAD-X TWISS, while the default generation script runs
`ptc_twiss` to produce its optimized table.

The user clarified that this default-generator comparison is not an admission
criterion or failure. No default-generator equivalence is claimed or required
for this explicitly approved snapshot recipe. This clarification does not
change the attempt's technical outcome, the unresolved warning record, or its
pending ledger disposition. No transferable shared-skill change is proposed
from the lattice-source distinction itself.

The post-run comparison used
[`tests/test_default_lattice.py`](../../../tests/test_default_lattice.py),
[`generate_flat_file.py`](../../../workflows/madx/generate_flat_file.py),
and [`Create_PTC_flat_file.madx`](../../../workflows/madx/scripts/Create_PTC_flat_file.madx).
It aligns with the evidence provenance and review traceability requirements
in the [evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## Superseded diagnostic evidence retained for pruning history

Iteration 0003 agent diagnostics `attempt-20261027T192342Z` and
`attempt-20261027T192432Z` preceded the artifact-complete run above and are
superseded. Their report/result/inventory hashes are retained in the review
ledger. The first diagnostic (`192342Z`) is removed from the raw bundle under
the three-bundle retention rule after this record; the other two raw
diagnostics remain among the three newest bundles.
