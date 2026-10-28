import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("admission_0003", HERE / "admission_harness.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class SkillContractTests(unittest.TestCase):
    def test_defaults_and_overrides_are_exposed(self):
        defaults = module.parser().parse_args([])
        self.assertEqual(defaults.snapshot_dir, module.SNAPSHOT)
        self.assertEqual(defaults.library, module.ROOT / "build_pyptc/libpyptc.so")
        selected = module.parser().parse_args(["--snapshot-dir", "s", "--output-root", "o", "--library", "l", "--madx", "m", "--attempt-id", "a"])
        self.assertEqual((selected.snapshot_dir, selected.output_root, selected.library, selected.madx, selected.attempt_id),
                         (Path("s"), Path("o"), Path("l"), Path("m"), "a"))

    def test_missing_snapshot_has_actionable_blocked_error(self):
        with self.assertRaisesRegex(module.Blocked, "Authorized snapshot is missing"):
            module.copy_snapshot(Path("/definitely/missing"), Path("/tmp/no-write"))

    def test_approved_recipe_rejects_all_unapproved_departures(self):
        for field, value in (("overlay", "other.strength"), ("wrapper", "other.madx"),
                             ("input_order", list(reversed(module.FILES))), ("variant", "other"),
                             ("sequence", "other")):
            changed = copy.deepcopy(module.RECIPE)
            if field == "overlay": changed[field] = value
            elif field == "wrapper": changed[field] = value
            else: changed[field] = value
            with self.subTest(field=field), self.assertRaises(module.Blocked):
                module.validate_recipe(changed)

    def test_snapshot_copy_has_stable_ids_and_no_writes_to_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            out.mkdir()
            before = {n: module.digest(module.SNAPSHOT/n) for n in module.FILES}
            _, copied = module.copy_snapshot(module.SNAPSHOT, out)
            self.assertEqual(set(copied), {f"Lattice_Files/00_Simplified_Lattice/{n}" for n in module.FILES})
            self.assertEqual(before, {n: module.digest(module.SNAPSHOT/n) for n in module.FILES})
            self.assertEqual(copied["Lattice_Files/00_Simplified_Lattice/2023.strength"], module.digest(out/"snapshot_inputs/2023.strength"))

    def test_artifact_inventory_indexes_auxiliary_evidence_without_self_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/"diagnostics").mkdir()
            (root/"diagnostics/trace.jsonl").write_text("trace\n")
            (root/"warning_summary.json").write_text("{}\n")
            rows = module.inventory(root)
            indexed = {row["path"]: row for row in rows}
            self.assertIn("diagnostics/trace.jsonl", indexed)
            self.assertIn("warning_summary.json", indexed)
            self.assertNotIn("artifact_digests.csv", indexed)
            self.assertNotIn("manifest.json", indexed)
            self.assertEqual(indexed["diagnostics/trace.jsonl"]["sha256"], hashlib.sha256(b"trace\n").hexdigest())

    def test_build_method_and_executed_command_are_distinct_fields(self):
        command = module.command_record(["bash", "build/build_ptc.sh"], module.ROOT, 0, Path("build.log"))
        self.assertEqual(command["argv"], ["bash", "build/build_ptc.sh"])
        self.assertNotIn("library", command)

    def test_canonical_result_requires_resolved_defaults_and_duplicate_fields_fail(self):
        result = {"attempt_id":"a","outcome":"preflight-ok","review_disposition":"awaiting review","seed":None,
                  "output_path":"runs/a","reference":{"mode":"working-copy-snapshot","source_revision":"r","sequence":"synchrotron","variant":"v","input_hashes":{}},
                  "target":{},"recipe":{},"executed_commands":{}}
        module.validate_canonical_result(result)
        del result["reference"]["sequence"]
        with self.assertRaisesRegex(ValueError, "resolved reference default"):
            module.validate_canonical_result(result)
        with self.assertRaisesRegex(ValueError, "Duplicate final field"):
            module.parse_json_unique('{"outcome":"blocked","outcome":"admitted"}')

    def test_normalized_reference_fingerprint_ignores_only_time_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.tfs", Path(tmp)/"b.tfs"
            a.write_text('@ TIME %s "t1"\n@ DATE %s "d1"\n@ LENGTH %le 10.0\n* NAME\n')
            b.write_text('@ TIME %s "t2"\n@ DATE %s "d2"\n@ LENGTH %le 10.0\n* NAME\n')
            self.assertEqual(module.normalized_tfs_digest(a), module.normalized_tfs_digest(b))

    def test_review_rendering_requires_accepted_scope_and_preserves_it(self):
        row = {"disposition":"accepted","reviewer":"user","acceptance_scope":"snapshot admission only"}
        rendered = module.render_review_scope("Technical report", row)
        self.assertIn("snapshot admission only", rendered)
        with self.assertRaises(ValueError):
            module.render_review_scope("Technical report", {"disposition":"awaiting review"})

    def test_normal_runner_does_not_modify_reviewed_ledger(self):
        ledger = module.STEP / "review_ledger.csv"
        old = hashlib.sha256(ledger.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            code = module.cli(["--snapshot-dir", str(Path(tmp)/"missing"), "--output-root", str(Path(tmp)/"runs"), "--attempt-id", "attempt-negative"])
            self.assertNotEqual(code, 0)
        self.assertEqual(old, hashlib.sha256(ledger.read_bytes()).hexdigest())

    def test_report_contract_mentions_pending_review_inventory_and_nonclaims(self):
        sample = {
            "attempt_id":"a", "outcome":"admitted-snapshot", "attempt_class":"agent-diagnostic",
            "skill":{"commit":"c","sha256":"h"}, "reference":{"source_revision":"s","observed_revision":"o","dirty_entry_count":2,"status_path":"status.txt","command":{"argv":["madx"]},"log_path":"madx.log"},
            "recipe":module.RECIPE, "target":{"build_method":"build","library":"lib","library_sha256":"d","api_trace":"trace","runtime_log":"runtime","structure":{},"smoke":{}},
            "harness_tests":{"count":11,"log":"tests.log"},"ledger":"review_ledger.csv","executed_commands":{"madx":{"argv":["madx","input.madx"]}},"warnings":{}
        }
        report = module.build_report(sample)
        for phrase in ("awaiting review", "artifact_digests.csv", "not clean-checkout admission", "one MAD-X TWISS"):
            self.assertIn(phrase, report)
        self.assertIn('"input.madx"', report)


if __name__ == "__main__":
    unittest.main()
