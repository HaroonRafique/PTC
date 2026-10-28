# User-run assessment: attempt 019

Date: 2026-10-28  
Run class: user-run  
Disposition: assessed; no acceptance  
Skill snapshot: `iteration-0004/SKILL.md`, SHA-256
`b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`

## Assessment against the benchmark skill

Attempt 019 is a complete execution of the declared case inventory, but it is
not a complete benchmark under the pinned skill and is not accepted. The
canonical outcome `incomplete-chromaticity-and-plot-review` is appropriate.

The run is a user-run on accepted snapshot admission
`attempt-20261027T194128Z`. It records the accepted input, flat-file, and
MAD-X executable identities and separately identifies a current API-level-5
PyPTC build. The effective recipe records the ordered five inputs, the 2023
strength overlay, `synchrotron`, `a1=b1=0`, and zero trim variables. The
candidate PyPTC source revision is `0ed4f9b2e293e5cd25c829624a0bff56fed62748`;
the attempt also records its uncommitted source-tree status and runner/module
hashes in `manifest.env`.

All 38 declared cases executed and were plotted: nominal, 28 signed corrector
cases, the QF K1 perturbation, six isolated QF misalignments, the full local
survey table, and its verified intersection. There were 37 completed
perturbations, no failed/blocked/unsupported cases, and none left unexecuted.
The inventory distinguishes these candidate cases from equivalence to the
Xsuite testbed: the exact Xsuite attempt-029 EFIELD table is not available in
this repository.

The nominal sample map is verified: all 586 MAD-X element exits are joined to
the corresponding PyPTC nodes using flat-file fibre index, element name, and
occurrence, with physical positions checked to `1e-9 m`. The run retains the
804 raw PyPTC node rows/printer groups and 586 matched boundaries. Thick
tracking completed for 64 turns with 65 samples from the initial state through
turn 64. MAD-X `PTC_TRACK` and PyPTC share the PTC engine, so this is not an
independent tracking-engine validation; turn residuals remain pending
tolerance.

Two required review items remain open:

1. **Chromaticity is blocked.** MAD-X reports `dQ/dDELTAP`; the PyPTC public
   API's `lattice_GET_CHROM` derivative coordinate and tune estimator are not
   established by this evidence. The native values and native differences are
   retained, but target `dQ/d(delta_p)` values and signed common-coordinate
   differences are not. No chromaticity tolerance is asserted.
2. **The composites fail the normal-size readability check.** There is one
   PNG per case and all 38 paths exist, but the nominal composite is
   `3300 x 36800` pixels and the survey-table composite is `3300 x 38400`.
   The nominal manifest has 23 panel groups, including both an overview and
   the full profile set. At normal viewing size the labels, ticks, and data
   are too compressed to review. Raster size/DPI does not satisfy the skill's
   explicit dense-composite readability check. The plot manifest and report
   correctly point to one composite per case, but the nominal working-point
   group also lacks converted target chromaticity and a verified common
   chromaticity difference.

No observable-specific cross-code tolerance or minimum meaningful-response
floor has been reviewed. The 14 profile residual summaries and perturbation
response summaries therefore remain `pending-tolerance`; no optics agreement
or physics-acceptance claim follows. The report correctly discloses these
limits and the unresolved chromaticity convention.

The full-table EFIELD evidence is strong for PyPTC application (the source
table is retained verbatim, and the API summary records all 38 applied
records), and the MAD-X `ESAVE` output is retained with a hash. However, the
bundle does not include a normalized per-component source-versus-MAD-X-ESAVE
audit or verdict. The raw tables can be reviewed, but the skill's
source-to-reference applied-state audit is not yet explicit; add that audit
before treating this case as fully reviewed.

## Comparison with existing PyPTC examples and tests

The generated workflow is consistent with the repository's public EFIELD
interface: it uses `PTC.apply_madx_error_table(...)` on fresh case-local
states, as does `examples/06_madx_efield_api.py`, and retains 38 source rows,
38 applied PyPTC records, the unmodified source table, and MAD-X's saved
`applied_error_table.tfs`. The existing example and `tests/test_efield_api.py`
also cover parser handling of normal/skew integrated multipoles, nonzero
unsupported fields, and field-only rows. Attempt 019's full local survey table
has zero K coefficients, so that full-table case exercises alignment records;
the separate `field_sp0_qf_k1_plus_0p1pct` case and the existing synthetic
K1L/K1SL example provide the magnetic-field coverage. This comparison is
learning evidence only; it was not used to construct the independent attempt.

The exact Xsuite attempt-029 EFIELD table remains unavailable. Therefore the
local table's application does not establish byte-for-byte or semantic
equivalence to the Xsuite candidate. The bundled 2023-overlay recipe and
case-local fresh-state structure are consistent with the local PyPTC
workflows. This assessment does not re-run the physics examples or tests.

## Required next work

- Resolve and document the PyPTC chromaticity coordinate/method, or define a
  like-for-like tune-versus-momentum comparison, before calculating a common
  `dQ/d(delta_p)` value.
- Redesign composites so a dense nominal plot and a representative perturbed
  plot are readable at normal viewing size while retaining one combined PNG
  per case, every required observable/response group, signed residuals,
  mappings, and scalar context.
- Review and record observable-specific agreement tolerances and
  minimum-meaningful-response floors before making a benchmark claim.
- Keep the external EFIELD equivalence claim open until the exact Xsuite
  source table is available and audited.
- Add a normalized source-to-MAD-X-`ESAVE` per-component application audit
  for the full survey-table case; the raw output table is retained but not
  compared in a machine-readable verdict.

## Provenance

| Evidence | SHA-256 |
|---|---|
| Skill snapshot | `b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b` |
| Attempt report | `bc319ad6653196d96e39f977affef6a8028f6e0986f7775b2a9a54a80769d114` |
| Attempt result | `d3c4a1ea736d8be2e538f460242f040aed34fcdabc7a960fd27b9979a09c4b84` |
| Attempt manifest | `6de6fefb460c3c727debbed1662ed60b8c8c8305e40119b302f706a42dacc694` |
| Case inventory | `c31e175ede2d0280117d6f9a19e2facf56d849ab410b53c1953a74bdbe186af9` |
| Plot manifest | `bfec6046303c6088a851017417d40858dd17a1aeab14aa0eeae888ee45eb6dd2` |
| Harness check log | `53e31304893a95f23396beb63bc21e2a70a2ffba5fa8920cbfd6caca9e950ed2` |
| Nominal composite | `4dd815e48913e23e0463ecdbe0372250f4a916629c86cf5052cffafd245d8e98` |
| Current API-5 library | `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c` |
| Candidate PyPTC source revision | `0ed4f9b2e293e5cd25c829624a0bff56fed62748` |
| Attempt orchestrator | `b842d1adbfebe15abe727a63d3be160135ae9f1261e30927580a1915d96d6d6a` |
| Workflow module | `6644a361fd68c4defe17231e9596d461aba2efe0a07410722002e325e79f7d29` |
| Accepted MAD-X executable | `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04` |
| Local EFIELD source | `c864ea0ac6bab8159d5763e9134d8788e6ad006352ae8034a37859bfa95351b6` |

The attempt's `harness-tests.log` records ten passing inventory/harness checks.
This is local Task 6 run evidence and Task 9 review maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
No `REP`, `EVAL`, physics acceptance, or publication-plan repository update is
created by this assessment.
