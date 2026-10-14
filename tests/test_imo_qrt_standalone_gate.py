"""Synthetic HTML mutations, no original exam content or answer publication."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Shared.tools.imo_qrt_standalone_gate import inspect_html, inspect_endpoints


def card(*, qid="TEST-001", emphasized=False, summary="Teacher solution",
         details_open=False, options=4, attempt=True):
    option_html = "".join(
        '<div class="qb-option-card" style="%s"><span class="qb-option-badge">(%s)</span>sample</div>' %
        ("border-color: var(--success)" if emphasized and i == 1 else "", chr(65 + i))
        for i in range(options)
    )
    return (
        '<article class="qb-question" id="q-%s" data-band="D2">' % qid
        + '<div class="qb-options-grid">' + option_html + '</div>'
        + ('<div class="qb-attempt-box">Attempt here</div>' if attempt else "")
        + '<details class="qb-disclosure" id="sol-disc-%s"%s>' % (
            qid, " open" if details_open else "")
        + '<summary><span>%s</span></summary>' % summary
        + '<div class="qb-disclosure-body">Verified Answer: Option (B)</div>'
        + '</details></article>'
    )


class DisclosureTests(unittest.TestCase):
    def test_safe_closed_disclosure_not_academic_approval(self):
        report = inspect_html(card())
        self.assertEqual(report["question_count"], 1)
        self.assertEqual(report["findings"], {})

    def test_pre_attempt_correct_option_highlight(self):
        self.assertEqual(inspect_html(card(emphasized=True))["findings"][
            "PREATTEMPT_CORRECT_OPTION_EMPHASIZED"], 1)

    def test_visible_summary_answer(self):
        self.assertEqual(inspect_html(card(summary="Answer: (B)"))["findings"][
            "PREATTEMPT_ANSWER_IN_VISIBLE_SOLUTION_SUMMARY"], 1)

    def test_closed_body_answer_is_not_visible_summary(self):
        self.assertNotIn("PREATTEMPT_ANSWER_IN_VISIBLE_SOLUTION_SUMMARY",
                         inspect_html(card())["findings"])

    def test_solution_default_open_fails(self):
        self.assertEqual(inspect_html(card(details_open=True))["findings"][
            "SOLUTION_DISCLOSURE_OPEN_BEFORE_ATTEMPT"], 1)

    def test_four_options_required(self):
        self.assertIn("QUESTION_OPTION_CARD_COUNT_NOT_FOUR",
                      inspect_html(card(options=3))["findings"])

    def test_attempt_required(self):
        self.assertIn("QUESTION_ATTEMPT_BOX_MISSING",
                      inspect_html(card(attempt=False))["findings"])

    def test_duplicate_question_id(self):
        report = inspect_html(card() + card())
        self.assertEqual(report["unique_question_ids"], 1)
        self.assertEqual(report["findings"]["DUPLICATE_RENDERED_QUESTION_ID"], 1)

    def test_endpoint_parity_positive_remains_review_required(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            for name in ("first.html", "second.html"):
                (root / name).write_text(card(), encoding="utf-8")
            result = inspect_endpoints(
                root, baseline_sha="a"*40, expected_questions=1,
                endpoints=("first.html", "second.html"))
            self.assertEqual(result["status"], "REVIEW_REQUIRED")
            self.assertEqual(result["academic_verdict"], "REVIEW_REQUIRED")
            self.assertEqual(result["hard_findings"], [])

    def test_endpoint_divergence_and_disclosure_fail(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root/"first.html").write_text(card(), encoding="utf-8")
            (root/"second.html").write_text(card(emphasized=True), encoding="utf-8")
            result = inspect_endpoints(
                root, baseline_sha="a"*40, expected_questions=1,
                endpoints=("first.html", "second.html"))
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("GENERATED_HTML_ENDPOINTS_DIVERGE", result["hard_findings"])

    def test_endpoint_missing_fails(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root/"first.html").write_text(card(), encoding="utf-8")
            result = inspect_endpoints(
                root, baseline_sha="a"*40, expected_questions=1,
                endpoints=("first.html", "missing.html"))
            self.assertIn("GENERATED_HTML_ENDPOINT_MISSING", result["hard_findings"])

    def test_baseline_sha_is_not_optional(self):
        with self.assertRaises(ValueError):
            inspect_endpoints(Path("."), baseline_sha="main")


if __name__ == "__main__":
    unittest.main()
