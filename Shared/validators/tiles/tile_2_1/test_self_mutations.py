#!/usr/bin/env python3
"""Adversarial Synthetic Mutation Tests for Tile (2, 1): QRT-RETRIEVE-D2.

Falsifiers verify that the validator fails closed against all 14 Blueprint Contract violations:
- Option pre-commit styling leaks
- Summary answer disclosures
- Unlocked pre-commit solutions
- Difficulty score out-of-bounds ([3, 5] for Band D2)
- Crux move signature missing
- KaTeX render defects
- Hint protected work leaks
- Progressive hint elements missing
- Missing question-specific Core 1 navigation target
- Core 1A parameter leakage
- Core 1B premature answer reveal
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from Shared.validators.tiles.tile_2_1.validator import validate_card

FIXTURE_PATH = Path(__file__).parent / "golden_fixture.json"


class TestTile21SelfMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def get_clean_fixture(self):
        return (
            copy.deepcopy(self.raw_fixture["source_question"]),
            self.raw_fixture["html_representation"],
            copy.deepcopy(self.raw_fixture.get("core_context"))
        )

    def test_01_golden_fixture_passes_cleanly(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["findings"], [])
        self.assertIn("QRT_RETRIEVE_D2_DECISIVE_ACT_REVIEW_REQUIRED", res["holds"])

    def test_02_falsifier_precommit_option_styling_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        mutated_html = html_snippet.replace('class="qb-option-btn"', 'class="qb-option-btn is_correct"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T01_PRECOMMIT_OPTION_STYLING", rules)

    def test_03_falsifier_summary_answer_leak_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        mutated_html = html_snippet.replace(
            '<summary class="qb-solution-summary">Show Complete Solution</summary>',
            '<summary class="qb-solution-summary">Answer: (B) Opposite angles 180</summary>'
        )
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T02_SUMMARY_ANSWER_LEAK", rules)

    def test_04_falsifier_solution_precommit_unlocked_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        mutated_html = html_snippet.replace('inert hidden data-locked="true"', 'open data-locked="false"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T03_SOLUTION_PRECOMMIT_UNLOCKED", rules)

    def test_05_falsifier_score_out_of_bounds_low_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["cognitive_classification"]["difficulty_score"] = 2
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_06_falsifier_score_out_of_bounds_high_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["cognitive_classification"]["difficulty_score"] = 6
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_07_falsifier_components_sum_mismatch_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["cognitive_classification"]["difficulty_components"]["algebra_computational_load"] = 2
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_08_falsifier_crux_move_missing_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["cognitive_classification"]["crux_move"] = ""
        q["answer"]["crux_move_ref"] = ""
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T05_CRUX_MOVE_REF_MISSING", rules)

    def test_09_falsifier_katex_error_span_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        mutated_html = html_snippet.replace(
            '<p>In a convex quadrilateral $PQRS$',
            '<p>In a convex quadrilateral <span class="katex-error">\\badcmd</span>'
        )
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T06_KATEX_RENDER_DEFECT", rules)

    def test_10_falsifier_hint1_protected_work_leak_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["hint_ladder"]["hint1_conceptual_nudge"] = "The sum of a pair of opposite angles equals 180 degrees."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    def test_11_falsifier_hint2_choice_leak_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["hint_ladder"]["hint2_tactical_step"] = "Notice that choice B is the correct option."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    def test_12_falsifier_progressive_hint_missing_in_html_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        mutated_html = html_snippet.replace('id="hint2-GOLDEN-RET-D2-001"', 'id="hint-deprecated"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T13_HINT_PROGRESSIVE_SEQUENCE_MISSING", rules)

    def test_13_falsifier_unit_navigation_missing_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        mutated_html = html_snippet.replace('data-core-unit-id="GEO-CIRC-CONCYC-01"', '')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T12_CORE_P2_TOPIC_ONLY_NO_QUESTION_UNIT", rules)

    def test_14_falsifier_core1a_parameter_leak_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        ctx["core1a"]["leak_test"] = "The sum of a pair of opposite angles equals 180 degrees exactly."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T07_CORE1A_PARAMETER_LEAK", rules)

    def test_15_falsifier_core1b_answer_before_attempt_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        ctx["core1b"]["answer_before_attempt"] = "ALLOWED"
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T08_CORE1B_PRECOMMIT_ANSWER_LEAK", rules)

    def test_16_falsifier_empty_hint_fails(self):
        q, html_snippet, ctx = self.get_clean_fixture()
        q["hint_ladder"]["hint1_conceptual_nudge"] = "   "
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T10_EMPTY_HINT", rules)


if __name__ == "__main__":
    unittest.main()
