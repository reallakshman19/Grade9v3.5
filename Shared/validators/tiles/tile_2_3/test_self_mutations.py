#!/usr/bin/env python3
"""Adversarial Synthetic Mutation & Stress Tests for Tile (2, 3): QRT-APPLY-D2.

Stress tests across 3 distinct Golden Fixtures:
1. GOLDEN-APP-D2-001: Mensuration (Heron's Formula Area 84 m^2)
2. GOLDEN-APP-D2-002: Coordinate Geometry (Diameter Midpoint & Radius Calculation)
3. GOLDEN-APP-D2-003: Algebra / Surds (Conjugate Radical Simplification sqrt(5))

Falsifiers verify that the validator fails closed against all Blueprint Contract rules (T01-T14):
- Option pre-commit styling leaks
- Summary answer disclosures
- Unlocked pre-commit solutions
- Difficulty score out-of-bounds ([3, 5] for Band D2)
- Component sum mismatch
- Crux move signature missing
- KaTeX render defects
- Hint protected work W leaks
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

from Shared.validators.tiles.tile_2_3.validator import validate_card

DIR = Path(__file__).parent
FIXTURE_1 = json.loads((DIR / "golden_fixture.json").read_text(encoding="utf-8"))
FIXTURE_2 = json.loads((DIR / "golden_fixture_2.json").read_text(encoding="utf-8"))
FIXTURE_3 = json.loads((DIR / "golden_fixture_3.json").read_text(encoding="utf-8"))


class TestTile23StressMutations(unittest.TestCase):
    def get_fixture_triplet(self, raw):
        return (
            copy.deepcopy(raw["source_question"]),
            raw["html_representation"],
            copy.deepcopy(raw.get("core_context"))
        )

    # -------------------------------------------------------------
    # Test 1: All 3 Golden Fixtures Pass Cleanly
    # -------------------------------------------------------------
    def test_01_all_3_golden_fixtures_pass_cleanly(self):
        for idx, raw in enumerate([FIXTURE_1, FIXTURE_2, FIXTURE_3], start=1):
            with self.subTest(fixture_index=idx, qid=raw["source_question"]["id"]):
                q, html_snippet, ctx = self.get_fixture_triplet(raw)
                res = validate_card(q, html_snippet, ctx)
                self.assertEqual(res["verdict"], "PASS")
                self.assertEqual(res["findings"], [])
                self.assertIn("QRT_APPLY_D2_DECISIVE_ACT_REVIEW_REQUIRED", res["holds"])

    # -------------------------------------------------------------
    # Stress Testing Falsifiers on Fixture 1 (Mensuration)
    # -------------------------------------------------------------
    def test_02_fixture1_falsifier_option_styling_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        mutated_html = html_snippet.replace('class="qb-option-btn"', 'class="qb-option-btn is_correct"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T01_PRECOMMIT_OPTION_STYLING", rules)

    def test_03_fixture1_falsifier_summary_answer_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        mutated_html = html_snippet.replace(
            '<summary class="qb-solution-summary">Show Complete Solution</summary>',
            '<summary class="qb-solution-summary">Answer: (A) 84 m^2</summary>'
        )
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T02_SUMMARY_ANSWER_LEAK", rules)

    def test_04_fixture1_falsifier_solution_unlocked_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        mutated_html = html_snippet.replace('inert hidden data-locked="true"', 'open data-locked="false"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T03_SOLUTION_PRECOMMIT_UNLOCKED", rules)

    def test_05_fixture1_falsifier_score_out_of_bounds_low_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        q["cognitive_classification"]["difficulty_score"] = 2
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_06_fixture1_falsifier_score_out_of_bounds_high_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        q["cognitive_classification"]["difficulty_score"] = 6
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_07_fixture1_falsifier_component_sum_mismatch_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        q["cognitive_classification"]["difficulty_components"]["algebra_computational_load"] = 1
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T04_SCORE_OUT_OF_BOUNDS", rules)

    def test_08_fixture1_falsifier_crux_missing_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        q["cognitive_classification"]["crux_move"] = ""
        q["answer"]["crux_move_ref"] = ""
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T05_CRUX_MOVE_REF_MISSING", rules)

    def test_09_fixture1_falsifier_hint1_w_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        q["hint_ladder"]["hint1_conceptual_nudge"] = "The evaluated area result is 84 m^2."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    def test_10_fixture1_falsifier_hint2_choice_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        q["hint_ladder"]["hint2_tactical_step"] = "Notice that choice A is the correct option."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    def test_11_fixture1_falsifier_core1a_parameter_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        ctx["core1a"]["leak_test"] = "The exact area of the triangular plot is 84 m^2."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T07_CORE1A_PARAMETER_LEAK", rules)

    def test_12_fixture1_falsifier_core1b_premature_answer_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_1)
        ctx["core1b"]["answer_before_attempt"] = "ALLOWED"
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T08_CORE1B_PRECOMMIT_ANSWER_LEAK", rules)

    # -------------------------------------------------------------
    # Stress Testing Falsifiers on Fixture 2 (Coordinate Geometry)
    # -------------------------------------------------------------
    def test_13_fixture2_falsifier_option_styling_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_2)
        mutated_html = html_snippet.replace('id="opt-A"', 'id="opt-A" data-correct="true"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T01_PRECOMMIT_OPTION_STYLING", rules)

    def test_14_fixture2_falsifier_unit_navigation_missing_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_2)
        mutated_html = html_snippet.replace('data-core-unit-id="COORD-CIRC-DIAM-02"', '')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T12_CORE_P2_TOPIC_ONLY_NO_QUESTION_UNIT", rules)

    def test_15_fixture2_falsifier_hint1_w_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_2)
        q["hint_ladder"]["hint1_conceptual_nudge"] = "The circle has Center (1, -1) and radius 5 exactly."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)

    # -------------------------------------------------------------
    # Stress Testing Falsifiers on Fixture 3 (Algebra / Surds)
    # -------------------------------------------------------------
    def test_16_fixture3_falsifier_katex_error_span_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_3)
        mutated_html = html_snippet.replace('<p>Simplify the radical', '<p>Simplify the <span class="katex-error">\\badcmd</span> radical')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T06_KATEX_RENDER_DEFECT", rules)

    def test_17_fixture3_falsifier_solution_unlocked_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_3)
        mutated_html = html_snippet.replace('inert hidden data-locked="true"', 'data-locked="false"')
        res = validate_card(q, mutated_html, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T03_SOLUTION_PRECOMMIT_UNLOCKED", rules)

    def test_18_fixture3_falsifier_empty_hint_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_3)
        q["hint_ladder"]["hint2_tactical_step"] = "   "
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T10_EMPTY_HINT", rules)

    def test_19_fixture3_falsifier_hint2_choice_leak_fails(self):
        q, html_snippet, ctx = self.get_fixture_triplet(FIXTURE_3)
        q["hint_ladder"]["hint2_tactical_step"] = "Remember choice A is the correct answer."
        res = validate_card(q, html_snippet, ctx)
        self.assertEqual(res["verdict"], "FAIL")
        rules = [f["rule"] for f in res["findings"]]
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", rules)


if __name__ == "__main__":
    unittest.main()
