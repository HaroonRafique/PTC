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

## MAD-X/PTC Resplitting Contract

The standard MAD-X generator uses `workflows/madx/ptc_scripts/resplit.ptc`
and `print_flat_file.ptc`. They currently set nominal `LMAX=0.5 m` and
`FUZZYLMAX=1.1`; the producer may therefore retain a gap up to `0.55 m`, while
the flat-file header records only nominal `LMAX`. PyPTC's separate runtime
checks measured orbit-node spacing against that stored nominal value. This
producer/consumer mismatch is tracked in admission feedback 0006 and the
review ledger. Do not silently change `LMAX` or `FUZZYLMAX` to suppress the
warning. Before changing the split policy, decide whether `LMAX` is a hard
maximum or whether its fuzzy tolerance is part of the contract, then keep the
generator, flat-file metadata, and PyPTC check consistent. Any split-policy
change must regenerate affected lattices and compare representative optics,
tracking results, node/fibre counts, and runtime against a retained baseline.

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

## Skill-Test Development And Benchmarking

Use the following as the default process when developing or benchmarking
PyPTC against an ISIS RCS skill in `isis-modelling-agents`:

- Start each skill application from the exact current skill revision. Rebuild
  the working harness from that skill for each iteration; do not quietly carry
  forward an earlier agent implementation as if it were a fresh skill result.
- Keep the user-facing attempt runner repeatable and runnable with its
  documented defaults. The user runs full skill-test or benchmark attempts.
  Agents may prepare the runner and run bounded diagnostic preflight/smoke
  checks, clearly labelled as diagnostics; those are not user-run skill-test
  results.
- After a user-run attempt, assess it first against the invoked skill, then
  compare the generated workflow with existing PyPTC examples and tests for
  learning. Do not use those examples/tests as hidden implementation inputs to
  the independent first attempt. Keep admission distinct from optics and
  benchmarking.
- Append evidence-backed feedback under the step's `feedback/` directory.
  Record the exact skill and code revisions, attempt IDs, hashes and outcomes,
  reusable gaps, PyPTC-specific findings, scope limits, and review status.
  Feedback files are immutable; create a new numbered file for later cycles.
- Keep review dispositions in the step's human-maintained ledger. The normal
  runner must not modify it or imply acceptance. Retain the newest three raw
  attempt bundles; before pruning older bundles, preserve their identities,
  relevant hashes, outcomes, and feedback links in the ledger/feedback record.
  Use the step's `prune_attempts.sh` dry run to inspect pruning and pass
  `--apply` only after the ledger and feedback records are complete.
- Route proposed reusable skill changes to a separate agent in
  `isis-modelling-agents`. Keep PyPTC-specific facts in this repository, present
  shared-skill edits for review there, and record the exact revised skill
  revision before the next fresh application.

## Work Diary

`WORK_DIARY.md` is the sole work-diary destination for PyPTC work. It contains
the relevant PyPTC admission history copied from the shared
`isis-modelling-agents` diary. From 2026-10-27 onward, append PyPTC decisions,
investigations, and substantive handoffs here; do not update another
repository's diary for PyPTC work. Keep attempt-specific evidence in this
repository's feedback files and review ledger. When a change warrants a diary
entry, make that entry before committing and include it in the same commit as
the related PyPTC work.

## Artefact Hygiene

The worktree may contain generated plots, flat files, build products, caches, or
unrelated files. Do not remove, revert, or overwrite unrelated files unless the
human explicitly asks.

## Git Commit Style

Every commit in this repository, including user-created and agent-created
commits, must use the established scoped subject style found in the Git
history:

- Format: `<type>[<scope>] lower-case summary`
- Use a short, meaningful type such as `<add>`, `<update>`, `<fix>`, or
  `<cleanup>`.
- Use `[pyptc]` for PyPTC work and a narrower established scope when it better
  identifies another component, such as `[ptc-interface]`.
- Keep the summary concise, lower-case, and imperative. Match examples in the
  history, including `<add>[pyptc] compare linear optics with madx`,
  `<update>[pyptc] standardise examples and outputs`, and
  `<fix>[pyptc] restore jan26 madx distorted orbit comparison`.
- Do not use bare subjects or alternate prefixes such as `docs:` or
  `fix[pyptc]:`; all commits must retain the angle-bracket type followed by
  the square-bracket scope.
- When a change warrants an entry in a maintained work diary, write that entry
  before committing and include it in the same commit as the related work. In
  repositories without a work diary, include the appropriate campaign record,
  such as feedback and ledger updates, with the commit.
