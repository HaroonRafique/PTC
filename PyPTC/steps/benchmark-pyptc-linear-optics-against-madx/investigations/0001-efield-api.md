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

This is an investigation and diagnostic result, not tolerance-based acceptance.
The full test and artifacts are retained under
`test_outputs/06_madx_efield_api/`. Its `report.md` and `result.json` record
the exact MAD-X binary, PyPTC library, source table, generated flat file,
mapped-exit counts, response summaries, and guard check. The final artifact
hashes are:

| Artifact | SHA-256 |
| --- | --- |
| `result.json` | `e1395727ba4c33b76456fb709387ca0e20d0a80950db693cec019da2017ef947` |
| `report.md` | `3c8cfe44d60dd1385eda5b5e2893d80edfd28ef2f8d0ac9a3aaed6cc8cd7c305` |
| Survey aligned profile CSV | `5161c1d305f5c501f0079120c2c37c9530a4932cbda9b5b7ec6ed8317ff0d2e8` |
| Survey comparison PNG | `031f75b5aa1158d01c7384ddc09b08a698f820f2908030734dd9ea6cfa1ea934` |
| Synthetic aligned profile CSV | `499b6290340d09c6b59debab43ba21d491fd52ce9bf6d0d5789c6fb2bdedb0a9` |
| Synthetic comparison PNG | `68707a49200d354852fa63d1f881e12bf9aeb623a13360445146a2f42810b607` |

The feature branch adds the ABI/Python path and tests. The files were built and
tested with the local `build_pyptc/libpyptc.so`; no parent PTC source was
modified. The exact Xsuite attempt-029 EFIELD source is still absent, so this
result does not reclassify that benchmark candidate.

## Final outcome

### Implemented surface

- Added `pyptc_add_madx_multipole_error` in `fortran/pyptc_api.f90` and
  `PTC.add_madx_multipole_error(...)` in Python. It maps MAD-X integrated
  normal/skew multipole errors for orders 0 through 20 into PTC's magnet
  multipole arrays. Thick-element coefficients are scaled by element length;
  thin-element values remain integrated. Parent-name error rows are split
  across matching slices in proportion to their lengths.
- Extended `read_madx_error_table` and `apply_madx_error_table` to retain and
  apply `K0L..K20L`, `K0SL..K20SL`, alongside `DX/DY/DS/DPHI/DTHETA/DPSI`.
- Nonzero EFIELD fields outside that implemented set are rejected before the
  lattice is mutated. In particular, monitor readout/scaling, RF multipole
  phase, and RF frequency/harmonic/lag fields remain unsupported.
- Bumped the additive PyPTC API level to 5 and included the symbol in the
  build/symbol smoke check.
- Added the repeatable example
  `python3 examples/06_madx_efield_api.py` and retained its complete input,
  MAD-X, PyPTC, aligned-profile, plot, report, and result evidence under
  `test_outputs/06_madx_efield_api/`.

### Verification

- `bash build/build_ptc.sh`: passed, including exported-symbol and ctypes
  checks for `pyptc_add_madx_multipole_error`.
- `python -m unittest discover -s tests -p 'test_efield_api.py' -v`: 3 parser
  tests passed, covering normal/skew values, field-only inclusion, and
  retention of unsupported values.
- `python examples/06_madx_efield_api.py`: completed two fresh-state MAD-X vs
  PyPTC cases and mapped 586/586 element exits in each. The survey table and a
  synthetic `K1L`/`K1SL` table were each applied with MAD-X `READMYTABLE` /
  `SETERR` and the PyPTC API. A nonzero `MREX` guard fixture was rejected as
  designed.
- The wrapped tune-response residuals were `8.34e-6` (Qx) and `-1.15e-6`
  (Qy) for the ISIS survey table, and `1.23e-5` (Qx) and `-8.92e-7` (Qy) for
  the synthetic multipole table. Synthetic `x`/`y` orbit-response residuals
  were below `1.1e-13 m`; maximum beta-response residuals were `6.61e-3 m`
  (`betx`) and `4.72e-3 m` (`bety`). These are reported measurements; no
  acceptance tolerances were supplied.

The implementation establishes that magnetic multipole EFIELD support can
be exposed without editing PTC core Fortran. It does not implement every
possible MAD-X EFIELD column, and it does not establish the tolerance for the
measured residuals. The correct disposition for the external Xsuite candidate
still depends on receiving and classifying that exact source table.
