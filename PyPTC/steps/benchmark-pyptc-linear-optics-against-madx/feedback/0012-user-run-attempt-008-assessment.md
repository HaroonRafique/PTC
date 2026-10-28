# User-run attempt 008 assessment

Date: 2026-10-28
Run: `runs/attempt-008`
Run class: user-run
Technical outcome: `incomplete-chromaticity-and-plot-review`
Skill: `benchmark-code-against-isis-rcs-optics`, iteration 0003, revision
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`, SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Admission basis: accepted `attempt-20261027T194128Z`, snapshot admission only
Evidence-gated publication plan: Task 6 campaign evidence and Task 9 review
maintenance in `docs/plans/2026-10-23-evidence-gated-agents-publication.md`.

## Evidence identity

| Artifact | SHA-256 |
|---|---|
| `report.md` | `590dd395c7d841a0cfb4660b9d578de5a5074c79e27026e1ab091b8046db3bdc` |
| `result.json` | `5f00aade4b4bc963e7b32054a19091b909b0438e30d25036808dd6a25027743b` |
| `manifest.json` | `95e22df5106f2ef3e4cbb1f81b6e948eb5e385fedf1375c01d551037803c4ee1` |
| `campaign_case_inventory.json` | `ff7733027ecbaa9a09ab315a4c288a0764a2fac252429ff8c6b127ef0cda65df` |
| `plot-manifest.json` | `965144f2bb072aeade942b30a103fa0c68371cbf0b0bceac12015cd7e8920410` |
| `harness-tests.log` | `c3fa15e905cdbd62fb5a6625285e60473b55d8241fc0fa9bfc086d6cc95b021e` |
| `manifest.env` | `aa949cb63f09e690c9b482169598f659e52724eab59b29499771150381661473` |
| `plots/cases/nominal.png` | `430ad40983b478a39f7acfbc546fbfe6928ce39c6afbab276ffbf5b0f7beb603` |

## Assessment against the pinned skill

The run verifies its accepted admission basis and retains matching MAD-X and
PyPTC identities. It produced 586 MAD-X TWISS rows and 804 PyPTC node rows;
all 586 element exits mapped by identity and position. Fourteen profile
residual summaries, scalar comparisons, and the nominal composite are present;
completed numerical differences remain `pending-tolerance`. The local harness
checks returned zero.

Thick bounded tracking produced complete finite records from both paths, but
both use the PTC tracking engine, so this is not independent tracking-engine
validation. Chromaticity remains blocked because the target derivative
coordinate is not established. No tolerance or physics acceptance is claimed.

The 38-case campaign inventory is present: nominal executed and plotted; all
37 non-nominal cases are explicitly `blocked-not-implemented`, with no
perturbation response outputs or plots. The single PNG therefore covers the
only executed case and does not satisfy the skill's broader declared-case
coverage. The user requested all missing cases in the runner; this run confirms
that inventory declaration has been implemented while execution and evidence
for the perturbation cases remain outstanding. This assessment supersedes no
earlier technical result and makes no acceptance decision.

## Learning comparison and disposition

The comparison with the established PyPTC optics workflow and test coverage is
already recorded in feedback 0009. Attempt 008 uses the same nominal workflow
and fixtures; no existing PyPTC example or suite was used as hidden input to
this independent skill application. The run is assessed as a user-run
incomplete skill attempt, with no benchmark acceptance, `REP`, or `EVAL`.
This local record supports Task 6 campaign evidence and Task 9 review
maintenance under the evidence-gated agents publication plan.

## Retention

After recording attempt 008 in this feedback, the corrected prune script's dry
run identified attempt 005 as the oldest of four bundles. It was pruned under
the standing three-bundle policy. Its report/result hashes and assessment
remain in feedback 0009 and the ledger. Attempts 006-008 are retained.
