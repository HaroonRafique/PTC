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
            if field == "overlay": changed["input_order"] = changed["input_order"] + [value]
            elif field == "wrapper": changed["wrapper"] = value
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
            "harness_tests":{"count":8,"log":"tests.log"},"ledger":"review_ledger.csv","executed_commands":{},"warnings":{}
        }
        report = module.build_report(sample)
        for phrase in ("awaiting review", "artifact_digests.csv", "not clean-checkout admission", "one MAD-X TWISS"):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
