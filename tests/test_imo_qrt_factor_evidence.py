"""Synthetic mechanical falsifiers for the separate five-factor HOLD ledger."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from Shared.tools.imo_qrt_validator import BANKS, check_one, validate_bank_dir

PIN = "a" * 40


def sample(qid="SYN-001"):
    return {
        "id": qid,
        "stem": "Synthetic question; no original source text.",
        "options": {"A": "one", "B": "two", "C": "three", "D": "four"},
        "answer": {"choice": "A"},
        "paper_origin_locator": {"question_number": 1},
        "solution": {"derivation": "A synthetic warrant."},
        "figure_ref": None,
        "cognitive_classification": {
            "primary_demand": "APPLY", "difficulty_band": "D2",
            "qrt_cell": "QRT-APPLY-D2",
            "difficulty_score": 3,
            "difficulty_components": {
                "concept_model_selection": 1,
                "representation_translation": 0,
                "reasoning_chain_length": 1,
                "algebra_computational_load": 1,
                "trap_exception_sensitivity": 0,
            },
            "crux_move": "Select the synthetic model.",
        },
    }


def evid(q):
    row = check_one(q)
    return row["difficulty_evidence"], {
        f["evidence"]: f["verdict"] for f in row["findings"]
    }


class FiveFactorHoldEvidenceTests(unittest.TestCase):
    def test_matching_five_factors_do_not_self_approve(self):
        q = sample()
        report, codes = evid(q)
        self.assertEqual(report["component_status"], "COMPLETE")
        self.assertEqual((report["stored_score"], report["derived_score"]), (3, 3))
        self.assertEqual((report["stored_band"], report["derived_band"]), ("D2", "D2"))
        self.assertEqual(report["score_consistency"], "MATCH")
        self.assertEqual(report["band_consistency"], "MATCH")
        self.assertEqual(report["academic_justification"], "REVIEW_REQUIRED")
        self.assertEqual(codes["FIVE_FACTOR_ACADEMIC_JUSTIFICATION_UNREVIEWED"], "REVIEW_REQUIRED")

    def test_hots_missing_factor_block_is_explicit_hold(self):
        q = sample("SOF-IMO-G09-HOTS-OLYMPIAD-Q024")
        del q["cognitive_classification"]["difficulty_components"]
        report, codes = evid(q)
        self.assertEqual(report["component_status"], "MISSING")
        self.assertIsNone(report["derived_band"])
        self.assertEqual(report["score_consistency"], "NOT_DERIVABLE")
        self.assertEqual(codes["FIVE_FACTOR_EVIDENCE_MISSING"], "REVIEW_REQUIRED")

    def test_present_non_mapping_components_fail(self):
        q = sample()
        q["cognitive_classification"]["difficulty_components"] = [0, 1, 2]
        report, codes = evid(q)
        self.assertEqual(report["component_status"], "INVALID_TYPE")
        self.assertEqual(codes["FIVE_FACTOR_STRUCTURE_INVALID"], "FAIL")

    def test_missing_and_extra_component_keys_fail_without_guessing(self):
        q = sample()
        factors = q["cognitive_classification"]["difficulty_components"]
        del factors["representation_translation"]
        factors["custom_factor"] = 0
        report, codes = evid(q)
        self.assertEqual(report["component_status"], "INVALID_KEYS")
        self.assertEqual(report["missing_keys"], ["representation_translation"])
        self.assertEqual(report["extra_keys"], ["custom_factor"])
        self.assertEqual(codes["FIVE_FACTOR_KEYS_INCOMPLETE_OR_EXTRA"], "FAIL")

    def test_invalid_three_and_boolean_factor_neither_clamp_nor_derive(self):
        for bad in (3, True, -1, 0.5):
            with self.subTest(bad=bad):
                q = sample()
                q["cognitive_classification"]["difficulty_components"]["algebra_computational_load"] = bad
                report, codes = evid(q)
                self.assertEqual(report["component_status"], "INVALID_VALUES")
                self.assertEqual(report["score_consistency"], "NOT_DERIVABLE")
                self.assertIsNone(report["derived_score"])
                self.assertEqual(codes["FIVE_FACTOR_VALUE_INVALID"], "FAIL")

    def test_score_and_band_mismatches_both_survive(self):
        q = sample()
        c = q["cognitive_classification"]
        c["difficulty_score"] = 8
        c["difficulty_band"] = "D4"
        c["qrt_cell"] = "QRT-APPLY-D4"
        report, codes = evid(q)
        self.assertEqual(report["score_consistency"], "MISMATCH")
        self.assertEqual(report["band_consistency"], "MISMATCH")
        self.assertEqual((report["derived_score"], report["derived_band"]), (3, "D2"))
        self.assertEqual(codes["FIVE_FACTOR_SCORE_MISMATCH"], "FAIL")
        self.assertEqual(codes["FIVE_FACTOR_BAND_MISMATCH"], "FAIL")

    def test_boolean_stored_total_is_not_an_integer_proof(self):
        q = sample()
        q["cognitive_classification"]["difficulty_components"] = {
            "concept_model_selection": 1,
            "representation_translation": 0,
            "reasoning_chain_length": 0,
            "algebra_computational_load": 0,
            "trap_exception_sensitivity": 0,
        }
        q["cognitive_classification"]["difficulty_score"] = True
        q["cognitive_classification"]["difficulty_band"] = "D1"
        q["cognitive_classification"]["qrt_cell"] = "QRT-APPLY-D1"
        report, codes = evid(q)
        self.assertEqual(report["score_consistency"], "INVALID_TYPE")
        self.assertEqual(codes["FIVE_FACTOR_SCORE_TYPE_INVALID"], "FAIL")

    def test_full_six_bank_denominator_has_independent_status_counters(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            inputs = root / "banks"
            inputs.mkdir()
            qs = [sample(f"SYN-{i}") for i in range(6)]
            del qs[1]["cognitive_classification"]["difficulty_components"]
            qs[2]["cognitive_classification"]["difficulty_components"]["algebra_computational_load"] = 3
            qs[3]["cognitive_classification"]["difficulty_score"] = 6
            qs[4]["cognitive_classification"]["difficulty_band"] = "D3"
            qs[4]["cognitive_classification"]["qrt_cell"] = "QRT-APPLY-D3"
            for name, q in zip(BANKS, qs):
                (inputs / name).write_text(json.dumps({"questions": [q]}), encoding="utf-8")
            report = validate_bank_dir(
                inputs, baseline_sha=PIN, expected_total=6,
                visual_manifest=root / "no-visuals.json",
                legacy_audit=root / "no-audit.json",
            )
            self.assertEqual((report["actual_total"], report["unique_ids"]), (6, 6))
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["difficulty_evidence_summary"], {
                "components": {"COMPLETE": 4, "INVALID_VALUES": 1, "MISSING": 1},
                "scores": {"MATCH": 3, "MISMATCH": 1, "NOT_DERIVABLE": 2},
                "bands": {"MATCH": 3, "MISMATCH": 1, "NOT_DERIVABLE": 2},
            })


if __name__ == "__main__":
    unittest.main()
