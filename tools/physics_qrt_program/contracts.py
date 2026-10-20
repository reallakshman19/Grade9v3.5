"""Deterministic fail-closed contracts for bounded Physics QRT worker evidence.

No production Physics/QRT input is rewritten.  PASS of these checks establishes
envelope consistency, never academic truth, Owner admission or merge authority.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath

PROGRAMME = "PHY-QRT-LTA-v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ROLES = ("L1", "L2", "L3", "L4")
CHECK_STATES = {"PASS", "FAIL", "NOT_RUN", "STALE", "REVIEW_REQUIRED"}
WORK_STATES = {"DRAFT_HOLD", "FROZEN_APPROVED"}
RECEIPT_STATES = {
    "NOT_RUN", "BLOCKED_INPUT", "BLOCKED_ORACLE", "STALE",
    "REVIEW_REQUIRED", "ESCALATE_WRITER", "FAILED_TESTS",
    "FAILED_BROWSER", "FALSE_PASS", "FALSE_ALARM", "READY_FOR_COORDINATOR",
}
SOURCE_CLASSES = {
    "SCHOOL_ISSUED", "OWNER_APPROVED_EXTERNAL_DEMAND",
    "OWNER_SUPPLIED", "AUTHOR_CREATED_CANDIDATE", "CANONICAL_LIBRARY",
    "DERIVED_AUDIT", "UNKNOWN",
}


def _sha(value: object, length: int) -> bool:
    return isinstance(value, str) and bool((HEX40 if length == 40 else HEX64).fullmatch(value))


def _safe_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and not any(x in (".", "..", "") for x in parts)


def _under(path: str, prefix: str) -> bool:
    return path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/")


def _overlap(a: str, b: str) -> bool:
    return _under(a.rstrip("/"), b.rstrip("/")) or _under(b.rstrip("/"), a.rstrip("/"))


def validate_lock(lock: dict, *, require_authorized: bool = False) -> list[str]:
    """Check source custody, lease isolation and (optionally) real write prerequisites."""
    if not isinstance(lock, dict):
        return ["LOCK_NOT_OBJECT"]
    errors: list[str] = []
    if lock.get("schema") != "physics-qrt.work-lock/v1":
        errors.append("LOCK_SCHEMA")
    if lock.get("programme") != PROGRAMME:
        errors.append("PROGRAMME_ID")
    if lock.get("repository") != "reallakshman19/Grade9v3.5":
        errors.append("REPOSITORY_SCOPE")
    if not _sha(lock.get("base_sha"), 40):
        errors.append("BASE_SHA")
    if lock.get("state") not in WORK_STATES:
        errors.append("WORK_STATE")
    if lock.get("scope_policy") != "GRADE9_DEMAND_FIRST_NO_EXTENSION_DEFAULT":
        errors.append("SCOPE_POLICY")
    leases = lock.get("writer_leases")
    if not isinstance(leases, dict) or set(leases) != set(ROLES):
        errors.append("WRITER_LEASE_ROLES")
        leases = {}
    occupied: list[tuple[str, str]] = []
    for role, paths in leases.items():
        if role not in ROLES or not isinstance(paths, list) or not paths:
            errors.append(f"INVALID_LEASE:{role}")
            continue
        for path in paths:
            if not _safe_path(path):
                errors.append(f"UNSAFE_LEASE:{role}:{path}")
                continue
            for prev_role, prev_path in occupied:
                if role != prev_role and _overlap(path, prev_path):
                    errors.append(f"OVERLAP:{role}:{prev_role}:{path}:{prev_path}")
            occupied.append((role, path))
    ids = lock.get("selected_question_ids")
    if not isinstance(ids, list) or any(not isinstance(q, str) or not q.strip() for q in ids):
        errors.append("QUESTION_ID_LIST")
        ids = []
    elif len(set(ids)) != len(ids):
        errors.append("DUPLICATE_QUESTION_ID")
    witnesses = lock.get("witnesses")
    if not isinstance(witnesses, list):
        errors.append("WITNESS_LIST")
        witnesses = []
    seen: set[str] = set()
    for i, w in enumerate(witnesses):
        if not isinstance(w, dict):
            errors.append(f"WITNESS_OBJECT:{i}")
            continue
        qid = w.get("question_id")
        if qid not in ids or qid in seen:
            errors.append(f"WITNESS_QUESTION_ID:{i}")
        if isinstance(qid, str):
            seen.add(qid)
        if w.get("source_class") not in SOURCE_CLASSES:
            errors.append(f"WITNESS_SOURCE_CLASS:{i}")
        if not _safe_path(w.get("source_path")) or not _sha(w.get("source_sha256"), 64):
            errors.append(f"WITNESS_SOURCE_DIGEST:{i}")
        if not isinstance(w.get("capability_ref"), str) or not w.get("capability_ref"):
            errors.append(f"WITNESS_CAPABILITY:{i}")
        if w.get("school_micro_demand") not in ("MICRO_TO_CONFIRM", "SCHOOL_CONFIRMED", "NOT_SCHOOL_CLAIMED"):
            errors.append(f"WITNESS_SCHOOL_DEMAND:{i}")
    governance = lock.get("governance")
    if not isinstance(governance, dict):
        errors.append("GOVERNANCE_OBJECT")
        governance = {}
    if require_authorized:
        if lock.get("state") != "FROZEN_APPROVED":
            errors.append("WORK_LOCK_NOT_APPROVED")
        if not governance.get("git_write_authorized"):
            errors.append("GIT_WRITES_NOT_AUTHORIZED")
        if not isinstance(governance.get("approval_ref"), str) or not governance["approval_ref"].strip():
            errors.append("OWNER_APPROVAL_REF_MISSING")
        if not lock.get("owner_issue"):
            errors.append("OWNER_ISSUE_MISSING")
        if not ids or set(ids) != seen:
            errors.append("SELECTED_WITNESSES_INCOMPLETE")
        if not _sha(governance.get("scientific_oracle_sha256"), 64):
            errors.append("SCIENTIFIC_ORACLE_UNREVIEWED")
        if governance.get("scientific_oracle_review") != "INDEPENDENT_REVIEWED":
            errors.append("SCIENTIFIC_REVIEW_MISSING")
    return errors


def validate_receipt(receipt: dict, lock: dict) -> list[str]:
    """Read-only worker receipt validation with strict source and writer boundaries."""
    if not isinstance(receipt, dict):
        return ["RECEIPT_NOT_OBJECT"]
    errors: list[str] = []
    if receipt.get("schema") != "physics-qrt.receipt/v1" or receipt.get("programme") != PROGRAMME:
        errors.append("RECEIPT_SCHEMA")
    role = receipt.get("agent")
    if role not in ROLES:
        errors.append("RECEIPT_ROLE")
    if receipt.get("base_sha") != lock.get("base_sha") or not _sha(receipt.get("base_sha"), 40):
        errors.append("STALE_BASE_SHA")
    candidate = receipt.get("candidate_sha")
    if candidate is not None and not _sha(candidate, 40):
        errors.append("INVALID_CANDIDATE_SHA")
    if receipt.get("state") not in RECEIPT_STATES:
        errors.append("RECEIPT_STATE")
    selected = lock.get("selected_question_ids", [])
    scope = receipt.get("scope")
    if not isinstance(scope, list) or not scope or not set(scope).issubset(set(selected)):
        errors.append("RECEIPT_SCOPE_NOT_LOCKED")
    checks = receipt.get("checks")
    if not isinstance(checks, list):
        errors.append("CHECKS_ARRAY")
        checks = []
    seen = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"CHECK_OBJECT:{index}")
            continue
        ident = check.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            errors.append(f"CHECK_ID:{index}")
        seen.add(ident)
        result = check.get("status")
        if result not in CHECK_STATES:
            errors.append(f"CHECK_STATUS:{index}")
        if not isinstance(check.get("command"), str) or not check.get("command"):
            errors.append(f"CHECK_COMMAND:{index}")
        if not isinstance(check.get("expected"), str) or not check.get("expected"):
            errors.append(f"CHECK_EXPECTED:{index}")
        if result == "PASS" and (check.get("exit_code") != 0 or not _sha(check.get("evidence_sha256"), 64) or not check.get("observed")):
            errors.append(f"FALSE_PASS_ENVELOPE:{index}")
        if result == "NOT_RUN" and (check.get("exit_code") is not None or check.get("evidence_sha256") is not None):
            errors.append(f"NOT_RUN_WITH_EXECUTION:{index}")
        if result in {"FAIL", "STALE"} and not check.get("observed"):
            errors.append(f"NO_FAILURE_OBSERVATION:{index}")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("ARTIFACTS_ARRAY")
        artifacts = []
    assigned = lock.get("writer_leases", {}).get(role, [])
    for i, a in enumerate(artifacts):
        if not isinstance(a, dict) or not _safe_path(a.get("path")):
            errors.append(f"ARTIFACT_PATH:{i}")
            continue
        if not _sha(a.get("sha256"), 64):
            errors.append(f"ARTIFACT_SHA256:{i}")
        if not any(_under(a["path"], prefix) for prefix in assigned):
            errors.append(f"WRITER_LEASE_VIOLATION:{i}")
    if receipt.get("state") == "READY_FOR_COORDINATOR":
        if not checks or any(c.get("status") != "PASS" for c in checks if isinstance(c, dict)):
            errors.append("READY_WITH_UNVERIFIED_CHECKS")
        if not artifacts:
            errors.append("READY_WITHOUT_ARTIFACT")
    for field in ("findings", "uncertainties"):
        if not isinstance(receipt.get(field), list):
            errors.append(f"RECEIPT_{field.upper()}_LIST")
    return errors


def converge(lock: dict, receipts: list[dict]) -> dict:
    """Never conclude scientific or release PASS from envelopes alone."""
    by_role: dict[str, dict] = {}
    findings: list[dict] = []
    for receipt in receipts:
        role = receipt.get("agent") if isinstance(receipt, dict) else None
        if role in by_role:
            findings.append({"code": "DUPLICATE_ROLE", "role": role})
        elif role in ROLES:
            by_role[role] = receipt
        else:
            findings.append({"code": "UNKNOWN_ROLE"})
    for role in ROLES:
        if role not in by_role:
            findings.append({"code": "MISSING_ROLE", "role": role})
        else:
            errors = validate_receipt(by_role[role], lock)
            if errors:
                findings.append({"code": "INVALID_RECEIPT", "role": role, "errors": errors})
            if by_role[role].get("state") != "READY_FOR_COORDINATOR":
                findings.append({"code": "WORKER_NOT_READY", "role": role, "state": by_role[role].get("state")})
    lock_errors = validate_lock(lock, require_authorized=True)
    if lock_errors:
        findings.append({"code": "AUTHORITY_HOLD", "errors": lock_errors})
    return {
        "schema": "physics-qrt.convergence/v1",
        "programme": PROGRAMME,
        "base_sha": lock.get("base_sha"),
        "workers_received": sorted(by_role),
        "envelope_ready": not findings,
        "science_verdict": "REVIEW_REQUIRED",
        "academic_verdict": "REVIEW_REQUIRED",
        "learner_verdict": "INSUFFICIENT_OR_UNKNOWN",
        "release_verdict": "HOLD",
        "findings": findings,
    }
