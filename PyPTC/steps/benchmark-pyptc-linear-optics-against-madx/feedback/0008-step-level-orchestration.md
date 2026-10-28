# Step-level benchmark orchestration

Date: 2026-10-28
User clarification: the new run format must keep executable orchestration
outside numbered run bundles and follow the Xsuite testbed's step-level
orchestration pattern.

The stable entry point is now
`scripts/shell/benchmark-pyptc-attempt.sh`. It validates the local environment,
allocates `runs/attempt-NNN`, records the orchestration/workflow source hashes
in `manifest.env`, runs the workflow with a retained log, and records failed
stage/command/log details on error. It does not alter the human-maintained run
index or review ledger. The Python workflow module is at
`scripts/python/benchmark_pyptc.py`; iteration 0003 retains its pinned skill
snapshot and PyPTC helper implementations, but no longer contains a user-run
entry-point script. Attempt bundles hold evidence and generated results only.

Agent smoke `attempt-004` exercised the shell allocation, workflow invocation,
and terminal bundle checks. It completed technically with outcome
`incomplete-chromaticity-and-plot-review`, produced a nominal case composite,
and is not a user-run test or acceptance.

| Artifact | SHA-256 |
|---|---|
| `report.md` | `0313c787d6024addea48bac1aab8d5b48b6548d47bd47ee7d5a5dcc8bad0d662` |
| `result.json` | `3c632a973317de401529f079505cd71f51098debecce81fd9496332064c4bb96` |
| `manifest.json` | `b49d8de5903abbfb9641b8cbece8ed8f6a9e4c51772b725a4948446051e8a0e0` |
| `manifest.env` | `5f0df69279f5d9225451a53bf0e79039492f1a04a45c5095bd81a70e3b9665ae` |
| `plot-manifest.json` | `84f237ebf30076d65a9cc59c0580e85936db6f9442966ddf63a91582b5d0a8db` |
| `plots/cases/nominal.png` | `430ad40983b478a39f7acfbc546fbfe6928ce39c6afbab276ffbf5b0f7beb603` |

The stable command is documented in the step README. Agent smoke mode is
`--smoke`; no-argument invocation is the user-run mode. This is local PyPTC
campaign evidence supporting Task 6 and Task 9 traceability in the evidence-
gated agents publication plan. The shared skill and Xsuite repository were not
modified.
