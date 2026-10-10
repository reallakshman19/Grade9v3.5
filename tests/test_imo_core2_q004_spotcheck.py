"""Self-check-only Q004 private-source checklist falsifiers; all bytes invented."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "TEST/imo-research"))

from core2_source_acquisition_gaps import (  # noqa: E402
    BUCKET, HANDOFF, artifact_paths, inventory, load,
    private_workspace, CENSUS, SourceGapError,
)
import q004_private_spotcheck as q4  # noqa: E402


class Q004PrivateSpotcheckTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        self.workspace = private_workspace(
            Path(self.root.name) / "q004-private", create=True
        )
        _, docs = inventory(load(CENSUS), load(HANDOFF))
        self.doc = docs[q4.DOC_ID]
        self.bytes = b"%PDF-1.4\n% ONLY SYNTHETIC TEST BYTES\n%%EOF\n"
        self.sha = hashlib.sha256(self.bytes).hexdigest()

    def install_synthetic_import(self):
        snapshot, receipt = artifact_paths(self.workspace, q4.DOC_ID)
        snapshot.write_bytes(self.bytes)
        receipt.write_text(json.dumps({
            "acquisition_id": "ACQ-SYNTHETIC-ONLY", "version": "1.0.0",
            "subject": "TEST", "bucket_id": BUCKET,
            "resource_ref": q4.DOC_ID, "source_kind": "FILE",
            "requested_locator": self.doc["requested_pdf_url"],
            "resolved_locator": str(Path(self.root.name) / "operator-synthetic.pdf"),
            "acquired_at": "2026-10-10T00:00:00+00:00",
            "media_type": "application/pdf", "byte_length": len(self.bytes),
            "sha256": self.sha, "snapshot_ref": str(snapshot),
        }) + "\n", encoding="utf-8")
        return snapshot, receipt

    @staticmethod
    def fill(packet):
        packet = copy.deepcopy(packet)
        packet["source_components"] = copy.deepcopy(q4.FIELDS)
        packet["spotcheck_actor_role"] = "SELF_SPOT_CHECK"
        packet["spotcheck_timestamp_utc"] = "2026-10-10T04:50:00Z"
        return packet

    def test_template_without_pdf_is_explicitly_nonadmitting(self):
        packet = q4.make_template(None)
        self.assertIsNone(packet["snapshot_sha256"])
        self.assertEqual(packet["historical_version_comparison"],
                         "NOT_CHECKED_NO_RETAINED_BYTES")
        self.assertEqual(len(packet["source_components"]), 9)
        self.assertTrue(all(s == "NOT_CHECKED"
                            for s in packet["source_components"].values()))
        result = q4.evaluate(packet, None)
        self.assertEqual(result["status"], q4.STATUS_MISSING)
        self.assertEqual((result["source_custody_hold"],
                          result["core2_eligible"], result["core2_admitted"]),
                         (68, False, False))

    def test_synthetic_import_snapshot_digest_is_exact_but_version_differs(self):
        self.install_synthetic_import()
        packet = q4.make_template(self.workspace)
        self.assertEqual(packet["snapshot_sha256"], self.sha)
        self.assertEqual(packet["snapshot_byte_length"], len(self.bytes))
        self.assertEqual(packet["historical_version_comparison"],
                         "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION")
        result = q4.evaluate(self.fill(packet), self.workspace)
        self.assertEqual(result["status"], q4.STATUS_VERSION)
        self.assertIn("SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED",
                      result["blocking_codes"])
        self.assertEqual(result["source_custody_hold"], 68)

    def test_synthetic_no_receipt_cannot_claim_bogus_sha(self):
        packet = q4.make_template(None)
        packet["snapshot_sha256"] = "a" * 64
        result = q4.evaluate(packet, None)
        self.assertEqual(result["status"], q4.STATUS_MISSING)
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      result["blocking_codes"])

    def test_corrupt_stored_snapshot_stays_hold(self):
        snapshot, _ = self.install_synthetic_import()
        packet = q4.make_template(self.workspace)
        snapshot.write_bytes(b"NOT-PDF")
        result = q4.evaluate(packet, self.workspace)
        self.assertEqual(result["status"], q4.STATUS_MISSING)

    def test_stale_receipt_digest_rejected(self):
        self.install_synthetic_import()
        packet = q4.make_template(self.workspace)
        packet["snapshot_sha256"] = "a" * 64
        result = q4.evaluate(packet, self.workspace)
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      result["blocking_codes"])

    def test_original_key_cannot_change(self):
        packet = q4.make_template(None)
        packet["printed_source_key_sighted"] = "C"
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_math_distractor_oracle_cannot_change(self):
        packet = q4.make_template(None)
        packet["derived_math"]["other_choice_outputs_at_x_zero"]["C"] = -1
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_three_archived_authored_goldens_cannot_claim_source_core2(self):
        # Historical PR #333 golden fixtures are WHOLLY_AUTHORED_NOT_SOF,
        # regardless of their proposed EXPLAIN-D2/MODEL-D3/JUSTIFY-D4 labels.
        for authored_id in (
            "GOLDEN-IMO327-EXPLAIN-D2",
            "GOLDEN-IMO327-MODEL-D3",
            "GOLDEN-IMO327-JUSTIFY-D4",
        ):
            packet = q4.make_template(None)
            packet["question_id"] = authored_id
            result = q4.evaluate(packet, None)
            self.assertEqual(result["core2_admitted"], False)
            self.assertEqual(result["source_custody_hold"], 68)
            self.assertIn(
                "PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                result["blocking_codes"],
            )

    def test_original_source_document_identity_is_pinned(self):
        packet = q4.make_template(None)
        packet["source_url"] = "https://evil.example.org/paper.pdf"
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_item_and_answer_page_are_pinned(self):
        packet = q4.make_template(None)
        packet["source_page_index"] = 1
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      q4.evaluate(packet, None)["blocking_codes"])
        packet = q4.make_template(None)
        packet["source_key_page_index"] = 0
        self.assertIn("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_source_protected_options_and_stems_cannot_be_inserted(self):
        for extra in ("original_source_stem", "publisher_options",
                      "figure_pixel_data", "pdf_bytes"):
            packet = q4.make_template(None)
            packet[extra] = "UNAUTHORIZED_SOURCE_CONTENT"
            with self.assertRaises(SourceGapError):
                q4.evaluate(packet, None)

    def test_fake_rights_or_admission_rejected(self):
        for key, forged in (("source_rights", "GRANTED"),
                            ("core2_eligible", True),
                            ("core2_admitted", True),
                            ("learner_published", True),
                            ("principal_independence", "INDEPENDENT"),
                            ("review_mode", "INDEPENDENT_REVIEW")):
            packet = q4.make_template(None)
            packet[key] = forged
            self.assertIn(
                "PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH",
                q4.evaluate(packet, None)["blocking_codes"])

    def test_all_nine_exact_status_categories_are_required(self):
        packet = q4.make_template(None)
        packet["source_components"].pop("captions")
        with self.assertRaises(SourceGapError):
            q4.evaluate(packet, None)

    def test_source_component_lists_not_treated_as_status_claim(self):
        packet = q4.make_template(None)
        packet["source_components"]["options"] = ["copied source choice"]
        self.assertIn("UNRECOGNIZED_OR_FALSE_SOURCE_COMPONENT_STATUS",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_premature_component_verification_rejected(self):
        packet = q4.make_template(None)
        packet["source_components"]["stem"] = "VERIFIED_BY_SOF"
        self.assertIn("UNRECOGNIZED_OR_FALSE_SOURCE_COMPONENT_STATUS",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_nine_components_incomplete_even_if_role_and_date_set(self):
        packet = q4.make_template(None)
        packet["spotcheck_actor_role"] = "SELF_SPOT_CHECK"
        packet["spotcheck_timestamp_utc"] = "2026-10-10T04:55:00Z"
        self.assertIn("NINE_COMPONENT_SELF_CHECK_INCOMPLETE",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_completed_self_check_requires_named_role_and_valid_utc(self):
        packet = self.fill(q4.make_template(None))
        packet["spotcheck_actor_role"] = None
        packet["spotcheck_timestamp_utc"] = "2026-10-10"
        findings = q4.evaluate(packet, None)["blocking_codes"]
        self.assertIn("COMPLETED_CHECK_REQUIRES_NAMED_SELF_ROLE_AND_UTC",
                      findings)
        self.assertIn("SPOT_CHECK_TIMESTAMP_INVALID", findings)

    def test_third_party_role_claim_rejected(self):
        packet = q4.make_template(None)
        packet["spotcheck_actor_role"] = "INDEPENDENT_SOF_REVIEWER"
        self.assertIn("REVIEW_AUTHORITY_INVALID",
                      q4.evaluate(packet, None)["blocking_codes"])

    def test_synthetic_positive_mechanical_gate_is_still_68_holds(self):
        """Patch matching fingerprint just as a hypothetical unit fixture."""
        digest = self.sha
        length = len(self.bytes)
        template = q4.make_template(None)
        template["snapshot_sha256"] = digest
        template["snapshot_byte_length"] = length
        template["historical_version_comparison"] = (
            "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY"
        )
        filled = self.fill(template)
        with mock.patch.object(
            q4, "_document",
            return_value=(self.doc, "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY",
                          digest, length),
        ):
            result = q4.evaluate(filled, self.workspace)
        self.assertEqual(result["status"], q4.STATUS_SELF)
        self.assertTrue(result["self_attestation_not_source_certificate"])
        self.assertEqual(result["source_custody_hold"], 68)
        self.assertFalse(result["core2_admitted"])
        self.assertEqual(result["source_rights"], "NOT_REVIEWED")

    def test_hypothetical_byte_match_not_enough_without_nine_dispositions(self):
        template = q4.make_template(None)
        template["snapshot_sha256"] = self.sha
        template["snapshot_byte_length"] = len(self.bytes)
        template["historical_version_comparison"] = (
            "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY"
        )
        with mock.patch.object(
            q4, "_document",
            return_value=(self.doc, "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY",
                          self.sha, len(self.bytes)),
        ):
            result = q4.evaluate(template, self.workspace)
        self.assertEqual(result["status"], q4.STATUS_INCOMPLETE)
        self.assertEqual(result["source_custody_hold"], 68)

    def test_assessment_must_be_private_file_not_symlink(self):
        path = Path(self.root.name) / "outside.json"
        path.write_text("{}", encoding="utf-8")
        with self.assertRaises(SourceGapError):
            q4._assessment_path(self.workspace, path)
        inside = self.workspace / "real.json"
        inside.write_text("{}", encoding="utf-8")
        link = self.workspace / "alias.json"
        link.symlink_to(inside)
        with self.assertRaises(SourceGapError):
            q4._assessment_path(self.workspace, link)


    def test_prepared_bundle_assessment_inside_exact_private_child_is_accepted(self):
        directory = self.workspace / "q004-private-review"
        directory.mkdir(mode=0o700)
        packet = directory / "q004.inspection.json"
        packet.write_text("{}", encoding="utf-8")
        self.assertEqual(q4._assessment_path(self.workspace, packet), packet)
        other = directory / "other.json"
        other.write_text("{}", encoding="utf-8")
        with self.assertRaises(SourceGapError):
            q4._assessment_path(self.workspace, other)

    def test_prepared_bundle_assessment_rejects_public_child_or_symlink(self):
        directory = self.workspace / "q004-private-review"
        directory.mkdir(mode=0o700)
        packet = directory / "q004.inspection.json"
        packet.write_text("{}", encoding="utf-8")
        directory.chmod(0o755)
        with self.assertRaises(SourceGapError):
            q4._assessment_path(self.workspace, packet)
        directory.chmod(0o700)
        packet.unlink()
        actual = directory / "actual.json"
        actual.write_text("{}", encoding="utf-8")
        packet.symlink_to(actual)
        with self.assertRaises(SourceGapError):
            q4._assessment_path(self.workspace, packet)


if __name__ == "__main__":
    unittest.main()
