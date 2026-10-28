# Iteration 0004 nominal-only runner gap

## Finding

Iteration 0004 inventories 38 candidates but runs only `nominal`. This is
hard-coded in `scripts/python/benchmark_pyptc.py`: `run_attempt()` names
`cases/nominal` directly, calls the MAD-X and PyPTC nominal functions once,
sets `executed_case_ids` to `['nominal']`, and writes only
`plots/cases/nominal.png`. The catalog marks all 37 perturbations
`blocked`/`deferred` because their case entry points have not been implemented.

The smoke suite encoded this behavior as expected: `test_only_nominal_is_included_and_remaining_candidates_are_blocked` asserted one
included case and 37 deferred cases. Consequently, the smoke test could pass
while the runner violated the skill's multi-case requirement. This is a
workflow implementation and validation gap, not a runtime failure in MAD-X or
PyPTC.

## Skill and campaign requirement

The pinned `iteration-0004/SKILL.md` requires the machine-readable inventory to
account for each candidate, independently invocable fresh-state execution for
each declared case, nominal-subtracted response records for perturbations, and
one combined plot for each executed case. A candidate can remain unexecuted
only with a specific evidence-backed disposition; missing runner code is not
technical evidence that the case is unsupported.

The 38-case set is sourced from Xsuite attempt-029 as a planning cross-reference
only. Each candidate still needs a PyPTC-specific applicability and API
assessment. Do not assume that importing the Xsuite case automatically proves
equivalent application on either MAD-X or PyPTC.

## Required correction

- Implement a catalog-driven per-case execution path that creates an
  independently auditable case state and runs both reference and target for
  every supported case.
- Retain nominal and perturbed records, calculate each engine's
  `perturbed - nominal` response, and create one case-level composite PNG for
  every case that runs.
- Keep only technically justified non-executed dispositions, with the exact
  missing capability or semantic evidence recorded per case.
- Replace the nominal-only smoke assertion with checks that prevent a
  nominal-only result from passing, verify execution accounting against the
  inventory, and require one valid plot-manifest entry per executed case.
- Run a bounded diagnostic smoke before presenting the next user-run attempt;
  do not label it as a user-run benchmark.

## Evidence and review status

- Skill snapshot: `iteration-0004/SKILL.md`, SHA-256
  `b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`.
- Latest diagnostic: `runs/attempt-011`; one nominal case executed and plotted.
- Catalog and runner: `scripts/python/benchmark_pyptc.py`.
- Smoke tests: `iteration-0004/tests/test_case_inventory.py`.
- No user-run result or multi-case benchmark acceptance is established by this
  feedback. Feedback is PyPTC campaign evidence under Task 6 and Task 9 of the
  [evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

Status: implementation correction in progress; no campaign review disposition.
