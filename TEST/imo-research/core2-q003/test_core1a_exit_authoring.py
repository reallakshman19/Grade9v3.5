#!/usr/bin/env python3
"""Source-safe Q003 CORE1A authored independent-exit regression.

Runs with the adjacent, wholly authored JSON only. The protected original
question, private rendered HTML and publisher assets are never loaded.
This protects source-level teaching content; it is NOT native/browser QA.

Run: python -m unittest discover -s TEST/imo-research/core2-q003 -p 'test_*.py'
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).with_name("core1a-authored.v1.json")
PAIRS = re.compile(r"\((-?\d+)\s*,\s*(-?\d+)\)")
STEP = "IMO-PAIR-M4"


def text_of(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(map(text_of, value))
    if isinstance(value, dict):
        return " ".join(text_of(item) for item in value.values())
    return ""


def check_authored_exit(record):
    if record.get("origin") != "AUTHORED":
        raise AssertionError("NON_AUTHORED_LESSON")
    steps = record["teaching_path"]
    if sum(s.get("id") == STEP for s in steps) != 1:
        raise AssertionError("STEP_ID_MISSING_OR_DUPLICATED")
    if sum(STEP in unit.get("step_refs", []) for unit in record["construction_units"]) != 1:
        raise AssertionError("STEP_CONSTRUCTION_BINDING_DRIFT")

    exit_task = record["exit_task"]
    pairs = [(int(x), int(y)) for x, y in PAIRS.findall(exit_task["prompt"])]
    if len(pairs) != 4:
        raise AssertionError("AUTHORED_EXIT_NOT_FOUR_PAIRS")
    residuals = [y - x * x for x, y in pairs]
    counts = Counter(residuals)
    if sorted(counts.values()) != [1, 3]:
        raise AssertionError("AUTHORED_EXIT_MATH_DRIFT")
    offset = next(v for v, n in counts.items() if n == 3)
    exception_index = next(i for i, v in enumerate(residuals) if v != offset)
    if str(pairs[exception_index]) not in exit_task["answer"]["summary"]:
        raise AssertionError("EXIT_MODEL_ANSWER_DRIFT")

    worked = record["authored_transfer"]
    if [y - x * x for x, y in worked["pairs"]] != worked["expected_residuals"]:
        raise AssertionError("WORKED_ANCHOR_MATH_DRIFT")
    if worked["expected_residuals"].count(worked["common_offset"]) != 3:
        raise AssertionError("WORKED_ANCHOR_INVARIANT_DRIFT")
    if worked["expected_residuals"][worked["exception_zero_based"]] == worked["common_offset"]:
        raise AssertionError("WORKED_ANCHOR_EXCEPTION_DRIFT")

    # Fields projected into the lesson BEFORE the independent exit. The
    # separate exit_task.answer is correctly excluded, as is the distinct
    # authored worked example that legitimately discloses its OWN answer.
    pre_exit = {
        "inferential_jump": record.get("inferential_jump", ""),
        "entry_assumptions": record.get("entry_assumptions", []),
        "teaching_path": steps,
        "construction_units": record["construction_units"],
        "misconceptions": record.get("misconceptions", []),
        "relations": record.get("relations", []),
        "representations": record.get("representations", []),
    }
    fingerprints = [
        exit_task["answer"]["summary"].lower(),
        ", ".join(str(v) for v in residuals),
        ", ".join(str(v) for v in residuals[:-1]) + " and " + str(residuals[-1]),
        "for the authored exit list",
        "first pair fails", "second pair fails", "third pair fails", "fourth pair fails",
    ]
    for group, content in pre_exit.items():
        normalized = text_of(content).lower()
        for phrase in fingerprints:
            if phrase and phrase in normalized:
                raise AssertionError("PRE_EXIT_ANSWER_DISCLOSURE:" + group)
    return {"result": "SOURCE_SAFE_AUTHORING_PASS", "pre_exit_groups": len(pre_exit)}


class Q003IndependentExitRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_candidate_does_not_spoil_independent_exit(self):
        self.assertEqual(check_authored_exit(self.record)["pre_exit_groups"], 7)

    def test_old_defect_is_detected(self):
        mutated = deepcopy(self.record)
        step = next(s for s in mutated["teaching_path"] if s["id"] == STEP)
        step["output"] = "For the authored exit list the residuals are 5, 5, 5 and 7: the fourth pair fails the new common offset 5."
        with self.assertRaisesRegex(AssertionError, "PRE_EXIT_ANSWER_DISCLOSURE"):
            check_authored_exit(mutated)

    def test_other_lesson_surfaces_cannot_spoil_exit(self):
        mutations = (
            lambda d: d["misconceptions"][0].update(repair=d["exit_task"]["answer"]["summary"]),
            lambda d: d["representations"][0]["reveal_stages"][0].update(purpose="The fourth pair fails."),
            lambda d: d["entry_assumptions"].append("For the authored exit list the correct result is known."),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate.__code__.co_firstlineno):
                candidate = deepcopy(self.record)
                mutate(candidate)
                with self.assertRaisesRegex(AssertionError, "PRE_EXIT_ANSWER_DISCLOSURE"):
                    check_authored_exit(candidate)

    def test_math_and_lesson_binding_mutations_fail_closed(self):
        mutations = (
            lambda d: d["authored_transfer"].update(expected_residuals=[0, 0, 0, 0]),
            lambda d: d["construction_units"][1].update(step_refs=[]),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate.__code__.co_firstlineno):
                candidate = deepcopy(self.record)
                mutate(candidate)
                with self.assertRaises(AssertionError):
                    check_authored_exit(candidate)


if __name__ == "__main__":
    unittest.main()
