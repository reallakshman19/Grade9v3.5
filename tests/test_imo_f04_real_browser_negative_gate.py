"""Fail-closed F04 real-browser negative receipt tests: never learner acceptance."""
import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from Shared.tools.imo_f04_real_browser_negative_gate import FLAGS, findings, main

PAGE = b"<html>TEST generated authored Core2A</html>"
PAGE_SHA = hashlib.sha256(PAGE).hexdigest()


def receipt() -> dict:
    return {
        "schema": "imo-f04-real-browser-negatives/v1",
        "source": "TEST_AUTHORED_CORE2A",
        "viewport_width": 390,
        "status": "NEGATIVE_PROBES_OK",
        "flags": {flag: True for flag in FLAGS},
        "blocking_codes": [],
        "chromium_execution_attested": False,
        "authentic_core2_admitted": False,
        "mastery_verified": False,
        "academic_accepted": False,
        "release_authorized": False,
        "core2a_sha256": PAGE_SHA,
    }


class F04RealBrowserNegativeGateTests(unittest.TestCase):
    def test_synthetic_good_structure_still_never_grants_authority(self):
        self.assertEqual(findings(receipt(), PAGE_SHA), [])
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "receipt.json"
            html = Path(tmp) / "core2a.html"
            source.write_text(json.dumps(receipt()), encoding="utf-8")
            html.write_bytes(PAGE)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["--receipt", str(source),
                                       "--rendered-core2a", str(html)]), 0)
            self.assertIn("NOT_CRYPTOGRAPHIC_ATTESTATION", out.getvalue())
            self.assertIn("ACADEMIC_LEARNER_RELEASE_HOLD", out.getvalue())

    def test_all_nine_negative_assertions_are_required(self):
        for flag in FLAGS:
            with self.subTest(flag=flag):
                data = receipt()
                data["flags"][flag] = False
                self.assertIn("BROWSER_NEGATIVE_ASSERTIONS_MISSING",
                              findings(data, PAGE_SHA))
                del data["flags"][flag]
                self.assertIn("BROWSER_NEGATIVE_ASSERTIONS_MISSING",
                              findings(data, PAGE_SHA))
        data = receipt()
        data["flags"]["unrequested_claim"] = True
        self.assertIn("BROWSER_NEGATIVE_ASSERTIONS_MISSING",
                      findings(data, PAGE_SHA))

    def test_mutated_rendered_page_or_forged_hash_denies(self):
        self.assertIn("BROWSER_NEGATIVE_RENDER_IDENTITY_MISMATCH",
                      findings(receipt(), hashlib.sha256(b"different").hexdigest()))
        data = receipt()
        data["core2a_sha256"] = "0" * 64
        self.assertIn("BROWSER_NEGATIVE_RENDER_IDENTITY_MISMATCH",
                      findings(data, PAGE_SHA))

    def test_asserted_mastery_or_release_is_not_accepted(self):
        for field in ("chromium_execution_attested", "authentic_core2_admitted",
                      "mastery_verified", "academic_accepted", "release_authorized"):
            with self.subTest(field=field):
                data = receipt()
                data[field] = True
                self.assertIn("BROWSER_NEGATIVE_UNSAFE_AUTHORITY",
                              findings(data, PAGE_SHA))

    def test_missing_bad_or_untrusted_receipts_denied(self):
        self.assertEqual(findings(None, PAGE_SHA),
                         ["INVALID_BROWSER_NEGATIVE_RECEIPT"])
        for attr,value,expected in (
            ("schema","unexpected","WRONG_BROWSER_NEGATIVE_SCOPE"),
            ("source","SOF_SOURCE","WRONG_BROWSER_NEGATIVE_SCOPE"),
            ("status","FAILED","BROWSER_NEGATIVE_PROBES_NOT_CLEAR"),
            ("blocking_codes",["anything"],"BROWSER_NEGATIVE_PROBES_NOT_CLEAR"),
            ("viewport_width",320,"BROWSER_NEGATIVE_VIEWPORT_INVALID"),
            ("flags","not a map","BROWSER_NEGATIVE_ASSERTIONS_MISSING"),
        ):
            with self.subTest(attr=attr):
                data = receipt()
                data[attr] = value
                self.assertIn(expected, findings(data, PAGE_SHA))

    def test_private_untrusted_error_never_appears_in_public_diagnostic(self):
        data = receipt()
        data["blocking_codes"] = ["PRIVATE RESPONSE SHOULD NOT BE SHARED"]
        data["extra_private_text"] = "PRIVATE RESPONSE SHOULD NOT BE SHARED"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "receipt.json")
            html = Path(tmp, "page.html")
            path.write_text(json.dumps(data), encoding="utf-8")
            html.write_bytes(PAGE)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["--receipt", str(path),
                                       "--rendered-core2a", str(html)]), 1)
            self.assertNotIn("PRIVATE", out.getvalue())

    def test_missing_or_invalid_json_is_fixed_denial(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp,"receipt.json")
            html = Path(tmp,"core2a.html")
            html.write_bytes(PAGE)
            for exists in (False,True):
                if exists:
                    path.write_text('{"private":"unreadable"', encoding="utf-8")
                out = io.StringIO()
                with redirect_stdout(out):
                    self.assertEqual(main(["--receipt",str(path),
                                           "--rendered-core2a",str(html)]),1)
                self.assertEqual(out.getvalue().strip(),
                                 "F04_REAL_BROWSER_NEGATIVE_BLOCKED; UNREADABLE_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
