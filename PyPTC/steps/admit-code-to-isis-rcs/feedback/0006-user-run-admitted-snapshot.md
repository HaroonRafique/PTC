# Feedback 0006: user-run admission against the current skill

## Attempt identity and outcome

Attempt `attempt-20261027T082315Z` is a user-run skill-test attempt using
admission skill commit `85a897a47b55951552226221dcdbc3b83a8daf71` (SHA-256
`ca7457645d0fe9049e7b55c50fc3b035b4db771bdb5984c6ab662cbe3cfbf35f`). It
completed with technical outcome `admitted-snapshot`; disposition remains
`awaiting review`. It is not clean-checkout admission or reviewed acceptance.

The source working copy was revision
`823e6c08dfa79a182548b07706b3d46f0157137a` with 206 dirty entries. As
previously authorized, MAD-X used only the five hash-identified direct inputs
materialized from the pinned `isis_2024` tree at
`1bada6a2ab94edd426c52b7e97a5d335926e0646`; dirty working-tree contents were
not used. The full status is retained in the bundle. The recipe used the
simplified ISIS RCS input with `2023.strength`, `synchrotron`,
`a1=b1=kqtd=kqtf=0`, and one TWISS calculation. The raw MAD-X log echoes all
five input calls, the selected sequence and effective zero settings, one saved
TWISS command, and the PTC flat-file export scripts.

| Artifact | SHA-256 |
| --- | --- |
| `report.md` | `25dc766a3a0ae276cb05fd7c8433f02b85570eb250771b4de46205c68ee2d790` |
| `result.json` | `4278eb6fa19630fe0fb2c2155174b5146f351f9deca267da67eecd43a4943e83` |
| `manifest.json` | `98abb12582f40d621332ae8d21f7762ff729afab3c83bc28d7dff234913a286e` |
| `harness-tests.log` | `153edc57ba807b8977e83b8752f94e3e0c8a813631caf1f79e4e5cdd632dca87` |
| `madx_work/madx.log` | `abf52d5b5da1527f7bf76f72938627ab8ef4d0c8d6fc01e175b448a42905c47b` |
| `pyptc_runtime.log` | `9044cb0b247391a198219302f68d2bec8af617b515d279375cd43a7bf2ecb70a` |
| `pyptc_api_trace.jsonl` | `bd179ae86e9196b557c143a25fad79fb66676786d706c0b52c9fa501db99e8df` |
| source status | `0de8a247d46a968b69d6af0287ad281e892d7e77c524062711ab60cae6565f6a` |
| flat file | `32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a` |
| raw reference TFS | `ae7c3867fcf194262a13ddf8f8746d312c1a4309ee86e9a2a1b25caf72faa803` |
| normalized TFS fingerprint | `d5dd3f8155590e0746a5d340d3dc8e3e21c4e0fb7f4b92d822f5c3e7784c1343` |
| `Maxwellian_bend_for_ptc.txt` | `5b6eb35b988369bbd73997584c6a625e02270c9083f4f9a73772f9a070ad179b` |
| `events.jsonl` | `9e8166df1b0b3f65aad4b314fa4d713b72900c7be6ab8301a67cceb5f70fd4a5` |
| `warning_summary.json` | `a239f415ca8e73b27978c69631766c625b4c2262c84d93e45c1a40e1d2ee9856` |

## Assessment against the pinned skill

The run satisfies the central snapshot-admission evidence chain: user-authorized
snapshot mode; retained dirty-state status and source identity; stable logical
input hashes; approved recipe and execution order; locally constructed,
no-lattice PyPTC bootstrap with API level 4; passing 10-test harness suite;
actual build, MAD-X and PyPTC commands/logs; structural import evidence;
reference-particle comparison; one-turn smoke and explicit loss policy; warning
summary; nonclaims; and separate pending-review ledger state.

The machine summary reports 375 PyPTC nodes and 586 flat-file fibre records,
circumference `163.36281999999989 m`, charge `+1`, and ring harmonic 71. The
586 count agrees with the existing default-lattice structural test, but this
attempt used the explicitly authorized files-only recipe, not the default
generator. `a1`, `b1`, `kqtd`, `kqtf`, all per-element trim values, and the base
D/F harmonic assignments checked by the harness were zero. The reference
particle comparison passed: MAD-X `pc=0.37033168 GeV/c`, PyPTC
`p0c=0.370331763608763 GeV/c`, difference `8.36e-8 GeV/c` within the recorded
`2e-7 GeV/c` tolerance. Kinetic energy passed its `2e-6 GeV` tolerance. The
raw PyPTC mass-summary field is not treated as authoritative. A zero-offset
particle completed one turn with finite coordinates and no reported loss.

The run retains 302 MAD-X warnings classified as ignored implicit element
redefinitions and three unresolved PyPTC messages: cavity-frequency
localization, `DLMAX > LMAX 0.5144`, and `ORBIT_WARNING 11`. No structural or
reference-particle discrepancy is apparent in this run, but the PyPTC warning
meanings still need human review. The result therefore stays pending review.
No optics, long-term tracking, collective-effects, or benchmark evidence was
generated.

The following skill-conformance issues remain visible for improvement:

- The report's `installation_method` says
  `bash build/build_ptc.sh builds build_pyptc/libpyptc.so`, while the manifest's
  actual command and event log show `bash build/build_ptc.sh` with no
  positional arguments. Use the recorded command as the executed fact and
  reconcile the descriptive field before the next fresh attempt.
- The bundle hashes the principal inputs, flat file, TWISS table, harness log,
  build/bootstrap logs, MAD-X/PyPTC logs and API trace. The separately retained
  `Maxwellian_bend_for_ptc.txt`, `events.jsonl`, and `warning_summary.json` do
  not have linked digests in the canonical result. The skill asks for digests
  of retained raw outputs; consider adding an artifact-hash inventory while
  keeping self-referential report/result/manifest files out of that inventory.
- The ten tests still do not cover every case specified by the skill: canonical
  result omission of resolved defaults, snapshot immutability and scratch
  isolation, duplicate final fields, and review-facing output from an accepted
  ledger row. These were also noted in feedback 0003; the current passing test
  count does not close those coverage gaps.
- The PyPTC runtime warnings remain unresolved; review should establish their
  expectedness or whether they indicate an issue in this minimal setup before
  treating the snapshot as accepted.

## Post-run comparison with PyPTC examples/tests

Existing PyPTC material was used only after the independent run. The fibre
count matches the 586-record check in `tests/test_default_lattice.py`; the
current attempt did not exercise its default lattice-generation route.
`examples/00_generate_flat_file.py` uses `common.generate_flat_file`, while
this attempt executed its authorized transparent recipe directly. The public
load, machine-summary and loss-aware tracking calls align with
`tests/test_pyptc_shims.py`; the attempt separately records 586 flat-file fibre
records and 375 PyPTC nodes. Optics examples/tests remain outside admission
scope.

This feedback and the ledger preserve attempt `082315Z`. The three-bundle
retention rule prunes the older `attempt-20261026T200752Z`; its report/result
hashes and history remain in feedback 0003 and the ledger. No shared skill
change or acceptance decision is implied.

## Follow-up: root cause of the resplitting warning

The `DLMAX > LMAX 0.51440000000000197` message exposes a producer/consumer
contract mismatch. The attempt copied the repository's standard
`workflows/madx/ptc_scripts/resplit.ptc`: `LMAX=0.5`, `FUZZYLMAX=1.1`, cutting
algorithm 2, and `THINLENS=0.01`. In `source/So_fitting.f90`, resplitting only
cuts a piece when it exceeds `LMAX * FUZZY_SPLIT`, so the producer allows up to
`0.55 m`. But the flat-file writer stores `LMAX` and does not store
`FUZZYLMAX` (`source/Sp_keywords.f90`); the separate PyPTC runtime therefore
reads `0.5 m` as its limit. Its orbit-node builder compares the measured
`0.5144 m` directly against that value (`source/Sq_orbit_ptc.f90`) and warns.

Thus the attempt did use the standard resplitting recipe, but it generated a
flat file whose measured node gap exceeds the limit advertised in the file.
The warning is valid from the consumer's available metadata; it is not enough
to call the gap acceptable merely because the producer used a 10% fuzzy
allowance. Earlier runtime logs were not retained in the inspected example
outputs, so the exact historical value `0.5144 m` cannot be confirmed. The
source code and shared scripts show that this mismatch is systemic for all
workflows using this recipe. Future feedback should report both configured
limits and verify consistency with the flat-file metadata. Repair options are
to make the producer enforce nominal `LMAX` (for example, `FUZZYLMAX=1.0`) or
to preserve the fuzzy tolerance in the flat-file contract and have consumers
apply it consistently. Changing `LMAX` alone does not remove the mismatch.

The cavity-frequency warning is independent and is caused by the no-RF layout.
`ORBIT_WARNING 11` is the sum of that warning's code `1` and the `DLMAX`
warning code `10`; it is not a third independent issue. This diagnosis does
not validate long-term tracking accuracy or establish acceptance.
