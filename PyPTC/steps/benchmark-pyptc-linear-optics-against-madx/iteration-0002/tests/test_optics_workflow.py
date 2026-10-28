from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ITERATION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITERATION_DIR))
import isis_rcs_optics as optics


def fixture_rows(names: list[str], positions: list[float]) -> tuple[list[dict[str, str]], list[dict[str, float]], list[SimpleNamespace], list[dict[str, object]]]:
    reference = []
    target = []
    fibres = []
    groups = []
    for index, (name, s_value) in enumerate(zip(names, positions), start=1):
        reference.append({"NAME": name, "S": str(s_value), **{key: "0.0" for key in ("X", "PX", "Y", "PY", "BETX", "BETY", "ALFX", "ALFY", "DX", "DPX", "DY", "DPY", "MUX", "MUY")}})
        target.append({"node_index": index - 1, "length": s_value - (positions[index - 2] if index > 1 else 0.0), "s_exit_m": s_value, **{key: 0.0 for key in ("orbitx", "orbitpx", "orbity", "orbitpy", "betax", "betay", "alphax", "alphay", "etax", "etapx", "etay", "etapy", "mux", "muy")}})
        fibres.append(SimpleNamespace(index=index, name=name, length=s_value - (positions[index - 2] if index > 1 else 0.0)))
        groups.append({"node_index": index - 1, "terminal_record": {"s_m": s_value, "fibre_name": name, "fibre_position": index, "cas": 2}})
    return reference, target, fibres, groups


class BoundaryMappingTests(unittest.TestCase):
    def test_preserves_duplicate_s_and_zero_length_by_occurrence(self) -> None:
        reference, target, fibres, groups = fixture_rows(["START", "MARKER_A", "MARKER_B", "END"], [0.0, 1.0, 1.0, 2.0])
        mapping, summary = optics.build_verified_boundary_map(reference, target, fibres, groups)
        self.assertEqual(summary["status"], "verified")
        self.assertEqual(len(mapping), 4)
        self.assertEqual(mapping[1]["reference_s_m"], mapping[2]["reference_s_m"])
        self.assertEqual(mapping[1]["element_name"], "MARKER_A")
        self.assertEqual(mapping[2]["element_name"], "MARKER_B")
        self.assertTrue(summary["periodic_endpoint_included"])

    def test_rejects_position_only_or_entry_exit_shift(self) -> None:
        reference, target, fibres, groups = fixture_rows(["A", "B"], [1.0, 2.0])
        target[0]["s_exit_m"] = 0.5
        mapping, summary = optics.build_verified_boundary_map(reference, target, fibres, groups)
        self.assertEqual(summary["status"], "blocked")
        self.assertTrue(summary["failures"])
        self.assertEqual(len(mapping), 2)

    def test_missing_occurrence_is_blocked(self) -> None:
        reference, target, fibres, groups = fixture_rows(["DUP", "DUP"], [1.0, 2.0])
        groups[1]["terminal_record"]["fibre_position"] = 1
        _, summary = optics.build_verified_boundary_map(reference, target, fibres, groups)
        self.assertEqual(summary["status"], "blocked")


class ConventionTests(unittest.TestCase):
    def test_dispersion_and_derivatives_use_run_beta0(self) -> None:
        names = ["A"]
        reference, target, fibres, groups = fixture_rows(names, [1.0])
        for key in ("DX", "DPX", "DY", "DPY"):
            reference[0][key] = "2.0"
        for key in ("etax", "etapx", "etay", "etapy"):
            target[0][key] = 1.0
        mapping, summary = optics.build_verified_boundary_map(reference, target, fibres, groups)
        self.assertEqual(summary["status"], "verified")
        aligned, metrics = optics.align_profiles(mapping, reference, target, beta0=0.5)
        self.assertEqual(aligned[0]["reference_dx"], 1.0)
        self.assertEqual(aligned[0]["target_dx"], 1.0)
        self.assertEqual(aligned[0]["target_minus_reference_dx"], 0.0)
        self.assertEqual(len(metrics), len(optics.PROFILE_FIELDS))

    def test_madx_chromaticity_version_conversion(self) -> None:
        direct, factor = optics.converted_chromaticity_from_madx(3.0, 0.5, "DELTAP")
        self.assertEqual((direct, factor), (3.0, 1.0))
        converted, factor = optics.converted_chromaticity_from_madx(3.0, 0.5, "PT")
        self.assertEqual((converted, factor), (1.5, 0.5))
        unknown, factor = optics.converted_chromaticity_from_madx(3.0, 0.5, "unknown")
        self.assertIsNone(unknown)


class SourceAndPrinterTests(unittest.TestCase):
    def test_ptc_printer_keeps_node_identity_and_cas(self) -> None:
        text = """  Node Number            0
  Number of PTC Integration Nodes 2
  0.0 START 1 -1
  1.0 MAGNET 2 2
 ****************************************************
"""
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nodes.txt"
            path.write_text(text, encoding="utf-8")
            parsed = optics.parse_ptc_orbit_nodes(path)
        self.assertEqual(parsed[0]["node_index"], 0)
        self.assertEqual(parsed[0]["terminal_record"]["fibre_name"], "MAGNET")
        self.assertEqual(parsed[0]["terminal_record"]["fibre_position"], 2)
        self.assertEqual(parsed[0]["terminal_record"]["cas"], 2)

    def test_source_family_uses_sequence_and_element_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "ISIS.elements").write_text("""! DRIFTS
d0: drift, l=1;
! MAIN DIPOLE
dip: sbend, l=1;
! MAIN QUADRUPOLES
qf: quadrupole, l=1;
! TRIM QUADRUPOLES
qtd: quadrupole, l=1;
""", encoding="utf-8")
            (root / "ISIS.sequence").write_text("""ring: sequence, refer=exit, l=4;
sp_d: d0, at=1;
sp_b: dip, at=2;
sp_q: qf, at=3;
sp_t: qtd, at=4;
endsequence;
""", encoding="utf-8")
            families, info = optics.classify_source_families(root, ["sp_d", "sp_b", "sp_q", "sp_t"])
        self.assertEqual(families, {"sp_d": "drifts", "sp_b": "main dipoles", "sp_q": "main quadrupoles", "sp_t": "trim quadrupoles"})
        self.assertFalse(info["unmapped_names"])


if __name__ == "__main__":
    unittest.main()
