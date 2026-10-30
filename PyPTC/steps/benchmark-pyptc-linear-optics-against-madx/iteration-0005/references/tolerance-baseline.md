# Linear-optics screening tolerance baseline

Status: current best shared screening baseline, adopted at the user's
direction on 2026-10-28. Use these criteria by default for comparable linear
optics results from any target code in this skill. They are provisional pending
the planned PyPTC comparison and subsequent user/physics review. They are not
physics acceptance limits or proof that either code is correct.

Baseline ID: `OPTICS-BASELINE-2026-10-28-v1`.

## Scope and provenance

The baseline combines the Xsuite testbed's user-approved comparison criteria
with the user's direction to use them as the shared best values so far. The
criteria were exercised in user-run Xsuite attempt-032, which completed all 38
declared cases and classified the 19 scalar/profile observables within these
limits. Attempt-032 remains pending review; this does not validate the limits
for PyPTC or establish physics acceptance.

The source recipe was `isis_2024` commit
`fcf2a348087d96ae9a3b48e481c0fc5560b9663f`, variant
`00_Simplified_Lattice`, sequence `synchrotron`, with the testbed CMW
`ISIS.strength` and the symmetrically applied user-directed `2023.strength`
overlay. That overlay remains outside admission attempt-017's reviewed scope.
Use the numerical criteria across codes only after reconciling the observable,
units, reference state, branch, sampling/mapping, and residual metric defined
below.

The Xsuite testbed's resolved
`steps/benchmark-code-against-isis-rcs-optics/reference-inputs/comparison-tolerances.json`
had SHA-256
`a7fbe56a89030be02aaaac03c1b0222d7f86482ea31639b3115ded42b30abe97` when
inspected; that testbed working-copy file was modified and uncommitted. Its
supporting records were:

- Feedback 0013, user-approved initial profile and scalar screening limits,
  SHA-256
  `a01d3b9581aa270f2a77fec168faa51cd1e4c8bbef51544acb80e16ba5e8da90`.
- Feedback 0016, user direction for the signed corrector x/y orbit-response
  limit, SHA-256
  `b8af712847309c0b9c84df228230dccb6cf23ba0915ce4ab41528a2af853bc82`.
- Feedback 0018, user-approved absolute circumference limit, SHA-256
  `f7d539e4067a82ac5d1857d79bca5af068c26246cd670c75c8fadbf9db2ac0b0`.
- Feedback 0020, user decision on full-campaign tune and chromaticity limits,
  SHA-256
  `d2d42c26ba0250379cb487a14c97ccbfc1f75936cc5b2a86de2409aef70ab216`.
- Feedback 0021, user-run attempt-032 assessment, SHA-256
  `1999429ca0ab1605471b63bc3385be266cc4023dd9db127b49bd17f47dd9b0a8`;
  report SHA-256
  `1bbe4570a873bcca7eed7e6540511407e18cd8f1e9a6d55576ef7e3e289ea595`.

The source material is campaign evidence. The user's 2026-10-28 direction in
this repository promotes the values below from that Xsuite recipe to the
shared provisional default, overriding the older testbed feedback request not
to generalise them without separate review. This promotion is explicitly for
screening and remains subject to PyPTC comparison and review.

## Shared default criteria

For each case, calculate residuals over verified matched samples. Use the
maximum absolute pointwise residual unless the table specifies a relative
metric. Compare full tunes on the same tune branch and phase profiles on the
same phase origin and unwrapped branch.

| Observable | Shared screening criterion | Units / method |
|---|---:|---|
| `betx`, `bety` | `max(abs(target-reference)/abs(reference)) ≤ 1e-3` | relative |
| `alfx`, `alfy` | `max(abs(target-reference)) ≤ 1e-3` | dimensionless |
| `mux`, `muy` | `max(abs(target-reference)) ≤ 1e-5` | turns |
| `dx`, `dy` | `max(abs(target-reference)) ≤ 1e-4` | m |
| `dpx`, `dpy` | `max(abs(target-reference)) ≤ 1e-4` | dimensionless |
| closed-orbit `x`, `y` | `max(abs(target-reference)) ≤ 1e-5` | m |
| closed-orbit `px`, `py` | `max(abs(target-reference)) ≤ 1e-5` | normalized coordinates |
| `qx`, `qy` | `abs(target-reference) ≤ 3e-6` per case | tune units; full tune on matched branch |
| `dqx_d_delta_p` | `abs(target-reference) ≤ 9e-4` per case | tune units per unit relative momentum |
| `dqy_d_delta_p` | `abs(target-reference) ≤ 3.5e-4` per case | tune units per unit relative momentum |
| circumference | `abs(target-reference) ≤ 1e-3` | m |
| signed corrector orbit response `x`, `y` | max absolute pointwise response residual `≤ 1e-4` per coordinate and signed case | m; compare `(perturbed - nominal)` in each engine over mapped samples |

Use the MAD-X/cpymad chromaticity definition already documented in the skill:
convert both results to `dQ/d(delta_p)` with
`delta_p=(p-p0)/p0`, including the version-appropriate MAD-X `beta0`
conversion. Do not apply the chromaticity limits to native derivatives with
unreconciled coordinates, higher-order chromaticity, or perturbation-response
chromaticity.

## Still pending or outside this baseline

- Cross-code perturbation-response tolerances for optics profiles, tunes, and
  chromaticities remain `pending-tolerance`. The response residual envelopes
  recorded in Xsuite attempt-030 are measurements, not limits. The corrector
  x/y orbit-response criterion above is the only response-family tolerance.
- Tune-from-tracking remains `pending-tolerance`.
- Turn-by-turn coordinates remain `non-equivalent` when the codes use
  different integration methods.
- Higher-order chromaticity and any observable not listed above have no shared
  tolerance; report measured differences as `pending-tolerance` after the
  observable has been made comparable.
- Minimum meaningful-response floors are application gates, not code-agreement
  tolerances.

## Maintenance and review

Use this table as the skill's default screening baseline until the PyPTC
comparison and user/physics review update it. For each code tested, preserve
the code/version, recipe, exact baseline revision/hash, case scope, per-case
differences, maximum and RMS residuals where useful, classifications, and
review state in that campaign's report and completion record. Do not adjust a
criterion silently to make a new code pass.

When evidence or review changes a value, append a dated revision entry here
with the old and new value, reason, source hashes, tested codes and revisions,
observed differences, and review state. Update the skill to point to this
file, and update its work diary and evidence record in the same reviewed work
unit. A PyPTC result is a comparison against this baseline; it is not by
itself a reason to relax or tighten a criterion. The user/physics reviewer
decides changes after reviewing matched definitions and residuals.

### Revision history

| Date | Change | Evidence / status |
|---|---|---|
| 2026-10-28 | Adopted Xsuite profile, scalar, circumference, and corrector-orbit criteria as the shared provisional default at the user's direction. | Xsuite attempt-032 passed the listed scalar/profile screens for its 38-case recipe; PyPTC comparison and user/physics review pending. |
