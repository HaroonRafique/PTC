# User-run assessment: attempt 020

Date: 2026-10-30
Run class: user-run
Disposition: assessed; no acceptance
Attempt outcome: `incomplete-perturbation-execution`
Skill: `iteration-0005/SKILL.md`, shared revision
`3aad35af0ad53337fc259e14d0d614fd55821aa5`, SHA-256
`b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae`
Tolerance baseline: `OPTICS-BASELINE-2026-10-28-v1`, SHA-256
`77bb8564d562a0a72b1eae738b097d6d614177f40db4abe01f81cb5236d671c8`

## Assessment against the skill

Attempt 020 is a substantial user-run application of iteration 0005, but it is
technically incomplete and not accepted. Its canonical outcome is correct. It
declares all 38 candidate cases and records their dispositions. The nominal
case, 28 signed corrector cases, and one QF field-strength case completed and
produced 30 case-level plots (nominal plus 29 perturbations). Six isolated
SP0_QF alignment cases, the full survey EFIELD table, and its verified
intersection failed before the PyPTC target process ran. They have no target
result or plot, and no result should be inferred for them.

### Provenance and model

The attempt uses accepted admission snapshot `attempt-20261027T194128Z`; its
accepted scope remains snapshot admission only. It pins the five ordered input
hashes, accepted flat-file hash, and MAD-X 5.02.00 binary hash. The effective
recipe records the 2023 strength overlay, `synchrotron`, `a1=b1=0`, all trim
variables zero, and the accepted flat file without nominal resplitting. The
candidate API-level-5 PyPTC library SHA-256 is
`d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`; its
source revision is `807a8d06e15e52628827031432110c90d1286bdb`. The MAD-X binary
SHA-256 is `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.

Exact workflow hashes are in the run manifest: `benchmark_pyptc.py`
`bfaa00f38a9988c3896c7812bd430f60fce4286930ccc7d259e5df894c351a89`,
`isis_rcs_optics.py`
`691123630b8087ad359ed0646c559a871a8fbfdad0e50736d12c1505086cef4c`,
`ptc_optics_worker.py`
`93227b5b24c3db7b1b79803b73ef7d3f0968081b53e9433edeedf034ea44f3b0`,
`ptc_tracking_worker.py`
`26e0ecef339574d2f0539dbbfbf8eb2e8731cf7c04ebc8f8a11ed508287c1524`, and
the shell orchestrator
`359812530fe56f0bfa5a28be45859b73f9f69fd30318b863714a594820448e46`.

### Nominal and completed-case results

Nominal mapping is verified: 586/586 MAD-X named element exits map to 586
PyPTC nodes by identity and physical exit position at `1e-9 m`; PyPTC produced
804 orbit-node rows and printer groups. Across 30 completed cases, 14 sampled
profile observables produced 344 within-tolerance and 76 out-of-tolerance
classifications (420 metrics total). Every `mux` and `muy` profile is out of
tolerance in all 30 completed cases; `dx` is out in 2 cases and `dy` in 14.
The other sampled profile metrics are within tolerance. This is provisional
screening evidence, not physics acceptance.

For nominal, orbit, momentum, beta, alpha, and dispersion metrics pass the
specified baseline. Phase and full tunes do not:

| Observable | Signed target minus reference | Baseline limit | Result |
|---|---:|---:|---|
| `mux` max absolute profile residual | `6.02e-5` turns | `1e-5` turns | out of tolerance |
| `muy` max absolute profile residual | `1.07e-4` turns | `1e-5` turns | out of tolerance |
| Horizontal full tune | `+5.39e-5` | `3e-6` | out of tolerance |
| Vertical full tune | `+1.07e-4` | `3e-6` | out of tolerance |
| Circumference | `-1.14e-13 m` | `1e-3 m` | within tolerance |

Across completed cases, 120/150 scalar metrics are out of tolerance: the two
tune and two chromaticity metrics in each case. Circumference is within
tolerance in all 30. Nominal native PyPTC chromaticities are numerically close
to MAD-X 5.02.00 `DQ`, but the pinned coordinate evidence identifies PyPTC as
`dQ/dPT` and MAD-X 5.02.00 as `dQ/dDELTAP`. After applying the run-local
`beta0=0.36713319993`, PyPTC-minus-MAD-X differences are `+3.00323` (horizontal)
and `+3.04167` (vertical), against limits `9e-4` and `3.5e-4`. This reproduces
the open discrepancy in investigation 0002; it does not identify its physical
or numerical cause. The run records the MAD-X finite-difference step as
`1e-6`, but does not report bounded step stability or matched-offset
comparison. Those remain follow-up diagnostics before final interpretation.

The requested thick tracking diagnostic completed for 64 turns and 65 samples.
Maximum x/y residuals are `2.50e-5 m` and `5.77e-5 m`, both
`pending-tolerance`. MAD-X `PTC_TRACK` and PyPTC use the PTC engine, so this is
not independent tracking-engine validation and does not gate transverse
optics. Corrector x/y response residuals are retained, but application status
is `pending-application-floor`; other response families are
`pending-tolerance`. No response agreement or perturbation acceptance is
claimed.

### Root cause of the eight failed cases

All eight failures report `RuntimeError: TFS file has no named element rows:
.../case_error_table.tfs`. This is a benchmark-harness parser defect, not
evidence that PyPTC rejected an error table. EFIELD tables have named rows but
no `S` column. The iteration-0005 `isis_rcs_optics.parse_tfs()` guard requires
both `NAME` and `S` and is intended for TWISS profiles. `audit_error_table_esave()`
reuses that TWISS parser on source and MAD-X `ESAVE` EFIELD tables. In
`run_perturbation_case()`, the audit executes after the MAD-X model but before
`run_pyptc_optics()`. The exception therefore aborts all six isolated
misalignment cases and both survey-table cases before PyPTC is invoked. MAD-X
case-local output and `applied_error_table.tfs` exist, but there is no target
application result, normalized source-to-ESAVE verdict, or plot.

Use an EFIELD-aware reader for the source/ESAVE audit, or make the shared TFS
parser require `S` only for profile tables while preserving strict TWISS
checks. Then rerun these cases in a new attempt. Do not classify this as
unsupported PyPTC functionality or as a numerical comparison.

### Plots and report quality

One combined PNG exists for every successful case; failed cases have no
fabricated plot. The manifest marks all 30 as
`visually_inspected_at_normal_size: false`. The nominal image is `1600 x 11700`
pixels; the field-strength image is `1600 x 12350`. Visual inspection of these
representatives at fit-to-page/screen size confirms labels, tables, axes, and
residual details are too compressed to review. The skill's normal-size
readability gate remains open. Improve legibility while keeping one PNG per
completed case, and mark inspection only after actual review.

The manifest names a `bare_working_point` group for perturbed cases too; those
panels should be labelled as the case's perturbed working point. The report
prints chromaticity results as a long Python dictionary literal, and retains
the stale nonclaim “No chromaticity agreement claim until target derivative
coordinate is established” even though this iteration applies the identified
conversion. Replace it with a precise statement that converted values are out
of tolerance and their cause/review remain open.

MAD-X redefinition and PyPTC runtime warnings are retained. The nominal record
counts 302 ignored implicit MAD-X redefinitions; the target records the
cavity-frequency, DLmax/LMAX, and orbit warning markers. They are not the cause
of the eight parser failures. The existing resplitting contract still applies;
do not silently change `LMAX` to suppress its warning.

### Comparison with PyPTC examples and tests

The repository EFIELD example uses `PTC.apply_madx_error_table()` for PyPTC
and MAD-X `READMYTABLE`/`SETERR` for the reference. Its stored output applies
the local survey table and a synthetic normal/skew field case.
`tests/test_efield_api.py` tests parsing with a `NAME` plus error-column TFS
schema and no `S`, including alignment and integrated multipole fields. These
existing paths show `S` is not an EFIELD requirement. They were inspected for
learning only, not used as hidden inputs to the independent attempt; no
example or physics test was rerun during this assessment. The attempt's ten
harness checks passed but do not validate the engine calculations or catch the
common audit defect.

The exact Xsuite attempt-029 EFIELD source is not archived in this repository;
the local April 2026 table does not prove byte-for-byte equivalence to it.

## Required follow-up

- Fix the iteration-0005 EFIELD audit/parser boundary so tables without `S`
  reach the PyPTC target, with focused tests for source and ESAVE EFIELD tables.
- Rebuild the next attempt from the same pinned skill revision and execute all
  38 candidates. Keep attempt 020 immutable.
- Make stitched plots readable at normal size, inspect representative plots,
  and reconcile the report and manifest review flags.
- Replace the raw chromaticity dictionary and stale nonclaim; keep converted
  values out of tolerance and investigate estimator/step effects without
  changing the provisional baseline.
- Continue phase/tune investigation; leave responses pending where tolerances
  or application floors are absent.
- Keep this attempt unaccepted and do not create a publication completion
  (`REP`) record: required cases and plot review are incomplete.

## Provenance

| Evidence | SHA-256 |
|---|---|
| Attempt report | `44ce9100558fb2c814a2242c2f772ec4906e8c496a0861dba2ed4ffa1296b4f4` |
| Attempt result | `2c735ddc114b85b956410b616f80c90f99bc728ce31ce00502d97ab38dbd9fb3` |
| Attempt manifest | `468acb3a52d78cf97315c118f536b1477b8e0af8b4279d9eb6604f61083aac7a` |
| Campaign case inventory | `7432911037a51e15d24f3bcc5b823f361a2c9ce821e24197af6297bf2f8a2ede` |
| Plot manifest | `9ac7e399a46fb731dcd6c06ec0aba110ca3b987e5d84187257e80e49e3269822` |
| Harness check log | `53e31304893a95f23396beb63bc21e2a70a2ffba5fa8920cbfd6caca9e950ed2` |
| Profile response summary | `62553745d90c1eec64f5118c3827a5e6c2b03f243992421f149ad8489a6e13c1` |
| Scalar response summary | `0d9de80ce8c95a3a5f16567080e2b1816f331995a934e5646d7ece1774974de0` |
| Nominal composite | `4117bc91cc10532de7c853daf68c573fddd36ad6f06da90a88790fa1483e069e` |
| Failed-case EFIELD table (SP0_QF DX) | `561446da055184b1d8b8ac471270dbf0dc1ea1141951292d8be86c02d75106d9` |
| Candidate PyPTC library | `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c` |

This assessment is local campaign feedback under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
It is not user/physics acceptance or publication completion.
