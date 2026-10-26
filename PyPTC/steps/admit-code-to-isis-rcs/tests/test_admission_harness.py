from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

STEP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STEP_DIR))

import run_admission as admission


class AdmissionHarnessTests(unittest.TestCase):
    def test_approved_recipe_has_overlay_after_base_strength_and_zero_defaults(self) -> None:
        recipe = admission.madx_script()
        positions = [recipe.index(f'CALL, FILE = "../reference_inputs/{name}";') for name in admission.REFERENCE_FILES]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("a1 := 0.0;", recipe)
        self.assertIn("b1 := 0.0;", recipe)
        self.assertIn("kqtd := 0.0;", recipe)
        self.assertIn("kqtf := 0.0;", recipe)
        self.assertIn("USE, SEQUENCE=synchrotron;", recipe)
        self.assertEqual(recipe.count("\nTWISS,"), 1)

    def test_strength_input_validation_requires_zero_harmonics_and_trims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ISIS.strength").write_text(
                "kqtd := 0.0;\nkqtf := 0.0;\n"
                "D7SIN=0.0;\nD7COS=0.0;\nD8SIN=0.0;\nD8COS=0.0;\n"
                "F8SIN=0.0;\nF8COS=0.0;\nF9SIN=0.0;\nF9COS=0.0;\n",
                encoding="utf-8",
            )
            (root / "2023.strength").write_text("qd_scale := 0.98;\n", encoding="utf-8")
            check = admission.validate_strength_inputs(root)
            self.assertEqual(check["base_trim_strengths"], {"kqtd": 0.0, "kqtf": 0.0})
            self.assertEqual(check["overlay_trim_assignments"], {"kqtd": None, "kqtf": None})

    def test_strength_input_validation_blocks_nonzero_overlay_trim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ISIS.strength").write_text(
                "kqtd := 0.0;\nkqtf := 0.0;\n"
                "D7SIN=0;\nD7COS=0;\nD8SIN=0;\nD8COS=0;\n"
                "F8SIN=0;\nF8COS=0;\nF9SIN=0;\nF9COS=0;\n",
                encoding="utf-8",
            )
            (root / "2023.strength").write_text("kqtd := 0.01;\n", encoding="utf-8")
            with self.assertRaises(admission.AdmissionBlocked):
                admission.validate_strength_inputs(root)

    def test_effective_strength_log_requires_every_harmonic_and_trim_to_be_zero(self) -> None:
        names = ["a1", "b1", "kqtd", "kqtf"]
        names += [f"kqtd_{index}" for index in range(10)]
        names += [f"kqtf_{index}" for index in range(10)]
        log_text = "\n".join(f"{name} = 0.0000000000000000E+00 ;" for name in names)
        values = admission.validate_effective_madx_strengths(log_text)
        self.assertEqual(len(values), 24)
        self.assertTrue(all(value == 0.0 for value in values.values()))
        with self.assertRaises(admission.AdmissionFailed):
            admission.validate_effective_madx_strengths(log_text.replace("kqtf_9 = 0.0000000000000000E+00 ;", "kqtf_9 = 1.0 ;"))

    def test_explicit_path_overrides_are_parsed(self) -> None:
        parsed = admission.parse_args([
            "--reference-repo", "/ref", "--library", "/lib.so",
            "--madx", "/madx", "--output-root", "/outputs", "--attempt-id", "trial-1",
        ])
        self.assertEqual(parsed.reference_repo, Path("/ref"))
        self.assertEqual(parsed.library, Path("/lib.so"))
        self.assertEqual(parsed.madx, Path("/madx"))
        self.assertEqual(parsed.output_root, Path("/outputs"))
        self.assertEqual(parsed.attempt_id, "trial-1")

    def test_missing_reference_writes_blocked_result_without_touching_review_ledger(self) -> None:
        ledger = STEP_DIR / "review_ledger.csv"
        original = ledger.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            args = SimpleNamespace(
                reference_repo=temporary_root / "missing-reference",
                library=admission.PYPTC_DIR / "build_pyptc" / "libpyptc.so",
                madx=admission.DEFAULT_MADX,
                output_root=temporary_root / "runs",
                attempt_id="blocked-test",
            )
            result, report_path, result_path = admission.run_admission(args)
            self.assertEqual(result["outcome"], "blocked")
            self.assertEqual(result["review_disposition"], "awaiting review")
            self.assertIn("Set ISIS_REFERENCE_REPO", result["failure"])
            self.assertTrue(report_path.is_file())
            self.assertTrue(result_path.is_file())
            self.assertIn("clean-checkout", report_path.read_text(encoding="utf-8"))
            canonical = json.loads(result_path.read_text(encoding="utf-8"))
            manifest = json.loads((report_path.parent / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(canonical["provenance"], manifest["provenance"])
            self.assertEqual(canonical["files"], manifest["files"])
        self.assertEqual(ledger.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
