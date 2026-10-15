"""Native QRT contract versus research metadata, using only synthetic examples."""
import copy
import unittest

from Shared.tools.imo_qrt_canonical_evidence import assess, inspect_research

REF = "BP-CORE2-SOURCE-QUESTION@1.11.0"


def native_question():
    return {
        "id": "SYN-Q1",
        "primary_capability_ref": "CAP-1",
        "difficulty": {
            "band": "D2", "score": 3, "components": {
                "concept_model_selection": 1, "representation_translation": 0,
                "reasoning_chain_length": 1, "algebra_computational_load": 1,
                "trap_exception_sensitivity": 0,
            },
        },
        "extensions": {
            "grade9v3:cognitive_demand": {
                "primary": "APPLY", "secondary": [], "basis": "Execute the given relation."
            },
            "grade9v3:analysis": {
                "stable_crux_move": "Select the correct relation.",
                "common_wrong_route": "Use an unrelated formula.",
            },
        },
        "answer": {
            "reasoning_route": [{
                "id": "SYN-M1", "kind": "EXECUTE", "action": "Apply the relation.",
                "why_valid": "The given conditions hold.", "inputs": [], "output": "synthetic value",
            }],
            "crux_move_ref": "SYN-M1",
        },
    }


PROFILE = {"profile_id": "SYN-PROFILE", "held": {"CAP-1": "DEMONSTRATED"}}
ROLE = {"web_blueprint_ref": REF, "ordered_blocks": [], "withheld_pre_attempt": True}


class EvidenceBridgeTests(unittest.TestCase):
    def test_research_metadata_never_implies_native_core_admission(self):
        q = {"id": "SYN-RESEARCH", "cognitive_classification": {
            "primary_demand": "APPLY", "difficulty_band": "D2", "qrt_cell": "QRT-APPLY-D2"
        }, "answer": {"choice": "B"}}
        r = assess(q)
        self.assertEqual(r["status"], "BLOCKED_MISSING_OR_INVALID_EVIDENCE")
        self.assertEqual(r["native_product_admission"], "NOT_GRANTED")
        self.assertIn("CANONICAL_FIVE_FACTOR_DIFFICULTY", r["missing_or_invalid"])
        self.assertIn("ANSWER_REASONING_ROUTE", r["missing_or_invalid"])
        self.assertIn("NATIVE_CORE_ROLE_RECORD", r["missing_or_invalid"])

    def test_real_canonical_resolver_and_subject_adapter_are_called(self):
        r = assess(native_question(), profile=PROFILE, native_role=ROLE)
        self.assertEqual(r["status"], "CANONICAL_RESOLVED_UNREVIEWED")
        self.assertEqual(r["canonical"]["template_id"], "QRT-APPLY-D2")
        self.assertEqual(len(r["canonical"]["asks"]), 12)
        self.assertIn("primary_move", r["canonical"]["basis_digests"])
        self.assertEqual(r["academic_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(r["native_product_admission"], "NOT_GRANTED")
        self.assertEqual(r["blueprint"]["status"], "STRUCTURE_COMPATIBLE")

    def test_missing_profile_cannot_be_inferred_from_bank(self):
        r = assess(native_question(), native_role=ROLE)
        self.assertIn("ACTUAL_LEARNER_PROFILE", r["missing_or_invalid"])

    def test_missing_core_role_cannot_be_guessed_from_qid(self):
        r = assess(native_question(), profile=PROFILE)
        self.assertIn("NATIVE_CORE_ROLE_RECORD", r["missing_or_invalid"])
        self.assertEqual(r["blueprint"]["status"], "NOT_RUN")

    def test_missing_crux_action_fails_before_resolver(self):
        q = native_question()
        q["answer"]["reasoning_route"][0].pop("action")
        r = assess(q, profile=PROFILE, native_role=ROLE)
        self.assertIn("ANSWER_CRUX_MOVE_REFERENCE", r["missing_or_invalid"])

    def test_bad_native_blueprint_binding_rejected(self):
        role = copy.deepcopy(ROLE)
        role["web_blueprint_ref"] = "BP-CORE1A-CONSTRUCTION@1.8.0"
        r = assess(native_question(), profile=PROFILE, native_role=role)
        self.assertEqual(r["blueprint"]["status"], "STRUCTURE_FAIL")
        self.assertIn("NATIVE_CORE2_BLUEPRINT_BINDING_INVALID", r["missing_or_invalid"])

    def test_unresolved_transfer_protected_move_rejected(self):
        q = native_question()
        q["transfer"] = {"protected_move_ref": "UNKNOWN"}
        r = assess(q, profile=PROFILE, native_role=ROLE)
        self.assertIn("TRANSFER_PROTECTED_MOVE_REFERENCE_UNRESOLVED", r["missing_or_invalid"])

    def test_difficulty_mutation_fails_using_canonical_rule(self):
        q = native_question()
        q["difficulty"]["score"] = 9
        r = assess(q, profile=PROFILE, native_role=ROLE)
        self.assertIn("CANONICAL_QRT_RESOLUTION_REJECTED", r["missing_or_invalid"])
        self.assertIn("SCORE_MISMATCH", r["canonical"]["reason"])

    def test_source_corpus_requires_evidence_it_does_not_have(self):
        result = inspect_research(baseline_sha="a"*40)
        self.assertEqual(result["total"], 260)
        self.assertEqual(result["unique_ids"], 260)
        self.assertEqual(result["canonical_resolved"], 0)
        self.assertEqual(result["missing_or_invalid_counts"]["ACTUAL_LEARNER_PROFILE"], 260)
        self.assertEqual(result["missing_or_invalid_counts"]["NATIVE_CORE_ROLE_RECORD"], 260)
        self.assertEqual(result["native_product_admission"], "NOT_GRANTED")

    def test_noncommit_ref_rejected(self):
        with self.assertRaises(ValueError):
            inspect_research(baseline_sha="main")


if __name__ == "__main__":
    unittest.main()
