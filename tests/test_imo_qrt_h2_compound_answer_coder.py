"""Coder-lane guard: keep compound-answer Q022 learner-owned before attempt."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "Mathematics/question-bank/sof-imo-2024-25-set-b.core2.json"
QID = "SOF-IMO-G09-L1-2024-25-B-Q022"


class Q022ProtectedWorkRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bank = json.loads(BANK.read_text(encoding="utf-8"))
        matches = [q for q in bank["questions"] if q["id"] == QID]
        if len(matches) != 1:
            raise AssertionError(f"Expected exactly one source Q022, found {len(matches)}")
        cls.question = matches[0]

    def test_precommit_tier_two_does_not_supply_numerical_answer(self):
        q = self.question
        self.assertIn("and it is a/an", q["stem"])
        self.assertIn(",", q["answer"]["value"])
        key_value, _ = [s.strip() for s in q["answer"]["value"].split(",", 1)]
        self.assertTrue(re.fullmatch(r"[+-]?\d+(?:\.\d+)?", key_value))
        hint = q["hint_ladder"]["hint2_tactical_step"]
        # Numeric component is protected even if the learner still must classify it.
        pattern = rf"(?<![\d.]){re.escape(key_value)}(?![\d.])"
        self.assertIsNone(re.search(pattern, hint), "Q022 hint leaks keyed numeric value")
        self.assertNotIn("= 9 - 2 =", hint)
        self.assertNotIn(q["answer"]["value"], hint)

    def test_tier_two_cues_method_without_keying_classification(self):
        q = self.question
        hint = q["hint_ladder"]["hint2_tactical_step"].lower()
        self.assertIn("difference of squares", hint)
        self.assertIn("yourself", hint)
        self.assertIn("decide whether", hint)
        self.assertNotIn("is rational", hint)
        self.assertNotIn("is irrational", hint)
        self.assertNotIn("option a", hint)
        self.assertNotIn("answer is", hint)


if __name__ == "__main__":
    unittest.main()
