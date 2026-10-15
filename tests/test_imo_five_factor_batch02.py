"""QRT249 source-side batch 02: fail-closed 10-record APPLY-D1 evidence checks."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from Shared.tools import question_difficulty

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "TEST/imo-qrt-repair/five_factor_batch02.v1.json"
KEYS = set(question_difficulty.COMPONENT_KEYS)


def blob_sha(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}".encode("ascii") + bytes((0,)) + payload).hexdigest()


class FiveFactorBatch02EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.by_id = {}
        for item in cls.ledger["source_files"]:
            payload = (ROOT / item["path"]).read_bytes()
            if blob_sha(payload) != item["git_blob_sha"]:
                raise AssertionError("SOURCE_BLOB_CHANGED: " + item["path"])
            bank = json.loads(payload.decode("utf-8"))
            if len(bank["questions"]) != item["question_count"]:
                raise AssertionError("SOURCE_DENOMINATOR_CHANGED: " + item["path"])
            cls.by_id.update({q["id"]: (item["path"], q) for q in bank["questions"]})

    def test_ten_distinct_ids_are_bounded_to_apply_d1(self):
        ledger = self.ledger
        self.assertEqual(ledger["schema"], "grade9-imo-five-factor-evidence-batch/v1")
        self.assertEqual(ledger["batch_id"], "QRT249-FIVEFACTOR-B02")
        self.assertEqual(ledger["baseline_source_head"], "90c859705feb0dfcedc6d33a013d9e563b7cac9d")
        self.assertEqual(ledger["observed_tile"], "QRT-APPLY-D1")
        self.assertEqual(ledger["published_academic_acceptances"], 0)
        rows = ledger["records"]
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({r["question_id"] for r in rows}), 10)
        self.assertTrue(all(r["review_status"] == "HOLD_QUALIFIED_FACTOR_REVIEW" for r in rows))

    def test_record_projection_and_authored_factor_review_remain_open(self):
        for row in self.ledger["records"]:
            with self.subTest(q=row["question_id"]):
                source_path, question = self.by_id[row["question_id"]]
                c = question["cognitive_classification"]
                self.assertEqual(row["source_file"], source_path)
                self.assertEqual(row["source_declared_cell"], c["qrt_cell"])
                self.assertEqual(c["qrt_cell"], "QRT-APPLY-D1")
                self.assertEqual(row["stored_score"], c["difficulty_score"])
                self.assertEqual(row["stored_band"], c["difficulty_band"])
                self.assertEqual(row["authored_components"], c["difficulty_components"])
                self.assertEqual(set(c["difficulty_components"]), KEYS)
                score = sum(c["difficulty_components"].values())
                self.assertEqual(score, row["mechanical_sum"])
                self.assertEqual(question_difficulty.band_for_score(score), row["mechanical_band"])
                self.assertEqual(row["stored_score"], 2)
                self.assertEqual(score, 1)
                self.assertNotEqual(c["difficulty_score"], score)
                self.assertTrue(row["source_reasoning_observation"])
                self.assertIn("Qualified", row["evidence_needed"])
                with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "SCORE_MISMATCH"):
                    question_difficulty.derive(
                        {"components": c["difficulty_components"],
                         "score": c["difficulty_score"], "band": c["difficulty_band"]},
                        question_ref=row["question_id"],
                    )

    def test_mutated_score_band_and_invalid_component_are_rejected(self):
        row = self.ledger["records"][0]
        projected = {"components": dict(row["authored_components"]), "score": 1, "band": "D1"}
        self.assertEqual(question_difficulty.derive(projected)["band"], "D1")
        for broken, failure in (
            ({**projected, "score": 2}, "SCORE_MISMATCH"),
            ({**projected, "band": "D2"}, "BAND_MISMATCH"),
            ({**projected, "components": {**projected["components"], "algebra_computational_load": 3}}, "COMPONENT_INVALID"),
        ):
            with self.subTest(failure=failure):
                with self.assertRaisesRegex(question_difficulty.DifficultyContractError, failure):
                    question_difficulty.derive(broken)


if __name__ == "__main__":
    unittest.main()
