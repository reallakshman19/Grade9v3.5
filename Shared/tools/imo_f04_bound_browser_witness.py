"""Observer-only F04 same-run render/Chromium evidence preflight (TEST).

This verifies fixed local inputs and hashes after a workflow has *actually*
invoked the canonical renderer and F02's Chromium harness. It cannot
cryptographically attest browser execution, academic quality, learner
understanding, authentic SOF custody, accessibility, or release readiness.
Protected canonical audit details must stay local; stdout is fixed-code/digest
metadata only. Never ship original W, hints, answers, or learner text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from Shared.tools.imo_f04_browser_receipt_gate import findings as browser_findings

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path("TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json")
PACKAGE = Path("TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json")
HTML = ("core1a.html", "core2a.html", "index.html")
WIDTHS = (320, 390, 768, 1280)
SHA = re.compile(r"[0-9a-f]{40}\Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    repo: Path,
    render_dir: Path,
    canonical_audit: Path,
    expected_sha: str,
    actual_sha: str,
) -> dict:
    """Use only fixed public reason codes; no raw input or error strings."""
    problems: list[str] = []
    hashes: dict[str, object] = {"html": {}, "screenshots": {}}
    if not SHA.fullmatch(expected_sha or "") or actual_sha != expected_sha:
        problems.append("CHECKOUT_SHA_MISMATCH")

    for key, name in (("manifest", MANIFEST), ("package", PACKAGE)):
        path = repo / name
        try:
            hashes[key] = digest(path)
        except OSError:
            problems.append("SOURCE_INPUT_MISSING")

    page_hashes = hashes["html"]
    for name in HTML:
        try:
            page_hashes[name] = digest(render_dir / name)
        except OSError:
            problems.append("RENDERED_HTML_MISSING")

    receipt_file = render_dir / "render-receipt.json"
    try:
        receipt = load(receipt_file)
        hashes["render_receipt"] = digest(receipt_file)
        if not isinstance(receipt, dict) or (
            receipt.get("output_roles") != ["CORE1A", "CORE2A"]
            or receipt.get("mode") != "PAGES"
            or receipt.get("held_to") != "REFERENCE"
            or receipt.get("gaps")
        ):
            problems.append("RENDER_RECEIPT_INVALID")
    except (OSError, ValueError, UnicodeError):
        problems.append("RENDER_RECEIPT_UNREADABLE")

    try:
        audit = load(canonical_audit)
        if not isinstance(audit, dict):
            raise ValueError("invalid type")
        render = audit.get("render")
        source_match = (
            audit.get("manifest_sha256") == hashes.get("manifest")
            and audit.get("package_sha256") == hashes.get("package")
        )
        page_match = (
            isinstance(render, dict)
            and render.get("status") == "REAL_CANONICAL_TEST_RENDER"
            and render.get("index_sha256") == page_hashes.get("index.html")
            and isinstance(render.get("pages"), dict)
            and all(
                isinstance(render["pages"].get(role), dict)
                and render["pages"][role].get("sha256") == page_hashes.get(name)
                for role, name in (("CORE1A", "core1a.html"), ("CORE2A", "core2a.html"))
            )
        )
        authority_safe = (
            audit.get("release_authorized") is False
            and audit.get("academic_accepted") is False
            and audit.get("source_core2_eligible") is False
            and audit.get("browser_qa") == "NOT_RUN"
        )
        if not source_match or not page_match:
            problems.append("INDEPENDENT_CANONICAL_DIGEST_MISMATCH")
        if not authority_safe:
            problems.append("CANONICAL_AUTHORITY_UNSAFE")
        if (audit.get("blocking_findings") != [] or not isinstance(render, dict)
                or render.get("navigation_findings") != []):
            problems.append("CANONICAL_RENDER_BLOCKED")
    except (OSError, ValueError, UnicodeError):
        problems.append("CANONICAL_AUDIT_UNREADABLE")

    browser_root = render_dir / "browser-evidence"
    browser_receipt = browser_root / "result.json"
    try:
        browser_data = load(browser_receipt)
        hashes["browser_receipt"] = digest(browser_receipt)
        problems.extend(browser_findings(browser_data))
    except (OSError, ValueError, UnicodeError):
        problems.append("BROWSER_RECEIPT_UNREADABLE")

    for width in WIDTHS:
        file = browser_root / f"core1a-{width}.png"
        try:
            if file.stat().st_size < 1000:
                raise ValueError("small")
            hashes["screenshots"][str(width)] = digest(file)
        except (OSError, ValueError):
            problems.append("BROWSER_SCREENSHOT_MISSING_OR_INVALID")
    try:
        pdf = browser_root / "core1a-print.pdf"
        if pdf.stat().st_size < 1000:
            raise ValueError("small")
        hashes["browser_pdf"] = digest(pdf)
    except (OSError, ValueError):
        problems.append("BROWSER_PRINT_PDF_MISSING_OR_INVALID")

    codes = sorted(set(problems))
    return {
        "schema": "imo-f04-same-run-browser-provenance/v1",
        "checkout_sha": expected_sha if SHA.fullmatch(expected_sha or "") else "INVALID",
        "verification": "STRUCTURAL_SAME_RUN_SHA_CHAIN_ONLY",
        "browser_execution_attested": False,
        "browser_run_by_workflow": "MUST_BE_VERIFIED_FROM_ACTIONS_STEPS",
        "academic_accepted": False,
        "source_core2_admitted": False,
        "learner_mastery_verified": False,
        "release_authorized": False,
        "status": "LOCAL_EVIDENCE_CHAIN_PRESENT_NOT_ACCEPTANCE" if not codes else "BLOCKED",
        "blocking_codes": codes,
        "sha256": hashes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--canonical-audit", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--safe-summary", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        actual = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        actual = "NO_GIT_CHECKOUT"
    result = evaluate(ROOT, args.render_dir, args.canonical_audit,
                      args.expected_sha, actual)
    # Public summary contains only fixed code identifiers and SHA-256 digests;
    # raw source, browser failures or protected F02 responses are excluded.
    args.safe_summary.parent.mkdir(parents=True, exist_ok=True)
    args.safe_summary.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                                 encoding="utf-8")
    print("F04_SAME_RUN_SHA_CHAIN_" + ("PRESENT" if not result["blocking_codes"] else "BLOCKED")
          + "; ACADEMIC_SOURCE_LEARNER_RELEASE_HOLD")
    return 1 if result["blocking_codes"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
