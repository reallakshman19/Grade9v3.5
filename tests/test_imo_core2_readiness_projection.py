"""Executable synthetic/negative checks for non-admitting source-readiness projection.

Fixture bytes and question are INVENTED, not SOF content or an authentication receipt.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "TEST/imo-research"))
from project_core2_readiness import (  # noqa: E402
    CENSUS_PATH, ReadinessError, project,
)
from Shared.library import source_custody  # noqa: E402

QID = "SOF-IMO-G09-SAMPLE-2026-27-Q004"
LOCATOR = "pdf_page_index=0;printed_item=4"


class IMOReadinessProjectionTests(unittest.TestCase):
    def setUp(self):
        self.census = json.loads(CENSUS_PATH.read_text(encoding="utf-8"))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        snapshot = Path(self.temp.name) / "fixture-synthetic.pdf"
        # This is synthetic file content, not a genuine paper or valid SOF PDF.
        payload = b"%PDF-1.4\n% INVENTED PRIVATE TEST BYTES\n%%EOF\n"
        snapshot.write_bytes(payload)
        sha = hashlib.sha256(payload).hexdigest()
        source = next(r for r in self.census["records"] if r["question_id"] == QID)
        acquisition = {
            "acquisition_id": "ACQ-SYNTHETIC-ONLY", "version": "1.0.0",
            "subject": "TEST", "bucket_id": "BUCKET-SYNTHETIC-ONLY",
            "resource_ref": "RESOURCE-SYNTHETIC-ONLY",
            "source_kind": "FILE",
            "requested_locator": source["source_document_url"],
            "resolved_locator": str(snapshot),
            "acquired_at": "2026-10-10",
            "media_type": "application/pdf",
            "byte_length": len(payload),
            "sha256": sha, "snapshot_ref": str(snapshot),
        }
        resource = {
            "_collection": "resources", "id": acquisition["resource_ref"],
            "origin": "SOURCE", "snapshot_digest": sha,
            "snapshot_ref": str(snapshot),
        }
        question = {
            "id": QID, "origin": "ORIGINAL",
            "origin_ref": resource["id"], "source_refs": [resource["id"]],
            "original_identifier": "4",
            "stem": "INVENTED fixture only: select the output relation.",
            "options": ["Invented option A", "Invented option B"],
            "subparts": [], "conditions": [], "figure_refs": [], "hints": [],
            "answer": {"summary": "INVENTED fixture response."},
        }
        proof = {
            "version": "1.0.0",
            "acquisition_ref": acquisition["acquisition_id"],
            "resource_ref": resource["id"],
            "source_item_locator": LOCATOR,
            "source_digest": sha,
            "custody_mode": "EMBEDDED_VERBATIM",
            "comparison_status": "ORIGINAL_EXACT",
            "demand_signature": source_custody.demand_signature(question),
            "components": {
                "original_identifier": "PRESERVED", "stem": "PRESERVED",
                "subparts": "NOT_PRESENT_IN_SOURCE", "options": "PRESERVED",
                "conditions": "NOT_PRESENT_IN_SOURCE",
                "figures": "NOT_PRESENT_IN_SOURCE",
                "captions": "NOT_PRESENT_IN_SOURCE",
                "hints": "NOT_PRESENT_IN_SOURCE",
                "answer_or_rubric": "PRESERVED",
            },
            "notes": ["SYNTHETIC POSITIVE MECHANICS ONLY"],
        }
        question["extensions"] = {"source_custody": proof}
        self.evidence = {
            "schema": "imo-g9-private-custody-evidence-v1",
            "items": [{
                "question_id": QID, "acquisition": acquisition,
                "resource": resource, "question": question,
                "supporting_resources": [],
                "inspected_sections": [LOCATOR],
                "access_status": "FULL_ITEM_INSPECTED",
            }],
        }

    def summary(self, evidence=None):
        return project(self.census,
                       self.evidence if evidence is None else evidence, repo=REPO)

    def status(self, mutate=None):
        evidence = copy.deepcopy(self.evidence)
        if mutate is not None:
            mutate(evidence["items"][0])
        report = self.summary(evidence)
        row = next(x for x in report["items"] if x["question_id"] == QID)
        return report, row

    def test_no_evidence_68_holds_and_no_admission(self):
        report = project(self.census, repo=REPO)
        self.assertEqual(len(report["items"]), 68)
        self.assertEqual(report["technical_spot_check_ready"], 0)
        self.assertEqual(report["source_custody_hold"], 68)
        self.assertEqual(report["technical_spot_check_pending"], 68)
        self.assertEqual((report["core2_eligible"], report["core2_admitted"],
                          report["rights_verified"], report["learner_published"]),
                         (0, 0, 0, 0))

    def test_synthetic_positive_exercises_movable_mechanical_boundary(self):
        report, item = self.status()
        self.assertEqual(report["technical_spot_check_ready"], 1)
        self.assertEqual(report["technical_spot_check_pending"], 67)
        self.assertEqual(report["source_custody_hold"], 68)
        self.assertEqual(item["status"], "READY_FOR_SPOT_CHECK_NOT_ADMITTED")
        self.assertTrue(item["technical_spot_check_ready"])
        self.assertFalse(item["rights_verified"])
        self.assertEqual((report["core2_eligible"], report["core2_admitted"]), (0, 0))

    def test_source_digest_tampered_is_held(self):
        _, item = self.status(lambda x: x["acquisition"].update(sha256="a" * 64))
        self.assertIn("RETAINED_BYTES_DIGEST_OR_SCHEMA_FAILED", item["blocking_codes"])

    def test_source_file_missing_is_held(self):
        _, item = self.status(lambda x: x["acquisition"].update(
            snapshot_ref=str(Path(self.temp.name) / "missing.pdf")))
        self.assertIn("RETAINED_BYTES_DIGEST_OR_SCHEMA_FAILED", item["blocking_codes"])

    def test_missing_snapshot_ref_is_held(self):
        _, item = self.status(lambda x: x["acquisition"].update(snapshot_ref=None))
        self.assertIn("RESTRICTED_SNAPSHOT_REQUIRED", item["blocking_codes"])

    def test_wrong_source_document_is_held(self):
        _, item = self.status(lambda x: x["acquisition"].update(
            requested_locator="https://example.org/unrelated.pdf"))
        self.assertIn("SOURCE_DOCUMENT_MISMATCH", item["blocking_codes"])

    def test_wrong_pdf_page_is_held(self):
        _, item = self.status(lambda x: x["question"]["extensions"][
            "source_custody"].update(
                source_item_locator="pdf_page_index=1;printed_item=4"))
        self.assertIn("PRECISE_SOURCE_ITEM_LOCATOR_MISMATCH",
                      item["blocking_codes"])

    def test_wrong_item_number_is_held(self):
        _, item = self.status(lambda x: x["question"].update(
            original_identifier="14"))
        self.assertIn("PRINTED_QUESTION_NUMBER_MISMATCH", item["blocking_codes"])

    def test_unresolved_components_are_held(self):
        _, item = self.status(lambda x: x["question"]["extensions"][
            "source_custody"]["components"].update(options="UNRESOLVED"))
        self.assertIn("CANONICAL_SOURCE_CUSTODY_PROOF_INVALID",
                      item["blocking_codes"])

    def test_changed_question_without_updated_signature_held(self):
        _, item = self.status(lambda x: x["question"].update(
            stem="INVENTED changed synthetic fixture stem"))
        self.assertIn("CANONICAL_SOURCE_CUSTODY_PROOF_INVALID",
                      item["blocking_codes"])

    def test_without_full_item_access_is_held(self):
        _, item = self.status(lambda x: x.update(
            access_status="SECTION_INSPECTED"))
        self.assertIn("FULL_ITEM_INSPECTION_NOT_RECORDED",
                      item["blocking_codes"])

    def test_author_claim_cannot_become_custody(self):
        _, item = self.status(lambda x: x["question"].update(origin="AUTHORED"))
        self.assertIn("CANONICAL_ITEM_IDENTITY_MISMATCH",
                      item["blocking_codes"])

    def test_source_bytes_in_public_tree_refused(self):
        _, item = self.status(lambda x: x["acquisition"].update(
            snapshot_ref=str(REPO / "public/source.pdf")))
        self.assertIn("RESTRICTED_SNAPSHOT_REQUIRED", item["blocking_codes"])

    def test_rights_claim_alias_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["items"][0]["rights_granted"] = True
        with self.assertRaises(ReadinessError):
            self.summary(evidence)

    def test_fabricated_reviewer_alias_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["items"][0]["academic_approved"] = True
        with self.assertRaises(ReadinessError):
            self.summary(evidence)

    def test_second_item_outside_68_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["items"][0]["question_id"] = "SYNTHETIC-NOT-IN-CENSUS"
        with self.assertRaises(ReadinessError):
            self.summary(evidence)

    def test_duplicate_evidence_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["items"].append(copy.deepcopy(evidence["items"][0]))
        with self.assertRaises(ReadinessError):
            self.summary(evidence)

    def test_frozen_research_census_cannot_be_promoted(self):
        census = copy.deepcopy(self.census)
        census["records"][0]["core2_eligible"] = True
        with self.assertRaises(ReadinessError):
            project(census, repo=REPO)

    def test_frozen_research_census_68_cannot_shrink(self):
        census = copy.deepcopy(self.census)
        census["records"].pop()
        with self.assertRaises(ReadinessError):
            project(census, repo=REPO)


if __name__ == "__main__":
    unittest.main()
