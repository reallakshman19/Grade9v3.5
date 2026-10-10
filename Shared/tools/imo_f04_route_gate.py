"""Read-only F04 learner-route gate, runnable without GitHub Actions or a renderer.

Input must be the sanitized local summary from imo_f04_canonical_slice.py.
A structural route pass is never academic, accessibility, transfer, source or release approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "agent3-imo-f04-canonical-vertical-slice/v1"
REQUIRED_ROUTES = frozenset({
    "CORE1A_STEP_FRAGMENT_NOT_ADDRESSABLE",
    "CORE2A_NOT_LINKED_TO_EXACT_REPAIR_STEP",
    "CORE1A_AUTHORED_CORE2A_RETURN_ABSENT",
    "CORE1A_REPAIR_STEP_DOM_ID_NOT_UNIQUE",
    "CORE2A_REPAIR_HELP_NAVIGATION_UNBOUND",
    "CORE1A_AUTHORED_RETURN_WRONG_CONCEPT",
    "CORE1A_AUTHORED_RETURN_BYPASSES_CONCEPT_GATE",
    "CORE2A_HELP_RUNTIME_NOT_RENDERED",
    "CORE2A_HELP_RUNTIME_STATIC_UNVERIFIED",
    "CORE2A_HELP_ASSISTANCE_ROLE_EXCLUDED",
    "CORE2A_HELP_PERSISTENCE_ROLE_EXCLUDED",
    "CORE2A_HELP_RESTORE_ROLE_EXCLUDED",
    "CORE2A_HELP_LOCAL_TRACE_INCOMPLETE",
})
REQUIRED_BLUEPRINTS = {
    "CORE1A": "BP-CORE1A-CONSTRUCTION@1.8.0",
    "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
}


def verdict(report: object) -> tuple[bool, str]:
    """Return safe reason code only: never echo raw author/learner data."""
    if not isinstance(report, dict) or report.get("schema") != SCHEMA:
        return False, "INVALID_SAFE_SUMMARY_SCHEMA"
    if report.get("release_authorized") is not False:
        return False, "RELEASE_STATUS_UNSAFE"
    if report.get("source_contract_status") != "HOLD_NOT_ACCEPTED":
        return False, "SOURCE_ACADEMIC_HOLD_MISSING"
    if report.get("qrt_cell") != "QRT-MODEL-D3":
        return False, "QRT_SOURCE_DRIFT"
    if report.get("blueprint_refs") != REQUIRED_BLUEPRINTS:
        return False, "BLUEPRINT_SOURCE_DRIFT"
    blocks = report.get("blocking_findings")
    if not isinstance(blocks, list) or blocks:
        return False, "CANONICAL_BLOCKING_FINDINGS_PRESENT"
    if report.get("render_status") != "REAL_CANONICAL_TEST_RENDER":
        return False, "NO_VALID_CANONICAL_TEST_RENDER"
    issues = report.get("integration_findings")
    if not isinstance(issues, list) or any(not isinstance(x, str) for x in issues):
        return False, "MISSING_OR_UNSAFE_ROUTE_DIAGNOSTIC"
    if issues:
        if any(x not in REQUIRED_ROUTES for x in issues):
            return False, "MISSING_OR_UNSAFE_ROUTE_DIAGNOSTIC"
        return False, "ROUTE_FINDINGS:" + ",".join(sorted(set(issues)))
    if report.get("state") not in {"INTEGRATION_GAPS_HELD", "EVIDENCE_READY_REVIEW_HOLD"}:
        return False, "UNEXPECTED_F04_PRODUCT_STATE"
    return True, "ROUTE_STRUCTURE_ONLY_NO_LEARNER_ACCEPTANCE"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        print("F04_ROUTE_BLOCKED: UNREADABLE_SAFE_SUMMARY")
        return 1
    accepted, reason = verdict(summary)
    if not accepted:
        print("F04_ROUTE_BLOCKED: " + reason)
        return 1
    print("F04_ROUTE_STRUCTURE_OK; ACADEMIC_QRT_BROWSER_LEARNER_RELEASE_HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
