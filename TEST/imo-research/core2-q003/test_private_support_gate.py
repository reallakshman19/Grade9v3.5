#!/usr/bin/env python3
"""Source-safe Q003 TEST adapter contract checks; NO original paper or renderer needed.

Run:
  python -m unittest discover -s TEST/imo-research/core2-q003 \
    -p 'test_private_support_gate.py' -v
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "imo_q003_private_adapter", HERE / "prepare_private.py"
)
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


def synthetic_case(count=3):
    """Fabricated numbers and text: no protected Q003 content."""
    row = {
        "question_id": "SYNTHETIC-ONLY-Q003",
        "source_url": "https://example.invalid/synthetic-not-a-source",
        "pdf_page_index": 0,
        "printed_page": 1,
        "printed_question_number": 3,
        "original_identifier": "SYNTHETIC-NOT-IMO",
        "stem": "Fabricated example for input-contract testing only.",
        "options": ["A. synthetic-1", "B. synthetic-2",
                    "C. synthetic-3", "D. synthetic-4"],
        "conditions": [],
        "figures": [],
        "source_hints": [],
        "authored": {
            "answer": {
                "summary": "Synthetic explanation.",
                "check": "Synthetic independent check.",
                "crux_move_ref": "SYNTHETIC-M1",
                "reasoning_route": [{
                    "id": "SYNTHETIC-M1",
                    "action": "Make an invented choice.",
                    "why_valid": "The simulated rule is stipulated.",
                    "output": "Invented output.",
                }],
            },
            "scaffolds": [
                {"prompt": "Synthetic support rung " + str(i)}
                for i in range(count)
            ],
            "difficulty": {"band": "D2"},
            "expected_time_seconds": 90,
        },
    }
    raw = json.dumps(row, sort_keys=True).encode("utf-8")
    expected = {
        key: row[key]
        for key in ("question_id", "source_url", "pdf_page_index",
                    "printed_page", "printed_question_number")
    }
    fields = ("question_id", "stem", "options", "conditions", "figures")
    expected["private_input_sha256"] = hashlib.sha256(raw).hexdigest()
    expected["source_item_sha256"] = hashlib.sha256(ADAPTER.canonical({
        key: row[key] for key in fields
    })).hexdigest()
    return row, expected, raw


class Q003PrivateSupportGate(unittest.TestCase):
    def test_exactly_three_rungs_are_admitted(self):
        row, receipt, raw = synthetic_case(3)
        ADAPTER.validate_private(row, receipt, raw)
        item = ADAPTER.bank(row, receipt)["questions"][0]
        support = item["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(len(support["support_completions"]), 3)
        self.assertEqual(
            [x["support_ref"] for x in support["support_completions"]],
            ["scaffolds[0]", "scaffolds[1]", "scaffolds[2]"],
        )
        self.assertEqual(
            [x["availability"] for x in support["support_completions"]],
            ["PRE_ATTEMPT_SAFE", "AFTER_ATTEMPT", "AFTER_ATTEMPT"],
        )
        self.assertEqual(support["protected_move_refs"], ["SYNTHETIC-M1"])

    def test_no_scaffolds_is_refused(self):
        self._expect_bad_count(0)

    def test_one_scaffold_is_refused(self):
        self._expect_bad_count(1)

    def test_two_scaffolds_are_refused(self):
        self._expect_bad_count(2)

    def test_fourth_unclassified_scaffold_is_refused(self):
        self._expect_bad_count(4)

    def test_nonlist_scaffolds_are_refused(self):
        row, receipt, _ = synthetic_case()
        row["authored"]["scaffolds"] = {"rung": "not a list"}
        raw = json.dumps(row, sort_keys=True).encode("utf-8")
        receipt["private_input_sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "THREE_GATED_RUNGS"):
            ADAPTER.validate_private(row, receipt, raw)

    def test_original_component_tampering_is_refused(self):
        row, receipt, _ = synthetic_case()
        row["options"][0] = "A. tampered"
        raw = json.dumps(row, sort_keys=True).encode("utf-8")
        # Even if someone updates the private-input SHA, the frozen
        # source-item component digest must still reject changed wording.
        receipt["private_input_sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "ITEM_COMPONENT_DIGEST_MISMATCH"):
            ADAPTER.validate_private(row, receipt, raw)

    def test_invalid_crux_is_refused(self):
        row, receipt, _ = synthetic_case()
        row["authored"]["answer"]["crux_move_ref"] = "ABSENT"
        raw = json.dumps(row, sort_keys=True).encode("utf-8")
        receipt["private_input_sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "AUTHORED_CRUX_MISSING"):
            ADAPTER.validate_private(row, receipt, raw)

    def _expect_bad_count(self, n):
        row, receipt, raw = synthetic_case(n)
        with self.assertRaisesRegex(ValueError, "THREE_GATED_RUNGS"):
            ADAPTER.validate_private(row, receipt, raw)


if __name__ == "__main__":
    unittest.main()
