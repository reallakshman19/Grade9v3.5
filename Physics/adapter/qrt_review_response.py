"""Structural checks for a future independent Physics review (not authentication).

Reviewers must independently work each question. Structural compliance is only
eligibility for Owner/coordinator verification; this program cannot determine
reviewer identity, competency, accuracy of derivation or scientific correctness.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from Physics.adapter.qrt_review_packet import recompute_packet_sha256

HEX64 = re.compile(r"^[0-9a-f]{64}$")
FINAL = {"ACCEPT", "REVISE", "REJECT"}


def validate_review_response(packet: dict, response: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict) or packet.get("schema") != "physics-qrt.science-review-request/v1":
        return ["REVIEW_REQUEST_SCHEMA"]
    if not isinstance(response, dict) or response.get("schema") != "physics-qrt.science-review-response/v1":
        return ["REVIEW_RESPONSE_SCHEMA"]
    if (not isinstance(packet.get("packet_sha256"), str)
            or not HEX64.fullmatch(packet["packet_sha256"])
            or response.get("packet_sha256") != packet.get("packet_sha256")):
        errors.append("REVIEW_WRONG_PACKET_SHA")
    # A forged packet with the original declared digest must never pass.
    try:
        if recompute_packet_sha256(packet) != packet.get("packet_sha256"):
            errors.append("PACKET_CONTENT_DIGEST_MISMATCH")
    except (ValueError, TypeError, OverflowError):
        errors.append("PACKET_CONTENT_DIGEST_INVALID")
    if response.get("source_base_sha") != packet.get("base_sha"):
        errors.append("REVIEW_STALE_SOURCE_BASE")
    reviewer = response.get("reviewer")
    if not isinstance(reviewer, dict):
        reviewer = {}
        errors.append("REVIEWER_OBJECT_REQUIRED")
    ident = reviewer.get("identity")
    if not isinstance(ident, str) or len(ident.strip()) < 3:
        errors.append("REVIEWER_IDENTITY_MISSING")
    if reviewer.get("independent_of_implementation") is not True:
        errors.append("REVIEWER_INDEPENDENCE_NOT_ASSERTED")
    if not isinstance(reviewer.get("competence_basis"), str) or not reviewer["competence_basis"].strip():
        errors.append("REVIEWER_COMPETENCE_NOT_ASSERTED")
    if not isinstance(reviewer.get("authentication_ref"), str) or not reviewer["authentication_ref"].strip():
        errors.append("REVIEW_AUTHENTICATION_REF_MISSING")
    expected = {q["question_id"]: q for q in packet.get("questions", [])}
    entries = response.get("per_question")
    if not isinstance(entries, list):
        entries = []
        errors.append("PER_QUESTION_NOT_ARRAY")
    seen: set[str] = set()
    for i, item in enumerate(entries):
        if not isinstance(item, dict):
            errors.append(f"REVIEW_ITEM_NOT_OBJECT:{i}")
            continue
        qid = item.get("question_id")
        if qid not in expected:
            errors.append(f"REVIEW_UNKNOWN_QUESTION:{i}")
            continue
        if qid in seen:
            errors.append(f"REVIEW_DUPLICATE_QUESTION:{qid}")
        seen.add(qid)
        if item.get("question_sha256") != expected[qid].get("question_sha256"):
            errors.append(f"REVIEW_QUESTION_SHA_MISMATCH:{qid}")
        if item.get("verdict") not in FINAL:
            errors.append(f"REVIEW_VERDICT_NOT_DECIDED:{qid}")
        if not isinstance(item.get("independent_derivation"), str) or len(item["independent_derivation"].strip()) < 30:
            errors.append(f"REVIEW_DERIVATION_MISSING:{qid}")
        if not isinstance(item.get("model_assumption_judgement"), str) or len(item["model_assumption_judgement"].strip()) < 15:
            errors.append(f"REVIEW_MODEL_APPLICABILITY_MISSING:{qid}")
        if not isinstance(item.get("falsifier_results"), list):
            errors.append(f"REVIEW_FALSIFIERS_MISSING:{qid}")
        else:
            results = item["falsifier_results"]
            required = expected[qid]["required_model_falsifiers"]
            covered = {v.get("case") for v in results if isinstance(v, dict)}
            if not set(required).issubset(covered):
                errors.append(f"REVIEW_FALSIFIERS_INCOMPLETE:{qid}")
            if any(not isinstance(v, dict) or v.get("outcome") not in ("REJECTS_FALSE_RESULT", "EXPOSES_GAP")
                   or not isinstance(v.get("reason"), str) or not v["reason"].strip()
                   for v in results):
                errors.append(f"REVIEW_FALSIFIER_RESULT_UNJUSTIFIED:{qid}")
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(s, str) or not s.strip() for s in refs):
            errors.append(f"REVIEW_EVIDENCE_MISSING:{qid}")
    if set(expected) != seen:
        errors.append("REVIEW_SET_INCOMPLETE")
    if response.get("overall") not in ("ACCEPT", "REVISE", "REJECT"):
        errors.append("OVERALL_VERDICT_MISSING")
    if (response.get("overall") == "ACCEPT"
            and any(isinstance(x, dict) and x.get("verdict") != "ACCEPT" for x in entries)):
        errors.append("OVERALL_ACCEPT_WITH_NONACCEPT_CASE")
    return errors


def evaluate(packet: dict, response: dict) -> dict:
    errors = validate_review_response(packet, response)
    return {
        "schema": "physics-qrt.review-response-check/v1",
        "structurally_complete": not errors,
        "status": "REVIEW_SUBMITTED_FOR_AUTHENTICATION" if not errors else "REVIEW_INCOMPLETE",
        "reviewer_authenticity": "NOT_VERIFIED_BY_THIS_TOOL",
        "science_certification": "NOT_GRANTED_BY_THIS_TOOL",
        "owner_authorization": "NOT_GRANTED_BY_THIS_TOOL",
        "release_verdict": "HOLD",
        "errors": errors
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--response", required=True)
    args = parser.parse_args()
    try:
        packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
        response = json.loads(Path(args.response).read_text(encoding="utf-8"))
        result = evaluate(packet, response)
    except (ValueError, OSError) as exc:
        result = {"status": "REVIEW_INCOMPLETE", "release_verdict": "HOLD",
                  "errors": [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "REVIEW_SUBMITTED_FOR_AUTHENTICATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
