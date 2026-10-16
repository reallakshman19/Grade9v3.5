#!/usr/bin/env python3
"""Create an answer-withheld, source-bound NLM Physics Pass A intake.

Input is the real candidate source on the current draft branch. No answer,
model oracle, hint, prior review, protected move, rubric or Post-A comparison
is allowed into the Stage A packet. Does not authenticate a human reviewer,
declare cognitive novelty, approve academic content or release any product.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

QUESTION_ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"
PACKAGE_RELATIVE = Path("Physics/library/phy-nlm-first-law.v1.json")
EXPECTED_SOURCE_BLOB = "fc80cc53261b3c4932836795333e7cffe35a5133"
EXPECTED_QUESTION_SHA = "310f32e0b09d1628b53e98164c46db477b84ab45ee20701ee43a01bc88c5d616"
REPO = Path(__file__).resolve().parents[2]


def compact_sha(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def build_blind_packet(*, root: Path = REPO) -> dict:
    source = (root / PACKAGE_RELATIVE).read_bytes()
    actual_blob = blob_sha(source)
    if actual_blob != EXPECTED_SOURCE_BLOB:
        raise ValueError(f"REVIEW_SOURCE_BLOB_DRIFT:{actual_blob}")
    doc = json.loads(source)
    matches = [q for q in doc.get("questions", []) if isinstance(q, dict)
               and q.get("id") == QUESTION_ID]
    if len(matches) != 1:
        raise ValueError("REVIEW_QUESTION_NOT_UNIQUE")
    question = matches[0]
    actual_question = compact_sha(question)
    if actual_question != EXPECTED_QUESTION_SHA:
        raise ValueError(f"REVIEW_QUESTION_DRIFT:{actual_question}")
    # Explicit allowlist prevents additions to canonical schema from leaking an
    # author answer or hint into the reviewer-facing blind packet.
    if not isinstance(question.get("stem"), str) or not isinstance(question.get("conditions"), list):
        raise ValueError("REVIEW_STEM_OR_CONDITIONS_INVALID")
    packet = {
        "schema": "physics-qrt.nlm289-blind-intake/v1",
        "phase": "PASS_A_ANSWER_WITHHELD",
        "question_id": QUESTION_ID,
        "source_path": PACKAGE_RELATIVE.as_posix(),
        "source_git_blob": EXPECTED_SOURCE_BLOB,
        "question_sha256": EXPECTED_QUESTION_SHA,
        "question_stem": question["stem"],
        "question_conditions": question["conditions"],
        "reviewer_qualification": "INDEPENDENT_HUMAN_NOT_ASSIGNED",
        "academic_verdict": "NOT_REVIEWED",
        "transfer_novelty_verdict": "NOT_REVIEWED",
        "qrt_verdict": "NOT_RUN",
        "release_verdict": "HOLD",
        "instructions": (
            "Qualified independent Physics reviewer: without opening source "
            "library, PR #295/#296/#297 solution, old full packets, or authored "
            "answers, derive from the question stem and conditions only. "
            "Freeze signed derivation, units, assumptions, threshold-equality "
            "interpretation, viable alternatives, falsifiers and reviewer identity "
            "with these exact source and question digests. Pass B may begin only "
            "after the independent Pass A receipt is authenticated by C0."
        )
    }
    packet["packet_sha256"] = compact_sha(packet)
    return packet


def validate_blind_packet(packet: dict) -> None:
    allowed = {"schema", "phase", "question_id", "source_path", "source_git_blob",
               "question_sha256", "question_stem", "question_conditions",
               "reviewer_qualification", "academic_verdict", "transfer_novelty_verdict",
               "qrt_verdict", "release_verdict", "instructions", "packet_sha256"}
    if set(packet) != allowed or packet.get("phase") != "PASS_A_ANSWER_WITHHELD":
        raise ValueError("BLIND_PACKET_SCHEMA_OR_PHASE_WRONG")
    forbidden = ("answer", "hint", "rubric", "oracle", "candidate_recomputed_prediction",
                 "reasoning_route", "falsifiers", "protected_move_ref", "61 N is sufficient only")
    body = json.dumps(packet, ensure_ascii=False, sort_keys=True)
    for secret in forbidden:
        if secret.lower() in (str(packet["question_stem"])+" "+
                              " ".join(packet["question_conditions"])).lower() and secret in ("answer", "hint", "rubric", "oracle"):
            raise ValueError(f"BLIND_QUESTION_INPUT_LEAK:{secret}")
    if compact_sha({key: value for key, value in packet.items() if key != "packet_sha256"}) != packet["packet_sha256"]:
        raise ValueError("BLIND_PACKET_DIGEST_MISMATCH")
    if any(key in body for key in ('"authored_answer_claim"', '"proposed_physics_model"',
                                  '"candidate_recomputed_prediction"', '"reasoning_route"',
                                  '"rubric"', '"hints"')):
        raise ValueError("BLIND_PACKET_ANSWER_FIELDS_PRESENT")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    scratch = (REPO / "build").resolve()
    if not out.is_relative_to(scratch) or out.name != "nlm289-pass-a.json":
        raise SystemExit("BLIND_PACKET_OUTSIDE_TEMP_BUILD_REFUSED")
    result = build_blind_packet()
    validate_blind_packet(result)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "phase": result["phase"],
        "source_git_blob": result["source_git_blob"],
        "question_sha256": result["question_sha256"],
        "packet_sha256": result["packet_sha256"],
        "reviewer": "UNASSIGNED",
        "human_approval": "NOT_OBTAINED",
        "released": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
