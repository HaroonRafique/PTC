# Case inventory runner smoke assessment

Date: 2026-10-28
Run class: agent diagnostic smoke
Final smoke run: `runs/attempt-007`
Preceding smoke: `runs/attempt-006` (superseded for final evidence)
Pinned skill: iteration 0003, revision
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`, SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Evidence-gated publication plan: Task 6 campaign evidence and Task 9 review
maintenance in `docs/plans/2026-10-23-evidence-gated-agents-publication.md`.

## Runner changes and checks

The step-level runner now materializes the complete 38-case cross-reference
from Xsuite testbed attempt 029 into `campaign_case_inventory.json` and
individual `cases/<case-id>/case.json` and `case_status.json` records. Its
source inventory is pinned by SHA-256
`c19abadada9efd8bd336ef4e0c587c82e464e2d714e8f13018c05389d493c67c`; the
case identities and settings are detailed in feedback 0010. The nominal case
status and plot path are updated after execution.

Shell syntax validation and Python bytecode compilation passed. Running
`./scripts/shell/benchmark-pyptc-attempt.sh --smoke` completed as
`incomplete-chromaticity-and-plot-review` in attempt 007. The run contains 38
case directories, one executed nominal case, 37 explicitly blocked
non-nominal cases, and one nominal composite PNG. Attempt 006 used the same
inventory but its nominal `case_status.json` incorrectly retained
`plot_status=not-produced`; attempt 007 fixes and verifies that status.

Attempt 007 evidence hashes:

| Artifact | SHA-256 |
|---|---|
| `report.md` | `71e1d0ce64dd944bfd3949769b88150432f83a13892fd8eb6f9da137f2cbcbd1` |
| `result.json` | `e60b5a65aaac24f62a51353feb86819fd9109fdd2255e2d2348cc87da86518fb` |
| `manifest.json` | `8f2891d69c4904f80f70fb237f5ed57279dcf229774696b86e44288c32f9ebe2` |
| `campaign_case_inventory.json` | `ff7733027ecbaa9a09ab315a4c288a0764a2fac252429ff8c6b127ef0cda65df` |
| `plot-manifest.json` | `8233e7d16c752fdaa83b5622dea719bb1c0db4b9d69f82ac5b96eebd34a22363` |
| `harness-tests.log` | `c3fa15e905cdbd62fb5a6625285e60473b55d8241fc0fa9bfc086d6cc95b021e` |
| `manifest.env` | `96ec4062dbdc5e14568739b981e4ff2aae2e87b2935949f4adac618fa0c05bea` |

Runner source hashes at the smoke run:

| Source | SHA-256 |
|---|---|
| `scripts/python/benchmark_pyptc.py` | `b6a894c01da2218582893e3511f4297d44111a89d3ffd68a1dc5e48a9445bb88` |
| `scripts/shell/benchmark-pyptc-attempt.sh` | `527fad9e0af715021a4a73dad2383330dc61139e5023211135bc5270cb163e18` |

## Limitations and disposition

This change makes all cases visible and prevents the previous silent nominal-
only inventory. It does **not** implement the non-nominal physics runs. All 28
corrector cases, the field-strength control, six alignment components, and two
survey-table cases remain `blocked-not-implemented`; no perturbation responses
or plots were fabricated. Although PyPTC has public misalignment and error
table methods, this benchmark runner has not yet built the matching fresh-state
MAD-X/PyPTC case application, audits, response metrics, and per-case
composites. The current Python API also lacks first-class direct lattice
strength setters for the corrector and K1 cases. The user should not treat
attempt 007 as the requested complete multi-case benchmark.

Disposition: agent diagnostic, inventory/orchestration smoke only; no
benchmark acceptance, `REP`, `EVAL`, or physics claim. The next work must
implement each case's reference/target application and response evidence, or
retain an evidence-backed non-applicable/unsupported/blocked classification.
This local record supports Task 6 evidence and Task 9 review maintenance in
the evidence-gated agents publication plan.

## Retention

The step's prune script still targeted the pre-redesign timestamped
`test_outputs/` directory. It was corrected to target `runs/attempt-NNN/` and
to validate the step-level attempt ID format. After the ledger and feedback
records were complete, its dry run identified attempts 001-004 for pruning;
`--apply` removed those bundles. Their report/result/manifest hashes and
outcomes remain in feedback 0007/0008 and the review ledger. Attempts 005-007
are the three retained bundles. The human-maintained run index retains the
historical rows and links them to feedback.
