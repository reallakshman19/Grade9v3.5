"""Negative tests for F04 same-run TEST evidence hash chain; no release grant."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools.imo_f04_bound_browser_witness import (
    HTML, MANIFEST, PACKAGE, WIDTHS, evaluate,
)

HEAD = "a" * 40


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")


class EvidenceFixture:
    def __init__(self, root: Path):
        self.repo = root / "repo"
        self.render = root / "render"
        self.audit_path = root / "audit.json"
        self.repo.mkdir()
        self.render.mkdir()
        for selected in (MANIFEST, PACKAGE):
            path = self.repo / selected
            write_json(path, {"TEST": True, "selected": selected.name})
        for name in HTML:
            (self.render / name).write_text("TEST CANONICAL " + name, encoding="utf-8")
        write_json(self.render / "render-receipt.json", {
            "output_roles": ["CORE1A", "CORE2A"],
            "mode": "PAGES", "held_to": "REFERENCE", "gaps": [],
        })
        self.audit = {
            "manifest_sha256": sha((self.repo / MANIFEST).read_bytes()),
            "package_sha256": sha((self.repo / PACKAGE).read_bytes()),
            "release_authorized": False,
            "academic_accepted": False,
            "source_core2_eligible": False,
            "browser_qa": "NOT_RUN",
            "blocking_findings": [],
            "render": {
                "status": "REAL_CANONICAL_TEST_RENDER",
                "navigation_findings": [],
                "index_sha256": sha((self.render / "index.html").read_bytes()),
                "pages": {
                    "CORE1A": {"sha256": sha((self.render / "core1a.html").read_bytes())},
                    "CORE2A": {"sha256": sha((self.render / "core2a.html").read_bytes())},
                },
            },
        }
        self.save_audit()
        self.receipt = {
            "schema": "imo-f02-concept-first-chromium/v2",
            "source": "TEST_CANDIDATE",
            "authentic_core2_admitted": False,
            "mastery_verified": False,
            "human_screen_reader": "NOT_RUN",
            "failures": [],
            "viewports": [
                {"width": width, "focus_after_check": "H3", "page_errors": [],
                 "note": "TEST-only visible behavior; no learner comprehension claim"}
                for width in WIDTHS
            ],
            "printed_svg": {
                "found": True, "count": 3, "visible": 3,
                "allInsideViewBox": True
            },
            "printed_pdf": {
                "bytes": 3456, "status": "GENERATED_NOT_MANUALLY_INSPECTED"
            },
        }
        self.save_receipt()
        folder = self.render / "browser-evidence"
        for width in WIDTHS:
            (folder / f"core1a-{width}.png").write_bytes(b"PNG" * 500)
        (folder / "core1a-print.pdf").write_bytes(b"%PDF" * 500)

    def save_audit(self):
        write_json(self.audit_path, self.audit)

    def save_receipt(self):
        write_json(self.render / "browser-evidence" / "result.json", self.receipt)

    def inspect(self, expected=HEAD, observed=HEAD):
        return evaluate(self.repo, self.render, self.audit_path, expected, observed)


class F04BoundBrowserWitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = EvidenceFixture(Path(self.tmp.name))

    def test_synthetic_chain_is_structural_only_never_a_browser_attestation(self):
        data = self.fixture.inspect()
        self.assertEqual(data["blocking_codes"], [])
        self.assertEqual(data["status"], "LOCAL_EVIDENCE_CHAIN_PRESENT_NOT_ACCEPTANCE")
        self.assertEqual(data["checkout_sha"], HEAD)
        self.assertFalse(data["browser_execution_attested"])
        self.assertFalse(data["academic_accepted"])
        self.assertFalse(data["source_core2_admitted"])
        self.assertFalse(data["learner_mastery_verified"])
        self.assertFalse(data["release_authorized"])
        self.assertEqual(len(data["sha256"]["html"]), 3)
        self.assertEqual(len(data["sha256"]["screenshots"]), 4)

    def test_checkout_sha_missing_invalid_or_cross_commit_is_blocked(self):
        for expected, actual in (
            ("bad", "bad"), (HEAD, "b" * 40),
            ("", HEAD), (HEAD, "NO_GIT_CHECKOUT"),
        ):
            with self.subTest(expected=expected, actual=actual):
                self.assertIn("CHECKOUT_SHA_MISMATCH",
                              self.fixture.inspect(expected, actual)["blocking_codes"])

    def test_tampering_rendered_page_without_regenerating_audit_is_detected(self):
        (self.fixture.render / "core1a.html").write_text(
            "replaced with stale page", encoding="utf-8"
        )
        data = self.fixture.inspect()
        self.assertIn("INDEPENDENT_CANONICAL_DIGEST_MISMATCH", data["blocking_codes"])

    def test_changed_manifest_or_missing_candidate_must_block(self):
        (self.fixture.repo / MANIFEST).write_text("changed", encoding="utf-8")
        self.assertIn("INDEPENDENT_CANONICAL_DIGEST_MISMATCH",
                      self.fixture.inspect()["blocking_codes"])
        (self.fixture.repo / PACKAGE).unlink()
        self.assertIn("SOURCE_INPUT_MISSING", self.fixture.inspect()["blocking_codes"])

    def test_missing_receipt_screenshot_pdf_and_wrong_render_contract(self):
        (self.fixture.render / "render-receipt.json").unlink()
        self.assertIn("RENDER_RECEIPT_UNREADABLE",
                      self.fixture.inspect()["blocking_codes"])
        (self.fixture.render / "browser-evidence" / "core1a-768.png").unlink()
        self.assertIn("BROWSER_SCREENSHOT_MISSING_OR_INVALID",
                      self.fixture.inspect()["blocking_codes"])
        (self.fixture.render / "browser-evidence" / "core1a-print.pdf").unlink()
        self.assertIn("BROWSER_PRINT_PDF_MISSING_OR_INVALID",
                      self.fixture.inspect()["blocking_codes"])
        write_json(self.fixture.render / "render-receipt.json", {
            "output_roles": ["CORE1A", "CORE2"], "mode": "PAGES",
            "held_to": "REFERENCE", "gaps": [],
        })
        self.assertIn("RENDER_RECEIPT_INVALID", self.fixture.inspect()["blocking_codes"])

    def test_malformed_browser_receipt_and_private_errors_do_not_leak(self):
        self.fixture.receipt["failures"] = ["PRIVATE learner response"]
        self.fixture.receipt["viewports"][0]["page_errors"] = ["PRIVATE"]
        self.fixture.save_receipt()
        result = self.fixture.inspect()
        self.assertIn("BROWSER_RECEIPT_RECORDED_FAILURE_OR_MALFORMED",
                      result["blocking_codes"])
        self.assertIn("BROWSER_RECEIPT_PAGE_ERRORS_PRESENT", result["blocking_codes"])
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_self_proclaimed_acceptance_is_rejected(self):
        self.fixture.audit["release_authorized"] = True
        self.fixture.save_audit()
        self.assertIn("CANONICAL_AUTHORITY_UNSAFE", self.fixture.inspect()["blocking_codes"])
        self.fixture.audit["release_authorized"] = False
        self.fixture.audit["render"]["navigation_findings"] = ["REPAIR_NOT_VERIFIED"]
        self.fixture.save_audit()
        self.assertIn("CANONICAL_RENDER_BLOCKED", self.fixture.inspect()["blocking_codes"])

    def test_unreadable_canonical_audit_fails_closed(self):
        self.fixture.audit_path.write_text("{garbage", encoding="utf-8")
        self.assertIn("CANONICAL_AUDIT_UNREADABLE", self.fixture.inspect()["blocking_codes"])


if __name__ == "__main__":
    unittest.main()
