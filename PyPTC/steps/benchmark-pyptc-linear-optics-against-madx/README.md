# PyPTC linear-optics benchmark against MAD-X

This is an independent skill-test campaign, separate from
`steps/admit-code-to-isis-rcs/`. Its admission basis is the user-accepted
snapshot attempt copied to
`admission_basis-accepted-attempt-20261027T194128Z/`. No failed admission
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
./iteration-0003/setup.sh
./scripts/shell/benchmark-pyptc-attempt.sh
```

The runner needs no arguments and automatically uses the step's `.venv` after
setup. New numbered run bundles are placed under `runs/attempt-NNN/`; inspect
`runs/INDEX.md` for the run list and review dispositions. Each case's data is
under `cases/<case-id>/` and its composite plot is under
`plots/cases/<case-id>.png`. Set
`PYPTC_BENCHMARK_RUN_CLASS=agent-diagnostic` only for an agent smoke run; the
default is `user-run`.

Tracking defaults to thick MAD-X `PTC_TRACK` and accepts the optional
`PYPTC_BENCHMARK_TRACKING_MODE=both` setting to also retain a separately
classified thin-mode diagnostic. See the iteration 0003 README for the
limitations and command details. Iteration 0003 is a feedback-driven
correction of the prior harness, not an independent fresh skill implementation.
The stable shell orchestrator is under `scripts/shell/`; Python workflow code
is under `scripts/python/`. Attempt bundles contain results and provenance,
not executable runner scripts.
The pre-redesign timestamped bundles in
`test_outputs/benchmark-pyptc-linear-optics-against-madx/` remain archived at
their original paths.

Iteration 0001 records the first skill attempt and its blocked profile map.
Iteration 0002 was generated from the updated skill at
`f5293a3754dc8c4e9a6a4ba987603924b91949f3` and uses the newly accepted
snapshot attempt `attempt-20261027T194128Z` as its evidence basis. It adds a
Python adapter around PTC's named orbit-marker interface, verifies element
exit identity/occurrence and position, and writes aligned profile residuals
and the nominal case composite when that map passes. It reuses the accepted
MAD-X 5.02.00 binary, PyPTC library, source snapshot and flat file by hash; it
does not change machine strengths or resplitting. Chromaticity remains blocked
until the PyPTC derivative coordinate is established, and bounded tracking
remains blocked until a matched complete per-turn workflow is verified. The
agent diagnostic smoke run `attempt-20261027T223232Z` verified all 586 named
element exits and completed target tracking for 64 turns without loss. MAD-X
retained 65 rows but produced non-finite coordinates, so the cross-code
tracking comparison is blocked as reference evidence, not classified as a
numerical mismatch. The composite plot is retained for user review; no
tolerance or physics acceptance has been set. Numerical differences without
reviewed observable-specific tolerances remain
`pending-tolerance`.

Iteration 0003 keeps that exact skill snapshot and the verified boundary
adapter, while correcting the tracking route in response to feedback 0005 and
the [thick/thin tracking investigation](diagnostics/tracking-mode-investigation-20261028.md).
It uses thick MAD-X `PTC_TRACK` by default. Thin mode is optional and remains a
reference-only diagnostic until a valid slicing policy and matching PyPTC
control are established. Iteration 0003 agent smoke outcomes, including the
default thick run and optional thin block, are recorded in
[`feedback/0006-iteration-0003-thick-tracking-smoke.md`](feedback/0006-iteration-0003-thick-tracking-smoke.md)
and the review ledger; they are not a user-run skill test.

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

The follow-up
[`diagnostics/ptc-orbit-marker-capability-20261027.md`](diagnostics/ptc-orbit-marker-capability-20261027.md)
probes the existing PTC `SETORBITMARKER` support and records a complete
fibre-boundary identity match through the Python-accessible PTC commands.

The tracking-mode probe
[`diagnostics/tracking-mode-investigation-20261028.md`](diagnostics/tracking-mode-investigation-20261028.md)
records the available MAD-X thick `PTC_TRACK` route, the classic thick `TRACK`
limitation, and the failed ten-slice `MAKETHIN` experiment. The next runner
should default to thick tracking and offer thin tracking only where a
validated slicing recipe is available. MAD-X `PTC_TRACK` shares the PTC
tracking engine with PyPTC and is not an independent tracking-engine
validation; it remains useful for exercising a valid thick-mode reference and
record path. The thin-mode investigation is still open.

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
skill evaluation: no matched baseline was run. Agent runs are bounded
diagnostics, not user-run skill tests or physics reviews. A `REP-####`
chronology record is required by the benchmark skill when a
code/reference/recipe/run reaches technical completion; an incomplete attempt
creates no `REP`, `EVAL`, physics claim, or acceptance. Keep full run bundles
here and do not copy bulky outputs into the publication repository.
