#!/usr/bin/env python3
"""R12 source-pinned native postcommit reviewer-handoff claim-boundary mutants."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from qrt_intent_contract import ContractError
from qrt_intent_postcommit_contract import (
    POSTCOMMIT_CHECKS, classify_postcommit_journey,
    verify_native_postcommit_handoff,
)

QUESTION = "Q-TEST-QRT-MODEL-D2-PRIMARY"
CONCEPT = "MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT"
MISSING = {
    "postcommit_context_link_present", "context_link_is_pinned",
    "return_link_present", "return_link_is_pinned",
    "attempt_text_restored", "assistance_marked",
}


def fixture() -> dict:
    observed = {k: k not in MISSING for k in POSTCOMMIT_CHECKS}
    observed["independent_credit_claimed"] = False
    findings = classify_postcommit_journey(observed)
    return {
        "schema": "imo182-r8-real-native-navigation/v1",
        "assisted_return": {
            "primary_question_id": QUESTION,
            "target_identity_expected_concept": CONCEPT,
            "context_link_at_source": False,
            "return_link_at_concept": False,
            "return_state_assisted": False,
            "source_attempt_restored": False,
            "target_identity_proven": False,
            "target_identity_findings": [],
        },
        "target_identity_findings": [],
        "qualified_semantic_review": "NOT_RUN",
        "owner_acceptance": False,
        "postcommit_native_journey": {
            "schema": "imo182-r11-native-postcommit-technical-probe/v1",
            "source_question_id": QUESTION,
            "selected_concept_id": CONCEPT,
            "native_renderer_only": True,
            "source_bytes_changed": False,
            "meaningful_mathematical_answer_submitted": False,
            "human_academic_evidence": False,
            "release": "HOLD",
            "observed": observed,
            "findings": findings,
            "technical_round_trip_complete": False,
        },
    }


class PostcommitReviewerHandoffTests(unittest.TestCase):
    def reject(self, code, edit):
        r = fixture()
        edit(r)
        with self.assertRaisesRegex(ContractError, "^" + code + ":"):
            verify_native_postcommit_handoff(r, QUESTION, CONCEPT)

    def test_six_observed_native_defects_are_truthfully_carried_forward(self):
        r = verify_native_postcommit_handoff(fixture(), QUESTION, CONCEPT)
        self.assertEqual(len(r["distinct_technical_findings"]), 6)
        self.assertEqual(r["technical_state"], "NATIVE_ROUNDTRIP_DEFECTS_OBSERVED")
        self.assertFalse(r["technical_round_trip_complete"])
        self.assertFalse(r["academic_approved"])
        self.assertFalse(r["owner_approved"])
        self.assertEqual(r["release"], "HOLD")

    def test_missing_native_postcommit_proof_rejected(self):
        self.reject("P5_R11_NATIVE_POSTCOMMIT_EVIDENCE_REQUIRED",
                    lambda r: r.pop("postcommit_native_journey"))

    def test_wrong_source_question_rejected(self):
        self.reject("P5_R11_NATIVE_SOURCE_IDENTITY_DRIFT",
                    lambda r: r["postcommit_native_journey"].update(source_question_id="WRONG"))

    def test_wrong_concept_rejected(self):
        self.reject("P5_R11_NATIVE_SOURCE_IDENTITY_DRIFT",
                    lambda r: r["postcommit_native_journey"].update(selected_concept_id="WRONG"))

    def test_forged_boolean_complete_flag_rejected(self):
        self.reject("P5_R11_NATIVE_FINDINGS_OR_STATUS_FORGED",
                    lambda r: r["postcommit_native_journey"].update(technical_round_trip_complete=True))

    def test_omitted_negative_finding_rejected(self):
        self.reject("P5_R11_NATIVE_FINDINGS_OR_STATUS_FORGED",
                    lambda r: r["postcommit_native_journey"].update(findings=[]))

    def test_forged_independent_credit_without_negative_finding_rejected(self):
        def change(r):
            r["postcommit_native_journey"]["observed"]["independent_credit_claimed"] = True
        self.reject("P5_R11_NATIVE_FINDINGS_OR_STATUS_FORGED", change)

    def test_wrong_shape_or_string_boolean_rejected(self):
        self.reject("P5_R11_NATIVE_STATUS_SCHEMA_DRIFT",
                    lambda r: r["postcommit_native_journey"]["observed"].update(
                        assistance_marked="false"))

    def test_missing_required_predicate_rejected(self):
        self.reject("P5_R11_NATIVE_STATUS_SCHEMA_DRIFT",
                    lambda r: r["postcommit_native_journey"]["observed"].pop(
                        "attempt_blank_rejected"))

    def test_release_or_human_claim_rejected(self):
        self.reject("P5_R11_NATIVE_CLAIM_BOUNDARY_VIOLATED",
                    lambda r: r["postcommit_native_journey"].update(release="GO"))

    def test_fake_precommit_target_validity_rejected(self):
        self.reject("P5_R11_NATIVE_PRECOMMIT_TARGET_STATUS_FORGED",
                    lambda r: r["assisted_return"].update(target_identity_proven=True))

    def test_hypothetically_complete_technical_journey_is_not_academic_approval(self):
        r = fixture()
        r["postcommit_native_journey"]["observed"] = {
            **{k: True for k in POSTCOMMIT_CHECKS},
            "independent_credit_claimed": False,
        }
        r["postcommit_native_journey"]["findings"] = []
        r["postcommit_native_journey"]["technical_round_trip_complete"] = True
        r["assisted_return"].update(
            context_link_at_source=True, return_link_at_concept=True,
            return_state_assisted=True, source_attempt_restored=True,
            target_identity_proven=True,
        )
        v = verify_native_postcommit_handoff(r, QUESTION, CONCEPT)
        self.assertTrue(v["technical_round_trip_complete"])
        self.assertEqual(v["technical_state"],
                         "ROUNDTRIP_TECHNICALLY_COMPLETE_NOT_QRT_APPROVED")
        self.assertFalse(v["owner_approved"])
        self.assertFalse(v["academic_approved"])
        self.assertEqual(v["release"], "HOLD")


if __name__ == "__main__":
    unittest.main()
