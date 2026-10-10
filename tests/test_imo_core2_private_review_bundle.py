"""Synthetic-only falsifiers for Q004 private source-page review preparation."""
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
import subprocess

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "TEST/imo-research"))

import q004_private_review_bundle as bundle  # noqa: E402
from core2_source_acquisition_gaps import (  # noqa: E402
    SourceGapError, artifact_paths, private_workspace,
)


class PrivateQ004ReviewBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = private_workspace(
            Path(self.tmp.name) / "restricted-source", create=True,
        )
        self.snapshot, _ = artifact_paths(self.workspace, bundle.DOC_ID)
        self.snapshot.write_bytes(b"%PDF-1.4\n% INVENTED ONLY; NOT AN SOF QUESTION\n%%EOF\n")
        self.digest = hashlib.sha256(self.snapshot.read_bytes()).hexdigest()
        self.packet = {
            "question_id": bundle.QID,
            "source_id": bundle.DOC_ID,
            "snapshot_sha256": self.digest,
            "snapshot_byte_length": self.snapshot.stat().st_size,
            "source_page_index": bundle.ITEM_PAGE,
            "source_key_page_index": bundle.KEY_PAGE,
            "historical_version_comparison": "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION",
            "source_components": {key: "NOT_CHECKED" for key in
                                  ("original_identifier", "stem", "subparts",
                                   "options", "conditions", "figures", "captions",
                                   "hints", "answer_or_rubric")},
            "core2_admitted": False,
        }

    @staticmethod
    def render_stub(pdf, page, output):
        output.write_bytes(bundle.PNG_MAGIC + b"SYNTHETIC_PNG_BYTES")
        return None

    def run_with(self, *, status="VERIFIED_RETAINED_BYTES_ONLY",
                 packet=None, renderer=None):
        with (
            mock.patch.object(bundle, "receipt_status", return_value=(status, [])),
            mock.patch.object(bundle, "make_template",
                              return_value=copy.deepcopy(
                                  self.packet if packet is None else packet)),
            mock.patch.object(bundle, "_render_page",
                              side_effect=renderer or self.render_stub),
        ):
            return bundle.prepare(self.workspace)

    def test_private_bundle_binds_exact_sha_both_pages_without_admitting(self):
        out = self.run_with()
        self.assertEqual(out["status"], "PRIVATE_INSPECTION_READY_NOT_ADMITTED")
        self.assertEqual(out["private_page_count"], 2)
        self.assertEqual(out["component_dispositions_completed"], 0)
        self.assertFalse(out["core2_admitted"])
        target = self.workspace / bundle.REVIEW_DIR
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o700)
        packet = json.loads((target / "q004.inspection.json").read_text())
        manifest = json.loads((target / "review-manifest.json").read_text())
        self.assertEqual(packet["snapshot_sha256"], self.digest)
        self.assertTrue(all(v == "NOT_CHECKED"
                            for v in packet["source_components"].values()))
        self.assertEqual(manifest["source_pdf_sha256"], self.digest)
        self.assertEqual([p["pdf_page_index_zero_based"]
                          for p in manifest["images"]], [0, 1])
        self.assertEqual({p["private_filename"] for p in manifest["images"]},
                         {"source-question-page.png", "source-answer-key-page.png"})
        for name in ("q004.inspection.json", "review-manifest.json",
                     "source-question-page.png", "source-answer-key-page.png"):
            self.assertEqual(stat.S_IMODE((target / name).stat().st_mode), 0o600)
        self.assertFalse(manifest["source_origin_authenticated"])
        self.assertFalse(manifest["rights_granted"])
        self.assertFalse(manifest["independent_reviewer_approved"])
        self.assertFalse(manifest["core2_admitted"])

    def test_local_import_can_be_inspected_but_origin_stays_unverified(self):
        out = self.run_with(status="IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED")
        self.assertIn("UNVERIFIED", out["source_retention_status"])
        manifest = json.loads(
            (self.workspace / bundle.REVIEW_DIR / "review-manifest.json").read_text()
        )
        self.assertFalse(manifest["source_origin_authenticated"])
        self.assertFalse(manifest["core2_eligible"])

    def test_missing_or_corrupt_receipt_refuses_bundle(self):
        for status in ("NOT_ACQUIRED", "INVALID"):
            with self.subTest(status=status), self.assertRaises(SourceGapError):
                self.run_with(status=status)
            self.assertFalse((self.workspace / bundle.REVIEW_DIR).exists())

    def test_false_acceptance_claim_rejected_before_render(self):
        p = copy.deepcopy(self.packet)
        p["core2_admitted"] = True
        with self.assertRaises(SourceGapError):
            self.run_with(packet=p)
        self.assertFalse((self.workspace / bundle.REVIEW_DIR).exists())

    def test_missing_digest_wrong_size_and_wrong_page_are_rejected(self):
        for key, invalid in (
            ("snapshot_sha256", None),
            ("snapshot_byte_length", 1234567),
            ("source_page_index", 99),
            ("source_key_page_index", 99),
        ):
            p = copy.deepcopy(self.packet)
            p[key] = invalid
            with self.subTest(key=key), self.assertRaises(SourceGapError):
                self.run_with(packet=p)

    def test_premarked_component_dispositions_are_rejected(self):
        p = copy.deepcopy(self.packet)
        p["source_components"]["stem"] = "PRESENT_SELF_CHECKED"
        with self.assertRaises(SourceGapError):
            self.run_with(packet=p)

    def test_existing_private_bundle_never_overwritten(self):
        target = self.workspace / bundle.REVIEW_DIR
        target.mkdir(mode=0o700)
        marker = target / "keep.txt"
        marker.write_text("previous human evidence")
        with self.assertRaises(SourceGapError):
            self.run_with()
        self.assertEqual(marker.read_text(), "previous human evidence")

    def test_failed_second_page_removes_entire_partial_bundle(self):
        def broken(pdf, page, output):
            if page == bundle.KEY_PAGE:
                raise SourceGapError("simulated key-page failure")
            return self.render_stub(pdf, page, output)
        with self.assertRaises(SourceGapError):
            self.run_with(renderer=broken)
        self.assertFalse((self.workspace / bundle.REVIEW_DIR).exists())

    def test_rejects_world_readable_workspace(self):
        os.chmod(self.workspace, 0o755)
        with self.assertRaises(SourceGapError):
            self.run_with()

    def test_renderer_rejects_non_png_bytes(self):
        out = self.workspace / "incorrect.png"
        def fake_run(argv, **kwargs):
            Path(argv[-1] + ".png").write_bytes(b"not a png at all")
            return mock.Mock(returncode=0)
        with (
            mock.patch.object(bundle.shutil, "which", return_value="/usr/bin/pdftoppm"),
            mock.patch.object(bundle.subprocess, "run", side_effect=fake_run),
            self.assertRaises(SourceGapError),
        ):
            bundle._render_page(self.snapshot, 0, out)

    def test_renderer_timeout_rejected_without_printing_pdf_content(self):
        with (
            mock.patch.object(bundle.shutil, "which", return_value="/usr/bin/pdftoppm"),
            mock.patch.object(
                bundle.subprocess, "run",
                side_effect=subprocess.TimeoutExpired(cmd="pdftoppm", timeout=60),
            ),
            self.assertRaises(SourceGapError),
        ):
            bundle._render_page(self.snapshot, 0, self.workspace / "timeout.png")


if __name__ == "__main__":
    unittest.main()
