#!/usr/bin/env python3
"""Canonical Core1B held TEST preview generator; no answer bytes distributed."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "TEST/library/imo-g9-divisibility-core1a.v1.json"
OUTPUT = REPO / "public/test/imo-grade9/core1b.html"
SOURCE_GIT_BLOB = "cbcfe1ffe69b7453a53ca3608f5b563b0f91776e"
PACKAGE_ID = "TEST-IMO-G9-CORE1A-NS-DIVISIBILITY-PILOT"
MICROTOPIC_ID = "MIC-TEST-IMO-G9-CONSECUTIVE-FACTOR-INVARIANTS"

# Closed output: content is deliberately NOT interpolated from worked source.
HTML = "<!doctype html>\n<html lang=\"en\" data-g9-role=\"TEST\" data-g9-preview-core=\"CORE1B\" data-g9-canonical-acceptance=\"false\">\n<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<meta name=\"robots\" content=\"noindex,nofollow\"><title>Core1B · held TEST preview</title>\n<link rel=\"stylesheet\" href=\"../../css/modern-learner.css\"></head>\n<body><main><header><p>TEST ONLY · Academic/QRT HOLD · Not for publication</p>\n<h1>Core1B: build a reconstruction attempt</h1></header>\n<article data-g9-role=\"CORE1B\" data-g9-unit=\"MIC-TEST-IMO-G9-CONSECUTIVE-FACTOR-INVARIANTS\" data-g9-proof-custody=\"WITHHELD\">\n<p>Write a decision you would test and explain why that test might help. No official question or worked solution is included.</p>\n<label for=\"core1b-attempt\">Your own attempt</label><textarea id=\"core1b-attempt\" data-g9-attempt rows=\"6\"></textarea>\n<button type=\"button\" data-g9-commit>Record attempt</button>\n<p data-g9-status role=\"status\" aria-live=\"polite\">A nonempty attempt is required; the complete reconstruction is not distributed.</p>\n<p>The model answer remains withheld pending source-rights clearance and independent academic review.</p>\n</article><a href=\"../index.html\">Back to TEST</a></main>\n<script>\n(()=>{const a=document.querySelector('article[data-g9-role=\"CORE1B\"]');\nconst field=a.querySelector('[data-g9-attempt]'),status=a.querySelector('[data-g9-status]');\na.querySelector('[data-g9-commit]').addEventListener('click',()=>{\nif(!field.value.trim()){a.removeAttribute('data-attempted');\nstatus.textContent='Blank attempts are refused; no solution is revealed.';field.focus();return;}\na.dataset.attempted='1';status.textContent='Attempt recorded; the held reconstruction is not supplied by this TEST page.';});})();\n</script></body></html>\n"

def build(source: Path = SOURCE) -> bytes:
    data = source.read_bytes()
    blob = hashlib.sha1(
        ("blob " + str(len(data)) + "\0").encode("ascii") + data
    ).hexdigest()
    if blob != SOURCE_GIT_BLOB:
        raise ValueError("CORE1B_SOURCE_BLOB_DRIFT")
    package = json.loads(data)
    microtopics = package.get("microtopics")
    ext = package.get("extensions") or {}
    if (package.get("package_id") != PACKAGE_ID
        or package.get("status") != "CANDIDATE"
        or not isinstance(microtopics, list)
        or len(microtopics) != 1
        or microtopics[0].get("id") != MICROTOPIC_ID
        or ext.get("grade9v3:qrt_admitted") is not False
        or ext.get("grade9v3:learner_published") is not False):
        raise ValueError("CORE1B_SOURCE_REVIEW_HOLD_DRIFT")
    return HTML.encode("utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != expected:
            raise SystemExit("CORE1B_PUBLIC_GENERATION_STALE")
        print("CORE1B_PUBLIC_SOURCE_SAFE: PASS")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(expected)
        print("CORE1B_PUBLIC_GENERATED_FROM_HELD_SOURCE: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
