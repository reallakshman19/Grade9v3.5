"""Synthetic falsifiers for scoped #164 CI evidence, never an academic/release test."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path

import summarize_imo_164_deltas as sut

HEAD = "a" * 40


def fixtures():
    groups = {}
    base = {}
    head = {}
    for group in sut.GROUPS:
        base[group] = ["existing:" + group]
        head[group] = ["existing:" + group]
        groups[group] = {
            "pinned_main_count": 1, "pr_count": 1,
            "introduced": [], "resolved": [],
        }
    assurance = {
        "schema": "imo-164-assurance-baseline/1",
        "scope": "ASSURANCE_FINDINGS_AND_PAGES_CHECK_ONLY",
        "global_guardrails_equivalence": "NOT_ESTABLISHED",
        "pinned_main": sut.PINNED, "candidate": HEAD,
        "original_pinned_main": base, "candidate_head": head,
        "deltas": groups, "new_failure_count": 0,
        "differential_pass": True,
    }
    generated = {
        "schema": "imo-164-baseline-differential/1",
        "scope": "NARROW_GENERATOR_CHECK_AND_HTML_PARITY",
        "pinned_main": sut.PINNED, "candidate": HEAD,
        "generator": {
            "baseline": {"stale_paths": ["common.js"], "architecture_drift": False,
                         "other_failure": False},
            "candidate": {"stale_paths": ["common.js"], "architecture_drift": False,
                          "other_failure": False},
            "new_stale_paths": [],
        },
        "html": [
            {"manifest": f"fixture-{n}.json", "changed_pages": [], "identical": True}
            for n in range(3)
        ],
        "errors": [], "parity_pass": True,
    }
    return generated, assurance


class SummaryTests(unittest.TestCase):
    def test_clean_delta_keeps_release_hold_and_unchanged_identities(self):
        g, a = fixtures()
        r = sut.summarize(g, a, HEAD)
        self.assertEqual(r["scoped_verdict"], "NO_NEW_FINDINGS_IN_COMPARED_SCOPE")
        self.assertEqual(r["release_state"], "HOLD")
        self.assertEqual(r["global_guardrails_full_same_runner"], "NOT_ESTABLISHED")
        for category in sut.GROUPS:
            self.assertEqual(r["assurance_id_categories"][category]["unchanged"],
                             {"count": 1, "ids": ["existing:" + category]})

    def test_real_new_id_fails_the_scoped_verdict(self):
        g, a = fixtures()
        key = "all_failure_findings"
        a["candidate_head"][key].append("new finding")
        a["deltas"][key]["introduced"] = ["new finding"]
        a["deltas"][key]["pr_count"] = 2
        a["new_failure_count"] = 1
        a["differential_pass"] = False
        r = sut.summarize(g, a, HEAD)
        self.assertEqual(r["scoped_verdict"], "INTRODUCED_FINDINGS_HOLD")
        self.assertEqual(r["assurance_id_categories"][key]["introduced"]["count"], 1)

    def test_new_stale_generated_file_fails_even_with_no_assurance_changes(self):
        g, a = fixtures()
        g["generator"]["candidate"]["stale_paths"].append("extra.js")
        g["generator"]["new_stale_paths"].append("extra.js")
        r = sut.summarize(g, a, HEAD)
        self.assertEqual(r["scoped_verdict"], "INTRODUCED_FINDINGS_HOLD")

    def test_wrong_sha_or_tampered_delta_refuses_comparison(self):
        g, a = fixtures()
        with self.assertRaisesRegex(ValueError, "wrong pinned checkout"):
            sut.summarize(g, a, "b" * 40)
        bad = copy.deepcopy(a)
        bad["deltas"]["canonical_severe"]["introduced"] = ["fake"]
        with self.assertRaisesRegex(ValueError, "comparison tampered"):
            sut.summarize(g, bad, HEAD)

    def test_inconsistent_generator_verdict_fails_closed(self):
        g, a = fixtures()
        g["parity_pass"] = False
        with self.assertRaisesRegex(ValueError, "generator error or verdict mismatch"):
            sut.summarize(g, a, HEAD)

    def test_cli_writes_hashed_receipt_and_refuses_missing_input(self):
        g, a = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p, q, target = (root / name for name in ("generator.json", "assurance.json",
                                                     "delta-summary.json"))
            p.write_text(json.dumps(g))
            q.write_text(json.dumps(a))
            self.assertEqual(sut.main([str(p), str(q), HEAD, str(target)]), 0)
            result = json.loads(target.read_text())
            self.assertIn("input_sha256", result)
            self.assertEqual(result["release_state"], "HOLD")
            target.unlink()
            self.assertEqual(sut.main([str(root / "missing.json"), str(q),
                                       HEAD, str(target)]), 2)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
