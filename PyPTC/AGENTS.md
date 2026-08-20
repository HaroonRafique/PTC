# PyPTC Agent Instructions

## Working Directory

Work from `/home/hr/Codes/PTC/PyPTC` for PyPTC tasks. Do not run normal
validation or examples from the parent repository or from `/tmp`.

## Build And Output Layout

- Use `build_pyptc/` for the local `libpyptc.so` build.
- Use `test_outputs/` for standard, repeatable user-facing example and workflow
  outputs.
- Do not create ad hoc `/tmp/...` outputs for routine validation. If a command
  needs scratch data, place it under the relevant repo-local output directory.
- Keep generated reference PNG/CSV/JSON outputs stable and named so a user can
  inspect them after running an example.

## Lattice Defaults

The generated simplified ISIS RCS flat file is the default lattice:
`workflows/madx/outputs/simplified/PTC-PyORBIT_flat_file.flt`.

Use the legacy readiness flat file only for explicit compatibility studies.
Jan26 full-error-table workflows should resolve the 38 source records to 38
PyPTC applications; 88 applications usually means the wrong sliced lattice was
used.

## Test And Example Rules

- User-facing physics checks should be runnable as scripts and should write PNG
  outputs where plotting is relevant.
- Keep pure parser/helper pytest tests for focused code checks, but workflow
  validation should go through the example scripts and `run_examples.sh`.
- The 1000-particle bunch examples should use PyParticleBunch-generated input
  and produce before/after dashboards with shared axis limits.
- Tune footprint and tune-vs-action information should be included in dashboard
  plots for 1000-particle tracking workflows, with tune/action data retained in
  the bunch diagnostics CSV.

## Artefact Hygiene

The worktree may contain generated plots, flat files, build products, caches, or
unrelated files. Do not remove, revert, or overwrite unrelated files unless the
human explicitly asks.

## Git Commit Style

Use the established commit style for agent-created commits:

- Format: `<type>[<scope>] message`
- Typical types: `<add>`, `<update>`, `<fix>`, `<cleanup>`
- Keep scope small and meaningful, for example `[pyptc]`
- Use a short lower-case summary, e.g. `<update>[pyptc] standardise examples`
