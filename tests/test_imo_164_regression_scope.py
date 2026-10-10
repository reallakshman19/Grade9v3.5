"""Issue #164 baseline/snapshot scope controls, never a global CI acceptance claim."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
INHERITED = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
AUDIT = ROOT / "TEST/imo-research/pilots/regression-scope-164.v1.json"
CORE2A = "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"
SECTIONS = ("resources","buckets","capabilities","microtopics","relations",
            "representations","question_families","questions","teaching_routes","data")

class RegressionScope164(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inherited = json.loads(INHERITED.read_text())
        cls.snapshot = json.loads(SNAPSHOT.read_text())
        cls.audit = json.loads(AUDIT.read_text())

    def test_every_inherited_record_retained_identically_except_one_authored_core2a_diagnostic(self):
        for section in SECTIONS:
            old = {x["id"]: x for x in self.inherited[section]}
            current = {x["id"]: x for x in self.snapshot[section]}
            self.assertEqual(len(old), len(self.inherited[section]), section)
            self.assertEqual(len(current), len(self.snapshot[section]), section)
            self.assertTrue(old.keys() <= current.keys(), (section, old.keys() - current.keys()))
            for id_, original in old.items():
                with self.subTest(section=section, id=id_):
                    if section == "questions" and id_ == CORE2A:
                        continue
                    self.assertEqual(current[id_], original, (section, id_))

    def test_core2a_change_is_focused_and_is_not_an_authority_rewrite(self):
        original = next(x for x in self.inherited["questions"] if x["id"] == CORE2A)
        updated = next(x for x in self.snapshot["questions"] if x["id"] == CORE2A)
        stable = copy.deepcopy(original)
        changed = copy.deepcopy(updated)
        allowed = {"stem","answer","extensions","failure_signal","independent_check","difficulty"}
        for obj in (stable, changed):
            for key in allowed:
                obj.pop(key, None)
        self.assertEqual(changed, stable)
        self.assertEqual(updated["origin"], "AUTHORED")
        self.assertEqual(updated["origin_ref"], original["origin_ref"])
        self.assertEqual(updated["source_refs"], original["source_refs"])
        self.assertIn("Does that reasoning prove", updated["stem"])
        self.assertNotIn("SOF-IMO-G09-", updated["stem"])

    def test_audit_never_calls_wide_guardrails_baselined_or_accepted(self):
        audit = self.audit
        self.assertEqual(audit["baseline_main_sha"], "778eb35a70517a46108ad0a5dc01dfc89f61c0e3")
        self.assertEqual(audit["scope"], "TEST_AUTHORED_PLUS_CONDITIONAL_SHARED_RENDERER_HINT_HOOK")
        self.assertEqual(audit["inherited_copy_policy"], "PINNED_SNAPSHOT_WITH_EXPLICIT_CORE2A_DIAGNOSTIC_FORK")
        self.assertEqual(audit["baseline_equivalence"], "NOT_ESTABLISHED")
        self.assertEqual(audit["guardrails_branch_head"]["conclusion"], "failure")
        self.assertEqual(audit["guardrails_branch_head"]["test_failures"], 119)
        self.assertEqual(audit["guardrails_branch_head"]["test_errors"], 34)
        self.assertEqual(audit["guardrails_branch_head"]["source"], "RUN_38078233685")
        self.assertFalse(audit["independent_baseline_attested"])
        self.assertFalse(audit["global_ci_accepted"])

if __name__ == "__main__":
    unittest.main()
