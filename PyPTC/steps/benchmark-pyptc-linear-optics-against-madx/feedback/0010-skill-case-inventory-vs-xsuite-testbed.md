# Skill case requirements and Xsuite testbed inventory

Date: 2026-10-28
Related assessment: user-run `runs/attempt-005`, feedback 0009
Pinned PyPTC skill snapshot: SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Xsuite reference checkout: `/home/hr/Codes/agentic_xsuite_test`, HEAD
`1461498061278abcf45a993be7ed30e77e88b7cd`
Xsuite case inventory: `steps/benchmark-code-against-isis-rcs-optics/runs/attempt-029/campaign-case-inventory.json`, SHA-256
`c19abadada9efd8bd336ef4e0c587c82e464e2d714e8f13018c05389d493c67c`
Inventory generator:
`steps/benchmark-code-against-isis-rcs-optics/scripts/xsuite/write_complete_case_configs.py`,
SHA-256 `18ab7bb134dc37ba5376417b4b2c6a69c26ebfe07129df3944f11dba925d9278`.

## Does the pinned skill name every exact case?

No. The pinned skill states case categories and evidence/coverage rules, not a
fixed machine-specific list of IDs. It says to run every fair comparison
exposed by the capability inventory; requires independent fresh-state entry
points for declared nominal/corrector/misalignment/error-table cases; and sets
coverage conditions for complete bidirectional corrector response, error-table
intersections, and staged field/alignment controls. Therefore a campaign must
declare its case inventory and justify applicability/coverage, but the literal
38 Xsuite IDs below are testbed-specific examples, not names embedded in the
generic skill text.

Attempt 005's runner has a hardcoded `cases/nominal` execution path and records
`perturbation_cases: []`. It did not construct an inventory or attempt any
non-nominal case. The nominal PNG is not evidence that the broader skill case
inventory ran. Feedback 0009 noted missing perturbation coverage; this
follow-up records the concrete Xsuite cross-reference requested by the user.

## Xsuite attempt-029 case inventory (38 total)

### Nominal (1)

- `nominal`

### Corrector response: 14 source-identified correctors, both polarities (28)

- `corrector_sp0_r0hd1_plus_1mrad`, `corrector_sp0_r0hd1_minus_1mrad`
- `corrector_sp0_r0vd1_plus_1mrad`, `corrector_sp0_r0vd1_minus_1mrad`
- `corrector_sp2_r2hd1_plus_1mrad`, `corrector_sp2_r2hd1_minus_1mrad`
- `corrector_sp2_r2vd1_plus_1mrad`, `corrector_sp2_r2vd1_minus_1mrad`
- `corrector_sp3_r3hd1_plus_1mrad`, `corrector_sp3_r3hd1_minus_1mrad`
- `corrector_sp3_r3vd1_plus_1mrad`, `corrector_sp3_r3vd1_minus_1mrad`
- `corrector_sp4_r4hd1_plus_1mrad`, `corrector_sp4_r4hd1_minus_1mrad`
- `corrector_sp4_r4vd1_plus_1mrad`, `corrector_sp4_r4vd1_minus_1mrad`
- `corrector_sp5_r5hd1_plus_1mrad`, `corrector_sp5_r5hd1_minus_1mrad`
- `corrector_sp5_r5vd1_plus_1mrad`, `corrector_sp5_r5vd1_minus_1mrad`
- `corrector_sp7_r7hd1_plus_1mrad`, `corrector_sp7_r7hd1_minus_1mrad`
- `corrector_sp7_r7vd1_plus_1mrad`, `corrector_sp7_r7vd1_minus_1mrad`
- `corrector_sp9_r9hd1_plus_1mrad`, `corrector_sp9_r9hd1_minus_1mrad`
- `corrector_sp9_r9vd1_plus_1mrad`, `corrector_sp9_r9vd1_minus_1mrad`

### Field-strength control (1)

- `field_sp0_qf_k1_plus_0p1pct`

### Single-element quadrupole alignment components (6)

- `sp0_qf_dx`
- `sp0_qf_dy`
- `sp0_qf_ds`
- `sp0_qf_dphi`
- `sp0_qf_dtheta`
- `sp0_qf_dpsi`

### Survey error-table cases (2)

- `survey_error_table`
- `survey_error_table_verified_intersection`

Total: 1 nominal + 28 corrector + 1 field-strength + 6 alignment + 2 survey
error-table cases = 38. This count is the `complete_case_count` in the
attempt-029 inventory; the selected list and source-file hashes are retained
in that artifact. The IDs above are reproduced from its `selected_case_ids`.
These are attempt-029 Xsuite cases, not proven PyPTC/MAD-X equivalents. They
are a cross-reference for PyPTC planning; each still needs a PyPTC/MAD-X
applicability and application assessment before it can be claimed equivalent.

## Required PyPTC follow-up

Before another attempt, build and review a machine-readable PyPTC campaign
inventory against these 38 cases and the pinned skill. For each case state
`included`, `not-applicable`, `unsupported`, or `blocked`, with evidence and a
reason. Do not silently reduce the inventory to nominal. Implement comparable
cases with independently invocable fresh-state entry points, per-engine
application evidence, response residuals, and one composite plot per case.
Preserve the two survey-table cases and the full corrector element/polarity
matrix. Keep cases that are not yet executable visible as blocked/deferred,
not absent.

No shared skill or Xsuite testbed file was modified. This local feedback
supports Task 6 evidence and Task 9 review maintenance in the evidence-gated
agents publication plan. It creates no `REP`, `EVAL`, tolerance decision, or
physics acceptance.
