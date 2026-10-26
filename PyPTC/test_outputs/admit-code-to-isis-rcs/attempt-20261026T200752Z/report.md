# PyPTC ISIS RCS admission attempt-20261026T200752Z

- Technical outcome: **admitted-snapshot**; external review disposition: **awaiting review**.
- Reference mode: `working-copy-snapshot`; snapshot source revision: `1bada6a2ab94edd426c52b7e97a5d335926e0646`.
- Shared skill: `85a897a47b55951552226221dcdbc3b83a8daf71`; SHA-256 `ca7457645d0fe9049e7b55c50fc3b035b4db771bdb5984c6ab662cbe3cfbf35f`.
- Snapshot source checkout revision/state: `823e6c08dfa79a182548b07706b3d46f0157137a`, dirty with 206 entries; full status: `reference_evidence/source_checkout_status.porcelain-v2.txt` (SHA-256 `0de8a247d46a968b69d6af0287ad281e892d7e77c524062711ab60cae6565f6a`).
- Input selection: pinned Git commit tree; dirty working-tree file contents were not used.
- Snapshot boundary: only the five listed direct lattice inputs are passed to MAD-X; the source checkout's unrelated files were not copied.
- Target-code commit: `4b9a30ab61c820e99d4f5c18804cafdfdbaeb25f`; runtime: Python `3.14.7 (main, Aug 10 2026, 00:00:00) [GCC 15.3.1 20260722 (Red Hat 15.3.1-1)]`, NumPy `2.3.5`.
- Target source: `git@github.com:HaroonRafique/PTC.git`; install/build method: `bash build/build_ptc.sh builds build_pyptc/libpyptc.so`.
- Loaded shared library SHA-256: `b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76`; API definition: `pyptc/core.py: PTC.__init__, PTC.api_level, PTC.init_lattice, machine_summary, scalar, track_particle_ptc_with_loss`.
- Bootstrap: locally constructed no-lattice library-load and API-level readback; loaded API level `4` without an ISIS lattice.
- Variant/sequence: `00_Simplified_Lattice with 2023.strength overlay` / `synchrotron`.
- Approved recipe authorization: user instructions on 2026-10-26; recipe recorded in step README and feedback 0001.
- Include order: `ISIS.injected_beam → ISIS.elements → ISIS.strength → 2023.strength → ISIS.sequence`.
- Machine settings: `a1=b1=kqtd=kqtf=0`; permitted reference calculation: one MAD-X TWISS calculation.
- Reviewed ledger: `steps/admit-code-to-isis-rcs/review_ledger.csv` (awaiting review).
- Effective command: `/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/steps/admit-code-to-isis-rcs/.venv/bin/python steps/admit-code-to-isis-rcs/iteration-0002/run_admission.py`

- Bootstrap evidence: `bootstrap/bootstrap.log`.
- Reference output table: `madx_work/reference_twiss.tfs` (SHA-256 `97336352b74e7e654ee944e9daced5bcd85198252b9a5d2cdef123258bfff58d`).
- MAD-X runtime: `5.02.00`; executable SHA-256 `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
- Attempt-local input snapshot: `snapshot_inputs/`; logical input names and hashes are in the result and manifest.
- Harness checks: 9 passed; log `harness-tests.log` (SHA-256 `9ebaaf28bcad12b6b56c272e652a679600e3139196d1ebfc297fe2a35887ca94`).

## Executed PyPTC calls

The actual calls and returned values are recorded in `pyptc_api_trace.jsonl`.
- `PTC.init_lattice(madx_work/PTC-PyORBIT_flat_file.flt)`
- `PTC.machine_summary()`
- `pyptc.read_flatfile_fibres(flat_file)`
- `PTC.scalar(ptc_get_p0c_)`
- `PTC.scalar(ptc_get_beta0_)`
- `PTC.scalar(ptc_get_kinetic_)`
- `PTC.track_particle_ptc_with_loss([0,0,0,0,0,0], turns=1)`

## Structural and reference-particle checks

{"charge": 1, "circumference_m": 163.36281999999989, "flat_file_fibre_count": 586, "gamma_t": 5.077658797213571, "harmonic": 71, "kinetic_energy_gev": 0.07044002991247011, "mass_gev": 0.9999999986892394, "n_nodes": 375}
{"derived_beta0": 0.36713319980867437, "kinetic_tolerance_gev": 2e-06, "madx_kinetic_gev": 0.07043999691247005, "madx_mass_gev": 0.938272046, "madx_pc_gev_c": 0.37033168, "mass_summary_raw_value": 0.9999999986892394, "mass_summary_units": "not assumed; API field is not used as a consistency authority", "p0c_difference_gev_c": 8.360876302404563e-08, "p0c_tolerance_gev_c": 2e-07, "pyptc_beta0": 0.367133282695325, "pyptc_kinetic_gev": 0.07044002991247011, "pyptc_p0c_gev_c": 0.370331763608763}

## Minimal smoke

{"coordinate_order": "PyPTC six-coordinate API order; all components initialized to zero", "final_coordinates": [-2.4868995751603507e-14, -2.105877638142796e-14, 0.0, 0.0, 0.0, 3.22068760549854e-14], "finite": true, "initial_coordinates": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "loss": {"lost": false, "lost_pos": 0, "lost_turn": 0}, "loss_policy": "any reported loss fails the one-turn smoke; all final coordinates must be finite", "pass": true, "turns": 1}

## Runtime warning summary

MAD-X: 302 warning/error lines; raw log `madx_work/madx.log` (SHA-256 `54bda3d0e96ce818cabd7e92c87dc316db95d2073fc1bee18389c87335bc2dab`).
PyPTC: 3 relevant runtime warning lines; raw log `pyptc_runtime.log` (SHA-256 `9044cb0b247391a198219302f68d2bec8af617b515d279375cd43a7bf2ecb70a`).
Disposition: MAD-X reports repeated element definitions as ignored; these are counted and retained. PyPTC runtime warnings remain unresolved for review. Structural and reference-particle checks passed, but warning interpretation remains pending external review.
- MAD-X category (302): implicit element re-definition ignored
- Unresolved PyPTC runtime warning for review: COULD NOT LOCALIZE NON 0.0_dp CAVITY FREQUENCY
- Unresolved PyPTC runtime warning for review: DLMAX > LMAX   0.51440000000000197
- Unresolved PyPTC runtime warning for review: ORBIT_WARNING           11

## Nonclaims

This technical outcome applies only to the five hash-identified reference inputs copied from 1bada6a2ab94edd426c52b7e97a5d335926e0646. It is not a clean-checkout result and does not describe the dirty source working tree at 823e6c08dfa79a182548b07706b3d46f0157137a.
It does not validate closed orbit, tunes, Twiss agreement, dispersion, long-term tracking, collective effects, or benchmark agreement. The technical result is pending external review; it is not reviewed acceptance.
