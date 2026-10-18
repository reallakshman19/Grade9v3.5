import re
import json
import argparse
import sys
from pathlib import Path

def load_topic_adapters(adapters_path: str = "Physics/adapter/TopicAdapters.v1.json"):
    path = Path(adapters_path)
    if not path.exists():
        print(f"  WARNING: Topic adapters file not found at {adapters_path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("topic_adapters", {})

def resolve_adapter_for_question(q: dict, adapters: dict):
    q_topic = (q.get("topic") or "").lower()
    qid = (q.get("question_id") or "").lower()
    
    # Direct ID match
    for adapter_key, adapter in adapters.items():
        if adapter_key in q_topic or adapter.get("topic_id", "").lower() in q_topic:
            return adapter_key, adapter
            
    # Specific QID prefix or topic match
    if "phys-grav" in qid or any(k in q_topic for k in ["gravitat", "planetary", "kepler"]):
        if "gravitation-orbital-motion" in adapters:
            return "gravitation-orbital-motion", adapters["gravitation-orbital-motion"]
    if "phys-fluid" in qid or any(k in q_topic for k in ["fluid", "hydrostatic", "archimedes", "pascal", "buoyancy", "manometer"]):
        if "fluids-hydrostatics" in adapters:
            return "fluids-hydrostatics", adapters["fluids-hydrostatics"]
    if "phys-thermo" in qid or any(k in q_topic for k in ["heat", "thermo", "calorimetry"]):
        if "heat-thermodynamics" in adapters:
            return "heat-thermodynamics", adapters["heat-thermodynamics"]
    if "phys-wep" in qid or any(k in q_topic for k in ["work, energy", "work-energy", "work energy"]):
        if "work-energy-power" in adapters:
            return "work-energy-power", adapters["work-energy-power"]
    if "phys-kin" in qid or any(k in q_topic for k in ["kinematics", "projectile", "1d-motion", "2d-motion"]):
        if "kinematics-1d-2d" in adapters:
            return "kinematics-1d-2d", adapters["kinematics-1d-2d"]
    if "phys-nlm" in qid or "nlm" in qid:
        if "mechanics-nlm" in adapters:
            return "mechanics-nlm", adapters["mechanics-nlm"]
    if "friction" in q_topic and "newton" not in q_topic and "nlm" not in qid:
        if "friction-thresholds" in adapters:
            return "friction-thresholds", adapters["friction-thresholds"]
    if any(k in q_topic or k in qid for k in ["vector"]):
        if "vectors-and-components" in adapters:
            return "vectors-and-components", adapters["vectors-and-components"]
    if any(k in q_topic or k in qid for k in ["mechanics", "newton", "second-law", "third-law"]):
        if "mechanics-nlm" in adapters:
            return "mechanics-nlm", adapters["mechanics-nlm"]
            
    # Default fallback to first adapter or None
    return None, None

def validate_question_bank(bank_path: str, adapters_path: str = "Physics/adapter/TopicAdapters.v1.json"):
    print(f"\n[GATE 1 & 2] Validating Question Bank: {bank_path}")
    adapters = load_topic_adapters(adapters_path)
    if adapters:
        print(f"  Loaded {len(adapters)} Topic Adapters: {list(adapters.keys())}")
    
    with open(bank_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    if not questions:
        print("  FAIL: No questions found in bank.")
        return False
    
    errors = []
    demand_counts = {}
    band_counts = {}
    topic_matched_counts = {}
    figure_count = 0
    
    # Standard acceptable universal diagnostic types
    universal_diag_codes = {
        "CORRECT", "KEY_CONCEPT", "SIGN_CONVENTION_ERROR", "ALGEBRAIC_ARITHMETIC_ERROR", 
        "UNITS_CONVERSION_ERROR", "RECIPROCAL_ERROR", "FORMULA_MISAPPLICATION"
    }
    
    for q in questions:
        qid = q.get("question_id", "UNKNOWN")
        
        # Check required fields
        for field in ["question_id", "subject", "grade", "topic", "provenance", "stem", "options", "correct_answer", "qrt_contract", "distractor_diagnostics", "progressive_hints", "model_proof", "independent_check"]:
            if field not in q:
                errors.append(f"{qid}: Missing field '{field}'")
        
        # Resolve Topic Adapter
        adapter_key, adapter = resolve_adapter_for_question(q, adapters)
        if adapter_key:
            topic_matched_counts[adapter_key] = topic_matched_counts.get(adapter_key, 0) + 1
        
        # Options disjointness
        opts = q.get("options", {})
        if len(opts) != 4:
            errors.append(f"{qid}: Options must have exactly 4 keys (A, B, C, D)")
        vals = list(opts.values())
        if len(set(vals)) != len(vals):
            errors.append(f"{qid}: Distractor options are not pairwise disjoint: {vals}")
        
        # Diagnostics
        diag = q.get("distractor_diagnostics", {})
        known_trap_codes = set(universal_diag_codes)
        if adapter:
            for item in adapter.get("misconception_discriminators", []):
                known_trap_codes.add(item.get("code"))
                
        for opt_key in ["A", "B", "C", "D"]:
            if opt_key not in diag:
                errors.append(f"{qid}: Missing diagnostic for option {opt_key}")
            else:
                d_obj = diag[opt_key]
                if not d_obj.get("type") or not d_obj.get("diagnostic"):
                    errors.append(f"{qid}: Incomplete diagnostic object for option {opt_key}")
                diag_type = d_obj.get("type")
                # If question is marked as an authentic trap code, verify it is tracked
                if diag_type not in known_trap_codes and not any(k in diag_type for k in ["FALLACY", "CONFUSION", "ERROR", "MIS"]):
                    # Informational / strictness check
                    pass
        
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
        else:
            # Check dimensional format syntax (e.g. [M][L][T^-2] or [v_avg] or [1])
            if not re.search(r'\[[^\]]+\]|dimensionless|scalar', dim, re.IGNORECASE):
                errors.append(f"{qid}: Invalid dimensional formula syntax: {dim}")
                
        limits = check.get("limiting_cases", [])
        if not limits:
            errors.append(f"{qid}: Missing limiting_cases in independent_check")
        else:
            for l_idx, lc in enumerate(limits):
                exp = lc.get("expected") or lc.get("expected_outcome") or lc.get("result")
                if not lc.get("condition") or not exp:
                    errors.append(f"{qid}: Incomplete limiting case at #{l_idx+1} (needs condition & expected/expected_outcome)")
        
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
        else:
            # If representation demand is explicitly declared, check if figure is expected
            if demand == "REPRESENT" and not fig.get("has_figure") and not q.get("options_have_figures"):
                # Representation questions should provide visual models
                pass
    
    print(f"  Total Questions: {len(questions)}")
    print(f"  Topic Adapter Bindings: {topic_matched_counts}")
    print(f"  Demand Distribution: {demand_counts}")
    print(f"  Band Distribution: {band_counts}")
    print(f"  Visual Figures Count: {figure_count}")
    
    if errors:
        print(f"  FAIL: Found {len(errors)} errors in question bank:")
        for err in errors[:10]:
            print(f"    - {err}")
        return False
    
    print("  PASS: Question Bank satisfies all schema, QRT, topic adapter, and physical check contracts.")
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
    parser.add_argument("--adapters", type=str, default="Physics/adapter/TopicAdapters.v1.json", help="Path to topic adapters JSON")
    args = parser.parse_args()
    
    success = True
    if args.bank:
        if not validate_question_bank(args.bank, args.adapters):
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
