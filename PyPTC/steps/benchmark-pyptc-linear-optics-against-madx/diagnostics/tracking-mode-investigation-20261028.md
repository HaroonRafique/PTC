# MAD-X thick and thin tracking mode investigation

Date: 2026-10-28 (artifact bundle date)

## Purpose and scope

This bounded sandbox investigation follows the user-run benchmark
`attempt-20261027T232957Z`, whose MAD-X classic `TRACK` record was non-finite
after one turn. It tests whether a thick tracking reference is available and
whether thin tracking can be enabled for this accepted ISIS RCS snapshot. It
does not change the admitted lattice, set a new integration policy, assess
optics agreement, or accept a tracking comparison.

The commands reused the accepted snapshot basis
`admission_basis-accepted-attempt-20261027T194128Z/`, MAD-X 5.02.00, its five
hash-pinned inputs, and zero harmonic and trim settings. The underlying
user-run context and hashes are recorded in
[`feedback/0005-user-run-iteration-0002-assessment.md`](../feedback/0005-user-run-iteration-0002-assessment.md).
All raw recipes, logs, summaries, and generated tracking output are retained
under
`test_outputs/benchmark-pyptc-linear-optics-against-madx/diagnostic-tracking-modes-20261028/`.

## Results

| Mode | Result | Interpretation |
|---|---|---|
| MAD-X classic `TRACK` with thick sequence, no `MAKETHIN` | No track file; log reports `THICK ELEMENT FOUND` and “Track dies nicely”. MAD-X returned code 0 despite stopping the tracking command. | Classic `TRACK` cannot run this thick sequence as-is. Its process return code alone is not a success signal. |
| MAD-X `PTC_TRACK`, thick layout (`MODEL=2`, `METHOD=6`, `NST=10`, `EXACT`) | MAD-X 5.02.00 completed normally and wrote turns 0–64, 65 finite samples. | This is a working thick-mode reference path. The underlying integrator is PTC, so it is not an independent tracking-engine validation of PyPTC. It is useful for exercising the thick PTC tracking route and validating record handling. |
| MAD-X classic `TRACK` after `MAKETHIN`, explicit `SELECT, FLAG=MAKETHIN, SLICE=10` | `MAKETHIN` stopped with a fatal negative drift of `-7.454545e-02 m` between sliced dipole-fringe elements; no tracking output was produced. | A global 10-slice policy is not valid for this sequence as configured. Thin tracking is not currently an available benchmark mode under this tested recipe. |

The successful `PTC_TRACK` output ends at turn 64 with
`x=0.0009056368365 m`, `px=-0.0001471054448`, `y=0.001237059196 m`,
`py=9.028000962e-05`, `t=-0.001794797149 m`, and `pt=0`. The run reports 586
original layout elements and 6,656 thin objects internal to the PTC layout.
These counts do not imply that the admitted PyPTC flat-file split was changed.

## Evidence identity

Paths below are relative to the diagnostic directory. SHA-256 values identify
the retained raw inputs and outputs.

| Mode/artifact | SHA-256 |
|---|---|
| `native-thick-track/tracking_recipe.madx` | `cb921fbc02aa3e30750d20e73ee54cf1272ff4af4c63414767e83a2c5ac39fcb` |
| `native-thick-track/madx.log` | `a8f1d2ec81774af76c285045b7370668fa22bccfadc7496641d6f1600de81dce` |
| `native-thick-track/summary.json` | `5b0cf3fb625735b7ef742eb0f4f594131c805a508120fb2c5f7e86c3fdd0706d` |
| `madx-ptc-thick/tracking_recipe.madx` | `6ff4fbd842f90559f2f4d3473cc8044e7bf905c128a46be3cd132dce3b1b8b7c` |
| `madx-ptc-thick/madx.log` | `81b90aff622fab4ea4042f29306a5ddb90d8aaa113c780c86834275add5a49ae` |
| `madx-ptc-thick/summary.json` | `27b2c2a84588f0a278ebaddbffc722755115255b9a8ee1f8e16bf5255b68ab89` |
| `madx-ptc-thick/track.obs0001.p0001` | `e6c3e3c884544b638d6e43caa221971fc897df3dcc0576db3e19a0d261b62b64` |
| `madx-thin-10-slices/tracking_recipe.madx` | `fcc9619a6ddb7474ca60dfad33695afe0887aef5d9e9df8fdd49337ed2a78812` |
| `madx-thin-10-slices/madx.log` | `63a15cc7c3248cd4c3f52034e30a7c4e4bf2ff66fceb8db57f9d900f4030df2e` |
| `madx-thin-10-slices/summary.json` | `833cdaa106667b2093fda2ba4ccda676ebac20a0e25f8ac37c5a286baf46c30e` |

Each `summary.json` also records mode, process return code, recipe and log
hashes, output names, and relevant status details. MAD-X emitted its known
element redefinition warnings in the successful thick run; they are retained
in its log and were not used as a pass/fail criterion.

## Consequences for the next benchmark runner

Use MAD-X `PTC_TRACK` as the default thick tracking route, and label it
explicitly as sharing the PTC tracking engine with the PyPTC target. Keep
classic thin `TRACK` optional and separately classified. A request for both
modes may run the thin route only with a declared, validated slicing recipe;
the present ten-slice policy must report unavailable/blocked and must not
invalidate an otherwise successful thick-mode record. Do not infer a thin
PyPTC mode: the current public target workflow exposes `track_bunch` on the
admitted flat file, not a verified matching classic thin-lens control.

Before adding any thin policy, diagnose the sequence-positioning and negative
drift cause and show that the resulting sequence is physically and
numerically usable. Do not silently change `LMAX`, `FUZZYLMAX`, the admitted
flat file, or the MAD-X input snapshot. Keep thick-versus-thin observables
separate from the independent MAD-X TWISS optics comparison.

## Evidence-gated publication link

This is local PyPTC campaign evidence for prospective campaign capture and
review under Task 6, with review-state maintenance under Task 9, of the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md).
It is an investigation report, not a completed skill attempt, matched
cross-code tracking result, `REP`, `EVAL`, tolerance decision, or physics
acceptance. The associated user-run status remains in the benchmark review
ledger and feedback 0005.
