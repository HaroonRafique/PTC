# Iteration 0003: thick tracking default

This is a feedback-driven correction of the iteration 0002 harness. It keeps
the exact pinned optics skill snapshot from iteration 0002 (revision
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`, SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`) and the
verified element-exit mapping adapter. It is **not represented as an
independent fresh skill implementation**: the user-run iteration 0002
assessment and the thick/thin investigation directly motivated these changes.

The iteration-0003 runner and setup entry points were retired when the
step-level orchestration was introduced. Its verified adapter modules now
live under `../scripts/python/iteration_0003/`; this directory retains the
skill snapshot and historical notes only. From the benchmark step directory,
use the current stable commands:

```bash
./scripts/shell/setup-benchmark.sh
./scripts/shell/benchmark-pyptc-attempt.sh
```

The step-level shell orchestrator takes no arguments for a user run. Use
`--smoke` only for an agent diagnostic. New results are allocated in
`../runs/attempt-NNN/`; run numbering starts at `attempt-001` and advances
from directories already present. The human-maintained `../runs/INDEX.md` is
not edited by the runner. By default it uses MAD-X 5.02.00
`PTC_TRACK` with a thick layout as the tracking reference, and runs the PyPTC
tracking workflow against the accepted flat file. Both routes use PTC, so
this exercises the thick tracking path but is not an independent tracking
engine comparison.

To request the optional additional thin-mode diagnostic:

```bash
PYPTC_BENCHMARK_TRACKING_MODE=both ./scripts/shell/benchmark-pyptc-attempt.sh --smoke
```

`both` retains the thick route as the primary result and separately tries
classic MAD-X `TRACK` after an explicit ten-slice `MAKETHIN`. That thin recipe
is currently known to fail on a negative drift and is marked blocked; it does
not invalidate the thick result. PyPTC's matching thin-lens control is marked
unavailable, so no thin cross-code comparison is made. The thin diagnostic is
not a validated slicing policy. The accepted flat file, split settings,
strengths, harmonics, and trim values remain unchanged.

Every declared case has a `case.json` and explicit `case_status.json` in the
attempt bundle. At present, only the nominal case executes and writes a
composite PNG. The 37 Xsuite cross-reference perturbation cases remain
`blocked-not-implemented` and have no plots; the runner records the reason for
each. The local skill requires a case-level composite for each executed
simulation case, and no plot is fabricated for a blocked case.

The next full skill-test run should be started by the user. Any agent smoke
run is labelled `agent-diagnostic` and is not a user-run result or acceptance.
The recorded smoke and its initial adapter/recipe corrections are in the
step's `feedback/0006-iteration-0003-thick-tracking-smoke.md`.
