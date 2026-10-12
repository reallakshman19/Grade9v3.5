#!/usr/bin/env python3
"""F02 E3 held-only source preflight. No learner mastery, identity, or credit authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
GOLDEN = ROOT / "TEST/imo-research/golden/imo-327-model-d3.v1.json"
SELECTED = "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01"
MICROTOPIC = "MIC-TEST-IMO-G9-COMMON-BASE-RELATION"
EXPOSED_EXIT = "CORE1A_DECLARED_EXIT"
EXPOSED_GOLDEN = "GOLDEN_REVIEW_FRESH_EXIT"
REVIEW_REQUIREMENTS = (
    "NEW_ITEM_CUSTODY_AND_UNSEENNESS_INDEPENDENTLY_VERIFIED",
    "FIRST_UNAIDED_ATTEMPT_AUTHENTICATED_WITH_DISCLOSURE_CHRONOLOGY",
    "SOURCE_BOUND_MATH_REASONING_RUBRIC_INDEPENDENTLY_ADJUDICATED",
    "MISCONCEPTION_VERSUS_EXECUTION_SLIP_HUMAN_REVIEW",
    "H_S_P_M_SEMANTIC_REVIEW_AND_OWNER_APPROVAL",
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _result(errors: list[str], findings: list[str]) -> dict:
    """Never copy raw learner-provided content, even for denied claims."""
    return {
        "schema": "imo-f02-e3-held-transfer-preflight/v1",
        "subject": "TEST",
        "assessment_status": "REVIEW_ONLY_HOLD_NOT_ACCEPTED",
        "independent_mastery_verified": False,
        "credit_eligible": False,
        "new_item_provisioned": False,
        "existing_assisted_target": SELECTED,
        "already_disclosed_probes": [EXPOSED_EXIT, EXPOSED_GOLDEN],
        "browser_local_trace_authority": "UNTRUSTED_NOT_CREDIT",
        "requirements": [{"code": code, "status": "INDEPENDENT_EVIDENCE_NOT_PROVIDED"}
                         for code in REVIEW_REQUIREMENTS],
        "errors": sorted(set(errors)),
        "findings": sorted(set(findings)),
    }


def preflight(manifest: object, package: object, golden: object,
              claim: object = None) -> dict:
    """Verify TEST boundaries and deny all untrusted independent-credit claims."""
    errors: list[str] = []
    if not all(isinstance(x, dict) for x in (manifest, package, golden)):
        return _result(["E3_SOURCE_OBJECT_MALFORMED"], ["E3_INDEPENDENT_EVIDENCE_NOT_ESTABLISHED"])
    selected, ext = manifest.get("selection"), package.get("extensions")
    if (manifest.get("subject") != "TEST" or manifest.get("output_roles") != ["CORE1A", "CORE2A"]
            or not isinstance(selected, dict) or selected.get("core2a") != [SELECTED]
            or selected.get("microtopics") != [MICROTOPIC]
            or selected.get("core2") != [] or selected.get("core2b") != []):
        errors.append("E3_MANIFEST_TRANSFER_OR_SOURCE_SELECTION_UNAUTHORIZED")
    if (package.get("subject") != "TEST" or package.get("status") != "CANDIDATE"
            or not isinstance(ext, dict)
            or any(ext.get(k) is not False for k in (
                "grade9v3:learner_published", "grade9v3:qrt_admitted",
                "grade9v3:core2_source_custody_granted"))):
        errors.append("E3_AUTHORING_OR_PUBLICATION_BOUNDARY_VIOLATED")
    questions, microtopics = package.get("questions"), package.get("microtopics")
    if (not isinstance(questions, list) or sum(
            isinstance(q, dict) and q.get("id") == SELECTED and q.get("origin") == "AUTHORED"
            for q in questions) != 1):
        errors.append("E3_SELECTED_AUTHORED_QUESTION_UNRESOLVED")
    exit_task = (microtopics[0].get("exit_task")
                 if isinstance(microtopics, list) and len(microtopics) == 1
                 and isinstance(microtopics[0], dict) else None)
    if (not isinstance(microtopics, list) or len(microtopics) != 1
            or not isinstance(microtopics[0], dict)
            or microtopics[0].get("id") != MICROTOPIC
            or not isinstance(exit_task, dict) or not isinstance(exit_task.get("prompt"), str)
            or not exit_task["prompt"].strip()):
        errors.append("E3_EXISTING_CORE1A_EXIT_UNRESOLVED")
    repair, governance = golden.get("core1a_repair"), golden.get("governance")
    stages = repair.get("sequence") if isinstance(repair, dict) else None
    if (golden.get("status") != "AUTHOR_REVIEW_FIXTURE_NOT_LEARNER_PRODUCT"
            or not isinstance(governance, dict) or governance.get("academic_review") != "NOT_GRANTED"
            or not isinstance(stages, list)
            or not any(isinstance(s, dict) and s.get("stage") == "FRESH_INDEPENDENT_EXIT"
                       and s.get("text") for s in stages)):
        errors.append("E3_GOLDEN_REVIEW_BOUNDARY_UNVERIFIED")
    findings = ["E3_INDEPENDENT_EVIDENCE_NOT_ESTABLISHED"]
    if claim is not None:
        if not isinstance(claim, dict):
            findings.append("E3_CLAIM_FORMAT_INVALID")
        else:
            item = claim.get("item_ref")
            if item == SELECTED:
                findings.append("E3_SAME_ASSISTED_QUESTION_IS_NOT_NEW_TRANSFER")
            elif item in (EXPOSED_EXIT, EXPOSED_GOLDEN):
                findings.append("E3_REPOSITORY_DISCLOSED_EXAMPLE_NOT_PROVEN_UNSEEN")
            else:
                findings.append("E3_UNRECOGNIZED_ITEM_NO_TRUSTED_CUSTODY_OR_UNSEENNESS")
            if claim.get("help_used") is True or claim.get("assisted") is True:
                findings.append("E3_ASSISTED_ATTEMPT_NOT_INDEPENDENT")
            if claim.get("source") == "F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1":
                findings.append("E3_EDITABLE_LOCAL_HISTORY_NOT_AUTHORITATIVE")
            else:
                findings.append("E3_EXTERNAL_ATTESTATION_UNVERIFIED")
            if claim.get("independent_mastery") is True or claim.get("award_credit") is True:
                findings.append("E3_UNAUTHORIZED_MASTERY_OR_CREDIT_CLAIM")
    return _result(errors, findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict-acceptance", action="store_true",
                        help="Always deny until a separate trusted academic process exists.")
    args = parser.parse_args(argv)
    try:
        report = preflight(read_json(MANIFEST), read_json(PACKAGE), read_json(GOLDEN))
    except (OSError, ValueError, UnicodeError, TypeError):
        report = _result(["E3_SOURCE_UNREADABLE"], ["E3_INDEPENDENT_EVIDENCE_NOT_ESTABLISHED"])
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print("E3_SOURCE_PREFLIGHT_" + ("PASS" if not report["errors"] else "FAIL")
          + "; INDEPENDENT_TRANSFER_NOT_PROVEN; ACADEMIC_AND_RELEASE_HOLD")
    return 1 if report["errors"] or args.strict_acceptance else 0


if __name__ == "__main__":
    raise SystemExit(main())
