from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ITERATION_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ITERATION_DIR.parents[2]
FIXTURE_ROOT = REPO_ROOT / "test_outputs" / "admit-code-to-isis-rcs" / ".iteration-0002-test-fixtures"
SPEC = importlib.util.spec_from_file_location("fresh_admission", ITERATION_DIR / "admission_harness.py")
assert SPEC and SPEC.loader
admission = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(admission)


class AdmissionSkillTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if FIXTURE_ROOT.is_dir() and not any(FIXTURE_ROOT.iterdir()):
            FIXTURE_ROOT.rmdir()

    def test_documented_defaults_and_cli_overrides(self) -> None:
        defaults = admission.make_parser().parse_args([])
        self.assertEqual(defaults.snapshot_dir, admission.SNAPSHOT_DIR)
        self.assertEqual(defaults.library, admission.REPO_ROOT / "build_pyptc/libpyptc.so")
        selected = admission.make_parser().parse_args([
            "--snapshot-dir", "local-snapshot", "--output-root", "evidence",
            "--library", "libcustom.so", "--madx", "madx-custom", "--attempt-id", "attempt-explicit",
        ])
        self.assertEqual(selected.snapshot_dir, Path("local-snapshot"))
        self.assertEqual(selected.output_root, Path("evidence"))
        self.assertEqual(selected.library, Path("libcustom.so"))
        self.assertEqual(selected.madx, Path("madx-custom"))
        self.assertEqual(selected.attempt_id, "attempt-explicit")

    def test_dirty_or_wrong_revision_blocks_clean_checkout(self) -> None:
        admission.clean_checkout_gate("# branch.oid abc\n", "abc", "abc")
        with self.assertRaises(admission.AdmissionBlocked):
            admission.clean_checkout_gate("# branch.oid abc\n1 .M N... file\n", "abc", "abc")
        with self.assertRaises(admission.AdmissionBlocked):
            admission.clean_checkout_gate("# branch.oid abc\n", "abc", "def")

    def test_local_snapshot_is_hash_verified_and_files_only(self) -> None:
        snapshot = admission.validate_snapshot(admission.SNAPSHOT_DIR)
        self.assertEqual(snapshot["manifest"]["files_copied"], 5)
        self.assertFalse(snapshot["manifest"]["nested_git_metadata_copied"])
        self.assertEqual(tuple(snapshot["files"]), admission.REFERENCE_NAMES)
        self.assertFalse((admission.SNAPSHOT_DIR / ".git").exists())

    def test_approved_recipe_and_unapproved_changes(self) -> None:
        admission.validate_recipe(copy.deepcopy(admission.AUTHORIZED_RECIPE))
        self.assertEqual(len(re.findall(r"(?im)^\s*TWISS\s*,", admission.madx_recipe())), 1)
        mutations = {
            "overlay": lambda recipe: recipe.update(extra_overlay="unapproved.madx"),
            "wrapper": lambda recipe: recipe.update(wrapper="changed.madx"),
            "include order": lambda recipe: recipe.update(include_order=list(reversed(recipe["include_order"]))),
            "variant": lambda recipe: recipe.update(variant="other lattice"),
            "sequence": lambda recipe: recipe.update(sequence="other_sequence"),
        }
        for label, mutate in mutations.items():
            with self.subTest(change=label):
                recipe = copy.deepcopy(admission.AUTHORIZED_RECIPE)
                mutate(recipe)
                with self.assertRaises(admission.AdmissionBlocked):
                    admission.validate_recipe(recipe)

    def test_harmonic_and_trim_defaults_are_zero(self) -> None:
        evidence = admission.validate_strengths(admission.validate_snapshot(admission.SNAPSHOT_DIR)["files"])
        self.assertEqual(evidence["base_zero_assignments"]["kqtd"], 0.0)
        self.assertEqual(evidence["base_zero_assignments"]["kqtf"], 0.0)
        self.assertTrue(all(value == 0.0 for key, value in evidence["base_zero_assignments"].items() if key not in ("kqtd", "kqtf")))

    def test_tfs_fingerprint_ignores_only_volatile_headers(self) -> None:
        FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=FIXTURE_ROOT) as temp:
            a = Path(temp) / "a.tfs"
            b = Path(temp) / "b.tfs"
            a.write_text('@ TIME %s "2026-10-26T18:00:00"\n@ LENGTH %le 10.0\n* NAME S\n$ %s %le\n"Q1" 1.0\n')
            b.write_text('@ TIME %s "2026-10-26T18:01:00"\n@ LENGTH %le 10.0\n* NAME S\n$ %s %le\n"Q1" 1.0\n')
            self.assertEqual(admission.normalized_tfs_fingerprint(a), admission.normalized_tfs_fingerprint(b))

    def test_report_preserves_pending_review_and_warning_disposition(self) -> None:
        result = {
            "attempt_id": "attempt-test", "outcome": "admitted-snapshot", "ledger": "review_ledger.csv",
            "effective_command": "python run_admission.py", "recipe": admission.AUTHORIZED_RECIPE,
            "snapshot_scope": "This is snapshot-scoped evidence only and is not a clean-checkout result.",
            "skill": {"commit": admission.PINNED_SKILL_COMMIT, "sha256": admission.PINNED_SKILL_SHA256},
            "harness_validation": {"tests_run": 9, "log_path": "harness-tests.log", "log_sha256": "tests-hash"},
            "reference": {"mode": "working-copy-snapshot", "source_revision": "abc", "observed_checkout_revision": "def",
                          "dirty_entry_count": 1, "status_evidence": "status.txt", "status_sha256": "hash"},
            "target": {"repository_commit": "target", "runtime": "python", "numpy": "numpy", "library_sha256": "libhash",
                       "official_source": "origin", "installation_method": "build", "bootstrap_kind": "local",
                       "bootstrap": {"api_level": 4}, "api_definition": "pyptc/core.py", "bootstrap_log": "bootstrap.log", "structure": {}, "reference_particle": {}},
            "executed_calls": [], "smoke": {"pass": True},
            "warning_summary": {"madx": {"line_count": 1, "categories": {"implicit re-definition ignored": 1}},
                                "pyptc": {"line_count": 1, "relevant": ["DLMAX > LMAX"]},
                                "disposition": "unresolved for review",
                                "madx_log_path": "madx.log", "madx_log_sha256": "loghash",
                                "pyptc_log_path": "pyptc_runtime.log", "pyptc_log_sha256": "targethash"},
        }
        report = admission.render_report(result)
        self.assertIn("awaiting review", report)
        self.assertIn("DLMAX > LMAX", report)
        self.assertIn("Unresolved PyPTC runtime warning", report)
        self.assertIn("snapshot-scoped", report)
        self.assertIn("not a clean-checkout result", report)

    def test_runtime_warning_classification_covers_both_engines(self) -> None:
        summary = admission.classify_runtime_warnings(
            "++++++ warning: implicit element re-definition ignored: q1\n",
            "DLMAX > LMAX 0.51\nORBIT_WARNING 11\n",
        )
        self.assertEqual(summary["madx"]["line_count"], 1)
        self.assertEqual(summary["madx"]["categories"]["implicit element re-definition ignored"], 1)
        self.assertEqual(summary["pyptc"]["line_count"], 2)

    def test_blocked_run_does_not_change_review_ledger(self) -> None:
        ledger = admission.STEP_DIR / "review_ledger.csv"
        before = hashlib.sha256(ledger.read_bytes()).hexdigest()
        FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=FIXTURE_ROOT) as temp:
            root = Path(temp)
            code = admission.cli([
                "--snapshot-dir", str(root / "missing"), "--output-root", str(root / "runs"),
                "--attempt-id", "attempt-ledger-guard",
            ])
            self.assertNotEqual(code, 0)
            result = json.loads((root / "runs/attempt-ledger-guard/result.json").read_text())
            self.assertEqual(result["outcome"], "blocked")
            self.assertEqual(result["review_disposition"], "awaiting review")
        after = hashlib.sha256(ledger.read_bytes()).hexdigest()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
