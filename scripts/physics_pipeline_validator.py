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
    
    # Explicit QRT contract adapter declaration
    qrt = q.get("qrt_contract", {})
    for explicit_key in qrt.get("topic_adapters", []):
        if explicit_key in adapters:
            return explicit_key, adapters[explicit_key]
    explicit_key = qrt.get("topic_adapter_key")
    if explicit_key in adapters:
        return explicit_key, adapters[explicit_key]

    # Specific QID prefix matches (highest precedence for question identity)
    if "phys-plane" in qid:
        if "motion-in-a-plane" in adapters:
            return "motion-in-a-plane", adapters["motion-in-a-plane"]
    if "phys-vec" in qid:
        if "vectors-and-components" in adapters:
            return "vectors-and-components", adapters["vectors-and-components"]
    if "phys-grav" in qid:
        if "gravitation-orbital-motion" in adapters:
            return "gravitation-orbital-motion", adapters["gravitation-orbital-motion"]
    if "phys-fluid" in qid:
        if "fluids-hydrostatics" in adapters:
            return "fluids-hydrostatics", adapters["fluids-hydrostatics"]
    if "phys-thermo" in qid:
        if "heat-thermodynamics" in adapters:
            return "heat-thermodynamics", adapters["heat-thermodynamics"]
    if "phys-wep" in qid:
        if "work-energy-power" in adapters:
            return "work-energy-power", adapters["work-energy-power"]
    if "phys-kin" in qid:
        if "kinematics-1d-2d" in adapters:
            return "kinematics-1d-2d", adapters["kinematics-1d-2d"]
    if "phys-nlm" in qid or "nlm" in qid:
        if "mechanics-nlm" in adapters:
            return "mechanics-nlm", adapters["mechanics-nlm"]

    # Direct ID match in topic text
    for adapter_key, adapter in adapters.items():
        if adapter_key in q_topic or adapter.get("topic_id", "").lower() in q_topic:
            return adapter_key, adapter

    # Broader topic keyword fallback
    if any(k in q_topic for k in ["gravitat", "planetary", "kepler"]):
        if "gravitation-orbital-motion" in adapters:
            return "gravitation-orbital-motion", adapters["gravitation-orbital-motion"]
    if any(k in q_topic for k in ["fluid", "hydrostatic", "archimedes", "pascal", "buoyancy", "manometer"]):
        if "fluids-hydrostatics" in adapters:
            return "fluids-hydrostatics", adapters["fluids-hydrostatics"]
    if any(k in q_topic for k in ["heat", "thermo", "calorimetry"]):
        if "heat-thermodynamics" in adapters:
            return "heat-thermodynamics", adapters["heat-thermodynamics"]
    if any(k in q_topic for k in ["work, energy", "work-energy", "work energy"]):
        if "work-energy-power" in adapters:
            return "work-energy-power", adapters["work-energy-power"]
    if any(k in q_topic for k in ["motion-in-a-plane", "motion in a plane", "planar motion"]):
        if "motion-in-a-plane" in adapters:
            return "motion-in-a-plane", adapters["motion-in-a-plane"]
    if any(k in q_topic for k in ["kinematics", "projectile", "1d-motion", "2d-motion"]):
        if "kinematics-1d-2d" in adapters:
            return "kinematics-1d-2d", adapters["kinematics-1d-2d"]
    if "friction" in q_topic and "newton" not in q_topic:
        if "friction-thresholds" in adapters:
            return "friction-thresholds", adapters["friction-thresholds"]
    if any(k in q_topic for k in ["vector", "vectors"]):
        if "vectors-and-components" in adapters:
            return "vectors-and-components", adapters["vectors-and-components"]
    if any(k in q_topic for k in ["mechanics", "newton", "second-law", "third-law"]):
        if "mechanics-nlm" in adapters:
            return "mechanics-nlm", adapters["mechanics-nlm"]

    return None, None

def validate_question_bank(bank_path: str, adapters_path: str = "Physics/adapter/TopicAdapters.v1.json", strict_golden: bool = False):
    print(f"\n{'='*80}")
    print(f"MULTI-ENGINE VALIDATION: {bank_path}")
    print(f"Mode: {'STRICT GOLDEN BENCHMARK (Core 1A -> Core 2 Contract)' if strict_golden else 'STANDARD VALIDATION'}")
    print(f"{'='*80}")
    
    adapters = load_topic_adapters(adapters_path)
    if adapters:
        print(f"[INIT] Loaded {len(adapters)} Topic Adapters: {list(adapters.keys())}")
    
    with open(bank_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    if not questions:
        print("  FAIL: No questions found in bank.")
        return False
    
    errors = []
    warnings = []
    demand_counts = {}
    band_counts = {}
    topic_matched_counts = {}
    competency_counts = {}
    figure_count = 0
    prompt_reveal_count = 0
    reasoning_ladder_count = 0
    
    universal_diag_codes = {
        "CORRECT", "KEY_CONCEPT", "SIGN_CONVENTION_ERROR", "ALGEBRAIC_ARITHMETIC_ERROR", 
        "UNITS_CONVERSION_ERROR", "RECIPROCAL_ERROR", "FORMULA_MISAPPLICATION",
        "VECTOR_SCALAR_CONFUSION", "SINGLE_FORCE_NEGLECT", "INCORRECT_FORCE_RATIO"
    }
    
    for q in questions:
        qid = q.get("question_id", "UNKNOWN")
        
        # ----------------------------------------------------
        # GATE 1: Core Schema & Option Disjointness
        # ----------------------------------------------------
        for field in ["question_id", "subject", "grade", "topic", "provenance", "stem", "options", "correct_answer", "qrt_contract", "distractor_diagnostics", "progressive_hints", "model_proof", "independent_check"]:
            if field not in q:
                errors.append(f"{qid}: Missing required field '{field}'")
        
        opts = q.get("options", {})
        if len(opts) != 4:
            errors.append(f"{qid}: Options must have exactly 4 keys (A, B, C, D)")
        vals = list(opts.values())
        if len(set(vals)) != len(vals):
            errors.append(f"{qid}: Distractor options are not pairwise disjoint: {vals}")
            
        correct_ans = q.get("correct_answer")
        if correct_ans not in ["A", "B", "C", "D"]:
            errors.append(f"{qid}: correct_answer must be one of ['A', 'B', 'C', 'D'], got '{correct_ans}'")
            
        # ----------------------------------------------------
        # GATE 2: QRT Cognitive Contract
        # ----------------------------------------------------
        qrt = q.get("qrt_contract", {})
        demand = qrt.get("primary_demand")
        band = qrt.get("difficulty_band")
        demand_counts[demand] = demand_counts.get(demand, 0) + 1
        band_counts[band] = band_counts.get(band, 0) + 1
        
        valid_demands = ["RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"]
        if demand not in valid_demands:
            errors.append(f"{qid}: Invalid QRT primary_demand '{demand}'")
        if band not in ["D1", "D2", "D3", "D4"]:
            errors.append(f"{qid}: Invalid QRT difficulty_band '{band}'")
            
        if strict_golden:
            supporting = qrt.get("supporting_demands", [])
            for sd in supporting:
                if sd not in valid_demands:
                    errors.append(f"{qid}: Invalid supporting_demand '{sd}'")
            factors = qrt.get("difficulty_factors", {})
            if not factors:
                errors.append(f"{qid}: Missing difficulty_factors in qrt_contract")
            else:
                for fk, fv in factors.items():
                    if not (1 <= fv <= 4):
                        errors.append(f"{qid}: difficulty_factor '{fk}'={fv} out of range [1, 4]")
            if not qrt.get("protected_work_W"):
                errors.append(f"{qid}: Missing protected_work_W in qrt_contract")
            
        # ----------------------------------------------------
        # GATE 3: Topic Adapter & Subtopic Competency Map
        # ----------------------------------------------------
        adapter_key, adapter = resolve_adapter_for_question(q, adapters)
        if adapter_key:
            topic_matched_counts[adapter_key] = topic_matched_counts.get(adapter_key, 0) + 1
            
        subtopic_ref = q.get("subtopic_competency_ref") or qrt.get("subtopic_competency_ref")
        if not subtopic_ref:
            msg = f"{qid}: Missing subtopic_competency_ref (required for Cross-Core 1-to-1 transfer)"
            if strict_golden:
                errors.append(msg)
            else:
                warnings.append(msg)
        else:
            competency_counts[subtopic_ref] = competency_counts.get(subtopic_ref, 0) + 1
            if adapter and "subtopic_competency_map" in adapter:
                if subtopic_ref not in adapter["subtopic_competency_map"]:
                    errors.append(f"{qid}: subtopic_competency_ref '{subtopic_ref}' not found in adapter '{adapter_key}' competency map")
                elif strict_golden:
                    comp_obj = adapter["subtopic_competency_map"][subtopic_ref]
                    targets = comp_obj.get("core2_transfer_target", [])
                    if qid not in targets:
                        errors.append(f"{qid}: Question ID not registered in adapter '{adapter_key}' transfer targets for competency '{subtopic_ref}'")
                    
        # ----------------------------------------------------
        # GATE 4: Distractor Diagnostics
        # ----------------------------------------------------
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
                if opt_key == correct_ans:
                    if diag_type not in ["CORRECT", "KEY_CONCEPT"]:
                        errors.append(f"{qid}: Correct option {opt_key} has invalid diagnostic type '{diag_type}'")
                else:
                    if diag_type in ["CORRECT", "KEY_CONCEPT"]:
                        errors.append(f"{qid}: Distractor option {opt_key} marked erroneously as '{diag_type}'")
                        
        # ----------------------------------------------------
        # GATE 5: Prompt-Reveal Progressive Hint Ladder
        # ----------------------------------------------------
        hints = q.get("progressive_hints", [])
        if len(hints) != 3:
            errors.append(f"{qid}: Expected exactly 3 progressive hints, got {len(hints)}")
        else:
            has_prompt_reveal = True
            for idx, h in enumerate(hints, 1):
                if h.get("tier") != idx:
                    errors.append(f"{qid}: Hint tier mismatch at index {idx}")
                
                # Check prompt-reveal pair
                p_q = h.get("prompt_question") or h.get("prompt")
                r_t = h.get("reveal_text") or h.get("text")
                if not p_q:
                    has_prompt_reveal = False
                    if strict_golden:
                        errors.append(f"{qid}: Tier {idx} hint missing 'prompt_question' (active prompt before reveal)")
                if not r_t:
                    errors.append(f"{qid}: Tier {idx} hint missing 'reveal_text' or 'text'")
                    
            if has_prompt_reveal:
                prompt_reveal_count += 1
            elif not strict_golden:
                warnings.append(f"{qid}: Hints use legacy text format instead of Golden prompt-reveal pair")

        # ----------------------------------------------------
        # GATE 6: 5-Step Reasoning Ladder & Multi-Engine Verification
        # ----------------------------------------------------
        proof = q.get("model_proof", {})
        ladder = proof.get("reasoning_ladder")
        derivation = proof.get("derivation_steps", [])
        
        is_5step = False
        if isinstance(ladder, dict):
            req_stages = ["understand", "represent", "connect", "calculate", "interpret"]
            if all(k in ladder for k in req_stages):
                is_5step = True
        elif isinstance(derivation, list) and len(derivation) >= 3:
            # Check if derivation contains step tags or text coverage
            full_proof_text = " ".join(str(s) for s in derivation).lower()
            if any(k in full_proof_text for k in ["understand", "represent", "connect", "calculate", "interpret", "step 1", "step 2"]):
                is_5step = True
                
        if is_5step:
            reasoning_ladder_count += 1
        else:
            msg = f"{qid}: Model proof lacks 5-step reasoning ladder (UNDERSTAND -> REPRESENT -> CONNECT -> CALCULATE -> INTERPRET)"
            if strict_golden:
                errors.append(msg)
            else:
                warnings.append(msg)
                
        if not proof.get("final_expression"):
            errors.append(f"{qid}: Missing final_expression in model_proof")
            
        # Independent Checks
        check = q.get("independent_check", {})
        dim = check.get("dimensional_formula", "")
        if not dim:
            errors.append(f"{qid}: Missing dimensional_formula in independent_check")
        else:
            if not re.search(r'\[[^\]]+\]|dimensionless|scalar', dim, re.IGNORECASE):
                errors.append(f"{qid}: Invalid dimensional formula syntax: {dim}")
                
        limits = check.get("limiting_cases", [])
        if not limits or len(limits) < 2:
            errors.append(f"{qid}: Expected at least 2 limiting_cases in independent_check, got {len(limits)}")
        else:
            for l_idx, lc in enumerate(limits):
                exp = lc.get("expected") or lc.get("expected_outcome") or lc.get("result")
                if not lc.get("condition") or not exp:
                    errors.append(f"{qid}: Incomplete limiting case #{l_idx+1}")
                    
        # Tripartite checks
        if strict_golden:
            if not check.get("quick_check"):
                errors.append(f"{qid}: Missing quick_check in independent_check")
            if not check.get("watch_out"):
                errors.append(f"{qid}: Missing watch_out in independent_check")
            if not check.get("review_this_idea"):
                errors.append(f"{qid}: Missing review_this_idea Cross-Core link in independent_check")

        # ----------------------------------------------------
        # GATE 7: Figure SVG Quality & Typography Floor
        # ----------------------------------------------------
        fig = q.get("figure", {})
        if fig.get("has_figure"):
            figure_count += 1
            svg = fig.get("svg_code", "")
            if svg:
                fonts = [int(m) for m in re.findall(r'font-size[=:]\s*[\"\']?(\d+)', svg)]
                violating = [f for f in fonts if f < 14]
                if violating:
                    errors.append(f"{qid}: SVG font-size violation (<14px): {violating}")

    # Summary Report
    print(f"\n[SUMMARY METRICS]")
    print(f"  Total Questions: {len(questions)}")
    print(f"  Topic Adapter Bindings: {topic_matched_counts}")
    print(f"  Subtopic Competency Coverage: {len(competency_counts)} unique ({competency_counts})")
    print(f"  Demand Distribution: {demand_counts}")
    print(f"  Band Distribution: {band_counts}")
    print(f"  Visual Figures Count: {figure_count}")
    print(f"  Prompt-Reveal Hint Ladders: {prompt_reveal_count} / {len(questions)}")
    print(f"  5-Step Reasoning Ladders: {reasoning_ladder_count} / {len(questions)}")
    
    if warnings:
        print(f"\n[ADVISORY WARNINGS: {len(warnings)}]")
        for w in warnings[:8]:
            print(f"  - {w}")
        if len(warnings) > 8:
            print(f"  ... and {len(warnings) - 8} more warnings.")

    if errors:
        print(f"\n[FAIL: {len(errors)} ERRORS DETECTED]")
        for err in errors[:15]:
            print(f"  - {err}")
        if len(errors) > 15:
            print(f"  ... and {len(errors) - 15} more errors.")
        return False
        
    print("\n[PASS] Question Bank passed all verification gates!")
    return True

def validate_master_app(app_path: str, expected_q_count: int = 25):
    print(f"\n{'='*80}")
    print(f"MASTER TABLET APP VALIDATION: {app_path}")
    print(f"{'='*80}")
    
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
        fonts = [int(m) for m in re.findall(r'font-size[=:]\s*[\"\']?(\d+)', svg)]
        bad = [f for f in fonts if f < 14]
        if bad:
            errors.append(f"SVG #{idx} has font-size below 14px floor: {bad}")
    
    # Check touch targets >= 48px in CSS
    if "min-height: 48px" not in html and "min-height:48px" not in html and "height: 48px" not in html:
        errors.append("CSS touch target min-height 48px floor declaration missing.")
    
    # Check progressive hint ladder interactive elements
    if 'class="hint-unlock-btn"' not in html and 'hint-toggle' not in html and 'data-hint-idx' not in html:
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
    parser.add_argument("--strict-golden", action="store_true", help="Enforce strict Golden Benchmark standards (prompt-reveals, 5-step ladders, Cross-Core grounding)")
    args = parser.parse_args()
    
    success = True
    if args.bank:
        if not validate_question_bank(args.bank, args.adapters, strict_golden=args.strict_golden):
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
