# Supplemental review: correct attempt-022 chromaticity coordinates

**Date:** 2026-10-31  
**Scope:** follow-up to user-run attempt 022 and feedback 0021. This does not
modify attempt 022's immutable raw files or change its overall disposition.  
**Disposition:** no acceptance; previous chromaticity conversion and related
classifications are superseded by investigation 0003.

## Correction

Feedback 0021 and the attempt-022 report multiplied PyPTC API chromaticities
by `beta0` and treated the returned values as `dQ/dPT`. That inference was
wrong. `lattice_GET_CHROM` explicitly uses PTC's `NOCAVITY + DELTA + ONLY_4D`
state. PTC's manual defines that normal-form coordinate as
`delta=(p-p0)/p0`; the PyPTC Fortran wrapper applies no additional scaling.
For the pinned MAD-X 5.02.00 binary, the `DQ1/DQ2` headers are also per
`DELTAP`, as confirmed by the exact-recipe `TWISS, DELTAP` scan and the MAD-X
5.06 release note documenting the later output-convention change. Compare the
two API values directly.

The fresh 8,192-turn PyPTC state scan also explains the earlier contrary
inference. The old scan supplied `dE/p0c` to PTC's default state, whose fifth
coordinate is `delta`; it therefore supplied approximately `beta0*delta`.
Its measured slope was lower by approximately `beta0`. A second run selected
the same `NOCAVITY + DELTA + ONLY_4D` state as the chromaticity getter and
passed `delta` directly. Its vertical slope agrees with the getter. This
identifies a likely separate coordinate-conversion defect in PyPTC's
user-facing tracking helpers and contradicts the old report's assumption that
the API getter and default-state tracking scan shared a coordinate.

Step-by-step definitions, source paths, manual references, diagnostic data,
hashes, and limitations are in
[`investigations/0003-chromaticity-coordinate-reassessment.md`](../investigations/0003-chromaticity-coordinate-reassessment.md).

## Attempt-022 values using the matching coordinate

The comparison below uses each case's existing native PyPTC and MAD-X scalar
values; no raw case output was changed.

| Plane | Nominal PyPTC minus MAD-X | Worst absolute difference in 38 cases | Provisional limit | Cases within |
|---|---:|---:|---:|---:|
| Horizontal | `+8.32020e-5` | `7.78212e-4` (`corrector_sp5_r5hd1_plus_1mrad`) | `9e-4` | 38/38 |
| Vertical | `+2.09457e-5` | `7.36948e-4` (`corrector_sp2_r2vd1_minus_1mrad`) | `3.5e-4` | 24/38 |

The scalar screen is therefore **90/190 out of tolerance**, not 152/190:
76 tune comparisons remain out, 14 vertical chromaticities are out, all
horizontal chromaticities and 24 vertical chromaticities are within, and all
circumferences remain within. The 92/532 profile result is unchanged. The
attempt still needs human review for tunes, phases, vertical chromaticity
responses, plots, and other pending items; no acceptance or `REP` follows.

## Follow-up

- Correct the next PyPTC benchmark runner/report implementation so it records
  PyPTC API chromaticity as `dQ/d(delta)` and does not apply `beta0` to that
  value. Keep MAD-X handling tied to the pinned executable version.
- Investigate and repair PyPTC tracking-helper conversion from Python energy
  deviation to the PTC default state's momentum-deviation coordinate, including
  the inverse output and longitudinal coordinate convention. Add an
  implementation regression test before relying on tracking-derived tunes.
- Route the reusable state/coordinate lessons to the separate
  `isis-modelling-agents` skill-development process; do not edit the skill
  snapshot in this follow-up.

## Evidence identities

- Attempt-022 report SHA-256:
  `a736a6e532cf21f0084a9291293c68a60fe6be6f8348ef834a94398064853bf6`.
- Attempt-022 result SHA-256:
  `500a35cf169e7b08d5ecbdc3f8da85211f7748cca43fde76ebbaaec064452c87`.
- Investigation 0003 and state-scan artifact identities are listed in that
  report. The original skill, attempt bundle, and feedback 0021 remain
  unchanged; this record supersedes only its chromaticity-coordinate
  interpretation.

This follow-up is PyPTC campaign evidence linked to the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
