#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests verifying Blueprint & QRT compliance of the Grade 9 Circles Master Question Bank."""

import json
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
from Shared.tools.audit_core_against_qrt import audit_hosted_suite, load_json, QRT_MATRIX_PATH, VALID_DEMANDS, VALID_BANDS
from Shared.tools.standalone_conformance import RULES, _top_level_rules
from Shared.tools import audit_math_and_fonts

class TestCirclesBlueprintQRT(unittest.TestCase):
    """Test suite ensuring Circles Master Question Bank and Tablet App strictly comply with Blueprint & QRT standards."""

    @classmethod
    def setUpClass(cls):
        cls.bank_path = REPO / "Mathematics" / "question-bank" / "sof-imo-circles-grade9.core2.json"
        cls.html_path = REPO / "standalone" / "practice" / "core2-mathematics-circles-grade9-master.html"
        cls.public_html_path = REPO / "public" / "standalone" / "practice" / "core2-mathematics-circles-grade9-master.html"
        cls.bank_data = json.loads(cls.bank_path.read_text(encoding="utf-8"))

    def test_question_count_and_blueprint_reference(self):
        """Verify question count is exactly 50 and declares BP-CORE2-SOURCE-QUESTION@1.11.0."""
        self.assertEqual(len(self.bank_data["questions"]), 50)
        self.assertEqual(self.bank_data.get("blueprint_ref"), "BP-CORE2-SOURCE-QUESTION@1.11.0")
        self.assertEqual(self.bank_data.get("total_questions"), 50)

    def test_canonical_qrt_demands_and_zero_invalid_demands(self):
        """Verify every question uses a canonical QRT demand and no deprecated CALCULATE remains."""
        for q in self.bank_data["questions"]:
            cog = q.get("cognitive_classification", {})
            demand = cog.get("primary_demand")
            band = cog.get("difficulty_band")
            cell = cog.get("qrt_cell")

            self.assertIn(demand, VALID_DEMANDS, f"Question {q['id']} has invalid demand: {demand}")
            self.assertIn(band, VALID_BANDS, f"Question {q['id']} has invalid band: {band}")
            self.assertEqual(cell, f"QRT-{demand}-{band}", f"Question {q['id']} has mismatched cell: {cell}")

    def test_five_factor_difficulty_scoring_integrity(self):
        """Verify the 5-component difficulty breakdown sums exactly to difficulty_score."""
        expected_keys = {
            "concept_model_selection",
            "representation_translation",
            "reasoning_chain_length",
            "algebra_computational_load",
            "trap_exception_sensitivity"
        }
        for q in self.bank_data["questions"]:
            cog = q.get("cognitive_classification", {})
            components = cog.get("difficulty_components", {})
            score = cog.get("difficulty_score")

            self.assertEqual(set(components.keys()), expected_keys, f"Question {q['id']} missing component keys")
            comp_sum = sum(components.values())
            self.assertEqual(score, comp_sum, f"Question {q['id']} difficulty score {score} != sum {comp_sum}")

            # Check band bounds
            band = cog.get("difficulty_band")
            if band == "D1":
                self.assertIn(score, [1, 2], f"D1 score out of bounds: {score}")
            elif band == "D2":
                self.assertIn(score, [3, 4], f"D2 score out of bounds: {score}")
            elif band == "D3":
                self.assertIn(score, [5, 6], f"D3 score out of bounds: {score}")
            elif band == "D4":
                self.assertIn(score, [7, 8, 9, 10], f"D4 score out of bounds: {score}")

    def test_explicit_conditions_and_cognitive_contract_slots(self):
        """Verify explicit conditions and QRT slots (X, Y, Z, W, wrong_idea, replacement_rule)."""
        required_slots = {"X", "Y", "Z", "W", "wrong_idea", "replacement_rule"}
        for q in self.bank_data["questions"]:
            conditions = q.get("conditions")
            self.assertIsInstance(conditions, list, f"Question {q['id']} conditions must be list")
            self.assertGreaterEqual(len(conditions), 2, f"Question {q['id']} must declare at least 2 conditions")

            contract = q.get("qrt_contract", {})
            self.assertEqual(set(contract.keys()), required_slots, f"Question {q['id']} missing QRT contract slots")
            for slot, val in contract.items():
                self.assertTrue(bool(val), f"Question {q['id']} slot {slot} is empty")

    def test_hosted_suite_qrt_audit_clean_pass(self):
        """Run audit_hosted_suite on standalone tablet HTML: must be 100% compliance with 0 flagged."""
        report = audit_hosted_suite(self.html_path)
        self.assertEqual(report["total_questions_audited"], 50)
        self.assertEqual(report["total_core1_modules_audited"], 8)

        summary = report["overall_summary"]
        for band, stats in summary["band_statistics"].items():
            self.assertEqual(stats["flagged_count"], 0, f"Band {band} has flagged questions: {stats}")
            self.assertEqual(stats["compliance_pct"], 100.0, f"Band {band} compliance != 100%: {stats}")

    def test_math_and_fonts_audit_zero_findings(self):
        """Verify zero math and font findings across HTML and JSON files."""
        f_html = audit_math_and_fonts.audit_html_file(self.html_path)
        f_public = audit_math_and_fonts.audit_html_file(self.public_html_path)
        f_json = audit_math_and_fonts.audit_json_question_bank(self.bank_path)

        self.assertEqual(len(f_html), 0, f"HTML findings: {f_html}")
        self.assertEqual(len(f_public), 0, f"Public HTML findings: {f_public}")
        self.assertEqual(len(f_json), 0, f"JSON findings: {f_json}")

if __name__ == "__main__":
    unittest.main()
