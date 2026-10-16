"""Source-first qualification for one *draft* NLM correction (Issue #289).

This test does NOT approve the academic novelty claim, confer QRT classification,
measure learner mastery, or grant release. It proves bounded source identity and
basic numerical/physical consistency against an immutable original Git revision.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "Physics/library/phy-nlm-first-law.v1.json"
BASE = "73c66b64158ee2ff57b099f990e1c2081d5c571f"
ORIGINAL_BLOB = "62b8df106e83db03ac80fbb4002a611ac3d6e49a"
QUESTION_ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"
CANDIDATE_DIGEST = "310f32e0b09d1628b53e98164c46db477b84ab45ee20701ee43a01bc88c5d616"
FIELDS = {"stem", "conditions", "hints", "hint_ladder", "answer"}
ANSWER_FIELDS = {"summary", "reasoning", "check", "acceptable_alternatives", "rubric", "reasoning_route"}


def canonical_sha(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class PhysicsNlm289SourceCorrection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:{SOURCE}"],
                              check=True, capture_output=True).stdout
        cls.source_bytes = (ROOT / SOURCE).read_bytes()
        cls.base = json.loads(base)
        cls.changed = json.loads(cls.source_bytes)
        cls.base_bytes = base
        cls.before = next(q for q in cls.base["questions"] if q["id"] == QUESTION_ID)
        cls.after = next(q for q in cls.changed["questions"] if q["id"] == QUESTION_ID)

    def test_original_and_candidate_pinned(self):
        self.assertEqual(blob_sha(self.base_bytes), ORIGINAL_BLOB)
        self.assertEqual(canonical_sha(self.after), CANDIDATE_DIGEST)

    def test_no_unrelated_package_records_changed(self):
        original = dict(self.base)
        candidate = dict(self.changed)
        original["questions"] = [q for q in original["questions"] if q["id"] != QUESTION_ID]
        candidate["questions"] = [q for q in candidate["questions"] if q["id"] != QUESTION_ID]
        self.assertEqual(original, candidate)
        self.assertEqual(len(original["questions"]), 51)

    def test_only_approved_one_question_fields_changed(self):
        before = self.before
        after = self.after
        changed_keys = {k for k in before if before[k] != after[k]}
        self.assertEqual(changed_keys, FIELDS)
        self.assertEqual({k for k in before["answer"]
                          if before["answer"][k] != after["answer"][k]}, ANSWER_FIELDS)
        self.assertEqual(after["transfer"], before["transfer"])
        self.assertEqual(after["representation_roles"], before["representation_roles"])
        self.assertNotIn("grade9v3:cognitive_demand", after["extensions"])

    def test_holds_remain_explicit_in_source_data(self):
        self.assertEqual(self.after["status"], "CANDIDATE")
        self.assertEqual(self.after["exposure"][0]["role"], "NEW_TRANSFER")
        # This is a source declaration, not a reviewer-approved new transfer.
        self.assertEqual(self.after["transfer"]["dimension"], "model_choice")
        self.assertFalse(self.after["evidence_refs"])

    def test_first_attempt_does_not_prewrite_governing_equation(self):
        visible = self.after["stem"] + " " + " ".join(self.after["conditions"])
        orient = self.after["hints"][0]["text"]
        for phrase in ("Resolve each pull", "do not take N = mg", "N = mg - P",
                       "N=100", "P cosθ =", "60 N", "62.5 N"):
            self.assertNotIn(phrase, visible + " " + orient)

    def test_physical_assumptions_and_boundary_accurate(self):
        conditions = " ".join(self.after["conditions"])
        self.assertIn("non-tipping", conditions)
        self.assertIn("non-rotating", conditions)
        self.assertIn("fixed", conditions)
        self.assertIn("floor contact", conditions)
        self.assertIn("not proof", conditions)
        self.assertIn("limiting static equilibrium", self.after["answer"]["summary"])

    def test_three_thresholds_and_contact(self):
        mu, mg = .75, 100
        angles = [(1, 0, 75), (.8, .6, 60), (.6, .8, 62.5)]
        for c, s, expected in angles:
            critical = mu * mg / (c + mu * s)
            self.assertTrue(math.isclose(critical, expected, abs_tol=1e-10))
            self.assertGreater(mg - critical * s, 0)
            self.assertAlmostEqual(critical*c, mu*(mg-critical*s))

    def test_worker_61_newton_rest_falsifiers(self):
        mu, mg, worker = .75, 100, 61
        directions = [(1, 0), (.8, .6), (.6, .8)]
        can_rule_out_rest = [worker*c > mu*(mg-worker*s) for c, s in directions]
        self.assertEqual(can_rule_out_rest, [False, True, False])
        # Equality is a possible impending slip, not proof of actual motion.
        self.assertAlmostEqual(60*.8, mu*(mg-60*.6))
        self.assertGreater(61*.8, mu*(mg-61*.6))
        self.assertIn("strictly", self.after["answer"]["summary"])

    def test_alternative_reasoning_is_present(self):
        self.assertGreaterEqual(len(self.after["answer"]["acceptable_alternatives"]), 4)
        content = " ".join(self.after["answer"]["acceptable_alternatives"])
        self.assertIn("mg/(sinθ+cosθ/μ_s)", content)
        self.assertIn("axis convention", content)
        self.assertIn("rounding", content)
        self.assertGreaterEqual(len(self.after["answer"]["rubric"]), 4)

    def test_protected_reasoning_does_not_turn_equality_into_motion(self):
        route = self.after["answer"]["reasoning_route"]
        self.assertEqual([r["id"] for r in route],
                         [r["id"] for r in self.before["answer"]["reasoning_route"]])
        protected = self.after["transfer"]["protected_move_ref"]
        self.assertEqual(next(r for r in route if r["id"] == protected)["kind"], "DECIDE")
        self.assertIn("strictly exceeds", route[2]["output"])
        self.assertIn("ruling out static rest", route[2]["output"])
        self.assertIn("does not itself prove motion", route[1]["why_valid"])
        self.assertIn("limiting static", route[3]["why_valid"])
        self.assertNotIn("starting pull", route[1]["action"])
        self.assertNotIn("can start the crate", route[2]["output"])

    def test_authored_hints_do_not_prove_h2_h3_ui(self):
        self.assertEqual(len(self.after["hint_ladder"]), 3)
        self.assertEqual(self.after["hint_ladder"][0]["purpose"], "ORIENT")
        self.assertEqual(self.after["hint_ladder"][1]["purpose"], "REPRESENT")
        self.assertEqual(self.after["hint_ladder"][2]["purpose"], "FIRST_RELATION")


if __name__ == "__main__":
    unittest.main()
