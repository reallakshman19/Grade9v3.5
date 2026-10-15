#!/usr/bin/env python3
"""#182 R13: native postcommit engineering repair matrix; never QRT acceptance."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

CHECKS = {
    "attempt_blank_rejected": "NAV_POSTCOMMIT_BLANK_UNLOCKED",
    "nonempty_attempt_committed": "NAV_POSTCOMMIT_VALID_ATTEMPT_NOT_COMMITTED",
    "precommit_solution_locked": "NAV_POSTCOMMIT_PREATTEMPT_SOLUTION_LEAK",
    "postcommit_context_link_present": "NAV_POSTCOMMIT_CONTEXT_LINK_MISSING",
    "context_link_is_pinned": "NAV_POSTCOMMIT_CONTEXT_WRONG_CONCEPT",
    "concept_reached": "NAV_POSTCOMMIT_CONCEPT_NOT_REACHED",
    "concept_is_pinned": "NAV_POSTCOMMIT_CONCEPT_ID_DRIFT",
    "return_link_present": "NAV_POSTCOMMIT_RETURN_LINK_MISSING",
    "return_link_is_pinned": "NAV_POSTCOMMIT_RETURN_WRONG_QUESTION",
    "same_question_reached": "NAV_POSTCOMMIT_SOURCE_QUESTION_LOST",
    "attempt_text_restored": "NAV_POSTCOMMIT_SOURCE_DRAFT_NOT_RESTORED",
    "assistance_marked": "NAV_POSTCOMMIT_ASSISTANCE_UNMARKED",
}
REPAIR_GROUPS = {
    "POSTCOMMIT_CONTEXT_LINK": ("postcommit_context_link_present", "context_link_is_pinned"),
    "TARGETED_SAME_QUESTION_RETURN": ("return_link_present", "return_link_is_pinned"),
    "ATTEMPT_DRAFT_PERSISTENCE": ("attempt_text_restored",),
    "ASSISTED_STATE_NO_INDEPENDENT_CREDIT": ("assistance_marked",),
}


def require(condition: bool, code: str, cell: str = "") -> None:
    if not condition:
        raise ValueError(f"{code}: {cell}")


def reported_defects(observed: dict) -> list[str]:
    problems = [code for name, code in CHECKS.items()
                if observed.get(name) is not True]
    if observed.get("independent_credit_claimed") is True:
        problems.append("NAV_POSTCOMMIT_FALSE_INDEPENDENT_CREDIT")
    return problems


def summarize(handoff: dict, reports: dict[str, tuple[dict, str]]) -> dict:
    cells = handoff.get("cells", [])
    require(len(cells) == 28 and len({r["cell_id"] for r in cells}) == 28,
            "R13_HANDOFF_NOT_EXACTLY_28")
    require(handoff.get("release") == "HOLD" and
            handoff.get("counts", {}).get("qualified_signed_verdicts") == 0 and
            handoff.get("counts", {}).get("owner_acceptances") == 0,
            "R13_FORGED_REVIEW_ACCEPTANCE")
    eligible = [c for c in cells if c["contract_status"] == "VALIDATED_PROPOSAL"]
    source_blocked = [c for c in cells if c["contract_status"] == "BLOCKED_RIVAL_REVIEW"]
    require(len(eligible) == 21 and len(source_blocked) == 7,
            "R13_UNEXPECTED_COVERAGE")
    require(set(reports) == {c["cell_id"] for c in eligible},
            "R13_NATIVE_REPORT_SET_MISMATCH")
    group_counts: Counter[str] = Counter()
    finding_counts: Counter[str] = Counter()
    rows = []
    for cell in sorted(eligible, key=lambda c: c["cell_id"]):
        cid = cell["cell_id"]
        nav, raw_sha = reports[cid]
        proofs = [r for r in cell["available_scoped_browser_proof"]
                  if r.get("name") == "REAL_NATIVE_POSTCOMMIT_SAME_QUESTION_DIAGNOSTIC"]
        require(len(proofs) == 1, "R13_MISSING_OR_DUPLICATE_P5_NATIVE_WITNESS", cid)
        w = proofs[0]
        post = nav.get("postcommit_native_journey", {})
        obs = post.get("observed", {})
        expected_qid = cell["qrt_hypothesis_not_a_verdict"]["primary_question_id"]
        expected_concept = w.get("selected_concept_id")
        require(isinstance(expected_qid, str) and bool(expected_qid.strip()) and
                nav.get("cell_id") == cid and
                post.get("schema") == "imo182-r11-native-postcommit-technical-probe/v1" and
                nav.get("schema") == "imo182-r8-real-native-navigation/v1" and
                post.get("source_question_id") == expected_qid and
                w.get("native_question_id") == expected_qid and
                post.get("selected_concept_id") == expected_concept and
                nav.get("assisted_return", {}).get("target_identity_expected_concept") == expected_concept and
                isinstance(expected_concept, str) and bool(expected_concept),
                "R13_NATIVE_SOURCE_IDENTITY_DRIFT", cid)
        require(w.get("sha256") == raw_sha and
                w.get("native_renderer_only") is True and
                w.get("separate_held_copy_not_authoritative") is True and
                post.get("native_renderer_only") is True and
                post.get("source_bytes_changed") is False,
                "R13_NATIVE_SOURCE_SHA_OR_COPY_DRIFT", cid)
        require(set(obs) == set(CHECKS) | {"independent_credit_claimed"} and
                all(type(v) is bool for v in obs.values()),
                "R13_INVALID_NATIVE_STATUS_FIELDS", cid)
        defects = reported_defects(obs)
        require(post.get("findings") == defects and
                w.get("distinct_technical_findings") == defects and
                type(post.get("technical_round_trip_complete")) is bool and
                post["technical_round_trip_complete"] == (len(defects) == 0) and
                w.get("technical_round_trip_complete") == (len(defects) == 0),
                "R13_FORGED_NATIVE_FINDINGS", cid)
        require(post.get("release") == "HOLD" and
                post.get("human_academic_evidence") is False and
                post.get("meaningful_mathematical_answer_submitted") is False and
                nav.get("owner_acceptance") is False and
                nav.get("qualified_semantic_review") == "NOT_RUN" and
                cell.get("release") == "HOLD" and
                cell["qualified_independent_reviewer"]["decision"] is None and
                cell["owner_separate_disposition"]["decision"] is None and
                w.get("academic_approved") is False and
                w.get("owner_approved") is False,
                "R13_FAKE_REVIEW_OR_RELEASE", cid)
        if obs["independent_credit_claimed"]:
            require(not post["technical_round_trip_complete"],
                    "R13_FALSE_INDEPENDENT_CREDIT", cid)
        groups = [name for name, dependent in REPAIR_GROUPS.items()
                  if any(obs[field] is False for field in dependent)]
        uncovered = [code for field, code in CHECKS.items()
                     if field not in {f for sub in REPAIR_GROUPS.values() for f in sub}
                     and not obs[field]]
        if uncovered or obs["independent_credit_claimed"]:
            groups.append("OTHER_NATIVE_GUARD_OR_FALSE_CREDIT")
        finding_counts.update(defects)
        group_counts.update(groups)
        rows.append({
            "cell_id": cid,
            "question_id": expected_qid,
            "concept_id": expected_concept,
            "native_browser_report_sha256": raw_sha,
            "technical_round_trip_complete": not defects,
            "finding_ids": defects,
            "engineering_repair_workstreams": groups,
            "independent_mastery_claimed": False,
            "academic_approved": False,
            "owner_approved": False,
            "release": "HOLD",
        })
    require(all(c.get("blocking_source_author_action") for c in source_blocked),
            "R13_FORGED_SOURCE_HOLD")
    blocked_rows = [{"cell_id": c["cell_id"],
                     "source_author_action_code": c["blocking_source_author_action"]["code"],
                     "native_browser_status": "NOT_RUN_SOURCE_BLOCKED",
                     "academic_approved": False, "owner_approved": False}
                    for c in sorted(source_blocked, key=lambda c: c["cell_id"])]
    return {
        "schema": "imo182-r13-native-engineering-repair-matrix/v1",
        "basis": "R11 real native Chromium + R12 P5 source/SHA proof",
        "scope": "TRACK_A_28_AUTHORED_TEST_ONLY",
        "counts": {"qrt_cells": 28, "native_source_bound": 21,
                   "source_blocked_no_native_report": 7,
                   "native_round_trips_complete": sum(not r["finding_ids"] for r in rows),
                   "technical_finding_occurrences": sum(finding_counts.values())},
        "engineering_workstream_cell_counts": dict(sorted(group_counts.items())),
        "technical_finding_cell_counts": dict(sorted(finding_counts.items())),
        "native_cells": rows,
        "source_blocked_cells": blocked_rows,
        "independent_academic_approvals": 0,
        "owner_qrt_acceptances": 0,
        "renderer_writer_permission": "NOT_GRANTED_BY_THIS_REPORT",
        "release": "HOLD",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    handoff = json.loads(args.handoff.read_text(encoding="utf-8"))
    reports = {}
    for file in sorted(args.evidence_dir.glob("*-real-navigation.json")):
        body = file.read_bytes()
        record = json.loads(body)
        cid = record["cell_id"]
        require(cid not in reports, "R13_DUPLICATE_NATIVE_REPORT", cid)
        reports[cid] = record, hashlib.sha256(body).hexdigest()
    report = summarize(handoff, reports)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("R13 exact-native repair matrix:", report["counts"],
          report["engineering_workstream_cell_counts"],
          "academic+Owner 0/28, release HOLD")


if __name__ == "__main__":
    main()
