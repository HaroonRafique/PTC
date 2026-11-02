# User-run assessment: attempt 023

Date: 2026-11-02  
Run class: `user-run`  
Disposition: assessed; no acceptance  
Attempt outcome: `completed-needs-human-review`  
Skill revision: `330746975383bc01ae100bea18ae54299b83cb2e`, blob
`7a1754e0c7838f4aee532b07dc708f76761bfc70`, SHA-256
`b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae`  
Tolerance baseline: `OPTICS-BASELINE-2026-10-28-v1`, SHA-256
`77bb8564d562a0a72b1eae738b097d6d614177f40db4abe01f81cb5236d671c8`

## Assessment against the pinned skill

Attempt 023 completed all 38 declared candidates: nominal, 28 signed corrector
cases, one field-strength case, six isolated alignment cases, the full local
EFIELD survey table, and the six-component verified intersection. There are
no failed, blocked, unsupported, or unexecuted cases, and each included case
has one composite plot. The accepted admission basis and recipe are recorded;
the recipe uses the five pinned source inputs, the 2023 overlay,
`a1=b1=0`, zero trims, `synchrotron`, and the accepted flat file without
resplitting. The nominal map verifies all 586 MAD-X rows against 586 PyPTC
element exits at `1e-9 m`; PyPTC retains 804 node rows/groups.

There is one material skill-conformance conflict. The exact skill snapshot
still says API-level-5 `PTC.chromaticities()` is `dQ/dPT` and instructs the
runner to multiply by `beta0`. Attempt 023 instead compares the native values
directly as `dQ/d(delta_p)`, following the source and state-controlled evidence
in [investigation 0003](../investigations/0003-chromaticity-coordinate-reassessment.md)
and [feedback 0022](0022-chromaticity-coordinate-reassessment.md). That
investigation supersedes the earlier inference, but the pinned skill has not
yet been reconciled with it. The runner's direct comparison is supported by
the PyPTC evidence; the application is therefore not fully conformant with
the pinned skill text until the shared skill is reviewed and updated through
its separate development process. The attempt report should also link the
investigation directly. No shared skill was changed in this campaign.
The snapshot content SHA is the same `b5724836...94ae` recorded for attempt
022, even though the repository revision identifier is newer; the relevant
skill text did not change between those user runs.

The report records `uncoupled-transverse-twiss`, RF inactive, zero harmonics,
and explicitly says coupling was not evaluated; its scope is limited to plane
observables. It inventories optional maps, normal forms, and coupling
indicators as unbenchmarked. This is a clear scope limit, not evidence that
the lattice is uncoupled. Corrector, field, alignment, and survey responses
are retained per case. The shared signed corrector x/y tolerance is present,
but application remains `pending-application-floor`; other response families
remain `pending-tolerance`. Both survey-table cases and all six isolated
misalignment source-to-ESAVE audits each compare 3,838 values with zero
mismatches. PyPTC application records retain one applied element for each
isolated case and 38 records for each survey-table case. These MAD-X audits
and PyPTC application records do not establish a minimum meaningful target
response. The exact external Xsuite attempt-029
EFIELD table is unavailable, and the report correctly avoids claiming that
the local table is byte-for-byte equivalent to it.

The runner's `completed-needs-human-review` outcome is appropriate. It does
not infer physics acceptance, and this assessment does not authorize a
`REP-####` publication record.

## Numerical results

The common screening baseline remains provisional. Across the 38 cases,
440/532 profile metrics are within tolerance and 92 are outside:

| Profile observable | Out of 38 | Worst absolute residual | Provisional limit | Worst case |
|---|---:|---:|---:|---|
| `mux` | 38 | `7.39717e-5` turns | `1e-5` | `corrector_sp9_r9hd1_plus_1mrad` |
| `muy` | 38 | `1.24965e-4` turns | `1e-5` | `corrector_sp0_r0vd1_plus_1mrad` |
| `dx` | 2 | `1.00664e-4 m` | `1e-4 m` | `corrector_sp0_r0hd1_plus_1mrad` |
| `dy` | 14 | `2.24000e-4 m` | `1e-4 m` | `corrector_sp5_r5vd1_plus_1mrad` |

All other profile observables are within the provisional screen. The largest
beta and alpha residuals remain below their recorded relative/absolute
criteria.

Across 190 scalar comparisons, 100 are within and 90 are outside:

| Scalar observable | Within | Outside | Nominal difference |
|---|---:|---:|---:|
| Horizontal tune | 0/38 | 38/38 | `+5.38959e-5` vs `3e-6` limit |
| Vertical tune | 0/38 | 38/38 | `+1.06528e-4` vs `3e-6` limit |
| Horizontal chromaticity, direct native comparison | 38/38 | 0/38 | `+8.32020e-5` vs `9e-4` limit |
| Vertical chromaticity, direct native comparison | 24/38 | 14/38 | `+2.09457e-5` nominal; worst absolute difference `7.36948e-4` vs `3.5e-4` limit |
| Circumference | 38/38 | 0/38 | `-1.14e-13 m` |

The attempt's chromaticity values reproduce the corrected attempt-022
interpretation: all horizontal cases and 24 vertical cases pass the
provisional screen; 14 vertical cases remain outside. This does not resolve
the skill text conflict or grant physics acceptance. The tune and phase
differences persist. Thick bounded tracking completed, but is a separate
diagnostic using the shared PTC tracking engine; it is not independent
tracking-engine validation or an acceptance gate.

## Plot review, provenance, and warnings

The bundle has 38 case PNGs. The composites are 1600 x 15,300 px for nominal
and 1600 x 16,150 px for perturbed cases, with 19 strips of 1600 x 850 px.
All 38 plot-manifest entries still say
`visually_inspected_at_normal_size: false`. The attempt therefore does not
close the skill's plot-review requirement. Representative plots should be
reviewed at panel scale, especially the working-point and response tables;
no readability claim is made for all 38 plots.

MAD-X 5.02.00 completed normally and logs 302 ignored implicit element
redefinitions. PyPTC runtime records `ORBIT_WARNING=11` and reports a maximum
orbit-node gap of about `0.5144 m` against nominal flat-file `LMAX=0.5 m`. This
is the already documented resplitting producer/consumer contract issue; it
was not changed or diagnosed by this attempt. Runtime logs are retained.

The run's 11 harness unit checks passed. Existing PyPTC
`tests/test_linear_optics_comparison.py` checks internal phase accumulation
against PTC's tune getter and interpolation behavior; it does not test MAD-X
tune agreement. `examples/01_plot_bare_twiss_closed_orbit.py` demonstrates the
same public optics getters but is not a cross-code comparison. The tracking
coordinate example and investigation 0003 support the distinction between
the chromaticity getter's `DELTA` state and the separate tracking-helper
coordinate issue. Existing EFIELD examples/tests cover the public table API
and parser behavior; this attempt extends the evidence to the benchmark's
case-local comparisons. The harness tests do not currently lock the
PyPTC/MAD-X chromaticity derivative definition, so add a focused regression
assertion after the skill's coordinate rule is reconciled.

One stale phrase remains in the attempt report's evidence-file list: it calls
`scalar_response_summary.csv` “converted chromaticity response residuals,”
although attempt 023 now stores a direct native-coordinate comparison.
Correct that label in the next runner revision without editing this raw run.

## Required follow-up

- Reconcile the shared skill's API-level-5 chromaticity paragraph with
  investigation 0003 through the separate skill-development process, then
  record the exact revised skill revision before the next fresh application.
- Keep attempt 023 unaccepted until the tune/phase differences and the 14
  vertical chromaticity outliers are reviewed against the provisional
  baseline.
- Complete normal-size review of the 38 case plots and set plot-manifest
  review states only from that inspection.
- Review meaningful-response floors and response tolerances. Keep response
  classifications pending where no reviewed criterion applies.
- Fix the stale “converted chromaticity” description in the report generator
  and add a focused regression check for the matched derivative coordinate.
- Do not change the known `LMAX`/`FUZZYLMAX` contract as a warning workaround;
  any split-policy change needs a regenerated lattice and representative
  optics/tracking comparison against a retained baseline.

## Provenance hashes

| Evidence | SHA-256 |
|---|---|
| Attempt report | `853899dd25acb9f178797da756a9b72357527f8fb8563e5d9fd0f1e1415f0215` |
| Attempt result | `6c5943050d7ee9ed7a3d27f5ec94fa62f33dd578d658998ef600107d90fd000a` |
| Attempt manifest | `310a4f6b17311a50437980fb3583397c2b76ab0078ff25bef3f52e273f87e5b8` |
| Campaign case inventory | `7d4216d03cabb879471cee43bbf4f68388f92f650d080901d2b8284ed0c498e4` |
| Plot manifest | `1533fa60be13f12e48ac7a8b8fe7a7e6b7078fb3de992c1d9958a5456fa76e97` |
| Harness test log | `e56f2b46c4a720004ba7e62eb18dcecd950aec709ce9fbded1fb63b4753d1e72` |
| Skill snapshot | `b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae` |
| Profile response summary | `05130e9bb839511fd6a6774dbc97fcbc4bb5ca5ee0dec4dbbc126fabbc43f49c` |
| Scalar response summary | `b046d23825de7ac53cf8c9562d0a24ef918a04a051dc01c91f48d4479a67f607` |

The candidate source revision is `c6398a7aead6467535c47a412962f9a08d378f95`,
candidate API level is 5, and library SHA-256 is
`d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`. The
MAD-X 5.02.00 binary SHA-256 is
`426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
The report, source identities, accepted-admission hashes, ordered input
hashes, and case evidence remain in the raw attempt bundle.

This PyPTC campaign record links to the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
It is evidence for review, not user/physics acceptance or publication
completion.
