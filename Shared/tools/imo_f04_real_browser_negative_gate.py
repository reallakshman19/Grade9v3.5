"""F04 fail-closed, privacy-safe structure gate for real Chromium negative probes.

A passed receipt is still a self-report, not an independent academic assessment,
browser attestation, authentic-source proof, learner mastery or release permission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "imo-f04-real-browser-negatives/v1"
FLAGS = frozenset({
    "inert_protected_template",
    "pre_attempt_repair_absent",
    "empty_attempt_no_event",
    "initial_attempt_event_only",
    "response_text_not_persisted",
    "post_attempt_repair_created",
    "corrupt_history_denied",
    "corrupt_history_not_overwritten",
    "forged_mastery_event_denied",
})


def findings(report: object, expected_html_sha256: str) -> list[str]:
    """Fixed denial codes only; never echo browser output or private responses."""
    if not isinstance(report, dict):
        return ["INVALID_BROWSER_NEGATIVE_RECEIPT"]
    issues = []
    if report.get("schema") != SCHEMA or report.get("source") != "TEST_AUTHORED_CORE2A":
        issues.append("WRONG_BROWSER_NEGATIVE_SCOPE")
    if (report.get("status") != "NEGATIVE_PROBES_OK"
            or report.get("blocking_codes") != []):
        issues.append("BROWSER_NEGATIVE_PROBES_NOT_CLEAR")
    flags = report.get("flags")
    if (not isinstance(flags, dict) or set(flags) != FLAGS
            or any(value is not True for value in flags.values())):
        issues.append("BROWSER_NEGATIVE_ASSERTIONS_MISSING")
    if (type(report.get("viewport_width")) is not int
            or report["viewport_width"] != 390):
        issues.append("BROWSER_NEGATIVE_VIEWPORT_INVALID")
    if (not isinstance(expected_html_sha256, str)
            or len(expected_html_sha256) != 64
            or report.get("core2a_sha256") != expected_html_sha256):
        issues.append("BROWSER_NEGATIVE_RENDER_IDENTITY_MISMATCH")
    if (report.get("chromium_execution_attested") is not False
            or report.get("authentic_core2_admitted") is not False
            or report.get("mastery_verified") is not False
            or report.get("academic_accepted") is not False
            or report.get("release_authorized") is not False):
        issues.append("BROWSER_NEGATIVE_UNSAFE_AUTHORITY")
    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--rendered-core2a", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        sha = hashlib.sha256(args.rendered_core2a.read_bytes()).hexdigest()
    except (OSError, ValueError, UnicodeError):
        print("F04_REAL_BROWSER_NEGATIVE_BLOCKED; UNREADABLE_EVIDENCE")
        return 1
    problems = findings(receipt, sha)
    if problems:
        print("F04_REAL_BROWSER_NEGATIVE_BLOCKED; " + ";".join(problems))
        return 1
    print("F04_REAL_BROWSER_NEGATIVE_STRUCTURE_OK; "
          "NOT_CRYPTOGRAPHIC_ATTESTATION; ACADEMIC_LEARNER_RELEASE_HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
