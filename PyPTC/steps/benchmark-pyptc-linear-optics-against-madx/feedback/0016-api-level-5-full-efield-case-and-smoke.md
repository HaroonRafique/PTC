# Iteration 0004 API-level-5 EFIELD case and all-case smoke

Date: 2026-10-28  
Run class: agent diagnostic only  
Final diagnostic: `runs/attempt-018`  
Skill snapshot: `iteration-0004/SKILL.md`, SHA-256
`b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`

## Runner update

The merged PyPTC magnetic EFIELD implementation raises the native ABI to level
5. The accepted admission bundle intentionally remains unchanged and contains
the original API-4 `libpyptc.so`; using it with the current Python wrapper would
not expose the new native symbol. Iteration 0004 setup now rebuilds the current
repository library with `build/build_ptc.sh`, checks API level 5, and the
runner records the candidate library separately from the accepted admission
library. The accepted five lattice inputs, flat file, and MAD-X binary remain
verified against their admission hashes.

The `survey_error_table` candidate changed from unsupported to included. It
copies the pinned full table
`workflows/madx/reference_errors/apr_2026_survey_corrected.tfs` byte-for-byte,
then uses MAD-X `READMYTABLE`/`SETERR` and the PyPTC
`apply_madx_error_table` API from fresh states. Its SHA-256 is
`c864ea0ac6bab8159d5763e9134d8788e6ad006352ae8034a37859bfa95351b6`. The
preflight audit found 38 nonzero records and no nonzero unsupported fields.
All 38 candidate cases now have `included` disposition. The exact EFIELD table
used by Xsuite attempt 029 is still not archived in this repository, so the
local full-table case is not claimed as byte-for-byte equivalent to that
external candidate. The local Apr 2026 table has no nonzero magnetic K terms;
the separate `examples/06_madx_efield_api.py` synthetic K1L/K1SL comparison is
the evidence that exercises nonzero multipole coefficients.

## Attempt 018 diagnostic result

Attempt 018 completed all 38 inventoried cases and generated 38 case plots.
There were 37 completed perturbations, no failed cases, no blocked or
unsupported candidates, and no unexecuted candidates. The nominal profile map
verified all 586 MAD-X element exits against PyPTC. Thick tracking completed
for 64 turns. The canonical outcome remains
`incomplete-chromaticity-and-plot-review`: chromaticity is blocked because the
PyPTC derivative coordinate is unresolved, and numerical response tolerances
remain unreviewed. This is an agent diagnostic, not a user-run attempt or
acceptance.

The full EFIELD case status is `completed` and its plot is
`runs/attempt-018/plots/cases/survey_error_table.png`. It applies all parsed
nonzero rows via `PTC.apply_madx_error_table(case_error_table, nonzero=True)`;
the full input remains unchanged in the case bundle. The API call list and all
applied row records are in
`runs/attempt-018/cases/survey_error_table/target/pyptc_api_summary.json`.

## Provenance and hashes

| Evidence | SHA-256 |
|---|---|
| Attempt result | `0833fa1e57c5a7b2589a17dfec14378f4af991d9fad5ce5fa96a41d5a511b14c` |
| Attempt manifest | `b7d2c8b1c92613ba29388f7b403ac37f41983ed3af23bdee90ae9027dc8ace77` |
| Attempt report | `64987e964976ca66daa27fd3779db2383f184a1966803dceb8e5754293d07c93` |
| Case inventory | `c31e175ede2d0280117d6f9a19e2facf56d849ab410b53c1953a74bdbe186af9` |
| Plot manifest | `d5bf9da9dae212a4f7d200f76cbe24b6065f440297fdb44b6424367c04bd51ad` |
| Harness test log | `83df724240afecb9907b62253ce36684acbe47c786cb1a3e22415599e463be45` |
| Current API-5 library | `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c` |
| Current PyPTC source revision | `0ed4f9b2e293e5cd25c829624a0bff56fed62748` |
| Benchmark runner source | `01c51766f7c25f2a9c2ac898564c8a2ec26430dbc0cd27b00a846d7ee5cd73a3` |
| Iteration setup script | `ef06c79c7bd0ad4e9ed90469bef34ebcd7591b6a0638a96129226204f7df2f14` |
| Case inventory tests | `589728fd10abf51020975f06a1d6b558c2b93bc95287fe00f83ba97b3d28b07f` |

The nine deterministic case-inventory tests passed. Setup rebuilt the shared
library and verified API level 5. Attempt 018 mapped 586/586 nominal exits,
completed the 64-turn thick tracking smoke, ran every included case, and
produced all 38 plots. Numerical differences remain pending tolerance and
human plot review; no `REP`, `EVAL`, physics claim, or acceptance is created.

This is Task 6 campaign evidence and Task 9 local review maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
