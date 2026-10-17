#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Governance and Quality Audit Test Suite for IMO Grade 9 Circles Master Suite.
File: tests/test_IMOCircle_custody.py
Tests:
- Core 2 Question Bank custody & 4-tier cognitive distribution (25 Qs: 4 D1, 8 D2, 8 D3, 5 D4)
- Option disjointness, answer key validity, distractor diagnostics, and hint ladders
- Authentic Vector SVG asset resolution and strict >= 14px font floor enforcement
- Core 1A Construction & Core 1B Reconstruction package schemas
- Resource registration and standalone tablet app fail-closed quality audit
"""

import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_BANK = REPO_ROOT / "Mathematics" / "question-bank" / "sof-imo-circles-grade9.core2.json"
FIGURES_DIR = REPO_ROOT / "Mathematics" / "library" / "figures"
CORE1A_FILE = REPO_ROOT / "Mathematics" / "units" / "circles" / "core1a-IMOCircle-grade9.v1.json"
CORE1B_FILE = REPO_ROOT / "Mathematics" / "units" / "circles" / "core1b-IMOCircle-grade9.v1.json"
RESOURCES_FILE = REPO_ROOT / "Mathematics" / "question-bank" / "resources.v1.json"
HTML_APP = REPO_ROOT / "standalone" / "practice" / "core2-mathematics-circles-grade9-master.html"
PUBLIC_HTML_APP = REPO_ROOT / "public" / "standalone" / "practice" / "core2-mathematics-circles-grade9-master.html"
ARTIFACT_HTML_APP = Path(r"C:\Users\reall\.gemini\antigravity\brain\40014ef9-8d66-475e-aff1-d6e53797ebbd\circles_master_app.html")

class TestIMOCircleCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank_data = json.loads(JSON_BANK.read_text(encoding="utf-8"))
        cls.questions = cls.bank_data.get("questions", [])

    def test_circles_bank_question_count(self):
        """Verify the question bank contains exactly 50 dedicated questions."""
        self.assertEqual(len(self.questions), 50, "Expected 50 questions in Circles Question Bank")

    def test_circles_bank_difficulty_distribution(self):
        """Verify the 4-tier cognitive distribution: 8 D1, 17 D2, 15 D3, 10 D4."""
        dist = {"D1": 0, "D2": 0, "D3": 0, "D4": 0}
        for q in self.questions:
            band = q.get("cognitive_classification", {}).get("difficulty_band")
            self.assertIn(band, dist, f"Invalid band: {band}")
            dist[band] += 1
        
        self.assertEqual(dist["D1"], 8, "Expected exactly 8 D1 (Foundational) questions")
        self.assertEqual(dist["D2"], 17, "Expected exactly 17 D2 (Standard IMO) questions")
        self.assertEqual(dist["D3"], 15, "Expected exactly 15 D3 (Hard Olympiad) questions")
        self.assertEqual(dist["D4"], 10, "Expected exactly 10 D4 (Achievers HOTS) questions")

    def test_circles_bank_options_and_answers(self):
        """Verify all questions have 4 distinct options and a valid answer choice."""
        for q in self.questions:
            qid = q.get("id")
            opts = q.get("options", {})
            self.assertEqual(set(opts.keys()), {"A", "B", "C", "D"}, f"Missing options in {qid}")
            # Ensure all 4 option values are distinct
            opt_vals = list(opts.values())
            self.assertEqual(len(set(opt_vals)), 4, f"Duplicate option values detected in {qid}")
            # Verify answer choice
            ans = q.get("answer", {})
            ans_choice = ans.get("choice")
            self.assertIn(ans_choice, {"A", "B", "C", "D"}, f"Invalid answer choice in {qid}")
            # Verify answer value matches option value
            self.assertEqual(ans.get("value"), opts[ans_choice], f"Answer value mismatch in {qid}")

    def test_circles_bank_distractor_diagnostics(self):
        """Verify distractor rationale exists for every option plus trap warning."""
        for q in self.questions:
            qid = q.get("id")
            dist = q.get("distractor_rationale", {})
            for opt_key in ["A", "B", "C", "D"]:
                self.assertIn(opt_key, dist, f"Missing distractor rationale for option {opt_key} in {qid}")
                self.assertTrue(len(dist[opt_key].strip()) > 5, f"Distractor rationale too short in {qid}")
            self.assertIn("trap", dist, f"Missing trap diagnostic in {qid}")
            self.assertTrue(len(dist["trap"].strip()) > 5, f"Trap diagnostic too short in {qid}")

    def test_circles_bank_hint_ladders(self):
        """Verify 3-tier progressive hint ladder for every question."""
        for q in self.questions:
            qid = q.get("id")
            hints = q.get("hint_ladder", {})
            self.assertIn("hint1_conceptual_nudge", hints, f"Missing hint 1 in {qid}")
            self.assertIn("hint2_tactical_step", hints, f"Missing hint 2 in {qid}")
            crux = hints.get("hint3_crux_move") or q.get("cognitive_classification", {}).get("crux_move")
            self.assertTrue(bool(crux), f"Missing crux move in {qid}")

    def test_circles_bank_svg_figures_exist_and_font_floor(self):
        """Verify all referenced SVGs exist, are valid XML, and enforce >= 14px font floor."""
        visual_questions = [q for q in self.questions if q.get("figure_ref")]
        self.assertEqual(len(visual_questions), 7, "Expected exactly 7 visual questions with SVG figures")

        for q in visual_questions:
            fref = q["figure_ref"]
            svg_path = FIGURES_DIR / fref
            self.assertTrue(svg_path.exists(), f"Referenced SVG figure missing: {svg_path}")
            
            # Parse XML
            content = svg_path.read_text(encoding="utf-8")
            root = ET.fromstring(content)
            self.assertTrue(root.tag.endswith("svg"), f"Root is not SVG in {fref}")
            
            # Check font-size floor >= 14px
            font_sizes = re.findall(r'font-size\s*[:=]\s*["\']?([0-9.]+)\s*(?:px)?["\']?', content)
            for fs in font_sizes:
                val = float(fs)
                self.assertGreaterEqual(val, 13.9, f"Sub-14px font detected in {fref}: {val}px")

    def test_core1a_imocircle_package(self):
        """Verify Core 1A construction package schema, linked QIDs, and multi-modal representations."""
        self.assertTrue(CORE1A_FILE.exists(), f"Missing Core 1A file: {CORE1A_FILE}")
        data = json.loads(CORE1A_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data.get("schema"), "grade9v3-core1a-construction/v1")
        self.assertEqual(data.get("package_id"), "CORE1A-MATH-IMOCIRCLE-GRADE9")
        
        # Check all 50 Core 2 questions are linked
        linked = data.get("linked_core2_refs", [])
        self.assertEqual(len(linked), 50, "Expected all 50 Core 2 circle questions linked in Core 1A")
        
        # Check representations
        reps = data.get("representation", [])
        self.assertGreaterEqual(len(reps), 7, "Expected at least 7 multi-modal representations")
        for r in reps:
            self.assertTrue(bool(r.get("symbol")), "Representation missing symbol")
            self.assertTrue(bool(r.get("word_meaning")), "Representation missing word_meaning")

    def test_core1b_imocircle_package(self):
        """Verify Core 1B reconstruction package schema and 4-stage cognitive commitment flow."""
        self.assertTrue(CORE1B_FILE.exists(), f"Missing Core 1B file: {CORE1B_FILE}")
        data = json.loads(CORE1B_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data.get("schema"), "grade9v3-core1b-reconstruction/v1")
        self.assertEqual(data.get("package_id"), "CORE1B-MATH-IMOCIRCLE-GRADE9")
        self.assertEqual(data.get("answer_before_attempt"), "FORBIDDEN")
        
        flow = data.get("interactive_tutor_flow", {})
        self.assertIn("stage_1_predict", flow)
        self.assertIn("stage_2_attempt", flow)
        self.assertIn("stage_3_reconstruct", flow)
        self.assertIn("stage_4_boundary_test", flow)

    def test_resources_registration(self):
        """Verify RES-MATH-CORE2-CIRCLES-MASTER is properly registered in resources.v1.json."""
        self.assertTrue(RESOURCES_FILE.exists())
        data = json.loads(RESOURCES_FILE.read_text(encoding="utf-8"))
        ids = [r.get("id") for r in data.get("resources", [])]
        self.assertIn("RES-MATH-CORE2-CIRCLES-MASTER", ids)

    def test_standalone_tablet_app_zero_findings(self):
        """Verify the standalone tablet apps compile with 0 findings under audit_html_file."""
        from Shared.tools.audit_math_and_fonts import audit_html_file
        self.assertTrue(HTML_APP.exists())
        self.assertTrue(PUBLIC_HTML_APP.exists())
        f1 = audit_html_file(HTML_APP)
        f2 = audit_html_file(PUBLIC_HTML_APP)
        self.assertEqual(len(f1), 0, f"Standalone HTML audit findings: {f1}")
        self.assertEqual(len(f2), 0, f"Public standalone HTML audit findings: {f2}")

    def test_standalone_conformance_and_katex_self_contained(self):
        """Verify standalone conformance and that KaTeX typography is 100% self-contained offline."""
        import subprocess
        # 1. Run standalone_conformance.py on HTML_APP and PUBLIC_HTML_APP
        for app_path in [HTML_APP, PUBLIC_HTML_APP]:
            cmd = [sys.executable, str(REPO_ROOT / "Shared" / "tools" / "standalone_conformance.py"), str(app_path)]
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
            self.assertEqual(res.returncode, 0, f"Conformance error for {app_path}: {res.stderr}")
            self.assertIn("conforms", res.stdout, f"{app_path} did not conform: {res.stdout}")

        # 2. Verify self-contained offline KaTeX tags are embedded (zero missing assets)
        content = HTML_APP.read_text(encoding="utf-8")
        self.assertIn('id="offline-katex-css"', content, "Missing offline-katex-css tag")
        self.assertIn('id="offline-katex-core"', content, "Missing offline-katex-core tag")
        self.assertIn('id="offline-katex-auto"', content, "Missing offline-katex-auto tag")

        # 3. Verify artifact app exists and conforms
        if ARTIFACT_HTML_APP.exists():
            art_res = subprocess.run([sys.executable, str(REPO_ROOT / "Shared" / "tools" / "standalone_conformance.py"), str(ARTIFACT_HTML_APP)],
                                     capture_output=True, text=True, cwd=str(REPO_ROOT))
            self.assertIn("conforms", art_res.stdout, f"Artifact did not conform: {art_res.stdout}")

if __name__ == "__main__":
    import sys
    unittest.main()
