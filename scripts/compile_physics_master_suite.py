# scripts/compile_physics_master_suite.py
"""
Compile Unified Master Standalone Tablet App for Grade 9 Olympiad Physics.
Combines all 8 subtopics (200 Questions, 68 Competencies, 72 Figures)
into a single self-contained, offline-first, pre-rendered KaTeX DOM application.
"""

import json
import re
import os
import sys
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.physics_prerender_engine import prerender_html

TOPIC_CONFIGS = [
    {
        "id": "mechanics-nlm",
        "name": "1. Mechanics (NLM & Friction)",
        "short_name": "Mechanics",
        "bank": "TEST/physics-research/question_bank_mechanics_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_nlm_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_nlm_reconstruction.v1.json"
    },
    {
        "id": "kinematics-1d-2d",
        "name": "2. Kinematics (1D Motion)",
        "short_name": "Kinematics",
        "bank": "TEST/physics-research/question_bank_kinematics_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_kinematics_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_kinematics_reconstruction.v1.json"
    },
    {
        "id": "work-energy-power",
        "name": "3. Work, Energy & Power",
        "short_name": "Work & Energy",
        "bank": "TEST/physics-research/question_bank_wep_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_wep_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_wep_reconstruction.v1.json"
    },
    {
        "id": "gravitation-orbital-motion",
        "name": "4. Gravitation & Orbital Motion",
        "short_name": "Gravitation",
        "bank": "TEST/physics-research/question_bank_gravitation_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_gravitation_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_gravitation_reconstruction.v1.json"
    },
    {
        "id": "fluids-hydrostatics",
        "name": "5. Fluids & Hydrostatics",
        "short_name": "Fluids",
        "bank": "TEST/physics-research/question_bank_fluids_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_fluids_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_fluids_reconstruction.v1.json"
    },
    {
        "id": "heat-thermodynamics",
        "name": "6. Heat & Thermodynamics",
        "short_name": "Thermodynamics",
        "bank": "TEST/physics-research/question_bank_thermo_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_thermo_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_thermo_reconstruction.v1.json"
    },
    {
        "id": "vectors-and-components",
        "name": "7. Vectors & Components",
        "short_name": "Vectors",
        "bank": "TEST/physics-research/question_bank_vectors_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_vectors_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_vectors_reconstruction.v1.json"
    },
    {
        "id": "motion-in-a-plane",
        "name": "8. Motion in a Plane",
        "short_name": "Planar Motion",
        "bank": "TEST/physics-research/question_bank_planar_motion_grade9.v1.json",
        "ontology": "TEST/physics-research/blueprints/core1a_physics_planar_motion_ontology.v1.json",
        "reconstruction": "TEST/physics-research/blueprints/core1b_physics_planar_motion_reconstruction.v1.json"
    }
]

def compile_physics_master_suite(output_path: str = "standalone/physics-olympiad-grade9-master-suite.html"):
    print(f"\n{'='*80}")
    print("COMPILING UNIFIED MASTER STANDALONE TABLET APP (ALL 8 TOPICS)")
    print(f"Output: {output_path}")
    print(f"{'='*80}\n")

    # Load Adapter Data
    with open(REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json", "r", encoding="utf-8") as f:
        adapters_data = json.load(f)["topic_adapters"]

    # Extract offline KaTeX bundle & base styles from circles master
    circles_html_path = REPO_ROOT / "standalone/practice/core2-mathematics-circles-grade9-master.html"
    with open(circles_html_path, "r", encoding="utf-8") as f:
        circles_html = f.read()

    css_link_match = re.search(r'<link id="offline-katex-css"[^>]+>', circles_html)
    offline_katex_css_tag = css_link_match.group(0) if css_link_match else ""

    style_match = re.search(r'<style>([\s\S]*?)</style>', circles_html)
    base_css = style_match.group(1) if style_match else ""

    all_questions = []
    all_topic_data = []
    total_figures = 0
    total_competencies = 0

    band_names = {
        "D1": "D1 Foundational",
        "D2": "D2 Standard Olympiad",
        "D3": "D3 Hard Olympiad",
        "D4": "D4 Achievers HOTS"
    }

    # Load all 8 topics
    for cfg in TOPIC_CONFIGS:
        tid = cfg["id"]
        with open(REPO_ROOT / cfg["bank"], "r", encoding="utf-8") as f:
            bank = json.load(f)
        with open(REPO_ROOT / cfg["ontology"], "r", encoding="utf-8") as f:
            ont = json.load(f)
        with open(REPO_ROOT / cfg["reconstruction"], "r", encoding="utf-8") as f:
            rec = json.load(f)
        adp = adapters_data[tid]

        t_qs = bank.get("questions", [])
        for q in t_qs:
            q["_topic_id"] = tid
            q["_topic_name"] = cfg["name"]
            if q.get("figure", {}).get("has_figure", False):
                total_figures += 1
        all_questions.extend(t_qs)

        comp_count = len(adp.get("subtopic_competency_map", {}))
        total_competencies += comp_count

        all_topic_data.append({
            "config": cfg,
            "bank": bank,
            "ontology": ont,
            "reconstruction": rec,
            "adapter": adp,
            "question_count": len(t_qs),
            "comp_count": comp_count
        })

    total_q = len(all_questions)
    print(f"Loaded {len(TOPIC_CONFIGS)} topics: {total_q} questions, {total_competencies} competencies, {total_figures} figures.\n")

    # Render Question Card (Tab 1)
    def render_card(q, global_idx):
        qid = q["question_id"]
        tid = q["_topic_id"]
        tname = q["_topic_name"]
        prov = q.get("provenance", {"paper_code": "OLYMPIAD", "year": "2026", "question_number": f"Q{global_idx+1:03d}", "tier": "GRADE-9"})
        qrt = q["qrt_contract"]
        demand = qrt["primary_demand"]
        band = qrt["difficulty_band"]
        supporting = qrt.get("supporting_demands", [])
        
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
            <button class="opt-btn" onclick="selectOption('{qid}', '{opt_key}', '{correct}')" id="opt-{opt_key}-{qid}" data-opt="{opt_key}" data-type="{d_type}" data-diag="{d_msg}">
                <span class="opt-key">{opt_key}</span>
                <span class="opt-text">{opt_text}</span>
            </button>
            """
            
        hints = q.get("progressive_hints", [])
        hints_html = ""
        for h in hints:
            tier = h.get("tier", 1)
            title = h.get("title", f"Hint Tier {tier}")
            pq = h.get("prompt_question", "")
            reveal = h.get("reveal_text", "")
            hints_html += f"""
            <div class="hint-tier locked" id="hint-tier-{tier}-{qid}">
                <div class="hint-tier-header">
                    <span class="hint-tier-title">{title}</span>
                    <button class="hint-unlock-btn" onclick="unlockHint('{qid}', {tier})">Reveal Tier {tier}</button>
                </div>
                <div class="hint-prompt">{pq}</div>
                <div class="hint-reveal hidden" id="hint-reveal-{tier}-{qid}">{reveal}</div>
            </div>
            """
            
        proof = q.get("model_proof", {})
        ladder = proof.get("reasoning_ladder", {})
        ladder_html = f"""
        <div class="ladder-step"><strong>1. Understand:</strong> {ladder.get('understand', '')}</div>
        <div class="ladder-step"><strong>2. Represent:</strong> {ladder.get('represent', '')}</div>
        <div class="ladder-step"><strong>3. Connect:</strong> {ladder.get('connect', '')}</div>
        <div class="ladder-step"><strong>4. Calculate:</strong> {ladder.get('calculate', '')}</div>
        <div class="ladder-step"><strong>5. Interpret:</strong> {ladder.get('interpret', '')}</div>
        """
        
        indep = q.get("independent_check", {})
        limits = indep.get("limiting_cases", [])
        limits_html = "".join(f"<li><strong>{lc.get('condition', '')}:</strong> {lc.get('expected', '')}</li>" for lc in limits)
        
        comp_ref = q.get("subtopic_competency_ref", "")
        
        return f"""
        <article class="question-card" id="card-{qid}" data-qid="{qid}" data-topic="{tid}" data-band="{band}" data-demand="{demand}" data-has-figure="{'true' if has_fig else 'false'}">
            <div class="card-header">
                <div class="card-source-tag">
                    <span class="qid-badge">{qid}</span>
                    <span class="topic-pill">{tname.split('.')[1].strip() if '.' in tname else tname}</span>
                    <span class="band-badge band-{band.lower()}">{band_names.get(band, band)}</span>
                    <span class="demand-badge demand-{demand.lower()}">{demand}</span>
                </div>
                <div class="card-meta-right">
                    <button class="comp-link-btn" onclick="jumpToCompetency('{comp_ref}', '{tid}')" title="Jump to Competency Atlas">
                        {comp_ref} &#8599;
                    </button>
                </div>
            </div>
            {supp_badges}
            <div class="stem-container">{q["stem"]}</div>
            {fig_html}
            <div class="options-container">{options_html}</div>
            <div class="feedback-banner hidden" id="feedback-{qid}">
                <div class="feedback-result" id="feedback-result-{qid}"></div>
                <div class="feedback-diag" id="feedback-diag-{qid}"></div>
            </div>
            <details class="hints-accordion">
                <summary class="hints-summary">
                    <span>💡 Progressive Socratic Hints (3 Tiers)</span>
                    <span class="hint-count-indicator" id="hint-indicator-{qid}">3 Tiers Available</span>
                </summary>
                <div class="hints-body">{hints_html}</div>
            </details>
            <details class="solution-accordion" id="sol-accordion-{qid}">
                <summary class="solution-summary">
                    <span>📐 5-Step Mathematical Reasoning Ladder &amp; Proof</span>
                    <span class="sol-badge">Formal Verification</span>
                </summary>
                <div class="solution-body">
                    <div class="ladder-container">{ladder_html}</div>
                    <div class="final-expr-box">
                        <strong>Final Analytical Expression:</strong> {proof.get('final_expression', '')}
                    </div>
                    <div class="indep-check-box">
                        <div class="indep-title">Independent Physical Verification</div>
                        <div class="indep-row"><strong>Dimensional Formula:</strong> <code>{indep.get('dimensional_formula', '')}</code></div>
                        <div class="indep-row"><strong>Limiting Cases:</strong><ul>{limits_html}</ul></div>
                        <div class="indep-row"><strong>Alternative Method:</strong> {indep.get('check_it_another_way', '')}</div>
                        <div class="indep-row watch-out-box"><strong>Watch Out Trap:</strong> {indep.get('watch_out', '')}</div>
                    </div>
                </div>
            </details>
        </article>
        """

    # Render Subtopic Competency Atlas (Tab 2)
    def render_topic_atlas(tdata):
        cfg = tdata["config"]
        tid = cfg["id"]
        tname = cfg["name"]
        ont = tdata["ontology"]
        rec = tdata["reconstruction"]
        adp = tdata["adapter"]

        pillars_html = ""
        for p in ont.get("invariant_pillars", []):
            p_code = p.get("code", "")
            p_title = p.get("title", "")
            p_law = p.get("canonical_law", "")
            p_phys = p.get("physical_meaning", "")
            p_comps = p.get("bound_competencies", [])
            p_comps_html = "".join(f'<span class="bound-comp-pill" onclick="jumpToCompetency(\'{c}\', \'{tid}\')">{c}</span>' for c in p_comps)
            pillars_html += f"""
            <div class="pillar-card" id="pillar-{p_code}-{tid}">
                <div class="pillar-header">
                    <span class="pillar-badge">{p_code}</span>
                    <span class="pillar-title">{p_title}</span>
                </div>
                <div class="pillar-law"><strong>Canonical Expression:</strong> {p_law}</div>
                <div class="pillar-phys"><strong>Physical Core:</strong> {p_phys}</div>
                <div class="pillar-bound-row">
                    <span class="bound-label">Bound Competencies:</span>
                    {p_comps_html}
                </div>
            </div>
            """

        comps_html = ""
        comp_map = adp.get("subtopic_competency_map", {})
        for cid, cinfo in comp_map.items():
            ctitle = cinfo.get("title", "")
            crule = cinfo.get("canonical_rule", "")
            cscope = cinfo.get("scope_condition", "")
            ccheck = cinfo.get("model_check", "")
            cmistake = cinfo.get("easy_mistake_to_make", "")
            targets = cinfo.get("core2_transfer_target", [])
            targets_html = "".join(f'<button class="comp-target-btn" onclick="jumpToQuestion(\'{t}\')">{t} &#8594;</button>' for t in targets)
            pref = cinfo.get("pillar_ref", "")

            comps_html += f"""
            <div class="comp-card" id="comp-{cid}">
                <div class="comp-card-header">
                    <span class="comp-id-badge">{cid}</span>
                    <span class="comp-title">{ctitle}</span>
                    <span class="comp-pillar-badge" onclick="jumpToPillar('{pref}', '{tid}')">{pref}</span>
                </div>
                <div class="comp-rule"><strong>Canonical Invariant:</strong> {crule}</div>
                <div class="comp-scope"><strong>Scope &amp; Validity Limits:</strong> {cscope}</div>
                <div class="comp-check"><strong>Mental Physical Check:</strong> {ccheck}</div>
                <div class="comp-mistake"><strong>Common Misconception Trap:</strong> {cmistake}</div>
                <div class="comp-targets">
                    <strong>Core 2 Practice Items ({len(targets)} questions):</strong>
                    <div class="comp-target-row">{targets_html}</div>
                </div>
            </div>
            """

        dag_rows = ""
        for layer in rec.get("curriculum_dag_4layers", []):
            layer_name = layer.get("layer_name", "")
            layer_desc = layer.get("description", "")
            bound = ", ".join(layer.get("bound_competencies", []))
            dag_rows += f"""
            <tr>
                <td><strong>{layer_name}</strong></td>
                <td>{layer_desc}</td>
                <td><code>{bound}</code></td>
            </tr>
            """

        return f"""
        <section class="topic-atlas-section" id="atlas-topic-{tid}">
            <div class="topic-atlas-header">
                <h2>{tname}</h2>
                <span class="topic-atlas-counts">{len(comp_map)} Atomic Competencies &bull; 5 Invariant Pillars &bull; {tdata['question_count']} Questions</span>
            </div>
            
            <div class="atlas-block-title">&#9878; Invariant Pillars ($P_1$ to $P_5$)</div>
            <div class="pillars-grid">{pillars_html}</div>

            <div class="atlas-block-title">&#128214; Atomic Competencies &amp; Mental Models</div>
            <div class="comps-grid">{comps_html}</div>

            <div class="atlas-block-title">&#9881; 4-Layer Pedagogical DAG</div>
            <table class="dag-table">
                <thead><tr><th>Curriculum Layer</th><th>Pedagogical Role</th><th>Bound Competencies</th></tr></thead>
                <tbody>{dag_rows}</tbody>
            </table>
        </section>
        """

    # Assemble HTML
    print("Rendering 200 question cards...")
    cards_html = "".join(render_card(q, idx) for idx, q in enumerate(all_questions))
    
    print("Rendering 8 Subtopic Competency Atlas sections...")
    atlas_html = "".join(render_topic_atlas(td) for td in all_topic_data)

    # Topic Filter Buttons
    topic_filters_html = '<button class="filter-chip active" onclick="filterByTopic(\'ALL\')" id="topic-chip-ALL">All Topics (200)</button>'
    for cfg in TOPIC_CONFIGS:
        cid = cfg["id"]
        cname = cfg["short_name"]
        topic_filters_html += f'<button class="filter-chip" onclick="filterByTopic(\'{cid}\')" id="topic-chip-{cid}">{cname} (25)</button>'

    full_html = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Grade 9 Olympiad Physics &bull; Master Curriculum Suite</title>
  <meta name="description" content="Complete Grade 9 Physics Olympiad & IIT-JEE Foundation curriculum suite: 200 Golden questions, 68 atomic competencies, 72 vector figures, 100% pre-rendered KaTeX.">
  {offline_katex_css_tag}
  <style>
    {base_css}
    
    /* Master Suite Overrides & Aesthetics */
    :root {{
      --primary-accent: #38bdf8;
      --primary-hover: #0284c7;
      --card-bg: #1e293b;
      --body-bg: #0b0f19;
      --border-color: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}
    
    body {{
      background-color: var(--body-bg) !important;
      color: var(--text-main) !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
      margin: 0;
      padding: 0;
      font-size: 15px;
    }}
    
    .master-header {{
      background: #0f172a;
      border-bottom: 1px solid #334155;
      padding: 24px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .master-header-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .header-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .header-title-box h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .header-title-box p {{
      margin: 4px 0 0 0;
      color: #94a3b8;
      font-size: 14px;
    }}
    .telemetry-strip {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .telemetry-item {{
      background: #1e293b;
      border: 1px solid #334155;
      padding: 6px 12px;
      border-radius: 8px;
      text-align: center;
    }}
    .telemetry-num {{
      font-size: 16px;
      font-weight: 800;
      color: #38bdf8;
    }}
    .telemetry-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94a3b8;
    }}
    
    /* Navigation Modes */
    .mode-switch-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      border-top: 1px solid #1e293b;
      padding-top: 14px;
    }}
    .mode-tabs {{
      display: flex;
      gap: 8px;
    }}
    .mode-tab-btn {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      font-size: 14px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 8px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 48px;
      transition: all 0.2s ease;
    }}
    .mode-tab-btn:hover {{
      border-color: #38bdf8;
      color: #f8fafc;
    }}
    .mode-tab-btn.active {{
      background: #0284c7;
      border-color: #38bdf8;
      color: #fff;
    }}
    
    /* Topic Chips */
    .topic-chips-row {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: thin;
    }}
    .filter-chip {{
      background: #0f172a;
      border: 1px solid #334155;
      color: #cbd5e1;
      font-size: 13px;
      font-weight: 600;
      padding: 8px 14px;
      border-radius: 9999px;
      cursor: pointer;
      white-space: nowrap;
      min-height: 40px;
      display: inline-flex;
      align-items: center;
      transition: all 0.15s ease;
    }}
    .filter-chip:hover {{
      border-color: #38bdf8;
      color: #fff;
    }}
    .filter-chip.active {{
      background: #0369a1;
      border-color: #38bdf8;
      color: #fff;
    }}
    
    /* Secondary Controls */
    .controls-bar {{
      max-width: 1400px;
      margin: 16px auto;
      padding: 0 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
    }}
    .filters-group {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .filter-select, .search-input {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #f8fafc;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 14px;
      min-height: 44px;
    }}
    .search-input {{
      min-width: 240px;
    }}
    .filter-select:focus, .search-input:focus {{
      outline: none;
      border-color: #38bdf8;
    }}
    .visible-indicator {{
      font-size: 14px;
      color: #94a3b8;
      font-weight: 600;
    }}
    
    /* Layout Containers */
    .main-container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px;
    }}
    .tab-content {{
      display: none;
    }}
    .tab-content.active {{
      display: block;
    }}
    
    /* Question Card Styling */
    .question-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      transition: border-color 0.2s ease;
    }}
    .question-card:hover {{
      border-color: #475569;
    }}
    .question-card.hidden {{
      display: none !important;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #334155;
    }}
    .card-meta-left {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .qid-badge {{
      background: #0f172a;
      border: 1px solid #475569;
      color: #f8fafc;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 10px;
      border-radius: 6px;
    }}
    .topic-pill {{
      background: rgba(168, 85, 247, 0.15);
      border: 1px solid #a855f7;
      color: #e9d5ff;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
    }}
    .band-badge {{
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
    }}
    .band-d1 {{ background: #065f46; color: #a7f3d0; }}
    .band-d2 {{ background: #075985; color: #bae6fd; }}
    .band-d3 {{ background: #854d0e; color: #fef08a; }}
    .band-d4 {{ background: #831843; color: #fbcfe8; }}
    
    .demand-badge {{
      font-size: 12px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      background: #334155;
      color: #e2e8f0;
    }}
    .comp-link-btn {{
      background: #0f172a;
      border: 1px solid #38bdf8;
      color: #38bdf8;
      font-size: 13px;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      min-height: 48px;
      transition: all 0.2s ease;
    }}
    .comp-link-btn:hover {{
      background: #0284c7;
      color: #fff;
    }}
    
    .stem-container {{
      font-size: 16px;
      line-height: 1.6;
      color: #f1f5f9;
      margin-bottom: 20px;
    }}
    .card-figure-container {{
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
      text-align: center;
    }}
    .card-figure-caption {{
      font-size: 13px;
      color: #94a3b8;
      margin-top: 8px;
      font-style: italic;
    }}
    
    /* Options */
    .options-container {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin: 20px 0;
    }}
    .opt-btn {{
      background: #0f172a;
      border: 1px solid #334155;
      color: #f8fafc;
      padding: 14px 18px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 15px;
      text-align: left;
      display: flex;
      align-items: center;
      gap: 14px;
      min-height: 52px;
      transition: all 0.15s ease;
    }}
    .opt-btn:hover {{
      border-color: #38bdf8;
      background: #131c31;
    }}
    .opt-key {{
      background: #1e293b;
      border: 1px solid #475569;
      color: #38bdf8;
      font-weight: 800;
      font-size: 14px;
      width: 30px;
      height: 30px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .opt-btn.correct {{
      background: rgba(34, 197, 94, 0.15) !important;
      border-color: #22c55e !important;
      color: #f0fdf4 !important;
    }}
    .opt-btn.correct .opt-key {{
      background: #22c55e;
      color: #052e16;
      border-color: #22c55e;
    }}
    .opt-btn.incorrect {{
      background: rgba(239, 68, 68, 0.15) !important;
      border-color: #ef4444 !important;
      color: #fef2f2 !important;
    }}
    .opt-btn.incorrect .opt-key {{
      background: #ef4444;
      color: #450a0a;
      border-color: #ef4444;
    }}
    
    /* Feedback Banner */
    .feedback-banner {{
      padding: 14px 18px;
      border-radius: 8px;
      margin: 16px 0;
      font-size: 14px;
      line-height: 1.5;
    }}
    .feedback-banner.correct {{
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid #22c55e;
      color: #86efac;
    }}
    .feedback-banner.incorrect {{
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      color: #fca5a5;
    }}
    .feedback-result {{
      font-weight: 800;
      font-size: 15px;
      margin-bottom: 4px;
    }}
    
    /* Accordions */
    details {{
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      margin-top: 12px;
      overflow: hidden;
    }}
    summary {{
      padding: 14px 18px;
      font-weight: 700;
      font-size: 14px;
      color: #38bdf8;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      min-height: 48px;
      user-select: none;
    }}
    summary:hover {{
      background: #1e293b;
    }}
    .hints-body, .solution-body {{
      padding: 16px 18px;
      border-top: 1px solid #1e293b;
      font-size: 14px;
      line-height: 1.6;
    }}
    
    /* Hints */
    .hint-tier {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 10px;
    }}
    .hint-tier-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .hint-tier-title {{
      font-weight: 700;
      color: #f8fafc;
      font-size: 14px;
    }}
    .unlock-btn {{
      background: #0369a1;
      border: 1px solid #38bdf8;
      color: #fff;
      font-size: 12px;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
    }}
    .unlock-btn:hover {{
      background: #0284c7;
    }}
    .hint-reveal {{
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px dashed #475569;
      color: #bae6fd;
    }}
    
    /* Solution Ladder */
    .ladder-container {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .ladder-step {{
      background: #1e293b;
      padding: 10px 14px;
      border-radius: 6px;
      border-left: 3px solid #38bdf8;
    }}
    .final-expr-box {{
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid #38bdf8;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
      color: #e0f2fe;
    }}
    .indep-check-box {{
      background: #1e293b;
      border: 1px solid #334155;
      padding: 14px 16px;
      border-radius: 8px;
    }}
    .indep-title {{
      font-weight: 700;
      font-size: 14px;
      color: #f8fafc;
      margin-bottom: 8px;
    }}
    .indep-row {{
      margin-bottom: 6px;
    }}
    .watch-out-box {{
      background: rgba(245, 158, 11, 0.1);
      border-left: 3px solid #f59e0b;
      padding: 8px 12px;
      border-radius: 4px;
      color: #fef3c7;
      margin-top: 10px;
    }}
    
    /* Atlas Tab Styles */
    .topic-atlas-section {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 32px;
    }}
    .topic-atlas-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 20px;
      border-bottom: 2px solid #334155;
      padding-bottom: 12px;
    }}
    .topic-atlas-header h2 {{
      margin: 0;
      font-size: 20px;
      color: #f8fafc;
    }}
    .topic-atlas-counts {{
      font-size: 13px;
      color: #94a3b8;
    }}
    .atlas-block-title {{
      font-size: 16px;
      font-weight: 800;
      color: #38bdf8;
      margin: 24px 0 14px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .pillars-grid, .comps-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }}
    .pillar-card, .comp-card {{
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .pillar-header, .comp-card-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}
    .pillar-badge {{
      background: #0284c7;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .pillar-title, .comp-title {{
      font-size: 15px;
      font-weight: 700;
      color: #f8fafc;
    }}
    .comp-id-badge {{
      background: #7c3aed;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .comp-pillar-badge {{
      margin-left: auto;
      background: rgba(56, 189, 248, 0.2);
      border: 1px solid #38bdf8;
      color: #38bdf8;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
    }}
    .comp-mistake {{
      background: rgba(239, 68, 68, 0.1);
      border-left: 3px solid #ef4444;
      padding: 8px 12px;
      border-radius: 4px;
      color: #fca5a5;
    }}
    .comp-target-row {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 6px;
    }}
    .comp-target-btn {{
      background: #1e293b;
      border: 1px solid #475569;
      color: #38bdf8;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
      transition: all 0.15s ease;
    }}
    .comp-target-btn:hover {{
      background: #0284c7;
      color: #fff;
      border-color: #38bdf8;
    }}
    .dag-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }}
    .dag-table th, .dag-table td {{
      border: 1px solid #334155;
      padding: 10px 14px;
      font-size: 13px;
      text-align: left;
    }}
    .dag-table th {{
      background: #0f172a;
      color: #38bdf8;
    }}
    
    .hidden {{ display: none !important; }}
    
    @media (max-width: 768px) {{
      .pillars-grid, .comps-grid {{
        grid-template-columns: 1fr;
      }}
      .header-top-row {{
        flex-direction: column;
        align-items: flex-start;
      }}
    }}
  </style>
</head>
<body>

  <header class="master-header">
    <div class="master-header-inner">
      <div class="header-top-row">
        <div class="header-title-box">
          <h1>&#9889; Grade 9 Olympiad Physics &bull; Master Curriculum Suite</h1>
          <p>Core 1A Pedagogical Ontology Blueprints &bull; Schema v2.0.0 Adapters &bull; Core 2 Golden Benchmarks</p>
        </div>
        <div class="telemetry-strip">
          <div class="telemetry-item"><div class="telemetry-num">8</div><div class="telemetry-label">Topics</div></div>
          <div class="telemetry-item"><div class="telemetry-num">200</div><div class="telemetry-label">Questions</div></div>
          <div class="telemetry-item"><div class="telemetry-num">68</div><div class="telemetry-label">Competencies</div></div>
          <div class="telemetry-item"><div class="telemetry-num">72</div><div class="telemetry-label">Vector SVGs</div></div>
          <div class="telemetry-item"><div class="telemetry-num">100%</div><div class="telemetry-label">Offline Static KaTeX</div></div>
        </div>
      </div>
      
      <div class="mode-switch-row">
        <div class="mode-tabs">
          <button class="mode-tab-btn active" onclick="switchMode('practice')" id="mode-btn-practice">
            <span>&#127919; Core 2 Practice Suite</span>
          </button>
          <button class="mode-tab-btn" onclick="switchMode('atlas')" id="mode-btn-atlas">
            <span>&#128214; Core 1A Competency Atlas</span>
          </button>
        </div>
        <div class="visible-indicator">
          Showing <span id="visible-count">200</span> of 200 Questions
        </div>
      </div>
      
      <div class="topic-chips-row">
        {topic_filters_html}
      </div>
    </div>
  </header>

  <div class="controls-bar" id="controls-bar">
    <div class="filters-group">
      <select class="filter-select" id="band-filter" onchange="applyFilters()">
        <option value="ALL">All Bands (D1–D4)</option>
        <option value="D1">D1 Foundational</option>
        <option value="D2">D2 Standard Olympiad</option>
        <option value="D3">D3 Hard Olympiad</option>
        <option value="D4">D4 Achievers HOTS</option>
      </select>
      <select class="filter-select" id="demand-filter" onchange="applyFilters()">
        <option value="ALL">All Demands</option>
        <option value="APPLY">APPLY</option>
        <option value="MODEL">MODEL</option>
        <option value="SYNTHESIZE">SYNTHESIZE</option>
        <option value="EXPLAIN">EXPLAIN</option>
        <option value="REPRESENT">REPRESENT</option>
        <option value="RETRIEVE">RETRIEVE</option>
        <option value="JUSTIFY">JUSTIFY</option>
      </select>
      <select class="filter-select" id="figure-filter" onchange="applyFilters()">
        <option value="ALL">All Questions</option>
        <option value="FIGURE_ONLY">Figures Only</option>
      </select>
    </div>
    <input type="text" class="search-input" id="search-input" placeholder="Search questions, QID, competencies..." oninput="applyFilters()">
  </div>

  <main class="main-container">
    <div class="tab-content active" id="tab-practice">
      {cards_html}
    </div>
    
    <div class="tab-content" id="tab-atlas">
      {atlas_html}
    </div>
  </main>

  <script>
    let currentTopic = 'ALL';
    let currentMode = 'practice';

    function switchMode(mode) {{
      currentMode = mode;
      document.querySelectorAll('.mode-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      document.getElementById('mode-btn-' + mode).classList.add('active');
      document.getElementById('tab-' + mode).classList.add('active');
      
      const controls = document.getElementById('controls-bar');
      if (mode === 'atlas') {{
        controls.classList.add('hidden');
      }} else {{
        controls.classList.remove('hidden');
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function filterByTopic(topicId) {{
      currentTopic = topicId;
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      const activeChip = document.getElementById('topic-chip-' + topicId);
      if (activeChip) activeChip.classList.add('active');
      
      if (currentMode === 'atlas') {{
        document.querySelectorAll('.topic-atlas-section').forEach(sec => {{
          if (topicId === 'ALL' || sec.id === 'atlas-topic-' + topicId) {{
            sec.classList.remove('hidden');
          }} else {{
            sec.classList.add('hidden');
          }}
        }});
      }}
      applyFilters();
    }}

    function applyFilters() {{
      const band = document.getElementById('band-filter').value;
      const demand = document.getElementById('demand-filter').value;
      const fig = document.getElementById('figure-filter').value;
      const query = (document.getElementById('search-input').value || '').toLowerCase().trim();
      
      const cards = document.querySelectorAll('.question-card');
      let visible = 0;

      cards.forEach(c => {{
        const cTopic = c.getAttribute('data-topic');
        const cBand = c.getAttribute('data-band');
        const cDemand = c.getAttribute('data-demand');
        const cHasFig = c.getAttribute('data-has-figure') === 'true';
        const cText = c.textContent.toLowerCase();

        let show = true;
        if (currentTopic !== 'ALL' && cTopic !== currentTopic) show = false;
        if (band !== 'ALL' && cBand !== band) show = false;
        if (demand !== 'ALL' && cDemand !== demand) show = false;
        if (fig === 'FIGURE_ONLY' && !cHasFig) show = false;
        if (query && !cText.includes(query)) show = false;

        if (show) {{
          c.classList.remove('hidden');
          visible++;
        }} else {{
          c.classList.add('hidden');
        }}
      }});

      document.getElementById('visible-count').textContent = visible;
    }}

    function selectOption(qid, optKey, correctKey) {{
      const card = document.getElementById('card-' + qid);
      if (!card) return;
      
      const buttons = card.querySelectorAll('.opt-btn');
      buttons.forEach(btn => {{
        btn.classList.remove('correct', 'incorrect');
      }});
      
      const clickedBtn = document.getElementById('opt-' + optKey + '-' + qid);
      const isCorrect = (optKey === correctKey);
      
      if (isCorrect) {{
        clickedBtn.classList.add('correct');
      }} else {{
        clickedBtn.classList.add('incorrect');
        const correctBtn = document.getElementById('opt-' + correctKey + '-' + qid);
        if (correctBtn) correctBtn.classList.add('correct');
      }}
      
      const feedback = document.getElementById('feedback-' + qid);
      const res = document.getElementById('feedback-result-' + qid);
      const diag = document.getElementById('feedback-diag-' + qid);
      
      feedback.classList.remove('hidden', 'correct', 'incorrect');
      if (isCorrect) {{
        feedback.classList.add('correct');
        res.textContent = 'Correct! Outstanding reasoning.';
        diag.textContent = clickedBtn.getAttribute('data-diag') || '';
      }} else {{
        feedback.classList.add('incorrect');
        res.textContent = 'Incorrect (' + clickedBtn.getAttribute('data-type') + ')';
        diag.textContent = clickedBtn.getAttribute('data-diag') || '';
      }}
      
      const sol = document.getElementById('sol-accordion-' + qid);
      if (sol) sol.open = true;
    }}

    function unlockHint(qid, tier) {{
      const rev = document.getElementById('hint-reveal-' + tier + '-' + qid);
      if (rev) {{
        rev.classList.remove('hidden');
      }}
      const box = document.getElementById('hint-tier-' + tier + '-' + qid);
      if (box) {{
        box.classList.remove('locked');
      }}
      const indicator = document.getElementById('hint-indicator-' + qid);
      if (indicator) {{
        indicator.textContent = 'Tier ' + tier + ' of 3 Unlocked';
      }}
    }}

    function jumpToCompetency(compRef, topicId) {{
      switchMode('atlas');
      filterByTopic('ALL');
      const target = document.getElementById('comp-' + compRef);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        target.style.borderColor = '#38bdf8';
        target.style.boxShadow = '0 0 20px rgba(56,189,248,0.4)';
        setTimeout(() => {{
          target.style.borderColor = '#334155';
          target.style.boxShadow = 'none';
        }}, 3000);
      }}
    }}

    function jumpToPillar(pillarCode, topicId) {{
      const target = document.getElementById('pillar-' + pillarCode + '-' + topicId);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        target.style.borderColor = '#38bdf8';
        setTimeout(() => target.style.borderColor = '#334155', 2500);
      }}
    }}

    function jumpToQuestion(qid) {{
      switchMode('practice');
      filterByTopic('ALL');
      document.getElementById('band-filter').value = 'ALL';
      document.getElementById('demand-filter').value = 'ALL';
      document.getElementById('figure-filter').value = 'ALL';
      document.getElementById('search-input').value = '';
      applyFilters();
      
      const target = document.getElementById('card-' + qid);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        target.style.borderColor = '#38bdf8';
        target.style.boxShadow = '0 0 25px rgba(56,189,248,0.5)';
        setTimeout(() => {{
          target.style.borderColor = '#334155';
          target.style.boxShadow = 'none';
        }}, 3000);
      }}
    }}
  </script>
</body>
</html>
"""

    raw_path = REPO_ROOT / "scratch/_raw_physics_master_suite.html"
    print(f"Writing raw intermediate file to {raw_path}...")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    final_output = REPO_ROOT / output_path
    final_output.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Executing Node.js KaTeX pre-rendering engine...")
    prerender_html(str(raw_path), str(final_output))

    # Copy to public/
    public_output = REPO_ROOT / "public" / output_path
    public_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(final_output, public_output)

    # Copy to artifact dir
    artifact_dir = Path("C:/Users/reall/.gemini/antigravity/brain/40014ef9-8d66-475e-aff1-d6e53797ebbd")
    if artifact_dir.exists():
        shutil.copyfile(final_output, artifact_dir / "physics_olympiad_grade9_master_suite.html")
        print(f"Copied to brain artifact directory: {artifact_dir / 'physics_olympiad_grade9_master_suite.html'}")

    print(f"\n[SUCCESS] Compiled Unified Physics Master Suite to:")
    print(f"  -> {final_output}")
    print(f"  -> {public_output}")

if __name__ == "__main__":
    compile_physics_master_suite()
