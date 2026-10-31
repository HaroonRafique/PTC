# Chromaticity coordinate reassessment: MAD-X, PTC state, and PyPTC

**Status:** The earlier PyPTC chromaticity conversion is withdrawn. For the
API-5 build and MAD-X 5.02.00 used in this campaign, the evidence supports
comparing `PTC.chromaticities()` directly with MAD-X `SUMM.DQ1/DQ2`; neither
side receives a `beta0` factor. A separate PyPTC tracking-input conversion
problem is identified below and remains to be fixed and regression-checked.

**Date:** 2026-10-31  
**Evidence class:** source audit, manual review, retained MAD-X finite-difference
run, and new bounded PyPTC state-controlled tracking diagnostic. This is not
physics acceptance.

## Executive finding

The attempt-019/0002 report made a mistaken inference: it treated the API
chromaticity and the default-state particle-tracking coordinate as if they
used the same fifth-coordinate definition. They do not. PTC supports distinct
`DELTA` and `PT` states. `lattice_GET_CHROM` explicitly constructs the
`NOCAVITY + DELTA + ONLY_4D` state, so its extracted normal-form coefficient is
with respect to momentum deviation `delta = (p-p0)/p0`. The PyPTC Python
tracking helper, meanwhile, writes `dE/p0c` into the fifth coordinate while
the normal ORBIT lattice is in PTC's default state, whose fifth coordinate is
momentum deviation. That helper therefore supplies approximately `beta0 *
delta` where the default state expects `delta`.

The new state-controlled scan reproduces this factor directly. Its default-
state control, with the old `dE/p0c` input, measures tune slopes smaller by
approximately `beta0`. When the same scan selects the `NOCAVITY + DELTA +
ONLY_4D` state used by `lattice_GET_CHROM` and supplies `delta` in the fifth
coordinate, the vertical slope agrees with the API value. This identifies the
earlier scan's coordinate mismatch; it does not validate the default-state
energy-to-coordinate conversion.

MAD-X 5.02.00's `DQ1/DQ2` are also per `DELTAP` in the actual benchmark run,
confirmed by the retained matched `TWISS, DELTAP` tune scan and the MAD-X
release history. Therefore the raw PyPTC API values and MAD-X headers use the
same derivative coordinate. Their close nominal agreement is expected, not a
coincidence requiring a `beta0` conversion. Across attempt 022's 38 cases,
native-coordinate horizontal chromaticity differences all meet their
provisional screen; 14 vertical cases do not.

## Step-by-step definitions and implementation path

### 1. Define the two longitudinal coordinates

Write

```text
delta = DELTAP = (p - p0) / p0
PT = (E - E0) / (p0 c)
```

At the reference particle, `dPT/d(delta) = beta0`, so for small offsets
`PT ~= beta0 * delta`. These are both dimensionless but are not the same
coordinate. A derivative with respect to one must not be assigned to the
other without checking the selected PTC state and the version-specific MAD-X
output convention.

### 2. What the MAD-X manual says about dispersion

The MAD-X User's Guide, in its conventions/linear-optics definitions, says
that MAD-X uses `PT` in place of `DELTAP` for the longitudinal variable and
defines `DX = dx/dPT` (similarly `DY`, `DPX`, `DPY`). Thus the physical-momentum
derivative is

```text
dx/d(delta) = beta0 * DX
```

This matches the observed workflow: multiply MAD-X dispersion by `beta0` when
comparing with the PyPTC node dispersion generated in `DELTA` state. The
dispersion rule alone does not establish the convention of every scalar
summary field, especially a `TWISS, CHROM` result whose implementation changed
between MAD-X releases.

### 3. What the MAD-X manual and version history say about `DQ`

The User's Guide describes `SUMM.DQ1/DQ2` generically as chromatic derivatives
with respect to `PT`, and describes `CHROM` as calculating chromaticity from
tune differences at the requested `DELTAP` and `DELTAP + 1e-6`. These
statements are not sufficiently version-specific to decide how the historical
5.02.00 binary writes its `DQ` values.

The official MAD-X change record says that the `TWISS, CHROM` output changed
in release 5.06.00 to report `DQ/DPT`; before that change it reported
`DQ/DELTAP`. The exact campaign executable is MAD-X 5.02.00, before this
change. The direct test retained from investigation 0002 is consistent with
that version history: for the exact recipe, symmetric `TWISS, DELTAP` scans
gave slopes of `-4.7454000` / `-4.7454100` horizontally and `-4.8061800` /
`-4.8061750` vertically, while the attempt-019 `DQ` headers were
`-4.745390843` and `-4.806168146`. Treat these exact 5.02.00 values as
`dQ/dDELTAP`; do not apply `beta0` to them.

### 4. What the PTC manual says about the fifth coordinate

Forest and Schmidt's 2010 *PTC User's Reference Manual*, Chapter 2 (state
definition and default state), says that states control tracking and TPSA
calculations. The default state has `TIME=false`; PTC uses momentum and path
length. Chapter 11, equation 11.4, explicitly distinguishes the two
coasting-beam normal forms:

```text
z5 = delta = (p-p0)/p0, z6 = L
or
z5 = PT = (E-E0)/(p0 c), z6 = cT  (TIME state)
```

The same chapter says chromatic tune terms are derivatives of the normal-form
Hamiltonian with respect to `x5`. Therefore the active PTC state is necessary
to identify the derivative coordinate. The manual does not permit inferring
`PT` merely from the symbol `x5` or from the fact that its value is
dimensionless.

### 5. PyPTC Python-to-Fortran route for `chromaticities()`

1. [`PTC.chromaticities()`](../../../pyptc/core.py) allocates two scalar
   outputs and calls `pyptc_get_chromaticities`.
2. [`pyptc_get_chromaticities`](../../../fortran/pyptc_api.f90) calls
   `lattice_GET_CHROM(my_ering, my_estate, chrom)` and copies the two returned
   values without applying a scale factor.
3. [`lattice_GET_CHROM`](../../../../source/So_fitting.f90) constructs
   `STATE = my_state + NOCAVITY0 + DELTA0 + ONLY_4D0 - RADIATION0`, then calls
   `INIT(STATE,2,0,BERZ)` before finding the orbit, tracking the map, and
   forming the normal form.
4. The function returns
   `NORM%DHDJ%V(1:2).SUB.'00001'`. There is no `beta0` multiplication or
   division in that function or its PyPTC ABI wrapper.
5. In the source's [`INTERNAL_STATE` and `S_init`](../../../../source/a_def_element_fibre_layout.inc)
   / [`Se_status.f90`](../../../../source/Se_status.f90) definitions, the
   `DELTA` flag selects a one-parameter momentum-deviation variable in the
   no-cavity, 4D state. This agrees with the PTC manual's `z5=delta` choice.

The API evidence therefore supports `PTC.chromaticities() = dQ/d(delta)` for
this call path. The earlier report's `dQ/dPT` label was based on matching the
API result to a tracking slope measured in a different PTC state; that was not
a like-for-like coordinate test.

### 6. The separate PyPTC particle-tracking conversion

[`particle_diagnostics`](../../../pyptc/core.py) currently converts a Python
`dE` input to `dE/p0c` and writes that number into PTC coordinate slot 5.
[`track_particle_ptc_with_loss`](../../../pyptc/core.py) then passes the six
values through the Fortran ABI to `PUT_RAY` and `TRACK_ONE_NODE` without a
longitudinal coordinate conversion. The ORBIT lattice is created in PTC's
default state (`DEFAULT0`); PTC manual Chapter 2 and equation 11.4 identify
that state's fifth coordinate as momentum deviation, not `PT`.

Thus for the default-state tracking route, a Python energy deviation should be
converted to momentum deviation, for example exactly as

```text
delta = sqrt((E0 + dE)^2 - m^2 c^4) / p0 - 1
```

with units handled consistently. Near the reference state this is
`delta ~= dE/(beta0*p0c)`. The current `dE/p0c` conversion is smaller by
approximately `beta0`. A full API fix must also review inverse conversion of
the returned fifth coordinate and the longitudinal sixth-coordinate
convention; this investigation does not silently change those public tracking
methods.

### 7. Reproduction that separated the two PTC states

`investigations/chromaticity_state_scan.py` ran in two fresh Python processes,
each with the accepted flat file and the same API-5 library, using symmetric
`delta` labels `±5e-5` and `±1e-4`, 8,192 turns, and a 1 mm transverse probe.

| Tracking setup | Fifth slot actually supplied | Measured central slope per labelled `delta` | API value | Interpretation |
|---|---:|---:|---:|---|
| Default state; old energy conversion | `PT ~= beta0*delta` but default state expects `delta` | X `-1.72501` / `-1.72507`; Y `-1.76435` / `-1.76615` | X `-4.74531`; Y `-4.80615` | Confirms the old control was underscaled by about `beta0`; it does not identify the API derivative coordinate. |
| `NOCAVITY + DELTA + ONLY_4D`; direct momentum input | `delta` | X `-4.76700` / `-4.77239`; Y `-4.80620` / `-4.80640` | X `-4.74531`; Y `-4.80615` | Same state and coordinate as `lattice_GET_CHROM`; vertical agrees closely, horizontal scan is less precise but consistent at the scale relevant here. |

The first row reproduces the factor that prompted the earlier wrong inference.
The key mistake was calling its fifth-slot input `PT` without first checking
the active state. The second row is the state-matched test.

## Reassessment of attempt 022 chromaticity results

The nominal PyPTC API values are `-4.745307641` and `-4.806147200`; MAD-X
5.02.00's `DQ1/DQ2` values are `-4.745390843` and `-4.806168146`. On the
common `dQ/d(delta)` coordinate, PyPTC-minus-MAD-X is `+8.32048e-5` horizontal
and `+2.09457e-5` vertical. Both are within the provisional limits `9e-4` and
`3.5e-4`.

Re-reading all 38 attempt-022 `scalar_comparisons.csv` files without the
erroneous `beta0` multiplication gives:

| Plane | Worst absolute difference | Provisional limit | Worst case | Cases within |
|---|---:|---:|---|---:|
| Horizontal | `7.78212e-4` | `9e-4` | `corrector_sp5_r5hd1_plus_1mrad` | 38/38 |
| Vertical | `7.36948e-4` | `3.5e-4` | `corrector_sp2_r2vd1_minus_1mrad` | 24/38 |

Accordingly, the attempt-022 statement that both converted chromaticities were
out of tolerance in every case is withdrawn. This correction changes the
scalar screen from 152/190 out of tolerance to 90/190: all 38 horizontal
chromaticities pass, 24 vertical chromaticities pass, and 14 vertical cases
remain out. The tune, circumference, profile, tracking, plot-review, and other
attempt dispositions are not changed by this coordinate correction. Attempt
022 remains unaccepted and requires human review.

## Findings, corrections, and remaining work

1. **Confirmed:** MAD-X dispersion in the pinned workflow is per `PT`; compare
   with momentum-normalized PyPTC dispersion using `beta0 * MAD-X DX`.
2. **Confirmed for the tested MAD-X release:** MAD-X 5.02.00 `TWISS, CHROM`
   `DQ1/DQ2` are per `DELTAP`; compare directly with the PyPTC chromaticity
   getter. The MAD-X convention change in 5.06.00 is why the generic manual
   definition cannot be applied to 5.02.00 without checking the version.
3. **Confirmed from the PyPTC call path and state-matched diagnostic:**
   `lattice_GET_CHROM` explicitly selects `DELTA`; no `beta0` factor belongs
   on `PTC.chromaticities()` for this API call.
4. **Identified implementation/documentation issue:** the user-facing Python
   particle diagnostic maps `dE` to `dE/p0c` while the ORBIT default state
   expects `delta`. Correct energy-to-momentum conversion and its inverse
   should be implemented in the PyPTC tracking API, then exercised by a
   regression test and reviewed with existing examples. This follow-on change
   is not included here.
5. The benchmark runner and report templates still multiply the PyPTC API
   chromaticity by `beta0`. They need a PyPTC-specific correction before the
   next benchmark attempt. Keep MAD-X conversion logic version-aware.
6. The precise horizontal state-matched tracking slope remains less stable
   than the vertical slope; this does not alter the direct API/manual/MAD-X
   coordinate finding, but it limits claims based on the horizontal tracking
   finite difference.

The original investigation 0002 and attempt bundles remain unchanged as
historical evidence. This report supersedes their interpretation of the
PyPTC chromaticity API and documents the flawed inference. See supplemental
attempt-022 feedback 0022 for the ledger-facing review disposition.

## Reproducibility and provenance

- Accepted flat file SHA-256:
  `32f96fb53f37cdefcf3c540431a4da6fab9b06f4bf3687b0700a4af0fe6a9d3a`.
- PyPTC API-5 `libpyptc.so` SHA-256:
  `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`.
- `pyptc/core.py` SHA-256:
  `37a246d66da327f67e56b1069495c593739b5a4d69386cdb533193bd81e57ad3`.
- `fortran/pyptc_api.f90` SHA-256:
  `d85f3526b04c6c9e6e697887c0da2ab48e4ee822737414cb2ec0fcfb4ca7fa91`.
- `../source/So_fitting.f90` SHA-256:
  `b55cbb16f40cad4d321a898fa5ff6c454389a3c566de8638e59bbece34696d7c`.
- PTC manual PDF SHA-256:
  `02c5530578259d31531094c179d35cfa1eff8cbbddc9b85035a454ba3fdd2453`.
- State diagnostic script SHA-256:
  `8a0c27d479110f0ea2c1509e3de8171a7c1d166544c7ff231556d9884050ec1f`.
- Default-state control JSON SHA-256:
  `72addb3eadf3c14707a429a851bd7e1def82c77698798fd996665b037204fbb6`.
- API-state JSON SHA-256:
  `b0abf355a3bc2be13b81d8000e187c17dd9ab13a95ea82c898791544813d5e4a`.
- API-state PTC command SHA-256:
  `143cc843a682cdb3f954bd614394f8e841d18b2bc20e6f59f44c5ce59e8b9410`.
- MAD-X executable SHA-256:
  `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
- Earlier MAD-X scan JSON SHA-256:
  `1486ff190a7c2b2f6e86fbea47c6a71d8e2db40f10a52edace9c7a5e698d8fd0`.

The new scripts and data are in `investigations/chromaticity_state_scan.py`
and `test_outputs/benchmark-chromaticity-coordinate-units/`.

## References and publication-plan link

1. É. Forest and F. Schmidt, *PTC User's Reference Manual*, CERN BE
   Department, 2010, Chapter 2 (states/default state) and Chapter 11,
   equation 11.4 (coasting-beam normal form coordinates). Local copy:
   `pyptc_documentation/references/pdfs/forest_schmidt_ptc_users_reference_manual_2010.pdf`.
   URL: <https://madx.web.cern.ch/doc/PTC_reference_manual.pdf>.
2. CERN, *MAD-X User's Guide*, version 5.02.08, conventions and TWISS module
   (general `PT`, `DELTAP`, dispersion, and `SUMM.DQ` definitions). URL:
   <https://madx.web.cern.ch/madx/releases/5.02.08/madxuguide.pdf>.
3. Methodical Accelerator Design, *MAD-X Changes*, release 5.06.00 entry,
   which records that `TWISS, CHROM` `DQ` changed from `DELTAP` to `PT`:
   <https://github.com/MethodicalAcceleratorDesign/MAD-X/blob/master/Changes.md#L320-L344>.
4. Methodical Accelerator Design, current `mad_twiss.c`, showing the later
   `CHROM` denominator `beta0 * DQ_DELTAP`:
   <https://github.com/MethodicalAcceleratorDesign/MAD-X/blob/master/src/mad_twiss.c#L3701-L3781>.

This investigation supports the
[evidence-gated agents publication plan](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md): it records the initial claim, the contradictory manual/version evidence, exact code paths, controlled comparison, hashes, and corrected claim limits. It authorizes no release or scientific acceptance.
