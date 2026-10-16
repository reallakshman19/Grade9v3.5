"""Real-source scientific review request tests, not academic signoff."""
import copy
import json
import unittest

from Physics.adapter.qrt_program.qrt_review_packet import make_packet, make_independent_intake, recompute_packet_sha256, candidate_prediction, SCENARIOS, selected_review_candidates
from tools.physics_qrt_program.bootstrap import HERE


class CandidateReviewPacketTests(unittest.TestCase):
    def test_one_nlm_pilot_packet_is_bounded_and_not_approved(self):
        candidate = selected_review_candidates("Q-PHY-NLM-2B-FRICTION-STATE-01")
        packet = make_packet(candidates=candidate)
        self.assertEqual(packet["question_count"], 1)
        self.assertEqual([x["question_id"] for x in packet["questions"]],
                         ["Q-PHY-NLM-2B-FRICTION-STATE-01"])
        self.assertEqual(packet["packet_sha256"], recompute_packet_sha256(packet))
        self.assertEqual(packet["reviewer_identity"], "UNASSIGNED")
        self.assertEqual(packet["review_verdict"], "NOT_REVIEWED")
        self.assertFalse(packet["permission_to_write"])
        self.assertEqual(packet["release_verdict"], "HOLD")
        self.assertNotEqual(packet["packet_sha256"], make_packet()["packet_sha256"])

    def test_one_nlm_blind_intake_contains_no_answer_or_falsifier(self):
        candidate = selected_review_candidates("Q-PHY-NLM-2B-FRICTION-STATE-01")
        intake = make_independent_intake(candidates=candidate)
        packet = make_packet(candidates=candidate)
        self.assertEqual(len(intake["questions"]), 1)
        self.assertEqual(intake["full_comparison_packet_sha256"], packet["packet_sha256"])
        self.assertEqual(intake["status"], "DERIVATION_REQUEST_UNASSIGNED")
        self.assertEqual(intake["qualified_reviewer"], "NOT_ASSIGNED")
        self.assertFalse(intake["owner_authorization"])
        self.assertEqual(intake["release_verdict"], "HOLD")
        assert_text = json.dumps(intake, sort_keys=True)
        for forbidden in ("authored_answer_claim", "candidate_recomputed_prediction",
                          "required_model_falsifiers", "proposed_physics_model"):
            self.assertNotIn(forbidden, assert_text)

    def test_unknown_one_question_cannot_fall_back_to_four(self):
        with self.assertRaisesRegex(ValueError, "REVIEW_QUESTION_NOT_UNIQUE_OR_NOT_CANDIDATE"):
            selected_review_candidates("Q-PHY-NLM-NOT-REAL")

    def test_duplicate_in_candidate_registry_fails_closed(self):
        # The one-question selection is not a licence to accept duplicate source IDs.
        from pathlib import Path
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
            row = next(x for x in src["cases"]
                       if x["question_id"] == "Q-PHY-NLM-2B-FRICTION-STATE-01")
            src["cases"].append(copy.deepcopy(row))
            path = root / "tools/physics_qrt_program/witnesses.candidate.v1.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(src), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "REVIEW_QUESTION_NOT_UNIQUE_OR_NOT_CANDIDATE"):
                selected_review_candidates("Q-PHY-NLM-2B-FRICTION-STATE-01", root=root)

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


    def test_packet_digest_matches_actual_canonical_bytes(self):
        packet = make_packet()
        self.assertEqual(packet["packet_sha256"], recompute_packet_sha256(packet))

    def test_stem_only_intake_withholds_answers_and_false_result_controls(self):
        intake = make_independent_intake()
        self.assertEqual(intake["status"], "DERIVATION_REQUEST_UNASSIGNED")
        self.assertEqual(len(intake["questions"]), 4)
        self.assertEqual(intake["scientific_verdict"], "NOT_REVIEWED")
        self.assertEqual(intake["release_verdict"], "HOLD")
        for question in intake["questions"]:
            self.assertTrue(question["authored_question_stem"])
            for withheld in ("authored_answer_claim", "candidate_recomputed_prediction",
                             "required_model_falsifiers", "proposed_physics_model"):
                self.assertNotIn(withheld, question)

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
