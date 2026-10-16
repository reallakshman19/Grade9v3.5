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
import subprocess
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
VERDICTS = ("PASS", "FAIL", "REVIEW_REQUIRED", "NOT_RUN", "NOT_APPLICABLE", "STALE", "ERROR")
SCHEMA = "imo-qrt-validator-intake/v1"
FINDINGS_SCHEMA = "imo-qrt-question-findings/v1"


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
            locator = q.get("paper_origin_locator")
            record["source_question_number"] = locator.get("question_number") if isinstance(locator, dict) else None
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



def _git_bytes(root: Path, *args: str) -> bytes:
    """Read-only Git object lookup; error is not evidence of a passed check."""
    call = subprocess.run(
        ["git", "-C", str(root), *args], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if call.returncode:
        raise ValueError("GIT_IDENTITY_UNVERIFIED: " + " ".join(args))
    return call.stdout


def verify_source_commit(repo_root: Path, source_sha: str) -> None:
    """Reject a well-formed but false source commit before creating findings."""
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise ValueError("EXACT_40_CHARACTER_SOURCE_COMMIT_REQUIRED")
    actual = _git_bytes(repo_root, "rev-parse", "HEAD").decode("ascii").strip()
    if actual != source_sha:
        raise ValueError("SOURCE_COMMIT_NOT_PINNED: expected=" + source_sha + " actual=" + actual)
    if _git_bytes(repo_root, "cat-file", "-t", source_sha).strip() != b"commit":
        raise ValueError("SOURCE_NOT_A_GIT_COMMIT")


def _verified_git_file(repo_root: Path, commit: str, relative: str) -> dict[str, str]:
    """Prove working bytes exactly equal the designated commit's Git blob."""
    if relative.startswith("/") or ".." in Path(relative).parts:
        raise ValueError("UNSAFE_PROVENANCE_PATH")
    target = (repo_root / relative).resolve()
    if not target.is_relative_to(repo_root.resolve()) or not target.is_file():
        raise ValueError("BOUND_FILE_MISSING_OR_UNSAFE: " + relative)
    git_bytes = _git_bytes(repo_root, "show", commit + ":" + relative)
    actual = target.read_bytes()
    if actual != git_bytes:
        raise ValueError("GIT_BLOB_CONTENT_MISMATCH: " + relative)
    blob = _git_bytes(repo_root, "rev-parse", commit + ":" + relative).decode("ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", blob):
        raise ValueError("GIT_BLOB_ID_INVALID")
    return {"path": relative, "git_blob_sha": blob, "sha256": digest(actual)}


def build_question_findings(report: dict[str, Any], *, repo_root: Path,
                            source_sha: str, validator_sha: str) -> dict[str, Any]:
    """Additive, Git-bound evidence view. Never upgrades academic status."""
    repo_root = repo_root.resolve()
    verify_source_commit(repo_root, source_sha)
    if not isinstance(validator_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", validator_sha):
        raise ValueError("EXACT_40_CHARACTER_VALIDATOR_COMMIT_REQUIRED")
    if _git_bytes(repo_root, "cat-file", "-t", validator_sha).strip() != b"commit":
        raise ValueError("VALIDATOR_NOT_A_GIT_COMMIT")
    if report.get("baseline_commit") != source_sha:
        raise ValueError("INTAKE_SOURCE_COMMIT_DISAGREES")
    if (report.get("actual_total"), report.get("unique_ids"), report.get("expected_total")) != (
        EXPECTED_TOTAL, EXPECTED_TOTAL, EXPECTED_TOTAL,
    ):
        raise ValueError("SOURCE_260_DENOMINATOR_MISMATCH")
    if len(report.get("questions", [])) != EXPECTED_TOTAL or len(report.get("tiles", {})) != 28:
        raise ValueError("SOURCE_OCCURRENCES_OR_QRT_BOARD_INCOMPLETE")
    source_files = []
    bank_dir = repo_root / "Mathematics" / "question-bank"
    for name in BANKS:
        rel = "Mathematics/question-bank/" + name
        proof = _verified_git_file(repo_root, source_sha, rel)
        inputs = [x for x in report.get("inputs", [])
                  if x.get("kind") == "RESEARCH_BANK" and Path(x.get("path", "")).resolve() == (bank_dir / name).resolve()]
        if len(inputs) != 1 or inputs[0].get("sha256") != proof["sha256"]:
            raise ValueError("INTAKE_BANK_PROVENANCE_MISMATCH: " + name)
        proof["question_count"] = inputs[0]["count"]
        source_files.append(proof)
    validator_paths = (
        "Shared/tools/imo_qrt_validator.py",
        "tests/test_imo_qrt_validator.py",
        "tests/test_imo_qrt_findings_contract.py",
        "TEST/imo-qrt-validator/question-findings.v1.schema.json",
    )
    validator_files = [
        _verified_git_file(repo_root, validator_sha, path) for path in validator_paths
    ]
    by_bank = {item["path"].rsplit("/", 1)[-1]: item for item in source_files}
    questions = []
    for row in report["questions"]:
        src = row["source_file"]
        bank = by_bank.get(src)
        if bank is None:
            raise ValueError("QUESTION_SOURCE_BANK_UNKNOWN")
        index = row["source_array_index"]
        if type(index) is not int or not 0 <= index < bank["question_count"]:
            raise ValueError("QUESTION_OCCURRENCE_OUT_OF_BOUNDS")
        original = json.loads((bank_dir / src).read_bytes())["questions"][index]
        if original.get("id") != row["id"]:
            raise ValueError("QUESTION_OCCURRENCE_ID_MISMATCH")
        occurrence = {
            "paper_id": src.removesuffix(".core2.json"),
            "question_number": row["source_question_number"],
            "question_id": row["id"],
            "source_path": bank["path"],
            "source_array_index": index,
            "source_git_blob_sha": bank["git_blob_sha"],
            "source_sha256": bank["sha256"],
        }
        findings = []
        for finding in row["findings"]:
            identity = "|".join((source_sha, bank["git_blob_sha"], validator_sha,
                                 occurrence["source_path"], str(index), row["id"],
                                 finding["rule"], finding["evidence"], finding["verdict"]))
            findings.append({**finding, "finding_id": digest(identity.encode("utf-8"))})
        questions.append({
            "occurrence": occurrence,
            "declared_tile": row["declared_tile"],
            "difficulty_evidence": row["difficulty_evidence"],
            "technical_verdict": "FAIL" if any(f["verdict"] == "FAIL" for f in findings)
                                 else "REVIEW_REQUIRED",
            "academic_verdict": row["academic_verdict"],
            "native_core_admission": row["native_core_admission"],
            "findings": findings,
            "independent_browser": "NOT_RUN",
            "independent_academic": "NOT_RUN",
        })
    return {
        "schema": FINDINGS_SCHEMA,
        "source_basis": {"commit": source_sha, "expected_total": EXPECTED_TOTAL,
                         "bank_files": source_files},
        "validator_basis": {"commit": validator_sha, "files": validator_files},
        "scope": "RESEARCH_INTAKE_ONLY",
        "status": report["status"],
        "academic_approval": "NOT_GRANTED",
        "source_rights": "UNVERIFIED",
        "execution": {"browser": "NOT_RUN", "academic": "NOT_RUN",
                      "independent_negative_controls": "NOT_RUN"},
        "matrix": {"expected_coordinates": 28, "occupied_coordinates": report["occupied_tiles"],
                   "tiles": report["tiles"]},
        "expected_total": EXPECTED_TOTAL,
        "actual_total": len(questions),
        "questions": questions,
        "stale_audits": report["stale_audits"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bank-dir", type=Path, default=BANK_DIR)
    p.add_argument("--visual-manifest", type=Path, default=VISUAL_MANIFEST)
    p.add_argument("--legacy-audit", type=Path, default=OLD_AUDIT)
    p.add_argument("--baseline-sha", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--findings-output", type=Path, help="optional source+validator Git-bound v1 export")
    p.add_argument("--validator-sha", help="required only with --findings-output")
    args = p.parse_args(argv)
    result = validate_bank_dir(args.bank_dir, visual_manifest=args.visual_manifest,
                               legacy_audit=args.legacy_audit, baseline_sha=args.baseline_sha)
    if args.findings_output:
        if not args.validator_sha:
            raise ValueError("VALIDATOR_COMMIT_REQUIRED_FOR_FINDINGS")
        # Strictly verify source and all validator blobs before publishing either file.
        export = build_question_findings(
            result, repo_root=args.bank_dir.resolve().parents[1],
            source_sha=args.baseline_sha, validator_sha=args.validator_sha,
        )
        args.findings_output.parent.mkdir(parents=True, exist_ok=True)
        args.findings_output.write_text(json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "schema", "baseline_commit", "status", "actual_total", "unique_ids", "occupied_tiles",
        "finding_counts", "fail_counts", "stale_audits")}, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
