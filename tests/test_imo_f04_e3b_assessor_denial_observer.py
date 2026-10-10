"""Independent F04 E3-B tests: synthetic MAC integrity is NOT learner proof."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import unittest

from Shared.tools.imo_f04_e3b_assessor_denial_observer import (
    ABSENCE_CODES, NO_AUTHORITY, evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
E3B = ROOT / "TEST/imo-research/candidates/imo_f02_e3_assessor_integrity.py"
spec = importlib.util.spec_from_file_location("f02_e3b_f04_denial_test", E3B)
f02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f02)
FIXTURE_KEY = b"EXPLICIT-SYNTHETIC-AGENT3-TEST-KEY-NOT-AN-ASSESSOR"
COMMIT = "a" * 40
DIGEST = "b" * 64


def no_assessor_receipt() -> dict:
    return {
        "schema": "imo-f02-e3-assessor-integrity-result/v1",
        "subject": "TEST",
        "integrity_status": "EXTERNAL_INTEGRITY_NOT_ESTABLISHED",
        "mac_integrity_verified": False,
        "new_unseen_item_verified": False,
        "authenticated_unaided_attempt_verified": False,
        "mathematical_reasoning_verified": False,
        "independent_mastery_verified": False,
        "credit_eligible": False,
        "academic_status": "HOLD_NOT_ACCEPTED",
        "learner_release_authorized": False,
        "blocking_codes": list(ABSENCE_CODES),
    }


def synthetic_metadata() -> dict:
    at = datetime(2026, 10, 10, tzinfo=timezone.utc)
    stamp = lambda t: t.isoformat().replace("+00:00", "Z")
    return {
        "schema": "imo-f02-e3-assessor-digest/v1",
        "item_content_sha256": "1" * 64,
        "rubric_sha256": "2" * 64,
        "session_nonce_sha256": "3" * 64,
        "first_attempt_sha256": "4" * 64,
        "custody_scope": "ASSESSOR_HELD_PRIVATE_UNPUBLISHED",
        "repair_complete_utc": stamp(at),
        "item_delivered_utc": stamp(at + timedelta(minutes=2)),
        "first_attempt_utc": stamp(at + timedelta(minutes=7)),
        "new_item_hint_count": 0,
        "new_item_answer_count": 0,
        "math_review_status": "NOT_YET_INDEPENDENTLY_REVIEWED",
        "curriculum_review_status": "GRADE9_DECISION_PENDING",
    }


def envelope(payload: dict, key: bytes = FIXTURE_KEY) -> dict:
    mac = hmac.new(key, f02.canonical(payload), hashlib.sha256).hexdigest()
    return {"payload": copy.deepcopy(payload), "hmac_sha256": mac}


class F04E3BAssessorIntegrityDenial(unittest.TestCase):
    def check_receipt(self, receipt=None, actual=COMMIT, expected=COMMIT):
        return evaluate(no_assessor_receipt() if receipt is None else receipt,
                        DIGEST, DIGEST, DIGEST, expected, actual)

    def test_01_no_external_assessor_receipt_is_valid_denial_only(self):
        result = self.check_receipt()
        self.assertEqual(result["status"], "EXTERNAL_ASSESSOR_NOT_ATTESTED_REVIEW_HOLD")
        self.assertEqual(result["blocking_codes"], [])
        self.assertFalse(result["external_key_independently_custodied"])
        for name in ("new_unseen_item_independently_verified",
                     "first_unaided_attempt_authenticated",
                     "reasoning_rubric_independently_accepted", "source_core2_admitted",
                     "academic_accepted", "learner_mastery_verified", "release_authorized"):
            self.assertIs(result[name], False)

    def test_02_missing_forged_or_malformed_denial_receipts_block(self):
        self.assertIn("E3B_F04_RECEIPT_INVALID",
                      evaluate(None, DIGEST, DIGEST, DIGEST, COMMIT, COMMIT)["blocking_codes"])
        for field, value, code in (
            ("mac_integrity_verified", True, "E3B_F04_EXTERNAL_WITNESS_NOT_ESTABLISHED"),
            ("academic_status", "APPROVED", "E3B_F04_EXTERNAL_WITNESS_NOT_ESTABLISHED"),
            ("integrity_status", "MAC_INTEGRITY_ONLY_REVIEW_REQUIRED", "E3B_F04_EXTERNAL_WITNESS_NOT_ESTABLISHED"),
            ("credit_eligible", True, "E3B_F04_UNAUTHORIZED_LEARNER_CREDIT_OR_RELEASE"),
            ("new_unseen_item_verified", True, "E3B_F04_UNAUTHORIZED_LEARNER_CREDIT_OR_RELEASE"),
            ("learner_release_authorized", True, "E3B_F04_UNAUTHORIZED_LEARNER_CREDIT_OR_RELEASE"),
            ("blocking_codes", [], "E3B_F04_ASSESSOR_ABSENCE_CODES_DRIFT"),
        ):
            with self.subTest(field=field):
                data = no_assessor_receipt()
                data[field] = value
                self.assertIn(code, self.check_receipt(data)["blocking_codes"])

    def test_03_private_responses_and_unexpected_fields_not_echoed(self):
        secret = "PRIVATE-STUDENT-ANSWER-DO-NOT-COPY"
        data = no_assessor_receipt()
        data["student_response"] = secret
        data["blocking_codes"] = [secret]
        result = self.check_receipt(data)
        self.assertIn("E3B_F04_RECEIPT_SCHEMA_INVALID", result["blocking_codes"])
        self.assertNotIn(secret, json.dumps(result))

    def test_04_checkout_and_source_digest_mismatch_block(self):
        result = self.check_receipt(actual="c" * 40)
        self.assertIn("E3B_F04_CHECKOUT_SHA_MISMATCH", result["blocking_codes"])
        data = evaluate(no_assessor_receipt(), "NO_DIGEST", DIGEST, DIGEST, COMMIT, COMMIT)
        self.assertIn("E3B_F04_SOURCE_DIGEST_INVALID", data["blocking_codes"])
        self.assertIn("E3B_F04_CHECKOUT_SHA_MISMATCH",
                      self.check_receipt(expected="bad")["blocking_codes"])

    def test_05_synthetic_valid_hmac_only_integrity_not_mastery(self):
        result = f02.verify(envelope(synthetic_metadata()), FIXTURE_KEY)
        self.assertTrue(result["mac_integrity_verified"])
        self.assertEqual(result["integrity_status"], "MAC_INTEGRITY_ONLY_REVIEW_REQUIRED")
        self.assertEqual(result["academic_status"], "HOLD_NOT_ACCEPTED")
        for field in NO_AUTHORITY:
            if field in result:
                self.assertIs(result[field], False)
        self.assertIn("E3B_HUMAN_ASSESSOR_TRUTH_REVIEW_REQUIRED", result["blocking_codes"])

    def test_06_self_chosen_key_can_sign_metadata_but_cannot_prove_independence(self):
        claimant_key = b"CLAIMANT-CONTROLS-THIS-SYNTHETIC-KEY-NOT-AN-ASSESSOR"
        report = f02.verify(envelope(synthetic_metadata(), claimant_key), claimant_key)
        self.assertTrue(report["mac_integrity_verified"])
        self.assertIs(report["credit_eligible"], False)
        self.assertIs(report["authenticated_unaided_attempt_verified"], False)
        self.assertIs(report["new_unseen_item_verified"], False)

    def test_07_changed_or_wrong_mac_and_leaked_fields_rejected(self):
        signed = envelope(synthetic_metadata())
        signed["payload"]["first_attempt_sha256"] = "f" * 64
        self.assertIn("E3B_MAC_TAMPERED_OR_WRONG_KEY",
                      f02.verify(signed, FIXTURE_KEY)["blocking_codes"])
        signed = envelope(synthetic_metadata())
        self.assertIn("E3B_MAC_TAMPERED_OR_WRONG_KEY",
                      f02.verify(signed, b"WRONG-TEST-KEY-AT-LEAST-32-BYTES-XXXXXXXX")["blocking_codes"])
        payload = synthetic_metadata()
        payload["student_name"] = "PRIVATE-IDENTITY"
        self.assertIn("E3B_PAYLOAD_FIELDS_INVALID",
                      f02.verify(envelope(payload), FIXTURE_KEY)["blocking_codes"])

    def test_08_invalid_chronology_and_help_count_denied(self):
        data = synthetic_metadata()
        data["first_attempt_utc"] = data["repair_complete_utc"]
        data["new_item_hint_count"] = 1
        codes = f02.verify(envelope(data), FIXTURE_KEY)["blocking_codes"]
        self.assertIn("E3B_CHRONOLOGY_INVALID", codes)
        self.assertIn("E3B_ASSISTANCE_OR_ANSWER_EXPOSURE", codes)

    def test_09_disclosed_existing_exact_stem_not_unseen(self):
        package=json.loads(f02.PACKAGE.read_text(encoding="utf-8"))
        golden=json.loads(f02.GOLDEN.read_text(encoding="utf-8"))
        exposed=f02.disclosed_hashes(package,golden)
        item=next(q["stem"] for q in package["questions"] if q.get("id") ==
                  "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01")
        data=synthetic_metadata()
        data["item_content_sha256"]=hashlib.sha256(item.encode("utf-8")).hexdigest()
        self.assertIn("E3B_REPOSITORY_DISCLOSED_ITEM",
                      f02.verify(envelope(data), FIXTURE_KEY, exposed)["blocking_codes"])

    def test_10_malformed_record_and_duplicate_json_fields_denied(self):
        self.assertIn("E3B_PAYLOAD_FIELDS_INVALID",
                      f02.verify({"payload": {}, "hmac_sha256": "0" * 64},
                                 FIXTURE_KEY)["blocking_codes"])
        with self.assertRaises(ValueError):
            json.loads('{"payload":{},"payload":{}}', object_pairs_hook=f02.unique_keys)

    def test_11_arbitrary_deceptive_extra_authority_never_passes_observer(self):
        data = no_assessor_receipt()
        data["independent_mastery_verified"] = True
        self.assertIn("E3B_F04_UNAUTHORIZED_LEARNER_CREDIT_OR_RELEASE",
                      self.check_receipt(data)["blocking_codes"])
        data = no_assessor_receipt()
        del data["blocking_codes"]
        self.assertIn("E3B_F04_RECEIPT_SCHEMA_INVALID",
                      self.check_receipt(data)["blocking_codes"])


if __name__ == "__main__":
    unittest.main()
