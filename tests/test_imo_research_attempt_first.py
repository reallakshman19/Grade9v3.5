"""Source-owned regressions for Issue #254 research learner protection.

This test intentionally does NOT replace or edit the independent QRT validator.
It checks the generated research HTML, not the governed native Core renderer.
"""
from __future__ import annotations

import json
import re
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (
    "standalone/mathematics-imo-grade9-master-suite.html",
    "public/standalone/mathematics-imo-grade9-master-suite.html",
    "public/test/imo-grade9/core2.html",
    "docs/test/imo-grade9/core2.html",
)
CARD_RE = re.compile(r'<article class="qb-question"\s+id="q-([^"]+)"(.*?)</article>', re.S)
SOLUTION_RE = re.compile(
    r'<details\b[^>]*id="sol-disc-([^"]+)"[^>]*>(.*?)</details>', re.S
)


class ResearchAttemptFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = [(ROOT / p).read_text(encoding="utf-8") for p in OUTPUTS]

    def test_four_generated_outputs_are_identical(self):
        self.assertEqual(len(set(self.built)), 1)

    def test_each_of_260_cards_starts_with_neutral_options_and_protected_answer(self):
        for output, html in zip(OUTPUTS, self.built):
            with self.subTest(output=output):
                cards = CARD_RE.findall(html)
                self.assertEqual(len(cards), 260)
                self.assertEqual(len({q for q, _ in cards}), 260)
                for qid, markup in cards:
                    with self.subTest(qid=qid):
                        self.assertEqual(markup.count('class="qb-option-card"'), 4)
                        self.assertNotIn('correct_style', markup)
                        self.assertNotRegex(markup, r'qb-option-card"[^>]*style="[^"]*--success')
                        self.assertIn(f'id="att-{qid}"', markup)
                        self.assertIn(f'id="commit-{qid}"', markup)
                        self.assertIn(f'id="feedback-{qid}" aria-live="polite"', markup)
                        self.assertRegex(
                            markup, r'id="sol-disc-' + re.escape(qid) + r'" hidden inert'
                        )
                        self.assertRegex(
                            markup, r'id="diag-disc-' + re.escape(qid) + r'" hidden inert'
                        )
                        solution = SOLUTION_RE.search(markup)
                        self.assertIsNotNone(solution)
                        summary = re.search(r'<summary>(.*?)</summary>', solution.group(2), re.S)
                        self.assertIsNotNone(summary)
                        self.assertNotRegex(summary.group(1), r'Answer\s*:\s*\([A-D]\)')
                        self.assertNotIn('rung-crux-container', markup.split(
                            f'id="diag-disc-{qid}"', 1
                        )[0])

    def test_commit_guard_and_keyboard_semantics_are_present(self):
        html = self.built[0]
        self.assertIn('function commitResearchAttempt(questionId)', html)
        self.assertIn('const working = attempt.value.trim();', html)
        self.assertIn("attempt.focus();", html)
        self.assertIn("solution.hidden = false;", html)
        self.assertIn("solution.removeAttribute('inert');", html)
        self.assertIn("diagnosis.hidden = false;", html)
        self.assertIn("summary.focus();", html)
        self.assertIn('aria-controls="sol-disc-', html)
        self.assertIn('aria-expanded="false"', html)
        self.assertIn('.qb-question [hidden] { display: none !important; }', html)

    def test_q046_full_hemisphere_velocity_and_units(self):
        data = json.loads((ROOT / "Mathematics/question-bank/"
            "sof-imo-hots-olympiad-expansion.core2.json").read_text(encoding="utf-8"))
        q = next(q for q in data["questions"] if q["id"].endswith("Q046"))
        self.assertIn("0.35", q["stem"])
        self.assertIn("0.35", q["hint_ladder"]["hint2_tactical_step"])
        self.assertIn("0.0035", q["solution"]["derivation"])
        self.assertIn("entire capacity", q["solution"]["derivation"])
        self.assertNotIn("Wait!", q["solution"]["derivation"])
        self.assertEqual(Fraction(18, 1) / Fraction(35, 10000) / 60, Fraction(600, 7))

    def test_q024_general_claim_is_qualified_not_regular_only(self):
        data = json.loads((ROOT / "Mathematics/question-bank/"
            "sof-imo-hots-olympiad-expansion.core2.json").read_text(encoding="utf-8"))
        q = next(q for q in data["questions"] if q["id"].endswith("Q024"))
        proof = q["solution"]["derivation"]
        self.assertIn("strictly convex", proof)
        self.assertIn("720", proof)
        self.assertIn("180", proof)
        self.assertIn("Original-source diagram/wording clarification", proof)
        self.assertNotIn("angle A +", proof)


if __name__ == "__main__":
    unittest.main()
