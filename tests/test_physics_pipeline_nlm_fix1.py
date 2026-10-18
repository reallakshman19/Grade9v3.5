"""NLM-FIX1 regression: measured difficulty and REPRESENT cannot regress to green templates.

Run: python -m unittest discover -s tests -p 'test_physics_pipeline_nlm_fix1.py' -v
Only NLM fixtures are mutated; other topic banks remain untouched.
"""
import copy
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "physics_pipeline_validator.py"
BANK = ROOT / "TEST" / "physics-research" / "question_bank_mechanics_grade9.v1.json"
ADAPTERS = ROOT / "Physics" / "adapter" / "TopicAdapters.v1.json"
spec = importlib.util.spec_from_file_location("physics_pipeline_validator_nlm_fix1", SOURCE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class NLMDemandCalibrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(BANK.read_text(encoding="utf-8"))

    def setUp(self):
        self.bank = copy.deepcopy(self.original)
        self.temp = TemporaryDirectory()

    def tearDown(self):
        self.temp.cleanup()

    def run_bank(self, strict=False):
        dest = Path(self.temp.name) / "bank.json"
        dest.write_text(json.dumps(self.bank, ensure_ascii=False), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            result = validator.validate_question_bank(str(dest), str(ADAPTERS), strict_golden=strict)
        return result, out.getvalue()

    def test_generated_bank_passes_factor_and_representation_contracts(self):
        ok, output = self.run_bank()
        self.assertTrue(ok, output)
        self.assertIn("28-CELL COVERAGE", output)
        self.assertGreaterEqual(sum(q["qrt_contract"]["primary_demand"] == "REPRESENT" for q in self.bank["questions"]), 4)
        self.assertGreaterEqual(sum(q["qrt_contract"]["difficulty_band"] == "D4" for q in self.bank["questions"]), 3)

    def test_template_vector_fails_even_if_derived_d4_matches(self):
        item = next(q for q in self.bank["questions"] if q["qrt_contract"]["difficulty_band"] == "D4")
        f = item["qrt_contract"]["difficulty_factors"]
        f.update(dict(zip(validator.NLM_FACTOR_KEYS, (4, 3, 4, 4, 4))))
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("forbidden back-filled template factor vector", output)

    def test_tag_mismatch_fails(self):
        item = self.bank["questions"][0]
        item["qrt_contract"]["difficulty_band"] = "D4"
        item["qrt_contract"]["cell_id"] = "PHYS-APPLY-D4"
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("band mismatch", output)

    def test_missing_factor_evidence_fails(self):
        self.bank["questions"][0]["qrt_contract"].pop("factor_evidence")
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("missing factor_evidence", output)

    def test_no_represent_item_fails(self):
        self.bank["questions"] = [
            q for q in self.bank["questions"]
            if q["qrt_contract"]["primary_demand"] != "REPRESENT"
        ]
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("topic bank has no REPRESENT", output)

    def test_empty_cell_report_and_derived_boundaries(self):
        coverage = validator.nlm_coverage_report(self.bank["questions"])
        self.assertEqual(len(coverage), 28)
        self.assertIn("PHYS-RETRIEVE-D4", coverage)
        self.assertEqual(coverage["PHYS-RETRIEVE-D4"], 0)
        for v, expected in [((1,1,1,1,4),"D1"),((1,2,2,2,2),"D2"),((3,3,3,3,3),"D3"),((4,4,4,3,3),"D4")]:
            factors = dict(zip(validator.NLM_FACTOR_KEYS, v))
            self.assertEqual(validator.derive_nlm_band(factors)[0], expected)

    def test_h3_answer_leak_fails(self):
        item = self.bank["questions"][0]
        final = item["model_proof"]["final_answer_value"]
        item["progressive_hints"][2]["reveal_text"] = "The answer is " + final
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("H3 reveals final answer", output)


if __name__ == "__main__":
    unittest.main()
