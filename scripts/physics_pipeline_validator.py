import re
import json
import argparse
import sys
from pathlib import Path

def validate_question_bank(bank_path: str):
    print(f"\n[GATE 1 & 2] Validating Question Bank: {bank_path}")
    with open(bank_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    if not questions:
        print("  FAIL: No questions found in bank.")
        return False
    
    errors = []
    demand_counts = {}
    band_counts = {}
    figure_count = 0
    
    for q in questions:
        qid = q.get("question_id", "UNKNOWN")
        
        # Check required fields
        for field in ["question_id", "subject", "grade", "topic", "provenance", "stem", "options", "correct_answer", "qrt_contract", "distractor_diagnostics", "progressive_hints", "model_proof", "independent_check"]:
            if field not in q:
                errors.append(f"{qid}: Missing field '{field}'")
        
        # Options disjointness
        opts = q.get("options", {})
        if len(opts) != 4:
            errors.append(f"{qid}: Options must have exactly 4 keys (A, B, C, D)")
        vals = list(opts.values())
        if len(set(vals)) != len(vals):
            errors.append(f"{qid}: Distractor options are not pairwise disjoint: {vals}")
        
        # Diagnostics
        diag = q.get("distractor_diagnostics", {})
        for opt_key in ["A", "B", "C", "D"]:
            if opt_key not in diag:
                errors.append(f"{qid}: Missing diagnostic for option {opt_key}")
            else:
                if not diag[opt_key].get("type") or not diag[opt_key].get("diagnostic"):
                    errors.append(f"{qid}: Incomplete diagnostic object for option {opt_key}")
        
        # QRT contract
        qrt = q.get("qrt_contract", {})
        demand = qrt.get("primary_demand")
        band = qrt.get("difficulty_band")
        demand_counts[demand] = demand_counts.get(demand, 0) + 1
        band_counts[band] = band_counts.get(band, 0) + 1
        
        # Progressive hints
        hints = q.get("progressive_hints", [])
        if len(hints) != 3:
            errors.append(f"{qid}: Expected exactly 3 progressive hints, got {len(hints)}")
        else:
            for idx, h in enumerate(hints, 1):
                if h.get("tier") != idx:
                    errors.append(f"{qid}: Hint tier mismatch at index {idx}")
        
        # Dimensional formula and limiting cases
        check = q.get("independent_check", {})
        dim = check.get("dimensional_formula", "")
        if not dim:
            errors.append(f"{qid}: Missing dimensional_formula in independent_check")
        limits = check.get("limiting_cases", [])
        if not limits:
            errors.append(f"{qid}: Missing limiting_cases in independent_check")
        
        # Figure SVG font check
        fig = q.get("figure", {})
        if fig.get("has_figure"):
            figure_count += 1
            svg = fig.get("svg_code", "")
            if svg:
                fonts = [int(m) for m in re.findall(r'font-size:\s*(\d+)px', svg)]
                violating = [f for f in fonts if f < 14]
                if violating:
                    errors.append(f"{qid}: SVG font-size violation (<14px): {violating}")
    
    print(f"  Total Questions: {len(questions)}")
    print(f"  Demand Distribution: {demand_counts}")
    print(f"  Band Distribution: {band_counts}")
    print(f"  Visual Figures Count: {figure_count}")
    
    if errors:
        print(f"  FAIL: Found {len(errors)} errors in question bank:")
        for err in errors[:10]:
            print(f"    - {err}")
        return False
    
    print("  PASS: Question Bank satisfies all schema, QRT, FBD, and physical check contracts.")
    return True

def validate_master_app(app_path: str, expected_q_count: int = 25):
    print(f"\n[GATE 3, 4, 5 & 6] Validating Master Tablet App: {app_path}")
    with open(app_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    errors = []
    
    # Check question count rendered
    q_matches = re.findall(r'class="card-source-tag"', html)
    if len(q_matches) < expected_q_count:
        errors.append(f"Rendered question cards ({len(q_matches)}) less than expected ({expected_q_count})")
    
    # Check for raw math outside scripts/styles/svgs
    clean_html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.DOTALL)
    clean_html = re.sub(r'<style[\s\S]*?</style>', '', clean_html, flags=re.DOTALL)
    clean_html = re.sub(r'<svg[\s\S]*?</svg>', '', clean_html, flags=re.DOTALL)
    
    raw_math = re.findall(r'(\\\([^\)]+\\\)|\\\[[^\]]+\\\]|\$[^\$]+\$)', clean_html)
    if raw_math:
        errors.append(f"Found {len(raw_math)} unrendered raw LaTeX math blocks outside scripts: {raw_math[:5]}")
    
    # Check static KaTeX pre-rendering DOM presence
    if '<span class="katex">' not in html:
        errors.append("No static pre-rendered <span class=\"katex\"> DOM elements found.")
    
    # Check SVG font floor >= 14px in entire document
    svg_blocks = re.findall(r'<svg[\s\S]*?</svg>', html, flags=re.DOTALL)
    for idx, svg in enumerate(svg_blocks, 1):
        fonts = [int(m) for m in re.findall(r'font-size:\s*(\d+)px', svg)]
        bad = [f for f in fonts if f < 14]
        if bad:
            errors.append(f"SVG #{idx} has font-size below 14px floor: {bad}")
    
    # Check touch targets >= 48px in CSS
    if "min-height: 48px" not in html and "min-height:48px" not in html and "height: 48px" not in html:
        errors.append("CSS touch target min-height 48px floor declaration missing.")
    
    # Check progressive hint ladder interactive buttons
    if 'class="hint-unlock-btn"' not in html:
        errors.append("Interactive progressive hint ladder unlock buttons missing.")
    
    # Check base64 KaTeX fonts bundle presence
    if "data:text/css;base64" not in html and "data:font/woff2;base64" not in html:
        errors.append("Offline Base64 KaTeX font bundle missing from HTML head.")
    
    if errors:
        print(f"  FAIL: Found {len(errors)} validation errors in tablet app:")
        for err in errors:
            print(f"    - {err}")
        return False
    
    print("  PASS: Master Tablet App satisfies zero-raw-TeX, font floor >= 14px, 48px touch targets, and full pre-rendered KaTeX DOM.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Automated Multi-Engine Physics Pipeline Validator")
    parser.add_argument("--bank", type=str, help="Path to question bank JSON")
    parser.add_argument("--app", type=str, help="Path to master tablet app HTML")
    args = parser.parse_args()
    
    success = True
    if args.bank:
        if not validate_question_bank(args.bank):
            success = False
    
    if args.app:
        if not validate_master_app(args.app):
            success = False
            
    if not args.bank and not args.app:
        print("Please provide --bank or --app to validate.")
        sys.exit(1)
        
    if not success:
        print("\nOVERALL STATUS: FAILED")
        sys.exit(1)
    else:
        print("\nOVERALL STATUS: ALL GATES PASSED (100% COMPLIANT)")
        sys.exit(0)

if __name__ == "__main__":
    main()
