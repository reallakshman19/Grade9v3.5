"""Self-authored negative fixtures for fail-closed QRT intake checks."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from Shared.tools.imo_qrt_validator import BANKS, check_one, validate_bank_dir, verify_source_commit, build_question_findings, ROOT

SHA = "a" * 40

def sample():
    return {
        "id": "SYN-001",
        "stem": "A synthetic practice prompt.",
        "options": {"A": "one", "B": "two", "C": "three", "D": "four"},
        "answer": {"choice": "B"},
        "paper_origin_locator": {"question_number": 1},
        "solution": {"derivation": "Synthetic derivation."},
        "figure_ref": None,
        "cognitive_classification": {
            "primary_demand": "APPLY", "difficulty_band": "D2",
            "qrt_cell": "QRT-APPLY-D2", "difficulty_score": 3,
            "crux_move": "Apply a known relation",
            "difficulty_components": {
                "concept_model_selection": 1, "representation_translation": 0,
                "reasoning_chain_length": 1, "algebra_computational_load": 1,
                "trap_exception_sensitivity": 0,
            },
        },
    }

def errors(q, visual=False):
    return {f["evidence"] for f in check_one(q, visual_needed=visual)["findings"]}

class IntakeChecks(unittest.TestCase):
    def test_valid_mechanics_do_not_grant_academic_acceptance(self):
        row = check_one(sample())
        self.assertEqual(row["academic_verdict"], "REVIEW_REQUIRED")
        self.assertFalse(any(f["verdict"] == "FAIL" for f in row["findings"]))

    def test_wrong_score(self):
        q = sample(); q["cognitive_classification"]["difficulty_score"] = 9
        self.assertIn("FIVE_FACTOR_SCORE_MISMATCH", errors(q))

    def test_score_eight_is_canonical_d4_without_remap(self):
        q = sample()
        c = q["cognitive_classification"]
        c["difficulty_components"] = {
            "concept_model_selection": 2, "representation_translation": 2,
            "reasoning_chain_length": 2, "algebra_computational_load": 1,
            "trap_exception_sensitivity": 1,
        }
        c["difficulty_score"] = 8
        c["difficulty_band"] = "D4"
        c["qrt_cell"] = "QRT-APPLY-D4"
        row = check_one(q)
        self.assertEqual((row["derived_score"], row["derived_band"]), (8, "D4"))
        self.assertNotIn("FIVE_FACTOR_BAND_MISMATCH", errors(q))
        self.assertNotIn("FIVE_FACTOR_SCORE_MISMATCH", errors(q))
        self.assertEqual(row["academic_verdict"], "REVIEW_REQUIRED")

    def test_wrong_band(self):
        q = sample(); q["cognitive_classification"]["difficulty_band"] = "D4"
        q["cognitive_classification"]["qrt_cell"] = "QRT-APPLY-D4"
        self.assertIn("FIVE_FACTOR_BAND_MISMATCH", errors(q))

    def test_missing_five_factors(self):
        q = sample(); del q["cognitive_classification"]["difficulty_components"]
        self.assertIn("FIVE_FACTOR_EVIDENCE_MISSING", errors(q))

    def test_out_of_range_component(self):
        q = sample(); q["cognitive_classification"]["difficulty_components"]["concept_model_selection"] = 3
        self.assertIn("FIVE_FACTOR_VALUE_INVALID", errors(q))

    def test_tile_disagreement(self):
        q = sample(); q["cognitive_classification"]["qrt_cell"] = "QRT-RETRIEVE-D2"
        self.assertIn("DECLARED_QRT_CELL_INCONSISTENT", errors(q))

    def test_bad_answer_letter(self):
        q = sample(); q["answer"]["choice"] = "E"
        self.assertIn("ANSWER_CHOICE_INVALID", errors(q))

    def test_visual_cue_is_not_evidence_of_svg(self):
        self.assertIn("VISUAL_CUE_WITHOUT_DECLARED_FIGURE", errors(sample(), True))

    def test_invalid_svg_reference(self):
        q = sample(); q["figure_ref"] = "nested/not_an_asset.svg"
        self.assertIn("UNSAFE_OR_INVALID_FIGURE_REFERENCE", errors(q))

    def test_exact_sha_required(self):
        with self.assertRaises(ValueError):
            validate_bank_dir(Path("."), baseline_sha="main")

    def test_duplicate_ids_and_stale_audit(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); bank = root / "banks"; bank.mkdir()
            for name in BANKS:
                (bank / name).write_text(json.dumps({"questions": [sample()]}))
            audit = root / "legacy.json"
            audit.write_text(json.dumps({"total_questions_audited": 184}))
            report = validate_bank_dir(bank, visual_manifest=root / "absent",
                                       legacy_audit=audit, expected_total=6, baseline_sha=SHA)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["actual_total"], 6)
            self.assertEqual(report["unique_ids"], 1)
            self.assertEqual(len(report["stale_audits"]), 1)

    def test_missing_bank(self):
        with TemporaryDirectory() as tmp:
            report = validate_bank_dir(Path(tmp), visual_manifest=Path(tmp)/"absent",
                                       legacy_audit=Path(tmp)/"absent", baseline_sha=SHA)
            self.assertEqual(len(report["missing_banks"]), len(BANKS))
            self.assertEqual(report["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
