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
| `attempt-015` | agent diagnostic | incomplete perturbation coverage | pruned | feedback 0015; 30 cases and plots; eight candidates deferred; report/result hashes preserved before pruning |
| `attempt-016` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0015; 37 cases/plots, but outcome omitted the unsupported full EFIELD case; report/result hashes preserved in ledger before pruning |
| `attempt-017` | agent diagnostic | incomplete perturbation coverage | pruned | feedback 0015 and review ledger preserve report/result/manifest hashes; 37/38 cases executed and plotted; full EFIELD unsupported, 586/586 boundaries mapped, thick tracking complete; no acceptance or reviewed response tolerances |
| `attempt-018` | agent diagnostic | incomplete chromaticity and plot review | pruned | feedback 0016 and review ledger preserve report/result/manifest hashes; all 38 cases executed/plotted with API-5 build; full local EFIELD table applied unchanged; 586/586 exits mapped, thick tracking complete; exact Xsuite table unavailable; raw bundle pruned under three-bundle policy |
| `attempt-019` | user run | incomplete chromaticity and plot review | assessed; no acceptance | feedback 0018; all 38 cases executed/plotted; 586/586 exits mapped and thick tracking complete; plots exist but fail normal-size readability review; diagnostic 0002 resolves PyPTC `dQ/dPT` vs MAD-X `DQ=dQ/dDELTAP`, showing common-coordinate chromaticity differences of about +3.00 (X) and +3.04 (Y); tolerance and cause remain open; see `investigations/0002-derivative-coordinates-and-units.md` |
| `attempt-020` | user run | incomplete perturbation execution | assessed; no acceptance | feedback 0019; iteration-0005 skill revision; 30/38 cases completed and plotted; 586/586 nominal exits mapped; eight error-table/misalignment cases stop in the source-to-ESAVE audit before PyPTC runs because the TWISS parser requires `S`; nominal phase/tunes and converted chromaticity are out of the provisional screen; all plot normal-size inspection flags are false and sampled composites unreadable; thick tracking complete, responses pending review |
| `attempt-021` | user run | incomplete perturbation execution | assessed; no acceptance | feedback 0020; 30/38 cases completed/plotted; no-S EFIELD parser works, but eight EFIELD/misalignment cases now fail in audit row indexing (`counter` undefined) before PyPTC runs; nominal tune/phase and converted chromaticity remain out of baseline; sampled composite tables/overview still have crowded labels; thick tracking complete, responses pending review |
