# Iteration 0003 thick-tracking remediation smoke

Date: 2026-10-28
Run class: `agent-diagnostic` for every attempt below
Pinned skill: `benchmark-code-against-isis-rcs-optics`, revision
`f5293a3754dc8c4e9a6a4ba987603924b91949f3`, SHA-256
`2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26`
Accepted admission basis: `attempt-20261027T194128Z`, snapshot admission only
Preparation commit: `9cd6a824e38f0be098970ea0a3e98a387adfac3a`
Evidence-gated publication plan: Task 6 campaign evidence and Task 9 review
maintenance in
`docs/plans/2026-10-23-evidence-gated-agents-publication.md`.

Iteration 0003 is a feedback-driven correction of iteration 0002, not an
independent fresh skill implementation. It reuses the pinned skill snapshot
and verified 586-element-exit adapter. The exact iteration skill SHA matches
the pin. At smoke time the runner SHA-256 was
`8c6434d4a2f56909fdc854b3576ce3e90bbb793c6b1055449bd091e6067e94e1` and the
optics module SHA-256 was
`b3679cb197e229fda81082e8198b710f6da980fa611d3c6487157d56b313ab38`.

## Diagnostic attempts

| Attempt | Outcome | Report SHA-256 | Result SHA-256 | Manifest SHA-256 | Note |
|---|---|---|---|---|---|
| `attempt-20261027T234802Z` | `failed` | `7123d8474d2dda73eb60bf20000dd456f994edfa933121286c0b6032bff73aa7` | `4d10855367736d8ed4ac37569a3d830f35162b175d71a4d0e14644ed467429a2` | `b5ecd08771a1d5e41282c85d82e4fc111e43a2256909cd63b3886489b374f529` | Exposed target turn-history field names `x_m/y_m`; comparison expected `x/y`. Corrected in the same iteration. |
| `attempt-20261027T234834Z` | `incomplete-chromaticity-and-plot-review` | `ee0b719ad5fb074f8f23ffb5182656d21e3cd443e86a8de049766d779470c89c` | `0bf4381aa0e7ab494bacb6648a8a7f9e2ba0d970b487b9027c4c56a70b59d1b4` | `6ae924536f15140c1c82d293bc61afcf48cf8be804536fc4c609074ac3ad88c3` | No mode variable set, so default thick mode was exercised. Thick MAD-X PTC and PyPTC each retained 65 finite samples, target loss check was clear, and tracking comparison was retained as pending tolerance. |
| `attempt-20261027T234844Z` | `incomplete-chromaticity-and-plot-review` | `c7c077e40e780b784bc806d93d58e9ab05ac1ffb7784d343e8711bee85c3f7c4` | `e9ac0319cbda00a40de156154780404216f24fbdc4ff94f4d32c2e5a7d51d118` | `f8ab88c3ee61361ba37b5c46c63a961c641999284370c689089f6b27598d5752` | Initial `both` recipe omitted the leading `USE, SEQUENCE`; thin MAKETHIN ran but gave non-finite coordinates. Superseded after recipe correction. |
| `attempt-20261027T234910Z` | `incomplete-chromaticity-and-plot-review` | `d9dd48adc7b1466f9d1a6ed22671306bd25fefbf806f577767cceb49d3ae9663` | `b9dbccd49f2595c13203e99c3610597d074b46fa792a8fe73077dab7c789b385` | `0d6632d4eed83b5893757a5c1360fa1f67b98babdaf54f5ab6a89a1394709b4b` | Corrected `both` smoke: thick route complete; optional 10-slice thin diagnostic reproduced the `-0.07454545 m` negative-drift failure and was classified `blocked-reference-slicing-policy` without blocking thick tracking. |

The successful thick recipe and log in `attempt-20261027T234834Z` have SHA-256
`a1bad14738c2b07fb1707579d901b457068a9903432a3f7486f3a990a49be52d` and
`f3f669cfef01578bdfe5a88ea3ccaf2621412fc15024e13a225e2a8d52084f26`.
The corrected thin recipe and log in `attempt-20261027T234910Z` have SHA-256
`75b7b28c28544c7125a5742a8fd2673660708160bc130344c6369814f6d1926a` and
`d650f750faedbfc7fb598b0cf308e6aac1d108fe9ea3ff727bbf71575b32b5a9`.
The harness fixture log in both complete smoke attempts has SHA-256
`f960a0873524c3abc6ecb5d49bed8bde5f5a81ccd9aca9156653c59e96913c41`; all
seven iteration-local fixtures passed.

## Assessment and limits

The default thick tracking route now completes with matched turn counts and
finite records in both paths. Across 65 initial-plus-turn samples, the
iteration 0003 thick smoke reports maximum absolute residuals of
`2.495633797e-5 m` for horizontal position and `5.766946953e-5 m` for vertical
position. These remain `pending-tolerance`, and MAD-X `PTC_TRACK` and PyPTC
share PTC; this is not independent engine validation or physics acceptance.

The optional thin route is reference-only. With the probe's exact command
ordering, ten-slice `MAKETHIN` stops before tracking on a negative drift; no
matching PyPTC thin control is established. No thin result is compared or used
to change the thick route's status. The accepted lattice inputs, flat file,
strengths, harmonics, trim values, and split policy are unchanged.

These are bounded agent diagnostics, not user-run skill tests. They do not
create an `REP`, `EVAL`, tolerance decision, or physics acceptance. Retain the
newest three raw attempt bundles after this feedback and ledger record is
complete; prior identities and hashes remain in feedback 0004/0005 and the
review ledger.
