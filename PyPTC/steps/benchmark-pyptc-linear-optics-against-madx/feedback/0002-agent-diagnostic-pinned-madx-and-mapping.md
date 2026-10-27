# Feedback 0002 — pinned MAD-X and profile-mapping preflight

This immutable update supersedes the environment limitation noted in
feedback 0001: the exact MAD-X 5.02.00 binary used by admission is present at
`workflows/madx/bin/madx-linux64_v5_02_00`. The runner now verifies its
SHA-256 against the accepted admission result and reruns it. The locally
installed cpymad/MAD-X 5.09.03 is not used. This record is still agent
diagnostic evidence; the user-run attempt and user review have not happened.

## Pinned provenance

- Skill repository revision: `a9aeca88bdf7e7e81c71423c8a99ca0937540d67`.
- Skill SHA-256: `ae393dba4f719f6416b061970f5974bf00b599db25eabfdfcb6836fbc4dfefbd`.
- Accepted admission: `attempt-20261027T082315Z`, snapshot-admission scope only.
- Accepted PyPTC code commit: `324c1a6e0389137c4f93658621089f9e01159827`; loaded library SHA-256 `b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76`.
- Pinned MAD-X 5.02.00 executable SHA-256: `426d2e88d42c14205d8930b2d720b7c5a5fffc7e499e3d0a7a4bf575e0110c04`.
- Ordered reference inputs and their hashes are read from the copied accepted bundle. Recipe state is `a1=b1=kqtd=kqtf=0`, with each `kqtd_i` and `kqtf_i` read back as zero.
- Final current runner SHA-256: `7bfc1278ba995d91a2b1d58bf8e01511314820a5a69caf1b087386dce6cb6ca4`.

The accepted bundle is copied as a whole into this separate benchmark step.
No failed admission attempt, existing PyPTC optics example/test, or Xsuite
artifact informed the first skill application. The only PyPTC source read was
the pinned Fortran/C wrapper implementation, used for API-boundary semantics.

## Diagnostic history after feedback 0001

| Attempt | Outcome | Evidence |
|---|---|---|
| `attempt-20261027T142636Z` | Pinned MAD-X and PyPTC smoke passed; profile mapping blocked | Report `28ea6d4f2fb7648ae98b766512ae67b5b5bbb44491c96a173ad65db418e0e0dd`; result `1188d11077c70a02a15e7217f0889d7a1ae0d2ab9c7ceb3233e0934f8dcf9ff7`; manifest `d477545bee51203f59179cf9aed58f37f0d678c79922668f5d63ea45c37dbeb3`. |
| `attempt-20261027T142741Z` | Diagnostic failed: effective-value parser did not request/log base `kqtd`; fixed before the next run | Report `a97f8b5f781df0074918f1195e96810c3078fc7a416985fe21bff60ab04aca5a`; result `49621f6f34d3c8e462865b5e6a3340a03de10c2044455ce011477e6a201a6eff`; manifest `ef9e228f71c10fce8510b1c22fb474ff1e03272317195f6c93fe360ca98118b1`. |
| `attempt-20261027T142753Z` | MAD-X 5.02.00 and PyPTC smoke passed; exact direct-s mapping remained blocked | Report `0c3e73e156995aa8df1192558cde9ead8ccd41649402d3f47a2803987cdb5a7e`; result `bacee6b876cb0c029af6e0909d541f2535f32d07ffaf83743c19bf5965bdf52d`; manifest `722cb00f30919bdcd2b888488bdd0509362e3585e8fb868e3d8b99889a16dc43`. |
| `attempt-20261027T143138Z` | Attempt to install unique MAD-X markers at all target node positions failed | Report `5c43b754ad45958d3d6165cc073b176376346a8a1c265041f3262e49c5391918`; result `80e700db7c88e39d33eafd9a6512278d94d897621b6e8ff2df1837f99f85163a`; manifest `e9f124e3ea504f535a7e8f6cf1d6060e3170e98f73ed1d08cdac2d3c0efbd5fd`. MAD-X fatal: negative drift between `PYPTC_NODE_0007` and `SP0_QD`, `-0.2596 m`. The recipe hash is `4bb768ecbaa2b8ff9c90814671aac6c58bb4e63ce69bc8fc89cf5ffaf5ebedce`; log hash is `bf3869f4dae80a9f109ce67f5d476eb696c6e38e8718e64f7f50865ec8cab7eb`. |
| `attempt-20261027T143428Z` | Stable no-argument runner smoke passed; comparison blocked | Report `53055d32b186fa325002bbbc1dd3e84e54a7ed0939500cc7413a6a54de5dccd3`; result `b67ce4e97d4fa629f73fe1bb58e2300086d2d87d54fa16b7d4c0399e858b4cbf`; manifest `4761e93fe021c8504cc3701099349718d4998cefe536aa8b5980dbfd8052cef2`. |
| `attempt-20261027T143507Z` | Final preflight smoke after collision-safe IDs and runner-hash capture; comparison blocked | Report `9b458e80706de7911f983a03bd7911c473b77078a4d6b473006b0426d505476c`; result `2c4672a4785d6572a9ab5c2144918f182aa37c4886c90ba95ff9fe46c7e37f3a`; manifest `ff0a4f83ff664507b8d695a3967c151e63504c040a2374b249566d0f99c4a6df`. |

## Findings against the skill

The final preflight reruns exact MAD-X 5.02.00 and PyPTC against the same
accepted five-file state. MAD-X TWISS explicitly requests orbit, beta, alpha,
dispersion, dispersion derivatives, phase, and `CHROM`; harmonic, trim, and
individual trim variables are read back as zero. The per-run MAD-X `GAMMA`
produces `beta0=0.36713319993`; the retained common-convention reference CSV
multiples `DX`, `DPX`, `DY`, and `DPY` by this value as required by the skill.
The run captures the 302 ignored MAD-X redefinition warnings and PyPTC's
no-RF and `DLMAX 0.5144 m > LMAX 0.5 m` messages.

Pinned PyPTC source inspection verifies that the exposed Twiss/orbit row is
the orbit-node exit value, with that node's length representing the preceding
longitudinal interval. The C interface converts zero-based indices to
one-based orbit-node indices. This resolves row sampling location, but the
public records still lack an element/occurrence identity. Direct MAD-X TWISS
has 586 rows; only 153 of 375 target node-exit positions have a unique exact
`s` match at `1e-9 m`. The largest nearest-position residual is `2.49315 m`.

Unique markers cannot simply be installed at all target positions: at least
one position lies inside a thick quadrupole, and MAD-X terminates with a
negative-drift error. No interpolation/splitting policy was authorized or
verified, so profile residuals remain uncomputed and profile comparability is
`blocked`. Do not change the established PyPTC resplitting or LMAX behavior as
part of this benchmark.

Scalar tune differences are `+5.3895921e-5` and `+1.0652754e-4`; circumference
difference is `-1.14e-13 m`. They remain `pending-tolerance`. Native MAD-X
chromaticities are `-4.745390843` and `-4.806168146`; PyPTC returns
`-4.745307641` and `-4.806147200`. Their small native differences are retained
but blocked from an agreement verdict until PyPTC's derivative coordinate is
reconciled with MAD-X 5.02.00 `dQ/dDELTAP`.

The diagnostic plot is not the skill's required combined profile/residual,
family-strip, and working-point plot. Tracking is blocked pending interpretable
linear prerequisites. No tolerance, physics acceptance, publication
completion record, or skill-effectiveness claim is made.

## User-run status

Iteration 0001's no-argument runner is ready for the user-run skill test. It
creates an inspectable raw bundle with a bounded, honest `blocked` result.
After the user runs it, assess that attempt first against the pinned skill,
then compare with existing PyPTC examples/tests for learning, and create the
next immutable feedback file. This feedback is only preflight evidence.
