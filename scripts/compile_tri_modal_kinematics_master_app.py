# scripts/compile_tri_modal_kinematics_master_app.py
"""
Compile Tri-Modal Master Tablet Application for Kinematics (1D Motion, 2D Projectiles & Relative Frames).
Architecture:
- Tab 1: Core 2 Practice Suite (25 Olympiad Cards with 5-Step Proofs & Prompt-Reveals)
- Tab 2: Core 1A Learner Textbook (11 Comprehensive Chapters from Golden PDF)
- Tab 3: Core 1B Recall & Reconstruction (Cognitive Dissonance Probes, Invariant Cycles, & First-Move Atlas)

12.7" Tablet Touch Screen Specification:
- Non-occluding relative header inside .app-container
- Offline Base64 KaTeX font-faces embedded directly into <style id="katex-offline-font-faces">
- Touch targets >= 48px floor
- Non-squished hint unlock buttons
- Node.js static DOM KaTeX pre-rendering (zero unrendered math)
"""

import json
import re
import os
import sys
import shutil
from pathlib import Path
import base64

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.physics_prerender_engine import prerender_html

def compile_tri_modal_kinematics():
    print(f"\n{'='*80}")
    print("COMPILING TRI-MODAL MASTER TABLET APP: KINEMATICS (1D & 2D MOTION)")
    print("Tripartite Architecture: Core 1A (Learn) <-> Core 1B (Recall) <-> Core 2 (Practice)")
    print(f"{'='*80}\n")

    # Load Data
    bank_path = REPO_ROOT / "TEST/physics-research/question_bank_kinematics_grade9.v1.json"
    ontology_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_kinematics_ontology.v1.json"
    reconstruction_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_kinematics_reconstruction.v1.json"
    adapters_path = REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json"

    with open(bank_path, "r", encoding="utf-8") as f:
        bank_data = json.load(f)
    with open(ontology_path, "r", encoding="utf-8") as f:
        ontology_data = json.load(f)
    with open(reconstruction_path, "r", encoding="utf-8") as f:
        reconstruction_data = json.load(f)
    with open(adapters_path, "r", encoding="utf-8") as f:
        adapters_data = json.load(f)["topic_adapters"]["kinematics-1d-2d"]

    # Extract base64 KaTeX & base CSS from existing master
    circles_html_path = REPO_ROOT / "standalone/practice/core2-mathematics-circles-grade9-master.html"
    with open(circles_html_path, "r", encoding="utf-8") as f:
        circles_html = f.read()

    css_link_match = re.search(r'<link id="offline-katex-css"[^>]+>', circles_html)
    offline_katex_css_tag = css_link_match.group(0) if css_link_match else ""

    b64_font_match = re.search(r'href="data:text/css;base64,([^"]+)"', circles_html)
    decoded_katex_css = ""
    if b64_font_match:
        try:
            decoded_katex_css = base64.b64decode(b64_font_match.group(1)).decode('utf-8', errors='ignore')
        except Exception:
            pass

    style_match = re.search(r'<style>([\s\S]*?)</style>', circles_html)
    base_css = style_match.group(1) if style_match else ""

    # =========================================================================
    # TAB 1: CORE 2 PRACTICE CARDS (25 Questions)
    # =========================================================================
    def render_practice_card(q, index):
        qid = q["question_id"]
        comp = q.get("subtopic_competency_ref", "KIN-01")
        band = q.get("qrt_contract", {}).get("difficulty_band", "D2")
        demand = q.get("qrt_contract", {}).get("primary_demand", "APPLY")
        comp_title = adapters_data.get("subtopic_competency_map", {}).get(comp, {}).get("title", comp)
        prov = q.get("provenance", {})
        prov_src = prov.get("source_fixture", "Grade 9 Benchmark Fixture")
        prov_exam = prov.get("exam_provenance", "Olympiad / JEE-Foundation")
        
        # Figure SVG
        fig_html = ""
        fig = q.get("figure", {})
        if fig and fig.get("svg"):
            fig_html = f"""
            <div class="card-figure-container">
                {fig['svg']}
                <div class="card-figure-caption">{fig.get('caption', '')}</div>
            </div>
            """

        # Options
        options = q.get("options", {})
        correct_key = q.get("correct_answer", "A")
        distractors = q.get("distractor_diagnostics", {})
        
        options_html = ""
        for opt_key in sorted(options.keys()):
            opt_val = options[opt_key]
            diag = distractors.get(opt_key, {}).get("diagnostic", "")
            is_correct = "true" if opt_key == correct_key else "false"
            options_html += f"""
            <button class="opt-btn" data-opt="{opt_key}" data-correct="{is_correct}" onclick="selectOption('{qid}', '{opt_key}', {is_correct})">
                <span class="opt-key">{opt_key}</span>
                <span class="opt-text">{opt_val}</span>
            </button>
            <div class="opt-diag" id="diag-{qid}-{opt_key}" style="display:none;" data-correct="{is_correct}">{diag}</div>
            """

        # Progressive Hints (3 Tiers)
        hints = q.get("progressive_hints", [])
        hints_html = ""
        for h in hints:
            tier = h.get("tier", 1)
            title = h.get("title", f"Tier {tier} Hint")
            prompt = h.get("prompt_question", "")
            reveal = h.get("reveal_text", "")
            hints_html += f"""
            <div class="hint-tier" id="hint-{qid}-{tier}">
                <div class="hint-tier-header">
                    <span class="hint-tier-title">Tier {tier}: {title}</span>
                    <button class="hint-unlock-btn" onclick="unlockHint('{qid}', {tier})">Unlock Hint</button>
                </div>
                <div class="hint-prompt">{prompt}</div>
                <div class="hint-reveal" id="reveal-{qid}-{tier}" style="display:none;">{reveal}</div>
            </div>
            """

        # 5-Step Model Proof Reasoning Ladder
        proof = q.get("model_proof", {})
        ladder = proof.get("reasoning_ladder", {})
        steps = proof.get("derivation_steps", [])
        steps_html = "".join(f"<li>{s}</li>" for s in steps)
        
        ladder_html = f"""
        <div class="ladder-step"><strong>1. Understand:</strong> {ladder.get('understand', '')}</div>
        <div class="ladder-step"><strong>2. Represent:</strong> {ladder.get('represent', '')}</div>
        <div class="ladder-step"><strong>3. Connect:</strong> {ladder.get('connect', '')}</div>
        <div class="ladder-step"><strong>4. Calculate:</strong> {ladder.get('calculate', '')}</div>
        <div class="ladder-step"><strong>5. Interpret:</strong> {ladder.get('interpret', '')}</div>
        """

        # Independent Check
        check = q.get("independent_check", {})
        method = check.get("method", "INDEPENDENT_CHECK")
        dim_formula = check.get("dimensional_formula", "")
        limits = check.get("limiting_cases", [])
        limits_html = "".join(f"<li><strong>{lc.get('condition', '')}:</strong> {lc.get('expected', '')}</li>" for lc in limits)
        quick = check.get("quick_check", "")
        watch = check.get("watch_out", "")

        return f"""
        <div class="question-card" id="card-{qid}" data-qid="{qid}" data-comp="{comp}" data-band="{band}">
            <div class="card-header">
                <div class="card-source-tag">
                    <span class="qid-badge">{qid}</span>
                    <span class="band-badge band-{band.lower()}">{band}</span>
                    <span class="demand-badge">{demand}</span>
                </div>
                <div class="card-comp-tag">
                    <button class="cross-link-btn" onclick="jumpToChapter('ch-{comp}')" title="Read Core 1A Textbook Chapter">
                        📘 {comp}: {comp_title} &#8594;
                    </button>
                </div>
            </div>

            <div class="card-provenance-bar">
                <span class="prov-src">Authority: {prov_src}</span> &bull; 
                <span class="prov-exam">{prov_exam}</span>
            </div>

            <div class="stem-container">
                {q.get('stem', '')}
            </div>

            {fig_html}

            <div class="options-container">{options_html}</div>

            <div class="feedback-banner" id="feedback-{qid}" style="display:none;"></div>

            <details class="hints-accordion">
                <summary>💡 Progressive Hints (3 Tiers: Physics &rarr; Model &rarr; First Move)</summary>
                <div class="hints-body">{hints_html}</div>
            </details>

            <details class="solution-accordion">
                <summary>📐 Complete 5-Step Model Proof &amp; Independent Verification</summary>
                <div class="solution-body">
                    <div class="solution-section-title">5-Step Pedagogical Reasoning Ladder</div>
                    <div class="ladder-container">{ladder_html}</div>
                    
                    <div class="solution-section-title">Formal Mathematical Derivation</div>
                    <ol class="derivation-list">{steps_html}</ol>
                    <div class="final-expression-box">
                        <strong>Final Expression:</strong> $${proof.get('final_expression', '')}$$
                    </div>

                    <div class="solution-section-title">Multi-Engine Independent Checks ({method})</div>
                    <div class="indep-check-box">
                        <div><strong>Dimensional Homogeneity:</strong> $${dim_formula}$$</div>
                        <div><strong>Limiting Boundary Cases:</strong>
                            <ul class="limiting-cases-list">{limits_html}</ul>
                        </div>
                        {f'<div><strong>Quick Check:</strong> {quick}</div>' if quick else ''}
                        {f'<div><strong>Watch Out:</strong> <span class="watch-out-text">{watch}</span></div>' if watch else ''}
                    </div>
                </div>
            </details>
        </div>
        """

    practice_cards_html = "".join(render_practice_card(q, i) for i, q in enumerate(bank_data["questions"]))

    # =========================================================================
    # TAB 2: CORE 1A LEARNER TEXTBOOK (11 Chapters from Golden PDF)
    # =========================================================================
    TEXTBOOK_UNITS = [
        {
            "id": "KIN-01",
            "pillar": "P1",
            "title": "Distance and Displacement",
            "subtitle": "Path length and endpoint change answer different questions",
            "story": "Distance counts the total path traveled. Displacement compares only the final and initial positions, with sign set by the chosen coordinate axis.",
            "key_idea": "Reversal is the decisive clue. Once the object turns around, distance and |displacement| diverge. $|\\Delta x| \\le s$ always.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="40" y1="60" x2="460" y2="60" stroke="#475569" stroke-width="2"/>
                <!-- Ticks -->
                <line x1="80" y1="50" x2="80" y2="70" stroke="#94a3b8" stroke-width="2"/><text x="80" y="90" fill="#94a3b8" font-size="14" text-anchor="middle">-6</text>
                <line x1="160" y1="50" x2="160" y2="70" stroke="#94a3b8" stroke-width="2"/><text x="160" y="90" fill="#94a3b8" font-size="14" text-anchor="middle">-2</text>
                <line x1="200" y1="50" x2="200" y2="70" stroke="#38bdf8" stroke-width="3"/><text x="200" y="90" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">0 (Start)</text>
                <line x1="340" y1="50" x2="340" y2="70" stroke="#10b981" stroke-width="2"/><text x="340" y="90" fill="#10b981" font-size="14" text-anchor="middle">+7 (Turn)</text>
                <!-- Forward Leg -->
                <path d="M 200 50 Q 270 20 340 50" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrow)"/>
                <text x="270" y="25" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">+7 m</text>
                <!-- Backward Leg -->
                <path d="M 340 70 Q 230 110 120 70" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
                <text x="230" y="115" fill="#f43f5e" font-size="14" font-weight="bold" text-anchor="middle">-11 m</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Mark start, turnaround points, and finish on one signed number line.",
                "Represent: Keep each leg signed for displacement ($\\Delta x = x_f - x_i$); use absolute leg length for distance ($s = \\sum |\\Delta x_k|$).",
                "Build: Write $\\Delta x = x_f - x_i$; Distance = $\\sum |\\text{leg}|$.",
                "Check: $|\\Delta x|$ can never exceed distance."
            ],
            "worked_example": "A robot moves $+7\\text{ m}$, then $-11\\text{ m}$, then $+2\\text{ m}$. Displacement: $\\Delta x = 7 - 11 + 2 = -2\\text{ m}$. Distance: $s = |7| + |-11| + |2| = 20\\text{ m}$.",
            "watch_out": "Do not convert every signed leg into a positive number before computing net displacement.",
            "quick_check": "A runner returns to the start after traveling $18\\text{ m}$. Distance = $18\\text{ m}$, Displacement = $0\\text{ m}$.",
            "practice_targets": ["PHYS-KIN-001"]
        },
        {
            "id": "KIN-02",
            "pillar": "P2",
            "title": "Average Speed and Average Velocity",
            "subtitle": "Same elapsed clock time, different numerator",
            "story": "Both averages share the identical total elapsed clock time $\\Delta t_{\\text{tot}}$. But average velocity uses net vector displacement, while average speed uses total scalar path distance.",
            "key_idea": "On any closed round trip, displacement is zero, so average velocity is identically zero ($v_{\\text{avg}} = 0$) even though average speed is strictly positive ($s_{\\text{avg}} > 0$).",
            "svg_diagram": """
            <svg viewBox="0 0 500 110" style="max-width:100%; height:auto;">
                <rect x="50" y="30" width="180" height="40" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
                <text x="140" y="55" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Outward: 60 km @ 40 km/h</text>
                <rect x="270" y="30" width="180" height="40" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
                <text x="360" y="55" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">Return: 60 km @ 30 km/h</text>
                <text x="250" y="95" fill="#94a3b8" font-size="14" text-anchor="middle">Round trip: Net displacement = 0 m &bull; Distance = 120 km</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Identify complete trip duration and whether origin is revisited.",
                "Represent: Total elapsed time $\\Delta t_{\\text{tot}} = t_1 + t_2 + \\dots$; Net displacement $\\Delta x = x_f - x_i$.",
                "Build: $v_{\\text{avg}} = \\frac{\\Delta x}{\\Delta t_{\\text{tot}}}$; $s_{\\text{avg}} = \\frac{\\text{total distance}}{\\Delta t_{\\text{tot}}}$.",
                "Check: $|v_{\\text{avg}}| \\le s_{\\text{avg}}$ always."
            ],
            "worked_example": "A car travels $60\\text{ km}$ at $40\\text{ km/h}$ ($1.5\\text{ h}$) and returns $60\\text{ km}$ at $30\\text{ km/h}$ ($2.0\\text{ h}$). Round trip: $\\Delta x = 0 \\implies v_{\\text{avg}} = 0$. Total distance = $120\\text{ km}$, total time = $3.5\\text{ h} \\implies s_{\\text{avg}} = \\frac{120}{3.5} \\approx 34.3\\text{ km/h}$.",
            "watch_out": "Never equate average speed to the magnitude of average velocity when the path contains turns or reversals.",
            "quick_check": "If an athlete completes one full lap of a $400\\text{ m}$ track in $50\\text{ s}$, average velocity is $0\\text{ m/s}$, average speed is $8\\text{ m/s}$.",
            "practice_targets": ["PHYS-KIN-010"]
        },
        {
            "id": "KIN-03",
            "pillar": "P3",
            "title": "Equal-Time and Equal-Distance Weighting",
            "subtitle": "What is equal determines the weighting: time vs distance",
            "story": "When motion is divided into segments, the average speed depends fundamentally on whether the intervals have equal duration or equal distance.",
            "key_idea": "Equal-time weighting yields arithmetic mean $v_{\\text{avg}} = \\frac{v_1 + v_2}{2}$. Equal-distance weighting yields harmonic mean $v_{\\text{avg}} = \\frac{2 v_1 v_2}{v_1 + v_2}$, because the traveler spends more time at the slower speed.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Equal Distance Box -->
                <rect x="40" y="25" width="200" height="60" rx="8" fill="#1e293b" stroke="#a855f7" stroke-width="1.5"/>
                <text x="140" y="48" fill="#a855f7" font-size="14" font-weight="bold" text-anchor="middle">Equal Distance (d, d)</text>
                <text x="140" y="72" fill="#e2e8f0" font-size="14" text-anchor="middle">Harmonic: 2v1*v2 / (v1 + v2)</text>
                <!-- Equal Time Box -->
                <rect x="260" y="25" width="200" height="60" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
                <text x="360" y="48" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Equal Time (t, t)</text>
                <text x="360" y="72" fill="#e2e8f0" font-size="14" text-anchor="middle">Arithmetic: (v1 + v2) / 2</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Check problem statement: are distances equal ($d_1 = d_2$) or times equal ($t_1 = t_2$)?",
                "Represent: For equal distance, express leg times $t_1 = d/v_1, t_2 = d/v_2$; for equal time, express leg distances $d_1 = v_1 t, d_2 = v_2 t$.",
                "Build: Divide total distance by total time: $v_{\\text{avg}} = \\frac{2d}{d/v_1 + d/v_2} = \\frac{2 v_1 v_2}{v_1 + v_2}$.",
                "Check: Harmonic mean is strictly less than arithmetic mean whenever $v_1 \\ne v_2$."
            ],
            "worked_example": "Driving half the distance at $30\\text{ km/h}$ and half at $60\\text{ km/h}$: $v_{\\text{avg}} = \\frac{2(30)(60)}{30 + 60} = \\frac{3600}{90} = 40\\text{ km/h}$ (not $45\\text{ km/h}$!).",
            "watch_out": "Using $(v_1 + v_2)/2$ for equal-distance segments is the single most common student trap in kinematics.",
            "quick_check": "If $v_2 \\to 0$ on the second half of a distance, $v_{\\text{avg}} \\to 0$ because the car never finishes the trip.",
            "practice_targets": ["PHYS-KIN-002"]
        },
        {
            "id": "KIN-04",
            "pillar": "P4",
            "title": "Velocity Sign, Acceleration Sign and Reversal",
            "subtitle": "Negative does not mean slowing down",
            "story": "On a signed 1D axis, plus and minus signs represent physical directions. The sign of velocity indicates direction of travel. The sign of acceleration indicates the direction in which velocity changes.",
            "key_idea": "Speeding up occurs when velocity and acceleration share the same sign ($v \\cdot a > 0$). Slowing down occurs when velocity and acceleration have opposite signs ($v \\cdot a < 0$). Negative acceleration speeds up a body moving in the negative direction.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="60" x2="450" y2="60" stroke="#475569" stroke-width="2"/>
                <!-- Left Moving Particle -->
                <circle cx="250" cy="60" r="8" fill="#f43f5e"/>
                <!-- v vector pointing left -->
                <line x1="250" y1="40" x2="160" y2="40" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="160,35 150,40 160,45" fill="#f43f5e"/>
                <text x="200" y="30" fill="#f43f5e" font-size="14" font-weight="bold">v = -4 m/s (moves left)</text>
                <!-- a vector pointing left -->
                <line x1="250" y1="80" x2="180" y2="80" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="180,75 170,80 180,85" fill="#f43f5e"/>
                <text x="210" y="100" fill="#f43f5e" font-size="14" font-weight="bold">a = -3 m/s² (speeds up left!)</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Read signs of initial velocity $u$ and acceleration $a$ along the chosen coordinate axis.",
                "Represent: Draw velocity arrow and acceleration arrow on the number line.",
                "Build: Calculate $v(t) = u + at$ and observe whether $|v(t)|$ increases or decreases.",
                "Check: Turnaround occurs at $v = 0$; acceleration can remain constant and non-zero across the turnaround."
            ],
            "worked_example": "A particle has $u = -4\\text{ m/s}$ and $a = -3\\text{ m/s}^2$ for $2\\text{ s}$. $v = -4 + (-3)(2) = -10\\text{ m/s}$. Speed $|v|$ increased from $4\\text{ m/s}$ to $10\\text{ m/s}$!",
            "watch_out": "Never assume negative acceleration automatically means deceleration.",
            "quick_check": "A particle with $v = +12\\text{ m/s}$ and $a = -4\\text{ m/s}^2$ slows down until $t = 3\\text{ s}$ ($v = 0$), then reverses and speeds up in the negative direction.",
            "practice_targets": ["PHYS-KIN-015"]
        },
        {
            "id": "KIN-05",
            "pillar": "P3",
            "title": "Build the State Before Choosing an Equation",
            "subtitle": "UVATS is a model check, not a formula list",
            "story": "Uniform acceleration motion is completely described by 5 parameters: initial velocity $u$, final velocity $v$, acceleration $a$, time $t$, and displacement $s$.",
            "key_idea": "Each of the 4 kinematic quad equations omits exactly one parameter. Select the single equation that excludes the unmeasured, unrequested variable.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <rect x="50" y="20" width="400" height="80" rx="8" fill="#1e293b" stroke="#334155"/>
                <text x="80" y="50" fill="#94a3b8" font-size="14">u = 5 m/s</text>
                <text x="160" y="50" fill="#38bdf8" font-size="14" font-weight="bold">v = ? (target)</text>
                <text x="250" y="50" fill="#94a3b8" font-size="14">a = 2 m/s²</text>
                <text x="330" y="50" fill="#f43f5e" font-size="14">t: absent</text>
                <text x="390" y="50" fill="#94a3b8" font-size="14">s = 24 m</text>
                <text x="250" y="85" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">Omit t &rarr; v² = u² + 2as</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Verify acceleration is strictly constant ($da/dt = 0$).",
                "Represent: Construct UVATS table listing knowns, unknown target, and excluded parameter.",
                "Build: Pick equation: omit $s \\to v = u + at$; omit $v \\to s = ut + \\frac{1}{2}at^2$; omit $t \\to v^2 = u^2 + 2as$; omit $a \\to s = \\frac{u+v}{2}t$.",
                "Check: Verify dimensional consistency and limits ($a \\to 0$)."
            ],
            "worked_example": "A car accelerates at $2\\text{ m/s}^2$ from $5\\text{ m/s}$ across $24\\text{ m}$. Time is unmentioned. Use $v^2 = u^2 + 2as = 5^2 + 2(2)(24) = 25 + 96 = 121 \\implies v = 11\\text{ m/s}$.",
            "watch_out": "Do not solve for time $t$ as an unnecessary intermediate step when $v^2 = u^2 + 2as$ connects knowns directly.",
            "quick_check": "If $u = 0$, $s \\propto t^2$ and $v \\propto \\sqrt{s}$.",
            "practice_targets": ["PHYS-KIN-004"]
        },
        {
            "id": "KIN-06",
            "pillar": "P3",
            "title": "Rebuild the Constant-Acceleration Equations",
            "subtitle": "Two physical ideas generate the equation family",
            "story": "The kinematic formulas are not arbitrary memorized rules; they are geometric consequences of linear $v-t$ velocity change and signed area.",
            "key_idea": "Displacement is the area under $v-t$: rectangle $ut$ plus triangle $\\frac{1}{2}(at)t = \\frac{1}{2}at^2$. Eliminating $t$ gives $v^2 = u^2 + 2as$. Distance in $n$-th second is $s_n = u + \\frac{1}{2}a(2n - 1)$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="60" y1="100" x2="440" y2="100" stroke="#94a3b8" stroke-width="2"/>
                <line x1="60" y1="100" x2="60" y2="20" stroke="#94a3b8" stroke-width="2"/>
                <!-- Area decomposition -->
                <polygon points="60,80 300,80 300,100 60,100" fill="rgba(56, 189, 248, 0.2)" stroke="#38bdf8"/>
                <text x="180" y="94" fill="#38bdf8" font-size="14">Rectangle: ut</text>
                <polygon points="60,80 300,30 300,80" fill="rgba(16, 185, 129, 0.2)" stroke="#10b981"/>
                <text x="210" y="65" fill="#10b981" font-size="14">Triangle: ½ at²</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Start with definitions $a = \\frac{v - u}{t} \\implies v = u + at$.",
                "Represent: Trapezoid area under $v-t$: $s = \\frac{u + v}{2} t$.",
                "Build: Substitute $v = u + at$ to obtain $s = ut + \\frac{1}{2}at^2$; substitute $t = \\frac{v-u}{a}$ to obtain $v^2 = u^2 + 2as$.",
                "Check: For interval from $t = n-1$ to $t = n$: $s_n = s(n) - s(n-1) = u + \\frac{1}{2}a(2n - 1)$."
            ],
            "worked_example": "From rest ($u = 0$) with uniform acceleration, displacement in first $4\\text{ s}$ is $32\\text{ m}$. $32 = \\frac{1}{2} a (4^2) = 8a \\implies a = 4\\text{ m/s}^2$. In 5th second: $s_5 = 0 + \\frac{1}{2}(4)(2 \\times 5 - 1) = 18\\text{ m}$.",
            "watch_out": "Do not confuse total displacement in $n$ seconds ($s = \\frac{1}{2}an^2$) with displacement during the $n$-th second ($s_n = \\frac{1}{2}a(2n - 1)$).",
            "quick_check": "Galileo's odd-number law: successive 1-second displacements from rest scale as $1 : 3 : 5 : 7 : \\dots$.",
            "practice_targets": ["PHYS-KIN-018"]
        },
        {
            "id": "KIN-07",
            "pillar": "P4",
            "title": "Multiphase Motion and Delayed Starts",
            "subtitle": "Carry physical state across boundaries; reset only the local clock",
            "story": "Complex journeys involve multiple stages: acceleration, cruising, and braking. State variables (velocity and position) must carry forward continuously across phase boundaries.",
            "key_idea": "Boundary speed carries forward ($u_2 = v_1$). For delayed start, body B's elapsed time is $\\tau = t - t_{\\text{delay}}$. Catch-up occurs when $x_A(t) = x_B(t)$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 110" style="max-width:100%; height:auto;">
                <rect x="40" y="30" width="120" height="40" rx="6" fill="#1e293b" stroke="#38bdf8"/>
                <text x="100" y="55" fill="#38bdf8" font-size="14" text-anchor="middle">Phase 1: Accel</text>
                <line x1="160" y1="50" x2="190" y2="50" stroke="#94a3b8" stroke-width="2"/>
                <rect x="190" y="30" width="120" height="40" rx="6" fill="#1e293b" stroke="#10b981"/>
                <text x="250" y="55" fill="#10b981" font-size="14" text-anchor="middle">Phase 2: Cruise</text>
                <line x1="310" y1="50" x2="340" y2="50" stroke="#94a3b8" stroke-width="2"/>
                <rect x="340" y="30" width="120" height="40" rx="6" fill="#1e293b" stroke="#f43f5e"/>
                <text x="400" y="55" fill="#f43f5e" font-size="14" text-anchor="middle">Phase 3: Brake</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Identify boundaries where acceleration changes or a new vehicle begins.",
                "Represent: Multi-segment timeline with local clocks $\\tau_k = t - t_{k,\\text{start}}$.",
                "Build: State handover: $v_{1,\\text{end}} = u_{2,\\text{start}}$; total displacement $s_{\\text{tot}} = s_1 + s_2 + s_3$.",
                "Check: Position cannot jump discontinuously."
            ],
            "worked_example": "Cart accelerates from 0 to $8\\text{ m/s}$ in $4\\text{ s}$ ($s_1 = \\frac{1}{2}(8)(4) = 16\\text{ m}$), cruises at $8\\text{ m/s}$ for $5\\text{ s}$ ($s_2 = 8 \\times 5 = 40\\text{ m}$), brakes to rest in $2\\text{ s}$ ($s_3 = \\frac{1}{2}(8)(2) = 8\\text{ m}$). Total displacement $= 16 + 40 + 8 = 64\\text{ m}$.",
            "watch_out": "Applying a single acceleration value across changing acceleration regimes.",
            "quick_check": "On a $v-t$ plot, three-phase motion forms a trapezoid whose area equals total displacement.",
            "practice_targets": ["PHYS-KIN-018"]
        },
        {
            "id": "KIN-08",
            "pillar": "P3",
            "title": "Vertical Motion and Free Fall",
            "subtitle": "The top is a velocity state, not a gravity-off state",
            "story": "Under ideal gravity near Earth, acceleration is strictly downward ($a_y = -g$) at all times during flight: ascending, at the turnaround apex, and descending.",
            "key_idea": "At the highest point, instantaneous velocity vanishes ($v = 0$), but acceleration remains exactly $-g$. Ascent and descent are time-reversal symmetric: $t_{\\text{up}} = t_{\\text{down}} = u/g$, $H_{\\max} = u^2 / (2g)$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="250" y1="100" x2="250" y2="20" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4"/>
                <circle cx="250" cy="25" r="8" fill="#facc15"/>
                <text x="270" y="25" fill="#facc15" font-size="14" font-weight="bold">Apex: v = 0, a = -g</text>
                <line x1="230" y1="90" x2="230" y2="35" stroke="#10b981" stroke-width="2"/>
                <text x="180" y="60" fill="#10b981" font-size="14">Rising (v > 0)</text>
                <line x1="270" y1="35" x2="270" y2="90" stroke="#f43f5e" stroke-width="2"/>
                <text x="320" y="60" fill="#f43f5e" font-size="14">Falling (v < 0)</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Set $+y$ upward; $a_y = -g$ constantly.",
                "Represent: Apex state: $v = 0$ at $t = u/g$.",
                "Build: $y(t) = ut - \\frac{1}{2}gt^2$; $v^2 = u^2 - 2gy$.",
                "Check: Landing speed equals launch speed $|v| = u$."
            ],
            "worked_example": "Ball thrown upward at $18\\text{ m/s}$ ($g = 9\\text{ m/s}^2$). Time to apex: $t = 18/9 = 2.0\\text{ s}$. Height: $H = 18^2 / (2 \\times 9) = 18\\text{ m}$.",
            "watch_out": "Claiming $a = 0$ at the top because the ball is momentarily at rest.",
            "quick_check": "Two stones dropped from rest for times $t$ and $2t$ fall distances in the ratio $1 : 4$ ($s \\propto t^2$).",
            "practice_targets": ["PHYS-KIN-003", "PHYS-KIN-007"]
        },
        {
            "id": "KIN-09",
            "pillar": "P2",
            "title": "Position-Time Graphs",
            "subtitle": "Slope is velocity; height is position",
            "story": "An $x-t$ graph records position versus time. The tangent slope represents instantaneous velocity ($v = dx/dt$). The vertical position on the page is position, not speed.",
            "key_idea": "Positive slope means moving in $+x$ direction; flat line means stationary ($v = 0$); negative slope means moving in $-x$ direction. Curvature indicates acceleration ($d^2x/dt^2$).",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="60" y1="100" x2="440" y2="100" stroke="#94a3b8" stroke-width="2"/>
                <line x1="60" y1="100" x2="60" y2="20" stroke="#94a3b8" stroke-width="2"/>
                <!-- Rising segment -->
                <line x1="60" y1="90" x2="220" y2="30" stroke="#10b981" stroke-width="2.5"/>
                <text x="130" y="50" fill="#10b981" font-size="14">Slope > 0 (+v)</text>
                <!-- Flat segment -->
                <line x1="220" y1="30" x2="380" y2="30" stroke="#38bdf8" stroke-width="2.5"/>
                <text x="300" y="22" fill="#38bdf8" font-size="14">Flat (v = 0)</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Check axes: horizontal is $t$, vertical is $x$.",
                "Represent: Slope $\\frac{\\Delta x}{\\Delta t}$ gives average velocity; tangent slope gives instantaneous velocity.",
                "Build: Linear segment: $v = \\frac{x_2 - x_1}{t_2 - t_1}$.",
                "Check: A horizontal line at $x = 100\\text{ m}$ indicates zero velocity."
            ],
            "worked_example": "Graph rises linearly from $x = 2\\text{ m}$ at $t = 0$ to $x = 14\\text{ m}$ at $t = 4\\text{ s}$, then flat for $3\\text{ s}$. Interval 1: $v = \\frac{14 - 2}{4 - 0} = 3\\text{ m/s}$. Interval 2: $v = 0\\text{ m/s}$.",
            "watch_out": "Confusing height with speed (an object high on the graph can be completely stationary).",
            "quick_check": "A steep slope indicates high speed; a flat slope indicates zero speed.",
            "practice_targets": ["PHYS-KIN-005"]
        },
        {
            "id": "KIN-10",
            "pillar": "P2",
            "title": "Velocity-Time and Acceleration-Time Graphs",
            "subtitle": "Slope, height and area have different physical jobs",
            "story": "On a $v-t$ graph, height is velocity, slope is acceleration ($a = dv/dt$), and signed area is net displacement ($\\Delta x = \\int v dt$).",
            "key_idea": "Signed area gives displacement; absolute area gives distance. On an $a-t$ graph, height is acceleration and area gives change in velocity $\\Delta v = v_f - v_i$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="60" x2="450" y2="60" stroke="#94a3b8" stroke-width="2"/>
                <!-- Positive area -->
                <rect x="80" y="30" width="140" height="30" fill="rgba(16, 185, 129, 0.2)" stroke="#10b981"/>
                <text x="150" y="50" fill="#10b981" font-size="14">+Area: +12 m</text>
                <!-- Negative area -->
                <rect x="220" y="60" width="160" height="30" fill="rgba(244, 63, 94, 0.2)" stroke="#f43f5e"/>
                <text x="300" y="80" fill="#f43f5e" font-size="14">-Area: -8 m</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Distinguish $v-t$ from $x-t$.",
                "Represent: Calculate geometric areas above the time axis ($+$) and below the time axis ($-$).",
                "Build: Net displacement $= \\text{Area}_+ - \\text{Area}_-$; Distance $= \\text{Area}_+ + \\text{Area}_-$.",
                "Check: Slope of horizontal $v-t$ line is 0 ($a = 0$)."
            ],
            "worked_example": "Particle moves at $+4\\text{ m/s}$ for $3\\text{ s}$, then $-2\\text{ m/s}$ for $4\\text{ s}$. $\\text{Area}_1 = 4 \\times 3 = +12\\text{ m}$; $\\text{Area}_2 = -2 \\times 4 = -8\\text{ m}$. Displacement $= 12 - 8 = +4\\text{ m}$. Distance $= 12 + 8 = 20\\text{ m}$.",
            "watch_out": "Adding negative area as negative when asked for total distance.",
            "quick_check": "If a particle completes a round trip, the positive area equals the negative area on its $v-t$ graph.",
            "practice_targets": ["PHYS-KIN-012"]
        },
        {
            "id": "KIN-11",
            "pillar": "P5",
            "title": "Interval Motion, Relative Frames & Graph Consistency",
            "subtitle": "Cumulative laws vs interval questions; Galilean acceleration cancellation",
            "story": "Displacement law $S(t)$ gives position change from origin to $t$. Interval distance requires endpoint subtraction. In relative motion under uniform gravity, common acceleration cancels completely.",
            "key_idea": "Two objects in free fall experience zero relative acceleration ($a_{\\text{rel}} = (-g) - (-g) = 0$). An $x-t$ curve cannot intersect a vertical line twice (single-valued physical history).",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <circle cx="150" cy="40" r="12" fill="#38bdf8"/>
                <text x="150" y="44" fill="#0f172a" font-size="14" font-weight="bold" text-anchor="middle">A</text>
                <line x1="150" y1="55" x2="150" y2="85" stroke="#38bdf8" stroke-width="2"/>
                <text x="165" y="75" fill="#38bdf8" font-size="14">-g</text>

                <circle cx="350" cy="60" r="12" fill="#10b981"/>
                <text x="350" y="64" fill="#0f172a" font-size="14" font-weight="bold" text-anchor="middle">B</text>
                <line x1="350" y1="75" x2="350" y2="105" stroke="#10b981" stroke-width="2"/>
                <text x="365" y="95" fill="#10b981" font-size="14">-g</text>

                <text x="250" y="30" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">Relative: a_rel = (-g) - (-g) = 0</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Check multi-body relative frames and vertical line test on graphs.",
                "Represent: Subtract accelerations: $\\vec{a}_{\\text{rel}} = \\vec{a}_A - \\vec{a}_B = \\vec{0}$.",
                "Build: Relative velocity is constant: $\\vec{v}_{\\text{rel}} = \\vec{u}_A - \\vec{u}_B$. Relative trajectory is a straight line.",
                "Check: A closed loop on $x-t$ implies two positions at the same clock time (physically impossible)."
            ],
            "worked_example": "Two objects in ideal free fall experience identical $g$. Their relative acceleration is $a_{\\text{rel}} = g - g = 0$. Viewed from object B, object A moves at constant velocity along a straight line.",
            "watch_out": "Assuming two falling objects accelerate toward or away from each other in the vertical direction.",
            "quick_check": "A vertical line intersecting a proposed $x-t$ graph twice violates single-particle physical causality.",
            "practice_targets": ["PHYS-KIN-013"]
        }
    ]

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
                <div class="quad-item watch-out">
                    <div class="quad-tag">⚠️ Watch Out / Student Trap</div>
                    <p>{u['watch_out']}</p>
                </div>
                <div class="quad-item quick-check">
                    <div class="quad-tag">💡 Quick Check</div>
                    <p>{u['quick_check']}</p>
                </div>
                <div class="quad-item transfer-target">
                    <div class="quad-tag">🎯 Core 2 Transfer Target</div>
                    <div class="target-buttons-row">{targets_html}</div>
                </div>
            </div>
        </article>
        """

    textbook_chapters_html = "".join(render_textbook_unit(u) for u in TEXTBOOK_UNITS)

    # =========================================================================
    # TAB 3: CORE 1B RECONSTRUCTION & FIRST-MOVE ATLAS
    # =========================================================================
    # Cognitive Dissonance Probes
    probes_html = ""
    for p in reconstruction_data.get("cognitive_dissonance_probes", []):
        pid = p.get("probe_id", "CDP")
        cref = p.get("competency_ref", "")
        trap = p.get("student_trap", "")
        soc = p.get("socratic_challenge", "")
        res = p.get("resolution", "")
        probes_html += f"""
        <div class="probe-card" id="probe-{pid}">
            <div class="probe-header">
                <span class="probe-id-badge">{pid}</span>
                <span class="probe-comp-ref">Competency: {cref}</span>
            </div>
            <div class="probe-trap">
                <div class="probe-subtag">Student Intuitive Trap</div>
                <p>"{trap}"</p>
            </div>
            <div class="probe-socratic">
                <div class="probe-subtag">Socratic Refutation Challenge</div>
                <p>{soc}</p>
            </div>
            <div class="probe-resolution">
                <div class="probe-subtag">Scientific Newtonian Resolution</div>
                <p>{res}</p>
            </div>
        </div>
        """

    # Reconstruction Cycles
    recons_html = ""
    for rc in reconstruction_data.get("reconstruction_cycles", []):
        cid = rc.get("cycle_id", "RECON")
        phenom = rc.get("phenomenon", "")
        cref = rc.get("competency_ref", "")
        std = rc.get("standard_derivation", "")
        recon = rc.get("phenomenological_reconstruction", {})
        limits = rc.get("limiting_boundary_checks", [])
        
        limits_html = "".join(f"<li><strong>{lc.get('limit', '')}:</strong> {lc.get('physical_consequence', '')}</li>" for lc in limits)
        
        recons_html += f"""
        <div class="recon-cycle-card" id="recon-{cid}">
            <div class="recon-header">
                <span class="recon-id-badge">{cid}</span>
                <span class="recon-comp-badge">Ref: {cref}</span>
                <h4 class="recon-title">{phenom}</h4>
            </div>

            <div class="recon-body">
                <div class="recon-standard">
                    <strong>Standard Formal Derivation:</strong>
                    <p>{std}</p>
                </div>

                <div class="recon-phenom-box">
                    <strong>Phenomenological Reconstruction ({recon.get('perspective', 'Physical Insight')}):</strong>
                    <p><em>Conceptual Pivot:</em> {recon.get('conceptual_pivot', '')}</p>
                    <p>{recon.get('harmonic_origin', recon.get('root_decomposition', recon.get('motion_in_elevator', recon.get('rectified_path', ''))))}</p>
                    <p>{recon.get('limiting_consequence', recon.get('ascent_descent_matching', recon.get('floor_motion', recon.get('collision_criterion', ''))))}</p>
                </div>

                <div class="recon-limits-box">
                    <strong>Limiting Boundary Invariant Checks:</strong>
                    <ul>{limits_html}</ul>
                </div>
            </div>
        </div>
        """

    # First-Move Atlas Table
    atlas_rows_html = ""
    for row in ontology_data.get("first_move_atlas", []):
        cid = row.get("competency_id", "")
        cue = row.get("cue", "")
        rep = row.get("representation", "")
        move = row.get("first_executable_move", "")
        anti = row.get("anti_pattern", "")
        atlas_rows_html += f"""
        <tr>
            <td class="atlas-cid"><button class="cross-link-btn" onclick="jumpToChapter('ch-{cid}')">{cid}</button></td>
            <td class="atlas-cue">{cue}</td>
            <td class="atlas-rep">{rep}</td>
            <td class="atlas-move"><strong>{move}</strong></td>
            <td class="atlas-anti"><span class="anti-tag">{anti}</span></td>
        </tr>
        """

    atlas_table_html = f"""
    <div class="atlas-table-container">
        <table class="atlas-table">
            <thead>
                <tr>
                    <th>Comp</th>
                    <th>Physical Cue / Trigger</th>
                    <th>Representation</th>
                    <th>First Executable Move</th>
                    <th>Anti-Pattern / Trap</th>
                </tr>
            </thead>
            <tbody>{atlas_rows_html}</tbody>
        </table>
    </div>
    """

    # =========================================================================
    # COMPOSE MASTER HTML
    # =========================================================================
    full_html = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Kinematics (1D &amp; 2D Motion) &bull; Tri-Modal Master Suite</title>
  <meta name="description" content="Tri-Modal Grade 9 Olympiad Physics Application: Core 1A Learner Textbook + Core 1B Recall & Reconstruction + Core 2 Olympiad Practice Suite.">
  {offline_katex_css_tag}
  <style id="katex-offline-font-faces">
    {decoded_katex_css}
  </style>
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

    * {{
      box-sizing: border-box;
    }}
    
    body {{
      background-color: var(--body-bg) !important;
      color: #f8fafc !important;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0;
      padding: 24px 16px;
      font-size: 16px;
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    /* 12.7" Tablet Optimized Container */
    .app-container {{
      width: 100%;
      max-width: 1100px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    
    /* Header & Navigation: Relative in document flow (Never occluding cards on 12.7" tablet) */
    .app-header {{
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px 28px;
      position: relative !important;
      top: auto !important;
      z-index: 10;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      width: 100%;
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 18px;
    }}
    .header-title-box h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 800;
      color: #fff;
      letter-spacing: -0.01em;
    }}
    .header-title-box p {{
      margin: 6px 0 0 0;
      font-size: 15px;
      color: #94a3b8;
    }}
    .tri-tabs-row {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .tri-tab-btn {{
      background: #1e293b;
      border: 1.5px solid var(--border);
      color: #94a3b8;
      font-size: 15px;
      font-weight: 700;
      padding: 12px 22px;
      border-radius: 10px;
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
      width: 100%;
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
      font-size: 15px;
      line-height: 1.6;
    }}
    .hint-tier {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 12px;
    }}
    .hint-tier-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 10px;
    }}
    .hint-tier-title {{
      font-size: 15px;
      font-weight: 700;
      color: #38bdf8;
      flex: 1 1 auto;
    }}
    .hint-unlock-btn {{
      background: #0284c7 !important;
      border: 1px solid #38bdf8 !important;
      color: #fff !important;
      font-size: 14px !important;
      font-weight: 700 !important;
      padding: 8px 18px !important;
      border-radius: 8px !important;
      cursor: pointer;
      min-height: 48px !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 8px;
      white-space: nowrap !important;
      width: auto !important;
      max-width: fit-content !important;
      flex-shrink: 0 !important;
      transition: all 0.2s ease;
    }}
    .hint-unlock-btn:hover {{
      background: #0369a1 !important;
      border-color: #7dd3fc !important;
      color: #fff !important;
    }}
    .hint-prompt {{
      font-size: 15.5px;
      color: #e2e8f0;
      line-height: 1.55;
    }}
    .hint-reveal {{
      background: #0f172a;
      border-left: 4px solid #22c55e;
      padding: 14px 18px;
      border-radius: 6px;
      margin-top: 10px;
      font-size: 15.5px;
      color: #f1f5f9;
      line-height: 1.6;
    }}

    .ladder-container {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin: 12px 0;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .ladder-step {{
      font-size: 15px;
      line-height: 1.5;
    }}
    .ladder-step strong {{
      color: var(--primary);
    }}
    .derivation-list {{
      padding-left: 20px;
      margin: 12px 0;
    }}
    .derivation-list li {{
      margin-bottom: 8px;
    }}
    .final-expression-box {{
      background: #0f172a;
      border: 1px solid #10b981;
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
      text-align: center;
    }}
    .indep-check-box {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin-top: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    /* Core 1A Textbook Styles */
    .textbook-chapter {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .chapter-header {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }}
    .chapter-badge-row {{
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }}
    .chapter-id-badge {{
      background: #059669;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .chapter-pillar-pill {{
      background: #1e3a8a;
      color: #93c5fd;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .chapter-title {{
      margin: 4px 0;
      font-size: 20px;
      color: #fff;
    }}
    .chapter-subtitle {{
      color: #94a3b8;
      font-size: 14px;
      font-style: italic;
    }}
    .textbook-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }}
    @media (max-width: 800px) {{
      .textbook-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    .story-box, .illustration-box, .method-box {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .box-tag {{
      font-size: 13px;
      font-weight: 700;
      color: var(--c1a-accent);
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .key-idea-callout {{
      background: rgba(16, 185, 129, 0.1);
      border-left: 3px solid var(--c1a-accent);
      padding: 10px 14px;
      border-radius: 4px;
      margin-top: 12px;
      font-size: 14px;
    }}
    .method-box {{
      margin-bottom: 20px;
    }}
    .method-list {{
      padding-left: 20px;
      margin: 0;
    }}
    .method-list li {{
      margin-bottom: 8px;
      font-size: 14.5px;
    }}
    .pedagogical-quad {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }}
    .quad-item {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      font-size: 14px;
    }}
    .quad-tag {{
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .worked-example .quad-tag {{ color: #38bdf8; }}
    .watch-out .quad-tag {{ color: #f43f5e; }}
    .quick-check .quad-tag {{ color: #facc15; }}
    .transfer-target .quad-tag {{ color: #10b981; }}
    .comp-target-btn {{
      background: #059669;
      border: 1px solid #10b981;
      color: #fff;
      font-size: 12px;
      font-weight: 700;
      padding: 8px 14px;
      border-radius: 6px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-top: 6px;
    }}
    .comp-target-btn:hover {{
      background: #047857;
    }}

    /* Core 1B Reconstruction Styles */
    .recon-section-intro {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    .recon-section-intro h3 {{
      margin: 0 0 8px 0;
      color: var(--c1b-accent);
    }}
    .atlas-table-container {{
      overflow-x: auto;
      margin-bottom: 28px;
      border: 1px solid var(--border);
      border-radius: 10px;
    }}
    .atlas-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      text-align: left;
    }}
    .atlas-table th {{
      background: #0f172a;
      color: #94a3b8;
      font-weight: 700;
      padding: 12px;
      border-bottom: 1px solid var(--border);
    }}
    .atlas-table td {{
      padding: 12px;
      border-bottom: 1px solid #243044;
      background: #1e293b;
    }}
    .atlas-table tr:hover td {{
      background: #243044;
    }}
    .atlas-cid {{
      font-weight: 800;
      color: var(--c1b-accent);
    }}
    .anti-tag {{
      background: rgba(244, 63, 94, 0.15);
      border: 1px solid #f43f5e;
      color: #fca5a5;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
    }}

    .probes-grid, .recons-grid {{
      display: flex;
      flex-direction: column;
      gap: 20px;
      margin-bottom: 28px;
    }}
    .probe-card, .recon-cycle-card {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
    }}
    .probe-header, .recon-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border);
    }}
    .probe-id-badge, .recon-id-badge {{
      background: #7c3aed;
      color: #fff;
      font-weight: 800;
      font-size: 12px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .probe-subtag {{
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 4px;
      text-transform: uppercase;
    }}
    .probe-trap .probe-subtag {{ color: #f43f5e; }}
    .probe-socratic .probe-subtag {{ color: #facc15; }}
    .probe-resolution .probe-subtag {{ color: #10b981; }}
    .probe-trap, .probe-socratic, .probe-resolution {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 10px;
      font-size: 14.5px;
    }}
    .recon-phenom-box {{
      background: rgba(124, 58, 237, 0.1);
      border-left: 3px solid var(--c1b-accent);
      padding: 14px;
      border-radius: 6px;
      margin: 12px 0;
      font-size: 14.5px;
    }}
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Header: Document Flow (Scrolls away cleanly on tablet) -->
    <header class="app-header">
      <div class="header-top">
        <div class="header-title-box">
          <h1>Kinematics &bull; Tri-Modal Master Tablet Suite</h1>
          <p>Grade 9 Olympiad Physics &bull; 1D Motion, 2D Projectiles &amp; Relative Frames</p>
        </div>
        <div class="header-meta-pill">
          <span class="badge badge-accent">12.7" Tablet Spec &bull; 25 Olympiad Cards</span>
        </div>
      </div>
      <nav class="tri-tabs-row">
        <button class="tri-tab-btn tab-c2 active" onclick="showTab('core2')">
          <span>🎯</span> Core 2: Olympiad Practice Suite
        </button>
        <button class="tri-tab-btn tab-c1a" onclick="showTab('core1a')">
          <span>📘</span> Core 1A: Learner Textbook (11 Ch)
        </button>
        <button class="tri-tab-btn tab-c1b" onclick="showTab('core1b')">
          <span>🧠</span> Core 1B: Recall &amp; Reconstruction
        </button>
      </nav>
    </header>

    <!-- Main Content Area -->
    <main class="main-wrap">
      <!-- TAB 1: CORE 2 PRACTICE -->
      <section id="tab-core2" class="tab-section active">
        {practice_cards_html}
      </section>

      <!-- TAB 2: CORE 1A TEXTBOOK -->
      <section id="tab-core1a" class="tab-section">
        {textbook_chapters_html}
      </section>

      <!-- TAB 3: CORE 1B RECONSTRUCTION -->
      <section id="tab-core1b" class="tab-section">
        <div class="recon-section-intro">
          <h3>⚡ First-Move Atlas (Operational Trigger Catalog)</h3>
          <p>Instantaneous cues, dual representations, first executable moves, and anti-patterns for all 11 kinematics competencies.</p>
        </div>
        {atlas_table_html}

        <div class="recon-section-intro">
          <h3>🔬 Deep Phenomenological Reconstruction Cycles</h3>
          <p>First-principles derivation vs time-reversal, time-budget weighting, and Galilean cancellation invariants.</p>
        </div>
        <div class="recons-grid">{recons_html}</div>

        <div class="recon-section-intro">
          <h3>⚠️ Cognitive Dissonance Dialog Probes</h3>
          <p>Socratic dialogues confronting intuitive misconceptions with mathematical rigor.</p>
        </div>
        <div class="probes-grid">{probes_html}</div>
      </section>
    </main>
  </div>

  <script>
    // Tab switching
    function showTab(tabId) {{
      document.querySelectorAll('.tab-section').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tri-tab-btn').forEach(el => el.classList.remove('active'));
      
      const targetSec = document.getElementById('tab-' + tabId);
      if (targetSec) targetSec.classList.add('active');
      
      if (tabId === 'core2') document.querySelector('.tab-c2').classList.add('active');
      if (tabId === 'core1a') document.querySelector('.tab-c1a').classList.add('active');
      if (tabId === 'core1b') document.querySelector('.tab-c1b').classList.add('active');

      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // Cross-links
    function jumpToChapter(chId) {{
      showTab('core1a');
      setTimeout(() => {{
        const el = document.getElementById(chId);
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    function jumpToCore2(qid) {{
      showTab('core2');
      setTimeout(() => {{
        const el = document.getElementById('card-' + qid);
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    // Option selection
    function selectOption(qid, optKey, isCorrect) {{
      const card = document.getElementById('card-' + qid);
      if (!card) return;
      
      // Highlight selected button
      card.querySelectorAll('.opt-btn').forEach(btn => {{
        btn.classList.remove('correct', 'incorrect');
        if (btn.getAttribute('data-opt') === optKey) {{
          btn.classList.add(isCorrect ? 'correct' : 'incorrect');
        }}
      }});

      // Show diagnostic
      card.querySelectorAll('.opt-diag').forEach(d => d.style.display = 'none');
      const diagEl = document.getElementById('diag-' + qid + '-' + optKey);
      if (diagEl) diagEl.style.display = 'block';

      // Feedback banner
      const banner = document.getElementById('feedback-' + qid);
      if (banner) {{
        banner.style.display = 'block';
        banner.className = 'feedback-banner ' + (isCorrect ? 'correct' : 'incorrect');
        banner.innerHTML = isCorrect ? 
          '<strong>&check; Outstanding!</strong> Correct Olympian deduction.' : 
          '<strong>&cross; Conceptual Trap Triggered!</strong> Check diagnostic feedback or unlock hints below.';
      }}
    }}

    // Hint unlocking
    function unlockHint(qid, tier) {{
      const reveal = document.getElementById('reveal-' + qid + '-' + tier);
      if (reveal) {{
        reveal.style.display = 'block';
        const btn = document.querySelector('#hint-' + qid + '-' + tier + ' .hint-unlock-btn');
        if (btn) {{
          btn.textContent = 'Unlocked';
          btn.disabled = true;
          btn.style.opacity = '0.6';
        }}
      }}
    }}
  </script>
</body>
</html>
    """

    # Write raw HTML for prerender engine
    raw_path = REPO_ROOT / "scratch/_raw_kinematics_tri_modal.html"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[OK] Wrote raw HTML template: {raw_path} ({len(full_html)} bytes)")

    # Target destinations
    output_path = REPO_ROOT / "standalone/practice/core2-physics-kinematics-grade9-master.html"
    public_path = REPO_ROOT / "public/standalone/practice/core2-physics-kinematics-grade9-master.html"
    artifact_path = Path(r"C:\Users\reall\.gemini\antigravity\brain\40014ef9-8d66-475e-aff1-d6e53797ebbd\physics_kinematics_master_app.html")

    # Run Node.js KaTeX Static DOM Prerender
    print("\n[PRERENDER] Executing Node.js KaTeX Static DOM Prerender Engine...")
    prerender_html(str(raw_path), str(output_path))
    print(f"[OK] Prerender completed: saved to {output_path}")

    # Copy to public and artifact
    public_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(output_path, public_path)
    print(f"[OK] Copied to public: {public_path}")

    if artifact_path.parent.exists():
        shutil.copyfile(output_path, artifact_path)
        print(f"[OK] Copied to brain artifact directory: {artifact_path}")

    print(f"\n{'='*80}")
    print("KINEMATICS MASTER TABLET APP COMPILATION COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    compile_tri_modal_kinematics()
