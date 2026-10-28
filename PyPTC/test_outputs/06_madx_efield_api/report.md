# PyPTC MAD-X EFIELD API side-by-side example

This is a reproducible test/example, not a tolerance-based acceptance.
The MAD-X path uses `READMYTABLE` and `SETERR`; PyPTC uses the public `apply_madx_error_table` API.
Each engine reads the same table and uses a fresh lattice state.

- MAD-X: `/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/workflows/madx/bin/madx-linux64_v5_02_00` (SHA-256 `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`)
- PyPTC library SHA-256: `d999479587a829469c84e175b9bc4b85b272eb7d58a9aa5a7994cce63e13ac2c`
- Source survey table SHA-256: `c864ea0ac6bab8159d5763e9134d8788e6ad006352ae8034a37859bfa95351b6`
- Generated PTC flat file SHA-256: `052380ab09cd8f68ff9563eefe00ee83fba4995a25506f5d7c78da7c8b592eb9`
- Unsupported nonzero EFIELD guard: `rejected-as-designed` (`MAD-X EFIELD contains unsupported nonzero fields: SP0_QF:MREX=0.0001`)

## Cases

### `isis_apr_2026_survey`

- Mapped exits: 586
- Wrapped tune residuals: Qx `8.33794e-06`, Qy `-1.14739e-06`
- Plot: `cases/isis_apr_2026_survey/madx_pyptc_efield_comparison.png`
- Aligned values: `cases/isis_apr_2026_survey/aligned_profiles.csv`

### `synthetic_normal_skew`

- Mapped exits: 586
- Wrapped tune residuals: Qx `1.22769e-05`, Qy `-8.91715e-07`
- Plot: `cases/synthetic_normal_skew/madx_pyptc_efield_comparison.png`
- Aligned values: `cases/synthetic_normal_skew/aligned_profiles.csv`

## Scope and limits

The API applies DX/DY/DS/DPHI/DTHETA/DPSI and integrated magnetic K0L..K20L/K0SL..K20SL.
Nonzero EFIELD fields outside that set fail before any lattice mutation. The example does not claim support for monitor readout/scaling, RF multipole phases, or RF frequency/harmonic/lag errors.
The checked-in survey table has zero multipole columns; the synthetic case exercises normal and skew field errors.
