#!/usr/bin/env python3
"""R13 exact-native repair matrix negative controls; no academic/Owner promotion."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qrt_intent_native_repair_matrix import (  # noqa: E402
    CHECKS, REPAIR_GROUPS, reported_defects, summarize,
)


def fixture():
    cells, reports = [], {}
    for i in range(28):
        cid = f"QRT-RETRIEVE-D{i+1}" if i < 21 else f"QRT-APPLY-D{i+1}"
        if i >= 21:
            cells.append({"cell_id": cid, "contract_status": "BLOCKED_RIVAL_REVIEW",
                          "blocking_source_author_action": {"code": "RIVAL_NOT_GROUNDED_IN_SOURCE"}})
            continue
        obs = {k: True for k in CHECKS}
        for bad in ("postcommit_context_link_present", "context_link_is_pinned",
                    "return_link_present", "return_link_is_pinned",
                    "attempt_text_restored", "assistance_marked"):
            obs[bad] = False
        obs["independent_credit_claimed"] = False
        question, concept = f"Q-{i}", f"MIC-{i}"
        n = {"schema": "imo182-r8-real-native-navigation/v1", "cell_id": cid,
             "assisted_return": {"target_identity_expected_concept": concept},
             "owner_acceptance": False, "qualified_semantic_review": "NOT_RUN",
             "postcommit_native_journey": {
                 "schema": "imo182-r11-native-postcommit-technical-probe/v1",
                 "source_question_id": question, "selected_concept_id": concept,
                 "native_renderer_only": True, "source_bytes_changed": False,
                 "meaningful_mathematical_answer_submitted": False,
                 "human_academic_evidence": False, "release": "HOLD",
                 "observed": obs, "findings": reported_defects(obs),
                 "technical_round_trip_complete": False}}
        sha = hashlib.sha256(json.dumps(n, sort_keys=True).encode()).hexdigest()
        reports[cid] = n, sha
        cells.append({"cell_id": cid, "contract_status": "VALIDATED_PROPOSAL",
                      "qrt_hypothesis_not_a_verdict": {"primary_question_id": question},
                      "release": "HOLD",
                      "qualified_independent_reviewer": {"decision": None},
                      "owner_separate_disposition": {"decision": None},
                      "available_scoped_browser_proof": [{
                          "name": "REAL_NATIVE_POSTCOMMIT_SAME_QUESTION_DIAGNOSTIC",
                          "technical_state": "NATIVE_ROUNDTRIP_DEFECTS_OBSERVED",
                          "native_question_id": question, "selected_concept_id": concept,
                          "sha256": sha, "native_renderer_only": True,
                          "separate_held_copy_not_authoritative": True,
                          "distinct_technical_findings": n["postcommit_native_journey"]["findings"],
                          "technical_round_trip_complete": False,
                          "academic_approved": False,
                          "owner_approved": False}]})
    return ({"cells": cells, "release": "HOLD",
             "counts": {"qualified_signed_verdicts": 0, "owner_acceptances": 0}}, reports)


class NativeRepairMatrix(unittest.TestCase):
    def rejects(self, code, mutate):
        handoff, reports = fixture()
        mutate(handoff, reports)
        with self.assertRaisesRegex(ValueError, "^" + code + ":"):
            summarize(handoff, reports)

    def test_exact_21_7_and_four_repair_workstreams(self):
        h, n = fixture()
        result = summarize(h, n)
        self.assertEqual(result["counts"], {
            "qrt_cells": 28, "native_source_bound": 21,
            "source_blocked_no_native_report": 7,
            "native_round_trips_complete": 0,
            "technical_finding_occurrences": 126})
        self.assertEqual(result["engineering_workstream_cell_counts"],
                         {k: 21 for k in sorted(REPAIR_GROUPS)})
        self.assertEqual(result["release"], "HOLD")

    def test_missing_report_rejected(self):
        self.rejects("R13_NATIVE_REPORT_SET_MISMATCH",
                     lambda h, r: r.pop("QRT-RETRIEVE-D1"))

    def test_duplicated_28th_cell_rejected(self):
        self.rejects("R13_HANDOFF_NOT_EXACTLY_28",
                     lambda h, r: h["cells"].append(h["cells"][0]))

    def test_fake_owner_verdict_rejected(self):
        self.rejects("R13_FORGED_REVIEW_ACCEPTANCE",
                     lambda h, r: h["counts"].update(owner_acceptances=1))

    def test_wrong_question_rejected(self):
        self.rejects("R13_NATIVE_SOURCE_IDENTITY_DRIFT",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"].update(
                         source_question_id="WRONG"))

    def test_missing_or_blank_question_id_rejected(self):
        for invalid_qid in (None, "", "  ", 42):
            with self.subTest(question_id=invalid_qid):
                def mutate(handoff, reports):
                    cell = handoff["cells"][0]
                    cell["qrt_hypothesis_not_a_verdict"]["primary_question_id"] = invalid_qid
                    cell["available_scoped_browser_proof"][0]["native_question_id"] = invalid_qid
                    reports["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"][
                        "source_question_id"] = invalid_qid
                self.rejects("R13_NATIVE_SOURCE_IDENTITY_DRIFT", mutate)

    def test_wrong_concept_rejected(self):
        self.rejects("R13_NATIVE_SOURCE_IDENTITY_DRIFT",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"].update(
                         selected_concept_id="WRONG"))

    def test_changed_sha_rejected(self):
        self.rejects("R13_NATIVE_SOURCE_SHA_OR_COPY_DRIFT",
                     lambda h, r: h["cells"][0]["available_scoped_browser_proof"][0].update(
                         sha256="0" * 64))

    def test_false_native_origin_rejected(self):
        self.rejects("R13_NATIVE_SOURCE_SHA_OR_COPY_DRIFT",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"].update(
                         native_renderer_only=False))

    def test_string_flag_rejected(self):
        self.rejects("R13_INVALID_NATIVE_STATUS_FIELDS",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"]["observed"].update(
                         assistance_marked="false"))

    def test_forged_complete_flag_rejected(self):
        self.rejects("R13_FORGED_NATIVE_FINDINGS",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"].update(
                         technical_round_trip_complete=True))

    def test_removed_negative_findings_rejected(self):
        self.rejects("R13_FORGED_NATIVE_FINDINGS",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"].update(
                         findings=[]))

    def test_false_release_rejected(self):
        self.rejects("R13_FAKE_REVIEW_OR_RELEASE",
                     lambda h, r: r["QRT-RETRIEVE-D1"][0]["postcommit_native_journey"].update(
                         release="GO"))

    def test_source_hold_not_reclassified_as_native(self):
        self.rejects("R13_FORGED_SOURCE_HOLD",
                     lambda h, r: h["cells"][-1].update(blocking_source_author_action=None))

    def test_future_engineering_green_is_never_academic_green(self):
        h, r = fixture()
        n, sha = r["QRT-RETRIEVE-D1"]
        for field in CHECKS:
            n["postcommit_native_journey"]["observed"][field] = True
        n["postcommit_native_journey"].update(findings=[], technical_round_trip_complete=True)
        h["cells"][0]["available_scoped_browser_proof"][0].update(
            distinct_technical_findings=[], technical_round_trip_complete=True)
        result = summarize(h, r)
        self.assertEqual(result["counts"]["native_round_trips_complete"], 1)
        self.assertFalse(result["native_cells"][0]["academic_approved"])
        self.assertFalse(result["native_cells"][0]["owner_approved"])
        self.assertEqual(result["release"], "HOLD")


if __name__ == "__main__":
    unittest.main()
