"""Falsifiers for diagnostic truthfulness; not exceptions to existing CI gates."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Shared.tools import ci_delta_summary as d


def record(ids, failed=(), errors=(), *, ran=None):
    return {"test_ids": list(ids), "ran": len(ids) if ran is None else ran,
            "failed": list(failed), "load_errors": list(errors)}


class DeltaDiagnosticTests(unittest.TestCase):
    def test_exact_same_population_same_failures_not_green(self):
        obj = d.compare(record(["a", "b"], ["b"]), record(["a", "b"], ["b"]))
        self.assertTrue(obj["collection_comparable"])
        self.assertEqual(obj["new_failing_ids"], [])
        self.assertEqual(obj["inherited_failing_ids"], ["b"])
        self.assertIn("NOT_A_GREEN_CI_RESULT", obj["classification"])

    def test_equal_counts_different_ids_are_not_comparable(self):
        obj = d.compare(record(["a", "c"], ["c"]), record(["a", "b"], ["b"]))
        self.assertFalse(obj["collection_comparable"])
        self.assertIn("TEST_COLLECTION_CHANGED", obj["comparability_limitations"])
        self.assertEqual(obj["new_failing_ids"], ["c"])
        self.assertEqual(obj["fixed_ids"], ["b"])

    def test_order_differences_do_not_change_population(self):
        obj = d.compare(record(["b", "a"]), record(["a", "b"]))
        self.assertTrue(obj["collection_comparable"])

    def test_duplicate_id_counts_do_change_population(self):
        obj = d.compare(record(["a", "b", "b"]), record(["a", "a", "b"]))
        self.assertFalse(obj["collection_comparable"])

    def test_loader_error_is_not_a_complete_comparison(self):
        obj = d.compare(record(["a", "bad"], ["bad"], ["bad"]), record(["a", "bad"], ["bad"], ["bad"]))
        self.assertFalse(obj["collection_comparable"])
        self.assertIn("TEST_MODULE_LOAD_ERRORS", obj["comparability_limitations"])

    def test_missing_test_ids_not_a_proof(self):
        base = {"ran": 2, "failed": [], "load_errors": []}
        obj = d.compare(record(["a", "b"]), base)
        self.assertFalse(obj["collection_comparable"])
        self.assertIn("TEST_IDS_NOT_RECORDED_ON_BOTH_SIDES", obj["comparability_limitations"])

    def test_partial_run_not_complete(self):
        obj = d.compare(record(["a", "b"], ran=1), record(["a", "b"]))
        self.assertFalse(obj["collection_comparable"])
        self.assertIn("COLLECTION_EXECUTION_COUNTS_DIFFER", obj["comparability_limitations"])

    def test_checkout_mismatch_not_misattributed_as_pr_head(self):
        same = record(["a"])
        obj = d.build(same, same, same, checkout_sha="actual", expected_sha="expected")
        self.assertEqual(obj["checkout_relation"], "MISMATCH_ACTUAL_CHECKOUT_NOT_EXPECTED_PR_HEAD")
        self.assertIn("guardrails", obj)
        self.assertIn("not a gate exemption", d.markdown(obj))

    def test_invalid_records_fail_not_silent_pass(self):
        with TemporaryDirectory() as temp:
            f = Path(temp)/"bad.json"
            f.write_text(json.dumps({"ran": False, "failed": [], "load_errors": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                d.read_record(f)

    def test_cli_writes_machine_readable_and_human_summary_without_gate_verdict(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            files = [root/x for x in ("head.json", "base.json", "main.json")]
            for file in files:
                file.write_text(json.dumps(record(["ok", "old"], ["old"])), encoding="utf-8")
            output, summary = root/"out.json", root/"summary.md"
            result = d.main(["--head", str(files[0]), "--base", str(files[1]),
                             "--pinned-main", str(files[2]), "--output", str(output),
                             "--summary", str(summary), "--checkout-sha", "abc", "--expected-head-sha", "abc"])
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(output.read_text())["checkout_relation"], "MATCH")
            self.assertIn("never means green", summary.read_text())


if __name__ == "__main__":
    unittest.main()
