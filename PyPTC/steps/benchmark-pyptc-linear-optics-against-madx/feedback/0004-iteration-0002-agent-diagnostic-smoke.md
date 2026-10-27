# Iteration 0002 agent diagnostic smoke and handoff

Date: 2026-10-27
Run class: `agent-diagnostic`
Skill: `benchmark-code-against-isis-rcs-optics`
Skill repository revision: `f5293a3754dc8c4e9a6a4ba987603924b91949f3`
Skill snapshot SHA-256: `2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Iteration: `0002`
Accepted admission basis: `attempt-20261027T194128Z`, accepted by the user for snapshot admission only.
Evidence plan: `docs/plans/2026-10-23-evidence-gated-agents-publication.md`,
Tasks 6 and 9.

## Final diagnostic

The fresh iteration was made from the pinned skill snapshot and accepted
admission bundle. It reuses the exact admitted PyPTC library, MAD-X 5.02.00
binary, five source inputs, and flat file by hash. The effective recipe uses
the accepted 2023 strength overlay, `synchrotron`, zero `a1`/`b1`, zero trims,
and no resplitting. The repeatable setup completed in the step `.venv`; the
no-argument runner auto-selects it. Seven focused harness fixtures passed.

Final smoke bundle: `attempt-20261027T223232Z`
Outcome: `blocked-bounded-tracking`
Report SHA-256: `464224d34a967aec23bf3b499174450cc9a107be974d6564f135225b0258685d`
Result SHA-256:
`d3037c0250716545c8c0d64e183077efb55151c1a427d363982c90d2e93345c8`

The mapping verified all 586 named MAD-X TWISS rows against PyPTC fibre
identity, occurrence and exit position. PyPTC returned 804 orbit-node Twiss
rows across 586 fibres; the verified boundary map selects the 586 named fibre
exits. Source-based family classification found no unmapped element names.
Profile data, signed residual summaries, scalar
comparisons and one nominal composite were generated. No observable tolerance
has been reviewed, so completed differences remain `pending-tolerance`.
Chromaticity remains blocked because the PyPTC public wrapper does not
establish the derivative coordinate.

The target tracking workers retained 65 samples for 64 turns, finite
coordinates and no reported loss. MAD-X also retained 65 samples, but its
coordinates become non-finite after the first traversal. Its process returned
success, which is not evidence of a valid tracking record. The comparison is
therefore `blocked`, classified as non-finite reference evidence; it is not a
numerical disagreement. Raw MAD-X and PyPTC tracking logs, recipes, and
histories are in the attempt bundle. No bounded-tracking agreement claim is
made. The composite was visually inspected in the diagnostic viewer; the
current tall raster is available for user inspection and should receive a
normal-size readability review before any plot acceptance.

## Earlier iteration 0002 diagnostics

These agent-only bundles were superseded during harness development. Their
exact report/result hashes and outcomes are recorded here and in the ledger;
they are not user-run benchmark results.

| Attempt | Outcome | Report SHA-256 | Result SHA-256 | Finding |
|---|---|---|---|---|
| `attempt-20261027T222725Z` | failed | `ce3c72661eb15fb7156923b5826889a04a4a19c80c1b2e612b7f8e9dba255d78` | `4d563bcc004afa8ccc7c0e6f01c742b708958c45a7b27ad0f79784a13609bcf5` | Admission schema used an older MAD-X binary hash key. |
| `attempt-20261027T222735Z` | `blocked-bounded-tracking` | `5ff1a4501750c91f31716816ea8087e325d24fbaaf871df50291c60c82e0b849` | `c8722913968ce5036e8a5e47b5ace88d9682fb93bad48f59a56738027d27303` | Mapping and profiles ran; MAD-X recipe readback was corrected to print effective values. |
| `attempt-20261027T222840Z` | failed | `39e6352f1454756fd1851a22bb9e658b005bee959676f7d55441494e342a2d70` | `a5d570e077c7c7c97fee8deb52a04bbe5d3f80d8148961bfcae5cc366be3b236` | Worker cleanup discarded API-level metadata before it was recorded. |
| `attempt-20261027T222850Z` | `blocked-bounded-tracking` | `31cebd54ddfb78350243eaa0d914fd737cdc251bdd6f7722aed0ef5f71f7cb42` | `ffac831ae4bdc4f7e87bf02dc07abdb0cc9a9456b6351472c41cead91d621fbd` | Mapping ran; subprocess isolation was added to prevent native PTC output from corrupting the terminal. |
| `attempt-20261027T222923Z` | `blocked-bounded-tracking` | `f25379c8b297fe78ea4409769ebea0b7f6fed605aa554b6a626166f5f878b678` | `76c78d5be7ee9a7f0b79bc67180f6e728af3b9feaf3a7ef1a4c123bdd02115e4` | First clean mapping and profile run; composite layout was revised. |
| `attempt-20261027T223155Z` | `blocked-bounded-tracking` | `9150720f116601557b7830f960a559d1bf2815744eb6386fcb257509603f48a4` | `3aee4a21e9d9d9967269ba3b02f4103580b017016a06bb60706be2e07dd32b9` | Exposed non-finite MAD-X tracking and an initial target-worker input-shape error. |

Earlier diagnostics `attempt-20261027T143428Z` and
`attempt-20261027T143507Z` remain covered by feedback 0002; the user-run
`attempt-20261027T145757Z` remains covered by feedback 0003. The new iteration
does not rewrite or reinterpret those records.

## Assessment and handoff

This is a successful harness smoke, not a complete skill benchmark. It
exercises a useful subset of the updated workflow: exact admission provenance,
MAD-X reference generation, PyPTC public marker sampling, verified element-exit
mapping, common profile/scalar output, plot generation, and bounded tracking
records with completeness and finite checks. The user should run the documented
no-argument command and review the resulting report and plot. After that,
assess the user-run attempt against the exact skill first, then compare the
workflow with PyPTC examples/tests for learning. Keep any feedback in a new
numbered file and retain the review disposition in the ledger. Do not treat
this diagnostic as a user-run result or physics acceptance.

The updated skill's broader fixture, capability-inventory, helper-documentation,
plot-manifest, and normal-size plot-readability requirements still need a
deliberate skill-first assessment. No shared skill edit was made. This local
record supports evidence traceability under publication-plan Tasks 6 and 9;
the episode remains an observational campaign and creates no `REP` or `EVAL`.
