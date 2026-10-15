#!/usr/bin/env python3
"""Adversarial Synthetic Mutation Tests for Tile (1, 3): QRT-APPLY-D1.

Falsifiers verify that the validator fails closed against all Blueprint Contract violations:
- Option pre-commit styling leaks
- Summary answer disclosures
- Unlocked pre-commit solutions
- Difficulty score out-of-bounds
- Primary demand mismatch
- Crux move signature missing
- KaTeX render defects
- Hint procedural execution W leaks
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

from Shared.validators.tiles.tile_1_3.validator import validate_card

FIXTURE_PATH = Path(__file__).parent / "golden_fixture.json"


class TestTile13SelfMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def get_clean_fixture(self):
        return (
            copy.deepcopy(self.raw_fixture["source_question"]),
            self.raw_fixture["html_representation"]
        )

    def test_01_golden_fixture_passes_cleanly(self):
        q, html_snippet = self.get_clean_fixture()
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["findings"], [])
        self.assertIn("QRT_APPLY_DECISIVE_ACT_AND_W_SEMANTIC_REVIEW_REQUIRED", res["holds"])

    def test_02_falsifier_precommit_option_styling_fails(self):
        q, html_snippet = self.get_clean_fixture()
        mutated_html = html_snippet.replace(
            'class="qb-option-btn"',
            'class="qb-option-btn is_correct"'
        )
        res = validate_card(q, mutated_html)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T01_PRECOMMIT_OPTION_STYLING", rules)

    def test_03_falsifier_summary_answer_leak_fails(self):
        q, html_snippet = self.get_clean_fixture()
        mutated_html = html_snippet.replace(
            '<summary class="qb-solution-summary">Show Complete Solution</summary>',
            '<summary class="qb-solution-summary">Answer: (D) South-West</summary>'
        )
        res = validate_card(q, mutated_html)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T02_SUMMARY_ANSWER_LEAK", rules)

    def test_04_falsifier_solution_precommit_unlocked_fails(self):
        q, html_snippet = self.get_clean_fixture()
        mutated_html = html_snippet.replace(
            'inert hidden data-locked="true"',
            'open data-locked="false"'
        )
        res = validate_card(q, mutated_html)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T03_SOLUTION_PRECOMMIT_UNLOCKED", rules)

    def test_05_falsifier_score_out_of_bounds_high_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["cognitive_classification"]["difficulty_score"] = 5
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_06_falsifier_score_out_of_bounds_negative_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["cognitive_classification"]["difficulty_score"] = -1
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_07_falsifier_components_sum_mismatch_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["cognitive_classification"]["difficulty_components"]["algebra_computational_load"] = 2
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_08_falsifier_crux_move_missing_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["cognitive_classification"]["crux_move"] = ""
        q["answer"]["crux_move_ref"] = ""
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T05_CRUX_MOVE_REF_MISSING", rules)

    def test_09_falsifier_primary_demand_mismatch_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["cognitive_classification"]["primary_demand"] = "EXPLAIN"
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T05_CRUX_MOVE_REF_MISSING", rules)

    def test_10_falsifier_katex_error_span_fails(self):
        q, html_snippet = self.get_clean_fixture()
        mutated_html = html_snippet.replace(
            '<p>A person is facing West',
            '<p>A person is facing West <span class="katex-error">\\badtheta</span>'
        )
        res = validate_card(q, mutated_html)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T06_KATEX_RENDER_DEFECT", rules)

    def test_11_falsifier_hint1_protected_work_leak_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["hint_ladder"]["hint1_conceptual_nudge"] = "Notice that turning 45° CCW from West results in South-West."
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    def test_12_falsifier_hint2_choice_leak_fails(self):
        q, html_snippet = self.get_clean_fixture()
        q["hint_ladder"]["hint2_tactical_step"] = "Choose option (D) as the final direction."
        res = validate_card(q, html_snippet)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    def test_13_falsifier_progressive_hint_missing_in_html_fails(self):
        q, html_snippet = self.get_clean_fixture()
        mutated_html = html_snippet.replace('id="hint2-GOLDEN-APP-D1-001"', 'id="hint-deprecated"')
        res = validate_card(q, mutated_html)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T13_HINT_PROGRESSIVE_SEQUENCE_MISSING", rules)

    def test_14_falsifier_core1_unit_nav_missing_fails(self):
        q, html_snippet = self.get_clean_fixture()
        mutated_html = html_snippet.replace('data-core-unit-id="u-logic-direction-sense"', '')
        res = validate_card(q, mutated_html)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T12_CORE_P2_TOPIC_ONLY_NO_QUESTION_UNIT", rules)

    def test_15_falsifier_core1a_parameter_leak_fails(self):
        q, html_snippet = self.get_clean_fixture()
        core_ctx = {
            "core1a": {
                "unit_id": "u-logic-direction-sense",
                "notes": "In this exercise, turning 45° clockwise then 180° clockwise and 270° anti-clockwise gives South-West."
            }
        }
        res = validate_card(q, html_snippet, core_context=core_ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T07_CORE1A_PARAMETER_LEAK", rules)

    def test_16_falsifier_core1b_unlocked_predict_gate_fails(self):
        q, html_snippet = self.get_clean_fixture()
        core_ctx = {
            "core1b": {
                "unit_id": "u-logic-direction-tutor",
                "answer_before_attempt": "ALLOWED"
            }
        }
        res = validate_card(q, html_snippet, core_context=core_ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T08_CORE1B_PRECOMMIT_ANSWER_LEAK", rules)


if __name__ == "__main__":
    unittest.main()
