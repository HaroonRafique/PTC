# User-run attempt 005 assessment

Date: 2026-10-28
Run: `runs/attempt-005`
Run class: `user-run`
Technical outcome: `incomplete-chromaticity-and-plot-review`
Skill: `benchmark-code-against-isis-rcs-optics`, revision
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`, SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Admission basis: user-accepted `attempt-20261027T194128Z`, snapshot admission
only
Evidence-gated publication plan: Task 6 campaign evidence and Task 9 review
maintenance in `docs/plans/2026-10-23-evidence-gated-agents-publication.md`.

## Evidence identity

| Artifact | SHA-256 |
|---|---|
| `report.md` | `a5082e3be20fee1730ec35d82d1bb91f94075d28620713dc1b296cab286b849f` |
| `result.json` | `aaa3f9b63412c99cd38fabaabc84ff7a835622f6979c9cf43c5df5e22d5a7820` |
| `manifest.json` | `99959ccacf91252db66b01030107ae8131205a11b4a06cbfb152bf07ce2035f5` |
| `manifest.env` | `936d1148030bad72722d0aa937d505def137d6753749dda03fc539eb8adfd9e3` |
| `plot-manifest.json` | `2e7ac77c4c538d1d8e46e449651b4f853962a173ea871c8d1b423a773d8482d7` |
| `plots/cases/nominal.png` | `430ad40983b478a39f7acfbc546fbfe6928ce39c6afbab276ffbf5b0f7beb603` |
| `harness-tests.log` | `c3fa15e905cdbd62fb5a6625285e60473b55d8241fc0fa9bfc086d6cc95b021e` |

## Assessment against the pinned skill

The runner used the accepted snapshot basis, exact PyPTC library and MAD-X
5.02.00 binary, five ordered input hashes, 2023 strength overlay, `synchrotron`,
zero `a1`/`b1`, zero trim values, and unchanged accepted flat file. It retained
586 MAD-X TWISS rows and 804 target node rows and verified all 586 named
element exits by identity and position. Fourteen profile residual summaries
were produced at the mapped exits. All are correctly left `pending-tolerance`;
no agreement claim is made. The seven local fixtures passed.

Bounded thick tracking retained 65 finite samples over turns 0–64 from both
paths and the target loss check was clear. Position residuals are
`pending-tolerance`. MAD-X `PTC_TRACK` and PyPTC both use PTC, so this is a
bounded workflow/record comparison, not independent tracking-engine
validation. The optional thin path was not requested.

The attempt is not complete under the skill. PyPTC chromaticity's derivative
coordinate remains unresolved, so no cross-code chromaticity conversion or
tolerance claim is justified. The nominal composite exists and contains the
nominal overview and detailed profile/residual panels, but the plot manifest
does not resolve its aligned-data references: panel entries specify
`aligned_profiles.csv` while the actual file is
`cases/nominal/aligned_profiles.csv`. Several report log paths also omit the
`cases/nominal/` prefix. The 3150 x 6900 composite was visually inspected; at
whole-image viewing scale its small working-point text and labels are not
comfortable to read, so normal-view readability remains unverified/insufficient.

Only the nominal case is currently declared and plotted. Its one composite
satisfies the one-composite-per-declared-case layout check, but the workflow
does not implement the wider skill's perturbation/error case inventory or
per-case response evidence. The case-level plot contract should be rechecked
when those cases are implemented.

## Learning comparison with PyPTC examples and tests

The historical
`workflows/madx/compare_madx_pyptc_closed_orbits.py` comparison converts MAD-X
dispersion using relativistic beta, calculates signed PyPTC-minus-MAD-X
residuals, and writes overlays/residual plots. `tests/test_madx_optics_benchmark.py`
covers completeness, residual metrics, beta normalization, aperture
interpolation, and a committed baseline's provenance. Attempt 005 adds stronger
name/occurrence/fibre/exit-position matching and bounded tracking records, but
its current plot-manifest relative paths are stale after moving data under
`cases/nominal/`. Existing workflow/test coverage is complementary; it does
not replace the current skill requirements. No existing suite execution is
claimed here; only the seven attempt-local fixtures were run by the user.

## Disposition

Record as `user-run assessed`, with no benchmark acceptance, `REP`, or `EVAL`.
Before another run, repair plot-manifest and report paths, improve and visually
verify normal-size plot readability, and continue addressing the skill's
capability inventory, perturbation-case, helper-documentation, and explicit
fixture gaps. This is local campaign evidence for publication-plan Tasks 6
and 9, not a physics acceptance.
