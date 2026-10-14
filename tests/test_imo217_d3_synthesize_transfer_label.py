"""Regression: changed-divisor SYNTHESIZE Core2B must not carry old REPRESENT path-set text.

Engineering source-label correctness only. Does not grade subject-QRT demand,
independent mathematics, H/S/P/M competency, or Owner acceptance.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "TEST/imo-research/qrt-d3/synthesize.v1.json"
LEDGER = ROOT / "TEST/imo-research/qrt-d3-successor/synthesize-source-supersession.v1.json"


class TestSynthesizeD3TransferLabel(unittest.TestCase):
    def test_changed_divisor_transfer_not_represent_marker_recycle(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        q = next(q for q in source["questions"]
                 if q["id"] == "Q-TEST-QRT-SYNTHESIZE-D3-BOUNDARY")
        self.assertEqual(q["id"], ledger["transfer_primary_id"])
        self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"],
                         "SYNTHESIZE")
        self.assertEqual(q["difficulty"]["band"], "D3")
        self.assertIn("SIX", q["stem"])
        self.assertEqual(q["family_exposure"]["closure"],
                         ledger["transfer_corrected_field_value"])
        self.assertNotIn(ledger["transfer_previous_field_value"],
                         q["family_exposure"]["closure"])
        self.assertIn("divisibility", q["family_exposure"]["closure"])
        self.assertIn("parity", q["family_exposure"]["closure"])
        self.assertIn("pending", q["family_exposure"]["closure"].lower())
        self.assertFalse(source["extensions"]["grade9v3:qrt_admitted"])


if __name__ == "__main__":
    unittest.main()
