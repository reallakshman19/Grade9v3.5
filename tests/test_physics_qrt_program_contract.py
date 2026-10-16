"""Pure-contract tests; no external network, GitHub writes or Physics code changes."""
from __future__ import annotations

import copy
import unittest

from tools.physics_qrt_program.contracts import converge, validate_lock, validate_receipt

SHA40 = "a" * 40
SHA64 = "b" * 64
QUESTION = "Q-PHY-NLM-2B-FRICTION-STATE-01"


def lock():
    return {
        "schema": "physics-qrt.work-lock/v1",
        "programme": "PHY-QRT-LTA-v1",
        "repository": "reallakshman19/Grade9v3.5",
        "base_sha": SHA40,
        "state": "DRAFT_HOLD",
        "scope_policy": "GRADE9_DEMAND_FIRST_NO_EXTENSION_DEFAULT",
        "owner_issue": None,
        "selected_question_ids": [QUESTION],
        "witnesses": [{
            "question_id": QUESTION,
            "source_class": "CANONICAL_LIBRARY",
            "source_path": "Physics/library/phy-nlm-first-law.v1.json",
            "source_sha256": SHA64,
            "capability_ref": "CAP-PHY-NLM-FRICTION-STATE",
            "school_micro_demand": "MICRO_TO_CONFIRM",
        }],
        "writer_leases": {
            "L1": ["evidence/physics-qrt-program/custody/"],
            "L2": ["tools/physics_qrt_program/oracles/", "tests/physics_qrt_oracles/"],
            "L3": ["tests/physics_qrt_browser/", "evidence/physics-qrt-program/browser/"],
            "L4": ["tests/physics_qrt_mutations/", "evidence/physics-qrt-program/mutations/"],
        },
        "governance": {"git_write_authorized": False, "approval_ref": None,
                       "scientific_oracle_sha256": None, "scientific_oracle_review": "REVIEW_REQUIRED"},
    }


def receipt(role="L1"):
    prefixes = lock()["writer_leases"][role]
    return {
        "schema": "physics-qrt.receipt/v1", "programme": "PHY-QRT-LTA-v1",
        "agent": role, "base_sha": SHA40, "candidate_sha": None,
        "state": "READY_FOR_COORDINATOR", "scope": [QUESTION],
        "checks": [{"id": "T1", "command": "python -m unittest test_exact_case",
                    "status": "PASS", "expected": "exit 0",
                    "observed": "real run exit 0", "exit_code": 0,
                    "evidence_sha256": SHA64}],
        "artifacts": [{"path": prefixes[0].rstrip("/") + "/report.json", "sha256": SHA64}],
        "findings": [], "uncertainties": [],
    }


class PhysicsProgrammeContractTests(unittest.TestCase):
    def test_draft_structure_not_permission(self):
        self.assertEqual(validate_lock(lock()), [])
        self.assertIn("WORK_LOCK_NOT_APPROVED", validate_lock(lock(), require_authorized=True))

    def test_authorized_requires_actual_fields(self):
        l = lock()
        l["state"] = "FROZEN_APPROVED"
        l["owner_issue"] = "reallakshman19/Grade9v3.5#999"
        l["governance"] = {"git_write_authorized": True, "approval_ref": "owner:event",
                           "scientific_oracle_sha256": SHA64,
                           "scientific_oracle_review": "INDEPENDENT_REVIEWED"}
        self.assertEqual(validate_lock(l, require_authorized=True), [])

    def test_missing_oracle_holds(self):
        l = lock()
        l["state"] = "FROZEN_APPROVED"
        l["governance"]["git_write_authorized"] = True
        self.assertIn("SCIENTIFIC_ORACLE_UNREVIEWED", validate_lock(l, require_authorized=True))

    def test_duplicate_or_unscoped_questions(self):
        l = lock()
        l["selected_question_ids"].append(QUESTION)
        self.assertIn("DUPLICATE_QUESTION_ID", validate_lock(l))

    def test_overlapping_leases_rejected(self):
        l = lock()
        l["writer_leases"]["L4"] = ["evidence/physics-qrt-program/custody/mutations/"]
        self.assertTrue(any(x.startswith("OVERLAP:") for x in validate_lock(l)))

    def test_path_traversal_rejected(self):
        l = lock()
        l["writer_leases"]["L4"] = ["../../Physics/library"]
        self.assertTrue(any(x.startswith("UNSAFE_LEASE:") for x in validate_lock(l)))

    def test_valid_receipt_envelope(self):
        self.assertEqual(validate_receipt(receipt(), lock()), [])

    def test_false_pass_must_have_exit_and_digest(self):
        r = receipt()
        r["checks"][0]["exit_code"] = None
        r["checks"][0]["evidence_sha256"] = None
        self.assertIn("FALSE_PASS_ENVELOPE:0", validate_receipt(r, lock()))

    def test_not_run_cannot_claim_execution(self):
        r = receipt()
        r["state"] = "NOT_RUN"
        r["checks"][0].update(status="NOT_RUN", exit_code=0, evidence_sha256=SHA64)
        self.assertIn("NOT_RUN_WITH_EXECUTION:0", validate_receipt(r, lock()))

    def test_foreign_agent_write_rejected(self):
        r = receipt()
        r["artifacts"][0]["path"] = "Physics/library/phy-nlm-first-law.v1.json"
        self.assertIn("WRITER_LEASE_VIOLATION:0", validate_receipt(r, lock()))

    def test_unpinned_scope_rejected(self):
        r = receipt()
        r["scope"] = ["Q-NOT-FROZEN"]
        self.assertIn("RECEIPT_SCOPE_NOT_LOCKED", validate_receipt(r, lock()))

    def test_source_head_drift_rejected(self):
        r = receipt()
        r["base_sha"] = "c" * 40
        self.assertIn("STALE_BASE_SHA", validate_receipt(r, lock()))

    def test_ready_disallows_failed_check(self):
        r = receipt()
        r["checks"][0].update(status="FAIL", observed="negative observed", exit_code=1)
        self.assertIn("READY_WITH_UNVERIFIED_CHECKS", validate_receipt(r, lock()))

    def test_convergence_missing_agents_holds(self):
        result = converge(lock(), [receipt("L1")])
        self.assertFalse(result["envelope_ready"])
        self.assertEqual(result["release_verdict"], "HOLD")
        self.assertEqual(result["science_verdict"], "REVIEW_REQUIRED")

    def test_convergence_all_agents_still_needs_owner_and_review(self):
        result = converge(lock(), [receipt(x) for x in ("L1","L2","L3","L4")])
        self.assertFalse(result["envelope_ready"])
        self.assertTrue(any(f["code"] == "AUTHORITY_HOLD" for f in result["findings"]))
        self.assertEqual(result["learner_verdict"], "INSUFFICIENT_OR_UNKNOWN")

    def test_duplicate_receipt_fails(self):
        result = converge(lock(), [receipt("L1"), receipt("L1")])
        self.assertIn("DUPLICATE_ROLE", {f["code"] for f in result["findings"]})


if __name__ == "__main__":
    unittest.main()
