"""Safe structural preflight for F02's held TEST Chromium evidence receipt.

Never accepts academic/learner release or authentic source rights; a self-reported
JSON file is NOT cryptographically bound to source SHA, renderer output or browser.
Only static public denial codes are emitted; never echo error or page-error text.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "imo-f02-concept-first-chromium/v2"
WIDTHS = (320, 390, 768, 1280)
FOCUS = frozenset(("H3", "H4"))


def findings(data: object) -> list[str]:
    """Return only fixed, privacy-safe finding identifiers."""
    if not isinstance(data, dict):
        return ["BROWSER_RECEIPT_NOT_OBJECT"]
    errors: list[str] = []
    if data.get("schema") != SCHEMA or data.get("source") != "TEST_CANDIDATE":
        errors.append("BROWSER_RECEIPT_SOURCE_SCHEMA_INVALID")
    if (data.get("authentic_core2_admitted") is not False
            or data.get("mastery_verified") is not False
            or data.get("human_screen_reader") != "NOT_RUN"):
        errors.append("BROWSER_RECEIPT_AUTHORITY_CLAIM_UNSAFE")
    raw_failures = data.get("failures")
    if not isinstance(raw_failures, list) or raw_failures:
        errors.append("BROWSER_RECEIPT_RECORDED_FAILURE_OR_MALFORMED")
    viewports = data.get("viewports")
    if not isinstance(viewports, list) or len(viewports) != len(WIDTHS):
        errors.append("BROWSER_RECEIPT_VIEWPORT_COVERAGE_INCOMPLETE")
    else:
        actual = []
        for item in viewports:
            if not isinstance(item, dict) or type(item.get("width")) is not int:
                errors.append("BROWSER_RECEIPT_VIEWPORT_INVALID")
                continue
            actual.append(item["width"])
            if item.get("focus_after_check") not in FOCUS:
                errors.append("BROWSER_RECEIPT_FOCUS_UNVERIFIED")
            if item.get("page_errors") != []:
                errors.append("BROWSER_RECEIPT_PAGE_ERRORS_PRESENT")
            if item.get("note") != "TEST-only visible behavior; no learner comprehension claim":
                errors.append("BROWSER_RECEIPT_UNQUALIFIED_LEARNER_CLAIM")
        if actual != list(WIDTHS):
            errors.append("BROWSER_RECEIPT_VIEWPORT_COVERAGE_INCOMPLETE")
    svg = data.get("printed_svg")
    if not isinstance(svg, dict) or any((
        svg.get("found") is not True,
        type(svg.get("count")) is not int or svg["count"] != 3,
        type(svg.get("visible")) is not int or svg["visible"] != 3,
        svg.get("allInsideViewBox") is not True,
    )):
        errors.append("BROWSER_RECEIPT_PRINT_STAGES_UNVERIFIED")
    pdf = data.get("printed_pdf")
    if (not isinstance(pdf, dict)
            or type(pdf.get("bytes")) is not int or pdf["bytes"] <= 1000
            or pdf.get("status") != "GENERATED_NOT_MANUALLY_INSPECTED"):
        errors.append("BROWSER_RECEIPT_PDF_NOT_GENERATED")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        print("BROWSER_RECEIPT_UNREADABLE; LEARNER_ACCEPTANCE_NOT_GRANTED")
        return 1
    problems = findings(report)
    if problems:
        print(";".join(problems) + "; LEARNER_ACCEPTANCE_NOT_GRANTED")
        return 1
    print("BROWSER_RECEIPT_STRUCTURE_OK; EVIDENCE_UNBOUND_TO_HEAD; "
          "BROWSER_ACCEPTANCE_NOT_GRANTED; ACADEMIC_AND_RELEASE_HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
