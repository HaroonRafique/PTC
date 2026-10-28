"""Deterministic checks for the iteration-0004 case inventory contract."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

step_dir = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(step_dir / "scripts/python"))
import benchmark_pyptc as workflow


class CaseInventoryTests(unittest.TestCase):
    def test_every_candidate_has_a_skill_valid_disposition_and_evidence(self) -> None:
        cases = workflow.campaign_case_catalog()
        self.assertEqual(len(cases), 38)
        self.assertEqual(len({case["case_id"] for case in cases}), 38)
        allowed = {"included", "not-applicable", "unsupported", "blocked"}
        for case in cases:
            with self.subTest(case=case["case_id"]):
                self.assertIn(case["disposition"], allowed)
                self.assertTrue(case["source_identity"])
                self.assertTrue(case["reason"])
                self.assertTrue(case["evidence"])
                self.assertTrue(case["reference_application_status"])
                self.assertTrue(case["target_application_status"])

    def test_supported_case_families_are_included_for_execution(self) -> None:
        cases = workflow.campaign_case_catalog()
        included = [case["case_id"] for case in cases if case["disposition"] == "included"]
        unsupported = [case for case in cases if case["disposition"] == "unsupported"]
        self.assertEqual(len(included), 37)
        self.assertEqual(included[0], "nominal")
        self.assertEqual(sum(case.get("kind") == "corrector" for case in cases if case["disposition"] == "included"), 28)
        self.assertEqual(sum(case.get("kind") == "field-error" for case in cases if case["disposition"] == "included"), 1)
        self.assertEqual(sum(case.get("kind") == "misalignment" for case in cases if case["disposition"] == "included"), 6)
        self.assertEqual(sum(case.get("case_id") == "survey_error_table_verified_intersection" for case in cases if case["disposition"] == "included"), 1)
        self.assertEqual([case["case_id"] for case in unsupported], ["survey_error_table"])
        self.assertIn("unsupported", unsupported[0]["target_application_status"])

    def test_corrector_strength_is_materialized_in_a_case_local_input_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            for name in ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"):
                (snapshot / name).write_text("sentinel\n", encoding="utf-8")
            strength = snapshot / "ISIS.strength"
            strength.write_text("r0hd1_kick:=0.0;\nother:=5;\n", encoding="utf-8")
            case_dir = root / "cases/corrector_sp0_r0hd1_plus_1mrad"
            case = next(case for case in workflow.campaign_case_catalog() if case["case_id"] == "corrector_sp0_r0hd1_plus_1mrad")
            case_input = workflow.materialize_case_input(snapshot, case, case_dir)
            self.assertIn("r0hd1_kick:=0.001;", (case_input / "ISIS.strength").read_text(encoding="utf-8"))
            self.assertIn("other:=5;", (case_input / "ISIS.strength").read_text(encoding="utf-8"))
            self.assertEqual(strength.read_text(encoding="utf-8"), "r0hd1_kick:=0.0;\nother:=5;\n")

    def test_isolated_misalignment_table_contains_only_the_declared_component(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "survey.tfs"
            destination = root / "isolated.tfs"
            source.write_text(
                "@ TYPE %06s \"EFIELD\"\n"
                "* NAME K0L DX DY DS DPHI DTHETA DPSI\n"
                "$ %s %le %le %le %le %le %le %le\n"
                "SP0_QF 1.5 0 0 0 0 0 0\n"
                "SP1_QF 2.5 0.1 0.2 0.3 0.4 0.5 0.6\n",
                encoding="utf-8",
            )
            case = next(case for case in workflow.campaign_case_catalog() if case["case_id"] == "sp0_qf_dx")
            audit = workflow.materialize_case_error_table(case, source, destination)
            self.assertEqual(audit["selected_row_count"], 1)
            data = [line.split() for line in destination.read_text(encoding="utf-8").splitlines() if line.startswith(("SP0", "SP1"))]
            self.assertEqual(float(data[0][2]), 1.0e-3)
            self.assertEqual([float(value) for value in data[0][1:2] + data[0][3:]], [0.0] * 6)
            self.assertEqual([float(value) for value in data[1][1:]], [0.0] * 7)

    def test_verified_intersection_keeps_alignment_fields_and_zeros_field_terms(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "survey.tfs"
            destination = root / "intersection.tfs"
            source.write_text(
                "* NAME K0L DX DY DS DPHI DTHETA DPSI\n"
                "$ %s %le %le %le %le %le %le %le\n"
                "SP0_QF 1.5 0.1 0.2 0.3 0.4 0.5 0.6\n",
                encoding="utf-8",
            )
            case = next(case for case in workflow.campaign_case_catalog() if case["case_id"] == "survey_error_table_verified_intersection")
            workflow.materialize_case_error_table(case, source, destination)
            data = [line.split() for line in destination.read_text(encoding="utf-8").splitlines() if line.startswith("SP0")][0]
            self.assertEqual(float(data[1]), 0.0)
            self.assertEqual([float(value) for value in data[2:]], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

    def test_serialized_records_keep_disposition_and_per_engine_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            inventory = workflow.write_case_catalog(Path(temporary))
            self.assertEqual(inventory["case_count"], 38)
            self.assertEqual(len(inventory["dispositions"]["unsupported"]), 1)
            case_path = Path(temporary) / "cases/survey_error_table/case_status.json"
            status = json.loads(case_path.read_text(encoding="utf-8"))
            self.assertEqual(status["disposition"], "unsupported")
            self.assertEqual(status["reference_application_status"], "not-run")
            self.assertIn("unsupported", status["target_application_status"])
            self.assertEqual(status["plot_status"], "not-produced")

    def test_nominal_subtracted_response_retains_both_engine_responses(self) -> None:
        nominal = [{"element_name": "QF", "element_occurrence": 1, "fibre_index": 4, "reference_s_m": 1.0, "target_s_m": 1.0}]
        perturbed = [{"element_name": "QF", "element_occurrence": 1, "fibre_index": 4, "reference_s_m": 1.0, "target_s_m": 1.0}]
        for observable in workflow.optics.PROFILE_FIELDS:
            nominal[0][f"reference_{observable}"] = 2.0
            nominal[0][f"target_{observable}"] = 3.0
            perturbed[0][f"reference_{observable}"] = 4.0
            perturbed[0][f"target_{observable}"] = 7.0
        response_rows, metrics = workflow.nominal_subtracted_responses(nominal, perturbed, "fixture")
        self.assertEqual(response_rows[0]["reference_response_x"], 2.0)
        self.assertEqual(response_rows[0]["target_response_x"], 4.0)
        self.assertEqual(response_rows[0]["response_residual_x"], 2.0)
        self.assertEqual(len(metrics), len(workflow.optics.PROFILE_FIELDS))

    def test_scalar_response_is_engine_specific_and_native_chromaticity_stays_blocked(self) -> None:
        nominal = [
            {"observable": "bare_horizontal_tune", "reference": 0.25, "target": 0.26, "units": "tune units"},
            {"observable": "bare_horizontal_chromaticity", "reference_native": -2.0, "target_native": -3.0},
        ]
        perturbed = [
            {"observable": "bare_horizontal_tune", "reference": 0.27, "target": 0.29, "units": "tune units"},
            {"observable": "bare_horizontal_chromaticity", "reference_native": -2.1, "target_native": -3.2},
        ]
        rows = workflow.nominal_subtracted_scalar_responses(nominal, perturbed, "fixture")
        tune = rows[0]
        chromaticity = rows[1]
        self.assertAlmostEqual(tune["reference_response"], 0.02)
        self.assertAlmostEqual(tune["target_response"], 0.03)
        self.assertAlmostEqual(tune["response_residual"], 0.01)
        self.assertIsNone(chromaticity["response_residual"])
        self.assertIn("blocked", chromaticity["classification"])


if __name__ == "__main__":
    unittest.main()
