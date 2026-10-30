# User-run assessment: attempt 021

Date: 2026-10-30
Run class: user-run
Disposition: assessed; no acceptance
Attempt outcome: `incomplete-perturbation-execution`
Skill: `iteration-0005/SKILL.md`, shared revision
`3aad35af0ad53337fc259e14d0d614fd55821aa`, SHA-256
`b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae`
Tolerance baseline: `OPTICS-BASELINE-2026-10-28-v1`, SHA-256
`77bb8564d562a0a72b1eae738b097d6d614177f40db4abe01f81cb5236d671c8`

## Assessment against the skill

Attempt 021 applies the same pinned iteration-0005 skill and linked provisional
tolerance baseline. All 38 candidate cases are inventoried and classified as
included. The nominal case plus 29 perturbations completed and produced 30
plots. Eight included alignment/EFIELD cases failed during the source-to-MAD-X
ESAVE audit, before their PyPTC target worker ran. No candidate was classified
unsupported or left unexecuted, but these eight failures prevent the required
all-case execution gate from passing. The canonical outcome is correctly
`incomplete-perturbation-execution`; the run is not accepted.

The attempted runner correction from the previous cycle worked through the
first failure: both the source EFIELD and MAD-X ESAVE tables were parsed despite
having no `S` column, with 38 named records each. The audit then failed in its
source-row indexing loop with `NameError: name 'counter' is not defined` for
all six isolated SP0_QF misalignments, `survey_error_table`, and
`survey_error_table_verified_intersection`. In
`scripts/python/iteration_0005/benchmark_pyptc.py`,
`audit_error_table_esave()` initializes `source_occurrence` and `source_index`
but mistakenly writes to undeclared `counter` and `index`. The saved-row loop
already uses the declared `saved_occurrence` and `saved_index`. This is a
runner defect, not a PyPTC API failure; no target application result or plot
exists for these eight cases.

The deterministic runner harness reports all 10 tests passing, but none calls
`audit_error_table_esave()`, so the runtime defect escaped the current fixture
suite. The case-inventory tests therefore do not establish the error-table
audit path. The existing `tests/test_efield_api.py` checks EFIELD TFS input
without an `S` column; `examples/06_madx_efield_api.py` compares MAD-X
`READMYTABLE`/`SETERR` with PyPTC's public `apply_madx_error_table()` API, and
its stored report records successful application within its declared scope.
Those example and test paths show that EFIELD does not require `S`, but they do
not exercise this benchmark's source-to-ESAVE row indexer. They were inspected
for learning only and were not rerun in this assessment.

## Provenance and nominal results

The attempt records accepted snapshot admission attempt
`attempt-20261027T194128Z`, API-level-5 PyPTC library SHA-256
`d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`, MAD-X
5.02.00 binary SHA-256
`426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`, the
2023 strength overlay, `synchrotron`, `a1=b1=0`, zero trims, and thick tracking.
The exact workflow source hashes are in `manifest.json`; the two modules
relevant to this follow-up are `benchmark_pyptc.py`
`a7ddbe6cb65fa35f31979d1b0e3490f7a7ec95dbde0e5526d14d9c8731c20100` and
`isis_rcs_optics.py`
`c45e1b2f2d4c27be10d6471bd5f50a7f8a90ec58ad1492bc2e5dc5beb28b0b63`.

Nominal mapping remains verified: 586/586 MAD-X named exits map to PyPTC
nodes at `1e-9 m`; PyPTC produced 804 orbit-node rows. Across the 30 completed
cases, 344 of 420 profile metrics are within the provisional baseline and 76
are out of tolerance. Phase `mux`/`muy` metrics are out in all completed cases;
other profile failures include `dx` in two cases and `dy` in fourteen.

For nominal, full tunes differ by `+5.3896e-5` and `+1.0653e-4`, against
`3e-6` limits. Phase maximum absolute residuals are `6.0229e-5` and
`1.0653e-4` turns, against `1e-5` limits. Circumference differs by
`-1.14e-13 m`, within its `1e-3 m` limit. Across completed cases, 120/150
scalar classifications are out of tolerance: both tunes and both converted
chromaticities in each case; circumference is within tolerance in all 30.

The run applies the `dQ/dPT` to `dQ/d(delta_p)` conversion using run-local
`beta0=0.36713319993`. The resulting nominal chromaticity differences are
`+3.00323` (horizontal; limit `9e-4`) and `+3.04167` (vertical; limit
`3.5e-4`). This reproduces the unresolved issue in investigation 0002 and
does not identify its cause. The report's nonclaims list is stale: it says no
chromaticity claim is made “until target derivative coordinate is
established”, although the run records the coordinate conversion and
out-of-tolerance values. The report also renders all chromaticity details as a
long Python dictionary literal. The next runner revision should state that the
coordinate conversion is applied, the results are out of tolerance, and the
cause remains open; render the values as a compact table.

Thick tracking completed 64 turns with 65 samples. Maximum x/y residuals are
`2.4956e-5 m` and `5.7669e-5 m`; both remain `pending-tolerance` and do not gate
transverse optics. Profile response summary has 28 rows: 2
`pending-application-floor` and 26 `pending-tolerance`; scalar response
summary has 10 `pending-tolerance` rows. No response acceptance is claimed.

## Plot review

The plot manifest links 30 case PNGs, each with one vertically stitched
composite and 1600 x 850 pixel strips. Its
`visually_inspected_at_normal_size` fields correctly remain false as runner
metadata. I inspected nominal and a representative corrector image at original
detail. Increasing strip height did not make the full composite readable at
fit-to-screen scale; the nominal working-point table has crowded/overlapping
cell text and its recipe note runs past the visible width. Titles and labels in
the 2 x 4 nominal overview are also crowded. Individual profile panels have
more room, but the 1600 x 15300 / 16150 pixel stitched images still require
scrolling and their top summary panels need layout changes. The plot
readability gate remains open; do not mark the images reviewed automatically.

## Required follow-up

- Correct source row indexing in `audit_error_table_esave()` so it uses
  `source_occurrence` and `source_index`. Add focused coverage of this function
  to the runner checks, then use the retained EFIELD source/ESAVE tables for a
  bounded audit smoke check before the next full user run.
- Keep all eight cases included and rerun all 38 from fresh case-local states;
  do not reclassify the runner failure as unsupported PyPTC behavior.
- Redesign the working-point table and nominal overview to avoid label
  collisions and clipping while preserving one composite PNG per case and all
  declared panel groups.
- Correct the stale chromaticity nonclaim and replace the raw dictionary in
  `report.md` with concise, auditable values. Keep the `dQ/dPT` interpretation,
  conversion, large residuals, and open cause explicit pending further
  coordinate/step investigation.
- Keep the provisional tolerance classifications and all response families
  pending human/physics review. No acceptance or `REP-####` completion record
  is supported by this run.

## Provenance hashes

| Evidence | SHA-256 |
|---|---|
| Attempt report | `98c007a53f2e3827e619fd582f8790aa691b30a4cedfebf40219322c5739e3bd` |
| Attempt result | `ca50dbf261fa28765e02b858f4d4739a2075220fb755c8aa8683f3586e10c4a9` |
| Attempt manifest | `92722df6ed531c31fc5fd5144665f2000bbf7989e382f8662ded7bfee9112ae6` |
| Case inventory | `7432911037a51e15d24f3bcc5b823f361a2c9ce821e24197af6297bf2f8a2ede` |
| Plot manifest | `eab14e8995d9a0a9895d1668548ace8882ddbfe41f7510274b75e32edcbd96e7` |
| Harness test log | `53e31304893a95f23396beb63bc21e2a70a2ffba5fa8920cbfd6caca9e950ed2` |
| Profile response summary | `62553745d90c1eec64f5118c3827a5e6c2b03f243992421f149ad8489a6e13c1` |
| Scalar response summary | `0d9de80ce8c95a3a5f16567080e2b1816f331995a934e5646d7ece1774974de0` |
| Nominal composite | `bad2c5cfd50ea645b58caef70d9189a3f6511c3a37bbe938fe540e546d68000c` |
| Representative corrector composite | `7786fecfaa77967c21867f7df9ea0aa7c8aa2d00b57b305f53a203c4814aa8ae` |
| Failed-case source EFIELD table (`sp0_qf_dx`) | `561446da055184b1d8b8ac471270dbf0dc1ea1141951292d8be86c02d75106d9` |
| Failed-case MAD-X ESAVE EFIELD table (`sp0_qf_dx`) | `1435897bbd20b3473252a811f67cce196b043f70734be378413420b19c9773e5` |
| Failed-case status (`sp0_qf_dx`) | `6eb9e0e1b89b9725d1316ffd6066c861bbca6d873f587c37aa97390fd16cb1de` |

This assessment is local campaign evidence under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
It is not user/physics acceptance or publication completion.
