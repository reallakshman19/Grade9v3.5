#!/usr/bin/env python3
"""Read-only, metadata-only Core2 Q004 blueprint-readiness audit.

This tool reads the existing canonical blueprint and source-question custody
schema. A spotcheck verdict is untrusted *operator metadata*, not a source PDF,
rights grant, independent inspection, canonical record, or product acceptance.
Never feed original SOF stems/options/figures or private PNG/PDF bytes to it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BLUEPRINT = "BP-CORE2-SOURCE-QUESTION"
BLUEPRINT_VERSION = "1.11.0"
QUESTION = "SOF-IMO-G09-SAMPLE-2026-27-Q004"
SOURCE = "SOF-IMO-G09-SAMPLE-2026-27"
SPOTCHECK_SCHEMA = "imo-g9-q004-spotcheck-verdict-v1"
REPORT_SCHEMA = "imo-core2-blueprint-readiness-v1"
# The nine semantic components are a public compatibility expectation. Their
# allowed *dispositions* and presence requirements are always read from schema.
NINE = frozenset({
    "original_identifier", "stem", "subparts", "options", "conditions",
    "figures", "captions", "hints", "answer_or_rubric",
})
REQUIRED_BLUEPRINT_COMPONENTS = frozenset({
    "IDENTITY", "STEM", "ATTEMPT", "SOLUTION", "SOLUTION_STEPS", "ANSWER",
})
PROOF_REQUIRED = frozenset({
    "version", "acquisition_ref", "resource_ref", "source_item_locator",
    "source_digest", "custody_mode", "comparison_status", "demand_signature",
    "components", "notes",
})
REQUIRED_COMPONENT_SLOTS = {
    "IDENTITY": "identity", "STEM": "attempt", "ATTEMPT": "attempt",
    "SOLUTION": "solution", "SOLUTION_STEPS": "solution", "ANSWER": "solution",
}
SPOTCHECK_KEYS = frozenset({
    "schema", "question_id", "status", "component_check_complete",
    "historical_version_comparison", "blocking_codes",
    "self_attestation_not_source_certificate", "source_custody_hold",
    "core2_eligible", "core2_admitted", "learner_published", "source_rights",
})
SPOTCHECK_STATUSES = frozenset({
    "HOLD_RETAINED_SOURCE_NOT_VERIFIED",
    "HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE",
    "HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE",
    "SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED",
})
BLOCKERS_ALWAYS = (
    "SOURCE_RECEIPT_NOT_INDEPENDENTLY_VERIFIED_BY_THIS_AUDIT",
    "NINE_COMPONENT_CANONICAL_CUSTODY_PROOF_REQUIRED",
    "INDEPENDENT_CUSTODY_AND_MATH_REVIEW_REQUIRED",
    "DOCUMENT_SPECIFIC_RIGHTS_DECISION_REQUIRED",
    "ACADEMIC_QRT_AND_OWNER_ADMISSION_REQUIRED",
    "LEARNER_RELEASE_NOT_AUTHORIZED",
)
MAX_METADATA_BYTES = 16384
# Upstream compare_historical_fingerprint returns only these values. A spotcheck
# summary cannot prove its own provenance, but internally contradictory claims
# must not be portrayed as a completed operator inspection.
VERSION_STATES = frozenset({
    "NOT_CHECKED_NO_RETAINED_BYTES", "NOT_CHECKED_INVALID_RECEIPT",
    "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY",
    "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION",
})


def _fields_equal(value: Any, names: frozenset[str]) -> bool:
    """Compare a schema/blueprint list without accepting duplicate or unhashable IDs."""
    return (isinstance(value, list) and len(value) == len(names)
            and all(isinstance(name, str) for name in value)
            and set(value) == names)


def _object(value: Any) -> dict[str, Any]:
    """Malformed checked-in schemas are HOLDs, never raw AttributeError traces."""
    return value if isinstance(value, dict) else {}


class AuditError(ValueError):
    """Internal categorized failure. No input text or private paths are echoed."""


def _read_json(path: Path, category: str, *, size_limit: int) -> dict[str, Any]:
    """Open the checked input once; never follow a final symlink or block on a FIFO."""
    try:
        # The prior path.is_symlink/stat/read_text sequence was vulnerable to
        # replacement between its check and the actual read. Validate the opened
        # descriptor and bound bytes read even if its reported size is stale.
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        if not hasattr(os, "O_NOFOLLOW") and path.is_symlink():
            raise AuditError(category)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > size_limit:
                raise AuditError(category)
            raw = stream.read(size_limit + 1)
        if len(raw) > size_limit:
            raise AuditError(category)
        def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            item: dict[str, Any] = {}
            for key, value in pairs:
                if key in item:
                    raise ValueError("duplicate JSON key")
                item[key] = value
            return item

        def reject_nonfinite(_: str) -> None:
            raise ValueError("non-finite JSON value")

        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys,
                          parse_constant=reject_nonfinite)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise AuditError(category) from exc
    if not isinstance(data, dict):
        raise AuditError(category)
    return data


def canonical_contracts(repo: Path) -> dict[str, Any]:
    """Verify existing, not redefined, schema/blueprint compatibility."""
    custody = _read_json(
        repo / "Shared/library/source-question-custody.schema.json",
        "SOURCE_CUSTODY_SCHEMA_UNAVAILABLE", size_limit=250000,
    )
    proof_props = custody.get("properties")
    if (custody.get("type") != "object"
        or custody.get("additionalProperties") is not False
        or not _fields_equal(custody.get("required"), PROOF_REQUIRED)
        or not isinstance(proof_props, dict)
        or set(proof_props) != PROOF_REQUIRED
        or _object(proof_props.get("version")).get("const") != "1.0.0"
        or _object(proof_props.get("source_digest")).get("pattern") != "^[0-9a-f]{64}$"
        or _object(proof_props.get("demand_signature")).get("pattern") != "^[0-9a-f]{64}$"
        or not _fields_equal(_object(proof_props.get("custody_mode")).get("enum"),
                             frozenset({"EMBEDDED_VERBATIM", "EXTERNAL_REFERENCE"}))
        or not _fields_equal(_object(proof_props.get("comparison_status")).get("enum"),
                             frozenset({"ORIGINAL_EXACT", "ADAPTED_DECLARED", "UNRESOLVED"}))):
        raise AuditError("CUSTODY_PROOF_TOP_LEVEL_DRIFT")
    components = proof_props.get("components")
    if not isinstance(components, dict):
        raise AuditError("CUSTODY_SCHEMA_COMPONENT_DRIFT")
    names = components.get("required")
    properties = components.get("properties")
    status_enum = _object(_object(custody.get("$defs")).get("componentStatus")).get("enum")
    if (components.get("type") != "object"
        or not _fields_equal(names, NINE) or not isinstance(properties, dict)
        or set(properties) != NINE or components.get("additionalProperties") is not False
        or not _fields_equal(status_enum, frozenset({
            "PRESERVED", "NOT_PRESENT_IN_SOURCE", "EXTERNAL_REFERENCE_VERIFIED", "UNRESOLVED"
        }))
        or any(_object(properties[k]).get("$ref") != "#/$defs/componentStatus"
               for k in NINE)):
        raise AuditError("CUSTODY_SCHEMA_COMPONENT_DRIFT")
    if custody.get("$id") != "https://grade9v3.local/source-question-custody.schema.json":
        raise AuditError("CUSTODY_SCHEMA_ID_DRIFT")

    registry = _read_json(
        repo / "Shared/web/interactive-page-blueprints.v1.json",
        "BLUEPRINT_REGISTRY_UNAVAILABLE", size_limit=300000,
    )
    if registry.get("registry_version") != "1.17.0":
        raise AuditError("CORE2_BLUEPRINT_MISSING_OR_DRIFTED")
    blueprints = registry.get("blueprints")
    if not isinstance(blueprints, list):
        raise AuditError("CORE2_BLUEPRINT_MISSING_OR_DRIFTED")
    matched = [b for b in blueprints if isinstance(b, dict) and b.get("id") == BLUEPRINT]
    if len(matched) != 1:
        raise AuditError("CORE2_BLUEPRINT_MISSING_OR_DRIFTED")
    bp = matched[0]
    slots = bp.get("slots")
    comps = bp.get("components")
    if (bp.get("version") != BLUEPRINT_VERSION or bp.get("status") != "ACTIVE"
        or bp.get("core_roles") != ["CORE2"]
        or not isinstance(slots, list) or not isinstance(comps, list)):
        raise AuditError("CORE2_BLUEPRINT_MISSING_OR_DRIFTED")
    required = [c.get("id") for c in comps
                if isinstance(c, dict) and c.get("level") == "REQUIRED"]
    if (not slots or not all(isinstance(s, dict) and isinstance(s.get("id"), str)
                             for s in slots)
        or len({s["id"] for s in slots}) != len(slots)
        or not all(isinstance(c, dict) and isinstance(c.get("id"), str)
                   and isinstance(c.get("slot"), str) for c in comps)
        or len({c["id"] for c in comps if isinstance(c, dict)
                and isinstance(c.get("id"), str)}) != len(comps)
        or not _fields_equal(required, REQUIRED_BLUEPRINT_COMPONENTS)
        or any(c.get("slot") not in {s["id"] for s in slots} for c in comps)
        or any(next((c.get("slot") for c in comps if c.get("id") == name), None)
               != slot for name, slot in REQUIRED_COMPONENT_SLOTS.items())):
        raise AuditError("CORE2_BLUEPRINT_REQUIRED_COMPONENT_DRIFT")
    return {
        "custody_schema_id": custody["$id"],
        "blueprint_ref": BLUEPRINT + "@" + bp["version"],
        "registry_version": registry.get("registry_version"),
        "custody_component_names": sorted(names),
        "blueprint_required_components": sorted(required),
    }


def _spotcheck_claim(row: dict[str, Any]) -> dict[str, Any]:
    """Treat external verdict as untrusted claim; never elevate authority."""
    if set(row) != SPOTCHECK_KEYS or row.get("schema") != SPOTCHECK_SCHEMA:
        raise AuditError("SPOTCHECK_METADATA_INVALID")
    if (row.get("question_id") != QUESTION
        or not isinstance(row.get("status"), str)
        or row["status"] not in SPOTCHECK_STATUSES
        or type(row.get("component_check_complete")) is not bool
        or row.get("self_attestation_not_source_certificate") is not True
        or type(row.get("source_custody_hold")) is not int
        or row.get("source_custody_hold") != 68
        or any(row.get(key) is not False for key in
               ("core2_eligible", "core2_admitted", "learner_published"))
        or row.get("source_rights") != "NOT_REVIEWED"
        or not isinstance(row.get("historical_version_comparison"), str)
        or row["historical_version_comparison"] not in VERSION_STATES
        or not isinstance(row.get("blocking_codes"), list)
        or len(row["blocking_codes"]) > 32
        or any(not isinstance(c, str) or not re.fullmatch(r"[A-Z0-9_]{1,100}", c)
               for c in row["blocking_codes"])):
        raise AuditError("SPOTCHECK_METADATA_INVALID")
    complete = row["status"] == "SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED"
    if complete and (not row["component_check_complete"] or row["blocking_codes"]):
        raise AuditError("SPOTCHECK_METADATA_INCONSISTENT")
    status = row["status"]
    version = row["historical_version_comparison"]
    findings = row["blocking_codes"]
    if (status == "HOLD_RETAINED_SOURCE_NOT_VERIFIED"
        and (version not in {"NOT_CHECKED_NO_RETAINED_BYTES", "NOT_CHECKED_INVALID_RECEIPT"}
             or "PRIVATE_RETAINED_PDF_RECEIPT_MISSING_OR_INVALID" not in findings)):
        raise AuditError("SPOTCHECK_METADATA_INCONSISTENT")
    if (status == "HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE"
        and (version != "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION"
             or "SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED" not in findings)):
        raise AuditError("SPOTCHECK_METADATA_INCONSISTENT")
    if status in {"HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE",
                  "SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED"} and (
            version != "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY"
            or (status == "HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE" and not findings)):
        raise AuditError("SPOTCHECK_METADATA_INCONSISTENT")
    return {"state": "SELF_CHECK_REPORTED_ONLY" if complete else "HOLD_REPORTED",
            "operator_self_check_claimed": complete}


def report(repo: Path = REPO, verdict: dict[str, Any] | None = None) -> dict[str, Any]:
    contracts = canonical_contracts(repo)
    spotcheck = {"state": "NO_VERDICT_SUPPLIED", "operator_self_check_claimed": False}
    if verdict is not None:
        spotcheck = _spotcheck_claim(verdict)
    blockers = list(BLOCKERS_ALWAYS)
    if verdict is None:
        blockers.insert(0, "PRIVATE_SOURCE_VERIFIER_RESULT_NOT_SUPPLIED")
    elif not spotcheck["operator_self_check_claimed"]:
        blockers.insert(0, "SOURCE_OPERATOR_SELF_CHECK_NOT_COMPLETE")
    return {
        "schema": REPORT_SCHEMA,
        "authority": "READ_ONLY_CONTRACT_GAP_AUDIT_NOT_SOURCE_ADMISSION",
        "source_id": SOURCE,
        "question_id": QUESTION,
        "contracts": contracts,
        "spotcheck": spotcheck,
        "decision": "HOLD_MISSING_EVIDENCE",
        "blockers": blockers,
        "rights_granted": False,
        "independent_review_accepted": False,
        "core2_eligible": False,
        "core2_admitted": False,
        "learner_published": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("operation", choices=("report",))
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--spotcheck-verdict", type=Path)
    args = parser.parse_args()
    try:
        verdict = (_read_json(args.spotcheck_verdict, "SPOTCHECK_METADATA_UNAVAILABLE",
                              size_limit=MAX_METADATA_BYTES)
                   if args.spotcheck_verdict is not None else None)
        value = report(args.repo_root, verdict)
    except AuditError as exc:
        # Fixed safe codes only; never echo raw data or private file paths.
        parser.exit(1, "CORE2_BLUEPRINT_READINESS_HOLD: " + str(exc) + "\n")
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
