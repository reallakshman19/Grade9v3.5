"""Contract tests for warning-only source/W preflight, not academic validation."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("source_w_preflight_201.py")
spec = spec_from_file_location("source_w_preflight_201", SOURCE)
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def question(stem: str, evidence: str = "Decide x stands for one of two item types") -> dict:
    return {"stem": stem, "difficulty": {"basis": "learner must select a variable", "component_evidence": {
        "concept_model_selection": evidence}}}


class SourceWWarningContracts(unittest.TestCase):
    def test_model_known_contradiction_flag(self):
        q = question("Choose a variable for the LARGE-cup count, form a model and solve")
        flags = module.check_question(q, "model", "Choose category unknown and complementary count")
        self.assertEqual([f["id"] for f in flags], ["QRT201-W-PRESELECTED-VARIABLE-CATEGORY"])
        self.assertIn("LARGE-cup", flags[0]["stem_excerpt"])
        self.assertNotIn("ACCEPT", flags[0]["severity"])

    def test_no_model_flag_without_named_category(self):
        q = question("Choose a variable and form a model that links count with revenue")
        self.assertEqual(module.check_question(q, "model", "Choose count category"), [])

    def test_no_model_flag_after_narrowing_author_claim(self):
        q = question("Choose a variable for the LARGE-cup count", evidence="Build a weighted sum")
        q["difficulty"]["basis"] = "Complementary total connects two given conditions"
        self.assertEqual(module.check_question(q, "model", "Build the weighted cost relation"), [])

    def test_retrieve_rival_apply_flag(self):
        q = question("Retrieve the right-triangle distance relation and calculate BOTH routes")
        flags = module.check_question(q, "retrieve", "Retrieve diagonal relation")
        self.assertEqual([f["id"] for f in flags], ["QRT201-DEMAND-RETRIEVE-VS-APPLY"])
        self.assertIn("APPLY", flags[0]["question_for_reviewer"])

    def test_retrieve_without_given_relation_is_not_falsely_cleared(self):
        q = question("Which fact gives the shortest path? Explain why")
        self.assertEqual(module.check_question(q, "retrieve"), [])

    def test_other_demand_not_inferred_from_same_wording(self):
        q = question("Choose a variable for the LARGE-cup count")
        self.assertEqual(module.check_question(q, "apply"), [])

    def test_justifys_assessed_question_is_core2a_proof_not_worked(self):
        package = {"questions": [
            {"id": "WORKED", "origin": "AUTHORED", "exposure": [{"core": "CORE1A"}]},
            {"id": "PROOF", "origin": "AUTHORED", "exposure": [{"core": "CORE2A"}]},
        ]}
        self.assertEqual(module.assessed_question(package, "justify")["id"], "PROOF")

    def test_missing_core2a_fails_structural_check(self):
        with self.assertRaises(ValueError):
            module.assessed_question({"questions": [{"id": "WORKED", "exposure": []}]}, "justify")

    def test_non_authored_core2a_not_admitted(self):
        q = {"id": "SOURCE", "origin": "ORGANIZER", "exposure": [{"core": "CORE2A"}]}
        with self.assertRaisesRegex(ValueError, "authored TEST"):
            module.assessed_question({"questions": [q]}, "retrieve")


if __name__ == "__main__":
    unittest.main()
