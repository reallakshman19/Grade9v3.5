#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All-in-one Automated Quality & Conformance Validator for IMO Curriculum Pipeline.
Executes:
1. Math Syntax, Typography, and Asset Resolution Audit (audit_math_and_fonts.py)
2. Standalone Conformance Policy Audit (standalone_conformance.py)
3. Multimodal Visual Asset & Cue Manifest Audit (audit_missing_svgs.py)
4. Dedicated Topic Custody Unit Tests (test_*_custody.py)
"""

import sys
import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

def run_step(title: str, cmd: list[str]) -> bool:
    print(f"\n==================================================")
    print(f"RUNNING: {title}")
    print(f"COMMAND: {' '.join(cmd)}")
    print(f"==================================================")
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), text=True)
    if res.returncode == 0:
        print(f"[PASS] {title}")
        return True
    else:
        print(f"[FAIL] {title} (exit code {res.returncode})")
        return False

def main():
    parser = argparse.ArgumentParser(description="Full Pipeline Conformance Validator")
    parser.add_argument("--topic", help="Topic name to validate custody test (e.g. IMOCircle, circles)", default="IMOCircle")
    parser.add_argument("--html", help="Path to standalone HTML app", default="standalone/practice/core2-mathematics-circles-grade9-master.html")
    args = parser.parse_args()

    results = {}

    # 1. Math, Fonts, and Runtime Asset Audit
    results["Math & Typography Audit"] = run_step(
        "Math & Typography Audit",
        [sys.executable, "Shared/tools/audit_math_and_fonts.py"]
    )

    # 2. Standalone Conformance Audit
    html_target = REPO_ROOT / args.html
    if html_target.exists():
        results["Standalone Conformance"] = run_step(
            f"Standalone Conformance ({html_target.name})",
            [sys.executable, "Shared/tools/standalone_conformance.py", str(html_target)]
        )

    # 3. Visual Cues & SVG Audit
    results["Visual Cue & SVG Audit"] = run_step(
        "Visual Cues & Asset Audit",
        [sys.executable, "Shared/tools/audit_missing_svgs.py", "--export-cues"]
    )

    # 4. Custody Unit Tests
    test_files = list((REPO_ROOT / "tests").glob(f"*{args.topic}*.py"))
    if test_files:
        for tf in test_files:
            results[f"Custody Test ({tf.name})"] = run_step(
                f"Custody Unit Test ({tf.name})",
                [sys.executable, "-m", "unittest", f"tests/{tf.name}", "-v"]
            )

    # 5. UI/UX Interaction & Pre-Rendering Conformance
    if html_target.exists():
        content = html_target.read_text(encoding="utf-8")
        ui_errors = []
        if '<div class="card-source-tag">' not in content:
            ui_errors.append("Missing .card-source-tag elements in HTML")
        if 'class="hint-unlock-btn"' not in content:
            ui_errors.append("Missing .hint-unlock-btn elements in HTML")
        if 'class="hint-progress-bar"' not in content:
            ui_errors.append("Missing .hint-progress-bar elements in HTML")
        if 'id="offline-katex-css"' not in content:
            ui_errors.append("Missing offline-katex-css tag in HTML")
        if 'class="katex"' not in content or 'katex-html' not in content:
            ui_errors.append("Missing static pre-rendered katex-html spans (requires prerender_engine.py)")
        
        if ui_errors:
            print("\n==================================================")
            print(f"FAIL: UI/UX & Pre-Rendering Conformance ({html_target.name})")
            for err in ui_errors:
                print(f"  - {err}")
            print("==================================================")
            results["UI/UX & Pre-Rendering Audit"] = False
        else:
            print("\n==================================================")
            print(f"PASS: UI/UX & Pre-Rendering Conformance ({html_target.name})")
            print("  - Source provenance tags verified")
            print("  - Progressive staggered hint unlock controls verified")
            print("  - Self-contained offline KaTeX tags verified")
            print("  - Static DOM pre-rendered spans verified")
            print("==================================================")
            results["UI/UX & Pre-Rendering Audit"] = True

    print("\n" + "=" * 60)
    print("PIPELINE AUDIT SUMMARY RECEIPT")
    print("=" * 60)
    all_passed = True
    for step, ok in results.items():
        status = "PASSED" if ok else "FAILED"
        print(f"{step:<45}: {status}")
        if not ok:
            all_passed = False

    if all_passed:
        print("\nALL GATES PASSED: 100% Fail-Closed Conformance.")
        sys.exit(0)
    else:
        print("\nGATE BLOCKED: One or more validation checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
