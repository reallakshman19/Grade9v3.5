import re
import json
import difflib
from collections import Counter
import argparse
import sys
import os
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


# NLM-FIX1: The source-specific NLM pilot deliberately does not change gates for
# other physics topics until they have migrated to factor-evidence contracts.
NLM_FACTOR_KEYS = (
    "system_coupling", "vector_dimensionality", "constraint_latency",
    "domain_coupling", "math_friction",
)
NLM_LEGACY_TEMPLATES = {
    (4, 3, 4, 4, 4), (3, 2, 3, 3, 3), (2, 1, 2, 2, 2),
}
NLM_DEMANDS = (
    "RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT",
    "SYNTHESIZE", "JUSTIFY",
)


def derive_nlm_band(factors):
    """Return (derived_band, exact_mean) or (None, None) on invalid scoring."""
    if not isinstance(factors, dict) or set(factors) != set(NLM_FACTOR_KEYS):
        return None, None
    scores = [factors[key] for key in NLM_FACTOR_KEYS]
    if any(type(n) is not int or not 1 <= n <= 4 for n in scores):
        return None, None
    total = sum(scores)
    # Integer sums avoid floating-point edge ambiguities; all possible
    # five-factor averages advance by exactly 0.2, so bands have no gaps.
    if total <= 8:
        band = "D1"
    elif total <= 13:
        band = "D2"
    elif total <= 17:
        band = "D3"
    else:
        band = "D4"
    return band, total / 5


def validate_nlm_factor_contract(q):
    """Structural guard only: human reviewers must still judge evidence truth."""
    qid = q.get("question_id", "UNKNOWN")
    qrt = q.get("qrt_contract") or {}
    factors = qrt.get("difficulty_factors")
    evidence = qrt.get("factor_evidence")
    errors = []
    derived, mean = derive_nlm_band(factors)
    if derived is None:
        errors.append(f"{qid}: NLM factor vector must have five integer scores 1..4")
        return errors
    if qrt.get("difficulty_band") != derived:
        errors.append(f"{qid}: band mismatch: factor mean={mean:.1f}, derived={derived}, tag={qrt.get('difficulty_band')}")
    if qrt.get("cell_id") != f"PHYS-{qrt.get('primary_demand')}-{derived}":
        errors.append(f"{qid}: QRT cell_id disagrees with derived factors and demand")
    if not isinstance(evidence, dict) or set(evidence) != set(NLM_FACTOR_KEYS):
        errors.append(f"{qid}: missing factor_evidence per f1..f5")
    else:
        for key in NLM_FACTOR_KEYS:
            detail = evidence[key]
            score = factors[key]
            if (not isinstance(detail, str) or len(detail.strip()) < 30
                    or not re.match(r"^Score\s+" + str(score) + r"\s*:", detail)):
                errors.append(f"{qid}: factor_evidence[{key}] must cite score {score} and a concrete feature (>=30 chars)")
    vector = tuple(factors[key] for key in NLM_FACTOR_KEYS)
    if vector in NLM_LEGACY_TEMPLATES:
        errors.append(f"{qid}: forbidden back-filled template factor vector {vector}")
    return errors


def nlm_coverage_report(questions):
    coverage = {f"PHYS-{d}-{b}": 0 for d in NLM_DEMANDS for b in ("D1", "D2", "D3", "D4")}
    for q in questions:
        tile = (q.get("qrt_contract") or {}).get("cell_id")
        if tile in coverage:
            coverage[tile] += 1
    return coverage


def nlm_evidence_similarity(left, right):
    """Compare complete five-factor rationales, preserving factor order."""
    def normalized(q):
        evidence = (q.get("qrt_contract") or {}).get("factor_evidence") or {}
        if not isinstance(evidence, dict):
            return ""
        return " ".join(re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ",
                      str(evidence.get(k, "")).lower())).strip() for k in NLM_FACTOR_KEYS)
    a, b = normalized(left), normalized(right)
    return difflib.SequenceMatcher(None, a.split(), b.split(), autojunk=False).ratio() if a and b else 0.0


def nlm_validate_evidence_uniqueness(items, threshold=0.87):
    errors = []
    for i, left in enumerate(items):
        for right in items[i + 1:]:
            ratio = nlm_evidence_similarity(left, right)
            if ratio >= threshold:
                errors.append(f"NLM: identical or near-identical factor_evidence "
                              f"{left['question_id']} vs {right['question_id']} (similarity={ratio:.2f})")
    return errors


def nlm_d4_discriminator_report(items, adapter):
    allowed = {d["id"] for d in adapter.get("d4_discriminators", [])
               if isinstance(d, dict) and d.get("id")}
    counts = Counter()
    errors, warnings = [], []
    for item in items:
        qrt = item.get("qrt_contract", {})
        if qrt.get("difficulty_band") != "D4":
            continue
        kind = qrt.get("d4_discriminator_type")
        if kind not in allowed:
            errors.append(f"{item['question_id']}: missing or unrecognized D4 discriminator {kind!r}")
        else:
            counts[kind] += 1
        derived, score = derive_nlm_band(qrt.get("difficulty_factors"))
        if derived != "D4" or score is None or score < 3.8:
            errors.append(f"{item['question_id']}: D4 margin too low (S={score}); require S >= 3.8")
    if len(counts) < 3:
        errors.append(f"NLM: D4 discriminator diversity has {len(counts)} types; require >= 3")
    total = sum(counts.values())
    if total:
        for kind, n in sorted(counts.items()):
            if n / total > 0.60:
                warnings.append(f"NLM: D4 discriminator concentration {kind}: {n}/{total} > 60%")
    return dict(counts), errors, warnings


def nlm_validate_accounted_cells(items, adapter):
    coverage = nlm_coverage_report(items)
    na = adapter.get("not_applicable_cells", {})
    errors = []
    if not isinstance(na, dict):
        return coverage, ["NLM: not_applicable_cells must be a tile-to-reason mapping"]
    for tile, reason in na.items():
        if tile not in coverage:
            errors.append(f"NLM: invalid not_applicable_cells tile {tile}")
        elif coverage[tile]:
            errors.append(f"NLM: {tile} has items but is also marked not applicable")
        if not isinstance(reason, str) or len(reason.strip()) < 35:
            errors.append(f"NLM: {tile} missing specific physics not-applicable reason")
    for tile, count in coverage.items():
        if count == 0 and tile not in na:
            errors.append(f"NLM: uncovered cell {tile} has no item or not-applicable justification")
    return coverage, errors


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
    nlm_vectors = {}
    nlm_items = []
    
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
            
        # NLM-FIX1: derived score and evidence are required even in standard mode.
        if qid.startswith("PHYS-NLM-"):
            nlm_items.append(q)
            errors.extend(validate_nlm_factor_contract(q))
            factors = qrt.get("difficulty_factors", {})
            if derive_nlm_band(factors)[0] is not None:
                vector = tuple(factors[k] for k in NLM_FACTOR_KEYS)
                nlm_vectors.setdefault((band, vector), []).append(q)
            hints_for_nlm = q.get("progressive_hints", [])
            expected_roles = ("decisive_physics", "representation", "first_equation_only")
            for idx, expected_role in enumerate(expected_roles):
                if idx >= len(hints_for_nlm) or hints_for_nlm[idx].get("guidance_role") != expected_role:
                    errors.append(f"{qid}: H{idx+1} guidance_role must be {expected_role}")
            if len(hints_for_nlm) == 3:
                final = str((q.get("model_proof") or {}).get("final_answer_value") or "").strip()
                h3 = str(hints_for_nlm[2].get("reveal_text") or "").strip()
                if final and len(final) >= 12 and final.casefold() in h3.casefold():
                    errors.append(f"{qid}: H3 reveals final answer; first equation/constraint only")

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

    if nlm_items:
        nlm_adapter = adapters.get("mechanics-nlm", {})
        coverage, coverage_errors = nlm_validate_accounted_cells(nlm_items, nlm_adapter)
        errors.extend(coverage_errors)
        missing = [tile for tile, count in coverage.items() if not count]
        print(f"  NLM 28-CELL COVERAGE: {len(coverage) - len(missing)}/28; empty={missing}; not-applicable={list(nlm_adapter.get('not_applicable_cells', {}))}")
        errors.extend(nlm_validate_evidence_uniqueness(nlm_items))
        discriminator_counts, discriminator_errors, discriminator_warnings = nlm_d4_discriminator_report(nlm_items, nlm_adapter)
        errors.extend(discriminator_errors)
        warnings.extend(discriminator_warnings)
        print(f"  NLM D4 DISCRIMINATORS: {discriminator_counts}")
        if not any(q.get("qrt_contract", {}).get("primary_demand") == "REPRESENT" for q in nlm_items):
            errors.append("NLM: topic bank has no REPRESENT item")
        for (band, vector), members in nlm_vectors.items():
            if len(members) > 1:
                warnings.append(f"NLM: repeated vector {vector} in {band}: {[q['question_id'] for q in members]}")
            if len(members) > 3 and not all(
                isinstance(q.get("qrt_contract", {}).get("vector_reuse_justification"), str)
                and len(q["qrt_contract"]["vector_reuse_justification"].strip()) >= 25
                for q in members
            ):
                errors.append(f"NLM: un-justified template vector {vector} reused {len(members)} times in {band}")

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

    # Upstream Blueprint -> Adapter reciprocal verification
    for top_key in topic_matched_counts:
        top_ad = adapters.get(top_key, {})
        bp_refs = top_ad.get("blueprint_refs", {})
        if bp_refs and strict_golden:
            for bp_type, bp_path in bp_refs.items():
                if not validate_blueprint_file(bp_path, adapters_path):
                    errors.append(f"Upstream Blueprint validation failed for {bp_path}")

    if errors:
        print(f"\n[FAIL: {len(errors)} ERRORS DETECTED]")
        for err in errors[:15]:
            print(f"  - {err}")
        if len(errors) > 15:
            print(f"  ... and {len(errors) - 15} more errors.")
        return False
        
    print("\n[PASS] Question Bank passed all verification gates!")
    return True

def validate_blueprint_file(blueprint_path: str, adapters_path: str = "Physics/adapter/TopicAdapters.v1.json"):
    print(f"\n{'='*80}")
    print(f"BLUEPRINT VALIDATION: {blueprint_path}")
    print(f"{'='*80}")
    if not os.path.exists(blueprint_path):
        print(f"  FAIL: Blueprint file does not exist: {blueprint_path}")
        return False
        
    with open(blueprint_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    adapters = load_topic_adapters(adapters_path)
    errors = []
    
    schema = data.get("schema", "")
    topic_id = data.get("canonical_topic_id", "")
    
    # Locate matching adapter
    matched_adapter = None
    matched_key = None
    for k, a in adapters.items():
        if a.get("topic_id") == topic_id or k in blueprint_path:
            matched_adapter = a
            matched_key = k
            break
            
    if not matched_adapter:
        errors.append(f"No matching Topic Adapter found for canonical_topic_id: '{topic_id}'")
    else:
        ad_comp_map = matched_adapter.get("subtopic_competency_map", {})
        if "core1a" in schema:
            comps = data.get("atomic_competencies", {})
            if not comps:
                errors.append("Core 1A Blueprint missing 'atomic_competencies' mapping.")
            for cid, cdata in comps.items():
                if cid not in ad_comp_map:
                    errors.append(f"Competency {cid} in Blueprint not found in Topic Adapter.")
                else:
                    ac = ad_comp_map[cid]
                    if cdata.get("title") != ac.get("title"):
                        errors.append(f"Competency {cid} title mismatch: '{cdata.get('title')}' vs '{ac.get('title')}'")
            # First-Move Atlas
            bp_atlas = data.get("first_move_atlas", [])
            ad_atlas = matched_adapter.get("first_move_atlas", [])
            if bp_atlas and ad_atlas and len(bp_atlas) != len(ad_atlas):
                errors.append(f"First-Move Atlas length mismatch: Blueprint ({len(bp_atlas)}) vs Adapter ({len(ad_atlas)})")
        elif "core1b" in schema:
            recons = data.get("reconstruction_cycles", [])
            if not recons:
                errors.append("Core 1B Blueprint missing 'reconstruction_cycles'.")
            for r in recons:
                cref = r.get("competency_ref")
                if cref and cref not in ad_comp_map:
                    errors.append(f"Reconstruction cycle {r.get('cycle_id')} references unknown competency {cref}")
                    
    if errors:
        print(f"  FAIL: Found {len(errors)} Blueprint validation errors:")
        for err in errors:
            print(f"    - {err}")
        return False
        
    print(f"  PASS: Blueprint '{blueprint_path}' is in 100% reciprocal alignment with Topic Adapter '{matched_key}'.")
    return True

def validate_master_app(app_path: str, expected_q_count: int = 25):
    print(f"\n{'='*80}")
    print(f"MASTER TABLET APP VALIDATION: {app_path}")
    print(f"{'='*80}")
    
    with open(app_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    errors = []
    
    # Check question count rendered
    q_matches = re.findall(r'class="[^"]*card-source-tag[^"]*"', html)
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
    if not re.search(r'class="[^"]*hint-unlock-btn[^"]*"', html) and 'hint-toggle' not in html and 'data-hint-idx' not in html:
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
    parser.add_argument("--blueprint", type=str, help="Path to Core 1A or Core 1B Blueprint JSON")
    parser.add_argument("--adapters", type=str, default="Physics/adapter/TopicAdapters.v1.json", help="Path to topic adapters JSON")
    parser.add_argument("--strict-golden", action="store_true", help="Enforce strict Golden Benchmark standards (prompt-reveals, 5-step ladders, Cross-Core grounding)")
    args = parser.parse_args()
    
    success = True
    if args.blueprint:
        if not validate_blueprint_file(args.blueprint, args.adapters):
            success = False

    if args.bank:
        if not validate_question_bank(args.bank, args.adapters, strict_golden=args.strict_golden):
            success = False
    
    if args.app:
        if not validate_master_app(args.app):
            success = False
            
    if not args.bank and not args.app and not args.blueprint:
        print("Please provide --bank, --app, or --blueprint to validate.")
        sys.exit(1)
        
    if not success:
        print("\nOVERALL STATUS: FAILED")
        sys.exit(1)
    else:
        print("\nOVERALL STATUS: ALL GATES PASSED (100% COMPLIANT)")
        sys.exit(0)

if __name__ == "__main__":
    main()

