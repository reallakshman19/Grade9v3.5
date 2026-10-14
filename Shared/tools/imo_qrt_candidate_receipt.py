#!/usr/bin/env python3
"""Read-only independent source-fidelity and rendered HTML receipt for repair candidate.

Does not execute candidate code, change source files, bless QRT, or merge anything.
Uses the exact source PR base SHA and pinned candidate worktree to prevent stale data.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from Shared.tools.imo_qrt_validator import BANKS
from Shared.tools.imo_qrt_standalone_gate import inspect_endpoints

SCHEMA = "imo-qrt-independent-candidate-receipt/v1"
SOURCE_FIELDS = ("id", "paper_origin_locator", "stem", "options", "answer", "figure_ref")
REVISION_FIELDS = ("hint_ladder", "solution", "distractor_rationale", "cognitive_classification", "difficulty")


def _git(repo: Path, *args: str) -> bytes:
    out = subprocess.run(["git", "-C", str(repo), *args],
                         check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out.stdout


def _read_bank(blob: bytes, *, label: str) -> dict[str, dict[str, Any]]:
    payload = json.loads(blob)
    if not isinstance(payload, dict) or not isinstance(payload.get("questions"), list):
        raise ValueError("INVALID_BANK_SCHEMA:" + label)
    out: dict[str, dict[str, Any]] = {}
    for q in payload["questions"]:
        if not isinstance(q, dict) or not isinstance(q.get("id"), str) or not q["id"]:
            raise ValueError("MISSING_QUESTION_ID:" + label)
        if q["id"] in out:
            raise ValueError("DUPLICATE_QUESTION_ID:" + q["id"])
        out[q["id"]] = q
    return out


def compare_source(base: dict[str, dict[str, Any]],
                   changed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Pure testable source-faithfulness predicate (not mathematical validation)."""
    b, c = set(base), set(changed)
    removed, added = sorted(b - c), sorted(c - b)
    drifts = []
    authored_updates = []
    for qid in sorted(b & c):
        for field in SOURCE_FIELDS:
            if base[qid].get(field) != changed[qid].get(field):
                drifts.append({"id": qid, "field": field,
                               "rule": "SOURCE_CUSTODY_CHANGE_REQUIRES_OWNER_AUTHORITY"})
        changed_fields = [key for key in REVISION_FIELDS
                          if base[qid].get(key) != changed[qid].get(key)]
        if changed_fields:
            authored_updates.append({"id": qid, "fields": changed_fields,
                                      "academic_review": "REVIEW_REQUIRED"})
    return {"base_question_count": len(base), "candidate_question_count": len(changed),
            "removed_ids": removed, "added_ids": added,
            "source_custody_drifts": drifts,
            "authored_changes": authored_updates,
            "status": "FAIL" if removed or added or drifts else "SOURCE_CUSTODY_PRESERVED"}


def inspect_candidate(*, candidate_root: Path, baseline_sha: str,
                      candidate_sha: str) -> dict[str, Any]:
    sha_pat = re.compile(r"^[0-9a-f]{40}$")
    if not sha_pat.fullmatch(baseline_sha) or not sha_pat.fullmatch(candidate_sha):
        raise ValueError("EXACT_40_CHARACTER_GIT_SHAS_REQUIRED")
    actual_sha = _git(candidate_root, "rev-parse", "HEAD").decode("ascii").strip()
    if actual_sha != candidate_sha:
        raise ValueError("CANDIDATE_EXACT_HEAD_MISMATCH")
    try:
        merge_base = _git(candidate_root, "merge-base", "--is-ancestor", baseline_sha, candidate_sha)
    except subprocess.CalledProcessError as exc:
        raise ValueError("BASELINE_NOT_ANCESTOR_OF_CANDIDATE") from exc

    bank_reports = []
    all_base: dict[str, dict[str, Any]] = {}
    all_new: dict[str, dict[str, Any]] = {}
    bank_dir = Path("Mathematics/question-bank")
    for name in BANKS:
        path = bank_dir / name
        before_raw = _git(candidate_root, "show", baseline_sha + ":" + path.as_posix())
        now_raw = (candidate_root / path).read_bytes()
        old = _read_bank(before_raw, label="base:" + name)
        new = _read_bank(now_raw, label="candidate:" + name)
        if set(all_base) & set(old) or set(all_new) & set(new):
            raise ValueError("DUPLICATE_ID_ACROSS_BANKS:" + name)
        all_base.update(old)
        all_new.update(new)
        bank_reports.append({"path": path.as_posix(), "base_sha256": sha256(before_raw).hexdigest(),
                             "candidate_sha256": sha256(now_raw).hexdigest(),
                             "source_count": len(old), "candidate_count": len(new)})
    source = compare_source(all_base, all_new)
    html = inspect_endpoints(candidate_root, baseline_sha=candidate_sha, expected_questions=260)

    blockers = []
    if source["status"] == "FAIL" or source["base_question_count"] != 260 or source["candidate_question_count"] != 260:
        blockers.append("SOURCE_IDENTITY_OR_CUSTODY_DRIFT")
    if html["hard_findings"] or html["status"] != "REVIEW_REQUIRED":
        blockers.append("RENDERED_HTML_STRUCTURAL_OR_DISCLOSURE_FAILURE")
    if html["rendered"] and (html["rendered"]["question_count"] != 260 or
                             html["rendered"]["unique_question_ids"] != 260):
        blockers.append("RENDERED_DENOMINATOR_MISMATCH")
    return {
        "schema": SCHEMA, "baseline_sha": baseline_sha, "candidate_sha": candidate_sha,
        "status": "FAIL" if blockers else "STRUCTURAL_CANDIDATE_REVIEW_REQUIRED",
        "blockers": blockers, "scope": "RESEARCH_STANDALONE_ONLY",
        "source_custody": source, "banks": bank_reports, "html": html,
        "academic_verdict": "REVIEW_REQUIRED", "qrt_cell_acceptance": "NOT_GRANTED",
        "native_core_admission": "NOT_GRANTED", "source_rights": "NOT_VERIFIED",
        "chromium_user_flow": "NOT_RUN",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-root", type=Path, required=True)
    p.add_argument("--baseline-sha", required=True)
    p.add_argument("--candidate-sha", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    result = inspect_candidate(candidate_root=args.candidate_root,
                               baseline_sha=args.baseline_sha,
                               candidate_sha=args.candidate_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_sha": result["candidate_sha"], "status": result["status"],
        "blockers": result["blockers"], "source_counts": [
            result["source_custody"]["base_question_count"],
            result["source_custody"]["candidate_question_count"]],
        "source_drifts": result["source_custody"]["source_custody_drifts"],
        "authored_changes": result["source_custody"]["authored_changes"],
        "html_status": result["html"]["status"],
        "html_findings": (result["html"]["rendered"] or {}).get("findings", {}),
        "endpoints": result["html"]["endpoints"], "academic_verdict": result["academic_verdict"],
    }, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
