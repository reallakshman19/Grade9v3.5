"""Regression guard: authored SYNTHESIZE-D3 must not carry a REPRESENT closure label.

This test guards a measured post-attempt learner HTML content defect; it does not
constitute qualified independent academic/QRT review.
"""
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "TEST/imo-research/qrt-d3/synthesize.v1.json"
TARGET_ID = "Q-TEST-QRT-SYNTHESIZE-D3-CLASSIFY"


class SynthesizeD3ExposureLabelTest(unittest.TestCase):
    def test_provisional_closure_matches_intended_demand(self):
        payload = json.loads(SOURCE.read_text(encoding="utf-8"))
        matches = [q for q in payload["questions"] if q.get("id") == TARGET_ID]
        self.assertEqual(len(matches), 1, "find exactly one authored Core2A main question")
        closure = matches[0]["family_exposure"]["closure"]
        self.assertIn("SYNTHESIZE-D3", closure)
        self.assertNotIn("REPRESENT question", closure)
        self.assertIn("academic", closure.lower())
        self.assertIn("pending", closure.lower())


if __name__ == "__main__":
    unittest.main()
