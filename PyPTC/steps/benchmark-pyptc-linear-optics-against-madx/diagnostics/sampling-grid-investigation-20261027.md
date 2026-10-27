# PyPTC/MAD-X sampling-grid discrepancy investigation

**Date:** 2026-10-27
**Campaign:** PyPTC linear-optics benchmark against MAD-X, iteration 0001
**Evidence run:** user-run `attempt-20261027T145757Z`
**Status:** diagnostic investigation; no code or split-policy change made

## Questions and finding

The two calculations use the same hash-identified ISIS RCS source inputs and
the same admitted machine-state recipe. The reporting points differ because
the two programs report on different grids:

- MAD-X TWISS reports rows at sequence element locations, normally at the
  element exit, and includes zero-length sequence entries and coincident
  locations.
- PyPTC's public all-node API reports the PTC orbit-node grid. The retained
  source-inspection record says each value is queried after tracking that
  orbit node, with that node's length representing the preceding interval.
  These orbit nodes can combine several short MAD-X elements or lie inside a
  longer MAD-X element.

This is therefore a sampling-method/API exposure discrepancy. It is **not**
just a single global “PTC start versus MAD-X end” offset, and the evidence does
not show that either program used a different lattice file. Matching counts
are not required for a valid comparison, but values must be aligned at the
same physical locations with the correct element occurrence and entrance or
exit side. The current PyPTC API does not expose enough location identity or
arbitrary-position sampling to establish that full map from Python alone.

## Input identity and machine state

MAD-X reread the five accepted snapshot inputs, in the admission order:
`ISIS.injected_beam`, `ISIS.elements`, `ISIS.strength`, `2023.strength`, and
`ISIS.sequence`. Their SHA-256 values are recorded in the user-run manifest
and match the copied accepted admission snapshot. PyPTC loaded the accepted
admission flat file, SHA-256
`32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a`; that
same hash is recorded in the accepted admission result and the user-run
manifest. The measurement recipe adds TWISS/CHROM columns without changing the
machine-state recipe. Both runs record `a1=b1=kqtd=kqtf=0` and the individual
trim readbacks as zero.

| Input | SHA-256 |
| --- | --- |
| `ISIS.injected_beam` | `2759a6ef97d7799412ba293c8fc788ad34c356ca3b7098acd2a106f7142c92df` |
| `ISIS.elements` | `33ec2aedddde548b4f19f9fe9dd26d48ce4445f36c2c118dfa82d239dda8dffa` |
| `ISIS.strength` | `912286281994f76e09561b42b32335b65dbc50d6d438f2caa3c8a9f7018b04cf` |
| `2023.strength` | `a66ca836e9bbdc6560b2196dbe02c12a3c1781bff0b74589d2995d7689f430ed` |
| `ISIS.sequence` | `3cfc1fbb8c39e0d455a0518c4c37abd28058e7e5937231e8bb7cc9462adc9e1d` |
| PyPTC flat file | `32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a` |
| MAD-X 5.02.00 executable | `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04` |
| PyPTC shared library | `b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76` |

Thus the inputs are different *representations*: MAD-X consumes the five
source files, while PyPTC consumes the PTC flat file generated from that
accepted snapshot. The provenance ties them to one declared lattice setup.
The grid discrepancy is not evidence of a lattice-input mismatch.

## What the retained data shows

| Record | Count | Interpretation |
| --- | ---: | --- |
| MAD-X TWISS rows | 586 | Same names in the same order as all 586 accepted flat-file fibre records; `S` matches their cumulative end positions within `2.85e-13 m` |
| Distinct MAD-X `s` values | 563 | 23 extra rows share an already represented position |
| Accepted PTC flat-file fibres | 586 | Includes 562 positive-length and 24 zero-length fibre records |
| PyPTC orbit-node rows | 375 | Public `ORBIT_N_NODE` records; node lengths sum to 163.36282 m |
| PyPTC positions at a unique exact MAD-X `s` | 153/375 | Exact-position coincidences with a single MAD-X row |
| PyPTC positions coincident with any MAD-X row | 156/375 | Three positions coincide with duplicated MAD-X `s` rows and are ambiguous without identity/side information |
| PyPTC positions strictly inside a flat-file fibre | 219/375 | Demonstrates internal orbit-node sampling within MAD-X element intervals |

The 586-to-375 difference is not explained just by removing the 24
zero-length fibres. The first PyPTC orbit interval, `0.0000–0.3900 m`, spans
three positive-length flat-file elements: `SP0_DIPFR8`, `SP0_DIPFR9`, and
`SP0_DIPFR10`. The next interval, `0.3900–0.7305 m`, spans
`DRIFT_0`, `SP0_R0HD1`, `DRIFT_1`, and `SP0_R0HM1`. At the same time, PTC
introduces orbit-node points within longer MAD-X elements. The orbit-node grid
therefore both coalesces some element boundaries and subdivides some element
bodies.

## Is it start, middle, or end sampling?

The `sampling_source_evidence` stored in the user-run manifest records an
inspection of the pinned PyPTC source revision
`324c1a6e0389137c4f93658621089f9e01159827`: `ORBIT_TRACK_NODE` is called
before the Twiss values are stored, and the node length is the interval just
traversed. The recorded source-file hashes are included in the manifest. The
same bundle's local Fortran wrapper loops over `ORBIT_N_NODE` and invokes
`orbit_track_node`; Python `all_node_twiss_orbit()` obtains one row per
`machine_summary()['n_nodes']` and calculates `s` as the cumulative node
length. The Python row does not include a source MAD-X element name or
occurrence.

MAD-X rows in the retained TFS carry element names and cumulative `S`; for
this sequence those values identify each element's reported exit. Direct
examples show that PyPTC can report between such exits:

| PyPTC node exit `s` | Containing MAD-X element interval | MAD-X reported exit `s` | What it demonstrates |
| ---: | --- | ---: | --- |
| 1.22600 m | `DRIFT_2`, 0.73050–2.21700 m | 2.21700 m | PyPTC subdivides a long drift |
| 3.41000 m | `SP0_QD`, 3.15040–3.66960 m | 3.66960 m | PyPTC samples inside a thick quadrupole |
| 8.46415 m | `DRIFT_8`, 5.97100–10.95730 m | 10.95730 m | PyPTC has repeated internal samples through a long drift |
| 13.64628 m | `SP1_DIP`, 12.17628–16.09628 m | 16.09628 m | PyPTC samples inside a thick dipole |

The `LMAX=0.5 m`, `FUZZYLMAX=1.1` resplitting recipe and the measured
PyPTC maximum node gap of `0.5144 m` are consistent with the approximately
half-metre internal orbit-node intervals. This investigation does not claim
to have reconstructed every low-level PTC rule that maps 586 flat-file fibres
to 375 orbit nodes: the core PTC layout implementation is not included in this
repository. The manifest preserves the earlier pinned-source inspection and
its file hashes, while the checked-in wrapper confirms that only the already
constructed orbit-node list is exposed.

The largest nearest-position residual, `2.49315 m`, occurs for PyPTC
`s=8.46415 m`, inside `DRIFT_8`; the nearest MAD-X boundary is more than two
metres away (the left and right boundaries are tied at the displayed
precision). That is why “pair each value with the nearest row” is not a valid
substitute for a boundary map.

## Why the row counts differ

MAD-X's 586 TWISS rows correspond one-for-one, by name and order, to the 586
records in the accepted flat file; their `S` values equal the cumulative
fibre-end positions to floating-point precision. They include zero-length
entries and can repeat an `s` value. The
PyPTC C/Fortran wrapper reports 375 records from `ORBIT_N_NODE`, not one record
for every parsed fibre. Its recorded node lengths tile the full circumference.
Examples above demonstrate that some orbit-node intervals span several
short elements, while other long elements are traversed through several
internal orbit-node intervals. The grids answer different reporting
questions, so equal row counts should not be expected.

The wrapper code in this repository exposes `node_twiss_orbit(index)`,
`all_node_twiss_orbit()`, and `node_phase_advances()` over the existing orbit
nodes. Its flat-file parser can list fibre names, indices, and lengths, but no
public method returns Twiss/orbit data at an arbitrary `s` or selected
element/occurrence boundary. The precise grouping/splitting implementation
belongs to the PTC core outside this checkout and cannot be inferred solely
from the Python API.

For reproducibility, the grid checks use `read_flatfile_fibres()` to recover
the ordered flat-file names and lengths, cumulative-sum those lengths, parse
the `NAME`/`S` fields from the captured MAD-X TFS, and compare PyPTC's retained
`s_exit_m` values with the preceding and following cumulative fibre
boundaries. The source files and outputs are linked below; no rerun or lattice
mutation was needed for these counts.

## Can PyPTC be made to report at MAD-X locations?

**In principle, yes.** The report grid is a software choice. A future
implementation could expose Twiss/orbit sampling at selected PTC fibre or
sequence boundaries, with element name, occurrence, and entrance/exit side.
That would let the benchmark request the MAD-X element-exit locations from
PyPTC, provided the PTC internals can calculate and return those states
without changing the physical maps.

Other possible routes are:

1. **Use verified common boundaries.** Compare only positions where both
   outputs have an exact, unique, identity-verified match. This gives partial
   coverage here (153 candidates), not a complete profile benchmark.
2. **Add a PTC observation-point API.** Query at named fibre/occurrence
   boundaries and record which side of each edge is sampled. This best matches
   MAD-X's existing element-exit report without adding reference markers.
3. **Resample MAD-X to the PTC nodes.** For a PTC point inside a thick element,
   split that MAD-X element into physically equivalent pieces and place an
   observation point there, or compute a documented local transfer-map
   interpolation. Preserve integrated fields, edge/fringe behavior, and
   one-sided values at discontinuities, then validate against unsplit scalar
   optics and tracking. The prior marker-only attempt failed because a marker
   placed inside an unsplit thick element led MAD-X to a negative drift; that
   rejects that insertion method, not all possible resampling methods.

Changing `LMAX` alone is **not** a demonstrated solution. It would change the
orbit-node segmentation/density and may change runtime or numerical tracking
behavior; it would not by itself guarantee nodes at every MAD-X element exit
or provide element identities. Keep the existing `LMAX` contract unchanged
until a controlled comparison tests any split-policy change, as required by
[AGENTS.md](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/AGENTS.md:31).

## Conclusion and next investigation

The evidence supports this conclusion:

- Same hash-identified source lattice and accepted recipe: **confirmed**.
- Different reporting grids: **confirmed**.
- MAD-X element-exit rows versus PyPTC orbit-node-exit rows: **confirmed**,
  with PyPTC nodes both combining short element intervals and appearing inside
  long elements.
- A single global start/end offset: **ruled out**.
- Physics disagreement caused by the grid: **not established**; profile
  residuals have not been computed.
- Current PyPTC Python API can directly request arbitrary MAD-X locations:
  **no**.
- PyPTC can be changed to expose selected locations in principle:
  **yes, subject to PTC-core/API work and physics-preserving validation**.

The next useful work is a bounded design/prototype for one observation point
inside a thick element and one at a zero-length/edge boundary. It should
preserve the existing split-policy baseline, record element occurrence and
sampling side, and compare the added query with the current adjacent node
values. Do not call the present benchmark complete until all declared profile
families have a verified mapping, residuals, plot evidence, and reviewed
tolerances.

## Evidence and publication link

Primary run artefacts:

- [User-run report](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T145757Z/report.md)
- [MAD-X TWISS data](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T145757Z/madx/reference_twiss.tfs)
- [PyPTC all-node data](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T145757Z/pyptc/profile_raw.csv)
- [Mapping diagnostic](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T145757Z/mapping_diagnostic.csv)
- [Run manifest](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T145757Z/manifest.json)
- [PyPTC wrapper](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/fortran/pyptc_api.f90:94), [Python optics API](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/pyptc/core.py:838), and [flat-file metadata parser](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/pyptc/lattice.py:49).
- [Accepted flat-file resplitting recipe](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/steps/benchmark-pyptc-linear-optics-against-madx/admission_basis-accepted-attempt-20261027T082315Z/madx_work/PTC_Scripts/resplit.ptc)
- [Campaign feedback 0003](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/steps/benchmark-pyptc-linear-optics-against-madx/feedback/0003-user-run-review.md)

This is local PyPTC campaign evidence under Task 6's prospective longitudinal
record practice and Task 9's event-driven maintenance in the [evidence-gated
agents publication plan, Task 6](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md:865)
and [Task 9](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md:1185).
The investigation is not a controlled baseline-versus-skill evaluation,
technical benchmark completion, or physics acceptance. No publication
chronology `REP-####` is created because the benchmark skill reserves that
completion event for a technically complete comparison. Keep this report and
the raw data in this repository; no shared publication-repository files were
modified.
