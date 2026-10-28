# Iteration 0004 updated-skill diagnostic smoke

Date: 2026-10-28
Run class: agent diagnostic only; no user-run benchmark or acceptance
Skill: `benchmark-code-against-isis-rcs-optics`
Skill base commit: `f5293a3754dc8c4e9a6a4ba987603924b91949f3`
Skill source worktree was modified; exact pinned snapshot:
`iteration-0004/SKILL.md`, SHA-256
`b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`.
Admission basis: accepted `attempt-20261027T194128Z`, snapshot admission only.
Evidence-gated publication link: Task 6 campaign evidence and Task 9 review
maintenance in `docs/plans/2026-10-23-evidence-gated-agents-publication.md`.

## Iteration 0004 changes

- Captured the exact current skill working tree and recorded its base commit and
  content hash. It is not misrepresented as a committed skill revision.
- Replaced the old `blocked-not-implemented` case statuses with the skill's
  dispositions. The 38-candidate inventory has one included nominal case and
  37 individually blocked/deferred perturbation candidates. Each record has a
  candidate source identity, reason/evidence, and separate reference and
  target application status. The Xsuite case list is used only as a planning
  cross-reference.
- Added three deterministic inventory contract checks.
- Built the nominal case composite as one vertically stitched PNG from
  3300×1600 pixel, 400 dpi strips. It includes magnet-family and working-point
  sections, separate nominal `βx`, `βy`, `Dx`, `Dy`, `x`, and `y` panels, all
  available Twiss overlays/residuals, and bounded x/y coordinate-versus-turn
  tracking panels.
- Reused the previously verified iteration-0003 element-boundary and tracking
  helper as code-specific support. This is disclosed in the iteration README;
  it is not a from-scratch rewrite of those helpers.

## Smoke chronology

| Run | Report SHA-256 | Result SHA-256 | Plot SHA-256 | Assessment |
|---|---|---|---|---|
| `attempt-009` | `f56a64a0d083139506255c3931e0be070221c175d43afa911f6db45b2dc8bbee` | `c4c4f52f75e52899958ef11824bb6c3ad528c47b45a10ecda78a8c264928b1a5` | `c7337c4d3a941fa02bc39866285c37eb8abdb5b595f1fde449886e8d1e133660` | Superseded: working-point text clipped horizontally. |
| `attempt-010` | `5a9b9e10b0e66c7437a0f0af0af8ea514abcc371c0e1d562ee3c4958ffa91fc3` | `2fbf37835902f78d8f96dc98c9ef8868cc7289efbcdca7c118afec2640b3ef35` | `6adab7972f73027f0897422b544b81f64745109a6f5d0140b537ebe2fee7b5ee` | Working-point table fixed; profile residual and tracking panel titles still overlapped. Superseded. |
| `attempt-011` | `4ec50bb91d7211a8f1d9a82465e677493072562ded71234a05f06b4133e4270c` | `886977debbf148fedc94603494705bc9d6b3ec6cb79c821fb29ec1ffe667028c` | `0ed173ad9b256ae0fae113fc4045a2ffa8f4171efe69882d9fdc22c6a17d8688` | Current corrected smoke. |

For attempt 011, manifest SHA-256 is
`9627b82d73fd06a69cdd135f0e68f6ecf4d646d6823a0db558cf30bf46b5190b`, case
inventory SHA-256 is
`5b35e1a070777755ab23d52a362efddc3e1bad8c3162e5e3941c2fad0cd3964e`, plot
manifest SHA-256 is
`424e5319ab4734f69d741c35fbacb095c1c2dcde1b1e4e9ecb406b9ae6bb26b1`, and
harness log SHA-256 is
`a1634d4bd3569c0a9420efd4cbe6e369b52306746dd8c4eabed7659e1c29d00c`. The
runner SHA-256 is
`4afd7b74d364b4805d1388a75dc9e125d672eedbd7169a96b138d5dffc62ae87`; the
shell orchestrator SHA-256 is
`7e523e3f441ac4e862cc0bfdde27ef3cff4a3d204bdd4745a28ee66c836610cf`.

The smoke completed with technical outcome
`incomplete-chromaticity-and-plot-review`: 586/586 named element exits mapped;
14 profile summaries retained as `pending-tolerance`; thick tracking retained
64 turns from both paths and is pending tolerance; chromaticity remains
blocked because PyPTC's derivative coordinate is not established. Nominal was
the only executed case. The other 37 candidates are explicitly blocked with
reasons; there are no fabricated results or plots. The tracking x/y versus
turn plots are present; a phase-space plot remains unavailable because the
retained comparison records contain no momentum coordinates.

The agent visually inspected representative working-point, orbit/residual, and
tracking strips from `attempt-011` at the rendered 3300×1600 strip size. Those
strips had readable labels and no observed clipping after the correction. The
entire stitched file is 3300×36800 pixels (23 strips); image dimensions alone
are not a readability claim. This is a smoke inspection, not the user's review
of a user-run benchmark.

## Assessment and remaining limits

The corrected runner is ready for a user-run nominal-focused skill attempt.
It is not ready to claim or execute complete perturbation coverage: 37 cases
remain blocked pending independent fresh-state entry points, application
audits, response definitions/metrics, and per-case outputs. The new skill's
case-accounting requirement is met; its full multi-case definition of done is
not. The shared helper reuse is transparent and should be considered when
assessing independence of the generated workflow.

No `REP`, `EVAL`, agreement acceptance, physics acceptance, or publication
decision is warranted by these diagnostics. The full comparison remains
incomplete; a user-run attempt is needed before skill feedback is assessed.
