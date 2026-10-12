"""Falsifiers for same-runner full Guardrails test IDs and step-status deltas."""
from __future__ import annotations
import copy
import unittest
from check_imo_164_guardrails_paired import compare, headers


def sample():
    old = [{"name": f"step-{n}", "exit_code": 0, "failure_headers": []}
           for n in range(42)]
    old[2]["exit_code"] = 1
    old[2]["failure_headers"] = [
        "FAIL: test_existing (test_contract.Gate.test_existing)"
    ]
    return old, copy.deepcopy(old)


class PairedGuardrailsTests(unittest.TestCase):
    def test_existing_red_is_not_new_green(self):
        old, new = sample()
        r = compare(old, new)
        self.assertEqual(r["differential_status"],
                         "NO_NEW_FAILURE_IDENTITIES_OR_STEPS")
        self.assertEqual(r["absolute_candidate"], "FAIL")
        self.assertEqual(r["candidate_header_count"], 1)
        self.assertEqual(len(r["unchanged_failure_ids"]), 1)

    def test_new_failing_step_detected_without_test_header(self):
        old, new = sample()
        new[6]["exit_code"] = 1
        r = compare(old, new)
        self.assertEqual(r["introduced_failing_steps"], ["step-6"])
        self.assertEqual(r["differential_status"], "INTRODUCED_FAILURE_HOLD")

    def test_new_test_failure_detected_on_old_red_step(self):
        old, new = sample()
        new[2]["failure_headers"].append(
            "ERROR: test_new (test_contract.Gate.test_new)")
        r = compare(old, new)
        self.assertEqual(len(r["introduced_failure_ids"]), 1)
        self.assertEqual(r["differential_status"], "INTRODUCED_FAILURE_HOLD")

    def test_removed_old_failure_does_not_claim_absolute_green(self):
        old, new = sample()
        new[2]["failure_headers"].clear()
        r = compare(old, new)
        self.assertEqual(len(r["resolved_failure_ids"]), 1)
        self.assertEqual(r["absolute_candidate"], "FAIL")

    def test_missing_named_step_aborts_comparison(self):
        old, new = sample()
        with self.assertRaisesRegex(ValueError, "missing full step coverage"):
            compare(old, new[:-1])
        new[0]["name"] = "other"
        with self.assertRaisesRegex(ValueError, "named step list"):
            compare(old, new)

    def test_parsing_captures_setupclass_and_subtest_parameters(self):
        text = (
            "other error text\n"
            "ERROR: setUpClass (test_publication_engine.ElicitedReveal)\n"
            "FAIL: test_a (test_library.Contract.test_a) (symbol='n mod 3')\n"
            "Ran 2999 tests in 12.31s\n"
        )
        self.assertEqual(len(headers(text)), 2)
        self.assertTrue(any("setUpClass" in s for s in headers(text)))
        self.assertTrue(any("symbol='n mod 3'" in s for s in headers(text)))


if __name__ == "__main__":
    unittest.main()
