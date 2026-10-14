#!/usr/bin/env python3
"""#182 R10 native link identity negative controls; not a learner acceptance."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from qrt_intent_real_navigation import (  # noqa: E402
    classify_assisted_return, classify_target_identity,
)


def native_link_fixture() -> dict:
    return {
        "expected_primary_question_id": "Q-TEST-QRT-MODEL-D2-PRIMARY",
        "source_question_id": "Q-TEST-QRT-MODEL-D2-PRIMARY",
        "expected_concept_id": "MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT",
        "observed_concept_id": "MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT",
        "context_link_present": True,
        "context_link_count": 1,
        "context_concept_ref": "MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT",
        "context_href": "core1a.html#MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT",
        "return_link_present": True,
        "return_link_count": 1,
        "return_question_ref": "Q-TEST-QRT-MODEL-D2-PRIMARY",
        "return_href": "core2a.html#Q-TEST-QRT-MODEL-D2-PRIMARY",
        "return_state_assisted": True,
        "return_state_independent": False,
    }


class NativeReturnTargetFalsifiers(unittest.TestCase):
    def invalid(self, finding: str, **mutation) -> None:
        candidate = native_link_fixture()
        candidate.update(mutation)
        self.assertIn(finding, classify_target_identity(candidate))

    def test_exact_pinned_context_and_question_accepted_as_target_only(self):
        self.assertEqual(classify_target_identity(native_link_fixture()), [])

    def test_explicitly_absent_native_links_are_not_forged_safe_links(self):
        state = native_link_fixture()
        state.update(context_link_present=False, context_link_count=0,
                     context_href=None, context_concept_ref=None,
                     return_link_present=False, return_link_count=0,
                     return_href=None, return_question_ref=None,
                     return_state_assisted=False)
        self.assertEqual(classify_target_identity(state), [])
        route_flags = {
            "context_link_at_source": False,
            "return_link_at_concept": False,
            "return_state_assisted": False,
            "source_attempt_restored": False,
        }
        self.assertEqual(len(classify_assisted_return(route_flags)), 4)

    def test_wrong_source_question_not_hidden_by_valid_links(self):
        self.invalid("NAV_SOURCE_QUESTION_ID_DRIFT",
                     source_question_id="Q-TEST-QRT-MODEL-D2-TRANSFER")

    def test_wrong_selected_concept_is_rejected(self):
        self.invalid("NAV_CONCEPT_ID_NOT_PINNED_SELECTION",
                     observed_concept_id="MIC-OTHER")

    def test_mismatched_concept_data_attribute_rejected(self):
        self.invalid("NAV_CONTEXT_LINK_WRONG_CONCEPT_OR_ORIGIN",
                     context_concept_ref="MIC-OTHER")

    def test_mismatched_concept_fragment_rejected(self):
        self.invalid("NAV_CONTEXT_LINK_WRONG_CONCEPT_OR_ORIGIN",
                     context_href="core1a.html#MIC-OTHER")

    def test_cross_origin_source_link_rejected(self):
        self.invalid("NAV_CONTEXT_LINK_WRONG_CONCEPT_OR_ORIGIN",
                     context_href="https://example.invalid/core1a.html#MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT")

    def test_duplicate_context_links_are_ambiguous(self):
        self.invalid("NAV_CONTEXT_LINK_WRONG_CONCEPT_OR_ORIGIN",
                     context_link_count=2)

    def test_wrong_question_data_attribute_rejected(self):
        self.invalid("NAV_RETURN_LINK_WRONG_QUESTION_OR_ORIGIN",
                     return_question_ref="Q-TEST-QRT-MODEL-D2-TRANSFER")

    def test_wrong_question_fragment_rejected(self):
        self.invalid("NAV_RETURN_LINK_WRONG_QUESTION_OR_ORIGIN",
                     return_href="core2a.html#Q-TEST-QRT-MODEL-D2-TRANSFER")

    def test_cross_origin_return_rejected(self):
        self.invalid("NAV_RETURN_LINK_WRONG_QUESTION_OR_ORIGIN",
                     return_href="//example.invalid/core2a.html#Q-TEST-QRT-MODEL-D2-PRIMARY")

    def test_ambiguous_duplicate_return_link_rejected(self):
        self.invalid("NAV_RETURN_LINK_WRONG_QUESTION_OR_ORIGIN",
                     return_link_count=2)

    def test_false_independent_credit_on_assisted_return_rejected(self):
        self.invalid("NAV_ASSISTED_RETURN_FALSE_INDEPENDENT_CREDIT",
                     return_state_independent=True)

    def test_local_relative_same_question_anchor_allowed(self):
        candidate = copy.deepcopy(native_link_fixture())
        candidate["return_href"] = "./core2a.html#Q-TEST-QRT-MODEL-D2-PRIMARY"
        candidate["context_href"] = "./core1a.html#MIC-TEST-QRT-MODEL-D2-TWO-CONSTRAINT"
        self.assertEqual(classify_target_identity(candidate), [])


if __name__ == "__main__":
    unittest.main()
