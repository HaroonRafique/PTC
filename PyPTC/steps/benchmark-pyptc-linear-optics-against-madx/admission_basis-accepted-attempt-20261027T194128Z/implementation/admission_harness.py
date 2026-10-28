#!/usr/bin/env python3
"""Run one auditable, snapshot-scoped PyPTC admission attempt."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEP = HERE.parent
ROOT = STEP.parents[1]
SNAPSHOT = STEP / "reference_snapshot"
SKILL_COMMIT = "97e63b1e4ef93aee07deacf09ad9592a223fffe6"
SKILL_SHA = "11c415652fcb053a8f5a2844ae93619ae37ae6dd74e471e67b8801c7b5dddd59"
FILES = ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence")
RECIPE = {
    "reference_mode": "working-copy-snapshot",
    "source_revision": "1bada6a2ab94edd426c52b7e97a5d335926e0646",
    "variant": "00_Simplified_Lattice with 2023.strength overlay",
    "sequence": "synchrotron",
    "overlay": "2023.strength",
    "wrapper": "attempt-local madx_work/admission_recipe.madx",
    "input_order": list(FILES),
    "settings": {"a1": 0.0, "b1": 0.0, "kqtd": 0.0, "kqtf": 0.0},
    "reference_calculation": "one MAD-X TWISS calculation",
    "ptc_support_scripts": ["resplit.ptc", "print_flat_file.ptc"],
    "authorization": "User instructions on 2026-10-26, restated in the step README and feedback 0001.",
}


class Blocked(Exception):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command_record(argv: list[str], cwd: Path, status: int, log: Path) -> dict:
    return {"argv": argv, "cwd": str(cwd), "returncode": status, "log": str(log)}


def select_attempt(output: Path) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"attempt-{now}"
    suffix = 2
    while (output / name).exists():
        name = f"attempt-{now}-{suffix:02d}"
        suffix += 1
    return name


def validate_recipe(candidate: dict) -> None:
    if candidate != RECIPE:
        raise Blocked("Reference recipe differs from the approved variant/order/overlay/sequence/settings.")


def parse_json_unique(text: str) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate final field in canonical record: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique)


def validate_canonical_result(result: dict) -> None:
    required = ("attempt_id", "outcome", "review_disposition", "seed", "output_path", "reference", "target", "recipe", "executed_commands")
    missing = [field for field in required if field not in result]
    if missing:
        raise ValueError(f"Canonical result omits resolved fields: {', '.join(missing)}")
    for field in ("mode", "source_revision", "sequence", "variant", "input_hashes"):
        if field not in result["reference"]:
            raise ValueError(f"Canonical result omits resolved reference default: {field}")


def normalized_tfs_digest(path: Path) -> str:
    stable = "\n".join(line for line in path.read_text(errors="replace").splitlines()
                         if not re.match(r"^@\s+(?:TIME|DATE)\b", line)) + "\n"
    return hashlib.sha256(stable.encode()).hexdigest()


def render_review_scope(technical_report: str, ledger_row: dict) -> str:
    if ledger_row.get("disposition") != "accepted" or not ledger_row.get("acceptance_scope"):
        raise ValueError("Review rendering requires an accepted ledger row with explicit scope.")
    return technical_report + f"\n## Reviewed disposition\n\nAccepted by {ledger_row.get('reviewer', 'unspecified reviewer')} for this scope only: {ledger_row['acceptance_scope']}\n"


def copy_snapshot(source: Path, bundle: Path) -> tuple[dict, dict[str, str]]:
    manifest_path = source / "source_manifest.json"
    if not manifest_path.is_file():
        raise Blocked(f"Authorized snapshot is missing: {manifest_path}")
    source_manifest = json.loads(manifest_path.read_text())
    info = source_manifest.get("reference_source", {})
    if (source_manifest.get("reference_mode") != RECIPE["reference_mode"]
            or info.get("materialized_revision") != RECIPE["source_revision"]
            or source_manifest.get("files_copied") != len(FILES)
            or source_manifest.get("nested_git_metadata_copied") is not False):
        raise Blocked("Snapshot identity or closure does not match the authorized recipe.")
    evidence = bundle / "reference_evidence"
    inputs = bundle / "snapshot_inputs"
    evidence.mkdir(parents=True)
    inputs.mkdir()
    status_src = source / info.get("checkout_status_evidence", "")
    if not status_src.is_file() or digest(status_src) != info.get("checkout_status_sha256"):
        raise Blocked("Snapshot dirty-state evidence is absent or fails its recorded digest.")
    shutil.copy2(status_src, evidence / "source_checkout_status.porcelain-v2.txt")
    shutil.copy2(manifest_path, evidence / "source_manifest.json")
    hashes = {}
    for name in FILES:
        logical = f"Lattice_Files/00_Simplified_Lattice/{name}"
        entry = source_manifest.get("input_files", {}).get(logical)
        origin = source / name
        if not entry or entry.get("local_path") != name or not origin.is_file() or digest(origin) != entry.get("sha256"):
            raise Blocked(f"Reference input missing or hash mismatch: {logical}")
        dest = inputs / name
        shutil.copy2(origin, dest)
        if digest(dest) != entry["sha256"]:
            raise Blocked(f"Copied input failed digest verification: {logical}")
        hashes[logical] = digest(dest)
    return source_manifest, hashes


def zero_state(inputs: Path) -> dict:
    assign = re.compile(r"^\s*([A-Za-z]\w*)\s*(?::=|=)\s*([-+0-9.eEdD]+)\s*;", re.M)
    base = {k.lower(): float(v.replace("D", "E").replace("d", "e"))
            for k, v in assign.findall((inputs / "ISIS.strength").read_text())}
    trim = {"kqtd": base.get("kqtd"), "kqtf": base.get("kqtf")}
    if any(v is None or v != 0 for v in trim.values()):
        raise Blocked(f"Input trim quadrupoles are not explicitly zero: {trim}")
    if any(abs(base.get(k, 0.0)) > 1e-12 for k in ("d7sin", "d7cos", "d8sin", "d8cos", "f8sin", "f8cos", "f9sin", "f9cos")):
        raise Blocked("Base strength file contains nonzero harmonic assignments.")
    return {"trim_strengths": trim, "harmonic_assignments": {k: base.get(k, 0.0) for k in
            ("d7sin", "d7cos", "d8sin", "d8cos", "f8sin", "f8cos", "f9sin", "f9cos")}}


def madx_input() -> str:
    calls = "\n".join(f'CALL, FILE="../snapshot_inputs/{name}";' for name in FILES)
    scripts = "\n".join(f'ptc_script, file="PTC_Scripts/{name}";' for name in RECIPE["ptc_support_scripts"])
    return f'''TITLE, "PyPTC admission iteration 0003";\n{calls}\na1=0; b1=0; kqtd=0; kqtf=0;\nUSE, SEQUENCE=synchrotron;\nVALUE, a1; VALUE, b1; VALUE, kqtd; VALUE, kqtf;\n'''+"\n".join(f"VALUE, {family}_{i};" for family in ("kqtd", "kqtf") for i in range(10))+f'''\nSELECT, FLAG=TWISS, CLEAR;\nSELECT, FLAG=TWISS, COLUMN=name, s, x, px, y, py, betx, bety, alfx, alfy;\nTWISS, SAVE, FILE="reference_twiss.tfs";\npropagation_method=2; order_of_integrator=6; integration_steps_per_element=5;\nptc_create_universe;\nptc_create_layout,time=true,model=propagation_method,exact=true,method=order_of_integrator,nst=integration_steps_per_element;\n{scripts}\nptc_end;\n'''


def run_command(argv: list[str], cwd: Path, log: Path, stdin: Path | None = None, timeout: int = 900) -> dict:
    with stdin.open("rb") if stdin else open(os.devnull, "rb") as input_stream:
        proc = subprocess.run(argv, cwd=cwd, stdin=input_stream, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout, check=False)
    log.write_bytes(proc.stdout)
    return command_record(argv, cwd, proc.returncode, log)


def inventory(bundle: Path) -> list[dict]:
    excluded = {"artifact_digests.csv", "manifest.json", "result.json", "report.md"}
    rows = []
    for path in sorted(p for p in bundle.rglob("*") if p.is_file() and p.name not in excluded):
        rel = path.relative_to(bundle).as_posix()
        rows.append({"path": rel, "role": artifact_role(rel), "sha256": digest(path)})
    with (bundle / "artifact_digests.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("path", "role", "sha256"))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def artifact_role(path: str) -> str:
    if path.startswith("snapshot_inputs/"): return "immutable reference input"
    if path.startswith("reference_evidence/"): return "snapshot provenance evidence"
    if "madx" in path.lower() or path.endswith((".madx", ".tfs", ".flt")): return "MAD-X recipe, trace, log, or output"
    if "pyptc" in path.lower() or "smoke" in path.lower(): return "PyPTC bootstrap, API trace, log, or smoke evidence"
    if "build" in path.lower(): return "PyPTC build evidence"
    if "test" in path.lower(): return "harness test evidence"
    return "attempt implementation or execution evidence"


def tfs_headers(path: Path) -> dict:
    headers = {}
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("@"):
            fields = line.split(maxsplit=3)
            if len(fields) == 4:
                value = fields[3].strip().strip('"')
                try:
                    value = float(value.replace("D", "E").replace("d", "e"))
                except ValueError:
                    pass
                headers[fields[1].upper()] = value
    return headers


def build_report(result: dict) -> str:
    r, t = result["reference"], result["target"]
    return f'''# PyPTC admission {result['attempt_id']}\n\n- Technical outcome: **{result['outcome']}**; external review: **awaiting review**.\n- Run class: {result['attempt_class']}.\n- Skill: `admit-code-to-isis-rcs` at `{result['skill']['commit']}`; SHA-256 `{result['skill']['sha256']}`.\n- Reference mode: `working-copy-snapshot`; input tree revision `{r['source_revision']}`; source checkout revision `{r['observed_revision']}` was dirty ({r['dirty_entry_count']} entries). Status evidence: `{r['status_path']}`.\n- Snapshot scope: exactly five copied files from the pinned source tree; no clean-checkout claim.\n- Recipe authorization: {result['recipe']['authorization']}\n- Variant/sequence: `{result['recipe']['variant']}` / `{result['recipe']['sequence']}`; include order: `{', '.join(result['recipe']['input_order'])}`. Settings: `a1=b1=kqtd=kqtf=0`; {result['recipe']['reference_calculation']}.\n- Exact commands executed: `{json.dumps(result['executed_commands'], sort_keys=True)}`. Build method: `{t['build_method']}`. Build invocation is separate; produced library `{t['library']}` SHA-256 `{t['library_sha256']}`.\n- Reference command: `{r['command']['argv']}`; raw log `{r['log_path']}`. Target API calls and runtime trace: `{t['api_trace']}`; raw runtime log `{t['runtime_log']}`.\n- Harness tests: {result['harness_tests']['count']} passed; `{result['harness_tests']['log']}`.\n- Structural checks: {json.dumps(t.get('structure', {}), sort_keys=True)}\n- Reference particle and smoke checks: {json.dumps(t.get('reference_particle', {}), sort_keys=True)}; {json.dumps(t.get('smoke', {}), sort_keys=True)}\n- Runtime warnings: {json.dumps(result.get('warnings', {}), sort_keys=True)}\n- Artifact digest inventory: [`artifact_digests.csv`](artifact_digests.csv), covering raw and derived supporting evidence, including auxiliary files and diagnostics. Inventory excludes itself and the report/manifest/result.\n- Reviewed ledger: `{result['ledger']}` (awaiting review).\n\nThis is technical evidence for the identified hashed snapshot only, not clean-checkout admission, optics validation, or benchmark agreement. It does not validate orbit, tunes, Twiss functions, dispersion, long-term tracking, or collective effects.\n'''


def run(args: argparse.Namespace) -> tuple[dict, Path]:
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    attempt = args.attempt_id or select_attempt(root)
    bundle = root / attempt
    if bundle.exists(): raise Blocked(f"Refusing to overwrite attempt bundle {bundle}")
    bundle.mkdir()
    for d in ("bootstrap", "madx_work/PTC_Scripts", "implementation"):
        (bundle / d).mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "admission_harness.py", bundle / "implementation/admission_harness.py")
    shutil.copy2(STEP / "run_admission.py", bundle / "implementation/run_admission.py")
    shutil.copytree(HERE / "tests", bundle / "implementation/tests")
    # Bootstrap PyPTC before reading or copying any ISIS lattice input.
    build_log = bundle / "bootstrap/build.log"
    build_argv = ["bash", "build/build_ptc.sh"]
    build_cmd = run_command(build_argv, ROOT, build_log, timeout=1200)
    if build_cmd["returncode"]: raise RuntimeError(f"PyPTC build failed: {build_log}")
    library = args.library.resolve()
    if not library.is_file(): raise Blocked(f"Build output library missing: {library}")
    retained_library = bundle / "bootstrap/libpyptc.so"
    shutil.copy2(library, retained_library)
    bootstrap_py = bundle / "bootstrap/library_probe.py"
    bootstrap_py.write_text("import json,sys; sys.path.insert(0,sys.argv[1]); from pyptc import PTC; p=PTC(sys.argv[2]); print(json.dumps({'library':p.library.resolve().as_posix(),'api_level':p.api_level()}))\n")
    bootstrap_log = bundle / "bootstrap/library_probe.log"
    boot_argv = [sys.executable, str(bootstrap_py), str(ROOT), str(retained_library)]
    boot_cmd = run_command(boot_argv, ROOT, bootstrap_log)
    if boot_cmd["returncode"]: raise RuntimeError(f"No-lattice PyPTC bootstrap failed: {bootstrap_log}")
    bootstrap = json.loads(bootstrap_log.read_text().splitlines()[-1])
    if Path(bootstrap["library"]).resolve() != retained_library.resolve():
        raise RuntimeError(f"PyPTC loaded unexpected library {bootstrap['library']}; expected {retained_library}")

    src_manifest, input_hashes = copy_snapshot(args.snapshot_dir.resolve(), bundle)
    validate_recipe(RECIPE)
    zero = zero_state(bundle / "snapshot_inputs")
    for name in RECIPE["ptc_support_scripts"]:
        shutil.copy2(ROOT / "workflows/madx/ptc_scripts" / name, bundle / "madx_work/PTC_Scripts" / name)
    test_log = bundle / "harness-tests.log"
    test_argv = [sys.executable, "-m", "unittest", "discover", "-s", str(HERE / "tests"), "-v"]
    test_cmd = run_command(test_argv, ROOT, test_log)
    if test_cmd["returncode"]:
        raise RuntimeError(f"Iteration 0003 harness tests failed: {test_log}")

    madx = args.madx.resolve()
    if not madx.is_file() or not os.access(madx, os.X_OK): raise Blocked(f"MAD-X binary unavailable: {madx}")
    recipe_file = bundle / "madx_work/admission_recipe.madx"
    recipe_file.write_text(madx_input())
    if len(re.findall(r"(?im)^\s*TWISS\s*,", recipe_file.read_text())) != 1:
        raise Blocked("Recipe does not contain exactly one TWISS call.")
    madx_log = bundle / "madx_work/madx.log"
    madx_cmd = run_command([str(madx)], bundle / "madx_work", madx_log, stdin=recipe_file, timeout=180)
    twiss, flat = bundle / "madx_work/reference_twiss.tfs", bundle / "madx_work/PTC-PyORBIT_flat_file.flt"
    if madx_cmd["returncode"] or not twiss.is_file() or not flat.is_file():
        raise RuntimeError(f"MAD-X did not produce reference TFS and flat file; see {madx_log}")

    api_script = bundle / "pyptc_admission_smoke.py"
    api_script.write_text('''import json, math, sys\nsys.path.insert(0, sys.argv[1])\nfrom pyptc import PTC, read_flatfile_fibres\ntrace=[]\ndef call(name, fn, *args):\n    value=fn(*args)\n    trace.append({"call":name,"arguments":[str(x) for x in args],"return":value})\n    return value\np=PTC(sys.argv[2]); call("PTC.init_lattice",p.init_lattice,sys.argv[3]); structure=call("PTC.machine_summary",p.machine_summary); fibres=read_flatfile_fibres(sys.argv[3]); trace.append({"call":"read_flatfile_fibres","arguments":[sys.argv[3]],"return_count":len(fibres)});\nscalars={n:call("PTC.scalar:"+s,p.scalar,s) for n,s in {"p0c_gev_c":"ptc_get_p0c_","beta0":"ptc_get_beta0_","kinetic_gev":"ptc_get_kinetic_"}.items()};\ninitial=[0.0]*6; coords,loss=call("PTC.track_particle_ptc_with_loss",p.track_particle_ptc_with_loss,initial,1); print(json.dumps({"library":str(p.library.resolve()),"api_level":p.api_level(),"structure":structure,"fibre_count":len(fibres),"scalars":scalars,"initial":initial,"final":[float(x) for x in coords],"loss":loss,"finite":all(math.isfinite(float(x)) for x in coords),"executed_api_trace":trace},default=str))\n''')
    runtime_log = bundle / "pyptc_runtime.log"
    api_argv = [sys.executable, str(api_script), str(ROOT), str(retained_library), str(flat)]
    api_cmd = run_command(api_argv, ROOT, runtime_log)
    if api_cmd["returncode"]: raise RuntimeError(f"PyPTC admission API failed: {runtime_log}")
    api = json.loads(runtime_log.read_text().splitlines()[-1])
    if not api["finite"] or api["loss"].get("lost"):
        raise RuntimeError("One-turn zero-offset particle smoke failed finite/no-loss policy.")
    headers = tfs_headers(twiss)
    pc_ref, length_ref = float(headers["PC"]), float(headers["LENGTH"])
    pc_target = float(api["scalars"]["p0c_gev_c"])
    length_target = float(api["structure"]["circumference_m"])
    if abs(pc_target - pc_ref) > 2e-7:
        raise RuntimeError(f"Reference momentum mismatch: MAD-X={pc_ref}, PyPTC={pc_target} GeV/c")
    if abs(length_target - length_ref) > 1e-6:
        raise RuntimeError(f"Circumference mismatch: MAD-X={length_ref}, PyPTC={length_target} m")
    mass_ref = float(headers["MASS"])
    gamma_ref = (1.0 + (pc_ref / mass_ref) ** 2) ** 0.5
    beta_ref = pc_ref / (mass_ref * gamma_ref)
    kinetic_ref = (pc_ref * pc_ref + mass_ref * mass_ref) ** 0.5 - mass_ref
    beta_delta = float(api["scalars"]["beta0"]) - beta_ref
    kinetic_delta = float(api["scalars"]["kinetic_gev"]) - kinetic_ref
    if abs(beta_delta) > 2e-6 or abs(kinetic_delta) > 2e-6:
        raise RuntimeError("PyPTC beta or kinetic energy is inconsistent with the MAD-X reference particle.")
    particle_record = {"madx_p0c_gev_c":pc_ref,"pyptc_p0c_gev_c":pc_target,"difference_gev_c":pc_target-pc_ref,"tolerance_gev_c":2e-7,
                       "mass_gev":mass_ref,"madx_beta":beta_ref,"pyptc_beta":api["scalars"]["beta0"],"beta_difference":beta_delta,
                       "madx_kinetic_gev":kinetic_ref,"pyptc_kinetic_gev":api["scalars"]["kinetic_gev"],"kinetic_difference_gev":kinetic_delta,
                       "madx_circumference_m":length_ref,"pyptc_circumference_m":length_target,"circumference_tolerance_m":1e-6}
    twiss_text = twiss.read_text(errors="replace")
    madx_warning_lines = [x.strip() for x in madx_log.read_text(errors="replace").splitlines() if re.search(r"^\+*\s*warning\s*:", x, re.I)]
    pyptc_warning_lines = [x.strip() for x in runtime_log.read_text(errors="replace").splitlines() if re.search(r"warning|error|dlmax|localize", x, re.I)]
    warning_categories = {}
    for line in madx_warning_lines:
        label = "implicit element re-definition ignored" if "re-definition" in line.lower() else line.split(":", 1)[-1].strip()
        warning_categories[label] = warning_categories.get(label, 0) + 1
    warnings = {"madx": {"count":len(madx_warning_lines),"categories":warning_categories,"examples":list(dict.fromkeys(madx_warning_lines))[:5]},
                "pyptc": {"count":len(pyptc_warning_lines),"unresolved":list(dict.fromkeys(pyptc_warning_lines))},
                "disposition": "MAD-X duplicate-definition warnings retained and classified; PyPTC cavity/localization/LMAX warnings remain unresolved for external review. Warning presence alone is not treated as a blocker."}
    record = json.loads((bundle / "reference_evidence/source_manifest.json").read_text())
    src = record["reference_source"]
    target_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    result = {
        "attempt_id": attempt, "output_path": str(bundle.resolve()),
        "attempt_class": "agent-diagnostic; not the user-run skill-test attempt" if os.getenv("PYPTC_ADMISSION_RUN_CLASS") == "agent-diagnostic" else "user-run skill-test attempt",
        "skill_iteration": "iteration-0003", "skill": {"name":"admit-code-to-isis-rcs","commit":SKILL_COMMIT,"sha256":SKILL_SHA},
        "outcome": "admitted-snapshot", "review_disposition": "awaiting review",
        "ledger": "steps/admit-code-to-isis-rcs/review_ledger.csv", "effective_command": " ".join([sys.executable,*sys.argv]), "seed": None,
        "recipe": RECIPE, "harness_tests": {"count": int(re.search(r"Ran (\d+) tests?", test_log.read_text()).group(1)), "command": test_cmd, "log":"harness-tests.log"},
        "executed_commands": {"entrypoint": {"argv":[sys.executable,*sys.argv],"cwd":str(Path.cwd()),"returncode":0,"log":None}, "harness_tests": test_cmd,"build":build_cmd,"bootstrap":boot_cmd,"madx":madx_cmd,"pyptc":api_cmd},
        "reference": {"mode":"working-copy-snapshot","source_revision":src["materialized_revision"],"observed_revision":src["checkout_revision_at_copy"],"dirty_entry_count":src["checkout_status_entry_count"],"status_path":"reference_evidence/source_checkout_status.porcelain-v2.txt","status_sha256":digest(bundle/"reference_evidence/source_checkout_status.porcelain-v2.txt"),"snapshot_manifest":"reference_evidence/source_manifest.json","input_hashes":input_hashes,"variant":RECIPE["variant"],"sequence":RECIPE["sequence"],"machine_settings":zero,"recipe_path":"madx_work/admission_recipe.madx","recipe_sha256":digest(recipe_file),"command":madx_cmd,"log_path":"madx_work/madx.log","log_sha256":digest(madx_log),"output":"madx_work/reference_twiss.tfs","output_sha256":digest(twiss),"normalized_output_sha256":normalized_tfs_digest(twiss),"normalization":"SHA-256 after removing TFS @TIME and @DATE header rows","flat_file":"madx_work/PTC-PyORBIT_flat_file.flt","flat_file_sha256":digest(flat),"binary":str(madx),"binary_sha256":digest(madx)},
        "target": {"repository_commit":target_commit,"official_source":subprocess.run(["git","config","--get","remote.origin.url"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip(),"runtime":sys.version,"numpy":importlib.metadata.version("numpy"),"installation_method":"The repository build script compiles libpyptc.so using Meson.","build_method":"bash build/build_ptc.sh","build_command":build_cmd,"build_output_library":str(library),"build_output_library_sha256":digest(library),"library":"bootstrap/libpyptc.so","library_sha256":digest(retained_library),"bootstrap":bootstrap,"bootstrap_command":boot_cmd,"runtime_log":"pyptc_runtime.log","runtime_log_sha256":digest(runtime_log),"api_trace":"Executed call trace in pyptc_runtime.log; instrumented by pyptc_admission_smoke.py.","api_trace_sha256":digest(runtime_log),"api_script_sha256":digest(api_script),"structure":api["structure"],"fibre_count":api["fibre_count"],"reference_particle":particle_record,"smoke":{"initial":api["initial"],"final":api["final"],"turns":1,"loss":api["loss"],"finite":api["finite"],"loss_policy":"Any reported loss or non-finite final coordinate fails."}},
        "warnings":warnings,"nonclaims":["No orbit, tunes, Twiss agreement, dispersion, long-term stability, collective effects, or benchmark validation."],
    }
    result["artifact_inventory"] = "artifact_digests.csv"
    result["artifact_digests"] = inventory(bundle)
    validate_canonical_result(result)
    (bundle/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    (bundle/"manifest.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    (bundle/"report.md").write_text(build_report(result))
    return result,bundle


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot-dir",type=Path,default=SNAPSHOT)
    p.add_argument("--output-root",type=Path,default=ROOT/"test_outputs/admit-code-to-isis-rcs")
    p.add_argument("--library",type=Path,default=ROOT/"build_pyptc/libpyptc.so")
    p.add_argument("--madx",type=Path,default=ROOT/"workflows/madx/bin/madx-linux64_v5_02_00")
    p.add_argument("--attempt-id")
    return p


def cli(argv: list[str] | None=None) -> int:
    args=parser().parse_args(argv)
    if args.attempt_id is None:
        args.attempt_id=select_attempt(args.output_root.resolve())
    try:
        result,bundle=run(args)
    except Blocked as exc:
        print(f"blocked: {exc}",file=sys.stderr); return 2
    except (OSError,RuntimeError,ValueError,KeyError,json.JSONDecodeError,subprocess.SubprocessError) as exc:
        print(f"failed: {exc}",file=sys.stderr); return 1
    print(f"Technical outcome: {result['outcome']} (pending external review)")
    print(f"Report: {bundle/'report.md'}")
    print(f"Canonical result: {bundle/'result.json'}")
    print(f"Manifest: {bundle/'manifest.json'}")
    return 0


if __name__ == "__main__": raise SystemExit(cli())
