"""Original pinned validator against actual Issue #287 AI review: format ≠ science.

This is a replay/receipt only, not an independent Physics reviewer or Pass A stimulus.
Do not attach this response to an answer-withheld first-pass reviewer intake.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Physics.adapter.qrt_program.qrt_review_packet import (
    make_packet, selected_review_candidates, recompute_packet_sha256
)
from Physics.adapter.qrt_program.qrt_review_response import evaluate, validate_review_response

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"fixtures/physics_qrt_nlm_ai_response_287.v1.json"
QUESTION="Q-PHY-NLM-2B-FRICTION-STATE-01"
ONE_PACKET="40c37373238ee796fc2857562cb38033b762277284322315dcc698c2cca12f10"
SOURCE_HEAD="8538d90ab73701afabc81369adb9ca3fefdd88fa"
COMMENT="https://github.com/reallakshman19/Grade9v3.5/issues/287#issuecomment-6216606071"

class ActualPublishedAIReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=make_packet(candidates=selected_review_candidates(QUESTION))
        cls.submitted=json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_one_question_packet_is_exact_pinned_content(self):
        p=self.packet
        self.assertEqual(p["question_count"],1)
        self.assertEqual(p["questions"][0]["question_id"],QUESTION)
        self.assertEqual(p["packet_sha256"],ONE_PACKET)
        self.assertEqual(recompute_packet_sha256(p),ONE_PACKET)
        self.assertFalse(p["permission_to_write"])
        self.assertEqual(p["release_verdict"],"HOLD")

    def test_submitted_json_exact_question_and_response_identity(self):
        r=self.submitted
        self.assertEqual(r["packet_sha256"],ONE_PACKET)
        self.assertEqual(r["source_base_sha"],self.packet["base_sha"])
        self.assertEqual(len(r["per_question"]),1)
        self.assertEqual(r["per_question"][0]["question_id"],QUESTION)
        self.assertEqual(r["per_question"][0]["question_sha256"],
                         self.packet["questions"][0]["question_sha256"])
        self.assertEqual(r["overall"],"REVISE")
        self.assertEqual(r["per_question"][0]["verdict"],"REVISE")

    def test_actual_original_pinned_validator_on_submitted_ai_response(self):
        self.assertEqual(validate_review_response(self.packet,self.submitted),[])
        result=evaluate(self.packet,self.submitted)
        self.assertTrue(result["structurally_complete"])
        self.assertEqual(result["status"],"REVIEW_SUBMITTED_FOR_AUTHENTICATION")
        self.assertEqual(result["reviewer_authenticity"],"NOT_VERIFIED_BY_THIS_TOOL")
        self.assertEqual(result["science_certification"],"NOT_GRANTED_BY_THIS_TOOL")
        self.assertEqual(result["owner_authorization"],"NOT_GRANTED_BY_THIS_TOOL")
        self.assertEqual(result["release_verdict"],"HOLD")

    def test_review_admits_ai_not_qualified_human(self):
        who=self.submitted["reviewer"]
        self.assertIn("AI-assisted",who["identity"])
        self.assertIn("NOT an accredited human",who["identity"])
        self.assertIn("NOT AUTHENTICATED",who["authentication_ref"])
        self.assertIn("no human-qualified",self.submitted["caveat"])
        self.assertFalse(evaluate(self.packet,self.submitted)["errors"])
        # Complete schema is NOT authentication, despite affirmative independence claim.

    def test_mutated_source_packet_cannot_reuse_response(self):
        p=copy.deepcopy(self.packet)
        p["questions"][0]["authored_question_stem"]+=" altered"
        self.assertIn("PACKET_CONTENT_DIGEST_MISMATCH",
                      validate_review_response(p,self.submitted))

    def test_wrong_question_digest_cannot_reuse_response(self):
        r=copy.deepcopy(self.submitted)
        r["per_question"][0]["question_sha256"]="0"*64
        self.assertIn("REVIEW_QUESTION_SHA_MISMATCH:"+QUESTION,
                      validate_review_response(self.packet,r))

    def test_wrong_falsifier_set_cannot_reuse_response(self):
        r=copy.deepcopy(self.submitted)
        r["per_question"][0]["falsifier_results"].pop()
        self.assertIn("REVIEW_FALSIFIERS_INCOMPLETE:"+QUESTION,
                      validate_review_response(self.packet,r))

    def test_missing_review_identity_fails(self):
        r=copy.deepcopy(self.submitted)
        r["reviewer"]["authentication_ref"]=""
        self.assertIn("REVIEW_AUTHENTICATION_REF_MISSING",
                      validate_review_response(self.packet,r))

    def test_no_synthetic_acceptance_override(self):
        r=copy.deepcopy(self.submitted)
        r["overall"]="ACCEPT"
        self.assertIn("OVERALL_ACCEPT_WITH_NONACCEPT_CASE",
                      validate_review_response(self.packet,r))

    def test_review_frozen_first_pass_is_separate_source(self):
        refs=self.submitted["per_question"][0]["evidence_refs"]
        self.assertTrue(any("6216380308" in x for x in refs))
        self.assertTrue(any("source" in x.lower() or SOURCE_HEAD in x for x in refs))
        self.assertIn("issuecomment-6216606071",COMMENT)

if __name__=="__main__":
    unittest.main()
