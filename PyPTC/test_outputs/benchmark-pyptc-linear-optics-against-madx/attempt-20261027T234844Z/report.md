# PyPTC/MAD-X linear-optics attempt attempt-20261027T234844Z

**Outcome:** `incomplete-chromaticity-and-plot-review`. **Run class:** `agent-diagnostic`.

## Accepted basis and recipe

This run uses the user-accepted admission snapshot `attempt-20261027T194128Z`. Its accepted scope is snapshot admission only. The exact accepted PyPTC shared library and MAD-X 5.02.00 binary were reused by digest. The effective recipe uses the five pinned inputs in admission order, the 2023 strength overlay, `synchrotron`, `a1=b1=0`, all trim variables zero, and the accepted flat file without resplitting.

## Sampling and profile comparison

MAD-X returned 586 named TWISS rows; PyPTC returned 804 orbit-node Twiss rows and 804 printer groups. The mapping status is `verified` with 586 matched element exits at a position tolerance of 1e-09 m. Mapping method and every row identity are retained in `boundary_map.csv`.

Reference dispersion columns were multiplied by this run's beta0=0.36713319993, derived from the MAD-X TWISS GAMMA header. 14 profile residual summaries are retained. All remain `pending-tolerance`; no agreement or physics claim is made.

## Chromaticity, tracking, and limitations

MAD-X 5.02.00 reports `DQ1/DQ2` as `dQ/dDELTAP`, equivalent to `dQ/d(delta_p)` with factor 1. The PyPTC native values are retained, but the public wrapper does not establish their derivative coordinate, so the cross-code chromaticity comparison is `blocked`: {'x': {'reference_native': -4.745390843, 'reference_definition': 'MAD-X 5.02.00 dQ/dDELTAP', 'target_native': -4.745307640951764, 'target_definition': 'PTC lattice_GET_CHROM coordinate not established by the public PyPTC API', 'converted_dQ_d_delta_p': None, 'signed_difference': 8.320204823597521e-05, 'classification': 'blocked', 'reason': 'the target native derivative coordinate and tune estimator are undocumented here; converting or equating it to dQ/d(delta_p) would be an unsupported inference', 'tolerance': None}, 'y': {'reference_native': -4.806168146, 'reference_definition': 'MAD-X 5.02.00 dQ/dDELTAP', 'target_native': -4.806147200304224, 'target_definition': 'PTC lattice_GET_CHROM coordinate not established by the public PyPTC API', 'converted_dQ_d_delta_p': None, 'signed_difference': 2.0945695776042328e-05, 'classification': 'blocked', 'reason': 'the target native derivative coordinate and tune estimator are undocumented here; converting or equating it to dQ/d(delta_p) would be an unsupported inference', 'tolerance': None}}.

Bounded tracking status is `complete`. Requested mode: `both`; the primary route is thick MAD-X `PTC_TRACK` against the PyPTC thick-lattice workflow. Both use the PTC tracking engine, so this is not an independent tracking-engine validation. The optional thin route is reference-only and separately classified because the ten-slice `MAKETHIN` diagnostic is unvalidated and no matching PyPTC thin control is established. Reference: `complete`; target: `complete`. The plan uses 64 turns from {'x_m': 0.001, 'xp_rad': 0.0, 'y_m': 0.001, 'yp_rad': 0.0, 'z_m': 0.0, 'dE_gev': 0.0}; see `tracking_summary.json` for complete counts and the reason if blocked. No target-only or partial record is presented as a cross-code comparison. No perturbation, nonlinear, long-term, collective-effects, clean-checkout admission, or production claim is made.

MAD-X and PyPTC runtime warnings are retained in `reference/madx.log` and `target/pyptc_runtime.log`. They are observations, not silently discarded or interpreted as resolved.

## Evidence files

- `boundary_map.csv` and `profile_mapping.json` — identity and position evidence.
- `aligned_profiles.csv` and `profile_residual_metrics.csv` — data and signed residual summaries, when mapping is verified.
- `scalar_comparisons.csv` and `capability_matrix.json` — scalar results and scope.
- `case_nominal/nominal_optics_composite.png` and `plot_manifest.json` — one nominal case composite when mapping is verified.
- `manifest.json`, `result.json`, and `harness-tests.log` — provenance, canonical status, and harness checks.
