# Linear optics benchmark runs

The runner allocates numbered run directories but does not modify this index.
Agent diagnostics are not user-run results or acceptance decisions.

| Run | Class | Outcome | Review | Evidence |
|---|---|---|---|---|
| `attempt-001` | agent diagnostic | failed | pending | feedback 0007; layout smoke exposed an uninitialized summary |
| `attempt-002` | agent diagnostic | incomplete chromaticity and plot review | pending | feedback 0007; default thick mode; nominal case plot present |
| `attempt-003` | agent diagnostic | incomplete chromaticity and plot review | pending | feedback 0007; consecutive allocator check; nominal case plot present |
| `attempt-004` | agent diagnostic | incomplete chromaticity and plot review | pending | feedback 0008; step-level shell orchestration smoke; nominal case plot present |
| `attempt-005` | user run | incomplete chromaticity and plot review | assessed; no acceptance | feedback 0009; mapping and thick tracking completed; chromaticity blocked and plot-manifest data paths unresolved; feedback 0010 cross-references all 38 Xsuite attempt-029 cases and clarifies skill coverage |
| `attempt-006` | agent diagnostic | incomplete chromaticity and plot review | pending | feedback 0011; 38-case inventory smoke; nominal plot-status metadata issue, superseded by attempt-007 |
| `attempt-007` | agent diagnostic | incomplete chromaticity and plot review | pending | feedback 0011; 38 cases inventoried, nominal executed/plotted, remaining 37 blocked-not-implemented |
| `attempt-008` | user run | incomplete chromaticity and plot review | assessed; no acceptance | feedback 0012; nominal mapping and thick tracking complete; chromaticity blocked; 37 perturbation cases blocked-not-implemented |
