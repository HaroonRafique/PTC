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
./iteration-0004/setup.sh
./scripts/shell/benchmark-pyptc-attempt.sh
```

The stable step-level runner has no arguments for a user run. Use
`./scripts/shell/benchmark-pyptc-attempt.sh --smoke` only for an agent
diagnostic. Each run receives the next `attempt-NNN` ID automatically.

The generated inventory assesses all 38 case candidates separately. The
Xsuite case set is only a planning cross-reference. The first smoke of this
iteration (attempt 011) exposed a nominal-only runner: only nominal was
executed and 37 cases were deferred. Feedback 0014 records that the smoke test
had encoded this behavior as success. The runner was corrected to execute 37
cases from fresh states: nominal, all 28 corrector polarities, the SP0_QF K1
field control, six isolated SP0_QF alignment components, and the six-component
verified survey intersection. Each executed case retains nominal-subtracted
profile and scalar responses and one composite PNG. The full EFIELD survey
table remains `unsupported` because current PyPTC applies only the six
alignment components. See feedback 0015 and attempt 017 for the correction and
smoke result.

This application reuses the previously verified PyPTC/MAD-X element-boundary
adapter and tracking helper from iteration 0003 as code-specific support; that
reuse is disclosed so it is not misrepresented as a complete from-scratch
reimplementation of those adapters. Fresh per-case entry points and source
hashes are recorded in the attempt bundle. The full survey-table case remains
outside PyPTC's current public error-table capability, so the campaign is
incomplete and claims neither complete 38-case coverage nor acceptance.

An agent smoke run is diagnostic evidence only. The user-run attempt is the
skill-test evidence to assess against this snapshot.
