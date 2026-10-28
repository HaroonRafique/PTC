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
| `attempt-006` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0011; superseded inventory smoke; report/result hashes retained in feedback and ledger |
| `attempt-007` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0011; nominal plotted; report/result hashes retained in feedback and ledger |
| `attempt-008` | user run | incomplete chromaticity and plot review | pruned; assessed, no acceptance | feedback 0012; 586/586 exits mapped, thick tracking complete, chromaticity blocked, 37 perturbations deferred; hashes retained in feedback and ledger |
| `attempt-009` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0013; first iteration-0004 smoke; clipped working-point table; hashes retained |
| `attempt-010` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0013; working-point table fixed; profile/tracking heading overlap; hashes retained |
| `attempt-011` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0013/0015; updated-skill smoke was nominal-only; hashes retained |
| `attempt-012` | agent diagnostic | interrupted | pruned | feedback 0015; response join raised `KeyError: occurrence`; partial bundle hashes retained |
| `attempt-013` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0015; 30 included cases and plots; response join fixed; hashes retained |
| `attempt-014` | agent diagnostic | incomplete perturbation coverage | pruned | feedback 0015; 30 cases and plots; profile response summary added; hashes retained |
| `attempt-015` | agent diagnostic | incomplete perturbation coverage | superseded | feedback 0015; 30 cases, per-case profile/scalar responses and plots; eight candidates still deferred |
| `attempt-016` | agent diagnostic | incomplete chromaticity and plot review | superseded | feedback 0015; 37 cases/plots, but outcome omitted the unsupported full EFIELD case; corrected in attempt 017 |
| `attempt-017` | agent diagnostic | incomplete perturbation coverage | pending | feedback 0015; 37/38 cases executed and plotted; full EFIELD unsupported, 586/586 boundaries mapped, thick tracking complete; no acceptance or reviewed response tolerances |
