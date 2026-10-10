"""F02 QRT × blueprint contract falsifiers: green source structure is NOT academic acceptance."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "TEST/imo-research/candidates/check_f02_qrt_blueprint_contract.py"
spec = importlib.util.spec_from_file_location("f02_contract", MODULE_PATH)
f02 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = f02
spec.loader.exec_module(f02)


class TestF02QRTBlueprintContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = f02.read_json(f02.PACKAGE)
        cls.manifest = f02.read_json(f02.MANIFEST)
        cls.matrix = f02.read_json(f02.qrt.MATRIX_PATH)
        cls.vocab = f02.read_json(f02.qrt.VOCAB_PATH)
        cls.blueprints = f02.read_json(f02.BLUEPRINTS)
        cls.goldens = [
            f02.read_json(f02.ROOT / "TEST/imo-research/golden" / n)
            for n in f02.GOLDEN_NAMES
        ]

    def audit(self, package=None, manifest=None, matrix=None, blueprints=None, goldens=None):
        return f02.audit(
            copy.deepcopy(package if package is not None else self.package),
            copy.deepcopy(manifest if manifest is not None else self.manifest),
            copy.deepcopy(matrix if matrix is not None else self.matrix),
            copy.deepcopy(self.vocab),
            copy.deepcopy(blueprints if blueprints is not None else self.blueprints),
            copy.deepcopy(goldens if goldens is not None else self.goldens),
        )

    def test_selected_item_is_one_model_d3_and_three_goldens_are_reviewer_only(self):
        result = self.audit()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["selected_cell"], "QRT-MODEL-D3")
        self.assertEqual(result["rendered_coverage_cells"], ["QRT-MODEL-D3"])
        self.assertEqual(result["golden_reference_cells"], list(f02.EXPECTED_CELLS))
        self.assertEqual(result["crux_move_ref"], "MOVE-IMO-R1-FACTOR")
        self.assertIn("4t", result["protected_W"])
        self.assertEqual(result["academic_status"], "HOLD_NOT_ACCEPTED")

    def test_semantic_asks_do_not_collapse_into_mechanical_pass(self):
        result = self.audit()
        self.assertEqual([a["ask"] for a in result["semantic_review_asks"]], list(f02.qrt.ASKS))
        self.assertTrue(all(a["status"] != "PASS" for a in result["semantic_review_asks"]))
        self.assertTrue(all("source_pointers" in a for a in result["semantic_review_asks"]))
        diagnostic = next(a for a in result["semantic_review_asks"] if a["ask"] == "M2")
        self.assertEqual(diagnostic["source_pointers"],
                         ["microtopics[0].extensions.grade9v3:concept_checkpoint.diagnostic"])
        self.assertEqual(diagnostic["status"], "STRUCTURED_RESPONSE_PATTERNS_COGNITIVE_CAUSE_UNVERIFIED")
        self.assertIn("M2_CAUSAL_MISCONCEPTION_VS_EXECUTION_SLIP_NOT_VERIFIED",
                      result["review_gates"])
        self.assertEqual(
            [s["stage"] for s in result["core1a_repair_reference_alignment"]],
            list(f02.REPAIR_STAGES),
        )
        self.assertEqual(
            result["core1a_repair_reference_alignment"][-1]["status"],
            "PROMPT_PRESENT_UNASSISTED_RETURN_NOT_ENFORCED",
        )
        self.assertIn("FRESH_UNASSISTED_POST_REPAIR_RETURN_NOT_ENFORCED", result["review_gates"])
        self.assertIn("FREE_TEXT_REASON_MATHEMATICAL_CORRECTNESS_NOT_GRADED", result["review_gates"])

    def test_actual_role_blueprints_have_required_slot_sources_not_acceptance(self):
        result = self.audit()
        names = {(x["role"], x["slot"]) for x in result["blueprint_required_slots"]}
        self.assertEqual(names, {
            ("CORE1A", "identity"), ("CORE1A", "construction"),
            ("CORE1A", "repair_closure"), ("CORE2A", "identity"),
            ("CORE2A", "attempt"), ("CORE2A", "reasoning"),
        })
        self.assertTrue(all("UNVERIFIED" in x["status"] for x in result["blueprint_required_slots"]))

    def test_neutral_counterexample_is_distinct_and_not_a_mastery_verdict(self):
        pkg = self.package
        diagnostic = pkg["microtopics"][0]["extensions"]["grade9v3:concept_checkpoint"]["diagnostic"]
        self.assertEqual((diagnostic["base"], diagnostic["exponent"]), (7, 2))
        self.assertEqual(diagnostic["status"], "LOCAL_STRUCTURED_NUMERICAL_PATTERN_NOT_MASTERY")
        self.assertEqual((7 ** 3, 7 ** 2 + 7), (343, 56))
        self.assertNotEqual(7 ** 3, 7 ** 2 + 7)
        self.assertEqual(self.audit()["errors"], [])

    def test_mutation_neutral_diagnostic_missing_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        del pkg["microtopics"][0]["extensions"]["grade9v3:concept_checkpoint"]["diagnostic"]
        self.assertIn("NEUTRAL_COUNTEREXAMPLE_MISSING_OR_NOT_AUTHORED",
                      self.audit(package=pkg)["errors"])

    def test_mutation_neutral_diagnostic_false_mastery_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["microtopics"][0]["extensions"]["grade9v3:concept_checkpoint"]["diagnostic"]["status"] = "INDEPENDENT_MASTERY"
        self.assertIn("NEUTRAL_COUNTEREXAMPLE_MISSING_OR_NOT_AUTHORED",
                      self.audit(package=pkg)["errors"])

    def test_mutation_neutral_diagnostic_leaks_target_model_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["microtopics"][0]["extensions"]["grade9v3:concept_checkpoint"]["diagnostic"]["prompt"] += " Set t=4^(2u)."
        self.assertIn("NEUTRAL_COUNTEREXAMPLE_LEAKS_D3_PROTECTED_WORK",
                      self.audit(package=pkg)["errors"])

    def test_mutation_wrong_third_hint_purpose_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["questions"][0]["hint_ladder"][2]["purpose"] = "CONNECT"
        self.assertIn("D3_H3_PURPOSE_EXPECTED_OPEN_THE_WAY", self.audit(package=pkg)["errors"])

    def test_mutation_answer_leaking_early_hint_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["questions"][0]["scaffolds"][0]["text"] = "Set t=4^(2u) and solve 4t=t+192."
        err = self.audit(package=pkg)["errors"]
        self.assertIn("D3_H1_LEAKS_PROTECTED_WORK", err)

    def test_mutation_noncanonical_or_unresolved_crux_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["questions"][0]["answer"]["crux_move_ref"] = "INVENTED-SHORTCUT"
        self.assertTrue(any("QRT_RESOLUTION_INVALID" in x for x in self.audit(package=pkg)["errors"]))

    def test_mutation_false_core2_admission_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["selection"]["core2"] = ["SOF-UNKNOWN"]
        self.assertIn("AUTHENTIC_CORE2_OR_TRANSFER_SELECTED", self.audit(manifest=manifest)["errors"])

    def test_mutation_golden_reviewer_status_cannot_be_promoted(self):
        gs = copy.deepcopy(self.goldens)
        gs[1]["status"] = "ACCEPTED"
        self.assertIn("GOLDEN_FALSE_PRODUCT_AUTHORITY", self.audit(goldens=gs)["errors"])

    def test_mutation_wrong_golden_cell_is_rejected(self):
        gs = copy.deepcopy(self.goldens)
        gs[0]["matrix"]["expected_cell"] = "QRT-APPLY-D1"
        self.assertIn("GOLDEN_CELL_SET_CHANGED_OR_REORDERED", self.audit(goldens=gs)["errors"])

    def test_mutation_missing_required_blueprint_slot_is_rejected(self):
        bs = copy.deepcopy(self.blueprints)
        next(x for x in bs["blueprints"] if x["id"] == "BP-CORE1A-CONSTRUCTION")["slots"].append({
            "id": "genuinely_required_new_slot", "required": True,
        })
        self.assertIn("BLUEPRINT_REQUIRED_SLOT_UNMAPPED_CORE1A_genuinely_required_new_slot",
                      self.audit(blueprints=bs)["errors"])

    def test_mutation_no_fresh_exit_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["microtopics"][0]["exit_task"]["prompt"] = ""
        self.assertIn("CORE1A_FRESH_EXIT_ABSENT", self.audit(package=pkg)["errors"])

    def test_mutation_repair_step_not_resolved_is_rejected(self):
        pkg = copy.deepcopy(self.package)
        pkg["questions"][0]["repair_ref"] = "TC-NOT-FOUND"
        self.assertIn("P2_REPAIR_REF_UNRESOLVED", self.audit(package=pkg)["errors"])


if __name__ == "__main__":
    unittest.main()
