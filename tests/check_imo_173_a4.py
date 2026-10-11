#!/usr/bin/env python3
"""Track A: inspect actual per-role Chromium A4 PDF bytes, not just print CSS.

Technical text/MediaBox check only. Human physical print remains NOT_RUN.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

FILES = {
    "core2a": "core2a-A4-preview.pdf",
    "core1a": "core1a-A4-preview.pdf",
    "core1b_before": "core1b-A4-before-commit.pdf",
    "core1b_after": "core1b-A4-after-commit.pdf",
}
A4 = (595.276, 841.890)
PROTECTED = "Three checks are instances"


def read_print(path: Path) -> dict:
    assert path.read_bytes().startswith(b"%PDF-"), (path, "not real Chromium PDF")
    pdf = PdfReader(path)
    assert 1 <= len(pdf.pages) <= 20, (path, len(pdf.pages))
    for n, page in enumerate(pdf.pages):
        bounds = (float(page.mediabox.width), float(page.mediabox.height))
        assert all(abs(actual - expected) < 2 for actual, expected in zip(bounds, A4)), (
            path, n, bounds, "not A4")
    text = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in pdf.pages))
    assert len(text) > 90, (path, len(text))
    assert "SOF-IMO-G09-" not in text, (path, "source exclusion")
    return {"pages": len(pdf.pages), "chars": len(text), "text": text}


def check(folder: Path) -> dict:
    receipt = json.loads((folder / "core1b-browser-receipt.json").read_text())
    assert receipt["human_acceptance"] == "NOT_RUN"
    assert receipt["status"] == "CANDIDATE_AUTOMATED_BROWSER_ONLY"
    assert len(receipt["checks"]) == 4 and all(
        r["status"] == "PASS_AUTOMATED" for r in receipt["checks"])
    for width in (320, 390, 768, 1280):
        for stage in ("before", "after"):
            assert (folder / f"core1b-{width}-{stage}.png").stat().st_size > 1000
    assert (folder / "core1b-200pct-proxy.png").stat().st_size > 1000
    printed = {role: read_print(folder / filename) for role, filename in FILES.items()}
    pre = printed["core1b_before"]["text"]
    post = printed["core1b_after"]["text"]
    assert "Boundary test" in pre, "Core1B boundary task not printed before commitment"
    assert PROTECTED not in pre, "CORE1B_PROTECTED_PDF_LEAK"
    assert PROTECTED in post, "Core1B post-attempt rubric closure absent"
    for role, info in printed.items():
        assert info["pages"] >= 1 and info["chars"] > 90, role
    return {"variant": receipt["variant"], "status": "STRUCTURAL_A4_CHECK_PASS",
            "human_print": "NOT_RUN", "academic": "NOT_ACCEPTED",
            "pdfs": {role: {"path": FILES[role], "pages": row["pages"],
                             "extracted_chars": row["chars"], "format": "A4"}
                     for role, row in printed.items()}}


def main(args: list[str]) -> None:
    assert len(args) == 2, "usage: check_imo_173_a4.py <five-evidence> <boundary-evidence>"
    reports = [check(Path(x)) for x in args]
    assert {r["variant"] for r in reports} == {"five", "boundary"}
    for dirname, row in zip(args, reports):
        (Path(dirname) / "a4-all-roles-validation.json").write_text(
            json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print("TRACK_A_ACTUAL_A4_AUTOMATED", json.dumps(reports))


if __name__ == "__main__":
    main(sys.argv[1:])
