#!/usr/bin/env python3
"""Issue #182 R11: post-commit native journey technical fail-closed mutants."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from qrt_intent_real_navigation import (  # noqa: E402
    POSTCOMMIT_CHECKS, classify_postcommit_journey,
)


def full_roundtrip() -> dict:
    return {**{field: True for field in POSTCOMMIT_CHECKS},
            "independent_credit_claimed": False}


class NativePostcommitTechnicalFalsifiers(unittest.TestCase):
    def test_all_technical_fields_required_and_distinct(self):
        self.assertEqual(len(POSTCOMMIT_CHECKS), 12)
        self.assertEqual(len(set(POSTCOMMIT_CHECKS.values())), 12)
        self.assertEqual(classify_postcommit_journey(full_roundtrip()), [])

    def test_twelve_independent_false_states_are_rejected(self):
        for field, error in POSTCOMMIT_CHECKS.items():
            with self.subTest(field=field):
                observed = full_roundtrip()
                observed[field] = False
                self.assertEqual(classify_postcommit_journey(observed), [error])

    def test_twelve_missing_fields_fail_closed(self):
        for field, error in POSTCOMMIT_CHECKS.items():
            with self.subTest(field=field):
                observed = full_roundtrip()
                del observed[field]
                self.assertEqual(classify_postcommit_journey(observed), [error])

    def test_assisted_answer_may_never_claim_independent_credit(self):
        observed = full_roundtrip()
        observed["independent_credit_claimed"] = True
        self.assertEqual(
            classify_postcommit_journey(observed),
            ["NAV_POSTCOMMIT_FALSE_INDEPENDENT_CREDIT"],
        )

    def test_postcommit_link_absence_never_promotes_browser_fallback(self):
        observed = full_roundtrip()
        observed["postcommit_context_link_present"] = False
        observed["context_link_is_pinned"] = False
        observed["return_link_present"] = False
        observed["return_link_is_pinned"] = False
        hits = classify_postcommit_journey(observed)
        self.assertEqual(len(hits), 4)
        self.assertIn("NAV_POSTCOMMIT_CONTEXT_LINK_MISSING", hits)
        self.assertIn("NAV_POSTCOMMIT_RETURN_LINK_MISSING", hits)

    def test_blank_attempt_cannot_count_as_commit(self):
        observed = full_roundtrip()
        observed["attempt_blank_rejected"] = False
        observed["nonempty_attempt_committed"] = False
        self.assertIn("NAV_POSTCOMMIT_BLANK_UNLOCKED",
                      classify_postcommit_journey(observed))
        self.assertIn("NAV_POSTCOMMIT_VALID_ATTEMPT_NOT_COMMITTED",
                      classify_postcommit_journey(observed))


if __name__ == "__main__":
    unittest.main()
