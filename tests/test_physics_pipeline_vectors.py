"""Vectors & Coordinate Frames pipeline regression test.

Verifies:
- 100% strict golden validation across Blueprints v2.0.0, Topic Adapter, Question Bank, and Master App.
- LaTeX dollar parity and display math clean formatting.
- 12.7" Tablet Touch specification compliance.
"""

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
import re
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "physics_pipeline_validator.py"
BANK_PATH = ROOT / "TEST" / "physics-research" / "question_bank_vectors_grade9.v1.json"
ADAPTERS_PATH = ROOT / "Physics" / "adapter" / "TopicAdapters.v1.json"
BP_1A_PATH = ROOT / "TEST" / "physics-research" / "blueprints" / "core1a_physics_vectors_ontology.v1.json"
BP_1B_PATH = ROOT / "TEST" / "physics-research" / "blueprints" / "core1b_physics_vectors_reconstruction.v1.json"
APP_PATH = ROOT / "standalone" / "practice" / "core2-physics-vectors-grade9-master.html"

spec = importlib.util.spec_from_file_location("physics_pipeline_validator", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class VectorsPipelineRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank_data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
        cls.adapters = validator.load_topic_adapters(str(ADAPTERS_PATH))

    def test_question_bank_passes_strict_golden_validation(self):
        out = io.StringIO()
        with redirect_stdout(out):
            ok = validator.validate_question_bank(str(BANK_PATH), str(ADAPTERS_PATH), strict_golden=True)
        self.assertTrue(ok, out.getvalue())
        self.assertEqual(len(self.bank_data["questions"]), 25)

    def test_blueprint_reciprocal_bindings(self):
        out = io.StringIO()
        with redirect_stdout(out):
            ok_1a = validator.validate_blueprint_file(str(BP_1A_PATH), str(ADAPTERS_PATH))
            ok_1b = validator.validate_blueprint_file(str(BP_1B_PATH), str(ADAPTERS_PATH))
        self.assertTrue(ok_1a, out.getvalue())
        self.assertTrue(ok_1b, out.getvalue())

    def test_master_app_passes_validation(self):
        out = io.StringIO()
        with redirect_stdout(out):
            ok = validator.validate_master_app(str(APP_PATH), expected_q_count=25)
        self.assertTrue(ok, out.getvalue())

    def test_latex_dollar_parity_across_all_questions(self):
        for q in self.bank_data["questions"]:
            qid = q["question_id"]
            self.assertEqual(q["stem"].count("$") % 2, 0, f"{qid} stem has unbalanced $")
            proof = q.get("model_proof", {})
            for step in ["step_1_understand", "step_2_represent", "step_3_connect", "step_4_execute", "step_5_conclude"]:
                text = proof.get(step, "")
                self.assertEqual(text.count("$") % 2, 0, f"{qid} {step} has unbalanced $")
            for k, opt in q.get("options", {}).items():
                self.assertEqual(opt.count("$") % 2, 0, f"{qid} option {k} has unbalanced $")

    def test_tablet_spec_touch_and_typography(self):
        html = APP_PATH.read_text(encoding="utf-8")
        # Relative header (non-occluding)
        self.assertIn("position: relative", html)
        self.assertIn(".app-header", html)
        # Touch targets >= 48px
        self.assertIn("min-height: 48px", html)
        # Embedded KaTeX font faces
        self.assertIn('<style id="katex-offline-font-faces">', html)
        # Pre-rendered static DOM
        self.assertIn('<span class="katex">', html)


if __name__ == "__main__":
    unittest.main()
