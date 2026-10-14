#!/usr/bin/env python3
"""Tests for the automated QRT audit engine (audit_core_against_qrt.py)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
from Shared.tools.audit_core_against_qrt import (
    audit_core2_question_card,
    audit_core1a_section,
    audit_core1b_section,
    audit_hosted_suite,
    load_json,
    QRT_MATRIX_PATH,
)


class TestAuditCoreAgainstQRT(unittest.TestCase):
    """Test suite for QRT compliance auditing across Core 1A, 1B, and Core 2."""

    def setUp(self) -> None:
        self.qrt_matrix = load_json(QRT_MATRIX_PATH)
        self.hosted_core2 = REPO / "public" / "test" / "imo-grade9" / "core2.html"
        self.master_suite = REPO / "standalone" / "mathematics-imo-grade9-master-suite.html"
        self.core1a_file = REPO / "public" / "test" / "imo-grade9" / "core1a.html"
        self.core1b_file = REPO / "public" / "test" / "imo-grade9" / "core1b.html"

    def test_audit_core2_perfect_card(self) -> None:
        card_html = """
        <article class="qb-question" data-band="D2" data-demand="APPLY" data-topic="Linear Equations" data-search="Q101 sample">
          <h2 class="qb-title">Q101. Sample Linear Item</h2>
          <div class="qb-stem-text">Solve $2x + 3 = 11$.</div>
          <div class="qb-options-grid"><div>(A) 4</div></div>
          <div class="qb-attempt-box"><textarea></textarea></div>
          <div class="ladder-rung"><span class="rung-tag">Rung 1</span><p>Isolate x.</p></div>
          <div class="ladder-rung"><span class="rung-tag">Rung 2</span><p>Subtract 3 then divide by 2.</p></div>
          <div class="trap-alert"><strong>Tempting Mistake & Why It Fails:</strong> Forgetting to divide 3 by 2.</div>
          <div class="sol-verified-box"><div class="sol-verified-badge">Formal Verification</div></div>
          <p><strong>Step-by-Step Derivation:</strong> 2x = 8 so x = 4.</p>
          <div class="verification-check"><strong>Verification Check:</strong> 2(4)+3=11.</div>
        </article>
        """
        res = audit_core2_question_card(card_html, 1, self.qrt_matrix)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["delta_qrt"], 0.0)
        self.assertEqual(res["band"], "D2")
        self.assertEqual(res["demand"], "APPLY")
        self.assertEqual(len(res["findings"]), 0)

    def test_audit_core2_detects_invalid_demand(self) -> None:
        card_html = """
        <article class="qb-question" data-band="D2" data-demand="INVENTED_DEMAND" data-topic="Triangles" data-search="Q102 bad">
          <div class="qb-stem-text">Stem</div>
          <div class="qb-options-grid"></div>
          <div class="qb-attempt-box"></div>
          <p><strong>Step-by-Step Derivation:</strong> Deriv</p>
          <div><strong>Verification Check:</strong> Check</div>
          <div><strong>Tempting Mistake & Why It Fails:</strong> Trap</div>
          <div class="ladder-rung"><p>H1</p></div>
          <div class="ladder-rung"><p>H2</p></div>
        </article>
        """
        res = audit_core2_question_card(card_html, 2, self.qrt_matrix)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("INVALID_COGNITIVE_DEMAND: INVENTED_DEMAND", res["findings"])

    def test_audit_core1a_full_compliance(self) -> None:
        content = """
        <h2>Conventions and Scope</h2>
        <p>Positive integers n modulo 6.</p>
        <div class="inferential-leap"><strong>The Inferential Leap:</strong> Construct invariant factors.</div>
        <p>Step 1: <strong>Why valid:</strong> Parity alternation.</p>
        <p>Step 2: <strong>Why valid:</strong> Division algorithm mod 3.</p>
        <div class="representation-bridge">Visual residue-table mapping.</div>
        <div class="trap-clinic">Trap Clinic: Refutation and replacement rule for non-coprime factor products.</div>
        <div class="exit-task">Independent Exit Task: Prove n^3-n is divisible by 6.</div>
        """
        res = audit_core1a_section(content, "Test Module 1A", "QRT-JUSTIFY-D2")
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["delta_qrt"], 0.0)

    def test_audit_core1a_detects_missing_conventions_and_why_valid(self) -> None:
        content = """
        <h2>Direct Proof</h2>
        <p>Here is the formula.</p>
        """
        res = audit_core1a_section(content, "Bad 1A Module", "QRT-APPLY-D2")
        self.assertEqual(res["status"], "FAIL")
        self.assertGreater(res["delta_qrt"], 0.50)
        self.assertIn("CORE1A_DECLARED_CONVENTIONS_MISSING", res["findings"])
        self.assertIn("CORE1A_INFERENTIAL_JUMP_NOT_EXPLICITLY_ISOLATED", res["findings"])

    def test_audit_core1b_full_compliance(self) -> None:
        content = """
        <div class="predict-gate">Predict unassisted recall before reveal.</div>
        <div class="attempt-box"><textarea class="qb-textarea"></textarea></div>
        <details class="model-proof"><summary>Check gate result</summary>Full model answer.</details>
        <div class="step-reconstruction">Complete step reconstruction.</div>
        <div class="boundary-test">Boundary test on limiting case with coprime condition.</div>
        """
        res = audit_core1b_section(content, "Test Module 1B", "QRT-APPLY-D2")
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["delta_qrt"], 0.0)

    def test_audit_hosted_core2_page(self) -> None:
        if not self.hosted_core2.is_file():
            self.skipTest("Hosted core2.html not present")
        report = audit_hosted_suite(self.hosted_core2, self.core1a_file, self.core1b_file)
        self.assertGreaterEqual(report["total_questions_audited"], 68)
        self.assertGreaterEqual(report["overall_summary"]["core2_d2_questions_count"], 34)
        # Verify Core 2 baseline compliance is 100% on D2
        d2_stat = report["overall_summary"]["band_statistics"]["D2"]
        self.assertEqual(d2_stat["compliance_pct"], 100.0)
        self.assertEqual(d2_stat["flagged_count"], 0)

    def test_audit_master_suite_page(self) -> None:
        if not self.master_suite.is_file():
            self.skipTest("Master suite not present")
        report = audit_hosted_suite(self.master_suite)
        self.assertGreaterEqual(report["total_questions_audited"], 184)
        self.assertGreaterEqual(report["overall_summary"]["core2_d2_questions_count"], 103)
        d2_stat = report["overall_summary"]["band_statistics"]["D2"]
        self.assertEqual(d2_stat["compliance_pct"], 100.0)

    def test_audit_item_inter_core_checkpoint(self) -> None:
        from Shared.tools.audit_core_against_qrt import audit_item_inter_core_checkpoint
        if not self.hosted_core2.is_file():
            self.skipTest("Hosted core2.html not present")
        res = audit_item_inter_core_checkpoint("2023-24-A-Q027", self.hosted_core2, self.core1a_file, self.core1b_file)
        self.assertIn("checkpoints", res)
        self.assertEqual(res["checkpoints"]["checkpoint_1_core2_custody"]["status"], "PASS")
        self.assertEqual(res["checkpoints"]["checkpoint_2_qrt_matrix_binding"]["status"], "PASS")
        self.assertEqual(res["demand"], "RETRIEVE")
        self.assertEqual(res["band"], "D1")


if __name__ == "__main__":
    unittest.main()
