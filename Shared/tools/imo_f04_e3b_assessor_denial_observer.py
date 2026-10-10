"""F04 TEST-only observer for F02 E3-B assessor-metadata integrity denial.

This is not a trusted assessor, custody attestation, student identity check,
math rubric, independent mastery decision, academic admission or release gate.
An HMAC alone only authenticates bytes relative to a key *whose independent
ownership must be established outside GitHub*. Public output is fixed codes
and SHA-256 digests only; never upload private items, keys or learner answers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("TEST/imo-research/candidates/imo_f02_e3_assessor_integrity.py")
TEST = Path("tests/test_imo_138_e3_assessor_integrity.py")
EXPECTED = {
    "schema", "subject", "integrity_status", "mac_integrity_verified",
    "new_unseen_item_verified", "authenticated_unaided_attempt_verified",
    "mathematical_reasoning_verified", "independent_mastery_verified",
    "credit_eligible", "academic_status", "learner_release_authorized",
    "blocking_codes",
}
NO_AUTHORITY = (
    "new_unseen_item_verified",
    "authenticated_unaided_attempt_verified",
    "mathematical_reasoning_verified",
    "independent_mastery_verified",
    "credit_eligible",
    "learner_release_authorized",
)
ABSENCE_CODES = [
    "E3B_ASSESSOR_METADATA_NOT_PROVIDED", "E3B_EXTERNAL_KEY_UNAVAILABLE"
]
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def evaluate(receipt: object, source_sha: str, test_sha: str,
             receipt_sha: str, expected_commit: str,
             actual_commit: str) -> dict:
    """Fixed enums/digests only: never copy untrusted source or private fields."""
    codes: list[str] = []
    if not SHA40.fullmatch(expected_commit or "") or actual_commit != expected_commit:
        codes.append("E3B_F04_CHECKOUT_SHA_MISMATCH")
    if not isinstance(receipt, dict):
        codes.append("E3B_F04_RECEIPT_INVALID")
    else:
        if set(receipt) != EXPECTED or receipt.get("schema") != "imo-f02-e3-assessor-integrity-result/v1" or receipt.get("subject") != "TEST":
            codes.append("E3B_F04_RECEIPT_SCHEMA_INVALID")
        if (receipt.get("integrity_status") != "EXTERNAL_INTEGRITY_NOT_ESTABLISHED"
            or receipt.get("mac_integrity_verified") is not False
            or receipt.get("academic_status") != "HOLD_NOT_ACCEPTED"):
            codes.append("E3B_F04_EXTERNAL_WITNESS_NOT_ESTABLISHED")
        if any(receipt.get(key) is not False for key in NO_AUTHORITY):
            codes.append("E3B_F04_UNAUTHORIZED_LEARNER_CREDIT_OR_RELEASE")
        if receipt.get("blocking_codes") != ABSENCE_CODES:
            codes.append("E3B_F04_ASSESSOR_ABSENCE_CODES_DRIFT")
    if any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
        for value in (source_sha, test_sha, receipt_sha)
    ):
        codes.append("E3B_F04_SOURCE_DIGEST_INVALID")
    codes = sorted(set(codes))
    return {
        "schema": "imo-f04-e3b-external-assessor-denial-observer/v1",
        "status": "EXTERNAL_ASSESSOR_NOT_ATTESTED_REVIEW_HOLD" if not codes else "BLOCKED",
        "blocking_codes": codes,
        "checkout_sha": expected_commit if SHA40.fullmatch(expected_commit or "") else "INVALID",
        "source_sha256": {
            "f02_e3b_source": source_sha,
            "f02_e3b_negative_tests": test_sha,
            "no_external_assessor_receipt": receipt_sha,
        },
        "synthetic_hmac_fixture_is_not_assessor_proof": True,
        "external_key_independently_custodied": False,
        "new_unseen_item_independently_verified": False,
        "first_unaided_attempt_authenticated": False,
        "reasoning_rubric_independently_accepted": False,
        "source_core2_admitted": False,
        "academic_accepted": False,
        "learner_mastery_verified": False,
        "release_authorized": False,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--safe-summary", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                         stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        actual = "GIT_UNAVAILABLE"
    try:
        report = json.loads(args.receipt.read_text(encoding="utf-8"))
        digests = [sha(ROOT / SOURCE), sha(ROOT / TEST), sha(args.receipt)]
    except (OSError, ValueError, UnicodeError, TypeError):
        report = None
        digests = ["INVALID"] * 3
    result = evaluate(report, *digests, args.expected_sha, actual)
    if "build" not in args.safe_summary.parts:
        print("E3B_F04_OUTPUT_PATH_UNSAFE; REVIEW_RELEASE_HOLD")
        return 1
    args.safe_summary.parent.mkdir(parents=True, exist_ok=True)
    args.safe_summary.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                                 encoding="utf-8")
    print("E3B_F04_ASSessor_HOLD_".upper()
          + ("PASS" if result["status"] != "BLOCKED" else "BLOCKED")
          + "; NO_UNSEEN_TRANSFER_OR_ACADEMIC_RELEASE")
    return int(bool(result["blocking_codes"]))


if __name__ == "__main__":
    raise SystemExit(main())
