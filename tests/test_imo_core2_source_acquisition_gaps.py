"""Offline, synthetic checks for private document acquisition and 68-item HOLD reporting."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "TEST/imo-research"))
from core2_source_acquisition_gaps import (  # noqa: E402
    BUCKET, CENSUS, HANDOFF, SOURCE_IDS, SourceGapError,
    FINGERPRINTS, HISTORICAL_PINS, HISTORICAL_PROBE_ARCHIVE_SHA256,
    RIGHTS_NOTICE, public_rights_notice,
    acquire, artifact_paths, compare_historical_fingerprint,
    historical_fingerprints, inventory, load, private_workspace,
    receipt_status, report,
)


class Core2SourceAcquisitionGapTests(unittest.TestCase):
    def setUp(self):
        self.census, self.handoff = load(CENSUS), load(HANDOFF)
        self.rows, self.docs = inventory(self.census, self.handoff)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace_path = Path(self.tmp.name) / "restricted"
        self.workspace = private_workspace(self.workspace_path, create=True)
        self.sample = self.docs["SOF-IMO-G09-SAMPLE-2026-27"]
        self.payload = b"%PDF-1.4\n% SYNTHETIC INVENTED TEST SNAPSHOT\n%%EOF\n"

    def write_fake_receipt(self, doc=None, changes=None, pdf=None):
        """Build test-only acquisition bytes; never claim SOF source identity."""
        doc = doc or self.sample
        snapshot, receipt = artifact_paths(self.workspace, doc["source_id"])
        snapshot.write_bytes(self.payload if pdf is None else pdf)
        sha = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        data = {
            "acquisition_id": "ACQ-SYNTHETIC-PRIVATE-TEST",
            "version": "1.0.0", "subject": "TEST",
            "bucket_id": BUCKET,
            "resource_ref": doc["source_id"],
            "source_kind": "URL",
            "requested_locator": doc["requested_pdf_url"],
            "resolved_locator": doc["requested_pdf_url"],
            "acquired_at": "2026-10-10T00:00:00+00:00",
            "media_type": "application/pdf",
            "byte_length": len(snapshot.read_bytes()),
            "sha256": sha,
            "snapshot_ref": str(snapshot),
        }
        if changes:
            data.update(changes)
        receipt.write_text(json.dumps(data) + "\n", encoding="utf-8")
        return snapshot, receipt

    def test_census_68_and_four_source_counts(self):
        self.assertEqual(len(self.rows), 68)
        self.assertEqual({k: v["position_count_in_68"]
                          for k, v in self.docs.items()}, SOURCE_IDS)

    def test_default_report_all_holds(self):
        output = report(self.census, self.handoff)
        self.assertEqual((output["question_count"], output["document_count"]), (68, 4))
        self.assertEqual(output["verified_retained_document_count"], 0)
        self.assertEqual((output["source_custody_hold"],
                          output["core2_eligible"], output["core2_admitted"],
                          output["learner_published"]), (68, 0, 0, 0))
        self.assertEqual(len(output["questions"]), len({
            x["question_id"] for x in output["questions"]}))

    def test_all_source_items_have_next_action(self):
        self.assertTrue(all(row["next_action"] and row["blocking_codes"]
                            for row in report(self.census, self.handoff)["questions"]))

    def test_missing_document_report_does_not_invent_digest(self):
        output = report(self.census, self.handoff)
        self.assertTrue(all(d["receipt_status"] == "NOT_ACQUIRED"
                            for d in output["documents"]))
        self.assertEqual(output["historical_version_matches"], 0)
        self.assertEqual(output["verified_retained_document_count"], 0)
        self.assertTrue(all(
            item["historical_version_comparison"] ==
            "NOT_CHECKED_NO_RETAINED_BYTES"
            for item in output["documents"]))

    def test_sighted_public_notice_is_not_specific_source_licence(self):
        obj = public_rights_notice(self.docs)
        self.assertEqual(obj["general_contact_email"], "info@sofworld.org")
        self.assertEqual(obj["notice_summary"],
                         "GENERAL_SOF_SITE_NOTICE_REQUIRES_PRIOR_WRITTEN_CONSENT_FOR_COPY_OR_USE")
        self.assertEqual(obj["rights_to_publish_original_works"], "NOT_EVIDENCED")
        self.assertIsNone(obj["permission_request_receipt"])
        self.assertEqual(obj["canonical_source_admission_count"], 0)
        result = report(self.census, self.handoff)
        self.assertEqual(result["source_specific_reproduction_grants_evidenced"], 0)
        self.assertEqual(result["source_custody_hold"], 68)
        self.assertEqual(result["core2_admitted"], 0)
        self.assertTrue(all(
            "SOURCE_SPECIFIC_WRITTEN_PERMISSION_NOT_EVIDENCED" in row["blocking_codes"]
            for row in result["questions"]))

    def test_public_notice_does_not_assume_specific_pdf_rightsholder(self):
        obj = public_rights_notice(self.docs)
        self.assertFalse(obj["publisher_rights_holder_for_all_mirror_pdfs_verified"])
        self.assertEqual(obj["notice_scope"],
                         "GENERAL_OFFICIAL_SITE_FOOTER_NOT_SPECIFIC_FOUR_PDF_LICENSE_REVIEW")

    def test_rights_record_fake_grant_is_rejected(self):
        obj = load(RIGHTS_NOTICE)
        obj["written_reproduction_permission_received"] = True
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_false_sent_email_is_rejected(self):
        obj = load(RIGHTS_NOTICE)
        obj["permission_request_sent"] = True
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_fake_source_approval_is_rejected(self):
        obj = load(RIGHTS_NOTICE)
        obj["documents"][0]["publication_authorized"] = True
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_unmatched_source_count_is_rejected(self):
        obj = load(RIGHTS_NOTICE)
        obj["documents"].pop()
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_cannot_relabel_notice_as_specific_licence(self):
        obj = load(RIGHTS_NOTICE)
        obj["notice_scope"] = "SOF_GRANTS_ALL_FOUR_PDFS"
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_cannot_invent_licensed_figure_use(self):
        obj = load(RIGHTS_NOTICE)
        obj["figure_reuse_authorized"] = True
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_integer_alias_cannot_impersonate_boolean(self):
        obj = load(RIGHTS_NOTICE)
        obj["written_reproduction_permission_received"] = 0
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_rights_record_boolean_alias_cannot_impersonate_zero(self):
        obj = load(RIGHTS_NOTICE)
        obj["canonical_source_admission_count"] = False
        with self.assertRaises(SourceGapError):
            public_rights_notice(self.docs, obj)

    def test_historical_artifact_sha_and_four_pins_are_frozen(self):
        meta = load(FINGERPRINTS)
        self.assertEqual(meta["source_artifact_zip_sha256"],
                         HISTORICAL_PROBE_ARCHIVE_SHA256)
        self.assertEqual(meta["source_workflow_run"], 37868836390)
        self.assertEqual(meta["source_job_id"], 113621920381)
        self.assertEqual(meta["source_artifact_id"], 11588893886)
        self.assertFalse(meta["artifact_contains_pdf_bytes"])
        self.assertEqual(meta["retained_original_pdf_documents"], 0)
        self.assertEqual(meta["verified_source_item_custody"], 0)
        self.assertEqual(meta["rights_status"], "NOT_REVIEWED")
        fp = historical_fingerprints(self.docs, meta)
        self.assertEqual(len(fp), 4)
        self.assertEqual(sum(x["byte_length"] for x in fp.values()), 18670898)
        self.assertEqual(fp["SOF-IMO-G09-SAMPLE-2026-27"]["sha256"],
                         "e1229c45cbecb13fe4e8ac65e83c1eec029e6eea83e601cc591e7ce97a65022f")

    def test_historical_digest_tampering_rejected(self):
        meta = load(FINGERPRINTS)
        meta["documents"][0]["sha256"] = "a" * 64
        with self.assertRaises(SourceGapError):
            historical_fingerprints(self.docs, meta)

    def test_historical_wrong_zip_digest_rejected(self):
        meta = load(FINGERPRINTS)
        meta["source_artifact_zip_sha256"] = "a" * 64
        with self.assertRaises(SourceGapError):
            historical_fingerprints(self.docs, meta)

    def test_historical_fake_retained_source_rejected(self):
        meta = load(FINGERPRINTS)
        meta["documents"][0]["snapshot_retained"] = True
        with self.assertRaises(SourceGapError):
            historical_fingerprints(self.docs, meta)

    def test_historical_fake_rights_grant_rejected(self):
        meta = load(FINGERPRINTS)
        meta["rights_status"] = "AUTHORIZED"
        with self.assertRaises(SourceGapError):
            historical_fingerprints(self.docs, meta)

    def test_historical_wrong_source_url_rejected(self):
        meta = load(FINGERPRINTS)
        meta["documents"][0]["requested_url"] = "https://example.org/fake.pdf"
        with self.assertRaises(SourceGapError):
            historical_fingerprints(self.docs, meta)

    def test_historical_duplicate_source_rejected(self):
        meta = load(FINGERPRINTS)
        meta["documents"][1] = copy.deepcopy(meta["documents"][0])
        with self.assertRaises(SourceGapError):
            historical_fingerprints(self.docs, meta)

    def test_historical_byte_match_oracle_still_does_not_admit_source(self):
        self.write_fake_receipt()
        status, _ = receipt_status(self.sample, self.workspace)
        snap, receipt_path = artifact_paths(self.workspace, self.sample["source_id"])
        own = load(receipt_path)
        fake_pin = {"sha256": own["sha256"], "byte_length": own["byte_length"]}
        self.assertEqual(compare_historical_fingerprint(
            self.sample, self.workspace, status, fake_pin),
            "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY")
        self.assertEqual(report(self.census, self.handoff,
                                self.workspace)["core2_admitted"], 0)
        # This deliberately injected fake fingerprint is NOT the production pin:
        self.assertNotEqual(fake_pin["sha256"],
                            HISTORICAL_PINS[self.sample["source_id"]][1])

    def test_historical_matching_hash_with_wrong_length_does_not_match(self):
        self.write_fake_receipt()
        status, _ = receipt_status(self.sample, self.workspace)
        _, receipt_path = artifact_paths(self.workspace, self.sample["source_id"])
        own = load(receipt_path)
        probe = {"sha256": own["sha256"],
                 "byte_length": own["byte_length"] + 1}
        self.assertEqual(compare_historical_fingerprint(
            self.sample, self.workspace, status, probe),
            "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION")

    def test_synthetic_import_is_different_version_and_all_items_hold(self):
        self.write_fake_receipt()
        output = report(self.census, self.handoff, self.workspace)
        self.assertEqual(output["historical_version_matches"], 0)
        documents = [d for d in output["documents"]
                     if d["source_id"] == self.sample["source_id"]]
        self.assertEqual(len(documents), 1)
        self.assertEqual(
            documents[0]["historical_version_comparison"],
            "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION")
        sample_rows = [q for q in output["questions"]
                       if q["source_id"] == self.sample["source_id"]]
        self.assertEqual(len(sample_rows), 10)
        self.assertTrue(all("REVIEW_SOURCE_DOCUMENT_VERSION_DRIFT"
                            in row["blocking_codes"] for row in sample_rows))
        self.assertEqual((output["source_custody_hold"],
                          output["core2_admitted"], output["learner_published"]),
                         (68, 0, 0))

    def test_page_observations_distinguish_unobserved(self):
        questions = report(self.census, self.handoff)["questions"]
        observed = [q for q in questions if q["observed_pdf_page_index"] is not None]
        unknown = [q for q in questions if q["observed_pdf_page_index"] is None]
        self.assertTrue(observed and unknown)
        self.assertTrue(all("ITEM_PAGE_OBSERVATION_NOT_COMPONENT_CUSTODY"
                            in q["blocking_codes"] for q in observed))
        self.assertTrue(all("ITEM_PAGE_LOCATOR_UNOBSERVED"
                            in q["blocking_codes"] for q in unknown))

    def test_discrepancy_cases_still_held(self):
        output = report(self.census, self.handoff)
        self.assertEqual(sum("RECORDED_SOURCE_DISCREPANCY_OPEN"
                             in x["blocking_codes"] for x in output["questions"]), 11)

    def test_synthetic_retained_byte_receipt_without_admission(self):
        self.write_fake_receipt()
        output = report(self.census, self.handoff, self.workspace)
        self.assertEqual(output["verified_retained_document_count"], 1)
        self.assertEqual(output["source_custody_hold"], 68)
        self.assertEqual(output["core2_admitted"], 0)
        sample = [x for x in output["questions"] if x["source_id"] ==
                  self.sample["source_id"]]
        self.assertEqual(len(sample), 10)
        self.assertTrue(all(x["document_receipt_status"] ==
                            "VERIFIED_RETAINED_BYTES_ONLY" for x in sample))
        self.assertTrue(all(x["status"] == "HOLD_NO_CORE2_ADMISSION" for x in sample))

    def test_bad_digest_cannot_verify(self):
        self.write_fake_receipt(changes={"sha256": "a" * 64})
        status, codes = receipt_status(self.sample, self.workspace)
        self.assertEqual((status, codes),
                         ("INVALID", ["RETAINED_DOCUMENT_RECEIPT_INVALID"]))

    def test_source_url_swap_rejected(self):
        self.write_fake_receipt(changes={
            "requested_locator": "https://example.com/other.pdf"})
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_www_same_host_redirect_is_allowed(self):
        self.write_fake_receipt(changes={
            "resolved_locator": "https://www.sofworld.org/download/file/fid/73719"
        })
        self.assertEqual(receipt_status(self.sample, self.workspace)[0],
                         "VERIFIED_RETAINED_BYTES_ONLY")

    def test_changed_source_handoff_url_rejected_even_with_matching_census(self):
        handoff = copy.deepcopy(self.handoff)
        census = copy.deepcopy(self.census)
        identity = self.sample["source_id"]
        evil = "https://untrusted.example.org/other.pdf"
        next(d for d in handoff["source_documents_queue"]
             if d["source_id"] == identity)["requested_pdf_url"] = evil
        for row in census["records"]:
            if row["source_id"] == identity:
                row["source_document_url"] = evil
        with self.assertRaises(SourceGapError):
            report(census, handoff)

    def test_cross_domain_redirect_rejected(self):
        self.write_fake_receipt(changes={
            "resolved_locator": "https://otherhost.example.net/item.pdf"})
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_missing_snapshot_rejected(self):
        snapshot, _ = self.write_fake_receipt()
        snapshot.unlink()
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "NOT_ACQUIRED")

    def test_fake_pdf_header_rejected(self):
        self.write_fake_receipt(pdf=b"<html>not pdf</html>")
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_acquisition_wrong_source_id_rejected(self):
        self.write_fake_receipt(changes={"resource_ref": "WRONG"})
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_symlink_receipt_rejected(self):
        snapshot, receipt = self.write_fake_receipt()
        safe = self.workspace / "replacement.json"
        receipt.rename(safe)
        receipt.symlink_to(safe)
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_private_dir_must_be_absolute(self):
        with self.assertRaises(SourceGapError):
            private_workspace(Path("relative/source-data"), create=True)

    def test_private_dir_cannot_be_checkout(self):
        with self.assertRaises(SourceGapError):
            private_workspace(REPO / "TEST", create=False)

    def test_private_dir_rejects_public_permissions(self):
        os.chmod(self.workspace, 0o755)
        with self.assertRaises(SourceGapError):
            private_workspace(self.workspace)

    def test_private_dir_rejects_symlink(self):
        link = Path(self.tmp.name) / "link"
        link.symlink_to(self.workspace, target_is_directory=True)
        with self.assertRaises(SourceGapError):
            private_workspace(link)

    def test_source_seed_count_tampering_fails(self):
        census = copy.deepcopy(self.census)
        census["records"].pop()
        with self.assertRaises(SourceGapError):
            report(census, self.handoff)

    def test_wrong_handoff_document_count_fails(self):
        handoff = copy.deepcopy(self.handoff)
        handoff["source_documents_queue"][0]["position_count_in_68"] = 25
        with self.assertRaises(SourceGapError):
            report(self.census, handoff)

    def test_frozen_core2_admission_cannot_be_faked(self):
        census = copy.deepcopy(self.census)
        census["records"][0]["core2_admitted"] = True
        with self.assertRaises(SourceGapError):
            report(census, self.handoff)

    def test_synthetic_network_acquisition_reuses_source_pipeline(self):
        def fetch(*, url, subject, bucket_id, resource_ref, acquired_at,
                  snapshot_output):
            snapshot_output.write_bytes(self.payload)
            sha = hashlib.sha256(self.payload).hexdigest()
            return {
                "acquisition_id": "ACQ-SYNTHETIC-ONLY",
                "version": "1.0.0", "subject": subject, "bucket_id": bucket_id,
                "resource_ref": resource_ref, "source_kind": "URL",
                "requested_locator": url, "resolved_locator": url,
                "acquired_at": acquired_at, "media_type": "application/pdf",
                "byte_length": len(self.payload), "sha256": sha,
                "snapshot_ref": str(snapshot_output),
            }
        with mock.patch(
            "core2_source_acquisition_gaps.source_pipeline.acquire_url",
            side_effect=fetch,
        ) as f:
            outcome = acquire(self.sample, self.workspace)
            self.assertEqual(f.call_count, 1)
        self.assertEqual(outcome["status"], "VERIFIED_RETAINED_BYTES_ONLY")
        snapshot, receipt = artifact_paths(self.workspace, self.sample["source_id"])
        self.assertTrue(snapshot.is_file() and receipt.is_file())
        self.assertEqual(stat.S_IMODE(snapshot.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
        self.assertEqual(outcome["core2_eligible"], False)
        self.assertEqual(receipt_status(self.sample, self.workspace)[0],
                         "VERIFIED_RETAINED_BYTES_ONLY")

    def test_offline_import_from_browser_download_is_not_authenticated(self):
        downloaded = Path(self.tmp.name) / "operator-browser-download.pdf"
        downloaded.write_bytes(self.payload)
        result = acquire(self.sample, self.workspace, local_file=downloaded)
        self.assertEqual(result["status"],
                         "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED")
        self.assertFalse(result["source_origin_authenticated"])
        self.assertFalse(result["core2_admitted"])
        self.assertEqual(result["sha256"],
                         hashlib.sha256(self.payload).hexdigest())
        snapshot, receipt = artifact_paths(self.workspace, self.sample["source_id"])
        self.assertEqual(stat.S_IMODE(snapshot.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
        downloaded.unlink()
        self.assertEqual(receipt_status(self.sample, self.workspace)[0],
                         "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED")
        gaps = report(self.census, self.handoff, self.workspace)
        self.assertEqual(gaps["local_import_document_count"], 1)
        self.assertEqual(gaps["verified_retained_document_count"], 1)
        self.assertEqual(gaps["source_custody_hold"], 68)
        self.assertEqual(gaps["core2_admitted"], 0)
        self.assertTrue(all("LOCAL_FILE_SOURCE_ORIGIN_UNVERIFIED"
                            in item["blocking_codes"]
                            for item in gaps["questions"]
                            if item["source_id"] == self.sample["source_id"]))

    def test_browser_download_html_response_is_rejected_and_deleted(self):
        downloaded = Path(self.tmp.name) / "fake-browser-download.pdf"
        downloaded.write_bytes(b"<html>Error</html>")
        with self.assertRaises(SourceGapError):
            acquire(self.sample, self.workspace, local_file=downloaded)
        snapshot, receipt = artifact_paths(self.workspace, self.sample["source_id"])
        self.assertFalse(snapshot.exists() or receipt.exists())

    def test_offline_import_symlink_source_rejected(self):
        downloaded = Path(self.tmp.name) / "real.pdf"
        downloaded.write_bytes(self.payload)
        link = Path(self.tmp.name) / "alias.pdf"
        link.symlink_to(downloaded)
        with self.assertRaises(SourceGapError):
            acquire(self.sample, self.workspace, local_file=link)

    def test_offline_import_relative_source_rejected(self):
        with self.assertRaises(SourceGapError):
            acquire(self.sample, self.workspace, local_file=Path("download.pdf"))

    def test_offline_import_missing_source_rejected(self):
        with self.assertRaises(SourceGapError):
            acquire(self.sample, self.workspace,
                    local_file=Path(self.tmp.name) / "does-not-exist.pdf")

    def test_offline_import_oversize_file_rejected_without_reading(self):
        downloaded = Path(self.tmp.name) / "oversize.pdf"
        with downloaded.open("wb") as stream:
            stream.truncate(101 * 1024 * 1024)
        with self.assertRaises(SourceGapError):
            acquire(self.sample, self.workspace, local_file=downloaded)

    def test_faked_local_file_receipt_redirect_rejected(self):
        self.write_fake_receipt(changes={
            "source_kind": "FILE",
            "resolved_locator": "https://sofworld.org/download/file/fid/73719",
        })
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_unrecognized_local_file_path_with_repo_origin_rejected(self):
        self.write_fake_receipt(changes={
            "source_kind": "FILE",
            "resolved_locator": str(REPO / "public/original.pdf"),
        })
        self.assertEqual(receipt_status(self.sample, self.workspace)[0], "INVALID")

    def test_network_failure_cleans_partial_snapshot(self):
        def partial(**kwargs):
            kwargs["snapshot_output"].write_bytes(b"partial")
            raise OSError("temporary provider failure")
        with mock.patch(
            "core2_source_acquisition_gaps.source_pipeline.acquire_url",
            side_effect=partial,
        ):
            with self.assertRaises(OSError):
                acquire(self.sample, self.workspace)
        s, receipt = artifact_paths(self.workspace, self.sample["source_id"])
        self.assertFalse(s.exists() or receipt.exists())

    def test_existing_private_snapshot_refuses_overwrite(self):
        self.write_fake_receipt()
        with self.assertRaises(SourceGapError):
            acquire(self.sample, self.workspace)

    def test_original_question_text_never_in_report(self):
        self.write_fake_receipt()
        serialized = json.dumps(report(self.census, self.handoff, self.workspace))
        self.assertNotIn("SYNTHETIC INVENTED TEST SNAPSHOT", serialized)
        self.assertNotIn(str(self.workspace), serialized)


if __name__ == "__main__":
    unittest.main()
