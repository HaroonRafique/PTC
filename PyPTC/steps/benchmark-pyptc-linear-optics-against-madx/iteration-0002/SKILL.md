---
name: benchmark-code-against-isis-rcs-optics
description: Use when comparing an admitted code's ISIS RCS linear optics or bounded tracking with cpymad/MAD-X; exclude nonlinear, resonance, and production studies.
---

# Benchmark a Code Against ISIS RCS Optics

Use this skill after `admit-code-to-isis-rcs` has a reviewed accepted outcome.
Establish a first, capability-aware comparison of a target code with a named
ISIS RCS `cpymad`/MAD-X reference. This is linear-optics and bounded
single-particle evidence, not a nonlinear or production benchmark.

## Scope and boundary

This skill compares the same identified reference recipe, effective machine
state, and reference particle on both sides. It covers closed or reference
orbit where applicable, linear optics, phase advance, tunes, dispersion,
circumference, and a small deterministic single-particle tracking cross-check.
Compare chromaticity when both codes provide an equivalent tune-versus-momentum
observable. Element-by-element quantities and turn-by-turn coordinates may be
compared when both sides provide equivalent observables.

Do not use it for amplitude-dependent tune, tune scans, resonance crossing,
Poincaré maps, long-term stability, collective effects, large particle sets,
or optimisation. Those need a later nonlinear or benchmark workflow after
this stage is accepted. Do not retune either model, change the machine state,
or alter an input recipe merely to reduce a discrepancy. If the user explicitly
directs an additional benchmark input or overlay beyond the accepted admission
recipe, record it as a separate benchmark recipe, including its provenance,
hash, application order, and effective settings. Apply the same resulting
machine state to the reference calculation and target import, and state that
the extra input is outside the admission's reviewed scope. Do not treat it as
admission evidence or silently change the recipe when authorization is unclear.

## Human-usable target-code workflow

Before interpreting benchmark results, leave the target project with a small,
documented workflow that a user can run and extend without an agent. Prefer the
target code's supported public API and build a thin, readable ISIS-facing layer
around it; do not duplicate or modify core physics when an adapter is enough.

- Provide a shell setup script that creates or activates the documented
  environment, installs the declared dependencies, and checks the loaded code
  and runtime versions. Make it repeatable and explain any required path
  overrides.
- Put useful repeatable actions in named Python functions or the target
  language's equivalent. Keep each function focused, explicit about inputs,
  outputs, units, and state changes, and consistent with the project's
  formatting, naming, and API conventions. Use descriptive domain names,
  idiomatic syntax, ordinary control flow, and concise docstrings; avoid opaque
  abbreviations, hidden global state, giant agent-only scripts, or unnecessary
  abstractions.
- Make the normal simulation entry point a readable sequence of those calls:
  resolve the machine input, initialise/load the lattice, define and validate
  the reference beam, calculate orbit and Twiss/linear optics, then perform
  the declared bounded tracking and save diagnostics. Keep configuration and
  analysis calls visible at the top level; keep their implementations in the
  reusable functions.
- Document the setup and run commands and each public helper's purpose,
  arguments, returned data, units, and side effects. The benchmark cases must
  call these same user-facing functions so the workflow being validated is the
  one the user will later use.

If the target project does not yet have this scaffold, create it before
benchmarking. Keep admission-level installation and lattice-load checks within
`admit-code-to-isis-rcs`; use this skill to add and exercise the optics and
bounded-tracking actions without changing their physics definitions.

## Required inputs

Before running a comparison, identify and record:

- the reviewed accepted admission record, its scope, and the target-code,
  runtime, and ISIS-reference identities it covers;
- the exact reference recipe and ordered input closure, including strength
  overlays or other post-input operations, reference mode, effective machine
  state, lattice variant, selected sequence, reference-particle record, and
  reference-run artefacts. Hash every input and record effective settings so
  both code paths can be shown to use the same state;
- target-code configuration and supported public APIs for orbit, optics,
  tracking, and tune estimation;
- coordinate, unit, sign, longitudinal-variable, and element/position mapping
  conventions; and
- an observable-specific comparison plan: definition, sampling or mapping,
  conversion/interpolation method where needed, absolute and/or relative
  tolerance, and acceptance owner for each proposed agreement claim.

For every proposed corrector, error, misalignment, or error-table comparison,
also declare the nominal-to-perturbed response observable, response norm, and
minimum meaningful response in each engine. Choose an observable that is
physically sensitive to the component being tested; closed-orbit response is
not suitable for every alignment or field perturbation. Record the pinned
target-library version, the inspected public import/application API, and every
effective setting. Verify effective behavior with a controlled response
comparison; a source-table read-back, element-name match, mutated source model,
or successful import call does not establish that the target applies a
perturbation. For each cross-code response observable, also declare its
agreement tolerance, tolerance source, and acceptance owner, or classify it
`pending-tolerance`. Report the numerical response difference, residual
statistic, and classification for every declared response observable even if
the chosen response plots show only orbit. Also retain numerical cross-code
comparisons for every observable in the benchmark's declared per-case
parameter set; a response plot limited to orbit does not narrow that reporting
set. Keep this agreement tolerance separate from the minimum
meaningful-response floor, which only gates whether application was observed.
Scope each response tolerance to its observable family, plane, and residual
metric; a reviewed orbit-response tolerance does not cover optics-profile,
tune, or chromaticity responses. Report which observable families have reviewed
criteria and leave the others `pending-tolerance`. Make every capability-matrix
verdict explanation agree with the criterion's actual scope: do not say a
response tolerance is absent when one has been reviewed for the stated
observable, plane, and metric, and do not extend that criterion to unreviewed
families.

Do not infer a tolerance from a convenient plot or an unrelated code. If no
reviewed tolerance exists, calculate and retain the difference but classify
the observable as `pending-tolerance`; it cannot support an agreement claim.
Stop with `blocked` for an ambiguous reference identity, admission scope,
machine state, convention, mapping, or observable definition.

## Chromaticity definition and coordinate conversion

Treat chromaticity as the tune derivative with respect to relative momentum at
the declared reference state:

```text
delta_p = (p - p0) / p0
xi_x = dQx / d(delta_p)
xi_y = dQy / d(delta_p)
```

This is not a derivative with respect to longitudinal position, arrival time,
or path-length coordinate. `cpymad` exposes MAD-X results; it does not define a
separate chromaticity convention. Record the MAD-X engine version, the actual
TWISS option and summary fields used, the reference particle, and the
coordinate with respect to which each reported derivative is defined.

The MAD-X User's Guide defines `PT = DeltaE / (p_ref c)` and
`DELTAP = Delta p / p_ref`; near the reference particle it gives
`PT = beta0 * DELTAP`, where `beta0` is the reference particle's relativistic
speed divided by `c`. Its `SUMM.DQ1` and `SUMM.DQ2` definitions are derivatives
with respect to `PT`. Convert those values to momentum chromaticity with the
chain rule:

```text
xi_x = beta0 * dQx/dPT
xi_y = beta0 * dQy/dPT
```

Use `beta0` for the same reference particle and run; do not substitute a beta
from a different admission or machine-state record. MAD-X's `TWISS, CHROM`
calculation evaluates tunes at the requested `DELTAP` and at
`DELTAP + 1e-6`. The output convention changed in MAD-X 5.06.00 from
`dQ/dDELTAP` to `dQ/dPT`. Therefore pin the engine version and follow its
version-matched definition: apply the factor `beta0` to `dQ/dPT`, and do not
apply it to a result already reported as `dQ/dDELTAP`. For coupled lattices,
record whether `CHROM` was enabled; MAD-X documents it as needed for proper
chromaticity calculation with coupling. Record the nominal `DELTAP`,
finite-difference method and step, and whether the result came from matrix
derivatives or the explicit tune difference. A field named `DQ1` alone does
not identify which convention was used.

Convert another code's result to the same `dQ/d(delta_p)` definition before
comparing. If its derivative is with respect to a different scalar coordinate
`u`, use `dQ/d(delta_p) = (dQ/du) * (du/d(delta_p))` at the same reference
state. For example, if `u = DeltaE/E0`, the local conversion is
`dQ/d(delta_p) = beta0^2 * dQ/du`; if `u = PT`, it is
`beta0 * dQ/du`. Derive other conversions from the code's documented
coordinate definition and the same species and reference energy/momentum.
When a trustworthy analytic conversion is unavailable, evaluate tunes at
matched physical momentum offsets and estimate both slopes against
`delta_p`, using compatible tune unwrapping and finite-difference settings.
Never equate a derivative with respect to `z`, `ct`, time, or path length to
chromaticity without an explicit physical mapping to momentum deviation.

Report the native definition, conversion factor, `beta0`, tune branch/mode,
offsets and estimator method with the converted values. Check that the result
is stable to a bounded change in finite-difference step when making a precision
claim. The MAD-X definition establishes units and normalization, not a
cross-code acceptance tolerance; until one is supplied and reviewed, classify
the difference as `pending-tolerance`.

If a plane-specific chromaticity residual persists after reference-state,
coordinate, and estimator reconciliation, inspect whether the pinned target
code's element-model settings differ from the reference. For Xsuite imported
bends, run a controlled edge-model diagnostic on fresh lines: compare the
importer default/linear model with `edge="dipole-only"` and `edge="full"` at
matched nominal and symmetric off-momentum points. For the diagnostic variant,
configure a fresh line with the Xsuite control
`line.configure_bend_model(edge="dipole-only")`; do not mutate the line already
used for the importer-default baseline. Record the pinned Xtrack version,
effective settings, tune slopes in both planes, and any nominal-tune shift.

For the cited testbed recipe (`isis_2024` commit
`fcf2a348087d96ae9a3b48e481c0fc5560b9663f`, `00_Simplified_Lattice`,
`synchrotron`, symmetric `2023.strength` overlay; Xsuite `0.58.0` and Xtrack
`0.110.0`), the vertical slope at `delta_p` step `1e-4` was
`-4.806175978859795` for MAD-X, `-4.635748516776950` for the Xsuite importer
default, and `-4.806175986891148` for `edge="dipole-only"`. The default
residual was `+0.170427462082845`; the dipole-only residual was about
`-8.03e-9`. The nominal vertical tune stayed within about `8e-10` of MAD-X.
`edge="full"` also gave a close slope, so dipole-only is not established as the
only model setting that reproduces this curve. These are findings for that
input and pinned versions, not expected values or acceptance criteria for
another run.

Keep the diagnostic variant separate from the main benchmark result. Record
the effective bend-edge setting for every fresh Xsuite line used in the main
cases. If no expert method review has adopted a bend-edge override, state the
setting actually used (including importer defaults when unchanged) and judge
chromaticity from those main cases; a close diagnostic curve does not change
the main-case verdict. If a reviewed decision adopts `edge="dipole-only"`,
apply and verify it on every fresh Xsuite line in the main cases, record it in
the resolved configuration and report, and recompute the affected comparisons.
Do not configure only the diagnostic line and present its result as a
production benchmark fix, universal equivalence, or physics acceptance. The
change remains a model-level result; the detailed MAD-X element-map equivalence
has not been independently proved.

## Capability inventory and comparability

Before calculations, make a compact capability matrix for the reference and
target code. Include reference/closed orbit, `Qx`/`Qy`, `βx`/`βy`, `αx`/`αy`,
horizontal and vertical dispersion and derivatives, phase advance,
circumference, chromaticity, element/position sampling, single-particle
tracking, and tune-from-tracking. Where both sides expose equivalent
definitions, also inventory corrector kicks/orbit response, trim-quadrupole or
harmonic tune control, integer/fractional/harmonic tunes, RF/harmonic data,
aperture metadata, and error or misalignment application. For each, record one
of:

- `comparable`: same observable, state, convention, and mapping are available;
- `unavailable`: one side cannot produce it;
- `non-equivalent`: outputs exist but definitions or models differ materially;
- `blocked`: an unresolved dependency prevents a meaningful calculation;
- `unbenchmarked`: the target exposes a feature with no reviewed comparable
  reference or expectation yet; and
- `pending-tolerance`, `within-tolerance`, or `out-of-tolerance`: a completed
  comparable calculation with its acceptance state.

Use `blocked` with the reason `target-application failure` when a declared
reference perturbation has a meaningful response in the chosen observable but
the target response is zero, below its declared significance floor, or
unverified. If that observable has no meaningful reference response, do not
infer that the perturbation is absent or the target failed: select and validate
a physically sensitive observable, or mark the case non-informative for the
proposed response test. A significance floor determines whether application
can be observed; it is not a cross-code tolerance. Application failure is
missing setup/interface evidence, not a numerical result and never
`pending-tolerance`.

Run every fair comparison exposed by the inventory. Do not silently omit a
capability because it is inconvenient. A missing common-core capability may
produce a useful limited report, but cannot support full first-pass acceptance;
state that scope explicitly. Chromaticity and element/position comparison are
additional capability-aware checks, not common-core prerequisites. Record
unavailability without preventing an otherwise complete scoped first-pass
result, but compare chromaticity when both codes can provide a documented
tune-versus-momentum observable. Convert it to the common momentum definition
below; do not skip the comparison merely because the codes use different
longitudinal momentum variables.

The common core, when both paths support it, is orbit, `βx`/`βy`, `αx`/`αy`,
dispersion and derivatives, phase advance, scalar `Qx`/`Qy`, circumference,
and matched bounded tracking. Each needs an equivalent reference and target
record, resolved conventions and mapping, an aligned table or scalar summary,
residual metrics, and a required plot or readable table. `pending-tolerance`
means that this completed evidence awaits a tolerance decision; it cannot
stand in for absent data, a missing plot, an unresolved mapping, or a
target-only tracking record.

## Case isolation

Each declared nominal, corrector, misalignment, error-table, or other
perturbation case must have an independently invocable user-style target-code
entry point. Start it from a fresh declared state rather than a mutable model
left by another case. Retain the case configuration, source identity/hash,
transformation/application record, and entry-point identity. An orchestrator
may run several cases, but it must not conceal state inheritance between them.
Treat a state-leaking or unidentifiable declared case as technically
incomplete, not as a numerical comparison result.

## Perturbation application evidence

For every declared perturbation, retain nominal and perturbed records for each
engine, then calculate each engine's response as `perturbed - nominal` before
making a target-versus-reference claim. If the reference response is below the
predeclared threshold, first determine whether the chosen observable is
sensitive to that perturbation. Select and validate a sensitive observable if
needed; if none can be established, mark the response test `blocked` as
non-informative, not as target-application failure. Matching zero responses do
not validate target application. If the reference response is meaningful, the
target must show and retain a verified response before its cross-code residuals
or tolerance can be interpreted.

For an error table, classify every requested component on each side as
`applied-and-verified`, `ignored`, `unsupported`, or `non-equivalent`.
`applied-and-verified` requires a component-specific fresh-state response
record consistent with the documented transformation, not merely successful
input parsing. A full-table comparison is comparable only over the
intersection of components verified on both sides; show all excluded
components and their classification. Keep the component names and
code-specific transformations in the campaign.

When a benchmark claims complete corrector-response coverage, define the
source-identified corrector set and declared kick settings and polarities
before running. For bidirectional coverage, run both declared polarities for
every corrector from an independent fresh nominal state; record each element,
plane, sign convention, setting, and applied-strength audit. A selected subset
supports only a subset claim, not complete corrector coverage. Do not turn a
campaign-specific kick magnitude into a shared default.

For transformed errors and misalignments, also establish source-to-target
transform semantics before interpreting a residual. For each field, record
the source operation order and coordinate-frame convention, the target import
API operation or attribute that receives it, and the target's sign, frame,
and composition semantics. Test each component in a fresh isolated state with
an observable that is physically sensitive to it, and compare the response
with the source model. A correct field readback or a measurable response alone
does not establish that the same physical transform was applied. If the target
offers distinct element-frame and no-frame operations, compare those
alternatives only in disposable diagnostic states. Keep diagnostic remaps out
of the benchmark path unless a separately authorized recipe records and
validates the change; leave remaining discrepancies unresolved until the
mapping is explained.

When perturbation cases are used to localize a discrepancy across excitation,
field-strength, and alignment behavior, establish separate controls for each
class before interpreting the combined cases. In particular, a corrector
response does not validate a quadrupole field-strength error, and an isolated
field-error control does not validate alignment transforms. Compare cases in
stages and keep independent unresolved observables separate; reporting them
together does not establish a causal relationship.

## Procedure

1. Confirm the admission review disposition is accepted and that its scope
   covers the target version and reference used for admission. Reuse its
   resolved inputs, hashes, logs, recipe, and nonclaims. If the user separately
   directs a benchmark input beyond that scope, record the authorized recipe
   and its delta from admission; do not present the added input as admitted or
   accepted. Stop if the effective benchmark recipe or its authorization is
   ambiguous.

   Confirm that the target project also has the documented shell environment
   setup and user-facing, reusable functions described above. If it does not,
   add that scaffold before the comparison; use the admission skill for
   installation and initial lattice-load checks, then expose the optics and
   tracking actions as readable target-code functions.

2. Freeze the comparison configuration. Record the reference and target
   commands, versions, dependency/runtime identities, every ordered input and
   overlay hash, the operations that create the effective machine state, seed
   where applicable, and output location. Confirm that the same resulting
   state feeds the reference calculation and target import. Inspect the pinned
   target-library source/API for relevant import behavior; record the source
   revision and every effective option, and use a controlled comparison to
   distinguish unsupported import from a configuration-induced model change.
   Declare proposed observables, mapping/sampling, tolerances, and the
   independent reviewer or acceptance record before interpreting results. For
   every declared case,
   record its fresh-state entry point, configuration, transformation, and
   source identity before it is executed. For a perturbation, also record the
   response observable/norm/threshold and target public application API with
   every effective setting.

3. Reconcile observables before comparing values. Confirm species, mass,
   charge, energy, momentum, beta, gamma, rigidity, transverse and
   longitudinal coordinates, orbit definition, Twiss/emittance convention,
   dispersion convention and normalisation, tune convention, phase origin and
   unwrapping, and longitudinal position origin and direction. For an ISIS
   MAD-X TWISS comparison using `dx`, `dpx`, `dy`, and `dpy`, apply the
   established Lorentz-beta normalisation before comparison: derive
   `beta = sqrt(1 - GAMMA^-2)` from that run's TWISS `GAMMA` header and multiply
   those four columns by `beta`. Record the header value, derived beta,
   conversion direction, and units; apply it consistently to aligned data,
   residuals, tables, and plots. For nominal-subtracted response profiles,
   transform both nominal and perturbed MAD-X records to the common convention
   before calculating their response; do not subtract native values with
   different normalizations. Do not substitute beta from the admission particle
   record. Establish
   entrance versus exit sampling, element identity plus occurrence mapping,
   position tolerance, periodic wrap, and every error-table or model
   transformation before interpreting residuals. Document any interpolation,
   its method and uncertainty, and unmatched elements; do not use it to hide
   a non-equivalent model. Do not compare arrays merely because they have the
   same length. For each code and pinned version, verify whether each Twiss
   row describes an element entrance, element exit, or an explicit periodic
   endpoint; record the API option that selects the sampling location and the
   element/occurrence and `s` value attached to every retained row. Never label
   an entry value with that element's exit position. Construct the cross-code
   boundary map from those verified row semantics, element occurrences, and
   physical positions rather than assuming equal row indices. If one API
   supplies entry values while the other supplies exit values, map the same
   physical boundary explicitly, including the final periodic endpoint. Check
   every mapped position against the declared position tolerance, and handle
   zero-length elements and repeated `s` values by element identity and
   occurrence; do not collapse or shift rows based on position alone. Retain
   the original row identity, sampling location, mapped counterpart, and
   position residual in the aligned data. If the mapping cannot be verified,
   classify the profile as `blocked` and do not interpret its residuals.
   In the attempt-019 investigation, pinned Xtrack `0.110.0`
   `Line.twiss()` returned entry values by default and included a periodic
   `_end_point`; requesting `values_at_element_exit=True` raised
   `NotImplementedError`. Treat this as version-specific evidence, not a
   promise for other releases: inspect the pinned version's API/source and
   verify the actual output before constructing the map.

4. Generate the reference and target linear-optics records without changing
   the reviewed machine state. For every `comparable` common-core observable,
   retain the raw records and compact aligned comparison table or scalar
   summary. Calculate signed and absolute differences, maximum and RMS
   residuals where meaningful, and the tolerance verdict. Show scalar results
   and profile residuals together: agreement in global tunes or circumference
   cannot stand in for agreement of beta, alpha, dispersion, phase, or
   chromaticity profiles. Leave large unexplained residuals visible and do not
   make a broad optics-agreement claim from selected scalar matches. Reference
   Twiss, phase, and tune values identify the run; target-code agreement
   requires the aligned comparison. A missing available common-core reference
   or target record makes the technical comparison incomplete, not
   `pending-tolerance`.

   For chromaticity, retain the native value and definition alongside the
   converted `dQ/d(delta_p)` value for each plane. Record the reference
   particle's `beta0`, code/version, tune branch assignment, nominal momentum
   offset, sampled offsets, finite-difference or matrix method, step, and
   conversion factor. Compare like-for-like estimates or re-evaluate both
   tune-versus-momentum curves at common physical momentum offsets. If the
   method, mode, or coordinate cannot be reconciled, classify chromaticity as
   `blocked` or `non-equivalent`, explain why, and retain the differences
   without inventing a tolerance. A completed conversion without an
   observable-specific reviewed tolerance remains `pending-tolerance`.

5. Produce reviewable plots from saved aligned data, not hand-copied numbers.
   Create one combined multi-panel plot file for each simulation case. Include
   every available comparable profile in that case's declared parameter set:
   orbit, `βx`, `βy`, `αx`, `αy`, dispersion and derivatives, phase advance,
   and any other declared TWISS profile. Combine the existing per-observable
   plots into this file without changing their definitions or presentation:
   each observable keeps its own independently scaled panel and its reference/
   target overlay against mapped `s`, plus a signed residual subplot at half
   the main-panel height. Use one case-level artifact, not a separate image
   file for each parameter. Include the case's existing scalar/working-point
   plot and readable scalar summaries where applicable; use a readable table
   rather than a fabricated plot only for scalar or unavailable observables.
   Build the plot manifest around the single case-level file and identify each
   panel group, linking it to exact aligned data, observable definition, units,
   scaling, mapping, identities, and masked or unmatched regions. Define the
   signed residual direction, such as `target − reference`, in each panel and
   table. Preserve case and code identities, overlays, visible markers, units,
   and mapping context in every profile panel.
   Include any declared perturbation-response plots as distinct panel groups
   in that same case file, preserving their existing observable definitions,
   overlays, residual direction, and scaling. Do not emit separate response
   plot files.

   In the nominal case composite, include the existing nominal master
   TWISS/orbit overview from the unperturbed lattice, before corrector,
   alignment, or survey-table perturbations. “Unperturbed” means no declared
   perturbation; retain the same approved base recipe and any explicitly
   authorized strength overlay used by both codes.
   Plot aligned MAD-X/reference and target data against the same verified
   mapped `s` samples. Give every plotted parameter its own panel so its scale
   and differences remain independently readable; do not combine beta and
   dispersion axes in one panel. Include separate panels for `βx`, `βy`, `Dx`,
   `Dy`, horizontal orbit, and vertical orbit when those observables are
   available. Distinguish both code series with clear labels and visible
   markers; use no connecting line or subdued/dashed lines so markers remain
   prominent.

   Keep a magnet-family colour strip at the top. Use yellow for main dipoles,
   dark green for main quadrupoles, red for trim quadrupoles, and a very light
   colour for drifts. Determine family membership from the identified lattice
   source and document the classification rule, source, and any ambiguous or
   unmapped elements; do not infer main-versus-trim membership from a plot
   name or choose colours as a substitute for classification evidence. Render
   other element families distinctly and consistently, with a legend or key.

   Add an associated working-point panel with explicit labels `Bare horizontal
   tune`, `Bare vertical tune`, `Bare horizontal chromaticity`, and `Bare
   vertical chromaticity`. For each label show the MAD-X/reference value, the
   target-code value, and the signed target-minus-reference difference. Use
   `dQ/d(delta_p)` for chromaticity after the documented conversion. Show the
   effective recipe/overlay identity, units, and verified sample mapping in
   the plot or its caption. Build this overview from saved nominal records and
   identify it as a distinct panel group in the case-level plot manifest and
   report; do not write a separate master-plot file. It is an at-a-glance view
   only: keep the detailed per-observable profile, residual, and perturbation-
   response panel groups distinct within the composite, and do not count the
   overview as a substitute for those residual plots. Do not infer agreement
   from the overview or working-point values.

   In sampled profile and response plots, make the sample markers visually
   prominent; avoid dominant solid connecting lines. In the plot manifest,
   record the sampled point count and mapping separately from raster image
   dimensions and DPI. These describe longitudinal sampling and image
   rendering independently; neither alone establishes that the data are
   sufficiently resolved. Do not impose a universal sampling or image
   resolution threshold without an observable-specific reviewed requirement.
   Visually inspect representative rendered composites at normal viewing size.
   Axis titles, tick labels, units, legends, and plotted data must be readable
   without relying on extreme zoom. Choose figure dimensions, panel layout, and
   font sizes based on panel count and intended viewing size; increasing pixel
   dimensions or DPI alone does not establish legibility. Create only output
   directories that contain artifacts, and use the same actual artifact
   locations in the report and manifest. Do not advertise empty per-case plot
   directories when composites are stored in a shared case-artifact folder;
   record which representative figure was checked for normal-size readability.

6. Run a bounded deterministic single-particle tracking cross-check only after
   its linear prerequisites are interpretable. Run both reference and target
   with the same declared initial condition relative to the same orbit, the
   same observation point and coordinate convention, a predeclared finite turn
   count, loss/finite policy, a named integration recipe for each engine, and
   tune-estimator settings. Record relevant integration controls and provide a
   bounded refinement or convergence check when making a precision tune claim.
   Retain both records, coordinate-versus-turn and phase-space plots,
   estimator inputs/settings, estimator resolution and limitations, and the
   derived tune comparison; do not use a scan or production tracking campaign.
   Before plotting, tuning, or classifying the result as comparable,
   validate that both records contain the declared complete turn count at the
   same observation point. State whether the retained sample count includes an
   initial row or only completed turns, and verify the corresponding expected
   count. Select and checkpoint the reference-tracking recipe/engine before
   execution; retain its runtime log or trace. Classify reference-engine setup
   failure, truncated reference record, target runtime failure, and numerical
   disagreement separately. A partial or target-only tracking record is
   `blocked` setup/interface evidence, not a completed common-core tracking or
   tune comparison. Compare turn-by-turn coordinates only when synchronisation
   and element mapping are equivalent; otherwise compare stated derived
   observables and record the limitation.

7. Compare every additional fair capability, such as chromaticity or
   element-by-element values, with the same provenance and classification.
   When claiming corrector response, correction, misalignment, or error-table
   comparability, define named perturbation cases, source identity and hash,
   transformation, applied-element mapping, and per-case evidence before
   interpreting results. Verify each case through its independently invocable
   fresh-state entry point before comparing it. For each perturbation, retain
   machine-readable nominal-to-perturbed response metrics for reference and
   target, and data-derived plots with nominal/perturbed overlays and signed
   response residuals. Where a source table is transformed before application,
   retain the source-to-reference-applied-state audit as well as the target
   application record. Do not compare across codes until both sides' response
   evidence passes the declared meaningful-response gate; classify a meaningful
   reference response with a zero, below-floor, or unverified target response
   as `blocked` for `target-application failure`. Select a response observable
   sensitive to each active component before applying the significance floor;
   an orbit-only zero for a component that changes optics is not evidence of
   failed application. Keep the significance floor distinct from any
   cross-code tolerance. Record the difference, residual statistic, tolerance
   source, and verdict for every declared response observable, or mark it
   `pending-tolerance`. If claiming complete bidirectional corrector coverage,
   include every source-identified corrector at each declared polarity from a
   fresh nominal state. When staged localization spans corrector excitation,
   field-strength error, and alignment behavior, compare a separate
   single-element field-error control before interpreting alignment cases; a
   passing control for one class does not validate another. For error tables,
   retain the per-component
   classifications and compare only their verified intersection. Keep
   code-specific controls, table names, and paths in the campaign rather than
   this skill.
   Record target capabilities that the reference cannot benchmark as
   `unbenchmarked`, together with the observable definition and proposed later
   reference/expectation source. Do not convert a new target-only feature into
   an agreement claim. Do not execute or plot a Poincaré map or other nonlinear
   diagnostic in this skill; route a requested resonance study to a separately
   scoped nonlinear workflow after first-pass review.

8. Publish a compact campaign-local report, canonical result, capability
   matrix, difference tables, and plot manifest. Distinguish technical results
   from reviewed acceptance. Retain per-code comparison and difference logs so
   a later code with an equivalent feature can reuse a reviewed expectation;
   preserve the original reference and scope rather than treating a previous
   target code as automatically authoritative.

   Whenever a code reaches technical completion under this skill, append a
   repository-level completion record to
   `docs/publications/evidence-gated-agents/evidence/chronology.md`. Use one
   `REP-####` record per completed code/reference/recipe/run; preserve earlier
   records instead of replacing them when a code is rerun. Include the target
   code and version, skill revision, reference and effective recipe identity,
   run ID, and links or hashes for the campaign report and comparison data. For
   every observable and case, record its definition and units, the tolerance
   criterion and its source/reviewer, the signed target-minus-reference
   difference and appropriate maximum/RMS residual, and the resulting
   `within-tolerance`, `out-of-tolerance`, or `pending-tolerance` status. When
   no tolerance has been supplied, retain the measured differences and mark
   them `pending-tolerance`; do not omit them. Identify user-approved
   screening tolerances as campaign-specific and keep them distinct from
   physics acceptance. Keep full tables, plots, and raw run artefacts in the
   campaign repository; the shared record is a compact summary and provenance
   link, not a duplicate campaign archive.

## Evidence bundle

Keep raw and derived evidence in the campaign repository. The inspectable
bundle must include:

- admission and reference identities, scope, resolved configuration, commands,
  versions, input identities/hashes, seed, and mapping identity;
- reference and target raw orbit/optics/tune records, aligned comparison
  tables or scalar summaries, residual metrics, tolerances, and
  per-observable classifications;
- native and converted chromaticity values for both planes, their tune mode
  and momentum-coordinate definitions, reference-particle beta where needed,
  sampled offsets/method/step, conversion factors, and signed differences;
- the capability matrix, including unavailable, non-equivalent, blocked, and
  unbenchmarked functions;
- exactly one combined multi-panel plot file per simulation case, containing
  profile, scalar/working-point, and declared response plot groups, plus a
  manifest that links the case artifact and each panel group to its exact data,
  observable definition, units, scaling, mapping, case/code identities, and
  signed residual direction; include the nominal master TWISS/orbit overview
  and working-point values as a panel group in the nominal case file, with
  distinct sample-count and raster-rendering metadata;
- tracking initial conditions, turn count, loss/finite policy, retained
  reference and target coordinates or compact diagnostics, named integration
  recipes and relevant controls, tune-estimator method/settings/resolution,
  any refinement or convergence check, derived tune comparison, tracking
  plots, observation-point identity, requested-versus-retained sample counts,
  and reference/target runtime logs or traces;
- named perturbation-case records, where those capabilities are compared,
  including independently invocable entry points, fresh-state confirmation,
  source identities/hashes, transformations, element mappings, target public
  application API and effective settings, nominal and perturbed records,
  the physically sensitive response observable and separate significance
  floor, machine-readable response metrics, response plots, and per-case
  outputs;
- the ordered machine-state inputs and operations, including any explicitly
  authorized benchmark-only additions beyond the admission recipe, with
  effective settings and evidence that reference and target used the same
  resulting state;
- for each transformed source table, its source-to-reference-applied-state
  audit where supported, and for each error-table component, its per-engine
  application classification and verified comparison intersection; and
- an explicit nonclaims list, including all deferred nonlinear validation.

Keep compact reviewed summaries and expectation records versioned when the
campaign policy permits. Do not commit bulky raw tables, particle dumps, or
plot collections to this shared repository.

## Definition of done

Technical comparison evidence is ready for review only when:

- the accepted admission scope and reference identity cover the admitted code
  and base reference; any separately authorized benchmark-only input is
  identified, provenance-pinned, applied consistently to both paths, and
  excluded from the admission claim;
- every comparable profile common-core observable is aligned, quantified, and
  included with visible sample markers in its own panel group within the
  single composite plot file for its case; no separate per-parameter plot
  files are emitted, including for response plots. Each panel group is linked
  from the data-derived plot manifest with sample count/mapping kept distinct
  from raster dimensions/DPI, and classified; every
  scalar common-core observable has a readable aligned summary table or
  working-point panel, and the nominal case composite includes the master
  TWISS/orbit overview with both codes on the same mapped longitudinal
  coordinate, recipe, and working-point comparison;
- no available common-core observable lacks an equivalent reference/target
  record, resolved convention/mapping, aligned data, or required plot/table;
- every missing, non-equivalent, blocked, and target-only capability is
  visible in the capability matrix;
- every agreement claim has a predeclared reviewed tolerance, while all other
  differences remain `pending-tolerance` or otherwise non-accepted;
- every available chromaticity comparison uses the common
  `dQ/d(delta_p)` definition or is explicitly classified `blocked` or
  `non-equivalent`, with its conversion and tune-estimation method retained;
- the bounded tracking cross-check has documented initial conditions, finite/
  loss result, named integration recipes, retained reference and target
  records, tune method and estimator limits, derived tune comparison, plots,
  limitations, reference-tracking checkpoint, common observation point, and
  complete declared sample counts; and
- every declared perturbation case has fresh-state configuration provenance
  and no unresolved state inheritance, and every meaningful reference response
  uses an observable sensitive to that perturbation and has target-side
  application evidence before any cross-code comparison claim; for transformed
  errors or misalignments, source-to-target operation order and frame semantics
  are also recorded and verified; every response observable has its own
  tolerance and verdict or remains `pending-tolerance`; and any complete
  bidirectional corrector-coverage claim includes every declared corrector and
  polarity; and
- the report names the remaining nonclaims and does not relabel a reference
  fingerprint, target-only capability, or tracking smoke check as optics or
  nonlinear agreement; and
- this repository contains a `REP-####` completion record for the target code,
  reference, recipe, and completed run, with per-observable/per-case
  tolerances, signed differences and residual summaries, and the review state
  linked to the campaign evidence.

## Harness checks

Keep deterministic harness checks independent of retained raw bundles. Use
compact fixtures to verify that independently invoked cases with conflicting
perturbations do not inherit state; complete and partial tracking records are
distinguished; initial-plus-turn and completed-turn sample-count conventions
are validated; and plot-manifest entries name identities, units, mapping, the
signed residual direction, and the residual-panel layout. A test fixture may
imitate a failed reference engine, but must not label that setup/interface
failure as numerical disagreement. Include fixtures where an import succeeds
but a required target application setting is omitted, and where a full table
silently applies only some components. They must classify the former as
`blocked` for `target-application failure`, expose the latter's component
coverage, and permit comparison only for the verified component intersection.
Include a perturbation whose orbit response is zero while a declared optics
observable changes, so an insensitive orbit-only gate is not mistaken for
failed application. Include a tracking case where identical coarse FFT bins
are reported with their resolution limits and are not promoted to a precision
tune-agreement claim. Verify that the nominal master-plot manifest entry
links the aligned nominal data, effective recipe, shared position mapping,
both code identities, magnet-family classification source, and converted
working-point values. Fixtures must include an entry-versus-exit offset and a
final periodic endpoint; ensure an entry value cannot be labeled with the same
element's exit `s` and that duplicate positions from zero-length elements
remain distinguishable by element occurrence. Check that each master-plot
observable has its own panel, the requested magnet-family colors and explicit
bare working-point labels are present, sampled profile and response plots keep
markers visible, and sample counts are recorded separately from raster
dimensions and DPI. For transformed misalignment cases, include a semantic
mapping check that distinguishes source frame/order from target API behavior;
if multiple target transform operations exist, ensure a diagnostic alternative
cannot silently replace the declared benchmark mapping. For claimed complete
corrector coverage, check that the declared element-by-polarity matrix has no
missing cases and that each case starts from a fresh nominal state. Include
distinct corrector and field-strength control cases when localizing
discrepancies across excitation, field, and alignment behavior. Check that
each response observable has a cross-code tolerance or is reported
`pending-tolerance`, separately from its meaningful-response floor.
For each fixture case, check that the manifest resolves to exactly one combined
plot file containing all declared profile and response panel groups, that the
nominal case file also contains the master overview group, and that no separate
per-parameter or per-response plot files are emitted. Verify that combining
panels preserves each existing observable's independent scale, overlay,
residual direction, marker visibility, and panel layout.
Check a dense representative composite at normal viewing size for readable axis
titles, ticks, units, legends, and data; pixel count or DPI alone must not pass
this check. Verify every plot path named by the manifest/report exists and that
no advertised plot directory is empty. For Xsuite, verify the effective
bend-edge setting is recorded for every fresh main-case line; an approved
override must be applied consistently, while an unapproved diagnostic variant
must not replace the main-case result. Check that capability explanations name
the exact tolerance scope and do not contradict its observable-level verdict.

Only a separate reviewed acceptance may authorise a subsequent nonlinear
workflow. An accepted first-pass optics comparison does not validate tune
variation, amplitude-dependent tune, resonance structures, Poincaré maps,
long-term tracking, collective effects, or an independent benchmark.

## Evidence and provenance

This reusable workflow is based on the staged ISIS integration and comparison
principles in `ISIS_modelling_agents_project_spec.md` and the source hierarchy.
The following code-specific sources inform the boundaries but do not prescribe
their implementations for another target code:

| Source | Evidence used |
|---|---|
| [PyPTC](https://github.com/HaroonRafique/PTC), `PyPTC/{README.md,docs/PTC_CAPABILITIES.md,workflows/madx/compare_madx_pyptc_closed_orbits.py}` | node-level Twiss/orbit, phase/tune consistency, MAD-X comparison plots/residuals, perturbation provenance, and bounded loss-aware tracking diagnostics |
| [ISIS optics GUI](https://gitlab.stfc.ac.uk/isis_accelerator_models/optics_gui), `README.md` | MAD-X-backed orbit, Twiss, tune, resonance-diagram, and machine-state separation |
| [PTC-PyORBIT3 examples](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/ptc_pyorbit3_examples), `common/diagnostics/README.md` | saved diagnostics, tune extraction, and compact output practice |
| [Survey-to-lattice FMon analysis](https://gitlab.stfc.ac.uk/isis_accelerator_models/survey_to_lattice), `08_fmon_tune_analysis/README.md` | explicit diagnostic subset and persisted comparison outputs |
| [ISIS-I_Models MAD-X User's Guide copy, commit `4c4f26d871d787379aa2c80c5f78005e4cd2ab61`](https://gitlab.stfc.ac.uk/mmf67433/isis-i_models/-/blob/4c4f26d871d787379aa2c80c5f78005e4cd2ab61/MADX_References/madxuguide.pdf), §§1.7.1, 1.7.4–1.7.5, 19 | MAD-X `PT`/`DELTAP`, `SUMM.DQ1/DQ2`, and the `TWISS, CHROM` tune-difference calculation and coupling note |
| [Official MAD-X 5.06.00 change log](https://github.com/MethodicalAcceleratorDesign/MAD-X/blob/5.06.00/Changes.md), release commit `c961b78` | Version-specific change of `TWISS, CHROM` chromaticity output from `dQ/dDELTAP` to `dQ/dPT` |
| [Xsuite ISIS testbed feedback 0008](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/9d70337f58c5d02b951f88190572e2a9c2475232/steps/benchmark-code-against-isis-rcs-optics/feedback/0008-attempt-017-cross-code-consistency-and-completion.md) | User-run feedback on consistent effective inputs, component-sensitive responses, tracking completeness and estimator limits, convention/sampling reconciliation, and the distinction between global scalars and optics profiles; numerical and physics acceptance remain open |
| [ISIS 2024 bare-TWISS plot](https://gitlab.stfc.ac.uk/isis_accelerator_models/isis_2024/-/blob/fb8c3a26706dac5250420beb2d8263a57f013fcb/Methods/HB25/01_Apply_Misalignments/twiss_bare_corrected.png), image SHA-256 `51cc1d4db9618e1c8c76362cfdaf37ccea00b55c304ace883a2051c23457feeb` | User-selected visual precedent for the lattice strip, beta/dispersion overview, separate horizontal and vertical orbit panels, and tune title; presentation precedent only |
| [Xsuite ISIS testbed](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test), attempt-018 feedback files `steps/benchmark-code-against-isis-rcs-optics/feedback/0009-attempt-018-benchmark-assessment.md` (SHA-256 `9a92ce3c6d090aea0af49fc6e904816555da99420a97875321d2a951ebbbfe55`) and `0010-attempt-018-master-twiss-plot.md` (SHA-256 `cd45af03a5da3ffbd1f79e3a3ca9f27a6328df19f594bbed0e15750bc6a8926c`) | User-reported attempt-018 plot gaps: missing bare/nominal master TWISS/orbit view, marker prominence, and the need to distinguish sample density from raster rendering; both feedback files were untracked when these hashes were recorded, and no tolerance or resolution adequacy is established |
| [Xsuite ISIS testbed](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test), attempt-019 feedback `steps/benchmark-code-against-isis-rcs-optics/feedback/0011-attempt-019-master-plot-and-twiss-boundary-investigation.md` (SHA-256 `4a7f717d379aaa18396c4ee90b525a55dfb3c00deb6d44914b6348e724ceccb8`) | User-run diagnostic identifies a version-specific entry-versus-exit row/position labeling error in the testbed profile exporter and requests separate parameter panels, magnet-family colours, and explicit bare tune/chromaticity labels; the shared skill requires verified boundary mapping and plot presentation but does not validate the testbed fix or establish reviewed tolerances or physics acceptance |
| [Xsuite ISIS testbed](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/060b3b5aee52e11fdc40bb1ab98bea9d20a1ba9d/steps/benchmark-code-against-isis-rcs-optics/feedback/0012-attempt-020-assessment-and-twiss-boundary-fix.md) (SHA-256 `560eacaefcfa3c2959697f5061948ab1c9d120d209e7cea75fd2ce39a91e31ea`) | User-run attempt-020 verified the row-boundary mapping in eleven cases and reported profile residuals; technical completion is distinct from tolerance and physics acceptance |
| [Xsuite ISIS testbed](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/060b3b5aee52e11fdc40bb1ab98bea9d20a1ba9d/steps/benchmark-code-against-isis-rcs-optics/feedback/0013-attempt-020-user-approved-optics-tolerances.md) (SHA-256 `a01d3b9581aa270f2a77fec168faa51cd1e4c8bbef51544acb80e16ba5e8da90`) | User-approved provisional screening tolerances and attempt-020 per-observable differences; these criteria are specific to that campaign and do not alone establish physics acceptance |
| [Xsuite ISIS testbed, attempt-022 feedback 0014](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/07361be33d8dd55e27f974a6b791e883e2bed0e4/steps/benchmark-code-against-isis-rcs-optics/feedback/0014-attempt-022-misalignment-import-investigation.md) (SHA-256 `843e0b776a53c96b58fe315d5364c989eb2bd609e04e40396b896804ca1aaf9b`) | User-run attempt-022 and bounded diagnostic show that component application and source-table readback do not alone prove transform-semantic equivalence; inspect source operation order/frame and target API mapping, test components in isolated states, and keep diagnostic remaps separate from benchmark configuration; campaign and physics review remain pending |
| [Xsuite ISIS testbed, attempt-023 feedback 0015](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/0bb80a925a2055507c6d53bf53451e6e423c37ec/steps/benchmark-code-against-isis-rcs-optics/feedback/0015-attempt-023-corrector-sweep-and-response-tolerances.md) (SHA-256 `46189befbcc12125fdbf2a05326ffb944c7d2c7a0c78616069c9b5450ca58014`) | Attempt-023 had only two positive corrector cases and response floors but no reviewed cross-code response tolerances; feedback proposes conditional full element-by-polarity coverage, a separate field-error control for staged localization, and per-observable response verdicts; campaign and physics review remain pending |
| [Xsuite ISIS testbed, attempt-025 feedback 0016](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/2ae7cb9201072e61ce105d0b303e2a2d36da6a94/steps/benchmark-code-against-isis-rcs-optics/feedback/0016-attempt-025-corrector-response-and-normalization-review.md) (SHA-256 `b8af712847309c0b9c84df228230dccb6cf23ba0915ce4ab41528a2af853bc82`) | Identifies MAD-X dispersion response subtraction before beta normalization and separates campaign-specific corrector orbit screening from optics-profile, tune, and chromaticity response criteria; establishes no physics acceptance |
| [Xsuite ISIS testbed, vertical chromaticity investigation (2026-10-27)](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test/-/blob/2ae7cb9201072e61ce105d0b303e2a2d36da6a94/steps/benchmark-code-against-isis-rcs-optics/diagnostics/vertical-chromaticity-investigation-2026-10-27.md) (SHA-256 `90e95181ac055d50c747f6b61520bd14971fcb6f5c16dbc98d3cfd669832ff6f`) | Pinned-version controlled Xsuite bend-edge variants make the vertical chromaticity slope approach the MAD-X result while retaining close nominal tunes; motivates a bounded diagnostic only, not a production setting or universal equivalence claim |
| [Xsuite ISIS testbed](https://gitlab.stfc.ac.uk/accelerator_simulation_framework/agentic_xsuite_test), `steps/benchmark-code-against-isis-rcs-optics/feedback/0017-attempt-026-plot-readability-and-bend-edge-follow-up.md` (SHA-256 `8ab3cbad05f8ef9570f6e7419fa587b52a7ab40a24bd92f78c27444a3b1ac809`; untracked at testbed HEAD `2ae7cb9201072e61ce105d0b303e2a2d36da6a94`) | Attempt-026 kept importer-default bend settings in its main cases; `dipole-only` and `full` were diagnostic-only. Requires the effective model to be explicit on every fresh main-case line, visual readability at normal size, artifact paths to match real non-empty directories, and capability explanations to match tolerance scope |

See `SOURCE_MATERIAL_HIERARCHY.md` for the distinction between generic
workflow, code knowledge, ISIS-machine facts, benchmark definitions, and
campaign-local evidence.
