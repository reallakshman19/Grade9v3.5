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


    def test_all_cells_have_item_or_physics_nonapplicability(self):
        adapter = json.loads(ADAPTERS.read_text(encoding="utf-8"))["topic_adapters"]["mechanics-nlm"]
        coverage, errors = validator.nlm_validate_accounted_cells(self.bank["questions"], adapter)
        self.assertEqual(errors, [])
        self.assertEqual(sum(bool(v) for v in coverage.values()), 24)
        self.assertEqual(len(adapter["not_applicable_cells"]), 4)
        broken = copy.deepcopy(adapter)
        broken["not_applicable_cells"].pop("PHYS-SYNTHESIZE-D1")
        _, errors = validator.nlm_validate_accounted_cells(self.bank["questions"], broken)
        self.assertTrue(any("uncovered cell" in x for x in errors))

    def test_d4_margin_and_discriminator_variety(self):
        adapter = json.loads(ADAPTERS.read_text(encoding="utf-8"))["topic_adapters"]["mechanics-nlm"]
        counts, errors, warnings = validator.nlm_d4_discriminator_report(self.bank["questions"], adapter)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(counts), 3)
        self.assertEqual(sum(counts.values()), 5)
        self.assertEqual(warnings, [])
        for q in self.bank["questions"]:
            if q["qrt_contract"]["difficulty_band"] == "D4":
                self.assertGreaterEqual(validator.derive_nlm_band(q["qrt_contract"]["difficulty_factors"])[1], 3.8)

    def test_shallow_d4_margin_is_rejected(self):
        item = next(q for q in self.bank["questions"] if q["question_id"] == "PHYS-NLM-040")
        item["qrt_contract"]["difficulty_factors"]["vector_dimensionality"] = 3
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("D4 margin too low", output)

    def test_identical_factor_evidence_is_rejected(self):
        self.bank["questions"][1]["qrt_contract"]["factor_evidence"] = copy.deepcopy(
            self.bank["questions"][0]["qrt_contract"]["factor_evidence"])
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("identical or near-identical factor_evidence", output)

    def test_near_identical_factor_evidence_is_rejected(self):
        original = copy.deepcopy(self.bank["questions"][0]["qrt_contract"]["factor_evidence"])
        original["math_friction"] += " The numerical details differ slightly."
        self.bank["questions"][1]["qrt_contract"]["factor_evidence"] = original
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("near-identical factor_evidence", output)

    def test_four_unjustified_shared_vectors_fail(self):
        d2 = [q for q in self.bank["questions"] if q["qrt_contract"]["difficulty_band"] == "D2"][:4]
        vector = copy.deepcopy(d2[0]["qrt_contract"]["difficulty_factors"])
        for q in d2:
            q["qrt_contract"]["difficulty_factors"] = copy.deepcopy(vector)
            q["qrt_contract"].pop("vector_reuse_justification", None)
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("un-justified template vector", output)

    def test_d4_concentration_warning(self):
        adapter = json.loads(ADAPTERS.read_text(encoding="utf-8"))["topic_adapters"]["mechanics-nlm"]
        items = [q for q in self.bank["questions"] if q["qrt_contract"]["difficulty_band"] == "D4"]
        for q in items[:4]:
            q["qrt_contract"]["d4_discriminator_type"] = "coupled-2d-response"
        items[-1]["qrt_contract"]["d4_discriminator_type"] = "system-boundary-switch"
        counts, errors, warnings = validator.nlm_d4_discriminator_report(items, adapter)
        self.assertEqual(counts["coupled-2d-response"], 4)
        self.assertTrue(any("> 60%" in w for w in warnings))
        self.assertTrue(any("diversity" in e for e in errors))

    def test_unrecognized_d4_discriminator_fails(self):
        item = next(q for q in self.bank["questions"] if q["qrt_contract"]["difficulty_band"] == "D4")
        item["qrt_contract"]["d4_discriminator_type"] = "generic-hard"
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("unrecognized D4 discriminator", output)

    def test_twelve_core2_decision_routes_are_marked_for_review(self):
        changed = [q["question_id"] for q in self.bank["questions"][:20]
                   if q.get("provenance", {}).get("scenario_distance")]
        self.assertGreaterEqual(len(changed), 10)
        self.assertEqual(changed[:12], [f"PHYS-NLM-{n:03d}" for n in range(1,13)])

    def test_impact_loop_and_turntable_independent_oracles(self):
        # 041: impact momentum, top-contact and energy threshold.
        g, radius = 10, 2
        bottom_speed = (5 * g * radius) ** 0.5
        self.assertEqual(bottom_speed, 10)
        self.assertEqual(3 * bottom_speed, 30)
        self.assertEqual(2 * bottom_speed, 20)
        # 040: coupled static friction bounds intersect at one tension.
        omega_squared = 10 / 3
        tension = 5 / 3
        self.assertAlmostEqual(omega_squared + tension, 5)
        self.assertAlmostEqual(2 * omega_squared - tension, 5)
        # 043: outer contact reaches its static friction bound first.
        self.assertEqual(min([0.2*10/0.5, 0.4*10/1, 0.3*10/1.5]), 2)


    def test_no_d4_discriminators_fails_closed(self):
        adapter = json.loads(ADAPTERS.read_text(encoding="utf-8"))["topic_adapters"]["mechanics-nlm"]
        _, errors, _ = validator.nlm_d4_discriminator_report([], adapter)
        self.assertTrue(any("diversity" in err for err in errors))

    def test_malformed_d4_vector_fails_not_crashes(self):
        item = next(q for q in self.bank["questions"] if q["qrt_contract"]["difficulty_band"] == "D4")
        item["qrt_contract"]["difficulty_factors"].pop("math_friction")
        ok, output = self.run_bank()
        self.assertFalse(ok)
        self.assertIn("five integer scores", output)
        self.assertIn("D4 margin too low", output)


if __name__ == "__main__":
    unittest.main()
