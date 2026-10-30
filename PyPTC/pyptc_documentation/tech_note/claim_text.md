# Claim marker index for the rendered technical note

This index mirrors the claims marked in the LaTeX sections. It is the Markdown input to the ISIS evidence-skill checker; the LaTeX source carries the same identifiers beside reader-facing statements.

The package exports the public PTC class, lattice and parser helpers, and plotting utilities. [claim:API-01]

The build script configures and compiles the shared library, verifies exported names, and performs a ctypes load check. [claim:BUILD-01]

The default lattice resolves to the generated simplified flat file; the helper regenerates it when needed. [claim:LATTICE-01]

PTC construction loads the selected shared library, then lattice initialization forwards a resolved path to PTC. [claim:API-02] [claim:API-03]

Users can query tunes, chromaticities, node phase advances, and node optics/orbit values. [claim:API-04]

The source API includes initialization, optics, tracking, edits, apertures, and time-dependent controls. [claim:API-06]

The supported code path raises errors for invalid initialization, status, or input shape conditions. [claim:FAIL-01] [claim:FAIL-02]

The flat-file parser extracts fibre metadata and resolves element names to one-based indices, including numbered sliced dipoles. [claim:LATTICE-02]

The bare optics example writes plot, CSV, and JSON artifacts to its output directory. [claim:EXAMPLE-01]

The bunch example generates a 1000-particle input and requests 64 turns of diagnostics. [claim:EXAMPLE-02]

The bunch-array wrapper converts Python rows into internal PTC values and converts final values back; the physical coordinate interpretation remains under review. [claim:TRACK-01] [claim:TRACK-02]

The simple bunch tracker validates an N x 6 array, copies it, tracks through the machine nodes for the requested turns, and optionally retains per-turn snapshots. [claim:TRACK-03]

The JVT aperture reader divides semi-aperture column values by 1000 before constructing records. [claim:AP-01]

The EFIELD wrapper applies a defined subset of alignment and integrated multipole fields and rejects unsupported nonzero fields before application. [claim:API-05] [claim:ERR-01]

The physical units and signs of the EFIELD mapping await domain review. [claim:ERR-02]

One-turn-map and normal-form convenience calls raise the not-exposed exception; normalized aperture scan and tune-smear calls do as well. [claim:LIMIT-01] [claim:LIMIT-02]

PTC/FPP literature discusses wider capabilities than the current PyPTC wrapper establishes. [claim:LIT-01]

The working source basis is pinned to commit `8824003c956390e921a1d469f77c247859a63258` and hashed implementation files. [claim:PROV-01]

The copied plots match their source images by SHA-256; each figure supports only the named example context. [claim:PROV-03] [claim:PROV-04]

The physical meaning, unit convention, and validity range of returned optics/orbit values are not established by field names alone. [claim:PHYS-01]

The note and claims remain pending named code, physics, and reader review. [claim:PROV-02]

The presence of time-dependent control methods does not establish a reviewed ISIS RCS operating workflow. [claim:CONTROL-01]
