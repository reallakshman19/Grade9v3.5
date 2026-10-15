"""Read-only falsifiers for QRT249 source-side five-factor batch 01.

This test is not an academic QRT acceptance gate and does not edit PR #250.
A passing result means the frozen evidence accurately describes unresolved records,
and that canonical difficulty derivation rejects wrong score/band projections.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from Shared.tools import question_difficulty


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "TEST/imo-qrt-repair/five_factor_batch01.v1.json"
EXPECTED_IDS = {
    "SOF-IMO-G09-L1-2024-25-B-Q022",
    "SOF-IMO-G09-L1-2024-25-B-Q025",
    "SOF-IMO-G09-L1-2024-25-B-Q028",
}
FACTOR_NAMES = set(question_difficulty.COMPONENT_KEYS)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}".encode("ascii") + bytes((0,)) + raw).hexdigest()


class FiveFactorBatch01EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
        cls.bank_path = ROOT / cls.evidence["source_file"]
        cls.bank_bytes = cls.bank_path.read_bytes()
        cls.questions = {
            question["id"]: question
            for question in json.loads(cls.bank_bytes.decode("utf-8"))["questions"]
        }

    def test_exact_readback_source_and_scoped_hold_are_pinned(self) -> None:
        self.assertEqual(self.evidence["schema"], "grade9-imo-five-factor-evidence-batch/v1")
        self.assertEqual(self.evidence["baseline_source_head"], "90c859705feb0dfcedc6d33a013d9e563b7cac9d")
        self.assertEqual(self.evidence["observed_tile"], "QRT-RETRIEVE-D1")
        self.assertEqual(self.evidence["published_academic_acceptances"], 0)
        self.assertEqual(git_blob_sha(self.bank_bytes), self.evidence["source_git_blob_sha"])
        entries = self.evidence["records"]
        self.assertEqual(len(entries), 3)
        self.assertEqual({row["question_id"] for row in entries}, EXPECTED_IDS)

    def test_all_three_are_observed_not_silently_approved(self) -> None:
        for row in self.evidence["records"]:
            with self.subTest(question_id=row["question_id"]):
                c = self.questions[row["question_id"]]["cognitive_classification"]
                self.assertEqual(c["qrt_cell"], "QRT-RETRIEVE-D1")
                self.assertEqual(c["primary_demand"], "RETRIEVE")
                self.assertEqual(row["source_declared_cell"], c["qrt_cell"])
                self.assertEqual(row["stored_score"], c["difficulty_score"])
                self.assertEqual(row["stored_band"], c["difficulty_band"])
                self.assertEqual(row["authored_components"], c["difficulty_components"])
                self.assertEqual(set(c["difficulty_components"]), FACTOR_NAMES)
                projected_score = sum(c["difficulty_components"].values())
                projected_band = question_difficulty.band_for_score(projected_score)
                self.assertEqual(projected_score, row["derived_score_from_authored_components"])
                self.assertEqual(projected_band, row["derived_band_from_authored_components"])
                self.assertNotEqual(c["difficulty_score"], projected_score)
                self.assertEqual(row["review_status"], "HOLD_QUALIFIED_FACTOR_REVIEW")
                self.assertTrue(row["source_reasoning_observation"])
                self.assertTrue(row["required_to_clear"])
                # The canonical engine must RED-flag actual unreconciled source data.
                with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "SCORE_MISMATCH"):
                    question_difficulty.derive({
                        "components": c["difficulty_components"],
                        "score": c["difficulty_score"],
                        "band": c["difficulty_band"],
                    }, question_ref=row["question_id"])

    def test_a_wrong_proposed_score_or_band_is_rejected(self) -> None:
        for row in self.evidence["records"]:
            with self.subTest(question_id=row["question_id"]):
                projected = {
                    "components": dict(row["authored_components"]),
                    "score": row["derived_score_from_authored_components"],
                    "band": row["derived_band_from_authored_components"],
                }
                observed = question_difficulty.derive(projected, question_ref=row["question_id"])
                self.assertEqual(observed["score"], projected["score"])
                self.assertEqual(observed["band"], projected["band"])
                wrong_score = {**projected, "score": projected["score"] + 1}
                with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "SCORE_MISMATCH"):
                    question_difficulty.derive(wrong_score, question_ref=row["question_id"])
                wrong_band = {**projected, "band": "D2"}
                with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "BAND_MISMATCH"):
                    question_difficulty.derive(wrong_band, question_ref=row["question_id"])
                invalid = {**projected, "components": {**projected["components"], "algebra_computational_load": 3}}
                with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "COMPONENT_INVALID"):
                    question_difficulty.derive(invalid, question_ref=row["question_id"])


if __name__ == "__main__":
    unittest.main()
