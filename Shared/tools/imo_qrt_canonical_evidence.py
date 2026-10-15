#!/usr/bin/env python3
"""Fail-closed research-to-canonical QRT/Blueprint *evidence* bridge.

The research question bank is not a native Core record. Never fabricate route
moves, a learner profile, concept links, or Owner academic acceptance. Delegate
resolvable inputs to the existing canonical QRT and Blueprint contracts.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Shared.tools import question_review_matrix as qrt
from Shared.tools import web_blueprint_contract as blueprint
from Shared.tools.imo_qrt_validator import BANKS, BANK_DIR

SCHEMA = "imo-canonical-evidence-bridge/v1"
REQUIRED = (
    "CANONICAL_FIVE_FACTOR_DIFFICULTY",
    "CANONICAL_DEMAND_AND_BASIS",
    "ANSWER_REASONING_ROUTE",
    "ANSWER_CRUX_MOVE_REFERENCE",
    "ACTUAL_LEARNER_PROFILE",
    "NATIVE_CORE_ROLE_RECORD",
)


def assess(question: dict[str, Any], *, profile: dict[str, Any] | None = None,
           native_role: dict[str, Any] | None = None,
           matrix: dict[str, Any] | None = None,
           vocab: dict[str, Any] | None = None,
           adapter: dict[str, Any] | None = None,
           registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """CANONICAL_RESOLVED means contract execution, NOT qualified QRT acceptance."""
    if not isinstance(question, dict):
        raise ValueError("QUESTION_OBJECT_REQUIRED")
    qid = str(question.get("id") or "<unidentified>")
    failures: list[str] = []
    difficulty = question.get("difficulty")
    demand = (question.get("extensions") or {}).get("grade9v3:cognitive_demand")
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    route = answer.get("reasoning_route")
    ref = answer.get("crux_move_ref")
    if not isinstance(difficulty, dict):
        failures.append(REQUIRED[0])
    if not isinstance(demand, dict) or not isinstance(demand.get("basis"), str) or not demand["basis"].strip():
        failures.append(REQUIRED[1])
    if not isinstance(route, list) or not route:
        failures.append(REQUIRED[2])
    if not isinstance(ref, str) or not ref.strip() or not isinstance(route, list) or not any(
        isinstance(m, dict) and m.get("id") == ref and isinstance(m.get("action"), str) and m["action"].strip()
        for m in route
    ):
        failures.append(REQUIRED[3])
    transfer = question.get("transfer")
    if isinstance(transfer, dict) and transfer.get("protected_move_ref"):
        protected = transfer["protected_move_ref"]
        if not isinstance(route, list) or not any(
            isinstance(m, dict) and m.get("id") == protected for m in route
        ):
            failures.append("TRANSFER_PROTECTED_MOVE_REFERENCE_UNRESOLVED")
    if not isinstance(profile, dict) or not isinstance(profile.get("held"), dict):
        failures.append(REQUIRED[4])
    if not isinstance(native_role, dict):
        failures.append(REQUIRED[5])

    native_blueprint: dict[str, Any] = {"status": "NOT_RUN", "errors": []}
    if isinstance(native_role, dict):
        try:
            findings = blueprint.validate_role_binding(
                "CORE2", native_role, registry=registry or blueprint.load_registry()
            )
            native_blueprint = {
                "status": "STRUCTURE_FAIL" if findings else "STRUCTURE_COMPATIBLE",
                "errors": findings,
                "ref": native_role.get("web_blueprint_ref"),
                "disclaimer": "Blueprint binding is not actual page/browser or academic proof",
            }
            if findings:
                failures.append("NATIVE_CORE2_BLUEPRINT_BINDING_INVALID")
        except (blueprint.WebBlueprintContractError, KeyError, TypeError, ValueError) as exc:
            failures.append("NATIVE_CORE2_BLUEPRINT_CONTRACT_ERROR")
            native_blueprint = {"status": "STRUCTURE_FAIL", "errors": [str(exc)]}

    resolution: dict[str, Any] | None = None
    if not failures:
        try:
            matrix = matrix if matrix is not None else qrt.load(qrt.MATRIX_PATH)
            vocab = vocab if vocab is not None else qrt.load(qrt.VOCAB_PATH)
            result = qrt.resolve_review(question, profile, matrix, vocab)
            if tuple(result.get("review", {})) != qrt.ASKS:
                raise qrt.QRTContractError("TWELVE_ASKS_NOT_COVERED")
            if adapter is None:
                adapter = qrt.load(ROOT / "Mathematics/adapter/DemandReview.json")
            result = qrt.specialize_resolution(result, adapter)
            resolution = {
                "status": "CANONICAL_RESOLVED_UNREVIEWED",
                "template_id": result["template_id"],
                "asks": list(result["review"]),
                "slots": {k: {"basis": v.get("basis", [])} for k, v in result["slots"].items()},
                "basis_digests": result["basis_digests"],
                "subject_adapter": result["subject_adapter"].get("adapter_digest"),
                "academic_verdict": "REVIEW_REQUIRED",
            }
        except (qrt.QRTContractError, ValueError, KeyError, TypeError) as exc:
            failures.append("CANONICAL_QRT_RESOLUTION_REJECTED")
            resolution = {"status": "REJECTED", "reason": str(exc)}

    failures = sorted(set(failures))
    return {
        "id": qid,
        "schema": SCHEMA,
        "status": "CANONICAL_RESOLVED_UNREVIEWED" if resolution is not None and not failures else "BLOCKED_MISSING_OR_INVALID_EVIDENCE",
        "missing_or_invalid": failures,
        "canonical": resolution,
        "blueprint": native_blueprint,
        "academic_verdict": "REVIEW_REQUIRED",
        "rights_verdict": "NOT_VERIFIED",
        "native_product_admission": "NOT_GRANTED",
    }


def inspect_research(*, bank_dir: Path = BANK_DIR, baseline_sha: str) -> dict[str, Any]:
    if len(baseline_sha) != 40 or any(x not in "0123456789abcdef" for x in baseline_sha):
        raise ValueError("EXACT_SOURCE_COMMIT_SHA_REQUIRED")
    sources: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for name in BANKS:
        f = bank_dir / name
        raw = f.read_bytes()
        bank = json.loads(raw)
        if not isinstance(bank, dict) or not isinstance(bank.get("questions"), list):
            raise ValueError("INVALID_QUESTION_BANK:" + name)
        sources.append({"path": str(f), "sha256": sha256(raw).hexdigest(),
                        "count": len(bank["questions"])})
        for q in bank["questions"]:
            if not isinstance(q, dict):
                raise ValueError("NONOBJECT_QUESTION:" + name)
            assessed = assess(q)
            assessed["source_file"] = name
            rows.append(assessed)
    totals = Counter(k for r in rows for k in r["missing_or_invalid"])
    ids = [r["id"] for r in rows]
    resolutions = sum(r["status"] == "CANONICAL_RESOLVED_UNREVIEWED" for r in rows)
    return {
        "schema": SCHEMA, "source_commit": baseline_sha, "scope": "RESEARCH_TO_NATIVE_READINESS",
        "total": len(rows), "unique_ids": len(set(ids)), "canonical_resolved": resolutions,
        "missing_or_invalid_counts": dict(sorted(totals.items())),
        "academic_verdict": "REVIEW_REQUIRED", "native_product_admission": "NOT_GRANTED",
        "sources": sources, "questions": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-sha", required=True)
    parser.add_argument("--bank-dir", type=Path, default=BANK_DIR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = inspect_research(bank_dir=args.bank_dir, baseline_sha=args.baseline_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "schema", "source_commit", "scope", "total", "unique_ids",
        "canonical_resolved", "missing_or_invalid_counts", "academic_verdict"
    )}, indent=2))
    return 0 if (result["total"] == result["unique_ids"] and
                 result["canonical_resolved"] == result["total"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
