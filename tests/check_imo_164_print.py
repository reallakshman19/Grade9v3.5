#!/usr/bin/env python3
"""Inspect *both* locked and solution-open real Chromium A4 PDFs.

A TEST-only evidence check, not human print/AT certification or source admission.
The question must print before commitment; its solution must not.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader

A4_WIDTH, A4_HEIGHT = 595.276, 841.890
PRINT_STATES = {
    "before": ("print_before", "core2b-A4-before-commit.pdf",
               "BEFORE_LEARNER_COMMIT_AND_SOLUTION_LOCKED"),
    "after": ("print", "core2b-A4-after-commit.pdf",
              "AFTER_LEARNER_COMMIT_AND_SOLUTION_OPEN"),
}
PROTECTED = {
    "five": ("Review and solution", "The deciding move", "gcd(24,5)"),
    "boundary": ("Review and solution", "The deciding move", "n mod 4"),
}


def printed_page(folder: Path, receipt: dict, stage: str, variant: str) -> tuple[int, str]:
    receipt_key, expected_name, state = PRINT_STATES[stage]
    entry = receipt.get(receipt_key)
    assert isinstance(entry, dict), (variant, stage, "missing print receipt")
    assert entry.get("state") == state, (variant, stage, "wrong print state")
    assert entry.get("format") == "A4", (variant, stage, "wrong print format")
    assert entry.get("status") == "PENDING_PDF_STRUCTURE_CHECK", (
        variant, stage, "wrong print evidence status")
    assert entry.get("path") == expected_name, (
        variant, stage, "unrecognized print evidence filename")
    file = folder / expected_name
    assert file.read_bytes().startswith(b"%PDF-"), (variant, stage, "PDF magic")
    reader = PdfReader(file)
    assert 1 <= len(reader.pages) <= 20, (variant, stage, len(reader.pages))
    for index, page in enumerate(reader.pages):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        assert abs(width-A4_WIDTH) < 2 and abs(height-A4_HEIGHT) < 2, (
            variant, stage, index, width, height)
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    assert len(text) > 100, (variant, stage, "too little extracted text", len(text))
    assert "divisib" in text.lower(), (variant, stage, "math stem absent from print")
    assert "SOF-IMO-G09-" not in text, (
        variant, stage, "unexpected publisher-source content")
    return len(reader.pages), text


def assert_print_boundary(variant: str, locked_text: str, open_text: str) -> None:
    """Negative acceptance: deny any protected solution marker before commit."""
    assert variant in PROTECTED, ("unknown review variant", variant)
    for marker in PROTECTED[variant]:
        assert marker not in locked_text, (
            variant, "PROTECTED_PRE_ATTEMPT_PRINT_LEAK", marker)
        assert marker in open_text, (
            variant, "MISSING_POST_ATTEMPT_SOLUTION", marker)


def negative_falsifiers() -> None:
    """A leak, even with a valid-looking receipt, must fail the assertion."""
    for variant, markers in PROTECTED.items():
        question = "Prove whether the consecutive product is divisible."
        solved = question + " " + " ".join(markers)
        assert_print_boundary(variant, question, solved)
        for marker in markers:
            try:
                assert_print_boundary(variant, question + " " + marker, solved)
            except AssertionError:
                pass
            else:
                raise AssertionError((variant, "falsifier failed to catch", marker))
        try:
            assert_print_boundary(variant, question, question)
        except AssertionError:
            pass
        else:
            raise AssertionError((variant, "missing postcommit proof went unnoticed"))


def check(folder: Path) -> dict:
    receipt = json.loads((folder / "browser-receipt.json").read_text())
    variant = receipt["variant"]
    assert variant in PROTECTED, variant
    assert receipt["status"] == "CANDIDATE_BROWSER_SMOKE"
    assert receipt["refresh"] == "CORE2B_FAILS_CLOSED_AND_REQUIRES_A_NEW_ATTEMPT"
    before_pages, before_text = printed_page(folder, receipt, "before", variant)
    after_pages, after_text = printed_page(folder, receipt, "after", variant)
    assert_print_boundary(variant, before_text, after_text)
    return {
        "variant": variant,
        "pages": after_pages,
        "before_pages": before_pages,
        "extracted_chars": len(after_text),
        "before_extracted_chars": len(before_text),
        "page_format": "A4",
        "before_status": "QUESTION_VISIBLE_PROTECTED_SOLUTION_ABSENT",
        "after_status": "EXPECTED_SOLUTION_PRESENT",
        "status": "STRUCTURE_AND_TEXT_PASS",
        "media_box_points": [A4_WIDTH, A4_HEIGHT],
        "before_path": PRINT_STATES["before"][1],
        "path": PRINT_STATES["after"][1],
    }


def main(argv: list[str]) -> None:
    assert len(argv) == 2, (
        "usage: check_imo_164_print.py <five-evidence> <boundary-evidence>")
    negative_falsifiers()
    out = [check(Path(folder)) for folder in argv]
    assert {x["variant"] for x in out} == {"five", "boundary"}, out
    for folder, row in zip(argv, out):
        (Path(folder) / "a4-print-validation.json").write_text(
            json.dumps(row, indent=2) + "\n")
    print("VERIFIED_A4_HELD_PDF", json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1:])
