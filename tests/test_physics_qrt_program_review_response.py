"""Review gate must never turn structural completeness into scientific approval."""
import copy
import unittest

from Physics.adapter.qrt_review_packet import make_packet
from Physics.adapter.qrt_review_response import evaluate, validate_review_response


def complete_test_response(packet):
    entries = []
    for q in packet["questions"]:
        entries.append({
            "question_id": q["question_id"],
            "question_sha256": q["question_sha256"],
            "verdict": "ACCEPT",
            "independent_derivation": "Candidate fixture only: independently solve the equations and verify each vector sign and physical condition.",
            "model_assumption_judgement": "For bounded test only, the declared assumptions are assessed separately from the code.",
            "falsifier_results": [
                {"case": text, "outcome": "REJECTS_FALSE_RESULT",
                 "reason": "Test-only record; not a real expert judgement."}
                for text in q["required_model_falsifiers"]],
            "evidence_refs": ["TEST-FIXTURE-NOT-AUTHENTICATED"],
        })
    return {
        "schema": "physics-qrt.science-review-response/v1",
        "packet_sha256": packet["packet_sha256"],
        "source_base_sha": packet["base_sha"],
        "reviewer": {
            "identity": "EXAMPLE-ONLY-REVIEWER",
            "independent_of_implementation": True,
            "competence_basis": "Test data only; not a claimed real reviewer.",
            "authentication_ref": "EXAMPLE-TEST-ONLY-NO-REAL-AUTHORITY",
        },
        "per_question": entries,
        "overall": "ACCEPT"
    }


class PhysicsReviewResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = make_packet()

    def test_complete_shape_still_not_scientific_certification(self):
        report = evaluate(self.packet, complete_test_response(self.packet))
        self.assertTrue(report["structurally_complete"])
        self.assertEqual(report["status"], "REVIEW_SUBMITTED_FOR_AUTHENTICATION")
        self.assertEqual(report["science_certification"], "NOT_GRANTED_BY_THIS_TOOL")
        self.assertEqual(report["release_verdict"], "HOLD")

    def test_template_missing_reviewer_and_rows_is_rejected(self):
        response = {"schema": "physics-qrt.science-review-response/v1",
                    "packet_sha256": self.packet["packet_sha256"],
                    "source_base_sha": self.packet["base_sha"],
                    "reviewer": {}, "per_question": [], "overall": "NOT_REVIEWED"}
        failures = validate_review_response(self.packet, response)
        self.assertIn("REVIEWER_IDENTITY_MISSING", failures)
        self.assertIn("REVIEW_SET_INCOMPLETE", failures)

    def test_mutated_packet_digest_is_rejected(self):
        response = complete_test_response(self.packet)
        response["packet_sha256"] = "f" * 64
        self.assertIn("REVIEW_WRONG_PACKET_SHA", validate_review_response(self.packet, response))


    def test_stem_tampering_with_old_digest_is_rejected(self):
        packet = copy.deepcopy(self.packet)
        response = complete_test_response(self.packet)
        packet["questions"][0]["authored_question_stem"] += " CHANGED_UNDER_REVIEW"
        self.assertIn("PACKET_CONTENT_DIGEST_MISMATCH",
                      validate_review_response(packet, response))
        self.assertEqual(evaluate(packet, response)["release_verdict"], "HOLD")

    def test_predicted_science_tampering_is_rejected(self):
        packet = copy.deepcopy(self.packet)
        response = complete_test_response(self.packet)
        packet["questions"][1]["candidate_recomputed_prediction"]["range"] = 999
        self.assertIn("PACKET_CONTENT_DIGEST_MISMATCH",
                      validate_review_response(packet, response))

    def test_seeded_falsifier_tampering_is_rejected(self):
        packet = copy.deepcopy(self.packet)
        response = complete_test_response(self.packet)
        packet["questions"][2]["required_model_falsifiers"].append("injected")
        self.assertIn("PACKET_CONTENT_DIGEST_MISMATCH",
                      validate_review_response(packet, response))

    def test_missing_one_question_is_rejected(self):
        response = complete_test_response(self.packet)
        response["per_question"].pop()
        self.assertIn("REVIEW_SET_INCOMPLETE", validate_review_response(self.packet, response))

    def test_optimistic_overall_verdict_does_not_override_revision(self):
        response = complete_test_response(self.packet)
        response["per_question"][0]["verdict"] = "REVISE"
        self.assertIn("OVERALL_ACCEPT_WITH_NONACCEPT_CASE",
                      validate_review_response(self.packet, response))

    def test_missing_independent_derivation_is_rejected(self):
        response = complete_test_response(self.packet)
        response["per_question"][0]["independent_derivation"] = ""
        self.assertTrue(any(e.startswith("REVIEW_DERIVATION_MISSING:")
                            for e in validate_review_response(self.packet, response)))

    def test_missing_falsifiers_is_rejected(self):
        response = complete_test_response(self.packet)
        response["per_question"][0]["falsifier_results"] = []
        self.assertTrue(any(e.startswith("REVIEW_FALSIFIERS_INCOMPLETE:")
                            for e in validate_review_response(self.packet, response)))

    def test_laundered_missing_reviewer_identity_is_rejected(self):
        response = complete_test_response(self.packet)
        response["reviewer"]["identity"] = ""
        self.assertIn("REVIEWER_IDENTITY_MISSING", validate_review_response(self.packet, response))

    def test_duplicate_question_is_rejected(self):
        response = complete_test_response(self.packet)
        response["per_question"].append(copy.deepcopy(response["per_question"][0]))
        self.assertTrue(any(e.startswith("REVIEW_DUPLICATE_QUESTION:")
                            for e in validate_review_response(self.packet, response)))


if __name__ == "__main__":
    unittest.main()
