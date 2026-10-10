#!/usr/bin/env python3
"""F02 E3-B TEST-only external assessor metadata integrity, NEVER academic credit."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import hmac
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
GOLDEN = ROOT / "TEST/imo-research/golden/imo-327-model-d3.v1.json"
SCHEMA = "imo-f02-e3-assessor-digest/v1"
SECRET_ENV = "IMO_E3_EXTERNAL_ASSESSOR_KEY_HEX"
HASH = re.compile(r"[0-9a-f]{64}\Z")
FIELDS = frozenset((
    "schema", "item_content_sha256", "rubric_sha256", "session_nonce_sha256",
    "first_attempt_sha256", "custody_scope", "repair_complete_utc",
    "item_delivered_utc", "first_attempt_utc", "new_item_hint_count",
    "new_item_answer_count", "math_review_status", "curriculum_review_status",
))
HASH_FIELDS = ("item_content_sha256", "rubric_sha256",
               "session_nonce_sha256", "first_attempt_sha256")
TIMES = ("repair_complete_utc", "item_delivered_utc", "first_attempt_utc")


def canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def disclosed_hashes(package: dict, golden: dict) -> set[str]:
    """Hash committed disclosed stems and exits, not secret assessment material."""
    phrases = [q.get("stem") for q in package.get("questions", []) if isinstance(q, dict)]
    phrases.extend(m.get("exit_task", {}).get("prompt") for m in package.get("microtopics", [])
                   if isinstance(m, dict))
    phrases.extend(s.get("text") for s in golden.get("core1a_repair", {}).get("sequence", [])
                   if isinstance(s, dict) and s.get("stage") == "FRESH_INDEPENDENT_EXIT")
    return {hashlib.sha256(p.encode("utf-8")).hexdigest() for p in phrases
            if isinstance(p, str) and p}


def parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        result = datetime.fromisoformat(value[:-1] + "+00:00")
        return result if result.utcoffset().total_seconds() == 0 else None
    except ValueError:
        return None


def result(codes: list[str], integrity: bool = False) -> dict:
    """Fixed enumerated codes only: never copy raw identity, answers or input."""
    return {
        "schema": "imo-f02-e3-assessor-integrity-result/v1",
        "subject": "TEST",
        "integrity_status": ("MAC_INTEGRITY_ONLY_REVIEW_REQUIRED" if integrity
                             else "EXTERNAL_INTEGRITY_NOT_ESTABLISHED"),
        "mac_integrity_verified": integrity,
        "new_unseen_item_verified": False,
        "authenticated_unaided_attempt_verified": False,
        "mathematical_reasoning_verified": False,
        "independent_mastery_verified": False,
        "credit_eligible": False,
        "academic_status": "HOLD_NOT_ACCEPTED",
        "learner_release_authorized": False,
        "blocking_codes": sorted(set(codes)),
    }


def verify(envelope: object, external_key: bytes | None,
           exposed_digest_set: set[str] | None = None) -> dict:
    if not isinstance(envelope, dict) or set(envelope) != {"payload", "hmac_sha256"}:
        return result(["E3B_ENVELOPE_FORMAT_INVALID"])
    payload, mac = envelope["payload"], envelope["hmac_sha256"]
    if not isinstance(payload, dict) or set(payload) != FIELDS:
        return result(["E3B_PAYLOAD_FIELDS_INVALID"])
    codes = []
    if payload["schema"] != SCHEMA:
        codes.append("E3B_SCHEMA_UNRECOGNIZED")
    if any(not isinstance(payload[k], str) or not HASH.fullmatch(payload[k])
           for k in HASH_FIELDS):
        codes.append("E3B_HASH_FIELD_INVALID")
    if (not "E3B_HASH_FIELD_INVALID" in codes
            and payload["item_content_sha256"] in (exposed_digest_set or set())):
        codes.append("E3B_REPOSITORY_DISCLOSED_ITEM")
    if payload["custody_scope"] != "ASSESSOR_HELD_PRIVATE_UNPUBLISHED":
        codes.append("E3B_EXTERNAL_CUSTODY_NOT_ESTABLISHED")
    timestamps = [parse_utc(payload[k]) for k in TIMES]
    if any(v is None for v in timestamps) or not (
            timestamps[0] < timestamps[1] < timestamps[2]):
        codes.append("E3B_CHRONOLOGY_INVALID")
    if (type(payload["new_item_hint_count"]) is not int
            or type(payload["new_item_answer_count"]) is not int
            or payload["new_item_hint_count"] != 0
            or payload["new_item_answer_count"] != 0):
        codes.append("E3B_ASSISTANCE_OR_ANSWER_EXPOSURE")
    if (payload["math_review_status"] != "NOT_YET_INDEPENDENTLY_REVIEWED"
            or payload["curriculum_review_status"] != "GRADE9_DECISION_PENDING"):
        codes.append("E3B_SELF_AWARDED_REVIEW_UNAUTHORIZED")
    if not isinstance(mac, str) or not HASH.fullmatch(mac):
        codes.append("E3B_MAC_FORMAT_INVALID")
    if not isinstance(external_key, bytes) or len(external_key) < 32:
        codes.append("E3B_EXTERNAL_KEY_UNAVAILABLE")
    if codes:
        return result(codes)
    expected = hmac.new(external_key, canonical(payload), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, mac):
        return result(["E3B_MAC_TAMPERED_OR_WRONG_KEY"])
    # MAC authenticates metadata only relative to a separately trusted key holder.
    # It does not witness actual event truth or independent academic approval.
    return result(["E3B_HUMAN_ASSESSOR_TRUTH_REVIEW_REQUIRED",
                   "E3B_INDEPENDENT_UNSEENNESS_AND_FIRST_ATTEMPT_UNVERIFIED",
                   "E3B_CURRICULUM_QRT_AND_OWNER_REVIEW_PENDING"], True)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate field")
        out[key] = value
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-envelope", type=Path,
                        help="Private metadata only. Never item, learner name or answer.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-external-integrity", action="store_true")
    args = parser.parse_args()
    if args.private_envelope is None:
        report = result(["E3B_ASSESSOR_METADATA_NOT_PROVIDED",
                         "E3B_EXTERNAL_KEY_UNAVAILABLE"])
    else:
        try:
            envelope = json.loads(args.private_envelope.read_text(encoding="utf-8"),
                                  object_pairs_hook=unique_keys)
            package = json.loads(PACKAGE.read_text(encoding="utf-8"))
            golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
            exposed = disclosed_hashes(package, golden)
            try:
                key = bytes.fromhex(os.environ.get(SECRET_ENV, ""))
            except ValueError:
                key = None
            report = verify(envelope, key, exposed)
        except (OSError, UnicodeError, TypeError, ValueError, KeyError, IndexError):
            report = result(["E3B_PRIVATE_ENVELOPE_UNREADABLE"])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                               encoding="utf-8")
    print("E3B_" + ("METADATA_INTEGRITY_ONLY" if report["mac_integrity_verified"]
                    else "NO_TRUSTED_ASSESSOR_WITNESS")
          + "; ACADEMIC_AND_PUBLICATION_HOLD")
    return int(args.require_external_integrity and not report["mac_integrity_verified"])


if __name__ == "__main__":
    raise SystemExit(main())
