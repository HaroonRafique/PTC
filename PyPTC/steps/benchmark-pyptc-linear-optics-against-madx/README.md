# PyPTC linear-optics benchmark against MAD-X

This is an independent skill-test campaign, separate from
`steps/admit-code-to-isis-rcs/`. Its only admission basis is the accepted
snapshot attempt copied to
`admission_basis-accepted-attempt-20261027T082315Z/`. No failed admission
attempt is used as a benchmark input, and the historical admission campaign
is left intact.

The accepted attempt established snapshot-scoped admission only. It did not
review PyPTC optics, a profile boundary map, chromaticity normalization, or any
cross-code tolerance. The copied basis preserves the accepted recipe, five
hash-pinned inputs, generated flat file, reference TWISS, and their source
evidence. The benchmark runner must not silently change the recipe, harmonic
settings (`a1 = b1 = 0`), trim settings, or flat-file splitting.

## Operator workflow

From this directory:

```bash
./iteration-0001/setup.sh
./iteration-0001/run_benchmark.py
```

The runner needs no arguments and automatically uses the step's `.venv` after
setup. Outputs are placed under
`test_outputs/benchmark-pyptc-linear-optics-against-madx/`. Set
`PYPTC_BENCHMARK_RUN_CLASS=agent-diagnostic` only for an agent smoke run; the
default is `user-run`.

Iteration 0001 is deliberately a first diagnostic. It reruns the pinned
MAD-X 5.02.00 binary from the accepted admission record and runs PyPTC from the
accepted flat file. It writes raw optics records, scalar differences, a
longitudinal-position mapping diagnostic, and a report. It does not claim
profile agreement when the boundary map is unresolved. No reviewed observable
tolerances have been supplied, so numerical differences remain
`pending-tolerance`.

## Review sequence

Assess the runner first against the pinned skill, then compare its output with
the existing PyPTC examples/tests for learning. Record evidence and feedback
locally in this step, including failures and limitations. Do not edit the
shared skill from this campaign. Any skill revision is handled separately and
must precede a fresh regenerated iteration. Keep the Xsuite effort independent.

The diagnostic report
[`diagnostics/sampling-grid-investigation-20261027.md`](diagnostics/sampling-grid-investigation-20261027.md)
explains the 586 MAD-X element rows versus 375 PyPTC orbit-node rows, verifies
the shared lattice provenance, and records the evidence limits and possible
sampling approaches. It is not a benchmark acceptance decision.

## Evidence-gated publication alignment

This campaign follows the prospective campaign-evidence practice in Task 6
and the event-driven `skill_used` / `campaign_evidence_reviewed` maintenance in
Task 9 of the
[evidence-gated publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
The exact skill revision, target and reference identities, attempt IDs,
hashes, outcomes, residual limits, review state, and feedback are recorded in
this step's manifests, `feedback/`, `review_ledger.csv`, and the local PyPTC
work diary.

This is an observational campaign episode, not a controlled baseline-versus-
skill evaluation: no matched baseline was run. The current agent preflight is
not a user-run skill test or physics review. A `REP-####` chronology record is
required by the benchmark skill when a code/reference/recipe/run reaches
technical completion; this first attempt is explicitly incomplete and creates
no `REP`, `EVAL`, physics claim, or acceptance. Keep full run bundles here and
do not copy bulky outputs into the publication repository.
