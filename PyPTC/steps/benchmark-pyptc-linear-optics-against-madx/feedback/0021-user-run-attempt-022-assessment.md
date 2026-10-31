# User-run assessment: attempt 022

Date: 2026-10-31
Run class: user-run
Disposition: assessed; no acceptance
Attempt outcome: `completed-needs-human-review`
Skill: `iteration-0005/SKILL.md`, shared revision
`3aad35af0ad53337fc259e14d0d614fd55821aa`, SHA-256
`b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae`
Tolerance baseline: `OPTICS-BASELINE-2026-10-28-v1`, SHA-256
`77bb8564d562a0a72b1eae738b097d6d614177f40db4abe01f81cb5236d671c8`

## Assessment against the skill

Attempt 022 completed the full declared candidate inventory: 38/38 cases,
including nominal, 28 signed corrector perturbations, QF field strength, six
isolated misalignments, the survey EFIELD table, and its verified intersection.
All cases have completed status and one case PNG. There are no failed,
unsupported, blocked, or unexecuted candidates. The outcome
`completed-needs-human-review` is appropriate: execution is complete, but the
screening results and plot readability do not support acceptance.

The source-to-ESAVE EFIELD audit and target application path now run. In all
six isolated misalignment cases and both survey-table cases, MAD-X source and
ESAVE tables each contain 38 records and the audit compares 3,838 component
values with zero mismatches. PyPTC target records are present: one selected
record for an isolated misalignment and 38 records for the full survey and
verified-intersection cases. This resolves the attempt-020 parser failure and
attempt-021 source-index `NameError` as harness defects; neither run was
evidence that PyPTC rejected the EFIELD API. The exact external Xsuite
attempt-029 EFIELD table remains unavailable, so the local survey-table case
does not establish byte-for-byte equivalence to that candidate.

The user-run harness test log reports 11 checks passed, now including the
iteration-0005 workflow import and a duplicate-name, no-`S` EFIELD source/ESAVE
audit fixture. This supports the audit helper's parser/index behavior; it does
not replace review of the engine results.

## Provenance and numerical findings

The accepted basis is snapshot admission attempt `attempt-20261027T194128Z`.
The recipe records the five pinned inputs in order, 2023 strength overlay,
`synchrotron`, `a1=b1=0`, zero trims, and thick tracking. The skill and
tolerance-baseline snapshots match the pinned hashes above. The API-level-5
PyPTC library SHA-256 is
`d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`; the
source revision is `7ab02da923b52f868f9e0e6247987cf33bcfcf53`. MAD-X 5.02.00
binary SHA-256 is
`426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
Exact workflow module hashes are in `manifest.json`.

Nominal boundary mapping is verified: 586/586 MAD-X element exits map to
PyPTC nodes at `1e-9 m`; PyPTC retained 804 node rows/printer groups. Across
38 completed cases, 440/532 profile metrics are within the provisional limits
and 92 are out. By observable, all 38 `mux` and all 38 `muy` values are out;
`dx` is out in two cases and `dy` in fourteen. The remaining profile
observables are within the current screen.

Across completed cases, 152/190 scalar results are out of tolerance. The two
tunes and two converted chromaticities fail in every case; circumference is
within tolerance in all 38. For nominal, full-tune differences are
`+5.3896e-5` and `+1.0653e-4`, against `3e-6` limits. Maximum phase-profile
residuals are `6.0229e-5` and `1.0653e-4` turns, against `1e-5` limits.
Circumference differs by `-1.14e-13 m`, within the `1e-3 m` limit.

The recorded conversion compares PyPTC `dQ/dPT` with MAD-X `dQ/dDELTAP` in
`dQ/d(delta_p)` using `beta0=0.36713319993`. The nominal converted differences
remain `+3.00323` horizontal (limit `9e-4`) and `+3.04167` vertical (limit
`3.5e-4`). Investigation 0002's discrepancy is reproduced; its physical or
numerical cause is still open. The corrected report now states the conversion
and out-of-tolerance status directly, and the nonclaims list no longer says
that the derivative coordinate has yet to be established. The coordinate
interpretation still requires review before a physics claim.

Thick tracking completed for 64 turns and 65 samples. Maximum x/y residuals
remain `2.4956e-5 m` and `5.7669e-5 m`, both `pending-tolerance`. MAD-X
`PTC_TRACK` and PyPTC share the PTC engine, so this is not an independent
tracking-engine validation. The response summaries retain 54
`pending-tolerance` and 2 `pending-application-floor` profile rows and 20
`pending-tolerance` scalar rows. No response or physics acceptance is claimed.

## Plot review

The manifest records 38 PNGs and keeps
`visually_inspected_at_normal_size: false` for each; the run did not claim to
have reviewed its plots. I inspected the nominal and one corrector composite
using original-detail crops. The revised nominal working-point panel is much
clearer, but the corrector composite's nominal-subtracted scalar-response
table still has overlapping cell text, and long headings are clipped. The
rightmost titles in the nominal 2 x 4 overview also reach the panel edge. Thus
the skill's readability gate remains open. The full images are 1600 x 15300 px
(nominal) and 1600 x 16150 px (perturbed); the 100%-zoom scroll instruction
does not resolve collisions inside a panel. Inspecting two representative
cases does not establish readability of all 38 plots.

The inspection crops are available under
`test_outputs/benchmark-pyptc-linear-optics-against-madx/` as
`attempt-022-nominal-top-panels.png` and
`attempt-022-corrector_sp0_r0hd1_plus_1mrad-top-panels.png`. They are derived
views for assessment, not additional benchmark case plots.

## Comparison with PyPTC examples and tests

The existing `tests/test_efield_api.py` covers error-table parsing without an
`S` column, and `examples/06_madx_efield_api.py` compares MAD-X
`READMYTABLE`/`SETERR` with the public PyPTC `apply_madx_error_table()` API.
The attempt-022 results now connect those API capabilities to the benchmark's
source-to-ESAVE audit: all eight audited cases produced zero field-value
mismatches, and their PyPTC workers produced application evidence. This does
not establish equivalence with the unavailable external Xsuite table. No
example physics run was repeated during assessment.

## Required follow-up

- Keep the run unaccepted. Resolve the tune/phase and chromaticity differences
  and review the provisional baseline before making cross-code agreement
  claims.
- Redesign the response table and long panel headings to prevent text overlap
  and clipping. Preserve the one-composite-per-case requirement, and review a
  representative dense nominal and perturbed plot at normal size.
- Review response tolerances and minimum meaningful-response floors; retain
  pending classifications until reviewed.
- Do not create a `REP-####` completion record while the plot review, tolerance
  review, and numerical discrepancies remain open.

## Provenance hashes

| Evidence | SHA-256 |
|---|---|
| Attempt report | `a736a6e532cf21f0084a9291293c68a60fe6be6f8348ef834a94398064853bf6` |
| Attempt result | `500a35cf169e7b08d5ecbdc3f8da85211f7748cca43fde76ebbaaec064452c87` |
| Attempt manifest | `ab6731a5a71937f912cabc02ed96abb4e0fd4fdf2ad8e39edeb5748e3f076e06` |
| Case inventory | `fce1036b1c9d34ccb6f693338c0fa7d06ad51ae926b6032689158e9c14820f1d` |
| Plot manifest | `360e5a0d0e403f1f8e01874be8f0cbd5b455832e52239a98fd0d95687756d8d4` |
| Harness test log | `7aa9bdfa3a9e531da6979a17eb8a4bd9c654ae068b5a2d7560aa7311ba9392f3` |
| Profile response summary | `05130e9bb839511fd6a6774dbc97fcbc4bb5ca5ee0dec4dbbc126fabbc43f49c` |
| Scalar response summary | `2dcdfe54cc5e175963371a6c45c601ef3b92f3e36e6808cb7952595ac03d58fc` |
| Nominal composite | `f13299bc3bc0d46f97ea58574a7d3419295eb39cc916fed79e5ca877430fb44e` |
| Corrector composite inspected | `c74bde8ee36fc0bde0e741a1e3fc316de3bb4ebfc679b41b82a197aa8f1dd983` |
| Nominal inspection crop | `2982cb5a81dd6b340a2bbf2be82535dd970535d916b669a5698c95ea25b715e` |
| Corrector inspection crop | `a09afcb327b8613e7fa31d33ead88be1a294ddaa1f4ead58a970e8315f56a134` |
| Full survey source-to-ESAVE audit | `9c42ba6acb4055fd15f2675bea7004556a6625adcb522aeeaae7170145a4b9ba` |
| Full survey PyPTC API summary | `9a08bc9ceb90cd891da8a60f661bb8e66ad3c69ef2ebe52237567a545a209276` |

This assessment is local campaign evidence under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
It is not user/physics acceptance or publication completion.

Retention note: older user-run bundle `attempt-019` is pruned under the
three-bundle policy after its report, result, manifest hashes, disposition,
and previous assessment link were carried forward in the review ledger and
feedback 0018.
