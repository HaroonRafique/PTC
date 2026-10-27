# User-run iteration 0002 assessment

Date: 2026-10-27
Attempt: `attempt-20261027T232957Z`
Run class: `user-run`
Outcome: `blocked-bounded-tracking`
Iteration: `0002`
Skill: `benchmark-code-against-isis-rcs-optics`
Skill revision: `f5293a3754dc8c4e9a6a4ba987603924b91949f3`
Skill SHA-256: `2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Accepted admission: `attempt-20261027T194128Z` (`snapshot admission only`)
Evidence-gated publication plan: Task 6 campaign evidence and Task 9
event-driven maintenance in
`docs/plans/2026-10-23-evidence-gated-agents-publication.md`.

## Evidence identity

| Artifact | SHA-256 |
|---|---|
| `report.md` | `cc3322d12b42a2517a345777dc366c248988c3208e922008607c048b03e141b0` |
| `result.json` | `3348eead9b4689fcdc40795582d3f531068aea7de85a8a561ec7690d070620c0` |
| `manifest.json` | `ad8c6535be37a1b704f9513ae2b6fa8656a2f3e2630f80487daeae09ad64f6a5` |
| `tracking_summary.json` | `178c5b8436635ade8ee53a818ae0a2ea9088532d06f3a2ef3a419a867997f69c` |
| `capability_matrix.json` | `41bbc7f8920f62cc7d0ca853cf80c71003f87950ec2943a5de0383af2575c8ff` |
| `plot_manifest.json` | `73ed82f15659fa11f3f18dd324b8129f683ab5bda7e9ff65a494781d766b0c83` |
| `case_nominal/nominal_optics_composite.png` | `430ad40983b478a39f7acfbc546fbfe6928ce39c6afbab276ffbf5b0f7beb603` |
| `reference/tracking/madx_tracking.log` | `06d7b8c4b8f91846d627650287bbe9449037efdc8646468c04bbdb8ad629af0a` |
| `reference/tracking/track.obs0001.p0001` | `219e3a3edccc01e8ae75e16a96ecacf7e72000e0906fc925dddf107ed28f03d4` |

The manifest records PyPTC source revision `e295f2a2750f94abc2928b6f76d259a5d01c1d3b`, target library SHA-256
`b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76`,
MAD-X 5.02.00 SHA-256
`426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`,
flat-file SHA-256
`32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a`,
and the five admitted input hashes. The effective recipe records the 2023
strength overlay, `synchrotron`, `a1=b1=0`, zero trim variables, and no
resplitting. Its target repository HEAD is `d8f6337fa0a5caa46c0948667b011a3fecf0dfed`;
the manifest also records that the checkout was dirty.

## Assessment against the pinned skill

The attempt correctly verifies the accepted snapshot scope and identities,
reuses the admitted flat file and library, and records the effective recipe.
The MAD-X TWISS run returns 586 rows. The target produces 804 orbit-node rows
for 586 fibres. The harness maps all 586 MAD-X element exits using fibre
identity, occurrence, name, and position, preserves zero-length identity and
the periodic endpoint, and records a `1e-9 m` position tolerance. This is
stronger evidence than matching by `s` alone.

The profile comparison retains all 14 observable families at 586 matched exits
with signed residual summaries. MAD-X dispersion and derivatives use this
run's `beta0=0.36713319993`. No reviewed tolerance exists, correctly leaving
these profiles and the scalar tune/circumference differences
`pending-tolerance`. The horizontal and vertical tune differences are
`+5.389592091e-5` and `+1.065275407e-4`; circumference differs by
`-1.14e-13 m`. These are reported values, not agreement claims. Chromaticity
is correctly blocked because the public PyPTC interface's derivative
coordinate is unresolved.

The seven bundled mapping/convention/parser/family fixtures pass. The target
tracking history retains 65 finite samples for 64 turns and its independent
loss check reports no loss. MAD-X retains the expected 65 rows but is
non-finite: the track file has `x=3.195274619 m` at turn 1 and NaNs from turn
2 onward. The runner correctly blocks the comparison rather than treating
these values as a cross-code residual. This is a repeat of the preflight
diagnostic, not a user-machine-specific failure.

### Tracking setup finding

The recorded MAD-X recipe runs:

```text
MAKETHIN, SEQUENCE=synchrotron, STYLE=TEAPOT;
```

The log explicitly says `no selection list, slicing all to one thin lens`.
MAD-X's track recipe therefore converts each thick element to its default
single thin slice. The admitted PyPTC flat file instead has 804 integration
nodes, created from the retained resplit recipe (`LMAX=0.5 m`, `FUZZYLMAX=1.1`,
`THINLENS=0.01`). This is a large integration-method mismatch and means the
MAD-X record is not yet a valid matched reference for bounded tracking. The
one-lens policy is a likely reason the trajectory becomes unphysical, but the
available evidence does not prove that it alone caused the NaNs. Keep the
reference tracking classification as `blocked-reference-nonfinite`; do not
infer a PyPTC tracking defect or numerical disagreement. Before a rerun,
prepare and inspect a deliberate MAD-X tracking slicing/integration policy,
retain its exact recipe, verify stable finite samples, and compare its
resulting machine state and integration controls with the target. Do not change
the admitted flat file or silently tune either model.

### Remaining skill gaps

- `capability_matrix.json` has ten generic categories, but it does not provide
  the required per-engine inventory for the full common core and the additional
  exposed capabilities: closed/reference orbit, integer/fractional/harmonic
  tunes, tune-from-tracking, RF/harmonic settings, corrector response, trim or
  harmonic control, aperture metadata, and error/misalignment application.
  Explanations should identify what MAD-X and PyPTC each expose and why a
  category is comparable, unavailable, blocked, non-equivalent, or
  unbenchmarked.
- The nominal plot manifest links the aligned data, mapping, signed residual
  direction, units, sample counts, and panel groups. It does not link the
  complete code identities and converted working-point values required by the
  skill's nominal master-plot contract.
- The composite is `3150 x 6900` pixels (`21 x 46` inches at 150 DPI). At
  normal overall viewing size its working-point text, ticks, and legends are
  too small to read comfortably. This is a readability failure despite the
  complete set of panels and visible sampled markers. The plot manifest still
  labels normal-size review as pending. Revise layout/typography and perform a
  recorded normal-size visual check; increasing pixel dimensions alone is not
  enough.
- The user-facing README gives setup/run commands but does not document each
  reusable helper's arguments, returned values, units, and side effects.
- The seven fixtures cover boundary occurrence/position, beta0 dispersion
  normalization, MAD-X chromaticity version conversion, PTC printer parsing,
  and family classification. They do not cover the updated skill's other
  explicit contracts: isolated conflicting cases, omitted target-application
  settings, partial error-table application, a zero-orbit but nonzero-optics
  response, partial/non-finite tracking classification, coarse FFT tune
  resolution, plot-manifest identity/working-point links, or composite plot
  normal-view and file-path validation.
- No `REP` or `EVAL` is appropriate: the bounded common-core tracking is
  blocked, the acceptance tolerances are unreviewed, and no benchmark
  acceptance has occurred.

## Learning comparison with existing PyPTC examples/tests

The attempt should be compared with, not retroactively seeded from,
`workflows/madx/compare_madx_pyptc_closed_orbits.py` and
`tests/test_madx_optics_benchmark.py`.

The existing comparison workflow already extracts PyPTC node optics, converts
MAD-X dispersion with the relativistic beta, computes PyPTC-minus-MAD-X
residuals, and writes overlay/residual plots. Its `rows_to_linear_table`
explicitly accounts for the MAD-X `s=0` entrance and PyPTC exit sampling. Its
plots organize each quantity in readable overlay/residual pairs. The new
attempt adds stronger exact name/occurrence/fibre/exit-position matching and
turn-record completeness/finite checks, which are useful skill-derived
improvements. The current attempt still needs the readability improvement
described above.

Existing tests cover shared-quantity completeness, native residual metrics,
MAD-X beta normalization, aperture interpolation, and a committed baseline's
provenance. The new iteration tests add entry/exit offsets, repeated positions,
occurrence identity, period endpoint, PTC printer parsing, and source-family
classification. Both suites are partial against the updated skill; neither
provides its newly required perturbation-application and tracking/plot
contract fixtures. No existing-test execution is claimed in this assessment;
the seven iteration-local checks were run by the user's runner and their log is
in the attempt bundle.

## Disposition and next work

This is a successful user-facing execution but an incomplete benchmark attempt.
Retain its bundle and classify it `user-run assessed`, with no acceptance.
Feedback 0004 records the agent preflight history; this file records the
user-run assessment. The shared skill is not edited here. The next skill cycle
should address the distinct tracking recipe issue and the capability,
documentation, fixture, and plot-readability gaps before another fresh
application. Keep the Xsuite campaign independent.

After recording this attempt, the three-bundle policy prunes
`attempt-20261027T222923Z`; its identity and hashes remain in feedback 0004 and
the ledger. The remaining raw bundles are `attempt-20261027T223155Z`,
`attempt-20261027T223232Z`, and this user-run attempt. This record supports the
prospective campaign evidence and event-driven review trail of publication-plan
Tasks 6 and 9. It does not create a `REP`, `EVAL`, tolerance decision, or
physics acceptance.
