"""Negative-control tests for F02 E3: source PASS is never independent mastery."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "TEST/imo-research/candidates/imo_f02_e3_transfer_gate.py"
spec = importlib.util.spec_from_file_location("f02_e3_transfer_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)


class HeldTransferEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = gate.read_json(gate.MANIFEST)
        cls.package = gate.read_json(gate.PACKAGE)
        cls.golden = gate.read_json(gate.GOLDEN)

    def check(self, claim=None, manifest=None, package=None, golden=None):
        return gate.preflight(copy.deepcopy(self.manifest if manifest is None else manifest),
                              copy.deepcopy(self.package if package is None else package),
                              copy.deepcopy(self.golden if golden is None else golden), claim)

    def test_real_source_is_held_no_unseen_item_is_provisioned(self):
        r = self.check()
        self.assertEqual(r["errors"], [])
        self.assertEqual(r["assessment_status"], "REVIEW_ONLY_HOLD_NOT_ACCEPTED")
        self.assertFalse(r["independent_mastery_verified"])
        self.assertFalse(r["credit_eligible"])
        self.assertFalse(r["new_item_provisioned"])
        self.assertEqual(r["already_disclosed_probes"], [gate.EXPOSED_EXIT, gate.EXPOSED_GOLDEN])
        self.assertEqual(len(r["requirements"]), 5)
        self.assertTrue(all(x["status"] == "INDEPENDENT_EVIDENCE_NOT_PROVIDED"
                            for x in r["requirements"]))

    def test_same_item_after_repair_cannot_be_independent_transfer(self):
        r = self.check({"item_ref": gate.SELECTED, "assisted": True,
                        "source": "F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1", "award_credit": True})
        for code in ("E3_SAME_ASSISTED_QUESTION_IS_NOT_NEW_TRANSFER",
                     "E3_EDITABLE_LOCAL_HISTORY_NOT_AUTHORITATIVE",
                     "E3_ASSISTED_ATTEMPT_NOT_INDEPENDENT",
                     "E3_UNAUTHORIZED_MASTERY_OR_CREDIT_CLAIM"):
            self.assertIn(code, r["findings"])
        self.assertFalse(r["credit_eligible"])

    def test_both_disclosed_probes_are_not_verified_unseen(self):
        for ref in (gate.EXPOSED_EXIT, gate.EXPOSED_GOLDEN):
            with self.subTest(ref=ref):
                r = self.check({"item_ref": ref, "assisted": False})
                self.assertIn("E3_REPOSITORY_DISCLOSED_EXAMPLE_NOT_PROVEN_UNSEEN", r["findings"])
                self.assertFalse(r["independent_mastery_verified"])

    def test_unknown_item_positive_self_report_is_not_credit(self):
        r = self.check({"item_ref": "NEW-UNVERIFIED", "unseen": True, "authenticated": True,
                        "semantic_reasoning_correct": True, "reviewer_approved": True,
                        "independent_mastery": True, "award_credit": True})
        self.assertIn("E3_UNRECOGNIZED_ITEM_NO_TRUSTED_CUSTODY_OR_UNSEENNESS", r["findings"])
        self.assertIn("E3_EXTERNAL_ATTESTATION_UNVERIFIED", r["findings"])
        self.assertFalse(r["credit_eligible"])

    def test_claim_text_never_echoes_into_public_codes(self):
        sentinel = "PERSONAL_ANSWER_TEXT_NEVER_WRITE_ME"
        r = self.check({"item_ref": sentinel, "answer_text": sentinel,
                        "learner_id": sentinel, "source": sentinel})
        self.assertNotIn(sentinel, json.dumps(r))
        self.assertTrue(all(x.startswith("E3_") for x in r["findings"]))

    def test_source_core2_or_core2b_selection_rejected(self):
        for role in ("core2", "core2b"):
            with self.subTest(role=role):
                m = copy.deepcopy(self.manifest)
                m["selection"][role] = ["FORGED"]
                self.assertIn("E3_MANIFEST_TRANSFER_OR_SOURCE_SELECTION_UNAUTHORIZED",
                              self.check(manifest=m)["errors"])

    def test_forged_publication_or_academic_grant_rejected(self):
        for key in ("grade9v3:learner_published", "grade9v3:qrt_admitted",
                    "grade9v3:core2_source_custody_granted"):
            with self.subTest(key=key):
                p = copy.deepcopy(self.package)
                p["extensions"][key] = True
                self.assertIn("E3_AUTHORING_OR_PUBLICATION_BOUNDARY_VIOLATED",
                              self.check(package=p)["errors"])

    def test_tampered_golden_review_authority_rejected(self):
        g = copy.deepcopy(self.golden)
        g["governance"]["academic_review"] = "GRANTED"
        self.assertIn("E3_GOLDEN_REVIEW_BOUNDARY_UNVERIFIED",
                      self.check(golden=g)["errors"])

    def test_cli_strict_refuses_grant(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--strict-acceptance"],
                           cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("INDEPENDENT_TRANSFER_NOT_PROVEN", r.stdout)
        self.assertNotIn("MASTERY_PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
