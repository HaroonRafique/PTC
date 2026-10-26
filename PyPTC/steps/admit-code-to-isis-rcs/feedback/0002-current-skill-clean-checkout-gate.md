# Feedback 0002: current-skill clean-checkout gate

## Evidence and scope

- **Evidence class:** agent-run diagnostic preflight; not a user-run skill-test
  attempt and not evidence of PyPTC admission.
- **Invoked skill:** `admit-code-to-isis-rcs`, `isis-modelling-agents` commit
  `85a897a47b55951552226221dcdbc3b83a8daf71`, skill SHA-256
  `ca7457645d0fe9049e7b55c50fc3b035b4db771bdb5984c6ab662cbe3cfbf35f`.
- **Target repository:** PyPTC commit
  `4b9a30ab61c820e99d4f5c18804cafdfdbaeb25f`.
- **Attempt:** `attempt-20261026T180201Z`, under
  `test_outputs/admit-code-to-isis-rcs/`.
- **Reference expected by the approved recipe:** `isis_2024` commit
  `1bada6a2ab94edd426c52b7e97a5d335926e0646`, simplified lattice with the
  `2023.strength` overlay, `synchrotron` sequence, include order
  `ISIS.injected_beam`, `ISIS.elements`, `ISIS.strength`, `2023.strength`,
  `ISIS.sequence`; `a1=b1=kqtd=kqtf=0`.
- **Publication cross-reference:** publication-plan Task 6 (controlled and
  longitudinal evaluation evidence) and Task 9 (event-driven skill-use and
  campaign-evidence maintenance). This blocked preflight makes no skill
  effectiveness, physics acceptance, or publication claim.

## Attempt outcome

The current skill revision was checked before constructing a fresh attempt. Its
latest change explicitly requires retaining pre-run porcelain status, verifying
the checked revision, and stopping before either engine when the clean
reference checkout is dirty. It also requires a human-readable warning summary
and tests for this gate.

A small preflight was generated in the attempt bundle from that skill revision;
the previous `run_admission.py` was not invoked. The preflight retained the
reference status as `reference_checkout_status.porcelain-v2.txt` and blocked
before MAD-X or PyPTC. The checkout at `/home/hr/Repositories/isis_2024` was at
`2ab9d5bd685f4a331e580ed56e7b070f6d5b2001`, rather than the approved
`1bada6a2ab94edd426c52b7e97a5d335926e0646`, and had 207 porcelain-v2 status
entries (tracked modifications and untracked paths). The exact status evidence
is SHA-256
`411801795c309de752963273b504610ebaea466008c71a3a868cc569b6f2e664`.

The attempt records its report (`report.md`, SHA-256
`8b3a889306882b893fdce7670ed90f92a1668596ede3b3938b49f3fdbd609aa6`),
canonical result (`result.json`, SHA-256
`e8e1ca30d9320e6fbdd940fe77a57214870157ef8505b57989ef3de2d9009813`),
manifest (`manifest.json`, SHA-256
`be48775ed9a8d0dc89774abceb84b74e687ce419cdd9acca93fde3e2324dc7e4`), and
fresh preflight script (`fresh_skill_preflight.py`, SHA-256
`bb10f90e181ec952122d81eb46f4229926db827a464c61b2ae6dc8651d3b8dd8`). The
report, result, and manifest link to the retained status evidence. Both engine
invocation flags are false. No reference inputs were copied; no output table or
runtime-warning log exists. The report states that no engine/runtime warnings
were generated or assessed because execution stopped before invocation.

The first invocation of the generated preflight itself exited before reading
the reference because I had pre-created its output directory and the script
expected to create it exclusively. No status evidence or engine activity came
from that launch. I corrected the setup to allow the pre-created attempt
directory, then reran the same preflight and retained the final script and
result above. This was a harness-construction mistake, not a PyPTC or
reference-engine result.

## Assessment against the updated skill

- The updated dirty-checkout gate worked as intended: the fresh attempt
  preserved a reviewable pre-run status record and stopped before either
  engine. It also identified the source-revision mismatch instead of inferring
  reference identity from pinned input hashes.
- The report, canonical result, and manifest link the same status record and
  SHA-256. The report states the approved recipe as planned but not executed,
  names the ledger and `awaiting review` disposition, and records that no
  reference result, PyPTC API call, bootstrap, or smoke test exists.
- The warning-summary requirement is represented for this blocked path: no
  engines ran, so there are no engine warnings to classify. No raw engine log
  can be provided for a pre-engine block.
- This attempt does not establish that a clean reference path passes, that a
  dirty checkout blocks via a mocked engine-call assertion, or that admission
  succeeds. It was intentionally limited to the observed preflight blocker.
- Prior harness gaps from feedback 0001 remain unresolved in the reusable
  `run_admission.py`; this fresh preflight did not modify or reuse that runner.
  In particular, bootstrap, API-call trace, complete admitted-report evidence,
  engine-warning classification, and the full negative test matrix remain
  unassessed by this attempt.
- No existing PyPTC examples or tests were consulted for this independent
  preflight. Their post-attempt learning comparison is deferred because no
  target-code operation was reached.

## Review and next step

- **Technical outcome:** `blocked`.
- **Review disposition:** `awaiting review`; no acceptance scope.
- **Reason:** the documented reference checkout is both dirty and at a revision
  other than the approved pinned revision. Snapshot mode has not been
  authorised, so no alternate mode or checkout was substituted.
- **Next step:** obtain a clean checkout at the approved revision through an
  explicitly selected reference path, or obtain explicit authorization for a
  working-copy snapshot. Then rebuild the full attempt from the current skill,
  run bootstrap before introducing ISIS inputs, and exercise the remaining
  skill requirements.
