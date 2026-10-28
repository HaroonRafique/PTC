# Iteration 0004 case execution runner fix and smoke

Date: 2026-10-28  
Run class: agent diagnostic only  
Final diagnostic: `runs/attempt-017`  
Skill snapshot: `iteration-0004/SKILL.md`, SHA-256
`b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`

## Finding and correction

Feedback 0014 identified the nominal-only defect. The catalog listed 38 cases,
but `run_attempt()` hard-coded a single nominal run and the smoke test asserted
that the other 37 cases were deferred. The test therefore passed without
checking the skill's per-case execution, response, and plot requirements.

The runner now iterates the included case inventory from independent case-local
states:

- 28 corrector cases edit only the named `ISIS.strength` kick variable in a
  fresh input copy, run the pinned MAD-X recipe, regenerate a flat file with
  the accepted PTC resplitting scripts, and load that file in a fresh PyPTC
  process.
- The SP0_QF K1 case applies and records an instance-level MAD-X strength
  override before the same fresh TWISS/flat-file workflow.
- Six isolated SP0_QF alignment cases generate case-local EFIELD tables with
  only the requested component nonzero. MAD-X `READMYTABLE`/`SETERR` and
  PyPTC `apply_madx_error_table` consume the same table from fresh states.
- The verified survey intersection retains the six EALIGN components and
  zeros non-alignment field terms before both fresh applications.
- The full EFIELD survey case is explicitly `unsupported`: current
  `pyptc/error_table.py` reads only NAME/DX/DY/DS/DPHI/DTHETA/DPSI and does not
  apply the table's non-alignment field components. It is not represented as a
  completed case.

Each executed perturbation retains both engines' nominal and perturbed profile
and scalar data, per-engine `perturbed - nominal` responses, response residuals,
and one composite PNG. Native chromaticity responses remain blocked because
the PyPTC derivative coordinate is unresolved. No response tolerance or
minimum meaningful-response floor has been reviewed; comparable response
results remain `pending-tolerance`.

## Final diagnostic evidence

Attempt 017 completed 37 of 38 candidate cases: nominal plus 36 perturbations.
All 37 executed cases mapped 586/586 MAD-X element exits and produced a
case-level plot. There were no failed included cases. The full EFIELD survey
case is the one unexecuted `unsupported` case; the canonical outcome is
`incomplete-perturbation-coverage`. Nominal thick tracking completed for 64
turns. This is a smoke result, not a user-run skill application, user review,
tolerance decision, or physics acceptance.

Attempt 017 artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `report.md` | `dfc74857b11b237d1a43e7a2fd26d6d154862fc4a1fbcf02defa791bdce0c93e` |
| `result.json` | `485780f9458977c721e3c907a354183e518f63471e9dc8201bcbbb203bf39261` |
| `manifest.json` | `525c5bc72c5bfe92c349978af186e73ccc3162d74663bba752e5f7f356d43cad` |
| `campaign_case_inventory.json` | `b0874400efb290dd90470c9b3cd46d2c717b0a27c156309be02a3697b8218198` |
| `plot-manifest.json` | `3055c65de54656b6a9ec6e0f54ddefcf92deef5b30841d2b26c6a6d9c018cebd` |
| `response_summary.csv` | `c116b229bad402ff91dc2aae46c50c588153526f17c9fedbd850fc8b7ac3ad05` |
| `scalar_response_summary.csv` | `1b14f4f1a88b573bd3df665fbb1280f51ab64afd45c3caee89b81ff5d74a8d0f` |
| `harness-tests.log` | `abacbd783e132214c10a5d854fdf96d4aa0bf904722bff5ff14db2a30d47f87c` |

Runner and adapter hashes used for the final diagnostic:

| Source | SHA-256 |
|---|---|
| `scripts/python/benchmark_pyptc.py` | `31d5a420993fea1ed140b2c9156e804d8dab2aaa5324aefcbba9ee26de69aa7c` |
| `iteration-0003/isis_rcs_optics.py` | `5629e87d7ba1e998c1ebe32c334a15518d2407a628c4ba94d7195af40f1a1da6` |
| `iteration-0003/ptc_optics_worker.py` | `93227b5b24c3db7b1b79803b73ef7d3f0968081b53e9433edeedf034ea44f3b0` |
| `iteration-0004/tests/test_case_inventory.py` | `014617ad585fe37df0f5c3313f0d22aa06212d325b6c76257827ced34066646d` |

The eight deterministic checks pass. They cover the full declared inventory,
fresh case-local input mutation, isolated EFIELD table generation, verified
intersection filtering, per-engine profile/scalar response arithmetic, and
explicit unsupported status. The complete diagnostic smoke also finished with
no failed included cases.

## Superseded diagnostic attempts and retention record

The following smoke bundles were generated while fixing the runner. They are
not user-run attempts. Keep only attempts 015-017 after recording the older
attempt identities and hashes here and in the review ledger.

| Attempt | Outcome | Evidence retained here |
|---|---|---|
| `attempt-012` | interrupted after the response join raised `KeyError: 'occurrence'`; no report/result | inventory SHA-256 `811aa4b806b1c718cb91aa1cca7c7aa88c76a514a8d8684e9a386d35daafc3e7`; plot-manifest SHA-256 `d68145cc994c6a96b68a231fb5f6f72cf0305fdfa1a354ec2f5ca8d7cec4d080` |
| `attempt-013` | 30 cases ran; response join fixed, but alignment/survey families still deferred; `incomplete-chromaticity-and-plot-review` | report `b76832c3da3ed2d7a0b78da616e58d35b6c0bf10ea3bc433884409b8335a179a`; result `aded27d0a29fab44e0c71a4d3803ac200e11af464095575b6e55c6c799f63718`; manifest `c4ad461e892e90276e97ca435f194bb3d6fbc3575fe954e8080d1a9bdb491881` |
| `attempt-014` | 30 cases and plots; first case-family response summary; eight candidates still deferred; `incomplete-perturbation-coverage` | report `03f2030deea04fa07fa864f69a7b054b9516e49913a4690167f62493d8d3492d`; result `9bc038ec21eee289d8891e31ee9a2eca829fadb12c6a0cf122bb395d0b547340`; manifest `7761c5146527a4d80c0fb17e82168fcbf5301d1a2336f4be6ed33bb2ea667722` |
| `attempt-015` | 30 cases and plots; profile and scalar responses; eight candidates still deferred; `incomplete-perturbation-coverage` | report `2b43c410e8b8087f38c9b363c31109d371fb758e0abc65a968e18ed2c243e725`; result `61eecd14dc7889b986f60dfbe2cdcb361c989c9eeb4da46c9b60cdbbfa5c624c`; manifest `0cb3a3dd5a5ee1f200ed4f28271a52dd823b3d194b909c708b47fea69eb10f7d` |
| `attempt-016` | 37 cases ran; outcome incorrectly omitted the unsupported full table and was corrected in attempt 017 | report `858a64e27f3b786f2b371b3b51a15d7f14a346b51c8f27e130e7137d24893ab8`; result `8ef18efee8f75985ff0475ac31dc6daf56c3b3fd00b8d2595c742489b5c475e3`; manifest `b1d0f3d225719e6974ff15d0219500568d06ed2c234fbe0131c47b09d9333a6f` |
| `attempt-017` | final corrected diagnostic; 37 cases and 37 plots; one full EFIELD case unsupported; `incomplete-perturbation-coverage` | hashes above |

These records support Task 6 campaign evidence and Task 9 review maintenance
under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
No `REP`, `EVAL`, tolerance approval, physics claim, or acceptance is created.

Status: corrected multi-case smoke ready for user review; one candidate remains
technically unsupported by the current public error-table reader.
