import json
import re
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.physics_prerender_engine import prerender_html

def compile_dual_mode_app(bank_path: str, ontology_path: str, reconstruction_path: str, adapter_key: str, output_path: str):
    print(f"\n{'='*80}")
    print(f"COMPILING DUAL-MODE TABLET APP")
    print(f"Bank: {bank_path}")
    print(f"Ontology: {ontology_path}")
    print(f"Reconstruction: {reconstruction_path}")
    print(f"Adapter Key: {adapter_key}")
    print(f"Output: {output_path}")
    print(f"{'='*80}")

    # 1. Load Data
    with open(REPO_ROOT / bank_path, "r", encoding="utf-8") as f:
        bank_data = json.load(f)

    with open(REPO_ROOT / ontology_path, "r", encoding="utf-8") as f:
        ontology_data = json.load(f)

    with open(REPO_ROOT / reconstruction_path, "r", encoding="utf-8") as f:
        reconstruction_data = json.load(f)

    with open(REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json", "r", encoding="utf-8") as f:
        all_adapters = json.load(f)["topic_adapters"]
    
    if adapter_key not in all_adapters:
        raise ValueError(f"Adapter key '{adapter_key}' not found in TopicAdapters.v1.json")
    adapter_data = all_adapters[adapter_key]

    # 2. Extract offline KaTeX bundle & base styles from circles master
    circles_html_path = REPO_ROOT / "standalone/practice/core2-mathematics-circles-grade9-master.html"
    with open(circles_html_path, "r", encoding="utf-8") as f:
        circles_html = f.read()

    css_link_match = re.search(r'<link id="offline-katex-css"[^>]+>', circles_html)
    offline_katex_css_tag = css_link_match.group(0) if css_link_match else ""

    style_match = re.search(r'<style>([\s\S]*?)</style>', circles_html)
    base_css = style_match.group(1) if style_match else ""

    topic_title = adapter_data.get("display_name", "Grade 9 Olympiad Physics")
    total_q = len(bank_data["questions"])

    # 3. Build Question Cards (Tab 1)
    band_names = {
        "D1": "D1 Foundational",
        "D2": "D2 Standard Olympiad",
        "D3": "D3 Hard Olympiad",
        "D4": "D4 Achievers HOTS"
    }

    def render_question_card(q, index):
        qid = q["question_id"]
        prov = q.get("provenance", {"paper_code": "OLYMPIAD", "year": "2026", "question_number": f"Q{index+1:02d}", "tier": "GRADE-9"})
        qrt = q["qrt_contract"]
        demand = qrt["primary_demand"]
        band = qrt["difficulty_band"]
        supporting = qrt.get("supporting_demands", [])
        
        # Supporting badges
        supp_badges = "".join(f'<span class="supp-badge">{sd}</span>' for sd in supporting)
        if supp_badges:
            supp_badges = f'<div class="supp-badges-row"><span class="supp-label">Cognitive Profile:</span> {supp_badges}</div>'
            
        fig = q.get("figure", {})
        has_fig = fig.get("has_figure", False)
        fig_html = ""
        if has_fig and fig.get("svg_code"):
            fig_html = f"""
            <div class="card-figure-container">
                {fig["svg_code"]}
                <div class="card-figure-caption">{fig.get("caption", "")}</div>
            </div>
            """
        
        # Options
        options = q["options"]
        correct = q["correct_answer"]
        diag = q["distractor_diagnostics"]
        
        options_html = ""
        for opt_key in ["A", "B", "C", "D"]:
            opt_text = options[opt_key]
            d_info = diag[opt_key]
            d_type = d_info.get("type", "")
            d_msg = d_info.get("diagnostic", "").replace('"', '&quot;')
            options_html += f"""
            <button class="option-btn" 
                    data-option="{opt_key}" 
                    data-correct="{correct}" 
                    data-type="{d_type}" 
                    data-diagnostic="{d_msg}" 
                    onclick="handleOptionClick(this)">
                <span class="option-letter">{opt_key}</span>
                <span class="option-content">{opt_text}</span>
            </button>
            """
        
        # Progressive Hint Ladder
        hints = q.get("progressive_hints", [])
        hint_ladder_html = ""
        if len(hints) >= 3:
            h1_prompt = hints[0].get("prompt_question", "")
            h1_reveal = hints[0].get("reveal_text") or hints[0].get("text", "")
            h2_prompt = hints[1].get("prompt_question", "")
            h2_reveal = hints[1].get("reveal_text") or hints[1].get("text", "")
            h3_prompt = hints[2].get("prompt_question", "")
            h3_reveal = hints[2].get("reveal_text") or hints[2].get("text", "")
            
            hint_ladder_html = f"""
            <div class="hint-ladder-container">
                <div class="hint-ladder-header">
                    <span class="hint-ladder-title">🎯 3-Tier Prompt-Reveal Hint Ladder</span>
                    <span class="hint-step-indicator" id="hint-indicator-{qid}">Tier 1 of 3 Available</span>
                </div>
                
                <div class="hint-tier-box tier-1 open" id="hint-tier-1-{qid}">
                    <div class="hint-tier-badge">Tier 1: {hints[0].get("title", "Key Physics")}</div>
                    <div class="hint-prompt-question">❓ <strong>Prompt:</strong> {h1_prompt}</div>
                    <div class="hint-reveal-text">💡 <strong>Physics Clue:</strong> {h1_reveal}</div>
                </div>
                
                <div class="hint-tier-box tier-2 locked" id="hint-tier-2-{qid}">
                    <div class="hint-tier-badge">Tier 2: {hints[1].get("title", "Physical Representation")}</div>
                    <div class="hint-locked-content" id="hint-lock-msg-2-{qid}">
                        <span>🔒 Tier 2 locked</span>
                        <button class="hint-unlock-btn" onclick="unlockHint('{qid}', 2)">Unlock Hint 2</button>
                    </div>
                    <div class="hint-unlocked-content hidden" id="hint-content-2-{qid}">
                        <div class="hint-prompt-question">❓ <strong>Prompt:</strong> {h2_prompt}</div>
                        <div class="hint-reveal-text">💡 <strong>Representation Clue:</strong> {h2_reveal}</div>
                    </div>
                </div>
                
                <div class="hint-tier-box tier-3 locked" id="hint-tier-3-{qid}">
                    <div class="hint-tier-badge">Tier 3: {hints[2].get("title", "Mathematical Relation")}</div>
                    <div class="hint-locked-content" id="hint-lock-msg-3-{qid}">
                        <span>🔒 Tier 3 locked</span>
                        <button class="hint-unlock-btn" onclick="unlockHint('{qid}', 3)">Unlock Hint 3</button>
                    </div>
                    <div class="hint-unlocked-content hidden" id="hint-content-3-{qid}">
                        <div class="hint-prompt-question">❓ <strong>Prompt:</strong> {h3_prompt}</div>
                        <div class="hint-reveal-text">💡 <strong>Execution Clue:</strong> {h3_reveal}</div>
                    </div>
                </div>
            </div>
            """
        
        # 5-Step Reasoning Ladder
        proof = q["model_proof"]
        ladder = proof.get("reasoning_ladder", {})
        ladder_html = ""
        if ladder and isinstance(ladder, dict):
            ladder_html = f"""
            <div class="reasoning-ladder-box">
                <div class="ladder-title">🧗 5-Step Physical Reasoning Ladder:</div>
                <div class="ladder-step"><span class="step-num">1</span><strong>Understand:</strong> {ladder.get("understand", "")}</div>
                <div class="ladder-step"><span class="step-num">2</span><strong>Represent:</strong> {ladder.get("represent", "")}</div>
                <div class="ladder-step"><span class="step-num">3</span><strong>Connect:</strong> {ladder.get("connect", "")}</div>
                <div class="ladder-step"><span class="step-num">4</span><strong>Calculate:</strong> {ladder.get("calculate", "")}</div>
                <div class="ladder-step"><span class="step-num">5</span><strong>Interpret:</strong> {ladder.get("interpret", "")}</div>
            </div>
            """
        
        proof_steps = "".join(f"<li>{s}</li>" for s in proof.get("derivation_steps", []))
        proof_html = f"""
        <details class="accordion-disclosure">
            <summary>📐 Complete Analytical Model Proof & Reasoning</summary>
            <div class="disclosure-body">
                {ladder_html}
                <div style="font-weight:700; color:#cbd5e1; margin: 12px 0 6px 0;">Mathematical Derivation Steps:</div>
                <ol class="proof-steps-list">
                    {proof_steps}
                </ol>
                <div class="proof-final-expression">
                    <strong>Final Mathematical Expression:</strong> $${proof["final_expression"]}$$
                </div>
            </div>
        </details>
        """
        
        # Independent check
        check = q["independent_check"]
        limit_items = "".join(f"<li><strong>{lc.get('condition', '')}:</strong> {lc.get('expected') or lc.get('expected_outcome', '')}</li>" for lc in check.get("limiting_cases", []))
        
        quick_check_html = f'<div class="sanity-check-row quick-check">⚡ <strong>Quick Check:</strong> {check.get("quick_check", "")}</div>' if check.get("quick_check") else ""
        alt_check_html = f'<div class="sanity-check-row alt-check">🔄 <strong>Check It Another Way:</strong> {check.get("check_it_another_way", "")}</div>' if check.get("check_it_another_way") else ""
        watch_out_html = f'<div class="sanity-check-row watch-out">⚠️ <strong>Watch Out:</strong> {check.get("watch_out", "")}</div>' if check.get("watch_out") else ""
        review_idea_html = f'<div class="sanity-check-row review-idea">📚 <strong>Review This Idea:</strong> {check.get("review_this_idea", "")}</div>' if check.get("review_this_idea") else ""
        
        subtopic_ref = q.get("subtopic_competency_ref", "")
        comp_obj = adapter_data.get("subtopic_competency_map", {}).get(subtopic_ref, {})
        pref = comp_obj.get("pillar_ref", "P1")
        
        subtopic_tag = f"""
        <div class="target-competency-row">
            <span class="target-comp-label">🎯 Target Competency:</span>
            <button class="target-comp-btn" onclick="jumpToCompetency('{subtopic_ref}')" title="Click to view full Core 1A pedagogical theory in Atlas">
                {subtopic_ref} • {comp_obj.get('title', '')} <span class="btn-pillar-pill">Pillar {pref}</span>
            </button>
        </div>
        """
        
        check_html = f"""
        <details class="accordion-disclosure">
            <summary>🔬 Multi-Engine Sanity Verification & Core 1 Grounding</summary>
            <div class="disclosure-body">
                {subtopic_tag}
                <div class="dim-formula-tag">
                    <strong>Dimensional Homogeneity:</strong> <code>{check.get("dimensional_formula", "")}</code>
                </div>
                <div class="limits-header"><strong>Boundary & Limiting Extremals:</strong></div>
                <ul class="limits-list">
                    {limit_items}
                </ul>
                {quick_check_html}
                {alt_check_html}
                {watch_out_html}
                {review_idea_html}
            </div>
        </details>
        """
        
        # System parameters
        sys_params = q.get("system_parameters", {})
        ideal_list = ", ".join(sys_params.get("idealizations", []))
        sys_html = f"""
        <div class="system-parameters-box">
            <div><strong>System:</strong> {sys_params.get("system_boundary", "")}</div>
            <div><strong>Reference Frame:</strong> {sys_params.get("reference_frame", "")}</div>
            <div><strong>Idealizations:</strong> {ideal_list}</div>
        </div>
        """
        
        return f"""
        <div class="question-card" 
             id="card-{qid}" 
             data-qid="{qid}" 
             data-band="{band}" 
             data-demand="{demand}" 
             data-has-figure="{'true' if has_fig else 'false'}">
            <div class="card-header">
                <div class="card-source-tag">
                    <span class="badge-code">{prov.get("paper_code","OLYMPIAD")} {prov.get("year","2026")}</span>
                    <span class="badge-num">{prov.get("question_number", f"Q{index+1:02d}")} • {prov.get("tier","GRADE-9")}</span>
                </div>
                <div class="card-meta-badges">
                    <span class="demand-badge demand-{demand.lower()}">{demand}</span>
                    <span class="band-badge band-{band.lower()}">{band_names.get(band, band)}</span>
                </div>
            </div>
            
            {supp_badges}
            {sys_html}
            
            <div class="card-stem">
                {q["stem"]}
            </div>
            
            {fig_html}
            
            <div class="options-container" id="options-{qid}">
                {options_html}
            </div>
            
            <div class="feedback-container hidden" id="feedback-{qid}"></div>
            
            {hint_ladder_html}
            
            <div class="disclosures-wrapper">
                {proof_html}
                {check_html}
            </div>
        </div>
        """

    all_cards_html = "\n".join(render_question_card(q, idx) for idx, q in enumerate(bank_data["questions"]))

    # 4. Build Tab 2: Core 1A Subtopic Competency Atlas
    competencies_html = ""
    for cid, cinfo in adapter_data.get("subtopic_competency_map", {}).items():
        targets = cinfo.get("core2_transfer_target", [])
        target_btns = "".join(f'<button class="comp-target-btn" onclick="jumpToQuestion(\'{t}\')">🎯 {t}</button>' for t in targets)
        pref = cinfo.get("pillar_ref", "P1")
        competencies_html += f"""
        <div class="competency-card" id="comp-{cid}">
            <div class="comp-header">
                <span class="comp-id">{cid}</span>
                <span class="comp-title">{cinfo['title']}</span>
                <span class="comp-pillar-badge" onclick="jumpToPillar('{pref}')" title="View parent physical axiom">Pillar {pref}</span>
            </div>
            <div class="comp-rule"><strong>Canonical Physical Rule:</strong> {cinfo['canonical_rule']}</div>
            <div class="comp-scope"><strong>Scope & Validity:</strong> {cinfo['scope_condition']}</div>
            <div class="comp-check"><strong>Model Verification Check:</strong> {cinfo['model_check']}</div>
            <div class="comp-mistake">⚠️ <strong>Easy Mistake to Make (Anti-Trigger):</strong> {cinfo['easy_mistake_to_make']}</div>
            <div class="comp-targets">
                <strong>Cross-Core Practice Targets:</strong>
                <div class="comp-target-row">{target_btns}</div>
            </div>
        </div>
        """

    # 5. Build Tab 2: Core 1A 5 Invariant Pillars
    pillars_html = ""
    for p in ontology_data.get("structural_pillars", []):
        bound_comps = p.get("competency_refs", [])
        bound_pills = "".join(f'<span class="bound-comp-pill" onclick="jumpToCompetency(\'{c}\')">{c}</span>' for c in bound_comps)
        pillars_html += f"""
        <div class="pillar-card" id="pillar-{p['pillar_id']}">
            <div class="pillar-header">
                <span class="pillar-id">{p["pillar_id"]}</span>
                <span class="pillar-name">{p["name"]}</span>
            </div>
            <div class="pillar-statement">{p["statement"]}</div>
            <div class="pillar-math">$${p["mathematical_invariant"]}$$</div>
            <div class="pillar-scope"><strong>Scope & Invariance:</strong> {p["scope_condition"]}</div>
            <div class="pillar-bound-row">
                <span class="bound-label">Bound Competencies:</span>
                {bound_pills}
            </div>
        </div>
        """

    # 6. Build Tab 2: Dependency Graph
    layers_html = ""
    for layer in ontology_data.get("dependency_graph", {}).get("layers", []):
        nodes_html = "".join(f"<div class='dep-node'><strong>{n['term']}</strong><div class='dep-desc'>{n.get('description', 'Prerequisites: ' + ', '.join(n.get('depends_on', [])))}</div></div>" for n in layer["nodes"])
        layers_html += f"""
        <div class="dep-layer">
            <div class="dep-layer-title">Layer {layer["layer_index"]}: {layer["name"]}</div>
            <div class="dep-nodes-row">{nodes_html}</div>
        </div>
        """

    # 7. Build Tab 2: Cognitive Conflict Matrix
    ccm_rows = ""
    for row in ontology_data.get("cognitive_conflict_matrix", []):
        ccm_rows += f"""
        <tr>
            <td class="ccm-concept"><strong>{row["concept"]}</strong></td>
            <td class="ccm-misconception">{row["intuitive_misconception"]}</td>
            <td class="ccm-truth">{row.get("newtonian_scientific_truth") or row.get("scientific_truth", "")}</td>
            <td class="ccm-experiment">{row["decisive_experiment"]}</td>
        </tr>
        """

    # 8. Build Tab 2: Core 1B Reconstruction Cycles
    recon_html = ""
    for rc in reconstruction_data.get("reconstruction_cycles", []):
        checks_html = ""
        for c in rc.get("limiting_boundary_checks", []):
            cond = c.get("condition") or c.get("limit", "")
            res = c.get("expected_outcome") or c.get("physical_consequence") or c.get("expected", "")
            checks_html += f"<li><code>{cond}</code>: {res}</li>"
            
        recon_pivot = rc.get("phenomenological_reconstruction", {})
        if isinstance(recon_pivot, dict):
            pivot_text = recon_pivot.get("conceptual_pivot", "")
            pivot_formula = f"$${recon_pivot.get('reconstructed_formula', '')}$$" if recon_pivot.get("reconstructed_formula") else ""
        else:
            pivot_text = str(recon_pivot)
            pivot_formula = ""
            
        recon_html += f"""
        <div class="recon-card">
            <div class="recon-title">{rc["phenomenon"]}</div>
            <div class="recon-section">
                <strong>Standard Textbook Derivation:</strong>
                <p>{rc["standard_derivation"]}</p>
            </div>
            <div class="recon-section pivot">
                <strong>Phenomenological Reconstruction:</strong>
                <p>{pivot_text}</p>
                {pivot_formula}
            </div>
            <div class="recon-checks">
                <strong>Limiting Boundary Stress-Tests:</strong>
                <ul>{checks_html}</ul>
            </div>
        </div>
        """

    # 9. Assembly HTML
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Grade 9 Olympiad Physics — {topic_title}</title>
  {offline_katex_css_tag}
  <style>
    {base_css}
    
    /* WCAG 2.5.5 Touch Target Compliance */
    .option-btn, .opt-btn, .hint-unlock-btn, .comp-target-btn, .target-comp-btn, .comp-pillar-badge, .bound-comp-pill {{
      min-height: 48px;
      touch-action: manipulation;
    }}
    
    /* Interactive Jump & Pulse Highlighting */
    .highlight-pulse {{
      box-shadow: 0 0 0 3px #38bdf8, 0 0 25px rgba(56, 189, 248, 0.7) !important;
      transition: box-shadow 0.3s ease;
    }}
    
    /* Target Competency Button in Question Card */
    .target-competency-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}
    .target-comp-label {{
      font-size: 13.5px;
      color: #94a3b8;
      font-weight: 600;
    }}
    .target-comp-btn {{
      background: rgba(168, 85, 247, 0.15);
      border: 1px solid #a855f7;
      color: #e9d5ff;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }}
    .target-comp-btn:hover {{
      background: rgba(168, 85, 247, 0.3);
      border-color: #c084fc;
    }}
    .btn-pillar-pill {{
      background: #38bdf8;
      color: #0f172a;
      font-size: 11px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    
    /* Cognitive Profile Row */
    .supp-badges-row {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .supp-label {{
      font-size: 12px;
      color: #94a3b8;
      font-weight: 600;
    }}
    .supp-badge {{
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #7dd3fc;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 12px;
    }}
    
    /* Competency Atlas Styling in Tab 2 */
    .competency-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-left: 4px solid #a855f7;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .comp-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .comp-id {{
      background: #a855f7;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 2px 8px;
      border-radius: 4px;
    }}
    .comp-title {{
      font-size: 16px;
      font-weight: 700;
      color: #f8fafc;
    }}
    .comp-pillar-badge {{
      margin-left: auto;
      background: rgba(56, 189, 248, 0.2);
      border: 1px solid #38bdf8;
      color: #38bdf8;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      transition: all 0.2s ease;
    }}
    .comp-pillar-badge:hover {{
      background: rgba(56, 189, 248, 0.4);
    }}
    .comp-rule, .comp-scope, .comp-check, .comp-mistake {{
      font-size: 14px;
      line-height: 1.5;
      margin-bottom: 8px;
      color: #cbd5e1;
    }}
    .comp-mistake {{
      background: rgba(248, 113, 113, 0.1);
      border-left: 3px solid #f87171;
      padding: 8px 12px;
      border-radius: 4px;
      color: #fecaca;
    }}
    .comp-targets {{
      margin-top: 12px;
      font-size: 13px;
      color: #94a3b8;
    }}
    .comp-target-row {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 8px;
    }}
    .comp-target-btn {{
      background: #0f172a;
      border: 1px solid #475569;
      color: #38bdf8;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      transition: all 0.2s ease;
    }}
    .comp-target-btn:hover {{
      background: #1e293b;
      border-color: #38bdf8;
      color: #fff;
    }}
    
    /* Pillar Card Bound Competencies */
    .pillar-bound-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 10px;
      flex-wrap: wrap;
    }}
    .bound-label {{
      font-size: 13px;
      color: #94a3b8;
      font-weight: 600;
    }}
    .bound-comp-pill {{
      background: rgba(168, 85, 247, 0.2);
      border: 1px solid #a855f7;
      color: #e9d5ff;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      transition: all 0.2s ease;
    }}
    .bound-comp-pill:hover {{
      background: rgba(168, 85, 247, 0.4);
    }}
    
    /* System Parameters Box */
    .system-parameters-box {{
      background: #1e293b;
      border: 1px solid #334155;
      border-left: 3px solid #38bdf8;
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 14px;
      font-size: 14px;
      color: #94a3b8;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .system-parameters-box strong {{
      color: #cbd5e1;
    }}
    .dim-formula-tag {{
      background: #0f172a;
      border: 1px solid #334155;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 10px;
      font-size: 14px;
      color: #e2e8f0;
    }}
    .limits-header {{
      font-size: 14px;
      color: #38bdf8;
      margin-bottom: 6px;
    }}
    .limits-list {{
      margin: 0;
      padding-left: 20px;
      font-size: 14px;
      color: #cbd5e1;
    }}
    .limits-list li {{
      margin-bottom: 4px;
    }}
    .demand-retrieve {{ background: #0369a1; color: #fff; }}
    .demand-explain {{ background: #0891b2; color: #fff; }}
    .demand-apply {{ background: #2563eb; color: #fff; }}
    .demand-model {{ background: #7c3aed; color: #fff; }}
    .demand-represent {{ background: #c026d3; color: #fff; }}
    .demand-synthesize {{ background: #ea580c; color: #fff; }}
    .demand-justify {{ background: #059669; color: #fff; }}
    
    /* Pillar & Ontology Styling */
    .pillar-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .pillar-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }}
    .pillar-id {{
      background: #38bdf8;
      color: #0f172a;
      font-weight: 800;
      font-size: 14px;
      padding: 2px 8px;
      border-radius: 4px;
    }}
    .pillar-name {{
      font-size: 17px;
      font-weight: 700;
      color: #f8fafc;
    }}
    .pillar-statement {{
      font-size: 15px;
      color: #cbd5e1;
      margin-bottom: 10px;
      line-height: 1.5;
    }}
    .pillar-math {{
      background: #0f172a;
      padding: 8px 12px;
      border-radius: 6px;
      border-left: 3px solid #38bdf8;
      margin-bottom: 8px;
    }}
    .pillar-scope {{
      font-size: 14px;
      color: #94a3b8;
    }}
    
    .dep-layer {{
      margin-bottom: 20px;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 14px;
    }}
    .dep-layer-title {{
      font-size: 16px;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 12px;
    }}
    .dep-nodes-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }}
    .dep-node {{
      background: #1e293b;
      border: 1px solid #475569;
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 14px;
    }}
    .dep-desc {{
      color: #94a3b8;
      margin-top: 4px;
      font-size: 13.5px;
    }}
    
    .ccm-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 14px;
    }}
    .ccm-table th, .ccm-table td {{
      padding: 12px;
      border: 1px solid #334155;
      text-align: left;
      line-height: 1.45;
    }}
    .ccm-table th {{
      background: #0f172a;
      color: #38bdf8;
      font-weight: 700;
    }}
    .ccm-concept {{ color: #f8fafc; }}
    .ccm-misconception {{ color: #f87171; }}
    .ccm-truth {{ color: #4ade80; }}
    .ccm-experiment {{ color: #cbd5e1; }}
    
    .recon-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .recon-title {{
      font-size: 17px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 10px;
    }}
    .recon-section {{
      font-size: 14.5px;
      margin-bottom: 10px;
      color: #cbd5e1;
      line-height: 1.5;
    }}
    .recon-section.pivot {{
      background: #0f172a;
      padding: 10px 14px;
      border-left: 3px solid #a855f7;
      border-radius: 6px;
    }}
    .recon-checks {{
      font-size: 14px;
      color: #94a3b8;
    }}
    .recon-checks ul {{
      margin: 6px 0 0 0;
      padding-left: 20px;
    }}
    .recon-checks li {{
      margin-bottom: 4px;
      color: #cbd5e1;
    }}
    
    .reasoning-ladder-box {{
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 12px;
    }}
    .ladder-step {{
      font-size: 14px;
      color: #e2e8f0;
      margin-bottom: 8px;
      line-height: 1.5;
    }}
    .step-num {{
      display: inline-block;
      width: 20px;
      height: 20px;
      line-height: 20px;
      text-align: center;
      background: #38bdf8;
      color: #0f172a;
      font-weight: bold;
      border-radius: 50%;
      margin-right: 8px;
      font-size: 11px;
    }}
    .sanity-check-row {{
      font-size: 14px;
      padding: 8px 10px;
      border-radius: 6px;
      margin-top: 8px;
      line-height: 1.45;
    }}
    .sanity-check-row.quick-check {{
      background: rgba(56, 189, 248, 0.1);
      border-left: 3px solid #38bdf8;
      color: #bae6fd;
    }}
    .sanity-check-row.alt-check {{
      background: rgba(74, 222, 128, 0.1);
      border-left: 3px solid #4ade80;
      color: #bbf7d0;
    }}
    .sanity-check-row.watch-out {{
      background: rgba(248, 113, 113, 0.1);
      border-left: 3px solid #f87171;
      color: #fecaca;
    }}
    .sanity-check-row.review-idea {{
      background: rgba(168, 85, 247, 0.1);
      border-left: 3px solid #a855f7;
      color: #e9d5ff;
    }}
  </style>
</head>
<body>
  <div class="app-container">
    <header class="app-header">
      <div class="header-left">
        <h1 class="header-title">Grade 9 Olympiad Physics</h1>
        <p class="header-subtitle">{topic_title} • Dual-Mode Master Suite</p>
        <div class="header-tags">
          <span class="app-tag">NSEP / IPhO / JEE Foundation</span>
          <span class="app-tag">{total_q} Questions</span>
          <span class="app-tag">Interactive SBA Competency Atlas</span>
          <span class="app-tag">Static DOM Pre-Rendered</span>
          <span class="app-tag">WCAG ≥48px Touch</span>
        </div>
      </div>
      <div class="header-right">
        <div class="status-pill"><span class="status-dot"></span> Offline Ready</div>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <div class="nav-tabs-container">
      <button class="nav-tab active" id="tab-btn-practice" onclick="switchMainTab('practice')">
        📚 Practice Questions Suite ({total_q})
      </button>
      <button class="nav-tab" id="tab-btn-ontology" onclick="switchMainTab('ontology')">
        🗺️ Subtopic Competency Atlas & Invariants (Core 1A / 1B)
      </button>
    </div>

    <!-- MAIN TAB 1: PRACTICE QUESTIONS -->
    <div id="tab-content-practice">
      <div class="toolbar">
        <div class="filter-group">
          <label class="filter-label">Difficulty Band:</label>
          <select id="band-filter" onchange="applyFilters()">
            <option value="ALL">All Bands (D1 - D4)</option>
            <option value="D1">D1 Foundational</option>
            <option value="D2">D2 Standard Olympiad</option>
            <option value="D3">D3 Hard Olympiad</option>
            <option value="D4">D4 Achievers HOTS</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Primary Demand:</label>
          <select id="demand-filter" onchange="applyFilters()">
            <option value="ALL">All Demands</option>
            <option value="RETRIEVE">RETRIEVE</option>
            <option value="EXPLAIN">EXPLAIN</option>
            <option value="APPLY">APPLY</option>
            <option value="MODEL">MODEL</option>
            <option value="REPRESENT">REPRESENT</option>
            <option value="SYNTHESIZE">SYNTHESIZE</option>
            <option value="JUSTIFY">JUSTIFY</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Visual Figures:</label>
          <select id="figure-filter" onchange="applyFilters()">
            <option value="ALL">All Items</option>
            <option value="FIGURE_ONLY">Items With Figures Only</option>
          </select>
        </div>
        <div class="summary-pill">
          Showing <span id="visible-count">{total_q}</span> of {total_q}
        </div>
      </div>

      <div class="cards-grid" id="cards-container">
        {all_cards_html}
      </div>
    </div>

    <!-- MAIN TAB 2: STRUCTURAL ONTOLOGY & COMPETENCY ATLAS -->
    <div id="tab-content-ontology" class="hidden">
      <div class="ontology-container">
        
        <!-- SECTION 1: SUBTOPIC COMPETENCY ATLAS -->
        <div class="ontology-section">
          <h2 class="section-title">🗺️ Subtopic Competency Atlas (Core 1A Pedagogical Units)</h2>
          <p class="section-desc">Atomic competencies governing the domain reasoning system. Each unit specifies the canonical physical rule, model check, easy mistake to avoid, and direct transfer challenges in Tab 1.</p>
          <div class="competencies-grid">
            {competencies_html}
          </div>
        </div>

        <!-- SECTION 2: 5 INVARIANT PHYSICAL PILLARS -->
        <div class="ontology-section">
          <h2 class="section-title">🏛️ 5 Invariant Physical Pillars</h2>
          <p class="section-desc">The core physical axioms and conservation laws that underpin all problem-solving in this domain.</p>
          {pillars_html}
        </div>

        <!-- SECTION 3: 4-LAYER DEPENDENCY GRAPH -->
        <div class="ontology-section">
          <h2 class="section-title">🔗 4-Layer Dynamic Dependency Graph</h2>
          <p class="section-desc">Hierarchical cognitive flow from primitive physical definitions to axiomatic dynamic laws and coupled synthesis.</p>
          {layers_html}
        </div>

        <!-- SECTION 4: COGNITIVE CONFLICT MATRIX -->
        <div class="ontology-section">
          <h2 class="section-title">⚡ Cognitive Conflict & Falsification Matrix</h2>
          <p class="section-desc">Juxtaposing intuitive pre-Newtonian misconceptions with strict physical invariants and decisive falsifying experiments.</p>
          <table class="ccm-table">
            <thead>
              <tr>
                <th>Physical Concept</th>
                <th>Intuitive Misconception</th>
                <th>Scientific Invariant Truth</th>
                <th>Decisive Falsification Experiment</th>
              </tr>
            </thead>
            <tbody>
              {ccm_rows}
            </tbody>
          </table>
        </div>

        <!-- SECTION 5: RECONSTRUCTION CYCLES (CORE 1B) -->
        <div class="ontology-section">
          <h2 class="section-title">🔄 4-Cycle Phenomenological Reconstruction (Core 1B)</h2>
          <p class="section-desc">Deconstruct standard textbook derivations and reconstruct physical intuition through alternative conceptual perspectives and limiting-case stress tests.</p>
          {recon_html}
        </div>

      </div>
    </div>

  </div>

  <script>
    function switchMainTab(tab) {{
      const practiceContent = document.getElementById('tab-content-practice');
      const ontologyContent = document.getElementById('tab-content-ontology');
      const practiceBtn = document.getElementById('tab-btn-practice');
      const ontologyBtn = document.getElementById('tab-btn-ontology');

      if (tab === 'practice') {{
        practiceContent.classList.remove('hidden');
        ontologyContent.classList.add('hidden');
        practiceBtn.classList.add('active');
        ontologyBtn.classList.remove('active');
      }} else {{
        practiceContent.classList.add('hidden');
        ontologyContent.classList.remove('hidden');
        practiceBtn.classList.remove('active');
        ontologyBtn.classList.add('active');
      }}
    }}

    function jumpToQuestion(qid) {{
      switchMainTab('practice');
      const el = document.getElementById('card-' + qid);
      if (el) {{
        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        el.classList.add('highlight-pulse');
        setTimeout(() => el.classList.remove('highlight-pulse'), 2500);
      }}
    }}

    function jumpToCompetency(cid) {{
      switchMainTab('ontology');
      const el = document.getElementById('comp-' + cid);
      if (el) {{
        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        el.classList.add('highlight-pulse');
        setTimeout(() => el.classList.remove('highlight-pulse'), 2500);
      }}
    }}

    function jumpToPillar(pid) {{
      switchMainTab('ontology');
      const el = document.getElementById('pillar-' + pid);
      if (el) {{
        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        el.classList.add('highlight-pulse');
        setTimeout(() => el.classList.remove('highlight-pulse'), 2500);
      }}
    }}

    function handleOptionClick(btn) {{
      const card = btn.closest('.question-card');
      const qid = card.getAttribute('data-qid');
      const correctOpt = btn.getAttribute('data-correct');
      const selectedOpt = btn.getAttribute('data-option');
      const diagType = btn.getAttribute('data-type');
      const diagMsg = btn.getAttribute('data-diagnostic');
      
      const optionButtons = card.querySelectorAll('.option-btn');
      optionButtons.forEach(b => {{
        b.classList.remove('selected', 'correct', 'incorrect');
        if (b.getAttribute('data-option') === correctOpt) {{
          b.classList.add('correct');
        }}
      }});
      
      const feedbackContainer = document.getElementById('feedback-' + qid);
      feedbackContainer.classList.remove('hidden', 'feedback-correct', 'feedback-incorrect');
      
      if (selectedOpt === correctOpt) {{
        btn.classList.add('correct');
        feedbackContainer.classList.add('feedback-correct');
        feedbackContainer.innerHTML = '<strong>✅ Correct!</strong> ' + diagMsg;
      }} else {{
        btn.classList.add('incorrect');
        feedbackContainer.classList.add('feedback-incorrect');
        feedbackContainer.innerHTML = '<strong>❌ Incorrect (' + diagType + '):</strong> ' + diagMsg;
      }}
    }}

    function unlockHint(qid, tier) {{
      const lockMsg = document.getElementById('hint-lock-msg-' + tier + '-' + qid);
      const content = document.getElementById('hint-content-' + tier + '-' + qid);
      const tierBox = document.getElementById('hint-tier-' + tier + '-' + qid);
      const indicator = document.getElementById('hint-indicator-' + qid);

      if (lockMsg && content && tierBox) {{
        lockMsg.classList.add('hidden');
        content.classList.remove('hidden');
        tierBox.classList.remove('locked');
        tierBox.classList.add('open');
        if (indicator) {{
          indicator.textContent = 'Tier ' + tier + ' of 3 Unlocked';
        }}
      }}
    }}

    function applyFilters() {{
      const band = document.getElementById('band-filter').value;
      const demand = document.getElementById('demand-filter').value;
      const fig = document.getElementById('figure-filter').value;
      const cards = document.querySelectorAll('.question-card');
      let visible = 0;

      cards.forEach(c => {{
        const cBand = c.getAttribute('data-band');
        const cDemand = c.getAttribute('data-demand');
        const cHasFig = c.getAttribute('data-has-figure') === 'true';

        let show = true;
        if (band !== 'ALL' && cBand !== band) show = false;
        if (demand !== 'ALL' && cDemand !== demand) show = false;
        if (fig === 'FIGURE_ONLY' && !cHasFig) show = false;

        if (show) {{
          c.classList.remove('hidden');
          visible++;
        }} else {{
          c.classList.add('hidden');
        }}
      }});

      document.getElementById('visible-count').textContent = visible;
    }}
  </script>
</body>
</html>
"""

    # 10. Write raw file and pre-render with Node.js KaTeX
    raw_path = REPO_ROOT / "scratch/_raw_dual_mode_app.html"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    final_output = REPO_ROOT / output_path
    final_output.parent.mkdir(parents=True, exist_ok=True)
    prerender_html(str(raw_path), str(final_output))

    # Copy to public/
    public_output = REPO_ROOT / "public" / output_path
    public_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(final_output, public_output)
    print(f"Successfully compiled dual-mode master app to {final_output} and {public_output}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile Dual-Mode Tablet App (Interactive Core 1A Textbook + Core 2 Master Suite)")
    parser.add_argument("--bank", required=True, help="Path to question bank JSON")
    parser.add_argument("--ontology", required=True, help="Path to Core 1A ontology JSON")
    parser.add_argument("--reconstruction", required=True, help="Path to Core 1B reconstruction JSON")
    parser.add_argument("--adapter-key", required=True, help="Adapter key in TopicAdapters.v1.json")
    parser.add_argument("--output", required=True, help="Output path for standalone HTML")
    args = parser.parse_args()

    compile_dual_mode_app(args.bank, args.ontology, args.reconstruction, args.adapter_key, args.output)
