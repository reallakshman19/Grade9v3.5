#!/usr/bin/env python3
"""#182 P4 exhaustive coverage *inventory*, not a 28-cell semantic acceptance.

Requires exact 28 authoritative authored TEST rows. A missing source-specific W
witness is PENDING_UNASSESSED, never a fabricated QRT contract. The previously
verified structural artifacts remain separate from qualified educational review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qrt_intent_contract import ensure, sha256, DEMANDS, BANDS

STATUS = (
    "CONTRACT_VALIDATED_REVIEW_REQUIRED",
    "BLOCKED_AUTHOR_RIVAL_DECLARATION",
    "SOURCE_SPECIFIC_CONTRACT_NOT_RUN",
)


def coverage(ledger: dict, bank: dict, evidence_dir: Path) -> dict:
    rows = ledger.get("rows", [])
    ids = {f"QRT-{d}-{b}" for d in DEMANDS for b in BANDS}
    ensure(len(rows) == 28 and {r["cell_id"] for r in rows} == ids,
           "P4_MATRIX_NOT_EXHAUSTIVE")
    witnesses = bank.get("witnesses", [])
    witnesses_by_cell = {w["cell_id"]: w for w in witnesses}
    ensure(len(witnesses) == len(witnesses_by_cell) and
           set(witnesses_by_cell).issubset(ids),
           "P4_WITNESS_DUPLICATE_OR_UNKNOWN")
    reports = {}
    for f in evidence_dir.glob("*.json"):
        if f.stem.endswith("-native") or f.stem.endswith("-w-audit"):
            continue
        obj = json.loads(f.read_text(encoding="utf-8"))
        if obj.get("cell_id") in ids:
            ensure(obj["cell_id"] not in reports,
                   "P4_DUPLICATE_REPORT")
            reports[obj["cell_id"]] = (f, obj)
    ensure(set(reports) == set(witnesses_by_cell),
           "P4_MISSING_OR_ORPHAN_CONTRACT",
           str(sorted(set(witnesses_by_cell) ^ set(reports))))
    entries = []
    for row in rows:
        cid = row["cell_id"]
        blocked = row["critical_educational_review_hold"]
        w = witnesses_by_cell.get(cid)
        status = "SOURCE_SPECIFIC_CONTRACT_NOT_RUN"
        contract_sha = None
        reviewer_code = None
        native = "NOT_RUN"
        browser = "NOT_RUN"
        if w:
            path, report = reports[cid]
            contract_sha = sha256(path)
            ensure(report.get("owner_qrt_acceptance") == "PENDING" and
                   report.get("qualified_academic_review") == "PENDING" and
                   report.get("semantic_review") == "HOLD_REVIEW_REQUIRED",
                   "P4_NO_ACADEMIC_PROMOTION", cid)
            if report["technical_contract"] == "VALIDATED_PROPOSAL":
                status = STATUS[0]
                nat = evidence_dir / (path.stem + "-native.json")
                ensure(nat.is_file(), "P4_NATIVE_WITNESS_MISSING", cid)
                n = json.loads(nat.read_text(encoding="utf-8"))
                ensure(n.get("native_evidence", {}).get(
                    "all_role_structure") == "PASS" and
                    all(x["semantic"] == "NOT_RUN" for x in
                        n["roles"].values()), "P4_NATIVE_SEMANTIC_PROMOTION", cid)
                native = "FIVE_REAL_NATIVE_ROLES_SHA_AND_GOLDEN_MATCH"
                audit = evidence_dir / (path.stem + "-w-audit.json")
                if audit.is_file():
                    a = json.loads(audit.read_text(encoding="utf-8"))
                    ensure(a["owner_qrt_acceptance"] == "PENDING",
                           "P4_BROWSER_OWNER_PROMOTION", cid)
                    browser = "SCOPED_PATH_W_AUDIT_HUMAN_REVIEW_REQUIRED"
            else:
                ensure(report["technical_contract"] == "BLOCKED_RIVAL_REVIEW" and
                       report.get("blocking_error_code") ==
                       "RIVAL_NOT_GROUNDED_IN_SOURCE",
                       "P4_UNEXPECTED_RIVAL_BLOCK", cid)
                status = STATUS[1]
                reviewer_code = report["blocking_error_code"]
        entries.append({
            "cell_id": cid,
            "primary_demand": row["demand"],
            "band": row["band"],
            "elevated_educational_hold": blocked,
            "evidence": {
                "source_commit_in_ledger": row["source"]["commit"],
                "authored_test_source": row["source"]["path"],
                "source_git_blob_sha_in_ledger":
                    row["source"]["git_blob_sha"],
                "manifest_git_blob_sha_in_ledger":
                    row["manifest"]["git_blob_sha"],
                "technical_source_ledger_status":
                    row["technical_adoption_status"],
                "qrt_contract_status": status,
                "qrt_contract_sha256": contract_sha,
                "blocking_reason_code": reviewer_code,
                "new_native_evidence": native,
                "new_browser_w_evidence": browser,
            },
            "independent_reviewer_nomination_issue":
                row["independent_reviewer_nomination_issue"],
            "qualified_reviewer": "PENDING",
            "owner_qrt_acceptance": False,
            "new_golden_designation": False,
            "release": "HOLD",
        })
    counts = {s: sum(x["evidence"]["qrt_contract_status"] == s
                      for x in entries) for s in STATUS}
    holds = [x for x in entries if x["elevated_educational_hold"]]
    ensure(len(holds) == 8 and
           sum(x["evidence"]["qrt_contract_status"] != STATUS[2]
               for x in holds) == 8,
           "P4_EIGHT_ELEVATED_HOLDS_MISSING")
    ensure(counts[STATUS[0]] == 7 and
           counts[STATUS[1]] == 2 and
           counts[STATUS[2]] == 19,
           "P4_UNEXPECTED_COVERAGE_COUNTS", repr(counts))
    return {
        "schema": "imo182-qrt-intent-exhaustive-coverage/v1",
        "scope": "28_AUTHORED_TEST_CELLS_NOT_68_PUBLISHER_ORIGINALS",
        "contract_validated_proposals": counts[STATUS[0]],
        "explicit_rival_declaration_holds": counts[STATUS[1]],
        "not_yet_question_specific_contract_tested": counts[STATUS[2]],
        "source_manifest_artifact_reconciliation":
            "EXISTING_LEDGER_EVIDENCE_NOT_NEW_QRT_REVIEW",
        "new_native_role_structural_witnesses": 5 * counts[STATUS[0]],
        "qualified_academic_signatures": 0,
        "owner_accepted_cells": 0,
        "release": "HOLD",
        "cells": entries,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--witness-bank", type=Path, required=True)
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    report = coverage(
        json.loads(args.ledger.read_text(encoding="utf-8")),
        json.loads(args.witness_bank.read_text(encoding="utf-8")),
        args.evidence_dir
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("P4 exhaustive 28 authored TEST cell accounting: 7 validated proposed "
          "with 35 native role structural witnesses; 2 explicit rival metadata "
          "HOLD; 19 not source-specifically compiled; 0 academic/Owner acceptance")


if __name__ == "__main__":
    main()
