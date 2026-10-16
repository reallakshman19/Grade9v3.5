"""Real-source scientific review request tests, not academic signoff."""
import copy
import json
import unittest

from Physics.adapter.qrt_review_packet import make_packet, candidate_prediction, SCENARIOS
from tools.physics_qrt_program.bootstrap import HERE


class CandidateReviewPacketTests(unittest.TestCase):
    def test_four_source_bound_review_requests(self):
        packet = make_packet()
        self.assertEqual(packet["question_count"], 4)
        self.assertEqual(packet["status"], "PENDING_INDEPENDENT_PHYSICS_REVIEW")
        self.assertEqual(packet["permission_to_write"], False)
        self.assertEqual(packet["review_verdict"], "NOT_REVIEWED")
        self.assertEqual(len(packet["packet_sha256"]), 64)
        self.assertTrue(all(row["authored_question_stem"] and row["question_sha256"]
                            for row in packet["questions"]))
        self.assertTrue(all(row["scientific_approval"] == "NOT_OBTAINED"
                            for row in packet["questions"]))
        self.assertTrue(all(len(row["required_model_falsifiers"]) >= 2 for row in packet["questions"]))

    def test_source_locked_without_trusting_fixture_prose(self):
        packet = make_packet()
        cases = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
        self.assertEqual({q["question_id"] for q in packet["questions"]},
                         {c["question_id"] for c in cases["cases"]})
        self.assertEqual({q["source_sha256"] for q in packet["questions"]},
                         {w["source_sha256"] for w in
                          __import__("tools.physics_qrt_program.bootstrap", fromlist=["assemble"]).assemble()["lock"]["witnesses"]})

    def test_candidate_numbers_are_not_approved(self):
        signed = candidate_prediction("Q-PHY-VEC-DECOMP-2A-QUADRANT-II-03")
        self.assertLess(signed["vx"], 0)
        self.assertGreater(signed["vy"], 0)
        projectile = candidate_prediction("Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04")
        self.assertAlmostEqual(projectile["time"], 2)
        self.assertAlmostEqual(projectile["range"], 30)
        friction = candidate_prediction("Q-PHY-NLM-2B-FRICTION-STATE-01")
        self.assertEqual(friction["can_start"], {"horizontal": False, "37deg": True, "53deg": False})
        packet = make_packet()
        self.assertEqual(packet["review_verdict"], "NOT_REVIEWED")

    def test_known_falsifiers_and_model_limits_for_each_case(self):
        self.assertEqual(len(SCENARIOS), 4)
        for question_id, scenario in SCENARIOS.items():
            with self.subTest(question_id=question_id):
                self.assertGreaterEqual(len(scenario["wrong_result_controls"]), 2)
                self.assertGreaterEqual(len(scenario["scientific_model_limits"]), 1)
                self.assertGreaterEqual(len(scenario["claims_to_challenge"]), 2)

    def test_candidate_source_drift_blocks_review_packet(self):
        value = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
        value["cases"][0]["source_blob_sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "SOURCE_BLOB_DRIFT"):
            make_packet(candidates=value)


if __name__ == "__main__":
    unittest.main()
