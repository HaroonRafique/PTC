# PTC polymorphic tracking: literature review and source map

**Research cut-off:** 2026-10-30
**PyPTC implementation basis:** repository commit `8824003c956390e921a1d469f77c247859a63258`
**Status:** curated primary-source review; not a complete census of every publication that cites PTC.

## Scope and search method

This review identifies sources that explain PTC itself, its fully polymorphic package (FPP), and its integration and user-facing modules in MAD-X. It records the direct PTC User's Reference Manual and the separately cited historical MAD-X PTC module manual. The selection prioritizes original author reports, CERN/KEK material, and JACoW proceedings. Search terms included “Polymorphic Tracking Code”, “PTC”, “FPP”, “MAD-X PTC integration”, “PTC reference manual”, and the relevant report and proceedings identifiers. Source records were checked against available repository/official-host metadata and the source documents where retrievable.

“All references” here means the located primary and authoritative PTC-specific manuals, technical reports, integration papers, and direct foundational publications needed to document PyPTC's current feature boundary. It does not mean every accelerator paper that happens to use or cite PTC. That corpus is too broad and is not a useful substitute for a systematic citation-index review. Follow-on application papers should be added when PyPTC documents a specific physical model that depends on them.

## Narrative

Forest, Schmidt, and McIntosh's 2002 report is the conceptual foundation. It describes PTC as a symplectic integrator and explains its polymorphic real/Taylor arithmetic and fibre-bundle representation of element frames and lattice topology. These ideas explain the parent library's broad design and why it can support tracking and map-based calculations. They do not establish which of those features the standalone PyPTC Python interface currently exposes. That boundary is determined by this repository's wrapper and ABI, not by the capabilities of PTC in general. The source report is bibliographically verified, but its official CERN direct-download endpoint returned an anti-bot HTML page to this environment; the PDF is therefore linked but not retained locally.

Forest and Schmidt's 2010 *PTC User's Reference Manual* is the direct manual found in this review. Its contents cover PTC state, geometry, tracking, and map-related routines. It is distinct from PyPTC's Python reference: readers should use the frozen Python wrapper and ABI to establish which operations this interface actually exposes.

The two 2006 ICAP contributions by Forest, Nogiwa, and Schmidt add useful implementation context. “The FPP and PTC Libraries” describes FPP as the polymorphic arithmetic foundation and summarizes PTC's beam/fibre structures. “The FPP Documentation” is a companion account of that dependency. These are primary author publications hosted in the KEK/JACoW proceedings archive and are retained locally. They are not API references for PyPTC.

Schmidt's 2005 PAC paper explains the MAD-X/PTC integration boundary: MAD-X and PTC are separate systems connected through lattice conversion and module interfaces. Skowronski, Schmidt, and Forest's 2007 PAC paper describes further MAD-X modules and examples of features accessible through that integration, including higher-order map and optics-related work. These papers are especially useful for distinguishing general PTC capability from capabilities made available through a particular wrapper. They are not evidence that PyPTC reproduces MAD-X command syntax or exposes each MAD-X PTC module.

The PTC User's Reference Manual by Forest and Schmidt is a direct user-level PTC source. The CERN-hosted PDF title page identifies the document as an October 2010 manual; the PDF is retained locally. It is distinct from the MAD-X PTC module reference commonly cited as a 2006 manual, which describes commands such as PTC_TWISS and PTC_TRACK. Its historical PDF URL currently serves the 2010 PTC User's Reference Manual, so the separate 2006 document was not retrieved. These manuals document their respective historical interfaces, not current PyPTC behavior or a guarantee of current MAD-X behavior.

Étienne Forest's book *From Tracking Code to Analysis* provides a later, deeper treatment of accelerator optics and generalized Courant-Snyder analysis. It is relevant theoretical context, but the publisher's book is not openly downloadable from the source located for this review; the DOI is recorded and no copy is included. It must not be used to infer meanings for PyPTC fields without tracing the implementation and obtaining physics review.

## Relevance to the PyPTC guide

The literature establishes the lineage and broad architectural ideas. PyPTC behavior is documented from the pinned Python implementation, `fortran/pyptc_api.f90`, the build script, examples, and recorded output artifacts. The technical note therefore labels code statements as implementation claims and leaves coordinate/physics meaning pending where code alone cannot settle it. A PTC capability described in literature is not counted as a PyPTC feature unless an exposed Python-to-ABI path is present.

## Bibliography and access status

Full structured entries are in [`references.bib`](references.bib). Download status, canonical URL, hash, and rights/access notes are in [`references/PDF_MANIFEST.csv`](references/PDF_MANIFEST.csv). The downloaded PDFs in this working documentation package are retained for research and internal documentation, with the source publication and access route recorded. Before redistribution, review the proceedings/publisher rights for each item.

| Source | Why it is included | Primary URL | Local PDF |
|---|---|---|---|
| Forest, Schmidt & McIntosh (2002), CERN-SL-2002-044 / KEK 2002-3 | Foundational PTC concepts, polymorphism, and fibre-bundle structure. | <https://cds.cern.ch/record/573082/files/sl-2002-044.pdf> | Not obtained: CERN anti-bot response. |
| Forest & Schmidt (2010), *PTC User's Reference Manual* | Direct reference for PTC state, geometry, and tracking routines. | <https://madx.web.cern.ch/doc/PTC_reference_manual.pdf> | `pdfs/forest_schmidt_ptc_users_reference_manual_2010.pdf` |
| Forest, Nogiwa & Schmidt (2006), “The FPP and PTC Libraries” | Author account of the FPP dependency and PTC structures. | <https://epaper.kek.jp/icap06/PAPERS/MOM1MP02.PDF> | `pdfs/forest_nogiwa_schmidt_fpp_ptc_2006.pdf` |
| Forest, Nogiwa & Schmidt (2006), “The FPP Documentation” | Companion source on FPP. | <https://accelconf.web.cern.ch/icap06/papers/WEPPP04.pdf> | `pdfs/forest_nogiwa_schmidt_fpp_documentation_2006.pdf` |
| Schmidt (2005), “MAD-X PTC Integration” | Explains separation and interface between MAD-X and PTC. | <https://proceedings.jacow.org/p05/papers/MPPE012.pdf> | `pdfs/schmidt_madx_ptc_integration_2005.pdf` |
| Skowronski, Schmidt & Forest (2007), “Advances in MAD-X using PTC” | Describes further MAD-X PTC modules and integration features. | <https://proceedings.jacow.org/p07/papers/THPAN070.pdf> | `pdfs/skowronski_schmidt_forest_madx_ptc_2007.pdf` |
| MAD-X PTC Documentation (2006) | Historical MAD-X module command reference. | <https://madx.web.cern.ch/doc/PTC_reference_manual.pdf> | Not separately obtained; the same URL served the 2010 PTC User's Reference Manual. |
| Forest (2016), *From Tracking Code to Analysis* | Extended theoretical treatment; publisher-restricted in the source located. | <https://doi.org/10.1007/978-4-431-55803-3> | Not downloaded. |

## Full citations and canonical URLs

The following entries provide the full bibliographic details in this Markdown review as well as in the machine-readable BibTeX file. URLs point to the publisher, proceedings, or institutional record used for this review.

1. Forest, É., Schmidt, F., and McIntosh, E. (2002). *Introduction to the Polymorphic Tracking Code: Fibre Bundles, Polymorphic Taylor Types and “Exact Tracking”*. CERN-SL-2002-044 (AP); KEK Report 2002-3, July 2002. CERN record and PDF URL: <https://cds.cern.ch/record/573082/files/sl-2002-044.pdf>. Local PDF: not obtained; see retrieval notes above and in the manifest.
2. Forest, E., Nogiwa, Y., and Schmidt, F. (2006). “The FPP and PTC Libraries.” In *Proceedings of the 8th International Computational Accelerator Physics Conference (ICAP 2006)*, Chamonix, France, pp. 17–21, paper MOM1MP02. PDF: <https://epaper.kek.jp/icap06/PAPERS/MOM1MP02.PDF>.
3. Forest, E., Nogiwa, Y., and Schmidt, F. (2006). “The FPP Documentation.” In *Proceedings of the 8th International Computational Accelerator Physics Conference (ICAP 2006)*, Chamonix, France, paper WEPPP04. PDF: <https://accelconf.web.cern.ch/icap06/papers/WEPPP04.pdf>.
4. Schmidt, F. (2005). “MAD-X PTC Integration.” In *Proceedings of the 21st IEEE Particle Accelerator Conference (PAC 2005)*, Knoxville, Tennessee, USA, pp. 1272–1274, paper MPPE012. DOI: <https://doi.org/10.1109/PAC.2005.1590731>. Proceedings PDF: <https://proceedings.jacow.org/p05/papers/MPPE012.pdf>.
5. Skowronski, P. K., Schmidt, F., and Forest, E. (2007). “Advances in MAD-X using PTC.” In *Proceedings of the 22nd IEEE Particle Accelerator Conference (PAC 2007)*, Albuquerque, New Mexico, USA, pp. 3381–3383, paper THPAN070. PDF: <https://proceedings.jacow.org/p07/papers/THPAN070.pdf>.
6. Forest, É., and Schmidt, F. (2010). *PTC User's Reference Manual*. CERN, BE Department, Geneva, Switzerland, October 15, 2010, 68 pp. PDF: <https://madx.web.cern.ch/doc/PTC_reference_manual.pdf>. The local PDF title page verifies this identity.
7. CERN MAD-X documentation (historically cited as 2006). *MAD-X PTC Reference Manual*. Historical URL: <https://madx.web.cern.ch/doc/PTC_reference_manual.pdf>. The URL currently serves the distinct 2010 PTC User's Reference Manual; publication details and the historical manual's separate source file remain unverified, so this is retained as a lead rather than treated as the downloaded document.
8. Forest, É. (2016). *From Tracking Code to Analysis: Generalised Courant-Snyder Theory for Any Accelerator Model*. Springer Japan. DOI and publisher record: <https://doi.org/10.1007/978-4-431-55803-3>. Full text not downloaded.

## Review limitations and actions

- The foundational 2002 report is not present locally even though it is the most important direct PTC reference. The immediate cause is the CERN download anti-bot page; the canonical URL and bibliographic identity remain recorded. A human may fetch it through an institutional browser if local retention is permitted.
- The PDF served from the old MAD-X PTC reference-manual URL is titled *PTC User's Reference Manual* and dated 2010, rather than the historical MAD-X PTC module manual commonly cited as 2006. Both identities and the URL collision are recorded; the historical module manual needs a better source URL.
- The available literature is historical. It does not replace checking the current PyPTC implementation, a current MAD-X release, or domain review.
- This review does not claim that PyPTC is scientifically validated for a particular ISIS RCS application; its benchmark work and evidence-gated review records remain separate.
