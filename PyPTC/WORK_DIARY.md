# PyPTC Work Diary

This is the local work diary for the PyPTC repository. Detailed attempt evidence remains in the relevant `steps/*/feedback/` records and review ledgers.

The historical entries below were copied from `/home/hr/Repositories/isis-modelling-agents/WORK_DIARY.md` on 2026-10-27. Only PyPTC admission entries were copied; unrelated shared-repository work was excluded. Their original dates and wording are retained as historical records. From this point forward, record PyPTC work in this local diary only; do not append PyPTC work to the `isis-modelling-agents` diary. The existing shared-diary entries remain historical and are not being removed.

## 2026-10-26 — PyPTC admission skill-use feedback

Applied the current admission skill to PyPTC in five agent-run diagnostic
attempts. The final two recorded technical `admitted` outcomes, but all five
were diagnostic runs rather than user-run skill tests. Campaign feedback 0001
in the PyPTC repository records each attempt and its hashes, the final smoke
result, the harness's nonconformance with requirements already in the shared
skill, and the evidence/review gaps. The local review ledger was populated as
`awaiting review`; no acceptance was inferred. Two older raw bundles were
pruned after their identities were retained, leaving the newest three.

The separate skill-review agent confirmed that the shared skill already
requires clean-checkout verification, API/report identity, ledger linkage,
pre-ISIS bootstrap evidence, resolved provenance, normalized fingerprints,
and recipe-negative tests. It proposed only two clarifications for user
review: retain and test the clean-checkout status evidence, and summarize and
classify relevant engine/runtime warnings in the report. No shared skill edit
was made. Draft `REP-0019` links the campaign feedback to Task 6 prospective
evidence and Task 9 event-driven maintenance; no controlled evaluation,
physics claim, or usage record was added. The usage-record policy remains
inactive. Existing uncommitted repository work was preserved; this evidence
update is uncommitted and awaits user review.

## 2026-10-26 — PyPTC admission feedback follow-up

Reviewed PyPTC feedback 0001 (SHA-256
`9f22adc628017b92c12557ad642d1ce9b6961223cf4694c1933d764ef07547ad`) against
the admission skill. Added the two narrowly reusable clarifications: retain
pre-run clean-checkout status evidence and block a dirty checkout before
either engine runs; summarize and classify relevant runtime warnings in the
report, identify unresolved warnings, and link the raw log. A warning alone
does not invalidate admission when no structural or reference discrepancy
remains unexplained. PyPTC-specific harness defects and warning text were not
generalized.

The skill draft was reviewed and committed alone as
`85a897a47b55951552226221dcdbc3b83a8daf71` (blob
`8a0104c08e01aa2b49551774ebdc160570c8d6e1`). No campaign run, skill retest,
physics review, or maturity change was made. The publication chronology has
`REP-0022`, linking the feedback to the committed skill revision while
preserving `REP-0019`. The user approved the record for commit and push.
Updated the admission row in `skills.csv` to pin revision `85a897a` and state
that it has not been retested; synchronized the publication README, evidence
README, and paper-outline evidence count. These records retain the pending
review status for `REP-0019` through `REP-0021` and make no physics or
skill-effectiveness claim. `git diff --check` passed for the documentation
update. No campaign run, skill retest, physics review, or maturity change was
made. The evidence and diary update was committed as
`0e0212c7758344cf7ea0502686770a417e9d6f1e` and pushed to `origin/main`, along
with the skill commit `85a897a47b55951552226221dcdbc3b83a8daf71`. The
sandboxed push could not read the system SSH proxy configuration; the
authorized elevated retry succeeded. The PyPTC checkout was consulted
read-only, and its existing local changes were left untouched. No usage record
was created because the usage-record policy remains inactive.

## 2026-10-26 — PyPTC admission harness skill test

Committed the independent PyPTC admission harness, its first feedback record,
and the human-maintained review ledger as `4b9a30ab61c820e99d4f5c18804cafdfdbaeb25f`
(`<add>[pyptc] add admission skill-test workflow`) in the PyPTC repository. The
commit also records the local rule that diary updates, where a diary exists, are
prepared before and included with related commits; in repositories without a
work diary, the relevant campaign feedback and ledger travel with the work. The
central `AGENTS.md` rule was clarified in this same diary-bearing change.
`git diff --cached --check` passed for the PyPTC commit. The three retained raw
attempt bundles remain local and uncommitted; detailed attempt identities,
hashes, outcomes, and limitations are in the committed feedback and ledger.
These were agent-run diagnostics, not a user-run skill test, and no admission
acceptance or optics/benchmark conclusion is claimed. Next step: continue the
user-run admission iteration, assess it against the pinned skill first, then
compare with existing PyPTC examples/tests for learning.

## 2026-10-26 — PyPTC admission reattempt against updated skill

Checked the current admission skill at `isis-modelling-agents` commit
`85a897a47b55951552226221dcdbc3b83a8daf71` (blob SHA-256
`ca7457645d0fe9049e7b55c50fc3b035b4db771bdb5984c6ab662cbe3cfbf35f`) before
starting a fresh diagnostic preflight. The preflight was generated independently
from that skill revision and did not invoke the earlier `run_admission.py`.

Attempt `attempt-20261026T180201Z` is **blocked**. Before either engine ran, the
preflight retained the complete porcelain-v2 status of the documented reference
checkout. That checkout was at `2ab9d5bd685f4a331e580ed56e7b070f6d5b2001`, not
the approved `1bada6a2ab94edd426c52b7e97a5d335926e0646`, and had 207 status
entries. The retained status file SHA-256 is
`411801795c309de752963273b504610ebaea466008c71a3a868cc569b6f2e664`. No
reference calculation, PyPTC bootstrap/import, or particle smoke was run; no
engine warning evidence or admission/optics/benchmark claim exists. Snapshot
mode was not authorized.

The local report, result, manifest, status evidence, and fresh preflight script
were initially retained under
`PTC/PyPTC/test_outputs/admit-code-to-isis-rcs/attempt-20261026T180201Z/`.
Feedback 0002 records their hashes, the applicable updated-skill requirements,
and the corrected first-launch setup error. The review ledger row remains
`awaiting review`. The `180201Z` raw bundle was subsequently pruned under the
three-bundle retention policy after its identity and hashes were preserved in
feedback 0002 and the ledger. The older `131700Z` bundle had likewise been
pruned after feedback 0001 and the ledger preserved its identity. No shared
skill or physics result was changed. Next step: select an explicitly
authorized clean reference at the pinned revision or authorize snapshot mode,
then rebuild the full admission attempt from the current skill.

## 2026-10-26 — PyPTC admission snapshot completed, review pending

After the user pushed `isis_2024`, its checkout was current at
`823e6c08dfa79a182548b07706b3d46f0157137a` but still had 206 dirty status
entries and did not match the approved input revision. The user authorized a
files-only reference snapshot in PyPTC: the five required simplified-lattice
files were materialized from pinned tree commit
`1bada6a2ab94edd426c52b7e97a5d335926e0646`, with source status evidence and
hash manifest. No `.git` metadata or unrelated `isis_2024` files were copied.
The earlier `attempt-20261026T180201Z` remains a valid historical blocked
preflight; it was not rewritten as a success.

Using the updated admission skill at `85a897a47b55951552226221dcdbc3b83a8daf71`,
PyPTC attempt `attempt-20261026T200752Z` technically passed the snapshot-scoped
structural, reference-particle and one-turn no-loss checks. Nine focused harness
tests passed. It is still `awaiting review`, not accepted; 302 ignored MAD-X
redefinition warnings and three unresolved PyPTC runtime messages are retained
for review. No optics or benchmark claim was made. Feedback 0003 records the
attempt history, hashes, skill-first assessment, post-run comparison with
existing PyPTC examples/tests, and limitations. The PyPTC review ledger remains
pending. Its raw-output retention rule was applied after evidence and ledger
rows were recorded; the newest three bundles remain. No shared skill, claim,
evaluation, or experience record was changed.

Next: review the unresolved warning meanings and the snapshot-scoped result;
then decide whether to proceed to optics. Do not treat the attempt as clean-
checkout admission or reviewed acceptance.

## 2026-10-26 — User-run PyPTC admission harness failure and fix

The user ran the no-argument PyPTC entry point as
`attempt-20261026T220607Z`. The launcher selected iteration 0002 and copied the
five-file pinned snapshot, but its own harness tests stopped before either
MAD-X or PyPTC ran. The report test fixture lacked the newly required
`skill_iteration` field, raising `KeyError` in `render_report()`. The generated
bundle also mislabeled every invocation as an agent diagnostic. Feedback 0004
records the user's operator confirmation, report/result/manifest/test log and
source hashes, and explicitly makes no lattice-admission or physics claim.

The harness test fixture now includes the iteration field, and attempt labels
default to user-run, with `PYPTC_ADMISSION_RUN_CLASS=agent-diagnostic` reserved
for agent diagnostics. Ten focused harness tests passed after the fix. The full
admission was not rerun, so MAD-X and PyPTC stages remain unverified after this
change. The failed raw attempt is retained among the newest three; the oldest
raw bundle was pruned only after its evidence was covered by feedback 0003 and
the review ledger. The PyPTC changes remain uncommitted at this diary entry.
Next: make the fix available for the user's next no-argument run and reassess
that attempt from the current skill revision.

## 2026-10-26 — PyPTC admission build-stage failure and repair

The user's next no-argument attempt, `attempt-20261026T221115Z`, passed all ten
harness tests and compiled/linked `libpyptc.so`, but stopped in the export-symbol
check before either lattice engine ran. The build log listed `ptc_init_` among
the library's exported symbols while the build script reported it missing.
Feedback 0005 records the run and hashes. The check used `grep -q` in a pipeline
under `pipefail`; direct repetitions did not reproduce the false negative, so
the timing cause is plausible but not independently reproduced.

The build check now uses `awk` over the full `nm -D` listing. A subsequent
`bash build/build_ptc.sh` completed the symbol checks and ctypes smoke import.
The admission itself has not yet been rerun through MAD-X or PyPTC. The review
ledger remains pending and no physics conclusion is claimed. The three-bundle
retention rule was applied after evidence capture, retaining attempts 200752,
220607 and 221115. PyPTC fix/evidence changes are not yet committed at this
entry; an unrelated optics skill edit in this repository remains untouched.
Next: the user reruns the no-argument entry point; then assess the actual
admission stages and their warnings.

## 2026-10-27 — PyPTC user-run snapshot admission

The user reran the no-argument launcher after the build-symbol check repair.
Attempt `attempt-20261027T082315Z` passed ten harness tests, the corrected
PyPTC build and no-lattice API bootstrap, one MAD-X TWISS/export, PyPTC public
lattice load and one-turn zero-offset smoke. Its technical outcome is
`admitted-snapshot` for the five hash-identified files from pinned
`isis_2024` tree `1bada6a2ab94edd426c52b7e97a5d335926e0646`; the observed source
checkout was dirty at `823e6c08dfa79a182548b07706b3d46f0157137a`. It is not a
clean-checkout result or reviewed acceptance.

The 586 flat-file fibre count and reference-particle comparisons passed; all
requested `a1`, `b1`, and trim values were zero. Three PyPTC runtime messages
remain unresolved alongside 302 classified ignored MAD-X element-redefinition
warnings. Feedback 0006 records the skill-first audit and post-run comparison
with existing PyPTC examples/tests. It also identifies a descriptive build
method mismatch, missing linked digests for auxiliary outputs, and outstanding
harness regression coverage. The ledger remains `awaiting review`; no optics or
benchmark evidence is claimed. The three-attempt retention policy was applied,
pruning 200752Z after its hashes were recorded; 220607Z, 221115Z, and 082315Z
remain. PyPTC evidence/ledger changes are uncommitted at this diary entry.
Next: review the PyPTC warnings and provenance gaps before accepting the
snapshot result or proceeding to optics.

## 2026-10-27 — PyPTC flat-file LMAX contract discrepancy

Follow-up source inspection of PyPTC admission attempt
`attempt-20261027T082315Z` found that the `DLMAX > LMAX 0.5144` warning is a
producer/consumer contract mismatch. The shared MAD-X resplitting scripts set
`LMAX=0.5` and `FUZZYLMAX=1.1`, so the producer may leave gaps up to `0.55 m`.
The flat-file header retains only nominal `LMAX`; the separate PyPTC runtime
compares measured orbit-node gaps to that nominal value and warns. The attempt
used the established scripts; no split policy was changed. The cavity warning
is separately explained by the no-RF layout; `ORBIT_WARNING 11` combines the
cavity and LMAX warning codes.

This configuration is shared by simplified and aperture lattice generation,
and by downstream workflows using the common flat-file generator. PyPTC
`AGENTS.md`, feedback 0006, and the review-ledger entry now record the
mismatch, prohibit silent threshold changes, and require a deliberate contract
choice followed by regenerated-lattice comparisons of optics, tracking,
structure counts, and runtime. A hard nominal limit could use
`FUZZYLMAX=1.0`; preserving fuzzy splitting would require carrying the tolerance
in the flat-file contract and applying it consistently. No simulation was
rerun, no acceptance decision was made, and no commit was created. The admission
passes its recorded snapshot checks under the user's stated exclusion of the
MAD-X redefinition warnings and PyPTC cavity/LMAX warnings; the full result
remains pending human review and this is not optics or benchmark acceptance.

## 2026-10-27 — User accepted PyPTC snapshot admission

The user accepted attempt `attempt-20261027T082315Z` for snapshot admission
only and noted that there were no substantive outputs available for them to
inspect. The PyPTC review ledger now records reviewer `user`, review date
2026-10-27, and scope `snapshot admission only; no substantive user-inspectable
outputs`. Feedback 0007 records the disposition; feedback 0006 retains the
technical attempt assessment and the `LMAX` producer/consumer mismatch.

This disposition is based on the recorded checks and the user's stated
exclusion of the MAD-X element-redefinition and PyPTC cavity/LMAX warnings. It
is not clean-checkout admission, optics validation, benchmarking, independent
physics-output verification, or resolution of the `LMAX` issue. No simulation
was rerun. No commit was created.

## 2026-10-27 — Local PyPTC diary established

Created this diary at the user’s direction and copied the relevant historical
PyPTC admission entries from the shared `isis-modelling-agents` diary. This
file is now the sole work-diary destination for future PyPTC changes and
substantive findings. Keep detailed attempt provenance in local feedback and
ledger records; do not update the shared diary for PyPTC work.

## 2026-10-27 — Git history style audit

Audited the PyPTC branch history against the required commit subject format.
The recent admission-work commits from `83aaff8` onward follow
`<type>[<scope>] lower-case summary`. Older commits include subjects outside
that format, including plain summaries and legacy prefix ordering. Those
commits are existing history; they were not rewritten. `AGENTS.md` continues
to require the established format for all future commits. This initial local
diary, the diary rule, the admission review disposition, and the LMAX feedback
updates are prepared together for a style-compliant commit. `git diff --check`
passed; no simulations or tests were run for this documentation change.

## 2026-10-27 — PyPTC linear-optics benchmark skill-test preflight

Created the independent campaign step
`steps/benchmark-pyptc-linear-optics-against-madx/`, separate from admission.
Copied only the user-accepted snapshot admission bundle
`attempt-20261027T082315Z` into the step as its provenance basis; failed
admission bundles were not copied. The Xsuite effort remains independent, and
no existing PyPTC optics example/test was read to construct this first
application. The shared benchmark skill was pinned at repository revision
`a9aeca88bdf7e7e81c71423c8a99ca0937540d67`, file SHA-256
`ae393dba4f719f6416b061970f5974bf00b599db25eabfdfcb6836fbc4dfefbd`.

Iteration 0001 now has a no-argument runner, isolated setup/requirements, raw
MAD-X/PyPTC records, scalar comparisons, dispersion-normalized reference data,
capability matrix, warning evidence, mapping diagnostics, and a report. The
runner verifies and executes the exact MAD-X 5.02.00 binary from the accepted
admission, reuses the accepted inputs and flat file, and confirms `a1`, `b1`,
`kqtd`, `kqtf`, and all indexed trim values are zero. Its current output is
`attempt-20261027T143507Z`, an **agent diagnostic**, not the user's skill-test
run. It reports `blocked-profile-mapping`; no profile residual, optics
acceptance, skill completion, or publication record is claimed.

The direct reference samples contain 586 TWISS rows; PyPTC exposes 375
node-exit rows. Only 153 target exit positions have a unique exact MAD-X `s`
sample at the diagnostic `1e-9 m` check, and the largest nearest-position
residual is `2.49315 m`. Pinned source inspection confirms PyPTC Twiss values
are recorded after tracking each node and its length belongs to the preceding
interval. A diagnostic attempt to put unique MAD-X markers at every target
position failed inside a thick quadrupole with a negative drift of `-0.2596
m`. No splitting or interpolation rule was assumed. The known `LMAX` contract
is unchanged.

MAD-X's current run requests orbit, beta, alpha, dispersion, dispersion
derivatives, phase, and `CHROM`. Its `GAMMA` yields `beta0=0.36713319993`,
applied to MAD-X `DX`, `DPX`, `DY`, and `DPY` in the retained common-convention
CSV. Tune and circumference differences remain `pending-tolerance`; PyPTC's
chromaticity derivative coordinate remains unreconciled with MAD-X 5.02.00
`dQ/dDELTAP`. The run retains 302 ignored MAD-X redefinition warnings and the
PyPTC no-RF and DLMAX/LMAX messages.

Feedback 0001 records initial runner preflight, including its failed
cpymad-version probe; feedback 0002 records the later discovery and use of the
pinned local MAD-X binary, marker-insertion failure, and final diagnostic.
The local human-maintained ledger records agent attempt outcomes and hashes.
The first user run is now recorded in feedback 0003 and the review ledger;
review proceeded against the pinned skill first and then consulted existing
PyPTC examples/tests for learning. Its profile map remains blocked, scalar
differences remain pending tolerance, and no acceptance is claimed. After
feedback and ledger records were complete, the retention helper pruned the
oldest marker-placement bundle, leaving the latest three. All PyPTC diary work
remains local to this repository.

## 2026-10-27 — first user-run optics benchmark review

The user ran `setup.sh` and the no-argument `run_benchmark.py` in the separate
linear-optics benchmark step. The retained bundle is
`attempt-20261027T145757Z`; report/result/manifest SHA-256 values are recorded
in feedback 0003. The run used the accepted admission basis and pinned MAD-X
5.02.00 successfully. It again produced 586 MAD-X TWISS rows and 375 PyPTC
node-exit rows, with only 153/375 unique exact position matches at the
diagnostic `1e-9 m` threshold and maximum nearest residual `2.49315 m`.
Accordingly, the outcome remains `blocked-profile-mapping`; no profile
residuals or optics acceptance are claimed. Tune and circumference differences
are retained as `pending-tolerance`; chromaticity is blocked on derivative
convention. The review identified that historical PyPTC comparison code
interpolates onto MAD-X positions but does not establish the stricter
element/occurrence mapping required by the current skill. See feedback 0003
for the skill-first assessment, learning comparison, and exact run hashes.

## 2026-10-27 — PyPTC/MAD-X optics sampling-grid investigation

Investigated the user-run profile-map block using the accepted admission basis,
raw MAD-X TFS, PyPTC all-node CSV, mapping diagnostic, PTC flat-file parser,
checked-in PyPTC API, resplitting recipe, and recorded pinned-source
inspection. The five MAD-X source inputs match the admitted snapshot; the
PyPTC flat-file hash matches the accepted admission result. Stronger grid
checks show the 586 MAD-X TWISS names and order match all 586 flat-file fibres,
and every MAD-X `S` equals its cumulative fibre-end location within
`2.85e-13 m`. There are 563 distinct `s` positions because some rows are
zero-length/coincident entries.

PyPTC returns 375 `ORBIT_N_NODE` rows covering the same circumference. Of
these, 153 have a unique exact MAD-X position, 3 additional exact positions
are ambiguous because multiple MAD-X rows share `s`, and 219 lie inside a
flat-file fibre. Example PTC intervals combine several short MAD-X elements;
other PTC samples occur inside long drifts, a thick quadrupole, and a thick
dipole. This confirms different reporting grids and rules out one global
start/end offset. It does not establish a physics mismatch. The current
Python API only exposes the already-created PTC orbit nodes, without
arbitrary-position sampling or element occurrence identity. A PTC API/core
change or validated reference resampling could align the grids; changing
`LMAX` alone is not demonstrated to do so and remains out of scope.

The report is
`steps/benchmark-pyptc-linear-optics-against-madx/diagnostics/sampling-grid-investigation-20261027.md`.
It links the run artefacts and relevant Task 6 longitudinal-evidence and Task
9 event-maintenance requirements in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Case inventory orchestration smoke

Updated the step-level optics runner to record the complete 38-case Xsuite
attempt-029 cross-reference in every attempt bundle, with per-case configs and
execution statuses. Agent diagnostic smoke attempt 007 validated the
inventory, the existing nominal optics/tracking path, and the nominal plot
status (attempt 006 exposed a stale nominal plot-status field, corrected in
007). The smoke completed with one nominal case and 37
`blocked-not-implemented` perturbation cases. The runner does not yet perform
their per-engine setup, application verification, response comparisons, or
plots; corrector and K1 controls also lack a first-class Python setter in the
current API. Documentation now states this limitation. Feedback 0011 records
source/code revisions, run IDs, hashes, outcomes, and scope. This is local
Task 6 campaign evidence and Task 9 review maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

The benchmark prune script was also corrected from the obsolete timestamped
`test_outputs/` layout to `runs/attempt-NNN/`. After its dry run confirmed the
ledger/feedback links, attempts 001-004 were pruned; their hashes and outcomes
remain in feedback 0007/0008 and the review ledger. Attempts 005-007 are the
three retained bundles.

## 2026-10-28 — Skill case coverage cross-reference

Reviewed the pinned PyPTC linear-optics skill against user-run benchmark
attempt 005 and the Xsuite testbed's attempt-029 campaign inventory. The skill
requires a declared capability-driven case inventory and gives conditional
coverage rules for correctors, misalignments, field controls, and error tables;
it does not enumerate Xsuite's machine-specific case IDs. Attempt 005 declared
and ran only nominal, so its plot count did not satisfy the broader
perturbation evidence expectations. Feedback 0010 records every one of the 38
Xsuite attempt-029 case IDs, inventory and generator hashes, and the need to
classify each case for PyPTC applicability before claiming equivalence. The
case list is a planning cross-reference, not an assertion that all Xsuite cases
are already valid PyPTC/MAD-X comparisons. This supplemental campaign record
supports Task 6 evidence and Task 9 review maintenance in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Prepare benchmark iteration 0003 thick tracking default

Prepared iteration 0003 in response to user-run feedback 0005 and the recorded
tracking-mode investigation. The runner retains the exact pinned optics skill
snapshot and the verified 586-element-exit adapter, and explicitly labels this
as a feedback-driven correction rather than an independent fresh skill
implementation. MAD-X `PTC_TRACK` with the thick PTC layout is now the default
reference tracking route. The optional `PYPTC_BENCHMARK_TRACKING_MODE=both`
adds a separately classified classic thin-track diagnostic using the tested
ten-slice recipe; the known negative-drift failure is recorded without
blocking the thick result. The report states that MAD-X `PTC_TRACK` and PyPTC
share the PTC engine, and that a matching PyPTC thin control has not been
established. The admitted lattice, harmonics, trims, and split settings are
unchanged.

The user-facing commands, environment option, and limitations are documented
in the step README and `iteration-0003/README.md`. Bounded agent diagnostics
`attempt-20261027T234834Z` (default thick) and
`attempt-20261027T234910Z` (`both`) completed with finite 65-sample thick
records; the seven local fixtures passed. The optional thin test reproduced
the known negative-drift failure. The initial failed smoke and intermediate
thin recipe-ordering error are retained in feedback 0006 with hashes and
supersession notes. These are diagnostics, not a user-run attempt or benchmark
acceptance. This preparation supports Tasks 6 and 9 of the evidence-gated
agents publication plan. After the ledger and feedback were complete, the
retention helper's dry run was reviewed and its `--apply` pruned the four
older bundles `234802Z`, `232957Z`, `223232Z`, and `223155Z`. Their identities,
hashes, and findings remain recorded in feedback 0004/0005/0006 and the ledger.
The retained newest three are `234834Z`, `234844Z`, and `234910Z`.

## 2026-10-28 — Adopt Xsuite-style benchmark run layout

Reworked new optics benchmark output to use sequential step-local bundles at
`steps/benchmark-pyptc-linear-optics-against-madx/runs/attempt-NNN/`, leaving
all existing timestamped `test_outputs/` bundles at their original paths.
Case data is now under `cases/<case-id>/` and case composites under
`plots/cases/<case-id>.png`. Added a human-maintained `runs/INDEX.md`; the
runner allocates IDs but does not edit the index or review ledger. Feedback
0007 records the user's requirement that the reusable optics skill require a
separate composite for every simulation case, linked from the report and plot
manifest.

Agent diagnostic `attempt-001` failed after allocation because the optional
thin summary was not initialized; the fix was applied. `attempt-002` and
`attempt-003` then completed consecutive smoke runs, each with one nominal
case and one manifest-linked PNG. Reports, results, manifests and plot hashes
are in feedback 0007; all three outcomes are in the index and review ledger.
No prior timestamped bundle was moved or removed. These are diagnostics, not a
user-run skill assessment or physics acceptance. This update follows Task 6
campaign evidence and Task 9 review maintenance in the evidence-gated agents
publication plan.

## 2026-10-28 — Assess user-run optics benchmark attempt 005

The user ran the step-level Xsuite-style orchestrator, allocating
`steps/benchmark-pyptc-linear-optics-against-madx/runs/attempt-005`. The
attempt used the accepted snapshot basis and unchanged strength/split settings.
It verified all 586 named MAD-X element exits against the PyPTC map, retained
14 profile residual summaries pending tolerance, passed seven local fixtures,
and completed finite thick tracking for turns 0–64 in both paths with a clear
target loss check. MAD-X `PTC_TRACK` and PyPTC share PTC; no independent engine
validation or tolerance acceptance is claimed. PyPTC chromaticity remains
blocked on the derivative coordinate.

Skill-first review found the nominal plot present but the plot manifest points
to `aligned_profiles.csv` at the bundle root instead of
`cases/nominal/aligned_profiles.csv`; report log references also omit the
case prefix. The 3150 x 6900 composite was inspected at whole-image scale and
its small working-point text/labels are not comfortably readable. Only
nominal is currently declared, so the current one-case plot count is met, but
the broader perturbation-case response requirements remain unimplemented.
Feedback 0009 records exact artifact hashes, this assessment, and comparison
with `compare_madx_pyptc_closed_orbits.py` and
`test_madx_optics_benchmark.py`. The run is assessed with no acceptance,
`REP`, or `EVAL`; its index and review-ledger rows retain that disposition.

## 2026-10-28 — Move benchmark orchestration outside run bundles

Following the user's clarification, replaced iteration-local launch of the
Python workflow with a stable step-level shell orchestrator at
`steps/benchmark-pyptc-linear-optics-against-madx/scripts/shell/benchmark-pyptc-attempt.sh`.
It allocates the numbered run, retains a workflow log, and records stage and
command details on failure. The implementation module lives under
`scripts/python/`; iteration 0003 retains the pinned skill snapshot and domain
helpers, with its old executable runner removed. Run bundles contain evidence,
not scripts. The index and review ledger remain human-maintained.

Agent diagnostic `attempt-004` completed through the new shell path and wrote
the nominal plot. Feedback 0008 records artifact hashes and the orchestration
contract. The outcome remains incomplete under the pinned skill and is not a
user-run assessment or physics acceptance. This records the orchestration
change for Task 6 evidence and Task 9 review maintenance in the evidence-gated
agents publication plan.

## 2026-10-27 — Prepare updated PyPTC linear-optics skill attempt

Generated benchmark iteration 0002 from the updated optics skill at
`isis-modelling-agents` revision `f5293a3754dc8c4e9a6a4ba987603924b91949f3`
(snapshot SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`). It
uses user-accepted admission snapshot attempt `attempt-20261027T194128Z`, with
snapshot-only scope, and reuses the five input files, 2023 strength overlay,
zero harmonics and trims, accepted flat file, PyPTC library, and MAD-X binary
by hash. Setup and seven harness fixtures passed in the agent diagnostic.

Smoke attempt `attempt-20261027T223232Z` mapped 586 named MAD-X exits to PyPTC
fibre boundaries by name, occurrence, and position; retained 804 PyPTC node
rows and mapped the 586 named fibre exits; generated aligned profile/scalar
evidence and one nominal composite. The target completed 64 turns with 65 finite samples
and no loss. MAD-X also emitted 65 samples but became non-finite, so the
cross-code tracking comparison remains blocked as invalid reference tracking
evidence, not a numerical disagreement. Scalar and profile differences remain
pending tolerance, and chromaticity remains blocked on the target derivative
coordinate. The composite is available for user review; normal-size
readability has not been accepted. Feedback 0004 records this and superseded
smoke attempts. The review ledger records attempt identities and hashes, and
the three newest raw bundles are retained. This local record supports evidence
traceability under Tasks 6 and 9 of the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
No shared skill edit, `REP`, `EVAL`, benchmark acceptance, or physics claim was
made.

## 2026-10-27 — Assess user-run optics benchmark iteration 0002

The user ran `attempt-20261027T232957Z` using the pinned updated skill
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`. Admission provenance and hashes
matched the accepted snapshot. MAD-X produced 586 TWISS rows; the target had
804 node rows across 586 fibres, and all 586 element exits were verified by
name, occurrence, fibre, and position. Fourteen profile residual summaries
and scalar differences were retained as pending tolerance; chromaticity is
blocked on the PyPTC derivative coordinate. The target supplied a finite,
loss-free 65-sample record for 64 turns. MAD-X supplied 65 rows but had
`x=3.195 m` at turn 1 and NaNs from turn 2; comparison remains blocked rather
than reported as numerical disagreement.

The MAD-X tracking recipe's `MAKETHIN` command selected no elements and the
log says the default was one thin lens per thick element. The admitted PyPTC
flat lattice has 804 integration nodes. This is a substantial integration
method mismatch and likely invalidates the MAD-X tracking record; the specific
cause of NaNs is not yet isolated. Feedback 0005 records exact artifact hashes,
the skill-first assessment, the evidence-based tracking finding, and learning
from the existing `compare_madx_pyptc_closed_orbits.py` workflow and
`test_madx_optics_benchmark.py`. It also records missing capability inventory,
helper documentation, explicit fixtures, plot-manifest identity links, and
normal-view readability. The review ledger retains the no-acceptance
disposition. The newest three attempt bundles are retained under the campaign
policy. This evidence trail supports Tasks 6 and 9 of the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
No skill edit, `REP`, `EVAL`, or physics acceptance was made.
This is diagnostic campaign evidence, not benchmark completion or physics
acceptance; no shared publication-repository file or split setting was
changed.

## 2026-10-28 — MAD-X thick and thin tracking mode investigation

Investigated the blocked bounded-tracking record from user attempt
`attempt-20261027T232957Z` using the accepted snapshot basis and pinned MAD-X
5.02.00. Classic MAD-X `TRACK` without thin conversion stopped at the first
thick element and produced no track file, although MAD-X returned code 0.
MAD-X `PTC_TRACK` with a thick PTC layout completed 64 turns and retained 65
finite samples. Because both PyPTC and this reference path use the PTC tracking
engine, that result is not an independent tracking-engine comparison. Classic
`TRACK` after explicit ten-slice `MAKETHIN` failed before tracking with a
negative drift of `-0.07454545 m` between sliced dipole-fringe elements.

Recipes, logs, summaries, and the successful track table are retained in
`test_outputs/benchmark-pyptc-linear-optics-against-madx/diagnostic-tracking-modes-20261028/`.
The formal report
`steps/benchmark-pyptc-linear-optics-against-madx/diagnostics/tracking-mode-investigation-20261028.md`
records each artifact hash, command-mode outcome, limitation, and proposed
runner treatment. In the next runner, thick tracking is the default; thin
tracking is separately optional and must remain blocked/unavailable until a
valid slicing policy is established. This local investigation supports Task 6
campaign evidence and Task 9 review-state maintenance in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
It does not establish a matched PyPTC/MAD-X tracking result or physics
acceptance.

## 2026-10-27 — PTC orbit-marker capability probe

After committing the sampling-grid report as `e295f2a`, inspected the PTC
source and PyPTC interfaces to determine whether matching MAD-X element exits
requires Fortran work. PTC already reads `pre_orbit_set.txt` before building
its orbit layout. Its `SETORBITMARKER` command adds orbit nodes at named fibre
exits; `PRINTORBITNODES` reports orbit-node groups with integration `s`, fibre
name, fibre position, and `CAS`. Existing Python calls `PTC.init_lattice()`
and `PTC.run_script()` can drive those hooks.

A bounded probe in an isolated test-output directory selected all 516 unique
fibre names from the accepted 586-fibre flat file. PTC returned 804 nodes,
retaining the LMAX internal nodes and adding element exits. Parsing the
existing printer output matched all 586 fibre ends by fibre position, name,
and cumulative `s` within `1e-9 m`; all 563 distinct MAD-X `s` positions were
represented. The resulting tunes matched the unmarked user run exactly. No
profile residuals were calculated, so this establishes sampling capability,
not optics agreement.

The follow-up report is
`steps/benchmark-pyptc-linear-optics-against-madx/diagnostics/ptc-orbit-marker-capability-20261027.md`;
the probe script and raw files are retained under
`test_outputs/benchmark-pyptc-linear-optics-against-madx/diagnostic-orbit-marker-probe/`.
This is a local Task 6 longitudinal-evidence / Task 9 event-maintenance
campaign observation linked to the evidence-gated publication plan. It does
not need a Fortran change: the next implementation belongs in Python
orchestration and parsing. Arbitrary in-fibre sampling remains outside the
demonstrated PTC marker capability. No shared publication file, skill, PTC
Fortran, or benchmark acceptance was changed.

## 2026-10-27 — Admission skill iteration 0003

Reconstructed a new admission harness from the updated
`admit-code-to-isis-rcs` skill at shared-repo commit
`97e63b1e4ef93aee07deacf09ad9592a223fffe6` (SHA-256
`11c415652fcb053a8f5a2844ae93619ae37ae6dd74e471e67b8801c7b5dddd59`). The
new implementation is under
`steps/admit-code-to-isis-rcs/iteration-0003/`; it does not import iteration
0002. It bootstraps PyPTC before copying or reading ISIS inputs, runs 11
focused skill-contract tests, captures exact commands and an executed API
trace, retains the loaded library, and writes a non-self-referential artifact
digest inventory.

Agent diagnostic `attempt-20261027T192533Z` completed as `admitted-snapshot`
pending external review. It used the authorized five-file snapshot from
`isis_2024` tree `1bada6a2ab94edd426c52b7e97a5d335926e0646`, the 2023 strength
overlay, zero harmonics and trims, `synchrotron`, one MAD-X TWISS calculation,
and one zero-offset one-turn PyPTC smoke. The momentum difference was
`8.36e-8 GeV/c`, circumference difference `1.1e-13 m`, and the smoke was
finite and loss-free. MAD-X reported 302 ignored element redefinitions;
PyPTC retained unresolved cavity localization, `DLMAX > LMAX`, and
`ORBIT_WARNING 11` messages. This is an agent diagnostic, not the user's
full skill-test run or an independent review. The report, result, manifest,
raw evidence, and digest inventory are in
`test_outputs/admit-code-to-isis-rcs/attempt-20261027T192533Z/`. The updated
requirements around exact command recording and artifact inventory align
with the evidence completeness and traceability requirements in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md);
no shared skill or external diary was modified.

Applied the existing three-bundle retention script after confirming its dry
run. It removed the October 26 failed bundles and the earlier October 27
accepted snapshot bundle. The accepted attempt's limited scope and evidence
hashes remain recorded in feedback 0006/0007 and the ledger; the raw bundle
was removed because the standing three-newest-bundles policy applies. The
three retained raw bundles are the iteration 0003 agent diagnostics at
`192342Z`, `192432Z`, and `192533Z`; the first two are marked superseded in
the ledger.

## 2026-10-27 — User run of admission iteration 0003

The user ran attempt `attempt-20261027T194128Z`. It completed with technical
outcome `admitted-snapshot`; ledger disposition remains `awaiting review`.
Assessment found the snapshot inputs, engine commands, outputs, smoke result,
warning record, manifest/result identity, and artifact inventory inspectable.
The post-run comparison with PyPTC's saved default simplified output showed
that the default's no-overlay recipe differs from the specifically approved
snapshot recipe. The user clarified this is not an admission issue. Feedback
0008 records the assessment, comparison, and remaining report/test-coverage
suggestions. This local evidence record follows the provenance and review
traceability expectations in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
No shared skill or external diary was changed.

## 2026-10-27 — User accepts admission snapshot iteration 0003

The user accepted snapshot admission for user-run attempt
`attempt-20261027T194128Z`, whose technical outcome is `admitted-snapshot`.
The review ledger now records reviewer `user`, disposition `accepted`, and
scope `snapshot admission only`. This acceptance leaves the MAD-X
duplicate-definition and PyPTC cavity-localization/LMAX warnings recorded and
unresolved; it does not claim clean-checkout admission, optics validation, or
benchmark agreement. The user's clarification that comparison with the
default simplified-lattice generator is outside the admission criterion is
also recorded. Feedback 0009 captures the disposition and links back to the
attempt evidence in feedback 0008. These local provenance and review records
support the traceability and human-review requirements in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — User-run optics attempt 008 assessment

Assessed user-run attempt 008 against the pinned iteration-0003 skill, then
compared the reused nominal workflow with existing PyPTC examples/tests as
recorded in feedback 0009. The run mapped 586/586 MAD-X element exits, retained
14 profile residual summaries and complete thick tracking records, and
produced the nominal composite. Differences remain pending tolerance;
chromaticity remains blocked; MAD-X `PTC_TRACK` and PyPTC share the PTC tracking
engine. Attempt 008 declares all 38 cases but only executes/plots nominal; the
other 37 perturbation cases remain blocked-not-implemented. Feedback 0012 and
the ledger/index record this incomplete outcome with no acceptance, `REP`, or
`EVAL`. This is local Task 6 evidence and Task 9 review maintenance in the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

After feedback 0012 and the ledger captured attempt 008, the corrected prune
script's dry run identified attempt 005 as the oldest of four bundles. It was
pruned under the three-bundle policy; its evidence hashes remain in feedback
0009 and the ledger. Attempts 006-008 are retained.

## 2026-10-28 — Updated optics skill iteration 0004 smoke

Pinned the current modified optics skill as `iteration-0004/SKILL.md` (SHA-256
`b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`, based on
shared-repository commit `f5293a3754dc8c4e9a6a4ba987603924b91949f3`). The new
inventory uses the skill's case dispositions and records evidence and
reference/target application status for all 38 candidate cases. One nominal
case is included; 37 perturbations remain blocked/deferred with reasons. The
Xsuite list is a planning cross-reference only. The runner now creates a
vertically stitched nominal PNG from 3300×1600 strips and has three focused
inventory contract checks.

Diagnostic smoke attempts 009 and 010 exposed clipped/overlapping figure
labels. Attempt 011 completed after those fixes. It mapped 586/586 element
exits, retained 14 profile residual summaries and complete 64-turn thick
tracking records, and generated a 23-strip 3300×36800 nominal image. I
visually checked working-point, orbit/residual, and tracking strips at their
normal rendered size. Chromaticity remains blocked, all differences remain
pending tolerance, 37 perturbations remain deferred, and phase-space plotting
is unavailable because the comparison records contain no momentum coordinates.
This remains an agent diagnostic, not a user-run benchmark or acceptance.
Feedback 0013, the run index, and the review ledger preserve the attempt
evidence and limitations.

The updated runner explicitly reuses the iteration-0003 boundary/tracking
adapter and records that limitation; it is not a from-scratch rewrite of those
helpers. After evidence was recorded, the three-bundle policy pruned attempts
006-008 and retained attempts 009-011; the older report/result hashes and
assessment links remain in feedback and the ledger. Attempt 011 is the current
smoke.
This is local Task 6 evidence and Task 9 review maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Iteration 0004 nominal-only runner gap

Review of the iteration-0004 attempt builder found that all 38 candidates were
listed, but `run_attempt()` hard-coded one nominal MAD-X/PyPTC execution and
one nominal plot. Its smoke test explicitly expected one included case and 37
deferred cases, so the diagnostic passed without satisfying the skill's
multi-case requirements. Feedback 0014 records the concrete code paths,
requirements, and correction criteria. The 37 cases cannot be deferred merely
because their execution paths are missing; each needs execution or a
PyPTC-specific evidence-backed disposition. Correcting the runner and its smoke
checks is in progress; attempt 011 remains a nominal-only diagnostic, not a
multi-case benchmark or user-run result. This is local Task 6 and Task 9 work
under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Multi-case runner correction complete

Feedback 0015 records the completed runner correction and diagnostic evidence.
The workflow now executes and plots nominal plus 36 supported perturbation
cases from fresh MAD-X/PyPTC states: all 28 corrector polarities, the SP0_QF K1
control, six isolated alignment components, and the six-component verified
survey intersection. Each case retains profile and scalar nominal-subtracted
responses. The full EFIELD survey case is explicitly unsupported because the
current public PyPTC reader does not apply its non-alignment field components.
Attempt 017 passed eight deterministic checks, mapped 586/586 reference exits,
completed all 37 included cases, and produced 37 case plots. Its result is
`incomplete-perturbation-coverage`, not acceptance; response tolerances remain
unreviewed and chromaticity remains blocked. Attempts 012-016 record the
intermediate failures and corrections; their hashes and dispositions are in
feedback 0015 and the review ledger before pruning under the three-bundle
policy. This is local Task 6 evidence and Task 9 maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — MAD-X EFIELD API investigation started

Created feature branch `feature/pyptc-efield-api` from clean commit
`32933d9`. The current Python error-table reader retains only six alignment
columns and calls `MAD_MISALIGN_FIBRE`; it does not implement general MAD-X
`SETERR` field errors. The checked-in Apr 2026 corrected survey table has
nonzero entries only in DX, DY, DPHI, DTHETA, and DPSI, so that table alone
does not prove multipole field-error support is needed. The exact Xsuite
attempt-029 table was not included in PyPTC attempt 017. PTC multipole
deviation arrays are accessed by existing additive AC/ramp shims, but MAD-X
field semantics and API sufficiency remain to be established. Investigation
provenance and scope are recorded in
`steps/benchmark-pyptc-linear-optics-against-madx/investigations/0001-efield-api.md`.
This is Task 6 investigation work under the evidence-gated agents publication
plan; no benchmark acceptance is implied.

## 2026-10-28 — MAD-X magnetic EFIELD API and side-by-side example

The feature branch now exposes integrated normal/skew magnetic multipole
errors through API level 5. The additive native shim and Python wrapper map
orders 0–20 to PTC magnet multipole arrays; the error-table API also applies
alignment columns and distributes parent-family integrated errors across
slices. Nonzero fields outside the implemented magnetic/alignment set are
rejected before lattice mutation. This required no edits to PTC core Fortran.

The repeatable example `examples/06_madx_efield_api.py` runs the checked-in
ISIS survey table and a synthetic K1L/K1SL case through fresh MAD-X and PyPTC
states. It maps all 586 element exits, retains per-case aligned CSVs, plots,
MAD-X recipes/logs, API traces, hashes, and machine-readable results under
`test_outputs/06_madx_efield_api/`. The standalone native build, focused
three-test parser suite, and full comparison example passed. Wrapped
tune-response residuals were 8.34e-6/-1.15e-6 (survey) and
1.23e-5/-8.92e-7 (synthetic) for Qx/Qy; synthetic orbit-response residuals
were below 1.1e-13 m. Maximum beta response residuals were 6.61e-3 m and
4.72e-3 m. No tolerances were supplied, so this is functional comparison
evidence and not tolerance-based acceptance.

The example also confirms that nonzero MREX is rejected. Monitor readout and
scaling, RF phase, and RF frequency/harmonic/lag fields remain unsupported.
The exact EFIELD table from Xsuite attempt 029 is still not archived in this
repository and was not treated as equivalent to the checked-in survey table.
The detailed scope, hashes, results, and evidence-gated publication-plan link
are in
`steps/benchmark-pyptc-linear-optics-against-madx/investigations/0001-efield-api.md`.
README and capability documentation describe the supported fields and retained
example. This is Task 6 implementation/evidence work; acceptance and the
external candidate's disposition remain open for review.

## 2026-10-28 — Include full EFIELD table in iteration 0004

The new PyPTC EFIELD API is API level 5, while the accepted admission bundle
preserves an API-4 library. Iteration 0004 setup now builds the current PyPTC
shared library, checks API level 5, and records the candidate library
separately from the immutable admission evidence. The accepted input snapshot
and base flat file remain hash-verified.

The runner now includes all 38 catalogued cases. For the full EFIELD case it
copies `apr_2026_survey_corrected.tfs` unchanged, audits it for nonzero
unsupported fields, and supplies that same table to fresh MAD-X and PyPTC
runs. The exact EFIELD table from Xsuite attempt 029 remains unavailable, so
the local table run is not described as byte-for-byte equivalent to that
external case. The local table has no nonzero K terms; the separate synthetic
K1L/K1SL EFIELD example exercises those new magnetic multipole fields.

Nine case-inventory checks passed; setup rebuilt the library and verified API
level 5. Agent diagnostic attempt 018 completed 38/38 cases and produced 38
case plots, with zero failed or unexecuted candidates. It mapped 586/586
nominal element exits and completed thick tracking for 64 turns. The result is
`incomplete-chromaticity-and-plot-review`: chromaticity remains blocked and
all tolerances remain pending. Feedback 0016, the run index, and review ledger
record artifact hashes, source/API identity, the full EFIELD application, and
review limits. This does not constitute user-run assessment or acceptance.
This is Task 6 campaign evidence and Task 9 maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Keep benchmark entry points outside iteration folders

Moved the current API-5 setup command to
`steps/benchmark-pyptc-linear-optics-against-madx/scripts/shell/setup-benchmark.sh`.
The single current attempt command remains in `scripts/shell/`. Removed the
obsolete iteration-0001 through iteration-0003 setup/run entry points. Moved
the active iteration-0003 adapters to `scripts/python/iteration_0003/`, moved
the superseded iteration-0002 helper/test source to `scripts/archive/`, and
moved current case tests to the step-level `tests/` directory. The iteration
folders now contain no `.py` or `.sh` files; a test enforces that rule.

The relocated setup rebuilt the API-level-5 shared library. Ten inventory
tests passed. A bounded adapter subprocess smoke through the new path produced
804 node rows, 586 fibres, and 804 printer groups; its outputs and report are
in `steps/benchmark-pyptc-linear-optics-against-madx/test_outputs/benchmark-runner-layout-smoke/`.
No new full attempt was allocated. Attempt 018 remains the evidence for the
38-case run and was completed before this path-only reorganization. Feedback
0017 records the old/new paths, hashes, and limits; the user command is now
`./scripts/shell/setup-benchmark.sh` followed by
`./scripts/shell/benchmark-pyptc-attempt.sh`. This is Task 6 campaign
maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Assess user-run benchmark attempt 019

Attempt 019 ran all 38 declared PyPTC/MAD-X optics cases and produced all 38
per-case composite images. Its 586 MAD-X element exits map to PyPTC at the
verified 1e-9 m tolerance, and the 64-turn thick tracking comparison completed
with 65 samples. The full local survey EFIELD table applied 38 records through
the API-5 build. The attempt remains incomplete and unaccepted: the PyPTC
chromaticity derivative coordinate is unresolved, response tolerances and
meaningful-response floors are pending, and the nominal composite is 3300 x
36800 pixels and unreadable at normal viewing size. Feedback 0018 records the
skill-first assessment, comparison with the existing EFIELD example/tests,
hashes, and corrective actions; the review ledger and run index record no
acceptance. This is Task 6 evidence and Task 9 review maintenance under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).

## 2026-10-28 — Resolve derivative coordinates and optics units

Ran bounded off-momentum diagnostics from attempt 019's accepted flat-file
basis and matched MAD-X recipe. The scan established that PyPTC's native
`lattice_GET_CHROM` value is per PTC `PT = ΔE/p0c`, while MAD-X 5.02.00 `DQ1/DQ2`
are per `DELTAP = Δp/p0`; the matched MAD-X tune slopes reproduce the `DQ`
headers. The common-coordinate conversion is therefore
`dQ/dDELTAP = beta0 * PTC.chromaticities()`. Converted values differ from
MAD-X by about +3.00 (X) and +3.04 (Y), so the previous raw numeric near-match
was misleading and chromaticity remains out of agreement pending cause and
tolerance review.

The same scan checked MAD-X dispersion at three named rows and found
`dX/dDELTAP = beta0 * DX`, supporting the adapter's existing `beta0 * DX`
conversion to PyPTC `etax`. The field-by-field coordinate/unit table also
records that `PX/PY` are dimensionless canonical momenta; the adapter's `rad`
labels are only paraxial approximations and need correction in a future
benchmark revision. The low-amplitude horizontal tune slope was less stable
than the vertical slope, which is retained as a diagnostic limit.

Full calculations, source paths, hashes, artifacts, conversions, and campaign
actions are documented in
`steps/benchmark-pyptc-linear-optics-against-madx/investigations/0002-derivative-coordinates-and-units.md`.
The original attempt-019 files and blocked result remain unchanged. This is
diagnostic evidence under the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md),
not acceptance or tolerance approval.

Following the three-bundle retention rule, attempts 015 and 016 were pruned
after feedback 0015 and the review ledger preserved their identities, hashes,
and outcomes. The retained raw bundles are attempts 017–019.

## 2026-10-30 — Draft PyPTC documentation package and literature review

Created `pyptc_documentation/` as a self-contained, source-grounded documentation
package based on the maintained ISIS technical-note class. It includes a detailed
execution plan, a narrative PTC literature review with full citations and direct
URLs, BibTeX, a PDF retrieval/hash/access manifest, five retrieved PTC/FPP PDFs,
source and claim ledgers, a draft technical note, editable TikZ diagrams, and
seven byte-identical PyPTC example/comparison plots with a provenance manifest.
The copied class's chopped-beam keyword defaults were replaced only in the local
copy. The template source was not changed.

The note follows the user path from build/import and lattice initialization
through optics, tracking, apertures, edits, and evidence boundaries. Code claims
are tied to PyPTC commit `8824003c956390e921a1d469f77c247859a63258` and recorded
source hashes. Coordinate/unit semantics, field interpretation, golden-case
status, code correspondence, physics review, and reader review remain pending.
The review records that the 2002 CERN PDF endpoint returned anti-bot HTML and
the historical 2006 MAD-X PTC manual URL served a distinct 2010 PTC User's
Reference Manual; these were not conflated. PDF redistribution rights also
remain unreviewed.

The final 14-page A4 draft built with the documented pdfLaTeX/BibTeX sequence.
LaTeX checks found no unresolved citations/references, missing files, or
overfull boxes; the local class and report content have no chopped-beam text.
All 14 rendered pages were visually inspected. The ISIS claim-ledger checker
passed with 0 errors and 0 warnings; its self-test passed. Build logs, extracted
text, metadata, and page renders are kept under
`pyptc_documentation/test_outputs/rendered_pages/`. Draft PDF SHA-256:
`ad761c77a3f241fe21aeb72c27e00ee77f36918accb4ea9676fbe8602b6ca337`.

The package is a working draft and does not claim scientific validation or
publication readiness. The implementation follows the evidence-gated
documentation expectations in the
[ISIS modelling-agent publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
Detailed task status, questions for later refinement, exact build checks, and
retrieval limits are recorded in
[`pyptc_documentation/PLAN.md`](pyptc_documentation/PLAN.md). No commit or push
was made at the time this entry was drafted; this entry is included with the
documentation package commit.
