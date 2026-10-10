"""Release decision intentionally fails closed until independent authorities sign off."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"TEST/imo-research/pilots/regression-scope-164.v1.json"
REVIEW=ROOT/"TEST/imo-research/pilots/transfer-comparison-164.v1.json"
PACKAGE=ROOT/"TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
MANIFESTS=(ROOT/"TEST/products/imo-g9-blueprint-first-five-transfer.manifest.json",
           ROOT/"TEST/products/imo-g9-blueprint-boundary-12-transfer.manifest.json")

class Issue164ReleaseHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=json.loads(AUDIT.read_text())
        cls.review=json.loads(REVIEW.read_text())
        cls.package=json.loads(PACKAGE.read_text())

    def test_source_rights_and_publication_flags_remain_blocked(self):
        ext=self.package["extensions"]
        for key in ("grade9v3:qrt_admitted","grade9v3:core2_source_custody_granted",
                    "grade9v3:learner_published"):
            self.assertIs(ext[key],False,key)
        self.assertEqual(self.review["source_core2_admitted"],0)
        self.assertEqual(self.review["source_positions_held"],68)
        for manifest in MANIFESTS:
            m=json.loads(manifest.read_text())
            self.assertEqual(m["subject"],"TEST")
            self.assertEqual(m["selection"]["core2"],[])
            self.assertEqual(m["bank_refs"],[])
            self.assertEqual(len(m["selection"]["core2b"]),1)

    def test_review_gate_and_baseline_are_not_fabricated(self):
        self.assertIsNone(self.review["selected_academic_variant"])
        self.assertIsNone(self.review["reviewer_name"])
        self.assertFalse(self.review["independent_math_review"])
        self.assertFalse(self.review["qrt_accepted"])
        self.assertFalse(self.review["owner_publication_approved"])
        self.assertEqual(self.review["qrt_comparison"]["status"],"AUTHOR_WORKSHEET_UNREVIEWED")
        self.assertEqual(self.audit["baseline_equivalence"],"NOT_ESTABLISHED")
        self.assertEqual(self.audit["narrow_pinned_main_verification"]["changed_html_pages"],0)
        self.assertEqual(self.audit["narrow_pinned_main_verification"]["new_stale_paths"],[])

        self.assertEqual(self.audit["assurance_pinned_main_verification"]["introduced_all_failure_findings"],0)
        self.assertEqual(self.audit["assurance_pinned_main_verification"]["release_eligibility"],"NOT_GRANTED")
        self.assertEqual(self.audit["assurance_pinned_main_verification"]["global_guardrails_equivalence"],"NOT_ESTABLISHED")
        self.assertFalse(self.audit["independent_baseline_attested"])
        self.assertFalse(self.audit["global_ci_accepted"])
        self.assertEqual(self.audit["observed_pr_diff_scope"]["explicit_shared_change"].split(":")[0],
                         "Shared/tools/render_core.py")

    def test_handoff_cannot_claim_release_or_owner_signoff(self):
        handoff=(ROOT/"TEST/imo-research/pilots/issue-164-technical-handoff.md").read_text()
        for required in ("HOLD — NOT RELEASE READY","Owner approval: NOT RECORDED",
                         "Academic reviewer: NOT RECORDED","Pinned-main CI baseline: NOT ESTABLISHED",
                         "QRT accepted: 0/28","SOF Core2 admitted: 0/68"):
            self.assertIn(required,handoff)
        self.assertIn("SHARED RENDERER",handoff)

if __name__=="__main__":
    unittest.main()
