# Iteration 0004: updated skill case inventory

This iteration uses the current working-tree copy of
`benchmark-code-against-isis-rcs-optics/SKILL.md`, captured on 2026-10-28.
Its source checkout was at commit `f5293a3754dc8c4e9a6a4ba987603924b91949f3`
with a modified skill file; the exact snapshot SHA-256 is
`b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b`.
The snapshot itself is `SKILL.md` in this directory. It is intentionally
identified as a working-tree snapshot, not as a committed skill revision.

Run from the campaign directory:

```bash
./scripts/shell/setup-benchmark.sh
./scripts/shell/benchmark-pyptc-attempt.sh
```

The stable step-level runner has no arguments for a user run. Use
`./scripts/shell/benchmark-pyptc-attempt.sh --smoke` only for an agent
diagnostic. Each run receives the next `attempt-NNN` ID automatically.

The generated inventory assesses all 38 case candidates separately. The
Xsuite case set is only a planning cross-reference. The first smoke of this
iteration (attempt 011) exposed a nominal-only runner: only nominal was
executed and 37 cases were deferred. Feedback 0014 records that the smoke test
had encoded this behavior as success. The runner correction in feedback 0015
executed 37 cases from fresh states; attempt 017 is the retained diagnostic
for that version. The current runner now includes the full EFIELD survey table
as the 38th case, using PyPTC API level 5. Setup rebuilds the current PyPTC
shared library, while the accepted admission source inputs and base flat file
remain hash-verified. The full local EFIELD table is preserved unchanged for
both MAD-X and PyPTC. Its unsupported nonzero fields are checked before the
run; the exact Xsuite attempt-029 table is not archived, so the local test does
not claim byte-for-byte equivalence to that external candidate. All cases are
intended to retain nominal-subtracted profile and scalar responses and one
composite PNG. Agent diagnostic attempt 018 completed all 38 cases and plots;
its result, artifact hashes, and limits are recorded in feedback 0016. The
full local table completed, but its source is not the unarchived Xsuite
attempt-029 table. The diagnostic is not a user-run assessment or acceptance;
the next step is the user-run skill attempt and review.

This application reuses the previously verified PyPTC/MAD-X element-boundary
adapter and tracking helper from iteration 0003 as code-specific support; that
reuse is disclosed so it is not misrepresented as a complete from-scratch
reimplementation of those adapters. Fresh per-case entry points and source
hashes are recorded in the attempt bundle. The accepted admission library is
kept as provenance; the benchmark target is the freshly built current library
so the new EFIELD API can be exercised. This does not change the admission
disposition or create tolerance-based acceptance.

An agent smoke run is diagnostic evidence only. The user-run attempt is the
skill-test evidence to assess against this snapshot.
