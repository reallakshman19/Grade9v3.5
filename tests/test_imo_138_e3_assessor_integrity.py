"""E3-B synthetic integrity falsifiers; no real student data or reviewer key."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "TEST/imo-research/candidates/imo_f02_e3_assessor_integrity.py"
spec = importlib.util.spec_from_file_location("f02_e3_assessor_integrity", SCRIPT)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)
TEST_KEY = b"SYNTHETIC-FIXTURE-NOT-AN-AUTHORIZED-REVIEWER-KEY-ONLY"


def payload():
    t = datetime(2026, 10, 10, tzinfo=timezone.utc)
    return {
        "schema": gate.SCHEMA,
        "item_content_sha256": "a" * 64,
        "rubric_sha256": "b" * 64,
        "session_nonce_sha256": "c" * 64,
        "first_attempt_sha256": "d" * 64,
        "custody_scope": "ASSESSOR_HELD_PRIVATE_UNPUBLISHED",
        "repair_complete_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "item_delivered_utc": (t+timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "first_attempt_utc": (t+timedelta(minutes=11)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "new_item_hint_count": 0,
        "new_item_answer_count": 0,
        "math_review_status": "NOT_YET_INDEPENDENTLY_REVIEWED",
        "curriculum_review_status": "GRADE9_DECISION_PENDING",
    }


def signed(value, key=TEST_KEY):
    return {"payload": copy.deepcopy(value),
            "hmac_sha256": hmac.new(key, gate.canonical(value), hashlib.sha256).hexdigest()}


class ExternalReviewerIntegrityTests(unittest.TestCase):
    def test_no_envelope_no_credit(self):
        result = gate.verify({}, None)
        self.assertFalse(result["mac_integrity_verified"])
        self.assertFalse(result["credit_eligible"])
        self.assertIn("E3B_ENVELOPE_FORMAT_INVALID", result["blocking_codes"])

    def test_synthetic_valid_mac_only_proves_metadata_integrity(self):
        r = gate.verify(signed(payload()), TEST_KEY)
        self.assertTrue(r["mac_integrity_verified"])
        self.assertFalse(r["new_unseen_item_verified"])
        self.assertFalse(r["authenticated_unaided_attempt_verified"])
        self.assertFalse(r["mathematical_reasoning_verified"])
        self.assertFalse(r["credit_eligible"])
        self.assertEqual(r["academic_status"], "HOLD_NOT_ACCEPTED")

    def test_any_changed_field_invalidates_mac(self):
        e = signed(payload())
        e["payload"]["rubric_sha256"] = "e" * 64
        self.assertIn("E3B_MAC_TAMPERED_OR_WRONG_KEY",
                      gate.verify(e, TEST_KEY)["blocking_codes"])

    def test_wrong_key_missing_key_short_key_rejected(self):
        for k in (None, b"short", b"x" * 64):
            with self.subTest(length=len(k) if k else 0):
                self.assertFalse(gate.verify(signed(payload()), k)["mac_integrity_verified"])

    def test_disclosed_existing_question_cannot_count_as_new(self):
        pkg = json.loads(gate.PACKAGE.read_text())
        golden = json.loads(gate.GOLDEN.read_text())
        exposed = gate.disclosed_hashes(pkg, golden)
        stem = next(q["stem"] for q in pkg["questions"]
                    if q["id"] == "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01")
        digest = hashlib.sha256(stem.encode("utf-8")).hexdigest()
        self.assertIn(digest, exposed)
        p = payload()
        p["item_content_sha256"] = digest
        self.assertIn("E3B_REPOSITORY_DISCLOSED_ITEM",
                      gate.verify(signed(p), TEST_KEY, exposed)["blocking_codes"])

    def test_chronology_reversal_and_answer_disclosure_rejected(self):
        p = payload()
        p["first_attempt_utc"] = p["repair_complete_utc"]
        p["new_item_answer_count"] = 1
        codes = gate.verify(signed(p), TEST_KEY)["blocking_codes"]
        self.assertIn("E3B_CHRONOLOGY_INVALID", codes)
        self.assertIn("E3B_ASSISTANCE_OR_ANSWER_EXPOSURE", codes)

    def test_bool_not_accepted_as_zero_count(self):
        p = payload()
        p["new_item_hint_count"] = False
        self.assertIn("E3B_ASSISTANCE_OR_ANSWER_EXPOSURE",
                      gate.verify(signed(p), TEST_KEY)["blocking_codes"])

    def test_self_claimed_review_is_rejected(self):
        p = payload()
        p["math_review_status"] = "APPROVED"
        self.assertIn("E3B_SELF_AWARDED_REVIEW_UNAUTHORIZED",
                      gate.verify(signed(p), TEST_KEY)["blocking_codes"])

    def test_extra_student_identity_and_answer_are_rejected_and_not_echoed(self):
        sentinel = "PRIVATE_CHILD_DETAILS_DO_NOT_COPY"
        p = payload()
        p["learner_name"] = sentinel
        p["answer_text"] = sentinel
        r = gate.verify(signed(p), TEST_KEY)
        self.assertIn("E3B_PAYLOAD_FIELDS_INVALID", r["blocking_codes"])
        self.assertNotIn(sentinel, json.dumps(r))

    def test_malformed_header_and_digest_denied(self):
        p = payload()
        p["item_content_sha256"] = "not-a-digest"
        self.assertIn("E3B_HASH_FIELD_INVALID",
                      gate.verify(signed(p), TEST_KEY)["blocking_codes"])

    def test_real_environment_absent_strict_cli_refuses_claim(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "--require-external-integrity"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("NO_TRUSTED_ASSESSOR_WITNESS", p.stdout)


if __name__ == "__main__":
    unittest.main()
