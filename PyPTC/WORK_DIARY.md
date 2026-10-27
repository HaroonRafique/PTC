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
