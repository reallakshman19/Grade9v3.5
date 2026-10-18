# scripts/compile_tri_modal_mechanics_master_app.py
"""
Compile Tri-Modal Master Tablet Application for Mechanics (NLM & Friction).
Architecture:
  - Tab 1: Core 2 Practice Suite (25 Olympiad Cards with 5-Step Proofs & Prompt-Reveals)
  - Tab 2: Core 1A Learner Textbook (11 Comprehensive Chapters from Golden PDF)
  - Tab 3: Core 1B Recall & Reconstruction (Cognitive Dissonance Probes, Invariant Cycles, & DAG)
"""

import json
import re
import os
import sys
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.physics_prerender_engine import prerender_html

def compile_tri_modal_mechanics():
    print(f"\n{'='*80}")
    print("COMPILING TRI-MODAL MASTER TABLET APP: MECHANICS (NLM & FRICTION)")
    print("Tripartite Architecture: Core 1A (Learn) <-> Core 1B (Recall) <-> Core 2 (Practice)")
    print(f"{'='*80}\n")

    # Load Data
    bank_path = REPO_ROOT / "TEST/physics-research/question_bank_mechanics_grade9.v1.json"
    ontology_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_nlm_ontology.v1.json"
    reconstruction_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_nlm_reconstruction.v1.json"
    adapters_path = REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json"

    with open(bank_path, "r", encoding="utf-8") as f:
        bank_data = json.load(f)
    with open(ontology_path, "r", encoding="utf-8") as f:
        ontology_data = json.load(f)
    with open(reconstruction_path, "r", encoding="utf-8") as f:
        reconstruction_data = json.load(f)
    with open(adapters_path, "r", encoding="utf-8") as f:
        adapters_data = json.load(f)["topic_adapters"]["mechanics-nlm"]

    # Extract base64 KaTeX & base CSS
    circles_html_path = REPO_ROOT / "standalone/practice/core2-mathematics-circles-grade9-master.html"
    with open(circles_html_path, "r", encoding="utf-8") as f:
        circles_html = f.read()

    css_link_match = re.search(r'<link id="offline-katex-css"[^>]+>', circles_html)
    offline_katex_css_tag = css_link_match.group(0) if css_link_match else ""

    style_match = re.search(r'<style>([\s\S]*?)</style>', circles_html)
    base_css = style_match.group(1) if style_match else ""

    # =========================================================================
    # TAB 1: CORE 2 PRACTICE CARDS (25 QUESTIONS)
    # =========================================================================
    band_names = {
        "D1": "D1 Foundational",
        "D2": "D2 Standard Olympiad",
        "D3": "D3 Hard Olympiad",
        "D4": "D4 Achievers HOTS"
    }

    def render_practice_card(q, index):
        qid = q["question_id"]
        prov = q.get("provenance", {"paper_code": "OLYMPIAD", "year": "2026", "question_number": f"Q{index+1:02d}", "tier": "GRADE-9"})
        qrt = q["qrt_contract"]
        demand = qrt["primary_demand"]
        band = qrt["difficulty_band"]
        supporting = qrt.get("supporting_demands", [])
        comp_ref = q.get("subtopic_competency_ref", "")
        
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
            <button class="opt-btn" onclick="selectOption('{qid}', '{opt_key}', '{correct}')" id="opt-{opt_key}-{qid}" data-opt="{opt_key}" data-type="{d_type}" data-diag="{d_msg}">
                <span class="opt-key">{opt_key}</span>
                <span class="opt-text">{opt_text}</span>
            </button>
            """
            
        # Hints
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
            
        # 5-step ladder
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
        
        return f"""
        <article class="question-card" id="card-{qid}" data-qid="{qid}" data-band="{band}" data-demand="{demand}" data-has-figure="{'true' if has_fig else 'false'}">
            <div class="card-header">
                <div class="card-source-tag">
                    <span class="qid-badge">{qid}</span>
                    <span class="band-badge band-{band.lower()}">{band_names.get(band, band)}</span>
                    <span class="demand-badge demand-{demand.lower()}">{demand}</span>
                </div>
                <div class="card-meta-right">
                    <button class="cross-link-btn" onclick="jumpToCore1A('{comp_ref}')" title="Read Core 1A Textbook Chapter">
                        📖 {comp_ref} Theory &#8599;
                    </button>
                    <button class="cross-link-btn" onclick="jumpToCore1B('RECON-01')" title="Practice Core 1B Reconstruction">
                        🧠 Reconstruct &#8599;
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

    # =========================================================================
    # TAB 2: CORE 1A NARRATIVE TEXTBOOK (11 UNITS FROM GOLDEN PDF)
    # =========================================================================
    textbook_units = [
        {
            "id": "NLM-01",
            "title": "Motion is Not Force",
            "subtitle": "Constant velocity can coexist with zero net force",
            "pillar": "P1",
            "story": "Newton I links change of velocity to net external force. Motion itself does not require a sustaining net force. A crate sliding at constant velocity on a frictionless surface has zero net force acting upon it.",
            "key_idea": "If velocity is constant in an inertial frame, acceleration is zero ($a = 0$), and therefore the net external force is strictly zero ($\\Sigma \\vec{F} = 0$).",
            "how_it_works": [
                "Choose the body and ask whether its velocity is changing.",
                "Draw all external forces acting on that body.",
                "Add them vectorially before discussing motion.",
                "Check: zero net force means constant velocity (including rest)."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 140" width="100%" height="140">
  <defs><marker id="ar1" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <rect x="130" y="40" width="120" height="60" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="190" y="75" font-size="16" font-family="sans-serif" text-anchor="middle" fill="#f8fafc" font-weight="bold">BODY (m)</text>
  <line x1="130" y1="70" x2="40" y2="70" stroke="#ef4444" stroke-width="3" marker-end="url(#ar1)"/>
  <text x="75" y="60" font-size="14" font-family="sans-serif" fill="#ef4444" font-weight="bold">40 N (Left)</text>
  <line x1="250" y1="70" x2="340" y2="70" stroke="#22c55e" stroke-width="3" marker-end="url(#ar1)"/>
  <text x="260" y="60" font-size="14" font-family="sans-serif" fill="#22c55e" font-weight="bold">40 N (Right)</text>
  <text x="190" y="125" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#94a3b8">ΣF = 40 - 40 = 0 ⟹ Constant Velocity v = 3 m/s</text>
</svg>""",
            "worked_example": "A crate moves right at $3\\text{ m/s}$ while $60\\text{ N}$ right and $60\\text{ N}$ left act on it. Since $F_{\\text{net}} = 60 - 60 = 0$, acceleration $a = 0$; it continues at constant velocity indefinitely.",
            "guided_try": {
                "prompt": "A puck glides at constant velocity on an ideal frictionless surface. What horizontal net force is required to sustain this motion?",
                "guide": "Name the body $\\to$ draw the representation $\\to$ state Newton I before calculating.",
                "solution": "Answer: $0\\text{ N}$. By Newton I, zero net force is required to maintain constant velocity."
            },
            "faded_try": "Change the mass of the crate from $10\\text{ kg}$ to $50\\text{ kg}$ while keeping the balanced $60\\text{ N}$ forces. Does the required net force change? (No; zero net force maintains any constant speed regardless of mass).",
            "watch_out": "A moving object does not automatically need a forward net force to keep moving.",
            "practice_targets": ["PHYS-NLM-001", "PHYS-NLM-002", "PHYS-NLM-021"]
        },
        {
            "id": "NLM-02",
            "title": "Choose the Body Before Drawing Forces",
            "subtitle": "Interactions become forces only after the body is chosen",
            "pillar": "P1",
            "story": "A free-body diagram is a diagram of strictly one chosen body. First identify what interacts with it (Earth, surface, rope, worker); then draw ONLY the forces exerted ON that body.",
            "key_idea": "The phrase 'force on X by Y' prevents body confusion and third-law errors. Never put 'force on Y by X' on X's diagram.",
            "how_it_works": [
                "Circle the specific body or system being analysed.",
                "List all interacting bodies (Earth, table, cable, hand).",
                "Convert each interaction into exactly one force arrow on the chosen body.",
                "Do NOT include forces the chosen body exerts on external objects."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 140" width="100%" height="140">
  <defs><marker id="ar2" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <circle cx="190" cy="70" r="45" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4"/>
  <rect x="155" y="45" width="70" height="50" rx="6" fill="#1e293b" stroke="#f8fafc" stroke-width="2"/>
  <text x="190" y="75" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#f8fafc">Book (B)</text>
  <line x1="190" y1="45" x2="190" y2="10" stroke="#22c55e" stroke-width="3" marker-end="url(#ar2)"/>
  <text x="200" y="25" font-size="14" font-family="sans-serif" fill="#22c55e">N (by Table)</text>
  <line x1="190" y1="95" x2="190" y2="135" stroke="#ef4444" stroke-width="3" marker-end="url(#ar2)"/>
  <text x="200" y="125" font-size="14" font-family="sans-serif" fill="#ef4444">W (by Earth)</text>
</svg>""",
            "worked_example": "For a book on a table, the book's FBD contains Earth-on-book weight ($W$) and table-on-book normal ($N$). The book-on-table downward push belongs strictly on the table's FBD.",
            "guided_try": {
                "prompt": "A crate is pushed across a floor by a worker. Name the three external interactions acting on the crate.",
                "guide": "Identify every object physically in contact with or gravitationally acting upon the crate.",
                "solution": "1. Worker-crate contact push. 2. Earth-crate gravitational pull. 3. Floor-crate normal contact and friction."
            },
            "faded_try": "If the worker suddenly stops pushing while the crate continues to slide, which interaction disappears immediately? (The worker-crate interaction vanishes; Earth and floor interactions remain).",
            "watch_out": "An action-reaction interaction pair is never two arrows on the same free-body diagram.",
            "practice_targets": ["PHYS-NLM-003", "PHYS-NLM-004"]
        },
        {
            "id": "NLM-03",
            "title": "Net Force is a Vector Sum",
            "subtitle": "Balanced forces and no forces are different physical statements",
            "pillar": "P2",
            "story": "Newton II uses the net external vector sum $\\Sigma \\vec{F}$, not whichever force is easiest to notice. Balanced forces can be very large individually while producing zero acceleration.",
            "key_idea": "Choose an explicit Cartesian coordinate system, assign signs to components, and sum algebraically: $\\Sigma F_x = m a_x$ and $\\Sigma F_y = m a_y$.",
            "how_it_works": [
                "Declare $+x$ and $+y$ coordinate axes.",
                "Resolve diagonal forces into orthogonal components using trigonometry.",
                "Compute $\\Sigma F_x$ and $\\Sigma F_y$ independently.",
                "Only then deduce acceleration components via $a_x = \\Sigma F_x / m$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 120" width="100%" height="120">
  <defs><marker id="ar3" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <rect x="130" y="30" width="100" height="50" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="180" y="60" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#f8fafc">Cart (5 kg)</text>
  <line x1="230" y1="55" x2="330" y2="55" stroke="#22c55e" stroke-width="3" marker-end="url(#ar3)"/>
  <text x="250" y="45" font-size="14" font-family="sans-serif" fill="#22c55e" font-weight="bold">+25 N</text>
  <line x1="130" y1="55" x2="50" y2="55" stroke="#ef4444" stroke-width="3" marker-end="url(#ar3)"/>
  <text x="65" y="45" font-size="14" font-family="sans-serif" fill="#ef4444" font-weight="bold">-10 N</text>
  <text x="180" y="105" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#38bdf8">F_net = +25 - 10 = +15 N (Right) ⟹ a = 3.0 m/s²</text>
</svg>""",
            "worked_example": "A cart has $25\\text{ N}$ pulling right and $10\\text{ N}$ pulling left. With right as positive, $F_{\\text{net},x} = 25 - 10 = +15\\text{ N}$. For $m = 5\\text{ kg}$, $a_x = 15/5 = 3.0\\text{ m/s}^2$ to the right.",
            "guided_try": {
                "prompt": "A box experiences $30\\text{ N}$ to the right and $30\\text{ N}$ to the left. What is its horizontal acceleration?",
                "guide": "Compute the algebraic sum with signs before invoking $a = F/m$.",
                "solution": "Answer: $0\\text{ m/s}^2$, regardless of whether the box is currently stationary or already gliding at high speed."
            },
            "faded_try": "If a third force of $15\\text{ N}$ is added directed to the left, what is the new net force and acceleration of the $5\\text{ kg}$ cart? ($F_{\\text{net}} = 25 - 10 - 15 = 0\\text{ N} \\implies a = 0$).",
            "watch_out": "Do not confuse 'net force is zero' with 'there are no forces acting'.",
            "practice_targets": ["PHYS-NLM-005", "PHYS-NLM-007"]
        },
        {
            "id": "NLM-04",
            "title": "Newton II and Dynamic Scaling",
            "subtitle": "Acceleration responds to net force and mass together",
            "pillar": "P4",
            "story": "For a body of constant mass, $\\vec{F}_{\\text{net}} = m\\vec{a}$. At fixed mass, acceleration scales directly with net force; at fixed net force, acceleration scales inversely with total mass.",
            "key_idea": "For simultaneous variations in force and mass, form scaling ratios before substituting raw numbers: $\\frac{a_2}{a_1} = \\left(\\frac{F_2}{F_1}\\right)\\left(\\frac{m_1}{m_2}\\right)$.",
            "how_it_works": [
                "Write $a_1 = F_1 / m_1$ and $a_2 = F_2 / m_2$.",
                "Form the dimensionless ratio $a_2 / a_1 = (F_2/F_1)(m_1/m_2)$.",
                "Preserve vector direction from the signed net force.",
                "Check unit consistency: $1\\text{ N} = 1\\text{ kg}\\cdot\\text{m/s}^2$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 130" width="100%" height="130">
  <rect x="20" y="20" width="340" height="90" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5"/>
  <text x="40" y="50" font-size="14" font-family="sans-serif" fill="#94a3b8">Case 1: F = 60 N, m = 5 kg ⟹ <tspan fill="#38bdf8" font-weight="bold">a = 12 m/s²</tspan></text>
  <text x="40" y="75" font-size="14" font-family="sans-serif" fill="#94a3b8">Case 2: F = 60 N, m = 10 kg (2x mass) ⟹ <tspan fill="#eab308" font-weight="bold">a = 6 m/s² (1/2 a)</tspan></text>
  <text x="40" y="100" font-size="14" font-family="sans-serif" fill="#94a3b8">Case 3: F = 30 N, m = 10 kg (1/2 F, 2x m) ⟹ <tspan fill="#ef4444" font-weight="bold">a = 3 m/s² (1/4 a)</tspan></text>
</svg>""",
            "worked_example": "If applied force halves ($F_2/F_1 = 1/2$) while mass doubles ($m_2/m_1 = 2$), acceleration becomes $(1/2) \\times (1/2) = 1/4$ of its original value.",
            "guided_try": {
                "prompt": "A $40\\text{ N}$ net force accelerates a $5\\text{ kg}$ object. What is its acceleration?",
                "guide": "Apply $a = F_{\\text{net}} / m$ directly.",
                "solution": "Answer: $a = 40 / 5 = 8.0\\text{ m/s}^2$."
            },
            "faded_try": "What net force is required to accelerate a $10\\text{ kg}$ object at the same $8.0\\text{ m/s}^2$? (Answer: $F = 10 \\times 8 = 80\\text{ N}$, double the force).",
            "watch_out": "'Half the force produces half the acceleration' is true ONLY if the accelerated mass remains strictly unchanged.",
            "practice_targets": ["PHYS-NLM-006", "PHYS-NLM-011", "PHYS-NLM-022"]
        },
        {
            "id": "NLM-05",
            "title": "Stopping Force Needs Two Models",
            "subtitle": "Kinematics supplies acceleration; Newton II supplies retarding force",
            "pillar": "P4",
            "story": "Determining stopping force requires coupling kinematics with dynamics. Do not jump directly from stopping distance to force. First isolate acceleration using kinematic relations, then evaluate force via Newton II.",
            "key_idea": "For uniform braking over distance $s$, evaluate $a = \\frac{v^2 - u^2}{2s} = -\\frac{u^2}{2s}$, then compute retarding force $F_{\\text{stop}} = m|a| = \\frac{m u^2}{2s}$.",
            "how_it_works": [
                "List kinematic state variables: $u, v=0, s$.",
                "Apply $v^2 = u^2 + 2as$ to determine acceleration $a$.",
                "Apply $F_{\\text{net}} = ma$ keeping signs explicit.",
                "If stopping time is required, compute $t = \\frac{2s}{u}$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 120" width="100%" height="120">
  <defs><marker id="ar5" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <line x1="30" y1="80" x2="350" y2="80" stroke="#475569" stroke-width="2"/>
  <rect x="40" y="45" width="50" height="35" rx="4" fill="#38bdf8"/>
  <text x="65" y="67" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#0f172a" font-weight="bold">u</text>
  <rect x="290" y="45" width="50" height="35" rx="4" fill="#64748b"/>
  <text x="315" y="67" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#fff" font-weight="bold">v=0</text>
  <line x1="90" y1="95" x2="290" y2="95" stroke="#38bdf8" stroke-width="2" marker-end="url(#ar5)"/>
  <text x="190" y="115" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#38bdf8">Stopping Distance s ⟹ F_stop = m u² / (2s)</text>
</svg>""",
            "worked_example": "A $0.020\\text{ kg}$ pellet moving at $100\\text{ m/s}$ penetrates a wooden barrier and stops in $0.10\\text{ m}$. $a = (0 - 100^2)/(2 \\times 0.10) = -50,000\\text{ m/s}^2$. Retarding force $F = (0.020)(-50,000) = -1000\\text{ N}$.",
            "guided_try": {
                "prompt": "If the same pellet stops over twice the distance ($0.20\\text{ m}$), what happens to $|a|$ and stopping force $|F|$?",
                "guide": "Inspect how $a$ and $F$ scale with $s$ in $F = mu^2 / (2s)$.",
                "solution": "Answer: Both $|a|$ and $|F|$ halve ($|a| = 25,000\\text{ m/s}^2, |F| = 500\\text{ N}$)."
            },
            "faded_try": "If initial velocity doubles to $200\\text{ m/s}$ with stopping distance unchanged, how does stopping force scale? ($F \\propto u^2$, so stopping force quadruples to $4000\\text{ N}$).",
            "watch_out": "Do not treat stopping distance and force as having a direct linear relation without quadratic velocity coupling.",
            "practice_targets": ["PHYS-NLM-010"]
        },
        {
            "id": "NLM-06",
            "title": "Static vs Kinetic Friction Thresholds",
            "subtitle": "Static friction is a self-adjusting constraint force; kinetic friction acts during sliding",
            "pillar": "P5",
            "story": "Friction opposes RELATIVE sliding between surfaces in contact, not absolute motion in the lab frame. Static friction self-adjusts ($0 \\le f_s \\le \\mu_s N$) to match the applied force. Once sliding occurs, friction drops to kinetic $f_k = \\mu_k N$.",
            "key_idea": "The maximum static threshold is $f_{s,\\max} = \\mu_s N$. If applied force $F < f_{s,\\max}$, the block does NOT move and $f_s = F$, NOT $\\mu_s N$!",
            "how_it_works": [
                "Calculate contact normal force $N$ from equilibrium perpendicular to interface.",
                "Evaluate threshold $f_{s,\\max} = \\mu_s N$.",
                "Compare driving force $F_{\\text{drive}}$ against $f_{s,\\max}$.",
                "If $F_{\\text{drive}} \\le f_{s,\\max}$, $f_s = F_{\\text{drive}}$ and $a=0$. If $F > f_{s,\\max}$, $f = \\mu_k N$ and $a = (F - \\mu_k N)/m$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 140" width="100%" height="140">
  <line x1="40" y1="110" x2="350" y2="110" stroke="#475569" stroke-width="2"/>
  <line x1="50" y1="110" x2="50" y2="20" stroke="#475569" stroke-width="2"/>
  <line x1="50" y1="110" x2="180" y2="30" stroke="#22c55e" stroke-width="3"/>
  <line x1="180" y1="30" x2="180" y2="50" stroke="#eab308" stroke-width="2" stroke-dasharray="3"/>
  <line x1="180" y1="50" x2="340" y2="50" stroke="#ef4444" stroke-width="3"/>
  <circle cx="180" cy="30" r="4" fill="#22c55e"/>
  <text x="185" y="25" font-size="14" font-family="sans-serif" fill="#22c55e" font-weight="bold">f_s,max = μ_s N</text>
  <text x="260" y="42" font-size="14" font-family="sans-serif" fill="#ef4444" font-weight="bold">f_k = μ_k N</text>
  <text x="90" y="85" font-size="14" font-family="sans-serif" fill="#22c55e">Static (f_s = F)</text>
</svg>""",
            "worked_example": "A $10\\text{ kg}$ crate rests on a floor with $\\mu_s = 0.40, \\mu_k = 0.30$. $N = 10 \\times 9.8 = 98\\text{ N} \\implies f_{s,\\max} = 0.40 \\times 98 = 39.2\\text{ N}$. If pulled with $25\\text{ N}$, static friction is exactly $25\\text{ N}$ (not $39.2\\text{ N}$) and the crate remains at rest.",
            "guided_try": {
                "prompt": "If the pull is increased to $50\\text{ N}$, what friction acts on the crate and what is its acceleration?",
                "guide": "Check if $50\\text{ N} > f_{s,\\max}$. If yes, switch to $f_k = \\mu_k N$.",
                "solution": "Since $50 > 39.2\\text{ N}$, the crate slides. Kinetic friction $f_k = 0.30 \\times 98 = 29.4\\text{ N}$. Net force $= 50 - 29.4 = 20.6\\text{ N} \\implies a = 20.6 / 10 = 2.06\\text{ m/s}^2$."
            },
            "faded_try": "If a person of mass $20\\text{ kg}$ sits on top of the crate, what is the new static friction threshold? ($N' = 30 \\times 9.8 = 294\\text{ N} \\implies f_{s,\\max}' = 0.40 \\times 294 = 117.6\\text{ N}$).",
            "watch_out": "Never assume static friction equals $\\mu_s N$ when the applied force is smaller than the threshold.",
            "practice_targets": ["PHYS-NLM-008", "PHYS-NLM-009", "PHYS-NLM-023"]
        },
        {
            "id": "NLM-07",
            "title": "Momentum is a Signed State",
            "subtitle": "Momentum carries the direction of velocity",
            "pillar": "P3",
            "story": "Linear momentum is $\\vec{p} = m\\vec{v}$. In one dimension, its sign carries the direction of velocity. When an object rebounds, the sign of velocity reverses, which makes the magnitude of momentum change $\\Delta p = p_f - p_i$ much larger than a simple speed difference.",
            "key_idea": "Always write signed initial and final momenta explicitly: $p_i = m v_i$, $p_f = m v_f$, then $\\Delta p = p_f - p_i$.",
            "how_it_works": [
                "Choose an explicit positive direction.",
                "Write signed velocities ($+v$ or $-v$).",
                "Compute signed initial and final momenta.",
                "Subtract final minus initial: $\\Delta p = p_f - p_i$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 120" width="100%" height="120">
  <defs><marker id="ar7" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <line x1="30" y1="60" x2="160" y2="60" stroke="#22c55e" stroke-width="3" marker-end="url(#ar7)"/>
  <text x="60" y="45" font-size="14" font-family="sans-serif" fill="#22c55e" font-weight="bold">p_i = +mv_1 (Right)</text>
  <line x1="350" y1="60" x2="220" y2="60" stroke="#ef4444" stroke-width="3" marker-end="url(#ar7)"/>
  <text x="230" y="45" font-size="14" font-family="sans-serif" fill="#ef4444" font-weight="bold">p_f = -mv_2 (Rebound)</text>
  <text x="190" y="105" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#38bdf8">|Δp| = m(v_1 + v_2) ⟹ Directions Add in Rebound!</text>
</svg>""",
            "worked_example": "A $0.20\\text{ kg}$ ball traveling at $+8.0\\text{ m/s}$ hits a wall and rebounds at $-6.0\\text{ m/s}$. $\\Delta p = 0.20(-6.0) - 0.20(+8.0) = -1.2 - 1.6 = -2.8\\text{ kg}\\cdot\\text{m/s}$ (magnitude $2.8\\text{ N}\\cdot\\text{s}$ directed away from wall).",
            "guided_try": {
                "prompt": "At fixed mass, what is the shape and gradient of a momentum-velocity ($p-v$) graph?",
                "guide": "Compare $p = mv$ with $y = mx$.",
                "solution": "Answer: A straight line through the origin $(0, 0)$; slope equals the object's mass $m$."
            },
            "faded_try": "If the ball sticks to the wall ($v_f = 0$) instead of rebounding, what is $\\Delta p$? ($\\Delta p = 0 - 1.6 = -1.6\\text{ kg}\\cdot\\text{m/s}$, much smaller than the rebound case).",
            "watch_out": "Never discard negative signs when an object rebounds; speed difference is $2\\text{ m/s}$, but velocity change is $14\\text{ m/s}$!",
            "practice_targets": ["PHYS-NLM-012", "PHYS-NLM-013"]
        },
        {
            "id": "NLM-07",
            "title": "Impulse and Average Force",
            "subtitle": "The same momentum change can be spread over more time",
            "pillar": "P3",
            "story": "Average force measures how quickly momentum changes: $\\bar{F} = \\frac{\\Delta p}{\\Delta t}$. Increasing the duration of impact $\\Delta t$ drastically reduces the peak force experienced for the exact same momentum change.",
            "key_idea": "This is the universal physics behind moving hands backward while catching a cricket ball, automotive crumple zones, and air bags.",
            "how_it_works": [
                "Evaluate the signed momentum change $\\Delta p = m\\Delta v$.",
                "Identify the interaction duration $\\Delta t$.",
                "Divide $\\Delta p$ by $\\Delta t$ to compute average force $\\bar{F}$.",
                "Check force direction: it points in the direction of $\\Delta p$, not $v_i$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 130" width="100%" height="130">
  <rect x="20" y="20" width="160" height="90" rx="6" fill="#1e293b" stroke="#ef4444" stroke-width="2"/>
  <text x="100" y="45" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#ef4444" font-weight="bold">Stiff Collision (Δt = 0.05s)</text>
  <text x="100" y="75" font-size="16" font-family="sans-serif" text-anchor="middle" fill="#fff">F_avg = 120 N</text>
  <rect x="200" y="20" width="160" height="90" rx="6" fill="#1e293b" stroke="#22c55e" stroke-width="2"/>
  <text x="280" y="45" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#22c55e" font-weight="bold">Cushioned (Δt = 0.30s)</text>
  <text x="280" y="75" font-size="16" font-family="sans-serif" text-anchor="middle" fill="#fff">F_avg = 20 N (6x less!)</text>
</svg>""",
            "worked_example": "A $0.50\\text{ kg}$ ball traveling at $+12\\text{ m/s}$ is caught and stopped in $0.30\\text{ s}$. $\\Delta p = -6.0\\text{ kg}\\cdot\\text{m/s} \\implies \\bar{F} = -6.0 / 0.30 = -20\\text{ N}$.",
            "guided_try": {
                "prompt": "If the ball is stopped stiffly in $0.05\\text{ s}$ instead of $0.30\\text{ s}$, what is the new average force?",
                "guide": "Apply $\\bar{F} = \\Delta p / \\Delta t$.",
                "solution": "Answer: $\\bar{F} = -6.0 / 0.05 = -120\\text{ N}$ (6 times larger force!)."
            },
            "faded_try": "What represents impulse on a force-time ($F-t$) graph? (The area under the $F-t$ curve equals impulse $J = \\int F\\,dt = \\Delta p$).",
            "watch_out": "Momentum ($[M L T^{-1}]$) and force ($[M L T^{-2}]$) are fundamentally different physical quantities.",
            "practice_targets": ["PHYS-NLM-014", "PHYS-NLM-015"]
        },
        {
            "id": "NLM-08",
            "title": "Newton III Interaction Pairs",
            "subtitle": "Equal and opposite does not mean same body",
            "pillar": "P1",
            "story": "A third-law interaction pair belongs to the same physical interaction, has equal magnitude and opposite direction, and acts on DIFFERENT bodies: $\\vec{F}_{AB} = -\\vec{F}_{BA}$.",
            "key_idea": "Use complete naming: 'force on B by A' and 'force on A by B'. Because they act on different bodies, they never cancel on a single free-body diagram.",
            "how_it_works": [
                "Identify both interacting bodies A and B.",
                "Write the two reciprocal force names.",
                "Place each force on the respective body's FBD.",
                "Apply Newton II separately to each body to find their individual accelerations."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 120" width="100%" height="120">
  <defs><marker id="ar8" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <rect x="50" y="35" width="80" height="50" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="90" y="65" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#fff">Body A</text>
  <rect x="250" y="35" width="80" height="50" rx="6" fill="#1e293b" stroke="#a855f7" stroke-width="2"/>
  <text x="290" y="65" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#fff">Body B</text>
  <line x1="50" y1="60" x2="10" y2="60" stroke="#38bdf8" stroke-width="3" marker-end="url(#ar8)"/>
  <text x="5" y="45" font-size="14" font-family="sans-serif" fill="#38bdf8">F_AB</text>
  <line x1="330" y1="60" x2="370" y2="60" stroke="#a855f7" stroke-width="3" marker-end="url(#ar8)"/>
  <text x="345" y="45" font-size="14" font-family="sans-serif" fill="#a855f7">F_BA</text>
  <text x="190" y="105" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#94a3b8">F_AB = - F_BA (Acts on DIFFERENT Bodies!)</text>
</svg>""",
            "worked_example": "Earth pulls an apple downward with gravity force $W$. The apple pulls Earth upward with an equal gravity force $W$. Their accelerations differ drastically ($a_{\\text{apple}} = 9.8\\text{ m/s}^2$ vs $a_{\\text{Earth}} \\approx 10^{-24}\\text{ m/s}^2$) because Earth's mass is massive.",
            "guided_try": {
                "prompt": "What is the third-law reaction partner of the table-on-book normal force?",
                "guide": "Swap the subject and agent in 'table on book'.",
                "solution": "Answer: The book-on-table downward contact force. (NOT the book's weight!)."
            },
            "faded_try": "Why do the action and reaction forces between horse and wagon not produce static equilibrium? (They act on different bodies: pull on wagon accelerates wagon; pull on horse is countered by horse's hooves pushing ground).",
            "watch_out": "Weight and normal force on a book resting on a table are balanced forces on ONE body, NOT a third-law pair.",
            "practice_targets": ["PHYS-NLM-016", "PHYS-NLM-017"]
        },
        {
            "id": "NLM-09",
            "title": "Momentum Conservation in Systems",
            "subtitle": "Choose the system boundary and check external impulse first",
            "pillar": "P3",
            "story": "Total momentum is conserved ONLY for a chosen system when the net external impulse over the interaction is negligible. Internal forces between system members always cancel in pairs.",
            "key_idea": "The conservation equation $\\vec{P}_{\\text{before}} = \\vec{P}_{\\text{after}}$ is valid only after checking that $\\Sigma \\vec{F}_{\\text{ext}} = 0$.",
            "how_it_works": [
                "Draw an explicit system boundary enclosing interacting bodies.",
                "Choose a coordinate positive direction.",
                "List all system momenta before and after interaction.",
                "Verify external forces are negligible during impact; then equate totals."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 120" width="100%" height="120">
  <rect x="30" y="15" width="320" height="90" rx="12" fill="none" stroke="#22c55e" stroke-width="2" stroke-dasharray="6"/>
  <text x="190" y="35" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#22c55e" font-weight="bold">ISOLATED SYSTEM BOUNDARY (ΣF_ext = 0)</text>
  <circle cx="100" cy="70" r="22" fill="#38bdf8"/>
  <text x="100" y="75" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#0f172a" font-weight="bold">m₁</text>
  <circle cx="280" cy="70" r="22" fill="#a855f7"/>
  <text x="280" y="75" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#0f172a" font-weight="bold">m₂</text>
  <text x="190" y="75" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#fff">m₁v₁ + m₂v₂ = const</text>
</svg>""",
            "worked_example": "Two ice skaters (masses $50\\text{ kg}$ and $75\\text{ kg}$) push apart from rest. Initial total $P = 0$. If the $50\\text{ kg}$ skater moves left at $3.0\\text{ m/s}$, the $75\\text{ kg}$ skater moves right at $v_2 = (50 \\times 3.0)/75 = 2.0\\text{ m/s}$.",
            "guided_try": {
                "prompt": "A falling ball speeds up under gravity. Is the momentum of the ball-only system conserved?",
                "guide": "Check if an external force acts on the ball.",
                "solution": "Answer: No; gravity exerts an external downward impulse $\\Delta p = mg\\Delta t$."
            },
            "faded_try": "If the system is defined as (Ball + Earth), is total momentum conserved? (Yes; gravity is then an internal force, and the ball-Earth system momentum is conserved).",
            "watch_out": "Do not claim conservation from one object's perspective when external forces act on it.",
            "practice_targets": ["PHYS-NLM-018", "PHYS-NLM-019"]
        },
        {
            "id": "NLM-10",
            "title": "Recoil, Rockets and Exchanged Momentum",
            "subtitle": "Equal momentum can produce drastically different speeds",
            "pillar": "P3",
            "story": "In explosions, gun recoil, and rocket propulsion, internal forces eject mass. The bullet and rifle acquire equal and opposite momentum: $m_{\\text{bullet}} v_{\\text{bullet}} = m_{\\text{rifle}} v_{\\text{recoil}}$.",
            "key_idea": "Because momentum is equal ($p = mv$), kinetic energy and speed scale inversely with mass: $v \\propto 1/m$ and $K = p^2/(2m) \\propto 1/m$. The lighter projectile carries almost all kinetic energy!",
            "how_it_works": [
                "Write system momentum conservation: $m_1 v_1 + m_2 v_2 = 0$.",
                "Solve for recoil velocity: $v_2 = -\\frac{m_1}{m_2} v_1$.",
                "Evaluate kinetic energy ratio: $K_1 / K_2 = m_2 / m_1$.",
                "For continuous mass ejection (rockets): apply Tsiolkovsky thrust $F = v_{\\text{rel}}\\frac{dm}{dt}$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 120" width="100%" height="120">
  <defs><marker id="ar10" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker></defs>
  <rect x="130" y="40" width="120" height="40" rx="6" fill="#475569"/>
  <text x="190" y="65" font-size="14" font-family="sans-serif" text-anchor="middle" fill="#fff">Rifle (M = 4 kg)</text>
  <circle cx="280" cy="60" r="8" fill="#eab308"/>
  <line x1="290" y1="60" x2="360" y2="60" stroke="#eab308" stroke-width="3" marker-end="url(#ar10)"/>
  <text x="300" y="45" font-size="14" font-family="sans-serif" fill="#eab308">v_b = 400 m/s</text>
  <line x1="130" y1="60" x2="60" y2="60" stroke="#ef4444" stroke-width="3" marker-end="url(#ar10)"/>
  <text x="65" y="45" font-size="14" font-family="sans-serif" fill="#ef4444">v_r = 1.0 m/s</text>
</svg>""",
            "worked_example": "A $4.0\\text{ kg}$ rifle fires a $0.010\\text{ kg}$ bullet at $400\\text{ m/s}$. Recoil velocity $v_{\\text{recoil}} = -(0.010 \\times 400)/4.0 = -1.0\\text{ m/s}$. Bullet kinetic energy is $800\\text{ J}$; rifle recoil kinetic energy is only $2\\text{ J}$!",
            "guided_try": {
                "prompt": "Why does the bullet inflict lethal damage while the rifle recoil is safely absorbed by the shooter's shoulder?",
                "guide": "Compare the kinetic energies using $K = p^2 / (2m)$.",
                "solution": "Answer: With equal momentum $p$, kinetic energy $K = p^2/(2m)$ is 400 times greater in the bullet ($800\\text{ J}$ vs $2\\text{ J}$)."
            },
            "faded_try": "If rifle mass is doubled to $8\\text{ kg}$, what happens to recoil velocity and recoil energy? (Recoil velocity halves to $0.5\\text{ m/s}$; recoil energy halves to $1\\text{ J}$).",
            "watch_out": "Equal momentum does NOT mean equal speed or equal kinetic energy.",
            "practice_targets": ["PHYS-NLM-018", "PHYS-NLM-019"]
        },
        {
            "id": "NLM-11",
            "title": "Read Force from a Motion Graph",
            "subtitle": "Velocity-time slope gives acceleration, which gives net force",
            "pillar": "P4",
            "story": "Motion graphs provide instantaneous dynamic data. The gradient of a velocity-time graph is acceleration: $a = \\frac{dv}{dt}$. Net force is obtained by multiplying slope by mass: $F_{\\text{net}} = m \\times \\text{slope}$.",
            "key_idea": "Horizontal segment ($a = 0$) $\\implies F_{\\text{net}} = 0$. Constant slope $\\implies$ constant net force. Change in direction of slope $\\implies$ reversal of net force.",
            "how_it_works": [
                "Divide the $v-t$ graph into piecewise linear segments.",
                "Compute acceleration from slope: $a = \\frac{v_2 - v_1}{t_2 - t_1}$.",
                "Multiply by mass: $F_{\\text{net}} = m a$.",
                "The area under a force-time graph gives total momentum change $\\Delta p$."
            ],
            "svg_diagram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 130" width="100%" height="130">
  <line x1="40" y1="100" x2="350" y2="100" stroke="#475569" stroke-width="2"/>
  <line x1="40" y1="100" x2="40" y2="20" stroke="#475569" stroke-width="2"/>
  <path d="M 40 100 L 120 40 L 220 40 L 300 100" fill="none" stroke="#38bdf8" stroke-width="3"/>
  <text x="80" y="55" font-size="14" font-family="sans-serif" fill="#22c55e">F > 0</text>
  <text x="170" y="30" font-size="14" font-family="sans-serif" fill="#eab308">F = 0</text>
  <text x="270" y="55" font-size="14" font-family="sans-serif" fill="#ef4444">F &lt; 0</text>
  <text x="350" y="115" font-size="14" font-family="sans-serif" fill="#94a3b8">t</text>
  <text x="25" y="25" font-size="14" font-family="sans-serif" fill="#94a3b8">v</text>
</svg>""",
            "worked_example": "A $2.0\\text{ kg}$ object's velocity rises from $0$ to $10\\text{ m/s}$ in $2\\text{ s}$, stays flat for $3\\text{ s}$, then drops to $0$ in $1\\text{ s}$. Forces: Phase 1: $F = 2 \\times (10/2) = +10\\text{ N}$. Phase 2: $F = 2 \\times 0 = 0\\text{ N}$. Phase 3: $F = 2 \\times (-10/1) = -20\\text{ N}$.",
            "guided_try": {
                "prompt": "What does a horizontal line on a velocity-time graph indicate about the net force acting on the object?",
                "guide": "Evaluate the slope $\\Delta v / \\Delta t$.",
                "solution": "Answer: Zero net force ($F_{\\text{net}} = 0$). Zero slope implies zero acceleration, so forces are balanced."
            },
            "faded_try": "What does the area under a force-time graph represent physically? (Impulse $J = \\Delta p$, the net momentum change).",
            "watch_out": "Never judge force magnitude by the height of the velocity curve; force is governed strictly by the SLOPE.",
            "practice_targets": ["PHYS-NLM-020", "PHYS-NLM-024", "PHYS-NLM-025"]
        }
    ]

    # Render Textbook Unit Card
    def render_textbook_unit(u):
        uid = u["id"]
        how_html = "".join(f"<li>{h}</li>" for h in u["how_it_works"])
        targets_html = "".join(f'<button class="comp-target-btn" onclick="jumpToCore2(\'{t}\')">{t} &#8594;</button>' for t in u["practice_targets"])
        
        return f"""
        <article class="textbook-chapter" id="ch-{uid}">
            <div class="chapter-header">
                <div class="chapter-badge-row">
                    <span class="chapter-id-badge">{uid}</span>
                    <span class="chapter-pillar-pill">Pillar {u['pillar']}</span>
                </div>
                <h3 class="chapter-title">{u['title']}</h3>
                <div class="chapter-subtitle">{u['subtitle']}</div>
            </div>

            <div class="textbook-grid">
                <div class="story-box">
                    <div class="box-tag">📖 Physical Story &bull; What is Happening?</div>
                    <p>{u['story']}</p>
                    <div class="key-idea-callout">
                        <strong>Decisive Key Idea:</strong> {u['key_idea']}
                    </div>
                </div>

                <div class="illustration-box">
                    <div class="box-tag">🎨 Staged Conceptual Illustration</div>
                    {u['svg_diagram']}
                </div>
            </div>

            <div class="method-box">
                <div class="box-tag">⚙️ How It Works (Step-by-Step Method)</div>
                <ol class="method-list">{how_html}</ol>
            </div>

            <div class="pedagogical-quad">
                <div class="quad-item worked-example">
                    <div class="quad-tag">📝 Worked Example</div>
                    <p>{u['worked_example']}</p>
                </div>
                <div class="quad-item guided-try">
                    <div class="quad-tag">🎯 Guided Try</div>
                    <p><strong>Prompt:</strong> {u['guided_try']['prompt']}</p>
                    <div class="guide-note"><em>Guide:</em> {u['guided_try']['guide']}</div>
                    <details class="mini-disclosure">
                        <summary>Show Solution</summary>
                        <div class="mini-disclosure-body">{u['guided_try']['solution']}</div>
                    </details>
                </div>
                <div class="quad-item faded-try">
                    <div class="quad-tag">🔄 Faded Perturbation Try</div>
                    <p>{u['faded_try']}</p>
                </div>
                <div class="quad-item watch-out">
                    <div class="quad-tag">⚠️ Watch Out Trap</div>
                    <p>{u['watch_out']}</p>
                </div>
            </div>

            <div class="chapter-footer">
                <span class="footer-label">Connected Core 2 Practice Items:</span>
                <div class="footer-targets">{targets_html}</div>
            </div>
        </article>
        """

    # =========================================================================
    # TAB 3: CORE 1B RECONSTRUCTION & RECALL
    # =========================================================================
    # Cognitive Dissonance Probes
    probes_html = ""
    for p in reconstruction_data.get("cognitive_dissonance_probes", []):
        pid = p.get("probe_id", "")
        probes_html += f"""
        <div class="probe-card" id="probe-{pid}">
            <div class="probe-header">
                <span class="probe-badge">{pid}</span>
                <span class="probe-title">Cognitive Dissonance Gate</span>
            </div>
            <div class="probe-scenario">
                <strong>Scenario:</strong> {p.get("scenario", "")}
            </div>
            <div class="probe-question">
                <strong>Dissonance Dilemma:</strong> {p.get("dissonance_question", "")}
            </div>
            <div class="unassisted-box">
                <textarea class="attempt-textarea" placeholder="Commit your unassisted physical reasoning before revealing model disclosure..." id="attempt-{pid}"></textarea>
                <button class="commit-attempt-btn" onclick="commitProbe('{pid}')" id="btn-commit-{pid}">Commit Attempt &bull; Reveal Resolution</button>
            </div>
            <div class="probe-resolution hidden" id="res-{pid}">
                <div class="res-tag">💡 Authentic Model Resolution</div>
                <p>{p.get("resolution", "")}</p>
            </div>
        </div>
        """

    # Phenomenological Reconstruction Cycles
    recons_html = ""
    for r in reconstruction_data.get("reconstruction_cycles", []):
        rid = r.get("cycle_id", "")
        phenom = r.get("phenomenon", "")
        std = r.get("standard_derivation", "")
        pr = r.get("phenomenological_reconstruction", {})
        limits = r.get("limiting_boundary_checks", [])
        limits_html = "".join(f"<li><strong>{lc.get('limit', '')}:</strong> {lc.get('physical_consequence', '')}</li>" for lc in limits)
        rf = pr.get("reconstructed_formula", "")
        rf_html = f'<div class="recon-formula"><strong>Reconstructed Invariant Law:</strong> $${rf}$$</div>' if rf else ""
        
        recons_html += f"""
        <div class="recon-card" id="recon-{rid}">
            <div class="recon-header">
                <span class="recon-badge">{rid}</span>
                <h4 class="recon-title">{phenom}</h4>
            </div>
            
            <div class="recon-body">
                <div class="recon-standard">
                    <strong>Standard Isolated Formulation:</strong>
                    <p>{std}</p>
                </div>
                
                <div class="recon-reconstructed">
                    <div class="recon-pivot-tag">✨ Phenomenological Perspective: {pr.get("perspective", "")}</div>
                    <p><strong>Conceptual Pivot:</strong> {pr.get("conceptual_pivot", "")}</p>
                    {rf_html}
                </div>

                <div class="recon-limits">
                    <strong>Limiting Boundary Invariants:</strong>
                    <ul>{limits_html}</ul>
                </div>
            </div>
        </div>
        """

    # 4-Layer Pedagogical DAG
    dag_rows = ""
    for layer in reconstruction_data.get("curriculum_dag_4layers", []):
        dag_rows += f"""
        <tr>
            <td><strong>{layer.get('layer_name', '')}</strong></td>
            <td>{layer.get('description', '')}</td>
            <td><code>{', '.join(layer.get('bound_competencies', []))}</code></td>
        </tr>
        """

    # Assemble All Tabs
    practice_cards_html = "".join(render_practice_card(q, idx) for idx, q in enumerate(bank_data["questions"]))
    textbook_cards_html = "".join(render_textbook_unit(u) for u in textbook_units)

    full_html = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Mechanics (NLM &amp; Friction) &bull; Tri-Modal Master Suite</title>
  <meta name="description" content="Tri-Modal Grade 9 Olympiad Physics Application: Core 1A Learner Textbook + Core 1B Recall & Reconstruction + Core 2 Olympiad Practice Suite.">
  {offline_katex_css_tag}
  <style>
    {base_css}
    
    :root {{
      --primary: #38bdf8;
      --primary-dark: #0284c7;
      --card-bg: #1e293b;
      --body-bg: #0b0f19;
      --border: #334155;
      --c1a-accent: #10b981;
      --c1b-accent: #a855f7;
      --c2-accent: #38bdf8;
    }}
    
    body {{
      background-color: var(--body-bg) !important;
      color: #f8fafc !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
      margin: 0;
      padding: 0;
      font-size: 15px;
    }}
    
    /* Header & Navigation */
    .tri-header {{
      background: #0f172a;
      border-bottom: 1px solid var(--border);
      padding: 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .tri-header-inner {{
      max-width: 1300px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .header-title-box h1 {{
      margin: 0;
      font-size: 22px;
      color: #fff;
    }}
    .header-title-box p {{
      margin: 4px 0 0 0;
      font-size: 14px;
      color: #94a3b8;
    }}
    .tri-tabs-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .tri-tab-btn {{
      background: #1e293b;
      border: 1px solid var(--border);
      color: #94a3b8;
      font-size: 14px;
      font-weight: 700;
      padding: 10px 20px;
      border-radius: 8px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }}
    .tri-tab-btn:hover {{
      border-color: var(--primary);
      color: #fff;
    }}
    .tri-tab-btn.tab-c2.active {{
      background: #0284c7;
      border-color: #38bdf8;
      color: #fff;
    }}
    .tri-tab-btn.tab-c1a.active {{
      background: #059669;
      border-color: #10b981;
      color: #fff;
    }}
    .tri-tab-btn.tab-c1b.active {{
      background: #7c3aed;
      border-color: #a855f7;
      color: #fff;
    }}

    .main-wrap {{
      max-width: 1300px;
      margin: 0 auto;
      padding: 24px 20px;
    }}
    .tab-section {{
      display: none;
    }}
    .tab-section.active {{
      display: block;
    }}
    
    /* Cross Link Buttons */
    .cross-link-btn {{
      background: #0f172a;
      border: 1px solid #475569;
      color: #38bdf8;
      font-size: 13px;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .cross-link-btn:hover {{
      border-color: #38bdf8;
      background: #1e293b;
    }}

    /* Question Cards */
    .question-card {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 10px;
    }}
    .card-source-tag {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .qid-badge {{
      background: #0f172a;
      border: 1px solid #475569;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .band-badge {{
      font-size: 12px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .band-d1 {{ background: #065f46; color: #a7f3d0; }}
    .band-d2 {{ background: #075985; color: #bae6fd; }}
    .band-d3 {{ background: #854d0e; color: #fef08a; }}
    .band-d4 {{ background: #831843; color: #fbcfe8; }}
    .demand-badge {{
      background: #334155;
      color: #e2e8f0;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    
    .stem-container {{
      font-size: 16px;
      line-height: 1.6;
      margin-bottom: 16px;
    }}
    .card-figure-container {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
      text-align: center;
    }}
    .card-figure-caption {{
      font-size: 13px;
      color: #94a3b8;
      margin-top: 6px;
      font-style: italic;
    }}

    /* Options */
    .options-container {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin: 16px 0;
    }}
    .opt-btn {{
      background: #0f172a;
      border: 1px solid var(--border);
      color: #fff;
      padding: 14px 18px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 15px;
      text-align: left;
      display: flex;
      align-items: center;
      gap: 12px;
      min-height: 52px;
    }}
    .opt-btn:hover {{
      border-color: var(--primary);
    }}
    .opt-key {{
      background: #1e293b;
      border: 1px solid #475569;
      color: var(--primary);
      font-weight: 800;
      width: 30px;
      height: 30px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .opt-btn.correct {{
      background: rgba(34, 197, 94, 0.15) !important;
      border-color: #22c55e !important;
    }}
    .opt-btn.incorrect {{
      background: rgba(239, 68, 68, 0.15) !important;
      border-color: #ef4444 !important;
    }}

    .feedback-banner {{
      padding: 14px 18px;
      border-radius: 8px;
      margin: 14px 0;
    }}
    .feedback-banner.correct {{ background: rgba(34, 197, 94, 0.15); border: 1px solid #22c55e; color: #86efac; }}
    .feedback-banner.incorrect {{ background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; }}

    /* Hints & Solutions */
    details {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-top: 12px;
      overflow: hidden;
    }}
    summary {{
      padding: 14px 18px;
      font-weight: 700;
      color: var(--primary);
      cursor: pointer;
      min-height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .hints-body, .solution-body {{
      padding: 16px;
      border-top: 1px solid var(--border);
      font-size: 14px;
      line-height: 1.6;
    }}
    .hint-tier {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 10px;
    }}
    .hint-tier-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .hint-unlock-btn {{
      background: #0369a1;
      border: 1px solid var(--primary);
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

    /* TAB 2: Core 1A Textbook Styles */
    .textbook-chapter {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 32px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }}
    .chapter-header {{
      border-bottom: 2px solid #059669;
      padding-bottom: 14px;
      margin-bottom: 20px;
    }}
    .chapter-badge-row {{
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 6px;
    }}
    .chapter-id-badge {{
      background: #059669;
      color: #fff;
      font-weight: 800;
      font-size: 14px;
      padding: 4px 10px;
      border-radius: 6px;
    }}
    .chapter-pillar-pill {{
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid #10b981;
      color: #a7f3d0;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
    }}
    .chapter-title {{
      font-size: 20px;
      margin: 4px 0;
      color: #fff;
    }}
    .chapter-subtitle {{
      color: #94a3b8;
      font-size: 14px;
    }}

    .textbook-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }}
    .story-box, .illustration-box, .method-box {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
    }}
    .box-tag {{
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #10b981;
      margin-bottom: 10px;
    }}
    .key-idea-callout {{
      background: rgba(16, 185, 129, 0.1);
      border-left: 3px solid #10b981;
      padding: 10px 14px;
      border-radius: 4px;
      margin-top: 14px;
      color: #d1fae5;
    }}
    .method-list {{
      padding-left: 20px;
      line-height: 1.7;
    }}

    .pedagogical-quad {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 20px;
    }}
    .quad-item {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .quad-tag {{
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .worked-example .quad-tag {{ color: #38bdf8; }}
    .guided-try .quad-tag {{ color: #fbbf24; }}
    .faded-try .quad-tag {{ color: #a855f7; }}
    .watch-out .quad-tag {{ color: #f87171; }}
    .watch-out {{ background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.3); }}

    .chapter-footer {{
      margin-top: 20px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .footer-targets {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .comp-target-btn {{
      background: #0f172a;
      border: 1px solid #475569;
      color: #38bdf8;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
    }}
    .comp-target-btn:hover {{
      border-color: #38bdf8;
      background: #1e293b;
    }}

    /* TAB 3: Core 1B Reconstruction Styles */
    .review-banner {{
      border: 2px solid #7c3aed;
      background: rgba(124, 58, 237, 0.1);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
      line-height: 1.6;
    }}
    .review-banner h2 {{
      margin: 0 0 6px 0;
      color: #c084fc;
    }}
    .probe-card, .recon-card {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 22px;
      margin-bottom: 24px;
    }}
    .probe-header, .recon-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .probe-badge {{
      background: #7c3aed;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .recon-badge {{
      background: #0284c7;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .probe-question {{
      background: #0f172a;
      border-left: 3px solid #7c3aed;
      padding: 12px 16px;
      border-radius: 4px;
      margin: 12px 0;
      color: #e9d5ff;
    }}
    .attempt-textarea {{
      width: 100%;
      min-height: 90px;
      background: #0f172a;
      border: 1px solid #475569;
      color: #f8fafc;
      padding: 12px;
      border-radius: 8px;
      font-family: inherit;
      font-size: 14px;
      box-sizing: border-box;
      margin-top: 8px;
    }}
    .commit-attempt-btn {{
      background: #7c3aed;
      border: none;
      color: #fff;
      font-weight: 700;
      font-size: 14px;
      padding: 10px 18px;
      border-radius: 6px;
      cursor: pointer;
      min-height: 48px;
      margin-top: 8px;
      display: inline-flex;
      align-items: center;
    }}
    .commit-attempt-btn:hover {{
      background: #6d28d9;
    }}
    .probe-resolution {{
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid #10b981;
      border-radius: 8px;
      padding: 14px 16px;
      margin-top: 14px;
    }}
    .res-tag {{
      font-weight: 800;
      color: #10b981;
      margin-bottom: 6px;
    }}

    .recon-pivot-tag {{
      color: #38bdf8;
      font-weight: 800;
      margin-bottom: 6px;
    }}
    .recon-formula {{
      background: #0f172a;
      padding: 12px;
      border-radius: 6px;
      margin: 10px 0;
    }}
    .dag-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
    }}
    .dag-table th, .dag-table td {{
      border: 1px solid var(--border);
      padding: 10px 14px;
      text-align: left;
      font-size: 14px;
    }}
    .dag-table th {{
      background: #0f172a;
      color: #c084fc;
    }}

    .hidden {{ display: none !important; }}
    
    @media (max-width: 800px) {{
      .textbook-grid, .pedagogical-quad {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <header class="tri-header">
    <div class="tri-header-inner">
      <div class="header-top">
        <div class="header-title-box">
          <h1>⚡ Mechanics (NLM &amp; Friction) &bull; Tri-Modal Master Suite</h1>
          <p>Tripartite Physics System: Core 1A (Textbook) &bull; Core 1B (Reconstruction) &bull; Core 2 (Practice)</p>
        </div>
        <div class="card-source-tag">
          <span class="qid-badge">GRADE-9</span>
          <span class="band-badge band-d2">CBSE + IIT-JEE</span>
          <span class="demand-badge demand-apply">100% GOLDEN</span>
        </div>
      </div>
      
      <div class="tri-tabs-row">
        <button class="tri-tab-btn tab-c1a active" onclick="switchTab('c1a')" id="btn-tab-c1a">
          <span>📖 Core 1A: Learner Textbook (11 Units)</span>
        </button>
        <button class="tri-tab-btn tab-c1b" onclick="switchTab('c1b')" id="btn-tab-c1b">
          <span>🧠 Core 1B: Recall &amp; Reconstruction</span>
        </button>
        <button class="tri-tab-btn tab-c2" onclick="switchTab('c2')" id="btn-tab-c2">
          <span>🎯 Core 2: Practice Suite (25 Cards)</span>
        </button>
      </div>
    </div>
  </header>

  <main class="main-wrap">
    <!-- TAB 1: CORE 1A TEXTBOOK -->
    <section class="tab-section active" id="sec-c1a">
      <div style="margin-bottom: 20px;">
        <h2 style="font-size: 20px; color: #10b981; margin: 0 0 6px 0;">Core 1A &bull; Conceptual Foundation &amp; First-Move Textbook</h2>
        <p style="color: #94a3b8; margin: 0;">Authored directly from the Golden Benchmark Standard (physics-nlm-revised-core1.pdf). Build the force-and-momentum reasoning system before touching problems.</p>
      </div>
      {textbook_cards_html}
    </section>

    <!-- TAB 2: CORE 1B RECONSTRUCTION -->
    <section class="tab-section" id="sec-c1b">
      <div class="review-banner">
        <h2>CORE 1B RECONSTRUCTION &bull; UNASSISTED RETRIEVAL</h2>
        <p>Test conceptual retention of Newton's Laws and friction thresholds without looking back at the textbook. Reconstruct the Atwood invariant, the reaction cone, and resolve cognitive dissonance paradoxes.</p>
      </div>
      
      <h3 style="color: #c084fc; font-size: 18px; margin: 24px 0 12px 0;">Stage 1 &bull; Cognitive Dissonance Retrieval Gates</h3>
      {probes_html}

      <h3 style="color: #38bdf8; font-size: 18px; margin: 32px 0 12px 0;">Stage 2 &bull; Phenomenological Reconstruction Cycles</h3>
      {recons_html}

      <h3 style="color: #f8fafc; font-size: 18px; margin: 32px 0 12px 0;">Stage 3 &bull; 4-Layer Pedagogical Dependency Graph (DAG)</h3>
      <table class="dag-table">
        <thead>
          <tr><th>Curriculum Layer</th><th>Pedagogical Function</th><th>Bound Competencies</th></tr>
        </thead>
        <tbody>
          {dag_rows}
        </tbody>
      </table>
    </section>

    <!-- TAB 3: CORE 2 PRACTICE CARDS -->
    <section class="tab-section" id="sec-c2">
      <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
          <h2 style="font-size: 20px; color: #38bdf8; margin: 0 0 6px 0;">Core 2 &bull; Master Olympiad Practice Suite</h2>
          <p style="color: #94a3b8; margin: 0;">25 authentic examination challenge cards with progressive prompt reveals and 5-step mathematical proofs.</p>
        </div>
      </div>
      {practice_cards_html}
    </section>
  </main>

  <script>
    function switchTab(tabId) {{
      document.querySelectorAll('.tri-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
      
      const btn = document.getElementById('btn-tab-' + tabId);
      const sec = document.getElementById('sec-' + tabId);
      if (btn && sec) {{
        btn.classList.add('active');
        sec.classList.add('active');
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function jumpToCore1A(compId) {{
      switchTab('c1a');
      const target = document.getElementById('ch-' + compId);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        target.style.borderColor = '#10b981';
        target.style.boxShadow = '0 0 25px rgba(16, 185, 129, 0.4)';
        setTimeout(() => {{
          target.style.borderColor = '#334155';
          target.style.boxShadow = 'none';
        }}, 3000);
      }}
    }}

    function jumpToCore1B(probeOrReconId) {{
      switchTab('c1b');
      const target = document.getElementById(probeOrReconId) || document.getElementById('recon-' + probeOrReconId) || document.getElementById('probe-' + probeOrReconId);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    function jumpToCore2(qid) {{
      switchTab('c2');
      const target = document.getElementById('card-' + qid);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        target.style.borderColor = '#38bdf8';
        target.style.boxShadow = '0 0 25px rgba(56, 189, 248, 0.4)';
        setTimeout(() => {{
          target.style.borderColor = '#334155';
          target.style.boxShadow = 'none';
        }}, 3000);
      }}
    }}

    function selectOption(qid, optKey, correctKey) {{
      const card = document.getElementById('card-' + qid);
      if (!card) return;
      
      const buttons = card.querySelectorAll('.opt-btn');
      buttons.forEach(btn => btn.classList.remove('correct', 'incorrect'));
      
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
      if (rev) rev.classList.remove('hidden');
      const box = document.getElementById('hint-tier-' + tier + '-' + qid);
      if (box) box.classList.remove('locked');
      const indicator = document.getElementById('hint-indicator-' + qid);
      if (indicator) indicator.textContent = 'Tier ' + tier + ' of 3 Unlocked';
    }}

    function commitProbe(pid) {{
      const res = document.getElementById('res-' + pid);
      if (res) res.classList.remove('hidden');
      const btn = document.getElementById('btn-commit-' + pid);
      if (btn) {{
        btn.textContent = 'Attempt Committed ✓';
        btn.style.background = '#059669';
      }}
    }}
  </script>
</body>
</html>
"""

    raw_path = REPO_ROOT / "scratch/_raw_mechanics_tri_modal.html"
    print(f"Writing raw intermediate file to {raw_path}...")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    output_path = REPO_ROOT / "standalone/practice/core2-physics-mechanics-grade9-master.html"
    print("Executing Node.js KaTeX pre-rendering engine...")
    prerender_html(str(raw_path), str(output_path))

    # Copy to public
    public_path = REPO_ROOT / "public/standalone/practice/core2-physics-mechanics-grade9-master.html"
    shutil.copyfile(output_path, public_path)

    # Copy to brain artifact directory
    artifact_dir = Path("C:/Users/reall/.gemini/antigravity/brain/40014ef9-8d66-475e-aff1-d6e53797ebbd")
    if artifact_dir.exists():
        shutil.copyfile(output_path, artifact_dir / "physics_master_app.html")
        print(f"Copied to brain artifact directory: {artifact_dir / 'physics_master_app.html'}")

    print(f"\n[SUCCESS] Compiled Tri-Modal Mechanics Master App to:")
    print(f"  -> {output_path}")
    print(f"  -> {public_path}")

if __name__ == "__main__":
    compile_tri_modal_mechanics()
