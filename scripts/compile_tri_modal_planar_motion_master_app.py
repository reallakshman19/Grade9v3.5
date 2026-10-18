# scripts/compile_tri_modal_planar_motion_master_app.py
"""
Compile Tri-Modal Master Tablet Application for Motion in a Plane (Projectiles, Relative Frames & Curvilinear Motion).
Architecture:
- Tab 1: Core 2 Practice Suite (25 Olympiad Cards with 5-Step Proofs & Prompt-Reveals)
- Tab 2: Core 1A Learner Textbook (11 Comprehensive Chapters from Golden PDF)
- Tab 3: Core 1B Recall & Reconstruction (Cognitive Dissonance Probes, Invariant Cycles, & First-Move Atlas)

12.7" Tablet Touch Screen Specification:
- Non-occluding relative header inside .app-container
- Offline Base64 KaTeX font-faces embedded directly into <style id="katex-offline-font-faces">
- Touch targets >= 48px floor
- Non-squished hint unlock buttons
- All SVG text font-size >= 14px floor
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

def compile_tri_modal_planar_motion():
    print(f"\n{'='*80}")
    print("COMPILING TRI-MODAL MASTER TABLET APP: MOTION IN A PLANE (2D MOTION)")
    print("Tripartite Architecture: Core 1A (Learn) <-> Core 1B (Recall) <-> Core 2 (Practice)")
    print(f"{'='*80}\n")

    # Load Data
    bank_path = REPO_ROOT / "TEST/physics-research/question_bank_planar_motion_grade9.v1.json"
    ontology_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_planar_motion_ontology.v1.json"
    reconstruction_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_planar_motion_reconstruction.v1.json"
    adapters_path = REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json"

    with open(bank_path, "r", encoding="utf-8") as f:
        bank_data = json.load(f)
    with open(ontology_path, "r", encoding="utf-8") as f:
        ontology_data = json.load(f)
    with open(reconstruction_path, "r", encoding="utf-8") as f:
        reconstruction_data = json.load(f)
    with open(adapters_path, "r", encoding="utf-8") as f:
        adapters_data = json.load(f)["topic_adapters"]["motion-in-a-plane"]

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
        comp = q.get("subtopic_competency_ref", "PLANE-01")
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
            "id": "PLANE-01",
            "pillar": "P1",
            "title": "2D Position & Velocity Component Independence",
            "subtitle": "From one direction to two: orthogonal Cartesian resolution",
            "story": "A straight-road journey can be described with one coordinate x. A particle moving across a plane requires two coordinates (x, y). We simplify two-dimensional motion by splitting it into two mutually perpendicular 1D motions that share a single common clock time t.",
            "key_idea": "Perpendicular motions are completely independent. Changes in horizontal velocity or position have zero influence on vertical motion, and vice versa.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="60" y1="100" x2="440" y2="100" stroke="#94a3b8" stroke-width="2"/>
                <line x1="60" y1="100" x2="60" y2="20" stroke="#94a3b8" stroke-width="2"/>
                <!-- Decomposed Vectors -->
                <line x1="60" y1="100" x2="260" y2="100" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="260,95 270,100 260,105" fill="#38bdf8"/>
                <text x="160" y="90" fill="#38bdf8" font-size="14" font-weight="bold">v_x = u cos theta</text>

                <line x1="60" y1="100" x2="60" y2="35" stroke="#10b981" stroke-width="3"/>
                <polygon points="55,35 60,25 65,35" fill="#10b981"/>
                <text x="75" y="55" fill="#10b981" font-size="14" font-weight="bold">v_y = u sin theta</text>

                <!-- Resultant Vector -->
                <line x1="60" y1="100" x2="260" y2="35" stroke="#facc15" stroke-width="3"/>
                <polygon points="255,42 265,32 250,32" fill="#facc15"/>
                <text x="180" y="50" fill="#facc15" font-size="14" font-weight="bold">Resultant v</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Choose the plane of motion as the Cartesian x-y plane.",
                "Represent: Decompose position r(t) = x(t) i + y(t) j and velocity v(t) = v_x(t) i + v_y(t) j.",
                "Build: Apply 1D kinematic equations along each axis independently.",
                "Check: Scalar speed is the Pythagorean magnitude |v| = sqrt(v_x^2 + v_y^2)."
            ],
            "worked_example": "A particle moves with $x(t) = 3t$ and $y(t) = 4t - 5t^2$. Horizontal velocity $v_x = 3\\text{ m/s}$ is constant. Vertical velocity $v_y = 4 - 10t$ changes under gravity. At $t = 0$: $|\\vec{v}| = \\sqrt{3^2 + 4^2} = 5\\text{ m/s}$.",
            "watch_out": "Treating x-motion and y-motion as two different objects. They are two orthogonal descriptions of the exact same particle at the same instant.",
            "quick_check": "If horizontal velocity is tripled, vertical acceleration remains unchanged at -g.",
            "practice_targets": ["PHYS-MIP-001", "PHYS-MIP-010"]
        },
        {
            "id": "PLANE-02",
            "pillar": "P1",
            "title": "Constant-Acceleration Equations in Vector Form",
            "subtitle": "Vector kinematic quad applied independently per axis",
            "story": "When acceleration vector a = a_x i + a_y j is constant in both magnitude and direction, each component behaves as a decoupled 1D uniform acceleration system.",
            "key_idea": "Vector equations v(t) = u + at and Delta r(t) = ut + 0.5*a*t^2 hold simultaneously and independently along both Cartesian axes.",
            "svg_diagram": """
            <svg viewBox="0 0 500 110" style="max-width:100%; height:auto;">
                <rect x="50" y="25" width="180" height="60" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
                <text x="140" y="48" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Horizontal (x)</text>
                <text x="140" y="72" fill="#e2e8f0" font-size="14" text-anchor="middle">a_x = 0 => x = u_x * t</text>
                <rect x="270" y="25" width="180" height="60" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
                <text x="360" y="48" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">Vertical (y)</text>
                <text x="360" y="72" fill="#e2e8f0" font-size="14" text-anchor="middle">a_y = -g => y = u_y t - ½gt²</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Verify acceleration is uniform in both magnitude and direction (da/dt = 0).",
                "Represent: Write vector components u = u_x i + u_y j and a = a_x i + a_y j.",
                "Build: Formulate component scalar equations: v_x = u_x + a_x t, v_y = u_y + a_y t, x = u_x t + 0.5*a_x t^2, y = u_y t + 0.5*a_y t^2.",
                "Check: Ensure clock time t is the unique common parameter linking the two orthogonal systems."
            ],
            "worked_example": "Particle starts from origin with $\\vec{u} = 5\\hat{i}\\text{ m/s}$ and $\\vec{a} = 2\\hat{i} - 4\\hat{j}\\text{ m/s}^2$. At $t = 3\\text{ s}$: $x = 5(3) + \\frac{1}{2}(2)(3^2) = 24\\text{ m}$; $y = 0(3) + \\frac{1}{2}(-4)(3^2) = -18\\text{ m}$. Position: $\\vec{r} = 24\\hat{i} - 18\\hat{j}\\text{ m}$.",
            "watch_out": "Adding horizontal and vertical velocities directly as scalars instead of vector addition.",
            "quick_check": "If acceleration has only a y-component (a_x = 0), x-velocity is conserved forever.",
            "practice_targets": ["PHYS-MIP-002", "PHYS-MIP-012"]
        },
        {
            "id": "PLANE-03",
            "pillar": "P1",
            "title": "Horizontal Launch from Elevated Height",
            "subtitle": "One sideways speed, one pure falling motion",
            "story": "When an object is launched horizontally with speed u from a cliff of height h, it possesses zero initial vertical velocity (u_y = 0). It begins falling downward under gravity at the exact same rate as a dropped ball.",
            "key_idea": "Vertical fall time is strictly $t_{\\text{fall}} = \\sqrt{\\frac{2h}{g}}$, completely independent of horizontal launch speed u. Horizontal range is $x = u \\sqrt{\\frac{2h}{g}}$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Cliff -->
                <rect x="50" y="30" width="80" height="80" fill="#334155"/>
                <text x="90" y="75" fill="#94a3b8" font-size="14" text-anchor="middle">Cliff h</text>
                <!-- Launch arrow -->
                <line x1="130" y1="30" x2="190" y2="30" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="190,25 200,30 190,35" fill="#38bdf8"/>
                <text x="165" y="22" fill="#38bdf8" font-size="14" font-weight="bold">u</text>
                <!-- Parabolic Path -->
                <path d="M 130 30 Q 250 30 380 110" fill="none" stroke="#facc15" stroke-width="2.5" stroke-dasharray="5"/>
                <!-- Ground -->
                <line x1="50" y1="110" x2="450" y2="110" stroke="#475569" stroke-width="2"/>
                <text x="380" y="105" fill="#10b981" font-size="14" font-weight="bold">Landing</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Identify launch conditions: u_x = u, u_y = 0, a_x = 0, a_y = -g.",
                "Represent: Vertical axis +y downward: y(t) = 0.5*g*t^2; Horizontal axis: x(t) = ut.",
                "Build: Set y = h => t = sqrt(2h / g). Substitute into range: x = u * sqrt(2h / g).",
                "Check: Impact speed is v = sqrt(u^2 + 2gh) by conservation of mechanical energy."
            ],
            "worked_example": "A stone is thrown horizontally at $15\\text{ m/s}$ from a $20\\text{ m}$ cliff ($g = 10\\text{ m/s}^2$). Time to ground: $t = \\sqrt{2(20)/10} = 2.0\\text{ s}$. Horizontal distance: $x = 15 \\times 2 = 30\\text{ m}$.",
            "watch_out": "Believing high horizontal launch speed 'fights gravity' and keeps the object in the air longer.",
            "quick_check": "A dropped coin and a horizontally fired rifle bullet released at the same instant from the same height strike level ground simultaneously.",
            "practice_targets": ["PHYS-MIP-003", "PHYS-MIP-004"]
        },
        {
            "id": "PLANE-04",
            "pillar": "P3",
            "title": "Ground-to-Ground Oblique Projectile Flight Time & Apex",
            "subtitle": "At the top, what actually becomes zero?",
            "story": "An oblique projectile launched at angle theta rises, reaches an apex summit, and descends along a symmetric parabola under constant downward gravitational acceleration -g.",
            "key_idea": "At the highest point, ONLY the vertical velocity vanishes ($v_y = 0$). Horizontal velocity remains $v_x = u\\cos\\theta > 0$. Ascent time equals descent time: $t_{\\text{apex}} = \\frac{u\\sin\\theta}{g}$, total flight time $T = \\frac{2u\\sin\\theta}{g}$, and peak height $H_{\\max} = \\frac{u^2\\sin^2\\theta}{2g}$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="105" x2="450" y2="105" stroke="#475569" stroke-width="2"/>
                <path d="M 80 105 Q 250 15 420 105" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
                <!-- Apex -->
                <circle cx="250" cy="38" r="6" fill="#facc15"/>
                <line x1="250" y1="38" x2="310" y2="38" stroke="#10b981" stroke-width="2.5"/>
                <polygon points="310,34 318,38 310,42" fill="#10b981"/>
                <text x="250" y="24" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">Apex: v_y = 0, v_x = u cos theta</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Decompose launch velocity: u_x = u cos theta, u_y = u sin theta.",
                "Represent: Vertical motion: v_y(t) = u sin theta - gt; y(t) = (u sin theta)t - 0.5*gt^2.",
                "Build: Set v_y = 0 => t_apex = (u sin theta) / g; H_max = (u^2 sin^2 theta) / (2g); T = (2u sin theta) / g.",
                "Check: Speed at apex is strictly minimum (u cos theta) but never zero unless theta = 90 deg."
            ],
            "worked_example": "Projected at $u = 20\\text{ m/s}$ at $\\theta = 30^\\circ$ ($g = 10\\text{ m/s}^2$). $u_y = 20\\sin 30^\\circ = 10\\text{ m/s}$. Apex time: $t = 10/10 = 1.0\\text{ s}$. Total flight time: $T = 2.0\\text{ s}$. Peak height: $H = 10^2 / 20 = 5.0\\text{ m}$. Speed at apex: $20\\cos 30^\\circ = 10\\sqrt{3}\\text{ m/s} \\approx 17.3\\text{ m/s}$.",
            "watch_out": "Setting total speed to zero at the apex.",
            "quick_check": "At the apex, the acceleration is still exactly g = 9.8 m/s^2 downward.",
            "practice_targets": ["PHYS-MIP-005", "PHYS-MIP-006", "PHYS-MIP-014"]
        },
        {
            "id": "PLANE-05",
            "pillar": "P3",
            "title": "Horizontal Range & Maximum Range Invariant",
            "subtitle": "Symmetric landing distance and the 45-degree optimum",
            "story": "Horizontal range R is the net horizontal displacement when the projectile returns to its launch elevation. It is the product of horizontal velocity and total flight time.",
            "key_idea": "Level-ground range is $R = u_x T = \\frac{u^2\\sin 2\\theta}{g}$. Maximum range occurs at $\\theta = 45^\\circ$, where $\\sin 2\\theta = 1 \\implies R_{\\max} = \\frac{u^2}{g}$. At this optimal angle, $H_{\\max} = \\frac{R_{\\max}}{4}$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="100" x2="450" y2="100" stroke="#475569" stroke-width="2"/>
                <!-- 45 deg trajectory -->
                <path d="M 80 100 Q 250 15 420 100" fill="none" stroke="#10b981" stroke-width="3"/>
                <text x="250" y="30" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">Optimal theta = 45 deg: R_max = u² / g</text>
                <text x="250" y="85" fill="#e2e8f0" font-size="14" text-anchor="middle">Height at R_max is H = R / 4</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Ensure launch and landing are on the same horizontal plane.",
                "Represent: Multiply horizontal speed by flight time: R = (u cos theta) * (2u sin theta / g).",
                "Build: Apply trigonometric identity 2 sin theta cos theta = sin 2theta => R = (u^2 sin 2theta) / g.",
                "Check: Range vanishes at theta = 0 deg (no flight time) and theta = 90 deg (no horizontal speed)."
            ],
            "worked_example": "A cannon fires with $u = 50\\text{ m/s}$ at $\\theta = 45^\\circ$ ($g = 10\\text{ m/s}^2$). Range: $R = 50^2 / 10 = 250\\text{ m}$. Maximum height: $H = 250 / 4 = 62.5\\text{ m}$.",
            "watch_out": "Using R = (u^2 sin 2theta)/g when firing off a cliff or onto an elevated hill.",
            "quick_check": "Maximum range requires sin 2theta = 1 => 2theta = 90 deg => theta = 45 deg.",
            "practice_targets": ["PHYS-MIP-007", "PHYS-MIP-008", "PHYS-MIP-015"]
        },
        {
            "id": "PLANE-06",
            "pillar": "P3",
            "title": "Complementary Launch Angles & Trajectory Envelopes",
            "subtitle": "Same range, different paths: high lob vs low drive",
            "story": "Because sin(2(90 - theta)) = sin(180 - 2theta) = sin 2theta, any two launch angles that add to 90 degrees achieve the exact same horizontal range for the same launch speed.",
            "key_idea": "Complementary angles $\\theta$ and $90^\\circ - \\theta$ produce identical ranges. The steeper angle stays in the air longer ($T_1/T_2 = \\tan\\theta_1$) and reaches higher peak ($H_1/H_2 = \\tan^2\\theta_1$). The geometric mean height satisfies $\\sqrt{H_1 H_2} = \\frac{R}{4}$, and flight time product is $T_1 T_2 = \\frac{2R}{g}$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="105" x2="450" y2="105" stroke="#475569" stroke-width="2"/>
                <!-- High Lob (60 deg) -->
                <path d="M 80 105 Q 240 10 400 105" fill="none" stroke="#a855f7" stroke-width="2.5"/>
                <text x="240" y="25" fill="#a855f7" font-size="14" font-weight="bold" text-anchor="middle">Lob (60 deg): Higher peak, longer time</text>
                <!-- Low Drive (30 deg) -->
                <path d="M 80 105 Q 240 60 400 105" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
                <text x="240" y="75" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Drive (30 deg): Same landing point R!</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Pair complementary angles: e.g. 15 deg and 75 deg, or 30 deg and 60 deg.",
                "Represent: Compare high lob (u_y > u_x) and low drive (u_x > u_y).",
                "Build: Multiply flight times: T1 * T2 = 2R / g; Multiply heights: sqrt(H1 * H2) = R / 4.",
                "Check: Ratio of maximum heights equals tan^2 theta_1."
            ],
            "worked_example": "Projectiles launched at $30^\\circ$ and $60^\\circ$ with $u = 40\\text{ m/s}$ ($g = 10\\text{ m/s}^2$). Range for both: $R = \\frac{1600\\sin 60^\\circ}{10} = 80\\sqrt{3}\\text{ m} \\approx 138.6\\text{ m}$. Height product: $\\sqrt{H_1 H_2} = \\frac{80\\sqrt{3}}{4} = 20\\sqrt{3}\\text{ m} \\approx 34.6\\text{ m}$.",
            "watch_out": "Assuming identical range implies identical flight times or velocities.",
            "quick_check": "The flight time product T1 * T2 = 2R / g depends only on horizontal range and g, completely independent of launch speed u.",
            "practice_targets": ["PHYS-MIP-009", "PHYS-MIP-016"]
        },
        {
            "id": "PLANE-07",
            "pillar": "P3",
            "title": "Cartesian Trajectory Parabola Equation",
            "subtitle": "Describe the path without using time",
            "story": "By eliminating clock time t between horizontal and vertical motion, we obtain the spatial equation of the curve traversed by the projectile.",
            "key_idea": "The path is an inverted Cartesian parabola: $y(x) = x\\tan\\theta - \\frac{g x^2}{2u^2\\cos^2\\theta} = x\\tan\\theta\\left(1 - \\frac{x}{R}\\right)$. This links height y directly to horizontal position x.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="100" x2="450" y2="100" stroke="#475569" stroke-width="2"/>
                <line x1="50" y1="100" x2="50" y2="20" stroke="#475569" stroke-width="2"/>
                <path d="M 50 100 Q 220 20 390 100" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
                <text x="220" y="35" fill="#f43f5e" font-size="14" font-weight="bold" text-anchor="middle">y(x) = x tan theta * (1 - x / R)</text>
                <circle cx="220" cy="60" r="5" fill="#38bdf8"/>
                <text x="220" y="80" fill="#38bdf8" font-size="14" text-anchor="middle">Target (x, y)</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Problem provides or asks for spatial coordinates (x, y) without requiring flight time.",
                "Represent: Substitute t = x / (u cos theta) into y = (u sin theta)t - 0.5*gt^2.",
                "Build: Use 1 / cos^2 theta = 1 + tan^2 theta to solve for launch angles required to clear target (x, y).",
                "Check: Verify boundary landmarks: y(0) = 0 and y(R) = 0."
            ],
            "worked_example": "A ball launched at $45^\\circ$ clears a fence at $x = 20\\text{ m}$. If range is $R = 80\\text{ m}$: $y(20) = 20\\tan 45^\\circ\\left(1 - \\frac{20}{80}\\right) = 20(1)\\left(\\frac{3}{4}\\right) = 15\\text{ m}$.",
            "watch_out": "Solving two separate quadratic equations in time when the factored range formula gives the answer in one line.",
            "quick_check": "At the midpoint x = R / 2: y = (R / 2) tan theta (1 - 1/2) = (R tan theta) / 4 = H_max.",
            "practice_targets": ["PHYS-MIP-011", "PHYS-MIP-017"]
        },
        {
            "id": "PLANE-08",
            "pillar": "P2",
            "title": "Relative Velocity: River-Boat Shortest Time vs Zero Drift",
            "subtitle": "Boat in a stream: orthogonal navigation and current compensation",
            "story": "A boat navigating a river of width W moving at speed v_r possesses engine speed v_b relative to the water. Resultant motion relative to the ground is v_net = v_b/w + v_w.",
            "key_idea": "Shortest time requires steering perpendicular to the banks ($\\theta = 90^\\circ$, $t_{\\min} = \\frac{W}{v_b}$); current speed has zero effect on crossing time! Zero drift requires steering upstream at $\\sin\\alpha = \\frac{v_r}{v_b}$, possible only if $v_b > v_r$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Banks -->
                <line x1="50" y1="20" x2="450" y2="20" stroke="#475569" stroke-width="2"/>
                <line x1="50" y1="100" x2="450" y2="100" stroke="#475569" stroke-width="2"/>
                <text x="70" y="60" fill="#38bdf8" font-size="14" font-weight="bold">Current v_r &rarr;</text>
                <!-- Shortest Time -->
                <line x1="200" y1="100" x2="200" y2="30" stroke="#10b981" stroke-width="2.5"/>
                <polygon points="195,30 200,20 205,30" fill="#10b981"/>
                <text x="210" y="45" fill="#10b981" font-size="14" font-weight="bold">Shortest time: head 90 deg</text>
                <!-- Zero drift -->
                <line x1="360" y1="100" x2="310" y2="30" stroke="#a855f7" stroke-width="2.5"/>
                <polygon points="305,32 305,22 315,26" fill="#a855f7"/>
                <text x="325" y="75" fill="#a855f7" font-size="14" font-weight="bold">Zero drift: head upstream</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Identify what is to be minimized: crossing time vs downstream drift.",
                "Represent: Perpendicular axis across river: v_y = v_b sin theta; Parallel axis along river: v_x = v_r + v_b cos theta.",
                "Build: Shortest time: maximize v_y => sin theta = 1 => t_min = W / v_b. Zero drift: set v_x = 0 => cos theta = -v_r / v_b.",
                "Check: If v_b < v_r, zero drift is impossible; minimum drift angle satisfies cos theta = v_b / v_r."
            ],
            "worked_example": "River width $W = 120\\text{ m}$, river current $v_r = 3\\text{ m/s}$, boat speed $v_b = 5\\text{ m/s}$. Shortest time: $t = 120/5 = 24\\text{ s}$; downstream drift $= 3 \\times 24 = 72\\text{ m}$. Zero drift: $\\sin\\alpha = 3/5 \\implies \\alpha \\approx 36.9^\\circ$ upstream; crossing time $t = \\frac{120}{\\sqrt{5^2 - 3^2}} = \\frac{120}{4} = 30\\text{ s}$.",
            "watch_out": "Steering angled upstream when asked for shortest time. Shortest time strictly requires steering directly across.",
            "quick_check": "The river current cannot assist crossing in the perpendicular direction; it only causes downstream drift.",
            "practice_targets": ["PHYS-MIP-013", "PHYS-MIP-018", "PHYS-MIP-019"]
        },
        {
            "id": "PLANE-09",
            "pillar": "P2",
            "title": "Relative Velocity: Rain-Man & Aircraft Wind Drift",
            "subtitle": "Rain problems: vector subtraction and relative tilt angle",
            "story": "When rain falls vertically downward at speed v_r and a person walks forward horizontally at speed v_m, the rain appears to strike diagonally from the front in the moving frame.",
            "key_idea": "Relative velocity is vector subtraction: $\\vec{v}_{\\text{rel}} = \\vec{v}_{\\text{rain}} - \\vec{v}_{\\text{man}} = -v_r\\hat{j} - v_m\\hat{i}$. To stay dry, the umbrella must tilt forward at an angle $\\tan\\theta = \\frac{v_m}{v_r}$ from the vertical.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Vertical rain -->
                <line x1="200" y1="20" x2="200" y2="80" stroke="#38bdf8" stroke-width="2"/>
                <polygon points="196,80 200,90 204,80" fill="#38bdf8"/>
                <text x="140" y="55" fill="#38bdf8" font-size="14" font-weight="bold">v_rain (down)</text>
                <!-- Backward relative runner -->
                <line x1="200" y1="90" x2="130" y2="90" stroke="#f43f5e" stroke-width="2"/>
                <polygon points="130,86 120,90 130,94" fill="#f43f5e"/>
                <text x="140" y="110" fill="#f43f5e" font-size="14" font-weight="bold">-v_man (back)</text>
                <!-- Resultant relative rain -->
                <line x1="200" y1="20" x2="130" y2="90" stroke="#facc15" stroke-width="3"/>
                <polygon points="130,82 122,94 136,92" fill="#facc15"/>
                <text x="220" y="60" fill="#facc15" font-size="14" font-weight="bold">v_rel: tilt umbrella forward &theta;</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Observer in motion relative to ground; precipitation or wind moving relative to ground.",
                "Represent: Draw relative vector triangle: v_rel = v_target - v_observer.",
                "Build: Relative speed |v_rel| = sqrt(v_r^2 + v_m^2); tilt angle from vertical theta = arctan(v_m / v_r).",
                "Check: As running speed increases, umbrella must be tilted more horizontally."
            ],
            "worked_example": "Rain falls vertically at $12\\text{ m/s}$. A cyclist rides at $5\\text{ m/s}$. Relative speed: $v_{\\text{rel}} = \\sqrt{12^2 + 5^2} = 13\\text{ m/s}$. Umbrella angle: $\\tan\\theta = 5/12 \\implies \\theta \\approx 22.6^\\circ$ forward from vertical.",
            "watch_out": "Tilting the umbrella backward. Because the observer moves forward, the rain appears to come from ahead.",
            "quick_check": "If a runner moves at the same speed as wind-blown rain, the rain appears to fall vertically.",
            "practice_targets": ["PHYS-MIP-020", "PHYS-MIP-021", "PHYS-MIP-022"]
        },
        {
            "id": "PLANE-10",
            "pillar": "P4",
            "title": "Uniform Circular Motion: Centripetal Acceleration Invariant",
            "subtitle": "Constant speed, turning velocity: the radial acceleration law",
            "story": "When an object travels along a circular path of radius R at constant speed v, its velocity vector turns continuously. This steady change in direction demands an inward radial acceleration.",
            "key_idea": "Centripetal acceleration is strictly directed toward the center: $a_c = \\frac{v^2}{R} = \\omega^2 R = \\frac{4\\pi^2 R}{T^2}$. Because velocity and acceleration are mutually perpendicular ($\\vec{v} \\cdot \\vec{a}_c = 0$), the speed remains constant while direction changes.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Circle orbit -->
                <circle cx="250" cy="60" r="45" fill="none" stroke="#475569" stroke-width="2" stroke-dasharray="4"/>
                <circle cx="250" cy="15" r="6" fill="#38bdf8"/>
                <!-- Tangent velocity -->
                <line x1="250" y1="15" x2="310" y2="15" stroke="#10b981" stroke-width="2.5"/>
                <polygon points="310,11 318,15 310,19" fill="#10b981"/>
                <text x="325" y="19" fill="#10b981" font-size="14" font-weight="bold">v</text>
                <!-- Centripetal acceleration -->
                <line x1="250" y1="15" x2="250" y2="50" stroke="#f43f5e" stroke-width="2.5"/>
                <polygon points="246,50 250,58 254,50" fill="#f43f5e"/>
                <text x="258" y="45" fill="#f43f5e" font-size="14" font-weight="bold">a_c = v² / R</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Circular trajectory with constant scalar speed (dv/dt = 0).",
                "Represent: Tangent velocity vector v and perpendicular radial acceleration a_c pointing toward center.",
                "Build: Express relations: omega = v / R = 2*pi / T; a_c = v^2 / R = omega^2 * R.",
                "Check: Centripetal acceleration scales quadratically with speed and inversely with circle radius."
            ],
            "worked_example": "A test vehicle travels around a roundabout of radius $R = 50\\text{ m}$ at speed $v = 20\\text{ m/s}$. Centripetal acceleration: $a_c = \\frac{20^2}{50} = \\frac{400}{50} = 8.0\\text{ m/s}^2$ directed inward.",
            "watch_out": "Claiming acceleration is zero because speed is constant.",
            "quick_check": "Doubling speed on a curve quadruples the required centripetal acceleration (a_c proportional to v^2).",
            "practice_targets": ["PHYS-MIP-023", "PHYS-MIP-024"]
        },
        {
            "id": "PLANE-11",
            "pillar": "P4",
            "title": "Non-Uniform Curvilinear Motion: Tangential vs Normal Components",
            "subtitle": "Intrinsic Frenet-Serret frame: separating speed change from direction change",
            "story": "Along a general curved path where both speed and direction change, acceleration resolves into two natural orthogonal directions: along the tangent and along the normal.",
            "key_idea": "Tangential acceleration $a_t = \\frac{dv}{dt}$ changes speed magnitude. Normal acceleration $a_n = \\frac{v^2}{\\rho}$ changes direction, where $\\rho$ is the instantaneous radius of curvature. Total acceleration is $|\\vec{a}| = \\sqrt{a_t^2 + a_n^2}$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <path d="M 60 100 Q 250 20 440 90" fill="none" stroke="#475569" stroke-width="2"/>
                <circle cx="250" cy="48" r="6" fill="#facc15"/>
                <!-- Tangent a_t -->
                <line x1="250" y1="48" x2="310" y2="58" stroke="#10b981" stroke-width="2.5"/>
                <polygon points="310,54 318,59 310,64" fill="#10b981"/>
                <text x="325" y="64" fill="#10b981" font-size="14" font-weight="bold">a_t = dv/dt</text>
                <!-- Normal a_n -->
                <line x1="250" y1="48" x2="240" y2="95" stroke="#f43f5e" stroke-width="2.5"/>
                <polygon points="236,95 238,103 244,95" fill="#f43f5e"/>
                <text x="180" y="90" fill="#f43f5e" font-size="14" font-weight="bold">a_n = v² / &rho;</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Motion along curved path with non-constant speed.",
                "Represent: Frenet-Serret frame: unit tangent u_t = v / |v| and unit normal u_n toward center of curvature.",
                "Build: a_t = (v . a) / v; a_n = sqrt(|a|^2 - a_t^2); Radius of curvature rho = v^2 / a_n.",
                "Check: At the peak of a projectile: v is horizontal u cos theta and a is vertical -g, so a_t = 0 and a_n = g => rho_apex = (u^2 cos^2 theta) / g."
            ],
            "worked_example": "A car speeds up along a circular track of radius $R = 100\\text{ m}$ with $a_t = 3.0\\text{ m/s}^2$ at speed $v = 20\\text{ m/s}$. Normal acceleration: $a_n = \\frac{20^2}{100} = 4.0\\text{ m/s}^2$. Total acceleration: $a = \\sqrt{3^2 + 4^2} = 5.0\\text{ m/s}^2$.",
            "watch_out": "Confusing total acceleration with normal centripetal acceleration when speed is varying.",
            "quick_check": "At any point where speed is momentarily stationary (dv/dt = 0), total acceleration is purely normal.",
            "practice_targets": ["PHYS-MIP-025"]
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
                    <p>{recon.get('harmonic_origin', recon.get('root_decomposition', recon.get('shortest_time', recon.get('apex_simplification', ''))))}</p>
                    <p>{recon.get('limiting_consequence', recon.get('geometric_mean', recon.get('zero_drift', recon.get('apex_curvature', ''))))}</p>
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
  <title>Motion in a Plane (2D Motion) &bull; Tri-Modal Master Suite</title>
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
          <h1>Motion in a Plane &bull; Tri-Modal Master Tablet Suite</h1>
          <p>Grade 9 Olympiad Physics &bull; Projectiles, Relative Frames &amp; Curvilinear Motion</p>
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
          <p>Instantaneous cues, dual representations, first executable moves, and anti-patterns for all 11 planar motion competencies.</p>
        </div>
        {atlas_table_html}

        <div class="recon-section-intro">
          <h3>🔬 Deep Phenomenological Reconstruction Cycles</h3>
          <p>First-principles derivation vs Galilean cancellation, complementary angle symmetry, and Frenet-Serret curvature.</p>
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
    raw_path = REPO_ROOT / "scratch/_raw_planar_motion_tri_modal.html"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[OK] Wrote raw HTML template: {raw_path} ({len(full_html)} bytes)")

    # Target destinations
    output_path = REPO_ROOT / "standalone/practice/core2-physics-planar-motion-grade9-master.html"
    public_path = REPO_ROOT / "public/standalone/practice/core2-physics-planar-motion-grade9-master.html"
    artifact_path = Path(r"C:\Users\reall\.gemini\antigravity\brain\40014ef9-8d66-475e-aff1-d6e53797ebbd\physics_planar_motion_master_app.html")

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
    print("PLANAR MOTION MASTER TABLET APP COMPILATION COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    compile_tri_modal_planar_motion()
