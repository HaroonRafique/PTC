# Coupled-map runner diagnostic smoke

Date: 2026-11-02
Run class: agent diagnostic smoke; not a user skill-test attempt
Skill revision: `330746975383bc01ae100bea18ae54299b83cb2e`
Skill SHA-256: `b57248367f33b0985b136bf119cb366fc03604d47a34e52fb05aaa42518994ae`

## Change

Added a nominal one-turn transverse map comparison to the benchmark workflow.
MAD-X writes a closed-orbit `PTC_TWISS` table using `ICASE=6`, `NO=1` and the
`RE11` through `RE44` transfer-map columns. The PyPTC optics worker estimates
the map using `pyptc.optics.one_turn_map()`. The attempt records both matrices,
their elementwise residuals, maximum and RMS residuals, the maximum cross-plane
residual, MAD-X map-file hash, and PyPTC symplectic residual. Coupled-map
tolerances and normal-form acceptance remain pending; the comparison is
nominal-only and diagnostic.

## Smoke evidence

The first diagnostic run stopped because the workflow checked lowercase MAD-X
column names while the TFS parser exposes uppercase names. The check was fixed.
The next `./scripts/shell/benchmark-pyptc-attempt.sh --smoke` run completed
with `completed-needs-human-review`. Its temporary bundle was removed by the
runner after success. The failed temporary bundle from the first run was also
removed after its failure was inspected; the untracked smoke outputs did not
remain in the worktree.

`python3 -m py_compile` passed for the three changed Python workflow modules,
`bash -n` passed for the orchestrator, and `git diff --check` passed. The
focused `tests/test_coupled_optics.py` suite could not run: pytest is absent
from the benchmark virtual environment. The smoke validates the complete
workflow and MAD-X map table generation, but does not establish physical
agreement, coordinate convention equivalence, or a tolerance.

## Scope and next review

Attempt 023 feedback remains immutable and records that coupling was not
evaluated in that run. This diagnostic does not replace a fresh user-run
attempt. The next user run should be assessed against its exact skill snapshot;
review should verify that MAD-X `RE` map coordinates and PyPTC's centered
tracking coordinates have matching conventions, inspect symplectic residuals
and matrix residuals, and decide whether a coupling tolerance is supportable.
The benchmark's perturbation cases are not yet separately map-compared.

## Source hashes

| Workflow source | SHA-256 after change |
|---|---|
| `scripts/python/iteration_0005/benchmark_pyptc.py` | `9e34b35c41cbfb94a91b802dcba52fa230370a4a006803c7c6a4f6ea80500245` |
| `scripts/python/iteration_0005/isis_rcs_optics.py` | `99160472c3d0fddd9fd2a50641ea09b4f905e3cf1084c9009385bded42093992` |
| `scripts/python/iteration_0005/ptc_optics_worker.py` | `874333a723bdeb21b70e611d095316239301730806c3f3380002ddd34b9ec5a9` |
