# Feedback 0004: user-run launcher failure and fix

## Attempt identity and outcome

The user ran the no-argument entry point from
`steps/admit-code-to-isis-rcs`:
`/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/steps/admit-code-to-isis-rcs/.venv/bin/python ./run_admission.py`.
The launcher selected skill iteration `0002` and wrote
`test_outputs/admit-code-to-isis-rcs/attempt-20261026T220607Z/`.

This was a **user-run failed attempt**, not an admission or physics failure.
The fresh harness suite ran 9 tests and had one error in
`test_report_preserves_pending_review_and_warning_disposition`: its fixture
omitted `skill_iteration`, which the newly updated `render_report()` indexed as
a required key. The failure occurred before the PyPTC build/bootstrap, MAD-X
reference calculation, or PyPTC lattice load. `events.jsonl` contains only the
snapshot-copy and harness-test-started stages; both engine-invoked fields are
false. The snapshot is the authorized five-file closure from
`1bada6a2ab94edd426c52b7e97a5d335926e0646`.

The generated report/result also incorrectly called this an agent-run
diagnostic because that label was hard-coded in the harness. Do not infer the
operator from the generated label: the user confirmed that they ran it. The
original bundle is preserved unchanged as evidence of both defects.

| Artifact | SHA-256 |
| --- | --- |
| `report.md` | `8e81639f5c9d1ab4a083bc739aefaff02fa745f6ad2cce3623945868135d96ea` |
| `result.json` | `f0b264411e7d44ce99fe3f1c297e5dc3d8db829cca01055db62504409bf9c278` |
| `manifest.json` | `f8fd2718ad87aaf6ceae7c8aa39b3d51c9831fe9dabbb6a5028eec3db8fb9c85` |
| `harness-tests.log` | `2e12af9629ea373058e1a4418ae8a45dfbfef76080ce32b0798e03d2eeb23c23` |
| `events.jsonl` | `61b1b2d7d1fde43d31693e2476f9c54bcda301d8be6d86d66e16a25b1a6fe591` |
| copied harness | `c08d4c041cd8c47c2db1d0c5be1773b27845f13a84638dc65a352d67f4b92f97` |
| copied launcher | `5066a188a951fd75ea45e10fb7b2f2e429189a32e827bedd43b01d67bde62ad8` |
| copied test file | `928c27df2ee1d82d132cb31f7e95156304d850dbb87adfb8db64f7a96e5035dc` |
| source checkout status | `0de8a247d46a968b69d6af0287ad281e892d7e77c524062711ab60cae6565f6a` |

## Fix prepared

The `render_report` fixture now supplies and checks `skill_iteration`. Attempt
classification defaults to `user-run skill-test attempt`; an agent explicitly
sets `PYPTC_ADMISSION_RUN_CLASS=agent-diagnostic` to label its own diagnostic
run while keeping the no-argument launcher interface. The iteration README
documents that convention. The focused suite now passes 10/10 tests. No new
full admission attempt has been run after the fix, so this remains unverified
against the MAD-X and PyPTC stages.

The attempt ledger remains `awaiting review` with no acceptance. The newest
three raw bundles are retained under the three-attempt policy; older attempt
hashes/outcomes remain in feedback 0001–0003 and the ledger.
