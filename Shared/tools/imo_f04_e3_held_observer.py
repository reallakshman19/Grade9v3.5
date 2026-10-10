"""Independent F04 observer for F02's denied E3 transfer gate (held TEST only).

Confirms source/receipt consistency and the five explicit missing adjudications.
Never converts F02's green negative-control CI into academic approval or
authenticated unseen learner transfer. Public output: fixed codes + hashes only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "imo-f04-e3-source-held-observer/v1"
F02_SCHEMA = "imo-f02-e3-held-transfer-preflight/v1"
QUESTION = "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01"
MICROTOPIC = "MIC-TEST-IMO-G9-COMMON-BASE-RELATION"
DECLARED = ("CORE1A_DECLARED_EXIT", "GOLDEN_REVIEW_FRESH_EXIT")
REQUIREMENTS = (
    "NEW_ITEM_CUSTODY_AND_UNSEENNESS_INDEPENDENTLY_VERIFIED",
    "FIRST_UNAIDED_ATTEMPT_AUTHENTICATED_WITH_DISCLOSURE_CHRONOLOGY",
    "SOURCE_BOUND_MATH_REASONING_RUBRIC_INDEPENDENTLY_ADJUDICATED",
    "MISCONCEPTION_VERSUS_EXECUTION_SLIP_HUMAN_REVIEW",
    "H_S_P_M_SEMANTIC_REVIEW_AND_OWNER_APPROVAL",
)
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observe(manifest: object, package: object, golden: object, e3: object) -> dict:
    """Safe fixed-code denial reasons only, never source/learner free text."""
    issues = []
    if not isinstance(manifest, dict) or (
        manifest.get("subject") != "TEST"
        or manifest.get("output_roles") != ["CORE1A", "CORE2A"]
        or not isinstance(manifest.get("selection"), dict)
        or manifest["selection"].get("core2a") != [QUESTION]
        or manifest["selection"].get("microtopics") != [MICROTOPIC]
        or manifest["selection"].get("core2") != []
        or manifest["selection"].get("core2b") != []
    ):
        issues.append("E3_F04_UNAUTHORIZED_MANIFEST_SCOPE")

    if not isinstance(package, dict):
        issues.append("E3_F04_UNAUTHORIZED_PACKAGE")
    else:
        ext = package.get("extensions")
        questions = package.get("questions")
        if (package.get("subject") != "TEST"
            or package.get("status") != "CANDIDATE"
            or not isinstance(ext, dict)
            or any(ext.get(k) is not False for k in (
                "grade9v3:learner_published",
                "grade9v3:qrt_admitted",
                "grade9v3:core2_source_custody_granted"))
            or not isinstance(questions, list)
            or sum(isinstance(q, dict)
                   and q.get("id") == QUESTION and q.get("origin") == "AUTHORED"
                   for q in questions) != 1):
            issues.append("E3_F04_UNAUTHORIZED_PACKAGE")

    if not isinstance(golden, dict) or (
        golden.get("status") != "AUTHOR_REVIEW_FIXTURE_NOT_LEARNER_PRODUCT"
        or not isinstance(golden.get("governance"), dict)
        or golden["governance"].get("academic_review") != "NOT_GRANTED"
    ):
        issues.append("E3_F04_GOLDEN_EXPOSURE_BOUNDARY_UNVERIFIED")

    if not isinstance(e3, dict) or (
        e3.get("schema") != F02_SCHEMA
        or e3.get("subject") != "TEST"
        or e3.get("existing_assisted_target") != QUESTION
        or e3.get("already_disclosed_probes") != list(DECLARED)
        or e3.get("browser_local_trace_authority") != "UNTRUSTED_NOT_CREDIT"
    ):
        issues.append("E3_F04_SOURCE_LEDGER_INVALID")
    else:
        if (e3.get("assessment_status") != "REVIEW_ONLY_HOLD_NOT_ACCEPTED"
            or e3.get("independent_mastery_verified") is not False
            or e3.get("credit_eligible") is not False
            or e3.get("new_item_provisioned") is not False):
            issues.append("E3_F04_UNAUTHORIZED_TRANSFER_CREDIT")
        if e3.get("errors") != [] or e3.get("findings") != [
            "E3_INDEPENDENT_EVIDENCE_NOT_ESTABLISHED"
        ]:
            issues.append("E3_F04_SOURCE_LEDGER_FINDINGS_UNSAFE")
        reqs = e3.get("requirements")
        if (not isinstance(reqs, list) or len(reqs) != len(REQUIREMENTS)
            or any(not isinstance(row, dict) for row in reqs)
            or [row.get("code") for row in reqs] != list(REQUIREMENTS)
            or any(row.get("status") != "INDEPENDENT_EVIDENCE_NOT_PROVIDED"
                   for row in reqs)):
            issues.append("E3_F04_INDEPENDENT_REVIEW_REQUIREMENTS_MISSING")

    issues = sorted(set(issues))
    return {
        "schema": SCHEMA,
        "status": "SOURCE_BOUND_DENIAL_ONLY" if not issues else "BLOCKED",
        "blocking_codes": issues,
        "required_review_codes": list(REQUIREMENTS),
        "source_core2_admitted": False,
        "new_unseen_item_provisioned": False,
        "first_unassisted_attempt_verified": False,
        "semantic_math_review_accepted": False,
        "independent_mastery_verified": False,
        "academic_accepted": False,
        "release_authorized": False,
        "e3_receipt_not_cryptographic_attestation": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--golden", type=Path, required=True)
    parser.add_argument("--e3-receipt", type=Path, required=True)
    parser.add_argument("--safe-output", type=Path, required=True)
    parser.add_argument("--require-independent-acceptance", action="store_true",
                        help="Explicit always-deny check; no trusted adjudication available.")
    args = parser.parse_args(argv)
    paths = {
        "manifest": args.manifest, "package": args.package,
        "golden": args.golden, "e3_receipt": args.e3_receipt
    }
    try:
        data = {k: json.loads(p.read_text(encoding="utf-8"))
                for k, p in paths.items()}
        digest = {k: sha(p) for k, p in paths.items()}
        if any(not HEX64.fullmatch(x) for x in digest.values()):
            raise ValueError("digest-invalid")
        result = observe(data["manifest"], data["package"],
                         data["golden"], data["e3_receipt"])
    except (OSError, ValueError, UnicodeError, TypeError):
        digest = {}
        result = observe(None, None, None, None)
        result["blocking_codes"] = sorted(set(
            result["blocking_codes"] + ["E3_F04_INPUT_UNREADABLE"]))
        result["status"] = "BLOCKED"
    result["source_sha256"] = digest
    if args.safe_output.parent != Path("build") and "build" not in args.safe_output.parts:
        print("E3_F04_OUTPUT_LOCATION_UNSAFE; RELEASE_HOLD")
        return 1
    args.safe_output.parent.mkdir(parents=True, exist_ok=True)
    args.safe_output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("E3_F04_HELD_SOURCE_OBSERVER_" + (
        "PASS" if not result["blocking_codes"] else "BLOCKED"
    ) + "; UNSEEN_UNASSISTED_TRANSFER_NOT_ESTABLISHED; ACADEMIC_RELEASE_HOLD")
    return 1 if result["blocking_codes"] or args.require_independent_acceptance else 0


if __name__ == "__main__":
    raise SystemExit(main())
