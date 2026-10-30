# PyPTC Documentation Implementation Plan

> **For agentic workers:** This plan is executed in-place in the PyPTC repository. Use the ISIS `document-physics-code-with-evidence` skill and Superpowers `executing-plans` workflow. Check off and update this file as each deliverable is reviewed against its evidence and validation criteria.

**Goal:** Build a source-grounded PyPTC documentation package in `pyptc_documentation/`, including a literature review and accessible PTC PDFs, an ISIS technical-note-derived LaTeX document, a quick start, user-oriented code-path chapters, diagrams, copied repository plots, and explicit review gaps.

**Architecture:** Keep the deliverables together under this directory: a maintained plan, a literature review with full citations and canonical URLs, a PDF/reference manifest, a source/claim ledger, and a separate LaTeX project copied from the maintained ISIS technical-note template. The report will follow a user journey from installation/build and lattice selection through Python APIs, optics, tracking, errors/apertures, diagnostics, outputs, and limitations; editable diagrams and byte-identical repository figures will support that narrative.

**Tech Stack:** Markdown; LaTeX with the copied ISIS class; BibTeX; Python's standard library for manifests/checks; Graphviz or TikZ source for editable diagrams; repository-generated PNGs copied without alteration.

**Spec:** User request dated 2026-10-30; local `AGENTS.md`; `/home/hr/Repositories/isis-modelling-agents/skills/documentation/document-physics-code-with-evidence/SKILL.md`; `/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md`; maintained template and rules in `/home/hr/Repositories/chopped_beam_orbit_analysis/v3_documentation/v3_report/` and its parent `AGENTS.md`.

## Global Constraints

- Work only in this PyPTC repository; do not edit the shared ISIS skills or another repository's diary.
- Keep implementation statements tied to the pinned PyPTC source revision, source path, hash, symbol, and line range.
- Label claims as `implemented`, `derived`, `domain_interpretation`, or `unresolved`; do not infer physics from identifiers or inherited prose.
- Keep production/public API routes distinct from tests, examples, diagnostic scripts, legacy interfaces, and unsupported behavior.
- Preserve the user's request to use the maintained ISIS report class and logo; copy them from `v3_documentation/v3_report/`, not from the legacy report project.
- Search primary/authoritative PTC sources first. Download accessible author/official PDFs into this directory and record URL, bibliographic identity, version/date, rights/status, and SHA-256. For restricted or unavailable PDFs, retain a full citation and canonical URL with the retrieval status; do not bypass access controls.
- Copy repository figures byte-for-byte, record original path and SHA-256, and explain each selection in a figure manifest and caption/evidence card.
- Mark code, physics, and reader reviews pending until named human reviewers have completed them.
- Keep the local work diary in `WORK_DIARY.md`; append a substantive record before any later commit.
- Do not commit or push unless the user asks.

## Directory and File Map

| Path | Responsibility |
|---|---|
| `pyptc_documentation/PLAN.md` | This execution record, status, decisions, validation, and later-review questions. |
| `pyptc_documentation/literature_review.md` | Narrative review of PTC polymorphic tracking sources with full citations, URLs, relevance, and evidence limits. |
| `pyptc_documentation/references.bib` | BibTeX entries used by the technical note. |
| `pyptc_documentation/references/pdfs/` | Locally retained, accessible primary-source PDFs with a PDF manifest. |
| `pyptc_documentation/references/PDF_MANIFEST.csv` | Canonical URL, identity, revision/date, licence/access status, SHA-256, and retrieval notes per PDF. |
| `pyptc_documentation/provenance/SOURCE_MANIFEST.csv` | Pinned repository/source revision, file paths, hashes, roles, and documented symbols. |
| `pyptc_documentation/provenance/CLAIMS.toml` | Claim IDs, evidence classes, file/hash/symbol/line references, checks, status, and reviewer fields. |
| `pyptc_documentation/tech_note/main.tex` | Report entry point based on the maintained ISIS class and logo. |
| `pyptc_documentation/tech_note/sections/` | Intro, quick start, user workflow/API chapters, limitations, references, and appendices. |
| `pyptc_documentation/tech_note/sections/quick_start.tex`, `sections/edits_and_boundaries.tex` | Editable TikZ source for the user-path and EFIELD guard flow diagrams. |
| `pyptc_documentation/tech_note/figures/` | Byte-identical copied PyPTC plots and figure manifest. |
| `pyptc_documentation/tech_note/README.md` | Build command, output location, and review status. |

## Execution Tasks

### Task 1: Pin the documentation basis and map the public user path

- [x] Confirm repository clean state and current commit (`8824003` at task start).
- [x] Read local PyPTC instructions, requested skills, publication plan, and maintained template guidance.
- [x] Record the active PyPTC source revision and hashes before drafting.
- [x] Map the user-facing path from install/build to import, default lattice, public APIs, outputs, errors, and examples.
- [x] Identify test-only, diagnostic, legacy, or unsupported paths and keep them separate from production/API claims.

### Task 2: Review PTC literature and archive accessible PDFs

- [x] Search repository history/docs and primary external sources for PTC/Polymorphic Tracking Code manuals, foundational papers, and implementation references.
- [x] Prioritize original manuals, author publications, official PTC/MAD-X/CERN materials, and stable DOI/arXiv/official repository records.
- [x] Write a narrative review that states scope, source-selection method, relevance to PyPTC, and limits; do not imply exhaustive coverage of every paper that mentions PTC.
- [x] Add full bibliographic citations and canonical URLs to `literature_review.md` and corresponding BibTeX entries.
- [x] Download accessible PDFs into `references/pdfs/`; record status, source URL, date/version, rights/access notes, and SHA-256 in `PDF_MANIFEST.csv`.
- [x] Leave closed or unavailable sources as citation-and-URL records with explicit download status.

### Task 3: Copy and clean the maintained ISIS technical-note template

- [x] Copy the class and logo from the active `v3_report/` template, plus only the minimal project scaffold needed to compile.
- [x] Record source paths and hashes for copied template assets.
- [x] Remove chopped-beam text, figures, bibliography entries, and appendices from the PyPTC copy without editing the source template.
- [x] Set a PyPTC title, neutral author/date metadata where author identity is not settled, and an explicit draft/review status.
- [x] Compile the cleaned template as the first technical-note draft.

### Task 4: Draft the document skeleton and quick start

- [x] Add an introduction stating purpose, audience, scope, and what PyPTC does and does not claim.
- [x] Add a quick start using commands verified from this repository; document expected output files and locations without presenting an unreviewed numerical result as validation.
- [x] Add a contents structure following the user's workflow: prerequisites/build, import and initialization, lattice input, optics/orbit access, particle/bunch tracking, apertures/losses, errors/EFIELD, diagnostics/plots, troubleshooting, limitations, references, and API/source appendices.
- [x] Include a top-level user workflow diagram before detailed implementation chapters.
- [x] Tag material statements with claim IDs linked to `CLAIMS.toml`.

### Task 5: Trace and document PyPTC code part by part

- [x] Document user interactions with exact entry points, relevant inputs/outputs, validation, failure behavior, and source locations.
- [x] Trace the Python-to-C/Fortran shim boundary and distinguish it from the wider parent PTC implementation.
- [x] Explain examples as separate runnable demonstrations and comparison evidence, not as the public API itself.
- [x] Record units and coordinate conversions only where code identifies them; flag physics interpretations that need review.
- [x] Add editable workflow diagrams, including the unsupported EFIELD rejection path.

### Task 6: Select, copy, and cite repository plots

- [x] Inventory existing repository plots that illuminate lattice optics, tracking, apertures/loss, misalignment, and error-table comparison.
- [x] Select plots whose source, run, command, and limitations are traceable.
- [x] Copy each selected image byte-for-byte into `tech_note/figures/` and verify source/copy SHA-256 equality.
- [x] Write a figure manifest with source path, hash, run or command, evidence claim, and selection reason.
- [x] Keep all numerical tolerances and acceptance language explicitly pending unless reviewed evidence already establishes them.

### Task 7: Verify source claims and build the note

- [x] Complete the source manifest and machine-readable claim ledger against pinned implementation files.
- [x] Run the ISIS claim-ledger checker against the draft and source manifest; it passes with only expected pending-review counts.
- [x] Build the final LaTeX document from `tech_note/` using the documented command; inspect the final log for unresolved references, missing figures, and citation errors.
- [x] Inspect rendered pages containing the title, quick start, diagrams, copied plots, and references at normal reading size; all 14 pages were rendered and inspected.
- [x] Check all tasks in this plan against the finished files; only verified deliverables are marked complete.
- [x] Append the PyPTC work diary with the documentation milestone, evidence checks, review limits, and publication-plan link.

## Acceptance and Review Status

- A reader can identify the current public PyPTC entry point, build and initialize it using documented commands, select the supported default lattice, run a minimal optics/tracking workflow, and locate its outputs.
- Each material code claim resolves to a pinned source file and check; each physics interpretation is independently sourced or explicitly pending.
- The literature review contains full citations and URLs; every locally retained PDF has a manifest entry and verified hash.
- The cleaned ISIS-class LaTeX note builds and its quick start, flow diagrams, captions, and plots are readable.
- Code review, physics review, and reader review remain explicitly `pending` until named reviewers act.

## User Questions for Later Refinement

These are intentionally deferred; proceed with conservative defaults and record any choice in this plan.

1. Should the final note be operator-first, developer-first, or balanced for both audiences?
2. Which named PyPTC maintainer should review code correspondence, and which accelerator physicist should review units, coordinate conventions, and scientific interpretation?
3. Should the literature scope include every paper that cites PTC, or only foundational PTC descriptions and sources directly relevant to current PyPTC features?
4. Are locally downloaded PDFs intended only for the working copy, or should the final repository retain them where author/publisher rights permit?
5. Should parent PTC Fortran internals be documented beyond the Python/ABI boundary and the PTC methods directly called by PyPTC?
6. What final note title, author list, release/distribution status, and version should appear on the cover?

## Decisions and Progress Log

- 2026-10-30: Use `/home/hr/Repositories/chopped_beam_orbit_analysis/v3_documentation/v3_report/` as the maintained template source; the older `ISIS_Tech_Note__Chopped_Beam_Analysis/` tree is legacy and will not be copied as the starting point.
- 2026-10-30: Keep literature review, downloadable PDFs, source/claim provenance, and LaTeX report together in this directory. Research scope is an evidence-backed PTC bibliography and narrative, not an unbounded exhaustive citation scrape.
- 2026-10-30: Search of PyPTC's Python, wrapper, tests, workflows, and parent PTC source found no maintained PTC bibliography in the code tree; parent Fortran carries authorship/copyright notices. The external review therefore records original PTC/FPP sources, MAD-X integration literature, historical module documentation, and later theory, and explicitly excludes the unbounded corpus of application papers.
- 2026-10-30: CERN's direct 2002-report PDF endpoint returned an anti-bot page; the KEK alternate host did not resolve. Five directly retrievable primary PTC/FPP papers and manuals are retained with local hashes; the foundational report, distinct historical MAD-X PTC module manual, and publisher book are cited with explicit retrieval/access status.
- 2026-10-30: Retrieval of the historical manual URL returned a 68-page PTC User's Reference Manual dated 2010, not the separately cited 2006 MAD-X PTC module manual. The downloaded filename, bibliography entry, and manifest now use the title-page identity; the 2006 record notes the URL/content mismatch.
- 2026-10-30: The copied class contained chopped-beam keyword defaults. Replaced the defaults in the local copy, recorded both original and derived-copy hashes, and left the template source untouched.
- 2026-10-30: Completed the basic `track_bunch()` user-path description against `PTC.track_bunch` in the pinned core source. Kept coordinate units and physical meaning under the existing physics-review hold.
- 2026-10-30: Expanded this Markdown review to include complete reference citations and direct URLs for every cited source; retained the 2006 MAD-X manual URL/content collision as an explicitly unresolved bibliographic lead.

## Final execution and review record

- The report built in `tech_note/` with the exact documented sequence: `pdflatex -interaction=nonstopmode -halt-on-error main.tex`, `bibtex main`, and the same `pdflatex` command twice more. The build log is `test_outputs/rendered_pages/latex-build.log`.
- Build checks: passed. The final LaTeX runs contain no LaTeX errors, unresolved citations or references, missing bibliography/figures, or overfull boxes. The cleaned report/class search found no chopped-beam content. `pdfinfo` reports 14 A4 pages.
- Final draft PDF SHA-256: `ad761c77a3f241fe21aeb72c27e00ee77f36918accb4ea9676fbe8602b6ca337`. The extracted text, PDF metadata, build log, and 90-dpi page renders are retained under `test_outputs/rendered_pages/` for review.
- Visual check: inspected all 14 rendered pages. Title metadata and keywords are PyPTC-specific; diagrams, API table, plots, captions, quick-start commands, and bibliography are readable at the rendered size. The diagrams are editable TikZ in the section sources. No layout defect requiring an editorial patch was observed.
- Evidence check: the ISIS claim-ledger checker passed with 0 errors and 0 warnings; the 19 code-mapped claims, 2 derived checks, 5 physics-review-pending claims, and 2 reader-review-pending claims were reported. Its self-test passed with the expected 9 negative-test codes. Seven copied plot hashes match their source manifest records; the five retained PDFs match their recorded SHA-256 values.
- Remaining gates: named human code, physics, and reader reviews are pending. PDF redistribution rights have not been independently reviewed. The 2002 CERN PDF endpoint and distinct historical MAD-X PTC module manual remain retrieval gaps. No approval, physics acceptance, or validation for ISIS RCS operation is claimed.
- Overall plan status: documentation package and reproducible draft complete; publication/release and scientific/code acceptance remain pending human review.
