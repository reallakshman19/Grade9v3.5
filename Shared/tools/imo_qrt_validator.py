#!/usr/bin/env python3
"""Read-only, fail-closed PR240 intake validator for Grade9 QRT.

This checks *evidence sufficiency*, never academic correctness or source rights.
Requires the canonical question_difficulty module from the selected repository.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

# Allow both direct script invocation and python -m execution from repository root.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from Shared.tools import question_difficulty
BANK_DIR = ROOT / "Mathematics" / "question-bank"
VISUAL_MANIFEST = ROOT / "Mathematics" / "research" / "visual_cues_manifest.json"
OLD_AUDIT = ROOT / "TEST" / "imo-research" / "audit" / "master_suite_qrt_alignment_audit.v1.json"
BANKS = (
    "sof-imo-2023-24-set-a.core2.json",
    "sof-imo-2024-25-set-b.core2.json",
    "sof-imo-2025-26-set-a.core2.json",
    "sof-imo-2025-26-set-b.core2.json",
    "sof-imo-hots-olympiad-expansion.core2.json",
    "sof-imo-sample-2026-27.core2.json",
)
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")
EXPECTED_TOTAL = 260
VERDICTS = ("PASS", "FAIL", "REVIEW_REQUIRED", "NOT_RUN", "NOT_APPLICABLE", "STALE")
SCHEMA = "imo-qrt-validator-intake/v1"


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def read_json(path: Path) -> tuple[Any, str]:
    raw = path.read_bytes()
    return json.loads(raw), digest(raw)


def check_one(question: dict[str, Any], *, visual_needed: bool = False) -> dict[str, Any]:
    """Do not confuse derived metadata with qualified academic judgement."""
    qid = question.get("id")
    issues: list[dict[str, str]] = []

    def emit(rule: str, verdict: str, evidence: str) -> None:
        issues.append({"rule": rule, "verdict": verdict, "evidence": evidence})

    if not isinstance(qid, str) or not qid:
        emit("V01", "FAIL", "QUESTION_ID_MISSING")
        qid = "<missing>"
    cls = question.get("cognitive_classification")
    cls = cls if isinstance(cls, dict) else {}
    demand, band = cls.get("primary_demand"), cls.get("difficulty_band")
    if demand not in DEMANDS:
        emit("V07", "FAIL", "UNKNOWN_PRIMARY_DEMAND")
    if band not in BANDS:
        emit("V06", "FAIL", "UNKNOWN_DIFFICULTY_BAND")
    cell = f"QRT-{demand}-{band}"
    if cls.get("qrt_cell") != cell or demand not in DEMANDS or band not in BANDS:
        emit("V08", "FAIL", "DECLARED_QRT_CELL_INCONSISTENT")

    # Numerical evidence is not academic acceptance: keep authored and derived fields
    # distinct so a corrupt component cannot be silently clamped/relabelled.
    components = cls.get("difficulty_components")
    stored_score = cls.get("difficulty_score")
    derived_score: int | None = None
    derived_band: str | None = None
    factor_evidence: dict[str, Any] = {
        "component_status": "MISSING" if components is None else "INVALID_TYPE",
        "missing_keys": [], "extra_keys": [], "invalid_components": [],
        "required_keys": list(question_difficulty.COMPONENT_KEYS),
        "stored_score": stored_score, "derived_score": None,
        "score_consistency": "NOT_DERIVABLE",
        "stored_band": band, "derived_band": None,
        "band_consistency": "NOT_DERIVABLE",
        "academic_justification": "REVIEW_REQUIRED",
    }
    if components is None:
        emit("V06", "REVIEW_REQUIRED", "FIVE_FACTOR_EVIDENCE_MISSING")
    elif not isinstance(components, dict):
        emit("V06", "FAIL", "FIVE_FACTOR_STRUCTURE_INVALID")
    else:
        required = set(question_difficulty.COMPONENT_KEYS)
        factor_evidence["missing_keys"] = sorted(required - set(components))
        factor_evidence["extra_keys"] = sorted(set(components) - required)
        if factor_evidence["missing_keys"] or factor_evidence["extra_keys"]:
            factor_evidence["component_status"] = "INVALID_KEYS"
            emit("V06", "FAIL", "FIVE_FACTOR_KEYS_INCOMPLETE_OR_EXTRA")
        else:
            invalid = [key for key in question_difficulty.COMPONENT_KEYS
                       if type(components[key]) is not int or not 0 <= components[key] <= 2]
            if invalid:
                factor_evidence["component_status"] = "INVALID_VALUES"
                factor_evidence["invalid_components"] = [
                    {"key": key, "value": components[key]} for key in invalid
                ]
                emit("V06", "FAIL", "FIVE_FACTOR_VALUE_INVALID")
            else:
                factor_evidence["component_status"] = "COMPLETE"
                derived_score = sum(components[key] for key in question_difficulty.COMPONENT_KEYS)
                derived_band = question_difficulty.band_for_score(derived_score)
                factor_evidence["derived_score"] = derived_score
                factor_evidence["derived_band"] = derived_band
                if type(stored_score) is not int:
                    factor_evidence["score_consistency"] = "INVALID_TYPE"
                    emit("V06", "FAIL", "FIVE_FACTOR_SCORE_TYPE_INVALID")
                elif stored_score != derived_score:
                    factor_evidence["score_consistency"] = "MISMATCH"
                    emit("V06", "FAIL", "FIVE_FACTOR_SCORE_MISMATCH")
                else:
                    factor_evidence["score_consistency"] = "MATCH"
                if band != derived_band:
                    factor_evidence["band_consistency"] = "MISMATCH"
                    emit("V06", "FAIL", "FIVE_FACTOR_BAND_MISMATCH")
                else:
                    factor_evidence["band_consistency"] = "MATCH"
                # Reuse the authoritative derivation, not a second band/scorer.
                # A canonical rejection without a known mismatch must fail closed.
                previous_defects = len(issues)
                try:
                    question_difficulty.derive(
                        {"components": components, "score": stored_score, "band": band},
                        question_ref=qid,
                    )
                except question_difficulty.DifficultyContractError:
                    if len(issues) == previous_defects and (
                        factor_evidence["score_consistency"] == "MATCH"
                        and factor_evidence["band_consistency"] == "MATCH"
                    ):
                        emit("V06", "FAIL", "FIVE_FACTOR_CANONICAL_REJECTION")
                emit("V06", "REVIEW_REQUIRED", "FIVE_FACTOR_ACADEMIC_JUSTIFICATION_UNREVIEWED")

    if not isinstance(cls.get("crux_move"), str) or not cls["crux_move"].strip():
        emit("V09", "FAIL", "RESEARCH_CRUX_MISSING")
    # Research crux prose alone cannot substitute canonical reasoning_route move refs.
    answer = question.get("answer")
    if not isinstance(answer, dict) or answer.get("choice") not in ("A", "B", "C", "D"):
        emit("V04", "FAIL", "ANSWER_CHOICE_INVALID")
    options = question.get("options")
    if not isinstance(options, dict) or set(options) != {"A", "B", "C", "D"} or not all(
        isinstance(x, str) and x.strip() for x in options.values()
    ):
        emit("V04", "FAIL", "FOUR_OPTIONS_MISSING_OR_INVALID")
    if not isinstance(question.get("stem"), str) or not question["stem"].strip():
        emit("V02", "FAIL", "STEM_MISSING")
    if not isinstance(question.get("paper_origin_locator"), dict):
        emit("V02", "REVIEW_REQUIRED", "SOURCE_OCCURRENCE_LOCATOR_MISSING")
    if not isinstance(question.get("solution"), dict) or not isinstance(
        question["solution"].get("derivation"), str
    ) or not question["solution"]["derivation"].strip():
        emit("V05", "FAIL", "DERIVATION_MISSING")
    if visual_needed and not question.get("figure_ref"):
        emit("V13", "REVIEW_REQUIRED", "VISUAL_CUE_WITHOUT_DECLARED_FIGURE")
    if question.get("figure_ref") is not None:
        figure = question["figure_ref"]
        if not isinstance(figure, str) or not figure or not re.fullmatch(
            r"(?:Mathematics/library/figures/)?[A-Za-z0-9_.-]+\.svg", figure
        ):
            emit("V03", "FAIL", "UNSAFE_OR_INVALID_FIGURE_REFERENCE")
        else:
            basename = figure.rsplit("/", 1)[-1]
            root = (ROOT / "Mathematics/library/figures").resolve()
            candidate = root / basename
            if not candidate.is_file() or candidate.resolve().parent != root:
                emit("V03", "REVIEW_REQUIRED", "DECLARED_SVG_ASSET_NOT_VERIFIED")
    # A true solution, justified demand and protected W require source & academic examination.
    emit("V04", "REVIEW_REQUIRED", "ANSWER_NOT_INDEPENDENTLY_SOLVED")
    emit("V07", "REVIEW_REQUIRED", "PRIMARY_DEMAND_SEMANTIC_UNREVIEWED")
    emit("V10", "REVIEW_REQUIRED", "PROTECTED_WORK_W_UNREVIEWED")
    emit("V19", "REVIEW_REQUIRED", "QUESTION_TO_SHARED_CORE_GRAPH_UNREVIEWED")
    emit("V28", "REVIEW_REQUIRED", "INDEPENDENT_QRT_ACCEPTANCE_NOT_PROVIDED")
    # The source-bank format is research; no unfounded native admission assertion.
    return {
        "id": qid,
        "declared_tile": cell,
        "derived_band": derived_band,
        "derived_score": derived_score,
        "difficulty_evidence": factor_evidence,
        "figure_declared": bool(question.get("figure_ref")),
        "findings": issues,
        "academic_verdict": "REVIEW_REQUIRED",
        "native_core_admission": "NOT_VERIFIED",
    }


def validate_bank_dir(bank_dir: Path = BANK_DIR, *, visual_manifest: Path = VISUAL_MANIFEST,
                      legacy_audit: Path = OLD_AUDIT, expected_total: int = EXPECTED_TOTAL,
                      baseline_sha: str | None = None) -> dict[str, Any]:
    if not isinstance(baseline_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline_sha):
        raise ValueError("EXACT_40_CHARACTER_SOURCE_COMMIT_REQUIRED")
    visual_ids: set[str] = set()
    inputs: list[dict[str, Any]] = []
    if visual_manifest.is_file():
        v, vsha = read_json(visual_manifest)
        visual_ids = {x.get("target_id") for x in v.get("core2_cues", []) if isinstance(x, dict) and x.get("target_id")}
        inputs.append({"path": str(visual_manifest), "sha256": vsha, "kind": "VISUAL_CUE"})
    records: list[dict[str, Any]] = []
    all_ids: list[str] = []
    bank_missing: list[str] = []
    for name in BANKS:
        path = bank_dir / name
        if not path.is_file():
            bank_missing.append(name)
            continue
        data, h = read_json(path)
        questions = data.get("questions") if isinstance(data, dict) else None
        if not isinstance(questions, list):
            raise ValueError("INVALID_QUESTIONS_ARRAY: " + name)
        inputs.append({"path": str(path), "sha256": h, "kind": "RESEARCH_BANK", "count": len(questions)})
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                raise ValueError(f"QUESTION_NOT_OBJECT: {name}:{i}")
            record = check_one(q, visual_needed=q.get("id") in visual_ids)
            record["source_file"] = name
            record["source_array_index"] = i
            records.append(record)
            all_ids.append(record["id"])

    total, unique = len(records), len(set(all_ids))
    counts = Counter(all_ids)
    duplicates = sorted(qid for qid, count in counts.items() if count > 1)
    tiles: dict[str, list[str]] = {f"QRT-{d}-{b}": [] for b in BANDS for d in DEMANDS}
    for record in records:
        if record["declared_tile"] in tiles:
            tiles[record["declared_tile"]].append(record["id"])
    stale_audits = []
    if legacy_audit.is_file():
        audit, h = read_json(legacy_audit)
        count = audit.get("total_questions_audited")
        if count != total:
            stale_audits.append({"path": str(legacy_audit), "sha256": h,
                                 "reported_question_count": count, "actual_question_count": total,
                                 "verdict": "STALE"})
    difficulty_summary = {
        "components": dict(sorted(Counter(
            r["difficulty_evidence"]["component_status"] for r in records
        ).items())),
        "scores": dict(sorted(Counter(
            r["difficulty_evidence"]["score_consistency"] for r in records
        ).items())),
        "bands": dict(sorted(Counter(
            r["difficulty_evidence"]["band_consistency"] for r in records
        ).items())),
    }
    findings = Counter(f["evidence"] for row in records for f in row["findings"])
    critical = Counter(f["evidence"] for row in records for f in row["findings"] if f["verdict"] == "FAIL")
    status = "FAIL" if bank_missing or duplicates or total != expected_total or critical or stale_audits else "REVIEW_REQUIRED"
    return {
        "schema": SCHEMA, "baseline_commit": baseline_sha,
        "scope": "RESEARCH_INTAKE_ONLY", "academic_approval": "NOT_GRANTED",
        "source_rights": "UNVERIFIED", "status": status, "expected_total": expected_total,
        "actual_total": total, "unique_ids": unique, "missing_banks": bank_missing,
        "duplicate_ids": duplicates, "occupied_tiles": sum(bool(v) for v in tiles.values()),
        "tiles": {k: {"count": len(ids), "question_ids": ids} for k, ids in tiles.items()},
        "finding_counts": dict(sorted(findings.items())), "fail_counts": dict(sorted(critical.items())),
        "stale_audits": stale_audits, "difficulty_evidence_summary": difficulty_summary,
        "inputs": inputs, "questions": records,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bank-dir", type=Path, default=BANK_DIR)
    p.add_argument("--visual-manifest", type=Path, default=VISUAL_MANIFEST)
    p.add_argument("--legacy-audit", type=Path, default=OLD_AUDIT)
    p.add_argument("--baseline-sha", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    result = validate_bank_dir(args.bank_dir, visual_manifest=args.visual_manifest,
                               legacy_audit=args.legacy_audit, baseline_sha=args.baseline_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "schema", "baseline_commit", "status", "actual_total", "unique_ids", "occupied_tiles",
        "finding_counts", "fail_counts", "stale_audits")}, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
