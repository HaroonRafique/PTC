# PTC orbit-marker capability assessment

**Date:** 2026-10-27
**Scope:** Determine whether MAD-X element-exit sampling requires a PyPTC
Fortran change, a Python integration change, or neither.
**Related investigation:** [sampling-grid discrepancy report](sampling-grid-investigation-20261027.md)
**Outcome:** the PTC capability is already present and can be driven through
the existing Python wrapper; a Python-level helper is sufficient for this
benchmark. No Fortran change is indicated.

## Evidence inspected

The PTC source is from the current repository revision
`e295f2a2750f94abc2928b6f76d259a5d01c1d3b`. The probe used the admitted
PyPTC flat file and the same built PyPTC library as user-run
`attempt-20261027T145757Z`.

| Component | Evidence |
| --- | --- |
| PTC orbit-node construction | `source/Sq_orbit_ptc.f90`, SHA-256 `14258663c4813e37a50f8dca01ed25aa8b2fbdb964b182f42c70637dbe790f3a` |
| PTC command parsing | `source/St_pointers.f90`, SHA-256 `88a26abf50e463ecdb34ad1d3f8d29e7cff4b8e1d31bf91f559fe1515c40cf72` |
| PTC initialization interface | `interface/ptcinterface.f90`, SHA-256 `3e1da18115e7e8e31c6f52c69fbe8fc83e7ff432ff159e650a2bec7883042b0c` |
| PyPTC Fortran bindings | `PyPTC/fortran/pyptc_api.f90`, SHA-256 `6c8f4fb8f288abaf63de6731b4556bec4de7a668761a7dfe2fb095c38c700d4d` |
| PyPTC Python API | `PyPTC/pyptc/core.py`, SHA-256 `484939ccbbbf6d6cc218d5b3a97167bb6ddfd383878adf442ac49a90bcced571` |
| Loaded library | `PyPTC/build_pyptc/libpyptc.so`, SHA-256 `b388eeceaa24df26e67e8d397220818f4a8a48e7193f790e0cf3acffa65efe76` |

Relevant source links: [orbit layout builder](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/source/Sq_orbit_ptc.f90:1179), [PTC `SETORBITMARKER` command](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/source/St_pointers.f90:293), [PTC orbit-node printer](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/source/St_pointers.f90:463), [pre-orbit initialization hook](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/interface/ptcinterface.f90:38), [PyPTC `init_lattice` / `run_script`](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/pyptc/core.py:200), and [node-Twiss API](/home/hr/Codes/PTC_PyORBIT3_Codex_Merge_Jul26/PTC/PyPTC/pyptc/core.py:838).

## Existing PTC support

The PTC initialization routine checks the current working directory for a
file named `pre_orbit_set.txt` and reads it **before** `MAKE_NODE_LAYOUT` and
`ORBIT_MAKE_NODE_LAYOUT`. The PTC command parser supports:

```text
SETORBITMARKER
<number of names>
<fibre name 1>
...
<fibre name N>
return
```

The layout builder marks a node when the current integration node is at
`CASEP1` and its parent fibre name is in the configured `orbitname` list. The
existing LMAX-based orbit nodes are retained as well. This means the command
can add observations at named fibre exits without changing lattice strengths
or the splitting recipe.

After initialization, PTC's `PRINTORBITNODES` command writes each orbit node's
integration-node records, including longitudinal `S`, element name, fibre
position, and `CAS`. The checked-in PyPTC Python class already exposes
`run_script(path)` to invoke this PTC command. Python also has the ordered
fibre names and indices from `pyptc.lattice.read_flatfile_fibres()`. Together,
these features provide inputs to select and identify the desired report
locations.

The current high-level `all_node_twiss_orbit()` returns values by orbit-node
index and length, without adding the PTC printer's element identity fields.
The generic `PTC.init_lattice()` does not take a marker list as an argument.
Those are Python interface convenience gaps. They do not prevent a
benchmark-level Python helper from creating the pre-orbit command file,
initializing in an isolated working directory, invoking the existing printer,
and parsing node identity metadata.

## Bounded probe

The probe is implemented in
[`probe_orbit_marker_api.py`](probe_orbit_marker_api.py). It read the accepted
flat file, selected every distinct fibre name (516 names for 586 fibres),
wrote `pre_orbit_set.txt` in an isolated output directory, initialized the
existing PyPTC shared library from that directory, collected the PyPTC Twiss
rows, and invoked `PRINTORBITNODES` through `PTC.run_script()`.

The result is retained under
`test_outputs/benchmark-pyptc-linear-optics-against-madx/diagnostic-orbit-marker-probe/`:

| Check | Result |
| --- | ---: |
| Flat-file fibre boundaries | 586 |
| Distinct marker names requested | 516 |
| PyPTC orbit-node records after adding named exits | 804 |
| MAD-X distinct `s` positions represented by PyPTC | 563/563 |
| Fibre-end records matched by fibre index, name, and `s` within `1e-9 m` | 586/586 |
| Fibre-end identity/position misses | 0 |
| PyPTC tunes | `qx=0.31605467692091`, `qy=0.76510661554073` |

Probe code and output hashes:

| Artifact | SHA-256 |
| --- | --- |
| Python probe | `87eeef73af734ace2959f4ef6d141ceca14885b936c6124c9d846775363c3d81` |
| `pre_orbit_set.txt` | `f206c7970be35ce2f682af86a8ecdd6e5fced8bcb0e674a4eae0626b391af1dd` |
| `pyptc_marked_nodes.csv` | `66cd174bb44bdb40441da177cc8fa0645cd85b10bae52474bc2e294017887901` |
| `def_orbit_node.txt` | `8e46d786e84699a82e777cfc53ce35efd9208573dd74400aef616067c86da930` |
| `ptc-runtime.log` | `63362bac468046150c6a8822ed6c3543d33f1fc6ecc016e7c4554e4befa40748` |
| `summary.json` | `c0a11ab4bd56f030027031a02471be93022a2736242d41a1c195ef6c19976bc9` |

The 804-node list preserves LMAX-driven internal observations while adding the
named element exits. Parsing the last integration-node entry for each printed
orbit-node group recovered every flat-file fibre end by its one-based fibre
position, exact element name, and cumulative `s`. The 516-name selector
matched all 586 fibre records, including repeated names at different
positions. Thus position-only ambiguity at coincident MAD-X `s` values can be
resolved using the PTC fibre position and name already printed by PTC.

The tunes are identical to the unmarked user run. This supports the
interpretation that the probe changed reporting locations, not machine
strengths or reference state. This probe did **not** compute aligned profile
residuals or establish physics agreement.

## Python versus Fortran decision

For the benchmark's target grid—MAD-X element exits—the required node-selection
mechanism already exists in the PTC core and is reachable through the current
PyPTC wrapper's initialization and script interfaces. **No Fortran change is
needed.** The next benchmark iteration can add a Python helper that:

1. Reads fibre names from the admitted flat file and writes
   `pre_orbit_set.txt` in the attempt's private working directory.
2. Initializes PyPTC while that directory is current, so PTC consumes the
   pre-orbit settings before creating the orbit layout.
3. Collects all-node Twiss data and invokes `PRINTORBITNODES`.
4. Parses each orbit-node group into a metadata row containing orbit-node
   index, endpoint `s`, element name, fibre index/occurrence, and `CAS` side.
5. Joins the PyPTC element-exit samples to the MAD-X records by verified
   element identity, occurrence, `s`, and boundary side; retains remaining
   LMAX-internal PyPTC rows with their enclosing fibre identity.
6. Checks that each expected MAD-X fibre boundary has exactly one corresponding
   PyPTC sample, accounting explicitly for zero-length and repeated-position
   entries, before calculating any residuals.

Because the pre-orbit filename and PTC runtime are process-global, this helper
must initialize in an isolated per-attempt working directory and avoid
concurrent PTC initialization in one process. That is manageable in Python and
is already how an evidence-producing benchmark runner can isolate runs.

For the narrower goal of sampling at the **existing MAD-X element exits**, a
Python-level benchmark helper is sufficient. A future structured PyPTC API
could expose the existing selection and identity records directly, but that
would be optional convenience work rather than a prerequisite. Sampling at
arbitrary positions *inside* an unsplit fibre is different: the name selector
does not accept arbitrary `s`. That would require a separate validated
element-splitting or PTC-core design and is not required to compare against
MAD-X's 586 existing element exits.

## Disposition and publication evidence

This supersedes the earlier report's statement that the available Python API
alone lacked a verified full element map: the high-level array is unlabeled,
but PTC already supplies a selectable node grid and a printer carrying the
identity metadata. The remaining implementation work belongs in the
benchmark's Python orchestration/parsing layer. Preserve the probe as
diagnostic evidence; do not promote it to profile agreement or physics
acceptance.

This is an observational campaign finding for Task 6's prospective evidence
record and Task 9's event-driven `campaign_evidence_reviewed` maintenance in
the [evidence-gated agents publication plan, Task 6](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md:865)
and [Task 9](/home/hr/Repositories/isis-modelling-agents/docs/plans/2026-10-23-evidence-gated-agents-publication.md:1185).
The benchmark remains technically incomplete. No `REP-####`, shared
publication-repository update, skill revision, Fortran edit, or physics
acceptance is made by this investigation.
