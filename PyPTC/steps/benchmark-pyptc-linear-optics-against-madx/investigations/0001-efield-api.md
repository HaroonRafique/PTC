# PyPTC MAD-X EFIELD API investigation

## Objective and provenance

- Repository: PyPTC
- Base commit: `32933d954fb794a5bb51790883b0b2d211bcaf82`
- Feature branch: `feature/pyptc-efield-api`
- Date started: 2026-10-28
- Objective: expose MAD-X `READMYTABLE`/`SETERR` EFIELD application through a
  supported Python API, compare PyPTC and MAD-X side by side, and retain a
  complete reproducible test as an example.
- Publication-plan link: [Evidence-gated agents publication plan](../../../../../../../../Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md)

All PyPTC implementation work is confined to this checkout and this feature
branch. Parent PTC sources are read-only references; no PTC core Fortran edits
are planned. No merge or feature-branch deletion is authorized by this record.

## Initial findings

The current `pyptc.apply_madx_error_table(...)` reader only retains
`NAME/DX/DY/DS/DPHI/DTHETA/DPSI`. Its native wrapper calls
`MAD_MISALIGN_FIBRE`; this is a six-component alignment implementation, not a
general EFIELD/`SETERR` implementation.

The checked-in `apr_2026_survey_corrected.tfs` contains 38 records. Inspection
of all numeric columns found nonzero values only in `DX`, `DY`, `DPHI`,
`DTHETA`, and `DPSI`; `DS` and every other EFIELD column are zero for this
particular file. Therefore that file alone does not demonstrate a need for a
multipole-error API. The exact EFIELD source from Xsuite attempt 029 was not
adopted into PyPTC attempt 017, so equivalence to that external candidate must
not be assumed.

The C ABI shim already reads/writes PTC magnet multipole deviation arrays for
AC and ramp controls. This shows the relevant data are reachable from the
additive PyPTC Fortran layer, but does not establish that generic MAD-X EFIELD
semantics can be implemented by a Python-only wrapper. The exact mapping,
units, supported columns, and unsupported cases will be established against
MAD-X before the API is declared complete.

## Evidence and review status

This is an investigation record, not a benchmark result or acceptance. The
initial evidence is source inspection and a nonzero-column count on the local
reference table. Side-by-side validation, final hashes, supported-field
coverage, and any remaining limitations will be added in a follow-up section
before the work is presented for review.

## Final outcome

Pending implementation and side-by-side validation.
