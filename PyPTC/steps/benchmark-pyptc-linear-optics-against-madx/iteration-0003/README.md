# Iteration 0003: thick tracking default

This is a feedback-driven correction of the iteration 0002 harness. It keeps
the exact pinned optics skill snapshot from iteration 0002 (revision
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`, SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`) and the
verified element-exit mapping adapter. It is **not represented as an
independent fresh skill implementation**: the user-run iteration 0002
assessment and the thick/thin investigation directly motivated these changes.

From the benchmark step directory:

```bash
./iteration-0003/setup.sh
./iteration-0003/run_benchmark.py
```

The runner takes no command-line arguments. New results are allocated in
`../runs/attempt-NNN/`; run numbering starts at `attempt-001` and advances
from directories already present. The human-maintained `../runs/INDEX.md` is
not edited by the runner. By default it uses MAD-X 5.02.00
`PTC_TRACK` with a thick layout as the tracking reference, and runs the PyPTC
tracking workflow against the accepted flat file. Both routes use PTC, so
this exercises the thick tracking path but is not an independent tracking
engine comparison.

To request the optional additional thin-mode diagnostic:

```bash
PYPTC_BENCHMARK_TRACKING_MODE=both ./iteration-0003/run_benchmark.py
```

`both` retains the thick route as the primary result and separately tries
classic MAD-X `TRACK` after an explicit ten-slice `MAKETHIN`. That thin recipe
is currently known to fail on a negative drift and is marked blocked; it does
not invalidate the thick result. PyPTC's matching thin-lens control is marked
unavailable, so no thin cross-code comparison is made. The thin diagnostic is
not a validated slicing policy. The accepted flat file, split settings,
strengths, harmonics, and trim values remain unchanged.

Each case writes raw data under `cases/<case-id>/` and one case-level composite
PNG under `plots/cases/<case-id>.png`; the plot manifest links each case to
that image. The local skill feedback requests that the shared skill require
this one-composite-per-simulation-case output.

The next full skill-test run should be started by the user. Any agent smoke
run is labelled `agent-diagnostic` and is not a user-run result or acceptance.
The recorded smoke and its initial adapter/recipe corrections are in the
step's `feedback/0006-iteration-0003-thick-tracking-smoke.md`.
