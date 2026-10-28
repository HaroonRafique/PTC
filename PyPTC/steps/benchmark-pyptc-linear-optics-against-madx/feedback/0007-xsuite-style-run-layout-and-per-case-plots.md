# Xsuite-style run layout and per-case plots

Date: 2026-10-28
Source of requirement: user review of the PyPTC optics attempt and request to
follow the organization used by `/home/hr/Codes/agentic_xsuite_test`.
Reference layout: `steps/benchmark-code-against-isis-rcs-optics/runs/attempt-NNN/`,
with root-level run evidence, `cases/<case-id>/` data, and
`plots/cases/<case-id>.png` composites.

## Reusable skill feedback

The optics skill should require one reviewable composite plot for every
simulation test case, not only the nominal case. Each case composite should
contain the case's available comparable profiles and declared response data
as separate readable panel groups, following the existing skill plotting
contract. The plot manifest and report must enumerate the case IDs and link
each to its exact PNG and source data. A run is missing required plot evidence
if a declared case has no composite; output paths must resolve to existing
files. Do not create empty plot directories for blocked cases, and report
blocked/failed cases explicitly.

This feedback clarifies discoverability and coverage across cases; it does not
replace the skill's existing requirement for per-observable panels and
residuals within each case composite. It also does not request one image per
observable.

## PyPTC implementation and smoke evidence

New output is written under the benchmark step's `runs/attempt-NNN/`; the
pre-redesign timestamped bundles under `test_outputs/` remain unchanged. The
runner does not update the human-maintained `runs/INDEX.md` or review ledger.
Current smoke evidence:

| Run | Outcome | Report SHA-256 | Result SHA-256 | Manifest SHA-256 | Plot |
|---|---|---|---|---|---|
| `attempt-001` | `failed` | `c72ce061b386659fc84734b23c87c389b7d10bb852dd9a9002efeb9fcdc7e404` | `b153d933cc3f0dd8624c941dcfa43c1807892a43853d49420a0f6c36d3975990` | `4819894848526cada6a83e06010ace9f7abbf5917543bf88c18ef9b147db4f03` | not produced; initial allocator-layout smoke exposed an uninitialized thin-mode summary |
| `attempt-002` | `incomplete-chromaticity-and-plot-review` | `c20c80fbf5c268236d15297df314ed05ff56e669562c8ffb8a00c511f130a1da` | `be4057726ec35623f0adf978759ea79ad2423eba7c0f66c52fb317236d3f4437` | `f5db503629baf002772a58eb6ae6bf32d9452a452e8511a938d99a849ec2087f` | `plots/cases/nominal.png`; plot manifest SHA-256 `af63744147b254c072f2b22f8bb9c37a8abc233d01717e1fe1a8a2da172d4169` |
| `attempt-003` | `incomplete-chromaticity-and-plot-review` | `ab80bfe37fdc8ba662e373e3a7f9c17d69ed6718a77be5c93ae52c120e0b973b` | `92bbea0d2b2d210da6c4db3f156ed2322fc993c74489c5dc6fc39374eab5b879` | `f36514fec10ba0122a37f61e8a66cd2fbd155a9f98f168efe78ed5fe5a1bae79` | `plots/cases/nominal.png`; plot manifest SHA-256 `64be69991e1c19ce46aa8d12def2556b3cfae6a4929aa4e3ce56878b89aceff3` |

Attempts 002 and 003 independently allocated consecutive run IDs and each
contains exactly one declared nominal case and one corresponding PNG. Both
were agent diagnostics, not user-run acceptance. Existing timestamped run
bundles were left in place. This is local PyPTC campaign feedback for a
separate shared-skill review; no shared skill file was modified.
