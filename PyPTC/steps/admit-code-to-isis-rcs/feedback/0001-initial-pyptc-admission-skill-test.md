# Feedback 0001: initial PyPTC admission skill application

## Evidence and scope

- **Evidence class:** agent-run diagnostic observations. These were not
  user-run skill-test attempts and do not establish skill effectiveness.
- **Invoked skill:** `admit-code-to-isis-rcs`, ISIS Modelling Agents commit
  `93ec13662741fccf44c708d23754a706217b5764`, skill blob
  `2823f6aa360b91b6bf6d99a1f55339eacd4b2378`.
- **Target:** PyPTC repository revision
  `cde0d28fbd1f5cf73a7e945c3bec44cc49f1cc0d`.
- **Reference:** `isis_2024` commit
  `1bada6a2ab94edd426c52b7e97a5d335926e0646`,
  `00_Simplified_Lattice` with `2023.strength`, sequence `synchrotron`.
  Approved include order: `ISIS.injected_beam`, `ISIS.elements`,
  `ISIS.strength`, `2023.strength`, `ISIS.sequence`.
- **Machine settings:** `a1=b1=0`; trim quads `kqtd=kqtf=0`. The reference
  recipe made one MAD-X TWISS table for the authorized reference calculation.
- **Testbed process precedent:** clean
  `agentic_xsuite_test` revision `387b43eee83b9bfaf7d2f436ddbe43ba42bb2f35`.
  Its admission instructions distinguish user-run attempts from agent
  diagnostics, keep feedback immutable, maintain a review index, and retain
  the three newest raw bundles.
- **Publication cross-reference:** `isis-modelling-agents` publication plan,
  Task 6 (controlled and longitudinal evaluation evidence) and Task 9
  (event-driven skill-use and campaign-evidence maintenance). No controlled
  paired evaluation, skill maturity promotion, physics review, or publication
  claim is made here.

## Attempt history

All five runs used the same PyPTC revision and the same pinned reference-input
hashes. They are retained here as diagnostic history. Their technical results
are not reviewed-ledger decisions.

| Attempt | Technical outcome | Observation | Report SHA-256 | Result SHA-256 | Manifest SHA-256 | MAD-X log SHA-256 |
|---|---|---|---|---|---|---|
| `attempt-20261026T131543Z` | `failed` | Relative input paths were wrong; MAD-X exited before expected outputs. | `661f0afde8bbce2253ac84ce9019e98dc53ba65f069b577ab1f8120e8db04384` | `df6c77d6da977b6b2d2493ed2907075cd46433414361d6b5fd052a31dcf3cd03` | `09939ab8a5bb4f38144f61fa02c2ae4cef2d1c805fdc166cdcadfc751346299c` | `aa5d07d08aa7352a8f007223f7327cf0ed4fc4f7c7691e26f20b15c8d8c245d1` |
| `attempt-20261026T131602Z` | `failed` | MAD-X succeeded, but the effective-value parser did not accept its semicolon formatting and reported all requested values missing. | `93776f00bf019a0489420647a03cba848358ae6237f2c4c5234a3397bc988369` | `2649f403012b35fa5d11082f4664c1ddb0263bd9a094dda7e7deeaddf04e4618` | `881c6e01b74020b452b175a127c87b0993224744cba65cf39bebbf7f81b784c9` | `e7f60c7ab6f7b8dcfe8ee29f53768b6d76cdec5dc784745b75876611bf3dec61` |
| `attempt-20261026T131700Z` | `failed` | Lattice loaded, but the momentum comparison tolerance was too tight for the flat-file value: PyPTC `0.370331763608763` versus input `0.37033168 GeV/c` (difference about `8.36e-8 GeV/c`). | `21806f6dd17d0562fbf61c67e4112bad7272ffadf89e1cd1433b989ae812af88` | `0937365d9ad806f8e01430b1cea976241b630a0d4ab2ec4ee4e6ae9fc9f7b581` | `b5ae4d82db03bfbe265d977ca98242083d149e4c0278d66e1f33f5ca864c5355` | `b9f96c398111802dcf76a0558064f23f5abff935180b0f6507020461e50662be` |
| `attempt-20261026T131858Z` | `admitted` | One-turn smoke passed. Review found that the machine-summary mass appeared under a `mass_gev` API key despite being raw AMU; the harness hash was also absent from provenance. | `538ce975515e7f57cf3a34a94902544d2759d7fc61318e42f26a326b058c036d` | `f489e4734de148f42802902515d3ece6c7153d2bd076b6433c1623d139bc75f0` | `280879b506932bf30a2c967cf75a9ab4f70cabf888067712ae80ec0c41efa596` | `a018c352196a7f163b348652ecb90f0473dc8b5438cc205c91eb868b687425b3` |
| `attempt-20261026T131925Z` | `admitted` | Momentum tolerance was documented; machine-summary mass was relabelled raw AMU; runner, setup, requirements, and unit-test hashes were added. Review gaps below remain. | `cf2bfe7b67cd2494b2b618461046ed346994878fcf07be78209552a1d53c0bcf` | `941771d6e0ead750df345d06b03cf6481d1080acc1697010937ee6197bc9d0bb` | `34f6475400c5c7d6b385dda27fb25ab1e39327344e4d8dba957945c012809acb` | `0f34c8bb48a444524342e8fccdd6a1920c5ca55c5748ba23d4018f9f09239e9e` |

The identical pinned input hashes in each bundle were:

| Logical input | SHA-256 |
|---|---|
| `Lattice_Files/00_Simplified_Lattice/ISIS.injected_beam` | `2759a6ef97d7799412ba293c8fc788ad34c356ca3b7098acd2a106f7142c92df` |
| `Lattice_Files/00_Simplified_Lattice/ISIS.elements` | `33ec2aedddde548b4f19f9fe9dd26d48ce4445f36c2c118dfa82d239dda8dffa` |
| `Lattice_Files/00_Simplified_Lattice/ISIS.strength` | `912286281994f76e09561b42b32335b65dbc50d6d438f2caa3c8a9f7018b04cf` |
| `Lattice_Files/00_Simplified_Lattice/2023.strength` | `a66ca836e9bbdc6560b2196dbe02c12a3c1781bff0b74589d2995d7689f430ed` |
| `Lattice_Files/00_Simplified_Lattice/ISIS.sequence` | `3cfc1fbb8c39e0d455a0518c4c37abd28058e7e5937231e8bb7cc9462adc9e1d` |

The final successful attempt recorded 375 PyPTC nodes, 586 flat-file fibre
records, circumference `163.36281999999989 m` versus the reference
`163.36282 m`, and harmonic number 71. It recorded zero `a1`, `b1`, `kqtd`,
`kqtf`, and all 20 derived trim strengths. The one-turn zero-offset particle
remained finite and was not reported lost. The momentum comparison used an
absolute tolerance of `2e-7 GeV/c`. This is technical software evidence only.

The final MAD-X log reports 302 warnings overall, including the PTC message
`DLMAX > LMAX` with a recommendation to resplit the lattice. The report links
the raw log but does not summarize this warning. The TFS raw hash changes
between repeated successful runs because its `TIME` header changes; no
normalised/semantic fingerprint is currently recorded.

## Assessment against the skill

### Demonstrated or handled well

- The run used the approved pinned source revision and exact input closure,
  rather than trusting a working output in the reference checkout.
- The approved 2023 overlay and include order were explicit. The source and
  effective checks found the requested zero harmonics and trim strengths.
- The run exercised PyPTC’s public lattice-loading and particle-tracking path,
  retained the MAD-X log, TFS, flat file, reference-particle data, and raw
  artifact hashes, and stated admission nonclaims.
- Technical outcome and review disposition are distinct in the result. The
  two successful attempts remain `awaiting review`.

### Harness nonconformances with explicit skill requirements

- At run time, `review_ledger.csv` contained only its header. Neither report
  nor canonical result linked the ledger, and none of the five runs had a row.
  This failed the skill’s existing review-record contract. After the audit,
  rows were added for all five attempts with disposition `awaiting review`, no
  acceptance scope, and this feedback as the review record. The two oldest raw
  bundles were subsequently pruned under the selected three-bundle policy.
- The runner extracts inputs with `git show` from the pinned commit but never
  checks or records the reference checkout’s working-tree status. The exact
  input tree is pinned, but the recorded `clean-checkout` mode does not satisfy
  the skill’s explicit requirement to verify checkout cleanliness.
- The human report names the MAD-X include order but does not expose the
  executed PyPTC API calls (`PTC`, `init_lattice`, reference-particle scalar
  reads, and one-turn tracking), or a precise authoritative API/documentation
  identity.
- Build command and shared-library hash are present, but no separate retained
  bootstrap result demonstrates build/import/trivial operation before ISIS
  input was introduced.
- Harness tests cover recipe ordering/basic zero values, explicit paths, the
  missing-reference blocker, and a ledger non-edit check on a blocked run.
  They do not guard complete canonical defaults, report completeness,
  technical-success pending review, or the unapproved-recipe negative cases.
- The validator checks base harmonic assignments and overlay trim assignments,
  but does not reject overlay assignments to every harmonic variable; the
  effective log checks `a1`/`b1` and trim strengths, not every possible
  overlay-defined harmonic amplitude.
- The effective command omits the MAD-X executable argument and allocated
  attempt ID even though related runtime and output details appear elsewhere.
  Both report and result should identify the review ledger.
- The 302-warning count and `DLMAX > LMAX` resplitting message are not
  surfaced in the human report, although the raw log is retained.
- The repeated TFS raw hashes differ because the `TIME` header changes, but no
  normalised fingerprint was retained. The skill already requires raw hashes
  plus a documented normalised fingerprint when repeated runs are compared.

## Lessons from existing PyPTC examples and tests

This comparison was performed after the independent harness and runs were
already created. It is learning evidence, not an input to those runs.

- `tests/test_default_lattice.py` establishes the simplified default and its
  586 flat-file fibre count. The final admission bundle also has 586 fibres;
  its 375 PyPTC nodes are a different structural count, not a contradiction.
- `examples/00_generate_flat_file.py` and `tests/test_pyptc_shims.py` illustrate
  local flat-file and PyPTC loading patterns. They were not used as the
  admission input authority; the attempt materialized the pinned input closure.
- `examples/01_plot_bare_twiss_closed_orbit.py` proceeds into Twiss, tunes, and
  chromaticities. Those checks are out of scope for admission and must remain
  in the later optics validation phase.
- PyPTC reports raw machine-summary mass in AMU under an API field named
  `mass_gev`. The admission record now labels this as raw AMU in the machine
  summary, but one reference-particle field still says only `raw` without a
  unit. This is PyPTC-specific interface evidence, not a reusable skill rule.

## Reusable skill feedback and local protocol

Most observations above are implementation failures against requirements
already present in the current shared skill; they should first be corrected in
the PyPTC harness, not repeated as new shared instructions. A separate
`isis-modelling-agents` skill-review agent compared this feedback with the
skill and confirmed it already requires a clean-checkout verification, API
identity and calls in the report, ledger links, pre-ISIS bootstrap evidence,
complete provenance, normalized fingerprints, and tests for unapproved recipe
changes and review-state separation.

Two narrowly reusable clarifications are proposed for separate skill review:

1. For clean-checkout mode, explicitly retain the pre-run cleanliness check
   and result in the evidence bundle, and test that a dirty checkout blocks
   before either engine runs. A pinned commit and input hashes alone do not
   show that the checkout was clean.
2. Consider requiring a concise report summary of relevant engine/runtime
   warnings, their disposition, and any unresolved warning, while retaining
   the raw log. Test that this summary is present. A warning alone need not
   invalidate admission unless it leaves a structural/reference discrepancy
   unexplained.

The momentum-rounding tolerance, raw mass units, harmonic parameter names, MAD-X
warning text, and PyPTC file layout are campaign/code-specific. They should not
be generalized into the shared skill. The API invocation, ledger linkage,
bootstrap evidence, provenance, fingerprints, and recipe-negative tests are
already shared-skill requirements and need harness fixes, not duplicate skill
text. None of these observations calls for Twiss, tune, dispersion, orbit
agreement, or benchmarking in admission.

From this point, PyPTC skill development and benchmarking will follow the
Xsuite testbed pattern: rebuild the working harness from the exact current
skill revision; have the user run full attempts; let the agent run only bounded
preflight/diagnostic checks; assess each user-run result against the skill
before comparing with existing PyPTC examples/tests; append immutable
feedback; update the manual ledger; and retain the newest three raw bundles.
A separate agent in `isis-modelling-agents` reviewed the current skill and
identified the two proposed clarifications above. A draft shared-skill change
is pending that agent’s follow-up and user review. These five earlier runs
remain agent-run diagnostics and are not retroactively classified as user-run
tests.

## Review and publication status

- **Technical review:** two runs reported `admitted`; both remain pending
  human review, and this feedback identifies outstanding evidence gaps.
- **Ledger:** the initial harness left it empty; rows now exist for all five
  attempts as `awaiting review`, with no acceptance scope. No agent assigns
  acceptance.
- **Skill follow-up:** the separate `isis-modelling-agents` review found the
  listed requirements already present and proposed only the two clarifications
  above; a draft and user review are pending.
- **Publication link:** prospective skill-use/campaign observation for Task 6
  and event-driven maintenance for Task 9 in
  `docs/plans/2026-10-23-evidence-gated-agents-publication.md`. This record
  does not satisfy a controlled paired evaluation, create a usage record while
  that policy is inactive, or change the technical note or abstract.
- **Review status:** awaiting user review; no named accelerator-physics
  acceptance or disclosure/release decision is recorded.
