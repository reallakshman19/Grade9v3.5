"""Read-only Wave-0 source candidates -> draft work lock; never an approval."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from Physics.adapter.qrt_crosswalk import inspect_question
from .contracts import validate_lock

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

class BootstrapError(ValueError):
    pass

def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def assemble(*, root: Path = ROOT, candidates: dict | None = None,
             draft_lock: dict | None = None) -> dict:
    candidates = copy.deepcopy(candidates if candidates is not None else _read(HERE / "witnesses.candidate.v1.json"))
    lock = copy.deepcopy(draft_lock if draft_lock is not None else _read(HERE / "work-lock.template.json"))
    if candidates.get("schema") != "physics-qrt.witness-candidates/v1":
        raise BootstrapError("CANDIDATES_SCHEMA")
    if candidates.get("programme") != lock.get("programme") or candidates.get("base_sha") != lock.get("base_sha"):
        raise BootstrapError("SOURCE_BASIS_MISMATCH")
    if candidates.get("stage") != "CANDIDATE_NOT_FROZEN":
        raise BootstrapError("CANDIDATES_ARE_NOT_AUTHORIZED")
    if lock.get("state") != "DRAFT_HOLD" or lock.get("governance", {}).get("git_write_authorized"):
        raise BootstrapError("LOCK_NOT_DRAFT_HOLD")
    cases = candidates.get("cases")
    if not isinstance(cases, list) or not cases:
        raise BootstrapError("EMPTY_CANDIDATE_SET")
    witnesses, details, errors = [], [], []
    for case in cases:
        if not isinstance(case, dict):
            raise BootstrapError("CANDIDATE_NOT_OBJECT")
        qid = case.get("question_id")
        try:
            record = inspect_question(case.get("package"), qid, root=root)
        except (ValueError, OSError, TypeError) as exc:
            errors.append(f"SOURCE_UNAVAILABLE:{qid}:{exc}")
            continue
        if record["errors"]:
            errors.append(f"SOURCE_DEFECT:{qid}:{record['errors']}")
        if record["primary_capability_ref"] != case.get("expected_capability"):
            errors.append(f"CAPABILITY_DRIFT:{qid}")
        if case.get("expected_core") not in record["declared_cores"]:
            errors.append(f"CORE_DRIFT:{qid}")
        if record["package_blob_sha"] != case.get("source_blob_sha"):
            errors.append(f"SOURCE_BLOB_DRIFT:{qid}")
        if record["source_class"] != "AUTHOR_CREATED_CANDIDATE":
            errors.append(f"SOURCE_CLASS_DRIFT:{qid}")
        witnesses.append({
            "question_id": qid, "source_class": record["source_class"],
            "source_path": record["package_path"], "source_sha256": record["package_sha256"],
            "capability_ref": record["primary_capability_ref"],
            "school_micro_demand": "MICRO_TO_CONFIRM"
        })
        details.append({
            "question_id": qid, "family": case.get("family"), "scope_role": case.get("scope_role"),
            "source_blob_sha": case.get("source_blob_sha"), "source_sha256": record["package_sha256"],
            "declared_core": case.get("expected_core"), "difficulty": record["difficulty"],
            "qrt_demand": "UNRESOLVED_RUN_CANONICAL_QRT",
            "science": "REVIEW_REQUIRED", "render": "NOT_ATTESTED"
        })
    lock["selected_question_ids"] = [x["question_id"] for x in witnesses]
    lock["witnesses"] = witnesses
    errors += validate_lock(lock)
    if errors:
        raise BootstrapError("; ".join(errors))
    return {
        "schema": "physics-qrt.bootstrap/v1",
        "status": "SOURCE_CANDIDATES_VERIFIED_AUTHORITY_HOLD",
        "lock": lock, "cases": details,
        "scientific_verdict": "REVIEW_REQUIRED",
        "academic_verdict": "REVIEW_REQUIRED",
        "release_verdict": "HOLD"
    }
