# Centralize benchmark scripts outside iteration folders

Date: 2026-10-28

## Change

All runnable setup and attempt entry points now live under `scripts/shell/`:

- `scripts/shell/setup-benchmark.sh`
- `scripts/shell/benchmark-pyptc-attempt.sh`

The old `setup.sh`/`run_benchmark.py` entry points in iterations 0001–0003
were removed as obsolete. Active iteration-0003 adapter modules were moved,
without changing their contents, to `scripts/python/iteration_0003/`. The old
iteration-0002 modules and tests were moved to `scripts/archive/iteration-0002/`
to keep their historical code outside iteration snapshots. Iteration-0004's
case tests now live in the step-level `tests/` directory. Iteration folders
retain skill snapshots, requirements, and notes, with no `.py` or `.sh`
scripts. An invariant test enforces that layout.

The stable setup command is now:

```bash
./scripts/shell/setup-benchmark.sh
```

It installs the pinned benchmark dependencies, builds `build_pyptc/libpyptc.so`
from current PyPTC source, and verifies API level 5. The stable attempt command
remains `./scripts/shell/benchmark-pyptc-attempt.sh`.

## Verification

- Setup completed from its new location and rebuilt the API-level-5 library.
- Ten step-level case/inventory tests passed, including the new invariant that
  no Python or shell scripts remain under `iteration-*`.
- A subprocess smoke through the relocated iteration-0003 adapter completed:
  804 PyPTC node rows, 586 fibres, and 804 printer groups. Retained output is
  under `test_outputs/benchmark-runner-layout-smoke/`; it checks adapter and
  worker relocation only and is not an optics comparison.
- No new skill attempt was allocated. Attempt 018 remains the full 38-case
  agent diagnostic; it completed before this path-only reorganization. Its
  preserved manifest identifies the source paths used at that time.

The iteration-0003 adapter contents retained their prior hashes:

| Module | SHA-256 |
|---|---|
| `scripts/python/iteration_0003/isis_rcs_optics.py` | `5629e87d7ba1e998c1ebe32c334a15518d2407a628c4ba94d7195af40f1a1da6` |
| `scripts/python/iteration_0003/ptc_optics_worker.py` | `93227b5b24c3db7b1b79803b73ef7d3f0968081b53e9433edeedf034ea44f3b0` |
| `scripts/python/iteration_0003/ptc_tracking_worker.py` | `26e0ecef339574d2f0539dbbfbf8eb2e8731cf7c04ebc8f8a11ed508287c1524` |

Updated active script hashes:

| Script | SHA-256 |
|---|---|
| `scripts/shell/setup-benchmark.sh` | `7975f35a7f29504b7ff4da8d68ae7ae39244d32b6db4fe8cc5b92348b6818b4b` |
| `scripts/shell/benchmark-pyptc-attempt.sh` | `b842d1adbfebe15abe727a63d3be160135ae9f1261e30927580a1915d96d6d6a` |
| `scripts/python/benchmark_pyptc.py` | `6644a361fd68c4defe17231e9596d461aba2efe0a07410722002e325e79f7d29` |
| `tests/test_case_inventory.py` | `bd8034ab599de4291bb913c61a4ab1bf7bb3cf79cb4e61cfeb0f51c608b71e53` |

The bounded layout smoke artifacts are retained and hashed:

| Artifact | SHA-256 |
|---|---|
| `test_outputs/benchmark-runner-layout-smoke/report.md` | `ff31a7d68b076a9ce5f239f0b824674d09714d34b9753d9e09b443874552b5af` |
| `target/node_twiss_raw.csv` | `667195d66be31bbb56d4b336ee0ac7634a8b0d35e1b79de53bf53b4561e2fb8e` |
| `target/def_orbit_node.txt` | `8e46d786e84699a82e777cfc53ce35efd9208573dd74400aef616067c86da930` |
| `target/pyptc_api_summary.json` | `b9c4c74cc0ba8272473afdae36f976389fa7fca4705247725449011692422234` |
| Current API-5 library | `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c` |

The full 38-case smoke evidence and its limits remain in feedback 0016 and
`runs/attempt-018/`. This layout correction is Task 6 campaign maintenance
under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
