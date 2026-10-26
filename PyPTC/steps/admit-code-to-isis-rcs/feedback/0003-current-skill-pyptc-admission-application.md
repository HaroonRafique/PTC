# Feedback 0003: current admission skill applied to PyPTC

## Evidence class and scope

This is agent-run skill-application evidence, not a user-run skill test. The
fresh harness was reconstructed from
`admit-code-to-isis-rcs` at `isis-modelling-agents` commit
`85a897a47b55951552226221dcdbc3b83a8daf71` (skill SHA-256
`ca7457645d0fe9049e7b55c50fc3b035b4db771bdb5984c6ab662cbe3cfbf35f`). It was
kept separate from the pre-existing PyPTC admission harness, examples and
tests. The approved inputs are the five-file snapshot in
`../reference_snapshot/`, materialized from `isis_2024` tree commit
`1bada6a2ab94edd426c52b7e97a5d335926e0646`. It contains no nested repository.

The source checkout was at `823e6c08dfa79a182548b07706b3d46f0157137a`, with
206 dirty status entries. Its full porcelain-v2 status is retained in the
snapshot and each attempt. The files used came from the pinned commit tree;
dirty working-tree contents were not used. Therefore the technical result is
limited to those five hash-identified inputs and does not establish a clean
checkout result or describe the dirty checkout.

The recipe follows the user's instructions: simplified ISIS RCS lattice,
`2023.strength` overlay, sequence `synchrotron`, `a1=b1=kqtd=kqtf=0`, and one
MAD-X TWISS reference calculation. The result is an admission smoke only. No
optics validation, benchmark, physics acceptance or shared-skill change is
claimed.

## Attempt history

All rows remain `awaiting review`; the ledger records `pending` and `none; no
acceptance`. Hashes below are SHA-256 of each report, canonical result and
manifest. The older 131858/131925 attempts and the blocked 180201 attempt remain
documented in feedback 0001 and 0002 respectively.

| Attempt | Outcome | Report SHA-256 | Result SHA-256 | Manifest SHA-256 | Learning |
| --- | --- | --- | --- | --- | --- |
| `attempt-20261026T195852Z` | blocked | `dae6c33375900aa38e0321bbbdeecf9452c144ea54b156fe375d2cd1acfae2d8` | `748ee33ec243a3aca6420d9e3df6440935e22b7c1c4493b2f72fbf75a49aa1cb` | `b85106ee9bb8d8861e1e76ceebd3b497ff9a052155707cde9a4c68fb24b46abe` | A naïve TWISS counter counted `SELECT ... TWISS` as a second calculation. Fixed with a command-aware matcher. |
| `attempt-20261026T195935Z` | admitted-snapshot | `5f906037dec3743d104194f87d364cbcc7a72b6c5fdd3e4f7df51807bcbd1cf0` | `8e7d6870a3c94c398f57b3ced17ef63013064c8d1864d0501ddb46c451e14091` | `c03639da64ec90f55ae26c5033c668d455c79f13b41512ce045ba43fd426b274` | Engine-native PyPTC stdout was not retained; warning assessment was incomplete. |
| `attempt-20261026T200142Z` | admitted-snapshot | `5295676ada16fc3a457f0a66d2a319e28e221c9301d0e15be95b47a146a514cf` | `0c9d8a206545842b04dbda60d113c8dc448a21b8f81931d01fea3cb2c0ab4b52` | `78f614f9f6e4316c3a1eefd480eea91a1fcb772dada3b7c13693aa3bc6921560` | Runtime log was retained, but a normal MAD-X iteration line was counted as an error; implementation and test copies were absent. |
| `attempt-20261026T200243Z` | admitted-snapshot | `4da58c7f886f9ba8717cda2593e3714625d9caae34207166ded7500aa550b4d9` | `df87c01605722ed7a13064846e6807f5fc0bf1e8e5926318bbd6bb04ea473903` | `f087b9744e71ba0d68d9bdeed49370707d5eb188d3790ff57c48d46c438c0f1c` | Warning count and both engine logs were fixed; snapshot nonclaim, target source identity and explicit smoke loss policy were still missing. |
| `attempt-20261026T200405Z` | admitted-snapshot | `cb038738a63fca2c4e2066fed6cad2d16adef25b6f7f6179953fb03f25d83fbb` | `b19cb93ddab43721bf2d7a6694d01d72134dca43e505c21e182882132c5980e9` | `2578f4318fe750a714ff487c930fc61eb8fd315e600b3afc1325c1f046cbd54c` | Added copied harness and 9-test record; snapshot scope, target source identity and loss policy still needed explicit representation. |
| `attempt-20261026T200601Z` | admitted-snapshot | `73737f02091b265cc2bdc25f1ead41ecab954b4c0059e3192662cb959f67c8b6` | `05b20bd5662b871fe441e973c62ef3d935763352423cbc819713668429d382a2` | `14be370f498845e8ad2dbc864deec6eda1bba85f3ce3d44a66d89e168774b0dc` | Added snapshot scope, target origin and loss policy, but report duplicated the dirty-tree disclaimer and omitted final punctuation. Superseded below. |
| `attempt-20261026T200752Z` | admitted-snapshot | `a53aaa7bfbc18e1f0c857a4ad1d3fe45aae9cd25e908c8e75026b2c32278a89f` | `9ddbf15bc08d0f245c2c16e58b69df784ea6e77a8ada2a6850966755f3139899` | `bc6ecf0da43bc6dc6439804a4756a11a127fbbe38a36ae208230a21908abca25` | Regenerated after correcting report wording; this is the current complete technical bundle. |

Earlier first-iteration evidence, including two earlier admitted bundles with
review gaps and a blocked dirty-checkout preflight, is retained by feedback
0001/0002 and ledger entries. All raw bundles older than the newest three are
eligible for pruning only after this feedback and ledger evidence are saved.

## Current attempt result

The current bundle is
`test_outputs/admit-code-to-isis-rcs/attempt-20261026T200752Z/`.
The independent harness tests passed 9/9. PyPTC built and loaded from the
identified target checkout (`git@github.com:HaroonRafique/PTC.git`, code commit
`4b9a30ab61c820e99d4f5c18804cafdfdbaeb25f`); the built library SHA-256 is
`b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76`, API level
4. The no-lattice bootstrap succeeded before the ISIS flat file was loaded.

MAD-X 5.02.00 produced the reference TFS and PyPTC loaded the exported flat
file. The parsed file has 586 fibre records and the machine summary has 375
PyPTC nodes, circumference `163.36281999999989 m`, charge `+1`, and harmonic
71. MAD-X `pc=0.37033168 GeV/c`; PyPTC `p0c=0.370331763608763 GeV/c`, a
difference of `8.36e-8 GeV/c` against a `2e-7 GeV/c` tolerance. Kinetic energy
also passed its recorded tolerance. PyPTC's raw `mass_gev` field is retained
but its units are not assumed and it is not used as the reference authority.

One zero-offset particle completed one turn with finite coordinates and no
reported loss. The explicit policy is that any reported loss fails and all
final coordinates must be finite. Effective MAD-X values for `a1`, `b1`,
`kqtd`, `kqtf`, and every per-element trim variable were zero. Base harmonic
amplitudes were zero; the overlay introduced no nonzero harmonic assignments.
The normalized TWISS fingerprint excludes only `@TIME` and `@DATE` rows.

The report retains 302 MAD-X warning lines, classified as ignored implicit
element redefinitions, and three unresolved PyPTC messages:
`COULD NOT LOCALIZE NON 0.0_dp CAVITY FREQUENCY`, `DLMAX > LMAX`, and
`ORBIT_WARNING 11`. Their significance has not been determined. The measured
structural and reference-particle checks passed, but the warning interpretation
is pending external review. This outcome is not reviewed acceptance.

## Assessment against the current skill

The current attempt now retains the main evidence chain required by the skill:
the exact skill revision and hash; identified target source and build/library;
authorized recipe and include order; source dirty-state evidence and pinned
input hashes; local bootstrap; engine/API commands and logs; warning summary;
flat-file and TWISS hashes plus normalized fingerprint; structural and
reference-particle checks; one-turn loss policy/result; nonclaims; pending
review disposition; and a copied implementation/test pair with its hashes.
The harness also guards the clean-checkout precondition and snapshot identity,
tests unapproved recipe changes, zero harmonic/trim defaults, report warning
disposition and volatile-header handling. The failed first fresh invocation
exposed and fixed an overly broad TWISS command counter before any engine ran.

Remaining feedback for the skill and its application:

- The full dirty-checkout gate is tested as a helper and was exercised by the
  earlier blocked preflight, but the successful snapshot run is still an
  explicitly authorized exception; it must not be presented as clean-checkout
  admission.
- The focused suite has nine tests. It does not yet establish broad report
  schema coverage, immutable attempt contents after creation, every parser
  edge case, or acceptance-ledger review workflow end to end.
- PyPTC warning meanings remain unresolved. Review must decide whether the
  three messages are expected for this minimal zero-offset smoke, require a
  narrower recipe, or indicate a material defect.
- No optics observable, closed orbit, tune, Twiss agreement, dispersion,
  long-term stability, collective-effects, or benchmarking evidence was
  generated, as required by this admission-only phase.
- PyPTC `machine_summary()` exposes `mass_gev` as approximately `1.0` while
  MAD-X mass is approximately `0.938272046 GeV`; the harness treats the PyPTC
  field as raw and does not use it as authority. The API field semantics merit
  separate review before adding a mass comparison requirement.

## Post-run learning comparison with existing PyPTC examples/tests

Only after generating and running the independent harness, existing PyPTC
examples/tests were inspected for learning. This comparison did not supply
code to the fresh harness.

- `tests/test_default_lattice.py` describes the generated simplified lattice
  as the default and checks the 586-fibre flat file. The attempt also parsed
  586 fibre records, but explicitly exercised the approved five-file snapshot
  recipe rather than the default lattice generator. This is a useful structural
  cross-check, not proof that the default-generation path was admitted.
- `examples/00_generate_flat_file.py` calls the shared
  `common.generate_flat_file` path. The fresh harness instead writes a
  transparent attempt-local MAD-X recipe from the pinned inputs. The generator
  path remains to be admitted separately if it is in scope.
- `tests/test_pyptc_shims.py` uses public `PTC` load, lattice initialization,
  machine summary and tracking APIs. The attempt independently exercised the
  corresponding public API surface, including loss-aware one-turn tracking.
- The 586 flat-file fibre records and 375 `machine_summary` nodes are different
  counts at different layers; they are retained separately and should not be
  conflated.
- Optics examples and tests were not used to judge admission and remain out of
  scope until the user starts the optics phase.

## Required follow-up

Keep the newest three raw attempt directories as requested by the established
retention rule. The older attempts' hashes, outcomes and lessons are captured
here and in the ledger. The work diary in `isis-modelling-agents` needs an
append-only correction recording that the pushed source now permitted an
explicit files-only pinned snapshot and that attempt `200752Z` technically
passed but awaits review; preserve the earlier blocked entry as history. No
attempt has been reviewed or accepted, no skill has been edited, and no commit
or push is implied by this feedback.
