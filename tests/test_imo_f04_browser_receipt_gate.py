"""F04 fail-closed browser receipt structure checks, never academic acceptance."""
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from Shared.tools.imo_f04_browser_receipt_gate import findings, main


def example() -> dict:
    """Synthetic, deliberately NOT an observed browser witness."""
    return {
        "schema": "imo-f02-concept-first-chromium/v2",
        "source": "TEST_CANDIDATE",
        "authentic_core2_admitted": False,
        "mastery_verified": False,
        "human_screen_reader": "NOT_RUN",
        "failures": [],
        "viewports": [
            {"width": width, "focus_after_check": "H3", "page_errors": [],
             "note": "TEST-only visible behavior; no learner comprehension claim"}
            for width in (320, 390, 768, 1280)
        ],
        "printed_svg": {"found": True, "count": 3, "visible": 3,
                        "allInsideViewBox": True, "viewBox": [0, 0, 400, 250]},
        "printed_pdf": {"bytes": 12345, "status": "GENERATED_NOT_MANUALLY_INSPECTED"},
    }


class F04BrowserReceiptStructureTests(unittest.TestCase):
    def test_synthetic_shape_has_no_structural_findings_but_no_acceptance(self):
        self.assertEqual(findings(example()), [])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "receipt.json")
            path.write_text(json.dumps(example()), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--receipt", str(path)]), 0)
            self.assertIn("EVIDENCE_UNBOUND_TO_HEAD", output.getvalue())
            self.assertIn("BROWSER_ACCEPTANCE_NOT_GRANTED", output.getvalue())
            self.assertIn("ACADEMIC_AND_RELEASE_HOLD", output.getvalue())

    def test_browser_failures_cannot_be_silenced_or_echoed(self):
        data = example()
        data["failures"] = ["protected-W PII from browser"]
        self.assertIn("BROWSER_RECEIPT_RECORDED_FAILURE_OR_MALFORMED", findings(data))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "receipt.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--receipt", str(path)]), 1)
            self.assertNotIn("protected-W", output.getvalue())
            self.assertNotIn("PII", output.getvalue())

    def test_wrong_schema_or_authority_claim_is_denied(self):
        for key, value, expected in (
            ("schema", "other", "BROWSER_RECEIPT_SOURCE_SCHEMA_INVALID"),
            ("source", "PUBLISHED", "BROWSER_RECEIPT_SOURCE_SCHEMA_INVALID"),
            ("authentic_core2_admitted", True, "BROWSER_RECEIPT_AUTHORITY_CLAIM_UNSAFE"),
            ("mastery_verified", True, "BROWSER_RECEIPT_AUTHORITY_CLAIM_UNSAFE"),
            ("human_screen_reader", "PASS", "BROWSER_RECEIPT_AUTHORITY_CLAIM_UNSAFE"),
        ):
            with self.subTest(key=key):
                data = example()
                data[key] = value
                self.assertIn(expected, findings(data))

    def test_missing_duplicate_or_unordered_viewports_denied(self):
        for width_list in ((320, 390, 768), (320, 390, 390, 1280),
                           (1280, 768, 390, 320), (320, 390, 768, True)):
            with self.subTest(width_list=width_list):
                data = example()
                data["viewports"] = [
                    {"width": width, "focus_after_check": "H3", "page_errors": [],
                     "note": "TEST-only visible behavior; no learner comprehension claim"}
                    for width in width_list
                ]
                self.assertIn("BROWSER_RECEIPT_VIEWPORT_COVERAGE_INCOMPLETE",
                              findings(data))

    def test_page_error_focus_and_unqualified_review_claim_denied(self):
        data = example()
        data["viewports"][0]["page_errors"] = ["learner private response"]
        data["viewports"][1]["focus_after_check"] = "BODY"
        data["viewports"][2]["note"] = "independent mastery awarded"
        issues = findings(data)
        self.assertIn("BROWSER_RECEIPT_PAGE_ERRORS_PRESENT", issues)
        self.assertIn("BROWSER_RECEIPT_FOCUS_UNVERIFIED", issues)
        self.assertIn("BROWSER_RECEIPT_UNQUALIFIED_LEARNER_CLAIM", issues)
        self.assertNotIn("learner private response", repr(issues))

    def test_print_and_pdf_generation_require_proof_not_visual_claim(self):
        for field, value, code in (
            ("printed_svg", {"found": True, "count": 3, "visible": 1,
                             "allInsideViewBox": True},
             "BROWSER_RECEIPT_PRINT_STAGES_UNVERIFIED"),
            ("printed_svg", None, "BROWSER_RECEIPT_PRINT_STAGES_UNVERIFIED"),
            ("printed_pdf", {"bytes": 900, "status": "GENERATED_NOT_MANUALLY_INSPECTED"},
             "BROWSER_RECEIPT_PDF_NOT_GENERATED"),
            ("printed_pdf", {"bytes": 12345, "status": "MANUALLY_ACCEPTED"},
             "BROWSER_RECEIPT_PDF_NOT_GENERATED"),
        ):
            with self.subTest(field=field, value=value):
                data = example()
                data[field] = value
                self.assertIn(code, findings(data))

    def test_nonobject_and_malformed_nested_structures_deny_cleanly(self):
        self.assertEqual(findings(None), ["BROWSER_RECEIPT_NOT_OBJECT"])
        for change in (
            {"viewports": "not a list"},
            {"viewports": [None, None, None, None]},
            {"printed_svg": {}},
            {"printed_pdf": {}},
            {"failures": None},
        ):
            with self.subTest(change=str(change)[:40]):
                data = example()
                data.update(change)
                self.assertTrue(findings(data))

    def test_invalid_json_or_missing_path_never_leaks_contents(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "bad.json")
            path.write_text('{"secret":"private response"', encoding="utf-8")
            for source in (path, Path(d, "missing.json")):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(["--receipt", str(source)]), 1)
                self.assertEqual(output.getvalue().strip(),
                                 "BROWSER_RECEIPT_UNREADABLE; LEARNER_ACCEPTANCE_NOT_GRANTED")


if __name__ == "__main__":
    unittest.main()
