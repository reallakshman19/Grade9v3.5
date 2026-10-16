"""Read-only source-to-capability/Core/QRT candidate inspection.

This reports what the *canonical package actually declares*. It does not certify
physics, source licensing, QRT semantics, published pages, or learner mastery.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from Shared.tools import question_difficulty

ROOT = Path(__file__).resolve().parents[3]
SOURCE_PREFIX = Path("Physics/library")


def inspect_question(package_path: str, question_id: str, *, root: Path = ROOT) -> dict:
    """Inspect a real named question without inventing missing joins."""
    errors: list[str] = []
    relative = Path(package_path)
    if relative.is_absolute() or ".." in relative.parts or not relative.is_relative_to(SOURCE_PREFIX):
        raise ValueError("PHYSICS_LIBRARY_PATH_REQUIRED")
    path = (root / relative).resolve()
    if not path.is_relative_to((root / SOURCE_PREFIX).resolve()) or not path.is_file():
        raise ValueError("PHYSICS_LIBRARY_SOURCE_UNAVAILABLE")
    source_bytes = path.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    git_blob_sha = hashlib.sha1(b"blob " + str(len(source_bytes)).encode("ascii") + b"\0" + source_bytes).hexdigest()
    package = json.loads(source_bytes)
    if not isinstance(package, dict) or package.get("subject") != "Physics":
        raise ValueError("PHYSICS_PACKAGE_REQUIRED")
    questions = package.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError("QUESTIONS_ARRAY_REQUIRED")
    matches = [q for q in questions if isinstance(q, dict) and q.get("id") == question_id]
    if len(matches) != 1:
        errors.append("QUESTION_MISSING" if not matches else "AMBIGUOUS_QUESTION_ID")
    question = matches[0] if len(matches) == 1 else {}
    primary = question.get("primary_capability_ref")
    capabilities = {c.get("id") for c in package.get("capabilities", []) if isinstance(c, dict)}
    if matches and primary not in capabilities:
        errors.append("PRIMARY_CAPABILITY_NOT_IN_PACKAGE")
    source_refs = question.get("source_refs") or []
    resources = {row.get("id") for row in package.get("resources", []) if isinstance(row, dict)}
    if matches and (not source_refs or any(ref not in resources for ref in source_refs)):
        errors.append("SOURCE_CUSTODY_REF_UNRESOLVED")
    difficulty = None
    if matches:
        try:
            difficulty = question_difficulty.derive(question.get("difficulty"), question_ref=question_id)
        except question_difficulty.DifficultyContractError as exc:
            errors.append(str(exc))
    exposed = [e.get("core") for e in question.get("exposure", []) if isinstance(e, dict)]
    compiled = [e.get("artifact_ref") for e in question.get("exposure", [])
                if isinstance(e, dict) and e.get("artifact_ref")]
    if matches and "CORE2B" in exposed:
        transfer = question.get("transfer") or {}
        if not all(transfer.get(k) for k in ("dimension", "builds_on", "protected_move_ref")):
            errors.append("CORE2B_TRANSFER_CONTRACT_INCOMPLETE")
        if not question.get("repair_ref") or not (question.get("answer") or {}).get("rubric"):
            errors.append("CORE2B_REPAIR_OR_RUBRIC_MISSING")
    return {
        "schema": "physics-qrt.source-crosswalk/v1",
        "question_id": question_id,
        "package_path": relative.as_posix(),
        "package_sha256": source_sha256,
        "package_blob_sha": git_blob_sha,
        "original_identifier": question.get("original_identifier"),
        "source_class": "AUTHOR_CREATED_CANDIDATE" if question.get("origin") == "AUTHORED" else "UNKNOWN_REVIEW_REQUIRED",
        "source_refs": source_refs,
        "primary_capability_ref": primary,
        "difficulty": difficulty,
        "qrt_demand": "UNRESOLVED_RUN_CANONICAL_QRT",
        "declared_cores": exposed,
        "compiled_artifact_refs": compiled,
        "render_verdict": "NOT_ATTESTED",
        "physics_verdict": "REVIEW_REQUIRED",
        "academic_verdict": "REVIEW_REQUIRED",
        "school_micro_demand": "MICRO_TO_CONFIRM",
        "errors": errors,
        "status": "SOURCE_STRUCTURALLY_BOUND_NOT_ACCEPTED" if not errors else "HOLD",
    }
