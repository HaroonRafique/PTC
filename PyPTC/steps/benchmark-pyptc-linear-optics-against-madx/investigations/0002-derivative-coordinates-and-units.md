# PyPTC and MAD-X derivative coordinates and optics units

**Status:** resolved for the nominal API-5 build and MAD-X 5.02.00 combination
used by benchmark attempt 019. This is a coordinate-convention finding, not a
benchmark acceptance or tolerance decision.

**Date:** 2026-10-28  
**Evidence class:** bounded diagnostic investigation; attempt 019 remains
immutable and retains its original `blocked` chromaticity disposition.

## Finding

There is no single derivative-coordinate conversion that can safely be applied
to every optics quantity in either code.

* PyPTC `PTC.chromaticities()` returns the `lattice_GET_CHROM` derivative with
  respect to PTC's canonical `PT` coordinate. With the Python particle
  convention used here, `PT = ΔE/p0c`; near the reference momentum,
  `dPT/d(Δp/p0) = beta0`.
* MAD-X 5.02.00 `DQ1/DQ2` in the retained `TWISS, CHROM` output are derivatives
  with respect to `DELTAP = Δp/p0`. Direct MAD-X `TWISS, DELTAP=...` tune scans
  reproduce both header values.
* Therefore, compare chromaticity in a common coordinate using
  `PyPTC dQ/d(Δp/p0) = beta0 * PTC.chromaticities()` or equivalently
  `MAD-X dQ/dPT = DQ / beta0`. The attempt-019 near-equality of the two raw
  chromaticity numbers was accidental: they are derivatives with respect to
  different variables.
* MAD-X `DX/DY/DPX/DPY` in the TWISS table are derivatives with respect to
  `PT`, not `DELTAP`. A finite difference of the closed orbit at matched
  `DELTAP` confirms `ΔX/ΔDELTAP = beta0 * DX`. The existing profile adapter's
  `beta0 * MAD-X dispersion` conversion to the PyPTC output is therefore
  consistent with this check.

At attempt 019's reference state, `beta0 = 0.36713319993` from MAD-X and
`0.36713328270` from PyPTC. Applying the conversion gives:

| Plane | PyPTC native `dQ/dPT` | PyPTC converted `dQ/dDELTAP` | MAD-X `DQ` (`dQ/dDELTAP`) | PyPTC minus MAD-X, common coordinate |
|---|---:|---:|---:|---:|
| X | -4.745307641 | -1.742160372 | -4.745390843 | +3.003230471 |
| Y | -4.806147200 | -1.764496599 | -4.806168146 | +3.041671547 |

This leaves a large chromaticity discrepancy after coordinate normalization.
The unit conversion resolves the interpretation of the previously blocked
comparison; it does not establish agreement, explain the physical cause, or
establish an acceptance tolerance. Do not treat attempt 019's original scalar
residuals as valid cross-code residuals.

## Evidence and derivation

### PyPTC chromaticity coordinate

The Python API passes `PTC.chromaticities()` straight through the Fortran shim
to `lattice_GET_CHROM`. The reference implementation extracts
`NORM%DHDJ%V(1:2).SUB.'00001'`; the shim applies no scaling. The coordinate
was identified experimentally by comparing that API value with tune slopes
from `PTC.particle_diagnostics` at known momentum offsets. The Python wrapper
maps `dE` [GeV] to PTC's fifth coordinate as `PT = dE/p0c`.

The original 1 mm, 4096-turn scan gave tracking slopes per `PT` of -4.798 to
-4.703 (X) and -4.661 to -4.830 (Y), depending on central-difference step,
around native API values -4.7453 and -4.8061. A second 0.25 mm, 8192-turn scan
gave Y slopes per `PT` of -4.8090 and -4.8066, closely matching the native
value. The X tune-slope estimates in this lower-amplitude scan were less
stable (-4.5829 and -4.5294 per `PT`); they are retained as a precision limit,
not selected over the initial scan. Together, source-level coordinate mapping
and both scans identify the native derivative as per `PT`; the horizontal
finite-difference estimate is less precise than the vertical one.

For a proton at this reference state,

```text
PT = (sqrt((p0c * (1 + DELTAP))^2 + m^2) - sqrt(p0c^2 + m^2)) / p0c
dPT/dDELTAP at DELTAP=0 = beta0
```

The exact energy expression above was used to construct the PyPTC scan inputs.
The linear conversion is evaluated at the reference state; it is not a claim
that `PT = beta0 * DELTAP` at finite offsets.

### MAD-X chromaticity coordinate

MAD-X 5.02.00 was run from the exact nominal recipe and accepted snapshot used
by attempt 019, replacing the terminal nominal `TWISS, CHROM` with
`TWISS, DELTAP=<offset>`. At symmetric offsets `±5e-5`, measured slopes were
`dQx/dDELTAP = -4.7454000` and `dQy/dDELTAP = -4.8061800`; at `±1e-4` they
were -4.7454100 and -4.8061750. The attempt-019 `DQ1/DQ2` headers are
-4.745390843 and -4.806168146. This establishes the MAD-X header convention
for this version and recipe by direct measurement.

### MAD-X dispersion coordinate

For three named rows, a central `±5e-5` momentum scan gave the following
relationship between the measured closed-orbit derivative and the nominal
MAD-X `DX` value:

| Row | MAD-X `DX` [m per PT] | finite difference `dX/dDELTAP` [m] | ratio `(dX/dDELTAP)/DX` | `beta0 * DX` [m] |
|---|---:|---:|---:|---:|
| `SP0_DIPFR8` | 3.434980877 | 1.261095508 | 0.367133196 | 1.261095521 |
| `SP0_QF` | 8.810117656 | 3.234486694 | 0.367133201 | 3.234486687 |
| `SP0_QD` | 5.714340249 | 2.097924022 | 0.367133200 | 2.097924021 |

The ratio is `beta0` to the precision of the TFS output. Attempt 019's PyPTC
`etax` values agree with `beta0 * DX` at these rows. This is independent
support for the existing dispersion alignment conversion and demonstrates
that the MAD-X `DX` derivative convention differs from the MAD-X `DQ` header
convention in this run. `DPX/DPY` follow the same derivative-coordinate
conversion; their reported values are dimensionless because the differentiated
canonical momentum is dimensionless.

## Field-by-field units and interpretation

| Quantity | MAD-X 5.02.00 | PyPTC API/output used here | Comparison rule |
|---|---|---|---|
| `s` | m | cumulative node position, m | Compare only at matched physical sampling positions. |
| `x`, `y` | m | `orbitx`, `orbity`, m | Direct unit comparison; align sign, reference orbit, and sampling point. |
| `px`, `py` | canonical transverse momentum divided by reference momentum, dimensionless | `orbitpx`, `orbitpy` are PTC canonical transverse coordinates; dimensionless | Compare canonical momentum coordinates. The adapter's current `rad` label / “slope” title is approximate and should not be presented as the exact unit. In the paraxial, on-momentum limit they approximate slopes. |
| `betx`, `bety` | m | `betax`, `betay`, m | Direct unit comparison after position alignment. |
| `alfx`, `alfy` | dimensionless | `alphax`, `alphay`, dimensionless | Direct comparison after definition and sampling alignment. |
| `dx`, `dy` | MAD-X derivative per `PT`, units m | PyPTC `etax`, `etay` in this mapping correspond to derivative per `DELTAP`, units m | Convert MAD-X value by multiplying by reference `beta0`. |
| `dpx`, `dpy` | derivative of dimensionless canonical momentum per `PT`, dimensionless | PyPTC `etapx`, `etapy`, dimensionless | Convert MAD-X value by multiplying by reference `beta0`. |
| `mux`, `muy` | phase advance in turns (`2π` radians per turn) | `mux`, `muy` cumulative phase in turns | Direct comparison after matching start convention; phase may differ by an integer turn if wrapped. |
| tunes `Q1/Q2` | full tune, integer plus fractional part | `PTC.tunes()` returns fractional tune | Compare fractional tunes after documenting the selected integer tune branch. |
| `DQ1/DQ2` | measured here as `dQ/dDELTAP` | `PTC.chromaticities()` is `dQ/dPT` | Convert PTC by multiplying by reference `beta0` to `dQ/dDELTAP`; convert MAD-X by dividing by `beta0` to `dQ/dPT`. |
| circumference | m | sum of PyPTC node lengths, m | Direct scalar comparison. |

`PT` and `DELTAP` are both dimensionless, but are different physical
coordinates. In MAD-X's convention, `PT = ΔE/(p0 c)`; at the reference state,
`dPT/dDELTAP = beta0`. A label of simply “dimensionless” is therefore
insufficient for derivative quantities: the differentiated variable must be
recorded too.

## Provenance

* User-run benchmark: `runs/attempt-019/`; skill snapshot: iteration 0004.
  The run bundle and its `blocked` result were not altered by this diagnostic.
* PTC input basis: `admission_basis-accepted-attempt-20261027T194128Z`.
  Flat file SHA-256:
  `32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a`.
* PyPTC shared library SHA-256:
  `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`;
  `pyptc/core.py` SHA-256:
  `37a246d66da327f67e56b1069495c593739b5a4d69386cdb533193bd81e57ad3`;
  `fortran/pyptc_api.f90` SHA-256:
  `d85f3526b04c6c9e6e697887c0da2ab48e4ee822737414cb2ec0fcfb4ca7fa91`;
  `../source/So_fitting.f90` SHA-256:
  `b55cbb16f40cad4d321a898fa5ff6c454389a3c566de8638e59bbece34696d7c`.
* MAD-X executable: `workflows/madx/bin/madx-linux64_v5_02_00`, SHA-256
  `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
* Attempt-019 nominal MAD-X TFS SHA-256:
  `fab59256f136fa1101962ef66c4f5c0254274fc986f9a9f40886e06367749710`;
  PyPTC API summary SHA-256:
  `b9c4c74cc0ba8272473afdae36f976389fa7fca4705247725449011692422234`.
* Accepted input hashes are retained in
  `test_outputs/benchmark-chromaticity-coordinate-units/madx/madx_tune_scan.json`.
* Diagnostic outputs: `test_outputs/benchmark-chromaticity-coordinate-units/`.
  The initial PyPTC scan is `pyptc_coordinate_scan.json`; the tighter
  follow-up is `pyptc_coordinate_scan_lowamp-8192.json`; matched MAD-X offsets
  and tunes are in `madx/madx_tune_scan.json` and `madx/madx_off_momentum_tunes.csv`.
  Their SHA-256 values are respectively
  `5892899019a95befa337c607e6b9004364f2902d563d0a94ab3c637ce8ed8fa2`,
  `844751afa019ceac121fa8c9f49dc07bb1c42a3491d0cfb1a8eab9672655e29c`,
  `1486ff190a7c2b2f6e86fbea47c6a71d8e2db40f10a52edace9c7a5e698d8fd0`,
  and `31c5cae6a7da1271fe98ea978e7f9562e9835d51c2c906b56c40f32a7889efc7`.
* Reproduction scripts:
  `investigations/chromaticity_coordinate_scan.py` and
  `investigations/madx_momentum_tune_scan.py`; their SHA-256 values are
  `9ba0e274f86a34f8c9b176e6efff59f282b22f3cb82d519508ffbb56d66b9043` and
  `e001717d64906854101c96beaa26b812013b3809852cee770e2af5230f181ba1`.
* Source path: `pyptc/core.py` maps particle `dE` to PTC `PT=dE/p0c`;
  `fortran/pyptc_api.f90` passes chromaticity through to
  `../source/So_fitting.f90:lattice_GET_CHROM` without rescaling.
* MAD-X convention reference: CERN, “Canonical Variables in MAD-X”,
  [presentation](https://indico.cern.ch/event/285867/contributions/650484/attachments/530109/730983/MADX_Dec_11.pdf).

## Benchmark and campaign consequences

1. Update the next benchmark adapter to report explicit native and converted
   chromaticities, with `PT` or `DELTAP` in the field name and metadata. Keep
   the attempt-019 result unchanged.
2. Correct the transverse momentum profile unit labels from `rad` to
   dimensionless canonical momentum. If a slope is useful for plotting, derive
   and label it separately using the local momentum and off-momentum state.
3. Keep the established MAD-X dispersion conversion by reference `beta0` and
   add a regression check against the retained finite-difference evidence.
4. Before setting a chromaticity tolerance, investigate why the common
   coordinate values differ by about 3.0 in both planes. This report does not
   identify whether the cause is a map/model difference, an API convention
   beyond the identified coordinate, or another configuration difference.
5. Update the review ledger and a new immutable feedback record for the next
   attempt. This report is campaign evidence, not skill feedback or acceptance.

## Publication-plan cross-reference

This record supports the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md)
by retaining the claim, exact source/API and data identities, reproducible
inputs and commands, raw diagnostic products, observed limits, and a clear
separation between diagnosis and acceptance. It does not authorize publication
or change the disposition of attempt 019.
