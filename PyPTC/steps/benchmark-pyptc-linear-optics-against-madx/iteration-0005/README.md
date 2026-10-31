# Iteration 0005: API-5 chromaticity and shared screening baseline

This fresh skill application snapshots the committed shared skill revision
`3aad35af0ad53337fc259e14d0d614fd55821aa`. The exact local skill snapshot is
`SKILL.md`, SHA-256
`b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae`.
Its linked tolerance baseline is copied to `references/tolerance-baseline.md`,
SHA-256
`77bb8564d562a0a72b1eae738b097d6d614177f40db4abe01f81cb5236d671c8`, ID
`OPTICS-BASELINE-2026-10-28-v1`.

The user-facing entry points stay at the step level:

```bash
./scripts/shell/setup-benchmark.sh
./scripts/shell/benchmark-pyptc-attempt.sh
```

The runner takes no arguments for a user run and auto-allocates the next
`attempt-NNN` directory under `runs/`. It declares and assesses all 38 current
candidate cases. The Xsuite testbed is used only as a case-inventory
cross-reference. Every included case gets fresh engine state, per-case scope
and capability records, normalized profiles/scalars, and one combined PNG
when its element map verifies.

This iteration applies the linked profile/scalar screening limits per case,
including full tunes on the MAD-X branch and API-level-5 PyPTC chromaticity
conversion from `dQ/dPT` to `dQ/d(delta_p)` using run-local `beta0`. It records
the corrector x/y response criterion while leaving its application state
pending until a meaningful-response floor is reviewed. Other response families
without shared criteria remain `pending-tolerance`. Full and isolated EFIELD
cases now retain a normalized source-to-MAD-X-`ESAVE` component audit.

The comparison is explicitly scoped to uncoupled plane Twiss. Coupling is not
evaluated, and the report must limit any resulting conclusion to that scope.
Each case records the effective `a1=b1=0` state, PTC harmonic metadata, and the
RF-active determination from the pinned source inputs. Thick tracking remains
the default separate diagnostic and does not gate transverse optics results.
Thin tracking remains an optional MAD-X-only diagnostic.

The iteration-specific module was assembled against this skill revision. It
carries forward the earlier case inventory and runner scaffolding, and reuses
the established PyPTC named-element boundary/tracking adapters from iteration
0003; no prior attempt output is used as measurement input. That reuse is
explicit in source and provenance. The old iteration-0004 snapshot and attempt
bundles remain unchanged. The new plot renderer reduces the prior 33,000+ pixel
nominal composite to compact stitched per-case groups; normal-size visual
inspection is still required after a user run.

No user-run benchmark or acceptance result is implied by preparing this
iteration. The first full run should be assessed against this exact snapshot.

User-run attempt 020 has since been assessed against this snapshot. Its outcome
is `incomplete-perturbation-execution`: 30 of 38 cases completed, while eight
misalignment/EFIELD cases stopped in the source-to-ESAVE audit before PyPTC ran
because the TWISS parser required an `S` column. The case composites were not
readable at normal size. See step feedback
[`0019-user-run-attempt-020-assessment.md`](../feedback/0019-user-run-attempt-020-assessment.md).

## Runner correction after attempt 020

The user run exposed two harness issues. The EFIELD source-to-ESAVE audit now
uses the generic TFS table parser, which does not require `S`; the TWISS parser
continues to require named rows and `S`. A targeted check parsed the retained
38-row source EFIELD table, 38-row MAD-X ESAVE table, and 586-row TWISS table.

Per-case output remains exactly one vertically stitched PNG containing the
declared panel groups. Each strip is now 1600 × 850 pixels with more room for
labels and tables. The scalar panel uses the `case_working_point` name and
case-relative labels. The manifest includes 100% zoom/scroll guidance; this
does not substitute for human visual inspection. The next run should be
attempt 021. The skill snapshot and tolerance baseline remain unchanged, so
this is a runner fix rather than a new skill application.

User-run attempt 021 used the correction above. The generic EFIELD parsing
worked, but `audit_error_table_esave()` then failed on a source-row indexing
`NameError` for the same eight cases before PyPTC ran. The full assessment,
including refreshed hashes, nominal results, and plot inspection, is in step
feedback [`0020-user-run-attempt-021-assessment.md`](../feedback/0020-user-run-attempt-021-assessment.md).

User-run attempt 022 completed all 38 cases using the corrected audit indexer.
The six isolated misalignment and two survey EFIELD cases each passed their
source-to-ESAVE audit with 3,838 compared values and zero mismatches. Attempt
022's profile and scalar results remain outside provisional limits, and the
corrector response table still has a readability defect. See
[`0021-user-run-attempt-022-assessment.md`](../feedback/0021-user-run-attempt-022-assessment.md)
for exact findings and hashes. The run is complete for human review, not
accepted.

Attempt 022 is the latest user-run result for this skill snapshot. Its full
execution resolves the previous runner audit failure; no new skill revision is
implied. Any later run should follow the reviewed runner/readability fixes and
retain the same skill and tolerance hashes unless a separately reviewed skill
update is applied.

The follow-up runner correction uses the declared `source_occurrence` and
`source_index` dictionaries, and the deterministic checks now import the
iteration-0005 module rather than the older step-level module. A no-`S`
duplicate-name source/ESAVE fixture verifies all records and fields. The
working-point table and nominal overview have been simplified to avoid the
crowding seen in attempt 021; the report now gives chromaticity values in a
small table, describes the applied conversion and open discrepancy, and does
not imply that failed cases reached target application. The focused runner
suite passed 11 tests. A renderer-only preview based on attempt-021 nominal
data is `test_outputs/benchmark-pyptc-linear-optics-against-madx/runner-preview-attempt-021.png`;
it is not a new benchmark result. The skill and tolerance snapshot are
unchanged. The next full run should allocate attempt 022.
