"""Independent candidate source-custody falsifiers; no original question text."""
import copy
import json
import unittest

from Shared.tools.imo_qrt_candidate_receipt import (compare_source, _read_bank,
    inspect_research_authority_claims)


def q():
    return {
        "id": "SYN-001", "stem": "Synthetic stem", "options": {"A": "1", "B": "2"},
        "answer": {"choice": "B"}, "paper_origin_locator": {"paper": "SYN", "question_number": 1},
        "figure_ref": "synthetic.svg", "hint_ladder": {"hint1_conceptual_nudge": "What relation?"},
        "solution": {"derivation": "Synthetic check"},
        "cognitive_classification": {"qrt_cell": "QRT-APPLY-D2"},
    }


class CandidateSourceTests(unittest.TestCase):
    def test_authored_solution_correction_preserves_source(self):
        old = q()
        new = copy.deepcopy(old)
        new["solution"]["derivation"] = "Corrected reasoning"
        new["hint_ladder"]["hint1_conceptual_nudge"] = "Find the invariant."
        report = compare_source({old["id"]: old}, {new["id"]: new})
        self.assertEqual(report["status"], "SOURCE_CUSTODY_PRESERVED")
        self.assertEqual(report["authored_changes"][0]["academic_review"], "REVIEW_REQUIRED")
        self.assertEqual(report["source_custody_drifts"], [])

    def test_original_stem_drift_requires_owner_authority(self):
        old = q()
        new = copy.deepcopy(old)
        new["stem"] = "Silently changed source"
        report = compare_source({old["id"]: old}, {new["id"]: new})
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["source_custody_drifts"][0]["field"], "stem")

    def test_option_order_and_identity_are_protected(self):
        old = q()
        new = copy.deepcopy(old)
        new["options"] = {"B": "2", "A": "1"}
        self.assertEqual(compare_source({old["id"]: old}, {new["id"]: new})["status"], "FAIL")

    def test_answer_key_may_not_drift_without_review(self):
        old = q()
        new = copy.deepcopy(old)
        new["answer"]["choice"] = "A"
        self.assertIn("answer", [f["field"] for f in
            compare_source({old["id"]: old}, {new["id"]: new})["source_custody_drifts"]])

    def test_figure_ref_and_source_locator_preserved(self):
        old = q()
        new = copy.deepcopy(old)
        new["figure_ref"] = None
        new["paper_origin_locator"]["paper"] = "DIFFERENT"
        self.assertEqual({f["field"] for f in compare_source(
            {old["id"]: old}, {new["id"]: new})["source_custody_drifts"]},
                         {"figure_ref", "paper_origin_locator"})

    def test_replaced_question_ids_fail(self):
        old = q()
        new = copy.deepcopy(old)
        new["id"] = "SYN-002"
        result = compare_source({old["id"]: old}, {new["id"]: new})
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["removed_ids"], ["SYN-001"])
        self.assertEqual(result["added_ids"], ["SYN-002"])

    def test_duplicate_bank_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE_QUESTION_ID"):
            _read_bank(json.dumps({"questions": [q(), q()]}).encode(), label="synth")

    def test_double_escaped_numbered_steps_are_a_format_regression(self):
        old = q()
        new = copy.deepcopy(old)
        old["solution"]["derivation"] = "1. Start\n2. Finish"
        new["solution"]["derivation"] = r"1. Start\n2. Finish"
        out = compare_source({old["id"]: old}, {new["id"]: new})
        self.assertEqual(out["status"], "FAIL")
        self.assertEqual(out["source_custody_drifts"], [])
        self.assertEqual(out["solution_format_regressions"][0]["candidate_count"], 1)

    def test_latex_neq_command_does_not_trigger_pseudo_newline_rule(self):
        old = q()
        new = copy.deepcopy(old)
        new["solution"]["derivation"] = r"Use x \neq y for distinct numbers."
        out = compare_source({old["id"]: old}, {new["id"]: new})
        self.assertEqual(out["solution_format_regressions"], [])
        self.assertEqual(out["status"], "SOURCE_CUSTODY_PRESERVED")

    def test_source_ungoverned_certification_claims_all_reported(self):
        html = ("BP-CORE1A &amp; BP-CORE1B CERTIFIED "
                "Anchored to 8 Authenticated Core 2 Questions "
                "20 MODULE PACKAGES · 100% CUSTODY")
        result = inspect_research_authority_claims(html)
        self.assertEqual(result, [
            "UNQUALIFIED_AUTHENTIC_SOURCE",
            "UNQUALIFIED_CORE_BLUEPRINT_CERTIFIED",
            "UNQUALIFIED_CUSTODY_100_PERCENT"])

    def test_research_scoped_copy_has_no_certification_issues(self):
        html = ("Research Core1A/Core1B draft. "
                "8 linked research question IDs (academic source pending). "
                "20 research module packages (Owner acceptance pending).")
        self.assertEqual(inspect_research_authority_claims(html), [])

    def test_question_prose_certified_generic_not_a_copy_match(self):
        self.assertEqual(inspect_research_authority_claims(
            "Show that a certified relation holds in a synthetic question."), [])

    def test_unreviewed_qrt_reclassification_not_automatic_approval(self):
        old = q()
        new = copy.deepcopy(old)
        new["cognitive_classification"]["qrt_cell"] = "QRT-JUSTIFY-D4"
        r = compare_source({old["id"]: old}, {new["id"]: new})
        self.assertEqual(r["status"], "SOURCE_CUSTODY_PRESERVED")
        self.assertIn("cognitive_classification", r["authored_changes"][0]["fields"])
        self.assertEqual(r["authored_changes"][0]["academic_review"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
