"""Canonical QRT resolution and review-state regression for issue #164 alternatives."""
import json
import unittest
from pathlib import Path
from Shared.tools import question_difficulty, question_review_matrix as qrt

ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/"TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
REVIEW=ROOT/"TEST/imo-research/pilots/transfer-comparison-164.v1.json"
FIVE="Q-TEST-IMO-164-FIVE-CONSECUTIVE-120"
BOUNDARY="Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY"

class AcademicCandidateQRT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions={q["id"]:q for q in json.loads(PKG.read_text())["questions"]}
        cls.review=json.loads(REVIEW.read_text())["qrt_comparison"]
        cls.matrix=qrt.load(qrt.MATRIX_PATH)
        cls.vocab=qrt.load(qrt.VOCAB_PATH)

    def test_real_qrts_resolve_with_canonical_vocabulary_and_12_review_prompts(self):
        self.assertEqual(len(qrt.DEMANDS)*len(qrt.BANDS),28)
        for id_ in (FIVE,BOUNDARY):
            with self.subTest(id=id_):
                q=self.questions[id_]
                profile={"profile_id":"TEST-IMO-164-UNDEMONSTRATED","held":{}}
                resolved=qrt.resolve_review(q,profile,self.matrix,self.vocab)
                self.assertEqual(resolved["template_id"],"QRT-JUSTIFY-D3")
                self.assertEqual(resolved["classification"]["demand"]["primary"],"JUSTIFY")
                self.assertEqual(resolved["classification"]["band"],"D3")
                self.assertEqual(tuple(resolved["review"]),qrt.ASKS)
                self.assertEqual(resolved["classification"]["difficulty_score"],7)
                self.assertEqual(resolved["classification"]["demand"]["primary_move_ref"],
                                 q["answer"]["crux_move_ref"])
                self.assertIn("UNRESOLVED", resolved["slots"]["Y"]["text"])
                self.assertEqual(q["transfer"]["protected_move_ref"],q["answer"]["crux_move_ref"])

    def test_evidence_score_is_derived_not_proof_of_academic_approval(self):
        projections={p["question_ref"]:p for p in self.review["candidate_projections"]}
        self.assertEqual(set(projections),{FIVE,BOUNDARY})
        for qid,p in projections.items():
            with self.subTest(qid=qid):
                q=self.questions[qid]
                derived=question_difficulty.derive(q["difficulty"],question_ref=qid)
                self.assertEqual(p["components"],list(derived["components"].values()))
                self.assertEqual(p["score"],derived["score"])
                self.assertEqual(p["derived_band"],derived["band"])
                cognitive=q["extensions"]["grade9v3:cognitive_demand"]
                self.assertEqual(p["primary_demand"],cognitive["primary"])
                self.assertEqual(p["secondary_demands"],cognitive["secondary"])
                self.assertTrue(set(cognitive["secondary"])<=set(qrt.DEMANDS))
                self.assertIn("PROPOSED ONLY",q["difficulty"]["basis"])
        self.assertFalse(json.loads(REVIEW.read_text())["qrt_accepted"])

    def test_exact_twelve_qrt_review_slots_explicitly_unapproved(self):
        self.assertEqual(self.review["status"],"AUTHOR_WORKSHEET_UNREVIEWED")
        self.assertEqual(self.review["canonical_template"],"QRT-JUSTIFY-D3")
        self.assertEqual(set(self.review["qrt_worksheet_slots"]),set(qrt.ASKS))
        for slot in self.review["qrt_worksheet_slots"].values():
            self.assertEqual(slot["review_state"],"NOT_REVIEWED")
            self.assertIsNone(slot["reviewer"])
            self.assertFalse(slot["owner_acceptance"])
        self.assertEqual(self.review["conclusion"],"UNDECIDED_NO_INDEPENDENT_REVIEW")

if __name__=="__main__":
    unittest.main()
