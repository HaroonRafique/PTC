# Admit PyPTC to the ISIS RCS

This step checks whether the current PyPTC package can load an identified ISIS
RCS simplified lattice and complete a small deterministic particle smoke run.
It is admission evidence only; it does not validate optics or benchmark
agreement.

## Environment and command

Run the setup once:

```bash
bash steps/admit-code-to-isis-rcs/setup.sh
```

Run admission with no arguments:

```bash
steps/admit-code-to-isis-rcs/.venv/bin/python \
  steps/admit-code-to-isis-rcs/run_admission.py
```

The entry point selects the highest numbered `iteration-NNNN` directory that
contains an `admission_harness.py`, then runs it with the documented defaults.
It builds PyPTC as part of the attempt. The current harness reads only the
authorized files-only snapshot in `reference_snapshot/`; it does not require
or change the external `isis_2024` checkout.

The run outputs are written under
`test_outputs/admit-code-to-isis-rcs/<attempt-id>/`. Each attempt contains a
human-readable report, canonical result, provenance manifest, MAD-X log,
reference TWISS table, generated flat file, and smoke-particle record.

## Approved reference recipe

The source revision is `1bada6a2ab94edd426c52b7e97a5d335926e0646` from the
`isis_2024` repository. The runner materializes these files from that commit:
`ISIS.injected_beam`, `ISIS.elements`, `ISIS.strength`, `2023.strength`, and
`ISIS.sequence`.

MAD-X loads the files in that order, then sets `a1=0`, `b1=0`, `kqtd=0`, and
`kqtf=0`, selects `synchrotron`, and performs one reference TWISS calculation.
It also exports a PTC flat file using the bundled MAD-X binary and PTC scripts
that belong to the current PyPTC project. The 2023 overlay scales the main
quadrupoles; the base strength file sets both trim quadrupole strengths to
zero. The runner verifies the explicit zero harmonic inputs and zero effective
trim strengths before it loads the generated flat file through the public
PyPTC Python API.

The default reference particle is the proton at `pc=0.37033168 GeV/c` specified
by the pinned input. The smoke test tracks one zero-offset particle for one
ring turn and requires finite final coordinates with no reported loss.

## Public helper behavior

`run_admission.py` requires no arguments. It detects the newest numbered skill
iteration and returns a non-zero exit status for blocked or failed attempts;
zero means only that the technical admission checks completed.

`review_ledger.csv` is separate from execution. Runs never edit it. A technical
`admitted` result remains `awaiting review` until a human records a disposition
and scope there.

## Skill-test iteration

PyPTC admission and later benchmarking skill tests follow the reviewable
iteration pattern used in `/home/hr/Codes/agentic_xsuite_test`:

1. Start each application from the exact shared-skill revision and reconstruct
   the working harness from that skill. Do not reuse an earlier agent-built
   harness as if it were a fresh skill result.
2. The user runs full skill-test attempts with the no-argument command above.
   Agent runs are limited to bounded preflight or diagnostic smoke checks and
   must be labelled as diagnostics.
3. Assess a user-run attempt against the invoked skill first. Compare it with
   existing PyPTC examples/tests afterward to identify learning; those
   examples/tests are not hidden inputs to the independent first attempt.
4. Add a new immutable, numbered feedback file with attempt and skill
   identities, evidence hashes, observations, reusable gaps, code-specific
   findings, and review state. Keep the human-maintained review ledger
   separate; the normal runner does not edit or accept its own result.
5. Keep the newest three raw bundles under
   `test_outputs/admit-code-to-isis-rcs/`. Before pruning an older bundle,
   record its attempt identity, outcome, artifact hashes, and feedback link.
   Inspect the proposed pruning with
   `bash steps/admit-code-to-isis-rcs/prune_attempts.sh`; pass `--apply` only
   after confirming the ledger and feedback records are complete.
6. Ask a separate agent in `isis-modelling-agents` to review transferable
   feedback and draft shared-skill changes for user review. Keep PyPTC-specific
   behavior here and record the exact revised skill revision before the next
   fresh application.

The initial five attempts were agent-run diagnostics, not user-run skill-test
results. Their first feedback record is
[`feedback/0001-initial-pyptc-admission-skill-test.md`](feedback/0001-initial-pyptc-admission-skill-test.md).
The record and ledger preserve the two earlier attempts' identities and hashes
after their raw bundles are pruned. Admission remains limited to lattice load,
reference-particle consistency, and the minimal smoke; optics and benchmarking
are separate steps.

## Nonclaims

Admission does not demonstrate target closed-orbit agreement, tunes, Twiss
functions, dispersion, chromaticity, long-term stability, collective-effects
validity, or benchmark agreement. Review acceptance is separate from the
technical run result.
