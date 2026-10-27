# Feedback 0001 — agent diagnostic preflight

This record covers only agent-run setup and smoke diagnostics for iteration
0001. It is not the post-user-run assessment and does not request or claim a
shared skill revision. The user-run linear-optics benchmark remains
outstanding.

## Pinned inputs and implementation

- Benchmark skill: `/home/hr/Repositories/isis-modelling-agents/skills/machine-integration/benchmark-code-against-isis-rcs-optics/SKILL.md`
- Skill repository revision observed: `a9aeca88bdf7e7e81c71423c8a99ca0937540d67`
- Skill file SHA-256: `ae393dba4f719f6416b061970f5974bf00b599db25eabfdfcb6836fbc4dfefbd`
- Accepted admission basis: `attempt-20261027T082315Z`, user accepted for snapshot admission only.
- Admission result SHA-256: `b170dd9df2768afbc37cb4c1cae4308f8759ce45fd247b90c5f88e5bb83c5db9`.
- Accepted target commit: `324c1a6e0389137c4f93658621089f9e01159827`.
- Accepted PyPTC library SHA-256: `b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76`.
- Accepted MAD-X 5.02.00 binary SHA-256: `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
- Accepted MAD-X TWISS SHA-256: `ae7c3867fcf194262a13ddf8f8746d312c1a4309ee86e9a2a1b25caf72faa803`.
- Iteration runner SHA-256 after final diagnostic: `337e9b4fc8d224e2d9cca0d52b5fb43a68fc63511ab922c7a8fe6a8d6dfd622d`.

The benchmark step is separate from the admission step. It copies the full
accepted admission bundle as provenance and uses no failed admission bundle.
It preserves the approved five-file input order, `2023.strength`, the
`synchrotron` sequence, `a1=b1=kqtd=kqtf=0`, and the already generated flat
file. No existing PyPTC optics example or test was used to construct the first
attempt. The Xsuite work remains independent.

## Agent diagnostic attempts

| Attempt | Outcome | Evidence and assessment |
|---|---|---|
| `attempt-20261027T142211Z` | Failed before a reference calculation | The runner called `madx.version()` although `cpymad` exposes `version` as a property. Report SHA-256 `533a7ed9850af519198dc8c5269d235137f90d2fc79339498ec5b0dd5577f777`; result SHA-256 `bf4762eaa00030f9d77db7193649345696617db5bd8938da52117d551e4ead43`; manifest SHA-256 `10a8ee5c11c55a5a02388f12de95ba57048d7292b304a8ea5744dd94157b2138`. Raw bundle pruned after this identity and outcome were recorded; it was an agent setup failure, not a user-run attempt. |
| `attempt-20261027T142218Z` | Exploratory output invalid as a pinned-reference comparison | The installed `cpymad` ran MAD-X 5.09.03; accepted admission reference is MAD-X 5.02.00. The changed engine must not be used as the benchmark reference. Report SHA-256 `ea04a99c9195203de3dbd8badf2e387dd4fe881bb563516937cf53d33e26dcae`; result SHA-256 `c3ff6cc0b84bca34383841fda73ccf53cf58380e816adf8dc938f1fad3af2dc1`; manifest SHA-256 `eff76f521d00fd5fb6dd706c4ebae6bb7b7acfa207d84452117da5e95129c178d82`. |
| `attempt-20261027T142322Z` | Smoke passed; optics comparison blocked | Reused the accepted 5.02.00 TWISS and imported the accepted flat file into PyPTC. This predates the final capability/report clarification. Report SHA-256 `a822db68a55eec0b5b744d88eed09af17d4638ff1b8b6bdd2d525f54f0c99c45`; result SHA-256 `5bd67491a7810c173bee62ac05dc2c6c23cc378c655f105d9fca2290804ba31f`; manifest SHA-256 `036398743d8d4c5ffbf5bbaca1718b3ec5a4465cb14ddabfa0eed968b39f0981`. |
| `attempt-20261027T142439Z` | Current agent diagnostic: `blocked-profile-mapping` | Reused MAD-X 5.02.00, imported PyPTC, captured native runtime output, wrote raw records and scalar differences. Report SHA-256 `d269cb337001b23d80bdbbaf7f6bf35f5706ccc94d0d9889e59c457e4a9a9155`; result SHA-256 `b84e4ec67cb78b01a999c5a086b400ccf89305ad37c06e0c9ec3a3777159c0f6`; manifest SHA-256 `757d7cdbac39d6701693a1168730b8077d06dcf17a5f978552090bb992291f0f`. |

## Skill-first findings and limitations

The smoke confirms PyPTC loads the accepted flat file and returns 375 node
records. Cumulative node lengths total `163.36281999999989 m`, matching the
accepted ring circumference at the displayed precision. PyPTC scalar tunes
are `0.31605467692091` and `0.76510661554073`; compared to MAD-X fractional
parts they differ by `+5.389592091e-5` and `+1.065275407e-4`. Circumference
difference is `-1.14e-13 m`. Those are diagnostic values only and remain
`pending-tolerance` because no reviewed criteria were supplied.

The copied reference TFS contains 586 rows but only columns `NAME, S, X, PX,
Y, PY, BETX, BETY, ALFX, ALFY`. It omits `DX, DPX, DY, DPY, MUX, MUY`, so the
accepted reference artifact cannot support all required profile observables.
The exact accepted MAD-X binary is present only in the old admission output
path, while local `cpymad` reports MAD-X 5.09.03. Iteration 0001 therefore
reuses the accepted reference file and refuses to silently substitute 5.09.03.
The runner should be extended only after the operator provides/reconstructs an
authorized pinned 5.02.00 way to calculate the missing columns.

For the 375 PyPTC candidate exit positions versus 586 MAD-X rows, only 153
have a unique exact `s` match at the diagnostic threshold `1e-9 m`; the
largest nearest-position residual is `2.49315 m`. These are not alignments:
the current public PyPTC optics records do not attach element/occurrence names,
and this iteration has not verified whether each API row represents an entry
or exit boundary. The profile comparison is correctly `blocked`; no
interpolation or profile residuals are reported. The skill's final combined
comparison figure, chromaticity conversion/comparison, bounded tracking, and
completion publication record are therefore not produced.

## Next action

The user should run `./iteration-0001/setup.sh` and
`./iteration-0001/run_benchmark.py` from the benchmark step. Then assess that
user-run first against the exact benchmark skill, then compare with existing
PyPTC examples/tests for learning, and write the next immutable feedback file.
Do not interpret the agent preflight as a user-run benchmark, optics result,
or skill completion.
