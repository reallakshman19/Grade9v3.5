#!/usr/bin/env python3
"""Read-only, source-pinned HOTS Q024/Q035 evidence screen.

This is a HOLD detector, not a geometric proof evaluator or QRT relabeller.
The research bank is not authentic-source or native Core admission.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BANK = Path("Mathematics/question-bank/sof-imo-hots-olympiad-expansion.core2.json")
TARGETS = ("SOF-IMO-G09-HOTS-OLYMPIAD-Q024", "SOF-IMO-G09-HOTS-OLYMPIAD-Q035")
SCHEMA = "imo-qrt-hots-review-evidence/v1"


def inspect(questions: list[dict[str, Any]], *, source_sha256: str,
            source_commit: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("EXACT_SOURCE_COMMIT_REQUIRED")
    if not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
        raise ValueError("EXACT_SOURCE_BLOB_DIGEST_REQUIRED")
    index: dict[str, dict[str, Any]] = {}
    for item in questions:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("QUESTION_ID_MISSING_OR_INVALID")
        if item["id"] in index:
            raise ValueError("DUPLICATE_QUESTION_ID:" + item["id"])
        index[item["id"]] = item

    cases = []
    for qid in TARGETS:
        q = index.get(qid)
        if q is None:
            cases.append({"id": qid, "status": "FAIL", "findings": [
                {"code": "HOTS_TARGET_QUESTION_MISSING", "verdict": "FAIL"}]})
            continue
        cls = q.get("cognitive_classification")
        cls = cls if isinstance(cls, dict) else {}
        demand, band = cls.get("primary_demand"), cls.get("difficulty_band")
        cell = cls.get("qrt_cell")
        solution = q.get("solution")
        derivation = (solution.get("derivation") if isinstance(solution, dict) else None)
        stem = q.get("stem")
        if not isinstance(stem, str):
            stem = ""
        if not isinstance(derivation, str):
            derivation = ""
        findings: list[dict[str, str]] = []

        def flag(code: str, verdict: str = "REVIEW_REQUIRED") -> None:
            findings.append({"code": code, "verdict": verdict})

        if not stem.strip() or not derivation.strip():
            flag("HOTS_STEM_OR_REASONING_MISSING", "FAIL")
        if cell != f"QRT-{demand}-{band}" or demand not in (
            "RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"
        ) or band not in ("D1", "D2", "D3", "D4"):
            flag("HOTS_DECLARED_QRT_INCONSISTENT", "FAIL")

        if qid.endswith("Q024"):
            broad_claim = bool(re.search(r"\b(any general|any arbitrary|all five.pointed stars)\b", stem.lower()))
            bounded_warrant = (
                "nondegenerate" in derivation.lower()
                and "convex" in derivation.lower()
            )
            figure_available = isinstance(q.get("figure_ref"), str) and bool(q["figure_ref"].strip())
            flag("Q024_ORIGINAL_SOURCE_DIAGRAM_AND_SCOPE_UNVERIFIED")
            flag("Q024_GEOMETRY_ARGUMENT_REQUIRES_QUALIFIED_REVIEW")
            if broad_claim and bounded_warrant:
                flag("Q024_BROAD_STEM_VS_BOUNDED_WARRANT")
            if not bounded_warrant:
                flag("Q024_PROOF_DOMAIN_QUALIFICATION_NOT_EVIDENCED")
            if not figure_available:
                flag("Q024_SOURCE_FIGURE_NOT_DECLARED")
            evidence = {
                "broad_claim_in_stem": broad_claim,
                "bounded_warrant_declared": bounded_warrant,
                "figure_reference_declared": figure_available,
                "authoritative_source_diagram_verified": False,
                "independent_geometry_proof_accepted": False,
                "declared_demand": demand, "declared_band": band, "declared_cell": cell,
                "classification_rewritten": False,
            }
        else:
            crux = cls.get("crux_move")
            crux = crux if isinstance(crux, str) else ""
            direct_apply_cue = bool(re.search(r"\bapply\s+ptolemy", crux.lower()))
            factors = cls.get("difficulty_components")
            factor_complete = isinstance(factors, dict) and len(factors) == 5
            flag("Q035_PRIMARY_LEARNER_ACTION_NOT_ADJUDICATED")
            flag("Q035_DIFFICULTY_FACTOR_JUSTIFICATION_UNREVIEWED")
            if direct_apply_cue and demand == "SYNTHESIZE":
                flag("Q035_APPLY_LANGUAGE_VS_SYNTHESIZE_PROPOSAL")
            if not factor_complete:
                flag("Q035_FIVE_FACTOR_EVIDENCE_MISSING")
            if (demand, band, cell) != ("SYNTHESIZE", "D4", "QRT-SYNTHESIZE-D4"):
                flag("Q035_CHANGED_CLASSIFICATION_NEEDS_CITED_ACCEPTANCE")
            evidence = {
                "direct_ptolemy_application_cue": direct_apply_cue,
                "five_factor_object_complete": factor_complete,
                "declared_demand": demand, "declared_band": band, "declared_cell": cell,
                "classification_rewritten": False,
                "independent_learner_demand_accepted": False,
            }
        cases.append({
            "id": qid,
            "status": "FAIL" if any(f["verdict"] == "FAIL" for f in findings)
                      else "REVIEW_REQUIRED",
            "evidence": evidence,
            "findings": findings,
            "academic_verdict": "REVIEW_REQUIRED",
            "source_rights": "NOT_VERIFIED",
            "native_core_admission": "NOT_GRANTED",
        })
    return {
        "schema": SCHEMA, "source_commit": source_commit,
        "source_path": str(BANK), "source_sha256": source_sha256,
        "scope": "RESEARCH_ACADEMIC_HOLD_TRIAGE_ONLY",
        "status": "FAIL" if any(c["status"] == "FAIL" for c in cases) else "REVIEW_REQUIRED",
        "cases": cases,
        "academic_approval": "NOT_GRANTED",
        "qrt_classification_acceptance": "NOT_GRANTED",
        "source_rights": "NOT_VERIFIED",
    }


def audit(*, root: Path = ROOT, source_commit: str) -> dict[str, Any]:
    raw = (root / BANK).read_bytes()
    data = json.loads(raw)
    rows = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError("HOTS_QUESTIONS_LIST_REQUIRED")
    return inspect(rows, source_sha256=sha256(raw).hexdigest(), source_commit=source_commit)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    result = audit(root=args.root, source_commit=args.source_commit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "schema", "source_commit", "source_sha256", "status", "cases",
        "academic_approval", "qrt_classification_acceptance",
    )}, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
