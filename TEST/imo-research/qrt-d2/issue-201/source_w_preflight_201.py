"""Issue #201: narrow, UNSIGNED preflight for source/learner-work contradictions.

Heuristics are warning-only; no cognitive-demand adjudication, QRT acceptance,
math proof, reviewer identity, Owner signature or release decision is emitted.
This is not a general semantic lint or a replacement for actual page review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
SOURCES = ROOT / "TEST/imo-research/qrt-d2"
DEMANDS = ("retrieve", "explain", "apply", "model", "represent", "synthesize", "justify")


def assessed_question(package: dict, demand: str) -> dict:
    """CORE2A exposure determines the assessed question, not an ID suffix."""
    matches = [q for q in package.get("questions", [])
               if any(e.get("core") == "CORE2A" for e in q.get("exposure", []))]
    if len(matches) != 1:
        raise ValueError(f"{demand}: expected exactly one CORE2A assessed question, found {len(matches)}")
    question = matches[0]
    if question.get("origin") != "AUTHORED":
        raise ValueError(f"{demand}: only authored TEST question permitted")
    return question


def check_question(question: dict, demand: str, claimed_w: str | None = None) -> list[dict]:
    """A positive heuristic is a question for humans, never a semantic verdict."""
    stem = question.get("stem", "")
    difficulty = question.get("difficulty", {})
    evidence = difficulty.get("component_evidence", {}).get("concept_model_selection", "")
    rationale = " ".join((difficulty.get("basis", ""), evidence, claimed_w or ""))
    findings: list[dict] = []

    # A named variable *category* is given, but the author credits deciding it.
    # A prompt that only says 'choose a variable' is not this contradiction.
    named_role = re.search(
        r"\b(?:choose|select|use|define|set)\s+(?:a|the|one)\s+variable\s+for\s+"
        r"(?:the\s+)?(?P<category>[A-Za-z][A-Za-z-]*(?:\s+[A-Za-z-]+){0,2})\s+count\b",
        stem, flags=re.IGNORECASE,
    )
    claims_choice = re.search(r"\b(?:select|choose|decide)\b[^.]{0,85}\b(?:variable|category|type|count)\b",
                              rationale, re.IGNORECASE)
    if demand == "model" and named_role and claims_choice:
        findings.append({
            "id": "QRT201-W-PRESELECTED-VARIABLE-CATEGORY",
            "severity": "REVIEW_REQUIRED_NOT_AUTOMATED_REJECTION",
            "evidence_fields": ["question.stem", "question.difficulty.component_evidence.concept_model_selection"],
            "stem_excerpt": named_role.group(0),
            "rationale_excerpt": evidence,
            "question_for_reviewer": (
                "Stem already selects a count category but difficulty rationale credits that selection. "
                "Is complement + weighted revenue formulation a sufficient learner-owned MODEL-D2 W, "
                "or does the item need a consistent revision/reclassification?"
            ),
        })

    # A prompt can use the word 'retrieve' while chiefly assessing APPLY.
    relation_given = re.search(r"\b(?:right[- ]triangle(?:\s+distance)?\s+relation|Pythagor(?:as|ean)(?:\s+relation|\s+theorem)?)\b",
                               stem, re.IGNORECASE)
    calculate_directive = re.search(r"\bcalculat(?:e|ing)\b", stem, re.IGNORECASE)
    if demand == "retrieve" and relation_given and calculate_directive:
        findings.append({
            "id": "QRT201-DEMAND-RETRIEVE-VS-APPLY",
            "severity": "REVIEW_REQUIRED_NOT_AUTOMATED_RECLASSIFICATION",
            "evidence_fields": ["question.stem", "question.extensions.grade9v3:cognitive_demand.primary"],
            "stem_excerpt": relation_given.group(0) + " … " + calculate_directive.group(0),
            "question_for_reviewer": (
                "Stem names the relation and directs calculation. Does independent fact retrieval "
                "decide success, or does executing the relation and comparing routes make APPLY primary?"
            ),
        })
    return findings


def build_report(source_dir: Path = SOURCES, ledger_path: Path | None = None) -> dict:
    if ledger_path is None:
        ledger_path = source_dir / "issue-201/evidence.v1.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    rows = ledger.get("rows", [])
    by_demand = {row.get("demand", "").lower(): row for row in rows}
    if len(rows) != len(DEMANDS) or set(by_demand) != set(DEMANDS):
        raise ValueError("expected exactly seven canonical D2 evidence rows")
    report_rows = []
    for demand in DEMANDS:
        path = source_dir / f"{demand}.v1.json"
        package = json.loads(path.read_text(encoding="utf-8"))
        question = assessed_question(package, demand)
        row = by_demand[demand]
        if row.get("band") != "D2":
            raise ValueError(f"{demand}: not D2 in canonical ledger")
        # The ledger's planned classification is author-side; do not promote it.
        declared_demand = question.get("extensions", {}).get("grade9v3:cognitive_demand", {}).get("primary")
        if declared_demand != demand.upper():
            raise ValueError(f"{demand}: source/ledger declared demand mismatch")
        findings = check_question(question, demand, row.get("protected_w"))
        report_rows.append({
            "candidate": f"QRT-{demand.upper()}-D2", "source_path": f"TEST/imo-research/qrt-d2/{demand}.v1.json",
            "question_id": question["id"], "declared_primary": declared_demand,
            "preflight_status": "REVIEW_FLAGS_PRESENT" if findings else "NO_TARGETED_RULE_TRIGGERED_NOT_CLEARED",
            "warnings": findings,
            "qualified_academic_review": "PENDING_INDEPENDENT",
            "owner_cell_decision": "PENDING",
        })
    return {
        "schema": "qrt201-source-w-warning-preflight/v1",
        "authority": "AUTHOR_SIDE_HEURISTIC_ONLY_NOT_QRT_REVIEW",
        "warning_policy": "Warnings do not fail CI or reclassify questions; structural/source errors do fail.",
        "coverage": "TWO_TARGETED_HEURISTICS_ONLY; ALL_SEVEN_CANDIDATES_ENUMERATED",
        "accepted_qrt_cells": "NOT_MODIFIED_OR_DECIDED",
        "rows": report_rows,
        "warning_count": sum(len(row["warnings"]) for row in report_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write warning-only JSON artifact here")
    args = parser.parse_args()
    report = build_report()
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(f"SOURCE_W_PREFLIGHT_COMPLETE: {len(report['rows'])} candidates; "
          f"{report['warning_count']} unsigned review flags; NO ACADEMIC/OWNER VERDICT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
