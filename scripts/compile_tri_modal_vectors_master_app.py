# scripts/compile_tri_modal_vectors_master_app.py
"""
Compile Tri-Modal Master Tablet Application for Vectors & Coordinate Frames.
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

def compile_tri_modal_vectors():
    print(f"\n{'='*80}")
    print("COMPILING TRI-MODAL MASTER TABLET APP: VECTORS & COORDINATE FRAMES")
    print("Tripartite Architecture: Core 1A (Learn) <-> Core 1B (Recall) <-> Core 2 (Practice)")
    print(f"{'='*80}\n")

    # Load Data
    bank_path = REPO_ROOT / "TEST/physics-research/question_bank_vectors_grade9.v1.json"
    ontology_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_vectors_ontology.v1.json"
    reconstruction_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_vectors_reconstruction.v1.json"
    adapters_path = REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json"

    with open(bank_path, "r", encoding="utf-8") as f:
        bank_data = json.load(f)
    with open(ontology_path, "r", encoding="utf-8") as f:
        ontology_data = json.load(f)
    with open(reconstruction_path, "r", encoding="utf-8") as f:
        reconstruction_data = json.load(f)
    with open(adapters_path, "r", encoding="utf-8") as f:
        adapters_data = json.load(f)["topic_adapters"]["vectors-and-components"]

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

    # =========================================================================
    # TAB 1: CORE 2 PRACTICE CARDS (25 Questions)
    # =========================================================================
    def render_practice_card(q, index):
        qid = q["question_id"]
        comp = q.get("subtopic_competency_ref", "VEC-01")
        band = q.get("qrt_contract", {}).get("difficulty_band", "D2")
        demand = q.get("qrt_contract", {}).get("primary_demand", "APPLY")
        comp_title = adapters_data.get("subtopic_competency_map", {}).get(comp, {}).get("title", comp)
        prov = q.get("provenance", {})
        prov_src = prov.get("source_fixture", "Grade 9 Golden Fixture (physics-vectors-revised-core2.pdf)")
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
        for opt_key, opt_text in options.items():
            is_correct = (opt_key == correct_key)
            diag_text = distractors.get(opt_key, "Option diagnostic.")
            options_html += f"""
            <button class="opt-btn" data-opt="{opt_key}" onclick="selectOption('{qid}', '{opt_key}', {str(is_correct).lower()})">
                <span class="opt-key">{opt_key}</span>
                <span class="opt-text">{opt_text}</span>
            </button>
            <div id="diag-{qid}-{opt_key}" class="opt-diag" style="display:none;">
                <strong>{'&check; Correct Insight:' if is_correct else '&cross; Trap Diagnosis:'}</strong> {diag_text}
            </div>
            """

        # Progressive Hints (3 Tiers with Open Prompt Questions)
        hints = q.get("progressive_hints", [])
        hints_html = ""
        for h in hints:
            tier = h.get("tier", 1)
            prompt = h.get("prompt", "")
            reveal = h.get("reveal", "")
            tier_title = "HINT 1 - WHAT IS THE KEY PHYSICS?" if tier == 1 else ("HINT 2 - HOW WOULD YOU REPRESENT IT?" if tier == 2 else "HINT 3 - WHAT WOULD YOU WRITE FIRST?")
            hints_html += f"""
            <div class="hint-item" id="hint-{qid}-{tier}">
                <div class="hint-header">
                    <span class="hint-badge">{tier_title}</span>
                    <button class="hint-unlock-btn" onclick="unlockHint('{qid}', {tier})">Reveal Answer</button>
                </div>
                <div class="hint-prompt"><strong>Question:</strong> {prompt}</div>
                <div class="hint-reveal" id="reveal-{qid}-{tier}" style="display:none;">
                    <strong>Reveal:</strong> {reveal}
                </div>
            </div>
            """

        # Model Proof (5 Steps)
        proof = q.get("model_proof", {})
        steps = [
            ("Step 1: Understand", proof.get("step_1_understand", "")),
            ("Step 2: Represent", proof.get("step_2_represent", "")),
            ("Step 3: Connect", proof.get("step_3_connect", "")),
            ("Step 4: Execute", proof.get("step_4_execute", "")),
            ("Step 5: Conclude", proof.get("step_5_conclude", ""))
        ]
        steps_html = "".join(f'<div class="proof-step"><strong>{title}:</strong> {text}</div>' for title, text in steps if text)

        # Independent Checks
        indep = q.get("independent_check", {})
        dim_formula = indep.get("dimensional_homogeneity", {}).get("formula", "[L]")
        limits = indep.get("limiting_cases", [])
        limits_html = "".join(f"<li><strong>{l.get('case', '')}:</strong> {l.get('check', '')}</li>" for l in limits)
        quick = indep.get("quick_check", "")
        watch = indep.get("watch_out", "")
        method = indep.get("method", "Dual Limiting Analysis")

        return f"""
        <div class="question-card" id="card-{qid}" data-band="{band}" data-comp="{comp}">
            <div class="card-header">
                <div class="card-source-tag">
                    <span class="qid-badge">{qid}</span>
                    <span class="band-badge band-{band.lower()}">{band}</span>
                    <span class="demand-badge">{demand}</span>
                </div>
                <div class="card-comp-box">
                    <button class="cross-link-btn" onclick="jumpToChapter('{comp}')">
                        &larr; Core 1A: {comp} - {comp_title}
                    </button>
                </div>
            </div>

            <div class="stem-container">
                {q['stem']}
            </div>

            {fig_html}

            <div class="options-container">
                {options_html}
            </div>

            <div id="feedback-{qid}" class="feedback-banner" style="display:none;"></div>

            <!-- Hint Ladder -->
            <div class="hint-ladder-container">
                <div class="hint-ladder-title">Context-Anchored Prompt-Reveal Hint Ladder</div>
                {hints_html}
            </div>

            <!-- Model Proof & Independent Checks -->
            <details class="solution-details">
                <summary class="solution-summary">
                    <span>View Olympian Derivation & Independent Checks</span>
                    <span class="summary-arrow">&blacktriangledown;</span>
                </summary>
                <div class="solution-content">
                    <div class="solution-section-title">5-Step Reasoning Ladder</div>
                    <div class="proof-steps-box">
                        {steps_html}
                    </div>
                    <div class="final-expr-box">
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
            "id": "VEC-01",
            "pillar": "P1",
            "title": "Scalars, Vectors and Sign",
            "subtitle": "Direction is information; sign belongs to a declared axis",
            "story": "A scalar is complete with magnitude alone (distance, speed, mass, time). A vector needs magnitude and direction (displacement, velocity, acceleration, force). In one dimension, direction can be encoded by sign only after you declare the positive axis convention.",
            "key_idea": "Do not classify from the unit. Ask whether reversing direction changes the physical state. Then declare an axis before attaching + or - signs. Reversing the positive axis flips algebraic signs but leaves physical reality invariant.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="50" y1="60" x2="450" y2="60" stroke="#94a3b8" stroke-width="2"/>
                <polygon points="450,55 460,60 450,65" fill="#94a3b8"/>
                <text x="465" y="65" fill="#94a3b8" font-size="14" font-weight="bold">+x East</text>
                <circle cx="200" cy="60" r="4" fill="#fff"/>
                <text x="200" y="80" fill="#94a3b8" font-size="14" text-anchor="middle">Origin 0</text>
                <!-- +8m East -->
                <line x1="200" y1="40" x2="360" y2="40" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="360,35 370,40 360,45" fill="#38bdf8"/>
                <text x="280" y="30" fill="#38bdf8" font-size="14" font-weight="bold">+8 m East</text>
                <!-- -5m West -->
                <line x1="200" y1="95" x2="100" y2="95" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="100,100 90,95 100,90" fill="#f43f5e"/>
                <text x="145" y="115" fill="#f43f5e" font-size="14" font-weight="bold">-5 m West</text>
            </svg>
            """,
            "how_it_works": [
                "Recognise: Check if reversing heading changes the physical outcome.",
                "Represent: Mark the positive axis arrow (+x East or Right) before calculating.",
                "Compute: Combine 1D displacements algebraically: Delta x = sum(signed legs).",
                "Interpret: Translate the sign of the final answer back into physical orientation."
            ],
            "worked_example": "A robot moves $+7\\text{ m}$, then $-11\\text{ m}$, then $+2\\text{ m}$ along the $x$-axis. Net displacement: $\\Delta x = (+7) + (-11) + (+2) = -2\\text{ m}$ ($2\\text{ m}$ West). Total distance traveled: $d = |+7| + |-11| + |+2| = 20\\text{ m}$.",
            "watch_out": "Treating negative sign as a smaller physical magnitude. An object moving at $-10\\text{ m/s}$ has 5 times the speed and 25 times the kinetic energy of an object at $+2\\text{ m/s}$.",
            "quick_check": "Flipping coordinate convention (+x pointing West) transforms displacement to +2 m, which still physically points West.",
            "practice_targets": ["PHYS-VEC-001", "PHYS-VEC-002"]
        },
        {
            "id": "VEC-02",
            "pillar": "P1",
            "title": "Draw, Compare, Translate, and Reverse Vectors",
            "subtitle": "Length represents magnitude; the arrowhead represents direction",
            "story": "A vector diagram is a physical representation, not decoration. Free vectors can be translated parallel to themselves without rotating or resizing without modifying the vector state. Reversing the arrow creates the opposite vector.",
            "key_idea": "Equal vectors need BOTH identical magnitude and identical direction. The opposite vector $-\\vec{A}$ has the same magnitude as $\\vec{A}$ but points exactly the other way ($180^\\circ$ reversal).",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Vector A -->
                <line x1="60" y1="80" x2="160" y2="40" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="155,48 165,38 150,37" fill="#38bdf8"/>
                <text x="110" y="45" fill="#38bdf8" font-size="14" font-weight="bold">Vector A</text>
                <!-- Translated Vector A -->
                <line x1="200" y1="80" x2="300" y2="40" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="295,48 305,38 290,37" fill="#38bdf8"/>
                <text x="250" y="45" fill="#38bdf8" font-size="14" font-weight="bold">A (translated = equal)</text>
                <!-- Opposite Vector -A -->
                <line x1="440" y1="40" x2="340" y2="80" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="345,72 335,82 350,83" fill="#f43f5e"/>
                <text x="390" y="75" fill="#f43f5e" font-size="14" font-weight="bold">-A (opposite)</text>
            </svg>
            """,
            "how_it_works": [
                "Read: Arrow length represents magnitude to scale; arrowhead indicates spatial ray.",
                "Translate: Move vectors across the canvas without rotation to align origins.",
                "Invert: To form -A, invert the arrowhead 180 degrees while keeping magnitude identical.",
                "Check: A + (-A) = 0 (the zero/null vector has magnitude zero and undefined direction)."
            ],
            "worked_example": "Two force vectors $\\vec{F}_1$ and $\\vec{F}_2$ each have magnitude $10\\text{ N}$. $\\vec{F}_1$ points East and $\\vec{F}_2$ points North. They are NOT equal vectors ($\\vec{F}_1 \\neq \\vec{F}_2$) because their directions are perpendicular, even though $|\\vec{F}_1| = |\\vec{F}_2| = 10\\text{ N}$.",
            "watch_out": "Believing equal magnitudes make vectors equal regardless of spatial direction.",
            "quick_check": "Two vectors satisfy $\\vec{A} + \\vec{B} = \\vec{0} \\iff \\vec{B} = -\\vec{A}$ (equal in magnitude and strictly antiparallel).",
            "practice_targets": ["PHYS-VEC-003", "PHYS-VEC-004"]
        },
        {
            "id": "VEC-03",
            "pillar": "P2",
            "title": "Components, Quadrants, and Angle Reference",
            "subtitle": "Choose the frame first; then project the arrow",
            "story": "Components are signed projections of a vector onto chosen axes. They are not extra physical vectors; they are another mathematical description of the same physical arrow.",
            "key_idea": "Geometry decides sine/cosine. The component adjacent to the stated angle uses cosine; the opposite component uses sine. Signs come from arrow direction and quadrant.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <line x1="250" y1="10" x2="250" y2="110" stroke="#64748b" stroke-width="1.5"/>
                <line x1="50" y1="60" x2="450" y2="60" stroke="#64748b" stroke-width="1.5"/>
                <!-- Vector in QII -->
                <line x1="250" y1="60" x2="130" y2="20" stroke="#facc15" stroke-width="3"/>
                <polygon points="135,28 125,18 140,18" fill="#facc15"/>
                <text x="175" y="30" fill="#facc15" font-size="14" font-weight="bold">A (Quadrant II)</text>
                <!-- Projections -->
                <line x1="250" y1="20" x2="130" y2="20" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4"/>
                <text x="190" y="15" fill="#38bdf8" font-size="14">A_x &lt; 0</text>
                <line x1="130" y1="60" x2="130" y2="20" stroke="#10b981" stroke-width="2" stroke-dasharray="4"/>
                <text x="80" y="45" fill="#10b981" font-size="14">A_y &gt; 0</text>
            </svg>
            """,
            "how_it_works": [
                "Frame: Mark +x and +y before calculating.",
                "Project: Identify adjacent side (cos) and opposite side (sin) relative to the stated angle.",
                "Signs: Determine quadrant signs: Q1 (+,+), Q2 (-,+), Q3 (-,-), Q4 (+,-).",
                "Check: Reconstruct magnitude via Pythagoras: |A| = sqrt(A_x^2 + A_y^2)."
            ],
            "worked_example": "Vector $\\vec{A}$ has magnitude $10.0\\text{ units}$ and points $30^\\circ$ above the negative $x$-axis (Quadrant II). $A_x = -10.0\\cos 30^\\circ = -5\\sqrt{3} \\approx -8.66\\text{ units}$, $A_y = +10.0\\sin 30^\\circ = +5.0\\text{ units}$.",
            "watch_out": "Assuming horizontal is always cosine and vertical is always sine without checking the reference axis.",
            "quick_check": "If angle theta is measured from the vertical y-axis, then A_y = |A| cos theta and A_x = |A| sin theta.",
            "practice_targets": ["PHYS-VEC-005", "PHYS-VEC-006"]
        },
        {
            "id": "VEC-04",
            "pillar": "P3",
            "title": "Add Vectors and Find a Resultant",
            "subtitle": "Head-to-tail geometry and component addition must agree",
            "story": "Vector addition combines directional changes. Place vectors head-to-tail; the resultant runs from the first tail to the final head. In components, add x with x and y with y.",
            "key_idea": "The resultant is not the path length. Triangle inequality guarantees $|A - B| \\le |R| \\le A + B$. Geometry and components are two views of the same addition.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Leg A (9m East) -->
                <line x1="80" y1="100" x2="260" y2="100" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="260,95 270,100 260,105" fill="#38bdf8"/>
                <text x="175" y="118" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">A = 9 m East</text>
                <!-- Leg B (12m North) -->
                <line x1="270" y1="100" x2="270" y2="20" stroke="#10b981" stroke-width="3"/>
                <polygon points="265,20 270,10 275,20" fill="#10b981"/>
                <text x="320" y="60" fill="#10b981" font-size="14" font-weight="bold">B = 12 m North</text>
                <!-- Resultant R -->
                <line x1="80" y1="100" x2="270" y2="10" stroke="#facc15" stroke-width="3"/>
                <polygon points="265,18 273,8 258,8" fill="#facc15"/>
                <text x="160" y="50" fill="#facc15" font-size="14" font-weight="bold">Resultant R = 15 m</text>
            </svg>
            """,
            "how_it_works": [
                "Diagram route: Place vectors head-to-tail; draw the closing vector from start to finish.",
                "Component route: R_x = sum(A_x), R_y = sum(A_y).",
                "Magnitude: For perpendicular legs, |R| = sqrt(R_x^2 + R_y^2).",
                "Check: Path length (9 + 12 = 21 m) is strictly greater than resultant displacement (15 m)."
            ],
            "worked_example": "A student walks $9.0\\text{ m}$ East, then $12.0\\text{ m}$ North. $|\vec{R}| = \\sqrt{9^2 + 12^2} = 15.0\\text{ m}$. Direction: $\\tan\\theta = 12/9 = 4/3 \\implies \\theta = 53.1^\\circ$ North of East.",
            "watch_out": "Adding vector magnitudes algebraically ($9 + 12 = 21\\text{ m}$) as the resultant magnitude.",
            "quick_check": "A closed displacement path finishing at the start has zero resultant (R = 0).",
            "practice_targets": ["PHYS-VEC-007", "PHYS-VEC-008", "PHYS-VEC-021"]
        },
        {
            "id": "VEC-05",
            "pillar": "P3",
            "title": "Subtract Vectors and Build Change Vectors",
            "subtitle": "Final minus initial is a geometric operation",
            "story": "Vector subtraction means add the opposite: $\\vec{A} - \\vec{B} = \\vec{A} + (-\\vec{B})$. Physical change vectors follow the same rule: $\\Delta\\vec{v} = \\vec{v}_f - \\vec{v}_i$ and $\\Delta\\vec{p} = \\vec{p}_f - \\vec{p}_i$.",
            "key_idea": "A change vector compares two states. Equal speeds do not imply zero change when directions differ! For turning at speed $v$ through angle $\\theta$: $|\\Delta\\vec{v}| = 2v\\sin(\\theta/2)$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Common origin -->
                <circle cx="120" cy="90" r="4" fill="#fff"/>
                <line x1="120" y1="90" x2="240" y2="90" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="240,85 250,90 240,95" fill="#38bdf8"/>
                <text x="185" y="110" fill="#38bdf8" font-size="14" font-weight="bold">v_i (East)</text>
                <line x1="120" y1="90" x2="120" y2="20" stroke="#10b981" stroke-width="3"/>
                <polygon points="115,20 120,10 125,20" fill="#10b981"/>
                <text x="75" y="45" fill="#10b981" font-size="14" font-weight="bold">v_f (North)</text>
                <!-- Change vector Delta v -->
                <line x1="250" y1="90" x2="120" y2="10" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="128,15 118,8 122,22" fill="#f43f5e"/>
                <text x="210" y="45" fill="#f43f5e" font-size="14" font-weight="bold">Δv = v_f - v_i</text>
            </svg>
            """,
            "how_it_works": [
                "State: Draw initial and final vectors from a common origin.",
                "Reverse: Subtracting means reversing the initial vector: Delta v = v_f + (-v_i).",
                "Compute: Delta v_x = v_fx - v_ix, Delta v_y = v_fy - v_iy.",
                "Interpret: Delta v points from the tip of v_i to the tip of v_f."
            ],
            "worked_example": "A cyclist travels $6.0\\text{ m/s}$ East, then turns North at $6.0\\text{ m/s}$. Speed is constant ($6.0\\text{ m/s}$), but $\\Delta\\vec{v} = 6\\hat{j} - 6\\hat{i}\\text{ m/s}$, with magnitude $|\\Delta\\vec{v}| = \\sqrt{6^2 + 6^2} = 6\\sqrt{2}\\text{ m/s} \\approx 8.49\\text{ m/s}$ directed North-West.",
            "watch_out": "Claiming Delta v = 0 because speed is unchanged.",
            "quick_check": "Complete 180-degree reversal of velocity at speed v gives Delta v = 2v.",
            "practice_targets": ["PHYS-VEC-009", "PHYS-VEC-010", "PHYS-VEC-022"]
        },
        {
            "id": "VEC-06",
            "pillar": "P2",
            "title": "Recover Magnitude and Direction",
            "subtitle": "Components are coordinates of the vector state",
            "story": "When $R_x$ and $R_y$ are known, the magnitude follows from the component triangle. The direction needs both a reference axis and the correct quadrant.",
            "key_idea": "Magnitude alone is not a complete vector answer. Report direction whenever the question asks for a vector quantity. Reference angle $\\tan\\alpha = |R_y / R_x|$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <rect x="100" y="30" width="160" height="70" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4"/>
                <line x1="100" y1="100" x2="260" y2="100" stroke="#38bdf8" stroke-width="3"/>
                <text x="180" y="118" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">R_x</text>
                <line x1="260" y1="100" x2="260" y2="30" stroke="#10b981" stroke-width="3"/>
                <text x="280" y="70" fill="#10b981" font-size="14" font-weight="bold">R_y</text>
                <line x1="100" y1="100" x2="260" y2="30" stroke="#facc15" stroke-width="3"/>
                <polygon points="255,38 263,28 250,28" fill="#facc15"/>
                <text x="160" y="55" fill="#facc15" font-size="14" font-weight="bold">|R| = √(R_x² + R_y²)</text>
            </svg>
            """,
            "how_it_works": [
                "Magnitude: |R| = sqrt(R_x^2 + R_y^2).",
                "Reference angle: tan alpha = |R_y / R_x|.",
                "Quadrant: Use signs of R_x and R_y to convert alpha into compass direction.",
                "Check: |R| >= max(|R_x|, |R_y|) and |R| <= |R_x| + |R_y|."
            ],
            "worked_example": "Two perpendicular horizontal forces: $9.0\\text{ N}$ East ($+x$) and $12.0\\text{ N}$ South ($-y$). Net magnitude: $|\vec{F}| = \\sqrt{9^2 + (-12)^2} = 15.0\\text{ N}$. Angle: $\\alpha = \\arctan(12/9) \\approx 53.1^\\circ$ South of East.",
            "watch_out": "Reporting magnitude without specifying angle and reference axis.",
            "quick_check": "If |R_x| = |R_y|, then angle is exactly 45 degrees and |R| = |R_x| sqrt(2).",
            "practice_targets": ["PHYS-VEC-011", "PHYS-VEC-012"]
        },
        {
            "id": "VEC-07",
            "pillar": "P4",
            "title": "Relative Velocity",
            "subtitle": "The observer is the vector you subtract",
            "story": "Relative velocity asks what one observer sees another object doing. 'Velocity of A relative to B' means subtract the observer B from A: $\\vec{v}_{A/B} = \\vec{v}_A - \\vec{v}_B$.",
            "key_idea": "Order follows the words: $\\vec{v}_{A/B} = \\vec{v}_A - \\vec{v}_B$. Express both velocities in the same axes before subtracting. To shift to observer B, apply $-\\vec{v}_B$ to all bodies.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Cyclist A -->
                <line x1="60" y1="40" x2="220" y2="40" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="220,35 230,40 220,45" fill="#38bdf8"/>
                <text x="140" y="30" fill="#38bdf8" font-size="14" font-weight="bold">v_A = 8 m/s East</text>
                <!-- Cyclist B -->
                <line x1="60" y1="80" x2="160" y2="80" stroke="#10b981" stroke-width="3"/>
                <polygon points="160,75 170,80 160,85" fill="#10b981"/>
                <text x="110" y="100" fill="#10b981" font-size="14" font-weight="bold">v_B = 5 m/s East</text>
                <!-- Relative Vector v_A/B -->
                <line x1="300" y1="60" x2="360" y2="60" stroke="#facc15" stroke-width="3"/>
                <polygon points="360,55 370,60 360,65" fill="#facc15"/>
                <text x="335" y="50" fill="#facc15" font-size="14" font-weight="bold">v_A/B = 3 m/s East</text>
            </svg>
            """,
            "how_it_works": [
                "Name roles: Object A, Observer B.",
                "Same frame: Write both ground-frame velocity vectors in the same coordinate system.",
                "Subtract: v_A/B = v_A - v_B.",
                "Check: If A and B move with identical velocity, v_A/B = 0."
            ],
            "worked_example": "Cyclist A moves East at $8.0\\text{ m/s}$; Cyclist B moves East at $5.0\\text{ m/s}$. Velocity of A relative to B: $\\vec{v}_{A/B} = 8.0 - 5.0 = +3.0\\text{ m/s}$ (East). Velocity of B relative to A: $\\vec{v}_{B/A} = 5.0 - 8.0 = -3.0\\text{ m/s}$ (West).",
            "watch_out": "Reversing subtraction order: v_A/B != v_B - v_A.",
            "quick_check": "Reciprocal antisymmetry: v_A/B = -v_B/A.",
            "practice_targets": ["PHYS-VEC-013", "PHYS-VEC-014", "PHYS-VEC-023"]
        },
        {
            "id": "VEC-08",
            "pillar": "P2",
            "title": "Tangent and Radial Directions",
            "subtitle": "Circular motion separates velocity direction from acceleration direction",
            "story": "At any point on a circular path, instantaneous velocity is tangent to the path. Centripetal acceleration points radially inward toward the centre.",
            "key_idea": "Constant speed does not mean constant velocity. Direction changes continuously, so the velocity vector changes and acceleration is non-zero: $a_c = \\frac{v^2}{R}$. Velocity and centripetal acceleration are strictly perpendicular: $\\vec{v} \\cdot \\vec{a}_c = 0$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Circle portion -->
                <circle cx="200" cy="110" r="70" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4"/>
                <circle cx="200" cy="40" r="5" fill="#fff"/>
                <text x="175" y="35" fill="#fff" font-size="14">Particle</text>
                <!-- Tangent Velocity -->
                <line x1="200" y1="40" x2="290" y2="40" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="290,35 300,40 290,45" fill="#38bdf8"/>
                <text x="250" y="30" fill="#38bdf8" font-size="14" font-weight="bold">v (tangent)</text>
                <!-- Radial Acceleration -->
                <line x1="200" y1="40" x2="200" y2="90" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="195,90 200,100 205,90" fill="#f43f5e"/>
                <text x="210" y="75" fill="#f43f5e" font-size="14" font-weight="bold">a_c (inward)</text>
            </svg>
            """,
            "how_it_works": [
                "Draw radius from centre to particle.",
                "Velocity: Draw tangent perpendicular to radius in direction of travel.",
                "Acceleration: Point radially inward toward centre: a_c = v^2 / R.",
                "Release: If constraint breaks, particle continues along tangent at speed v."
            ],
            "worked_example": "A stone whirled clockwise on a horizontal string. At the topmost point (12 o'clock), velocity points due East (tangent). If string breaks, stone flies due East in a straight line at that instant.",
            "watch_out": "Believing the object flies radially outward when released (centrifugal misconception).",
            "quick_check": "In uniform circular motion, tangential acceleration is zero (a_t = dv/dt = 0) while radial acceleration is non-zero (a_n = v^2 / R).",
            "practice_targets": ["PHYS-VEC-015", "PHYS-VEC-016"]
        },
        {
            "id": "VEC-09",
            "pillar": "P1",
            "title": "Interaction Pairs and Body Ownership",
            "subtitle": "Equal-and-opposite forces can act on different bodies",
            "story": "Newton-III pairs are vector pairs with equal magnitude and opposite direction, but they act on different bodies: $\\vec{F}_{A\\text{ on }B} = -\\vec{F}_{B\\text{ on }A}$. Net-force equations contain only forces acting on the chosen body.",
            "key_idea": "Body ownership prevents false cancellation. Always label force as 'Agent on Target'. Action-reaction pairs can NEVER appear on the same isolated body diagram.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Book FBD -->
                <rect x="80" y="45" width="120" height="30" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
                <text x="140" y="65" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Book</text>
                <line x1="140" y1="45" x2="140" y2="15" stroke="#10b981" stroke-width="2.5"/>
                <polygon points="135,15 140,5 145,15" fill="#10b981"/>
                <text x="150" y="25" fill="#10b981" font-size="14">N (table on book)</text>
                <line x1="140" y1="75" x2="140" y2="105" stroke="#f43f5e" stroke-width="2.5"/>
                <polygon points="135,105 140,115 145,105" fill="#f43f5e"/>
                <text x="150" y="105" fill="#f43f5e" font-size="14">W (Earth on book)</text>
                <!-- Partner note -->
                <text x="350" y="55" fill="#e2e8f0" font-size="14" text-anchor="middle">Equal &amp; opposite on book</text>
                <text x="350" y="80" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">NOT a Newton-III pair!</text>
            </svg>
            """,
            "how_it_works": [
                "Choose body: Decide whose free-body diagram you are drawing.",
                "Name interaction: table on book, Earth on book, etc.",
                "Pair: F_{A on B} = -F_{B on A} (acts on A, not B).",
                "Check: Normal force and gravity on book balance by First Law, not Third Law."
            ],
            "worked_example": "A book rests on a table. The reaction partner to $\\vec{N}_{\\text{table on book}}$ is $\\vec{N}_{\\text{book on table}}$ (downward on table). The reaction partner to $\\vec{W}_{\\text{Earth on book}}$ is $\\vec{F}_{\\text{book on Earth}}$ (upward on Earth).",
            "watch_out": "Cancelling action-reaction forces on a single object.",
            "quick_check": "If an elevator accelerates upward, normal force changes to m(g + a) != mg, yet third-law pairs remain equal and opposite.",
            "practice_targets": ["PHYS-VEC-017", "PHYS-VEC-018"]
        },
        {
            "id": "VEC-10",
            "pillar": "P5",
            "title": "Angle Between Vectors and Work",
            "subtitle": "The angle between force and displacement controls the sign",
            "story": "Work is a scalar built from two vectors: $W = \\vec{F} \\cdot \\vec{s} = |\\vec{F}||\\vec{s}|\\cos\\theta$. Its sign depends strictly on the angle $\\theta$ between force and displacement.",
            "key_idea": "Read the angle from the physical arrows before using the equation. $\\theta = 0^\\circ \\implies +Fs$; $\\theta = 90^\\circ \\implies 0$; $\\theta = 180^\\circ \\implies -Fs$.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <!-- Common origin -->
                <circle cx="250" cy="60" r="5" fill="#fff"/>
                <!-- Displacement s East -->
                <line x1="250" y1="60" x2="380" y2="60" stroke="#38bdf8" stroke-width="3"/>
                <polygon points="380,55 390,60 380,65" fill="#38bdf8"/>
                <text x="320" y="50" fill="#38bdf8" font-size="14" font-weight="bold">Displacement s</text>
                <!-- Braking Force F West -->
                <line x1="250" y1="60" x2="120" y2="60" stroke="#f43f5e" stroke-width="3"/>
                <polygon points="120,65 110,60 120,55" fill="#f43f5e"/>
                <text x="170" y="50" fill="#f43f5e" font-size="14" font-weight="bold">Braking Force F</text>
                <text x="250" y="90" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">θ = 180° ⇒ W = -Fs &lt; 0</text>
            </svg>
            """,
            "how_it_works": [
                "Represent: Draw F and s from a common reference point.",
                "Angle: Identify true angle theta between the vectors (0 <= theta <= 180 deg).",
                "Relation: W = F s cos theta.",
                "Check: Braking forces oppose displacement (theta = 180 deg), doing negative work."
            ],
            "worked_example": "A braking force of $200\\text{ N}$ acts opposite a $15\\text{ m}$ displacement ($\\theta = 180^\\circ$). Work done: $W = 200 \\times 15 \\times \\cos 180^\\circ = -3000\\text{ J}$.",
            "watch_out": "Assuming work is always positive because energy is a scalar.",
            "quick_check": "Centripetal force acts at 90 degrees to displacement, doing zero work: W_c = 0.",
            "practice_targets": ["PHYS-VEC-019", "PHYS-VEC-020", "PHYS-VEC-024"]
        },
        {
            "id": "VEC-11",
            "pillar": "P2",
            "title": "Bridge to Motion in 2D",
            "subtitle": "One vector state becomes two component equations",
            "story": "Motion in a plane becomes manageable when position, velocity and acceleration are split into $x$ and $y$ components. The components share the same time $t$ but evolve independently.",
            "key_idea": "The component method is the bridge: represent the vector state first ($\\vec{v} = v_x\\hat{i} + v_y\\hat{j}$), solve each axis, then reconstruct the final vector if needed.",
            "svg_diagram": """
            <svg viewBox="0 0 500 120" style="max-width:100%; height:auto;">
                <rect x="50" y="25" width="180" height="60" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
                <text x="140" y="48" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Horizontal (x)</text>
                <text x="140" y="72" fill="#e2e8f0" font-size="14" text-anchor="middle">v_x = constant (a_x = 0)</text>
                <rect x="270" y="25" width="180" height="60" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
                <text x="360" y="48" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">Vertical (y)</text>
                <text x="360" y="72" fill="#e2e8f0" font-size="14" text-anchor="middle">v_y = u_y - gt (a_y = -g)</text>
            </svg>
            """,
            "how_it_works": [
                "State: Write vector in unit vectors: v = v_x i + v_y j.",
                "Separate: Write one equation for x and one for y.",
                "Solve: Advance both components with shared clock t.",
                "Reconstruct: Recover speed |v| = sqrt(v_x^2 + v_y^2) and direction."
            ],
            "worked_example": "A ball has velocity components $v_x = 6.0\\text{ m/s}$ and $v_y = 8.0\\text{ m/s}$. Speed is $|\\vec{v}| = \\sqrt{6^2 + 8^2} = 10.0\\text{ m/s}$. Direction: $\\theta = \\arctan(8/6) \\approx 53.1^\\circ$ above the $+x$-axis.",
            "watch_out": "Mixing horizontal and vertical kinematic variables into a single 1D equation.",
            "quick_check": "In projectile motion, horizontal acceleration is zero (a_x = 0) and vertical acceleration is strictly -g.",
            "practice_targets": ["PHYS-VEC-023", "PHYS-VEC-025"]
        }
    ]

    def render_textbook_unit(u):
        uid = u["id"]
        how_html = "".join(f"<li>{step}</li>" for step in u["how_it_works"])
        targets_html = "".join(f'<button class="target-link-btn" onclick="jumpToCore2(\'{t}\')">{t}</button>' for t in u["practice_targets"])

        return f"""
        <div class="textbook-unit" id="{uid}">
            <div class="unit-header">
                <span class="unit-id-badge">{uid}</span>
                <span class="unit-pillar-badge">{u['pillar']}</span>
                <h2 class="unit-title">{u['title']}</h2>
            </div>
            <div class="unit-subtitle">{u['subtitle']}</div>

            <div class="unit-section">
                <div class="unit-section-title">Physical Concept &amp; Story</div>
                <p class="unit-story">{u['story']}</p>
            </div>

            <div class="unit-key-idea">
                <strong>Key Idea:</strong> {u['key_idea']}
            </div>

            <div class="unit-svg-container">
                {u['svg_diagram']}
            </div>

            <div class="unit-section">
                <div class="unit-section-title">How It Works (Systematic Reasoning)</div>
                <ol class="how-it-works-list">{how_html}</ol>
            </div>

            <div class="unit-worked-example">
                <strong>Worked Landmark Example:</strong>
                <p>{u['worked_example']}</p>
            </div>

            <div class="unit-notes-row">
                <div class="unit-watch-out">
                    <strong>Watch Out:</strong> {u['watch_out']}
                </div>
                <div class="unit-quick-check">
                    <strong>Quick Check:</strong> {u['quick_check']}
                </div>
            </div>

            <div class="unit-targets-row">
                <strong>Core 2 Challenge Practice Cards:</strong>
                <div class="targets-btn-group">{targets_html}</div>
            </div>
        </div>
        """

    textbook_units_html = "".join(render_textbook_unit(u) for u in TEXTBOOK_UNITS)

    # =========================================================================
    # TAB 3: CORE 1B RECALL & RECONSTRUCTION (Cycles, Probes & Atlas)
    # =========================================================================
    
    # 1. First-Move Atlas Table (11 Rows)
    atlas_rows_html = ""
    for r in ontology_data["first_move_atlas"]:
        cid = r["competency_id"]
        atlas_rows_html += f"""
        <tr>
            <td class="atlas-comp-cell"><button class="atlas-link-btn" onclick="jumpToChapter('{cid}')">{cid}</button></td>
            <td class="atlas-cue-cell"><strong>{r['cue']}</strong></td>
            <td class="atlas-rep-cell">{r['representation']}</td>
            <td class="atlas-move-cell">{r['first_executable_move']}</td>
            <td class="atlas-anti-cell"><span class="anti-text">{r['anti_pattern']}</span></td>
        </tr>
        """

    # 2. Phenomenological Reconstruction Cycles
    recons_html = ""
    for cycle in reconstruction_data.get("reconstruction_cycles", []):
        cid = cycle.get("cycle_id", "")
        phenom = cycle.get("phenomenon", "")
        comp_ref = cycle.get("competency_ref", "")
        std = cycle.get("standard_derivation", "")
        recon = cycle.get("phenomenological_reconstruction", {})
        
        recon_body_html = ""
        if isinstance(recon, dict):
            for k, v in recon.items():
                label = k.replace("_", " ").title()
                recon_body_html += f"<p><strong>{label}:</strong> {v}</p>"
        else:
            recon_body_html = f"<p>{recon}</p>"

        limits = cycle.get("limiting_boundary_checks", [])
        limits_html = ""
        for lim in limits:
            cond = lim.get("limit") or lim.get("condition") or ""
            out = lim.get("physical_consequence") or lim.get("expected_outcome") or ""
            limits_html += f"<li><strong>{cond}:</strong> {out}</li>"

        recons_html += f"""
        <div class="recon-card">
            <div class="recon-header">
                <span class="recon-id-badge">{cid}</span>
                <span class="recon-comp-badge">{comp_ref}</span>
                <h3 class="recon-title">{phenom}</h3>
            </div>
            <div class="recon-section">
                <div class="recon-section-title">Standard Algebraic Derivation</div>
                <p class="recon-std-text">{std}</p>
            </div>
            <div class="recon-section">
                <div class="recon-section-title">Phenomenological Reconstruction</div>
                <div class="recon-pivot-box">{recon_body_html}</div>
            </div>
            <div class="recon-section">
                <div class="recon-section-title">Limiting Boundary Verification</div>
                <ul class="recon-limits-list">{limits_html}</ul>
            </div>
        </div>
        """

    # 3. Cognitive Dissonance Probes
    probes_html = ""
    for p in reconstruction_data.get("cognitive_dissonance_probes", []):
        pid = p.get("probe_id", "")
        pref = p.get("competency_ref", "")
        trap = p.get("student_trap") or p.get("scenario") or ""
        soc = p.get("socratic_challenge") or p.get("dissonance_question") or ""
        res = p.get("resolution", "")

        probes_html += f"""
        <div class="probe-card">
            <div class="probe-header">
                <span class="probe-id-badge">{pid}</span>
                <span class="probe-comp-badge">{pref}</span>
            </div>
            <div class="probe-trap">
                <strong>Intuitive Trap / Misconception:</strong> {trap}
            </div>
            <div class="probe-challenge">
                <strong>Socratic Disruption:</strong> {soc}
            </div>
            <div class="probe-resolution">
                <strong>Newtonian Resolution:</strong> {res}
            </div>
        </div>
        """

    # 4. Cognitive Conflict Matrix
    ccm_html = ""
    for c in ontology_data.get("cognitive_conflict_matrix", []):
        cid = c.get("id", "")
        concept = c.get("concept", "")
        misc = c.get("intuitive_misconception", "")
        truth = c.get("newtonian_scientific_truth", "")
        exp = c.get("decisive_experiment", "")

        ccm_html += f"""
        <div class="ccm-card">
            <div class="ccm-header">
                <span class="ccm-id-badge">{cid}</span>
                <h4 class="ccm-title">{concept}</h4>
            </div>
            <div class="ccm-grid">
                <div class="ccm-col ccm-misc">
                    <strong>Intuitive Belief:</strong>
                    <p>{misc}</p>
                </div>
                <div class="ccm-col ccm-truth">
                    <strong>Newtonian Truth:</strong>
                    <p>{truth}</p>
                </div>
            </div>
            <div class="ccm-exp">
                <strong>Decisive Experiment:</strong> {exp}
            </div>
        </div>
        """

    # =========================================================================
    # MASTER HTML DOCUMENT ASSEMBLY (12.7" Tablet Touch Spec)
    # =========================================================================
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes"/>
  <title>Vectors &amp; Coordinate Frames - Tri-Modal Master Tablet App</title>
  {offline_katex_css_tag}
  <style id="katex-offline-font-faces">
  {decoded_katex_css}
  </style>
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --accent: #10b981;
      --accent-hover: #059669;
      --danger: #f43f5e;
      --warning: #facc15;
      --border: #334155;
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-family);
      line-height: 1.6;
      font-size: 16px;
      -webkit-font-smoothing: antialiased;
      padding: 0;
    }}
    
    /* 12.7" Tablet Container */
    .app-container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 20px;
    }}
    
    /* Relative Header (Non-occluding) */
    .app-header {{
      position: relative;
      background: #111827;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 22px 28px;
      margin-bottom: 24px;
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
      border-color: var(--accent);
      background: #064e3b;
    }}
    .opt-btn.incorrect {{
      border-color: var(--danger);
      background: #4c0519;
    }}
    .opt-diag {{
      background: #1e293b;
      border-left: 3px solid var(--primary);
      padding: 10px 14px;
      font-size: 14px;
      color: #e2e8f0;
      margin-bottom: 8px;
      border-radius: 0 6px 6px 0;
    }}

    .feedback-banner {{
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 15px;
      margin: 14px 0;
    }}
    .feedback-banner.correct {{
      background: #064e3b;
      border: 1px solid #059669;
      color: #a7f3d0;
    }}
    .feedback-banner.incorrect {{
      background: #4c0519;
      border: 1px solid #e11d48;
      color: #fecdd3;
    }}

    /* Hints */
    .hint-ladder-container {{
      margin: 18px 0;
      border-top: 1px dashed var(--border);
      padding-top: 16px;
    }}
    .hint-ladder-title {{
      font-size: 14px;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
    }}
    .hint-item {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      margin-bottom: 10px;
    }}
    .hint-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .hint-badge {{
      font-size: 12px;
      font-weight: 800;
      color: var(--warning);
      text-transform: uppercase;
    }}
    .hint-unlock-btn {{
      background: #334155;
      border: 1px solid #64748b;
      color: #fff;
      font-size: 13px;
      font-weight: 700;
      padding: 8px 14px;
      border-radius: 6px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
    .hint-unlock-btn:hover {{
      background: #475569;
    }}
    .hint-prompt {{
      font-size: 14px;
      color: #cbd5e1;
      margin-bottom: 6px;
    }}
    .hint-reveal {{
      background: #1e293b;
      border-left: 3px solid var(--warning);
      padding: 10px 14px;
      font-size: 14px;
      color: #fef08a;
      border-radius: 0 6px 6px 0;
      margin-top: 8px;
    }}

    /* Solution Details */
    .solution-details {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-top: 16px;
      overflow: hidden;
    }}
    .solution-summary {{
      padding: 14px 18px;
      font-weight: 700;
      font-size: 15px;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #1e293b;
      min-height: 48px;
    }}
    .solution-content {{
      padding: 18px;
    }}
    .solution-section-title {{
      font-size: 14px;
      font-weight: 800;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 14px 0 8px 0;
    }}
    .proof-step {{
      margin-bottom: 10px;
      font-size: 15px;
      line-height: 1.6;
    }}
    .final-expr-box {{
      background: #1e293b;
      border: 1px solid var(--border);
      padding: 12px 16px;
      border-radius: 6px;
      margin: 14px 0;
      font-size: 16px;
    }}
    .indep-check-box {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px 16px;
      font-size: 14px;
      line-height: 1.6;
    }}
    .limiting-cases-list {{
      margin-left: 20px;
      margin-top: 6px;
    }}
    .watch-out-text {{
      color: #f87171;
    }}

    /* Filter Pills */
    .filter-pills-row {{
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .filter-pill {{
      background: #1e293b;
      border: 1px solid var(--border);
      color: #94a3b8;
      font-size: 14px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 20px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
    }}
    .filter-pill.active {{
      background: var(--primary);
      border-color: var(--primary);
      color: #0b0f19;
    }}

    /* Tab 2: Textbook Styling */
    .textbook-unit {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 28px;
    }}
    .unit-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }}
    .unit-id-badge {{
      background: #0284c7;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 10px;
      border-radius: 6px;
    }}
    .unit-pillar-badge {{
      background: #059669;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .unit-title {{
      font-size: 20px;
      font-weight: 800;
      color: #fff;
    }}
    .unit-subtitle {{
      font-size: 15px;
      color: #38bdf8;
      margin-bottom: 16px;
      font-style: italic;
    }}
    .unit-section {{
      margin-bottom: 14px;
    }}
    .unit-section-title {{
      font-size: 13px;
      font-weight: 800;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 6px;
    }}
    .unit-story {{
      font-size: 15px;
      line-height: 1.6;
    }}
    .unit-key-idea {{
      background: #0c4a6e;
      border-left: 4px solid #38bdf8;
      padding: 12px 16px;
      border-radius: 0 8px 8px 0;
      margin: 16px 0;
      font-size: 15px;
      color: #e0f2fe;
    }}
    .unit-svg-container {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
      text-align: center;
    }}
    .how-it-works-list {{
      margin-left: 20px;
      font-size: 15px;
      line-height: 1.7;
    }}
    .unit-worked-example {{
      background: #0f172a;
      border: 1px solid #334155;
      padding: 14px 16px;
      border-radius: 8px;
      margin: 16px 0;
      font-size: 15px;
    }}
    .unit-notes-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin: 14px 0;
    }}
    @media (max-width: 768px) {{
      .unit-notes-row {{ grid-template-columns: 1fr; }}
    }}
    .unit-watch-out {{
      background: #4c0519;
      border-left: 3px solid #f43f5e;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      color: #fecdd3;
    }}
    .unit-quick-check {{
      background: #064e3b;
      border-left: 3px solid #10b981;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      color: #a7f3d0;
    }}
    .unit-targets-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid var(--border);
      flex-wrap: wrap;
    }}
    .targets-btn-group {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .target-link-btn {{
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
    }}
    .target-link-btn:hover {{
      background: #1e293b;
      border-color: #38bdf8;
    }}

    /* Tab 3: Recall & Atlas Styling */
    .atlas-table-box {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 28px;
      overflow-x: auto;
    }}
    .atlas-title {{
      font-size: 18px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 6px;
    }}
    .atlas-desc {{
      font-size: 14px;
      color: #94a3b8;
      margin-bottom: 16px;
    }}
    .atlas-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    .atlas-table th {{
      background: #0f172a;
      color: #94a3b8;
      text-align: left;
      padding: 12px;
      border-bottom: 2px solid var(--border);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .atlas-table td {{
      padding: 12px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
      line-height: 1.5;
    }}
    .atlas-link-btn {{
      background: #0f172a;
      border: 1px solid #475569;
      color: #38bdf8;
      font-weight: 800;
      font-size: 12px;
      padding: 6px 10px;
      border-radius: 4px;
      cursor: pointer;
      min-height: 48px;
      display: inline-flex;
      align-items: center;
    }}
    .atlas-link-btn:hover {{
      border-color: #38bdf8;
      background: #1e293b;
    }}
    .anti-text {{
      color: #f87171;
    }}

    .recon-card, .probe-card, .ccm-card {{
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .recon-header, .probe-header, .ccm-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .recon-id-badge, .probe-id-badge, .ccm-id-badge {{
      background: #7c3aed;
      color: #fff;
      font-weight: 800;
      font-size: 12px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .recon-comp-badge, .probe-comp-badge {{
      background: #0284c7;
      color: #fff;
      font-weight: 800;
      font-size: 12px;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .recon-title, .ccm-title {{
      font-size: 17px;
      font-weight: 800;
      color: #fff;
    }}
    .recon-section {{
      margin-bottom: 12px;
    }}
    .recon-section-title {{
      font-size: 13px;
      font-weight: 800;
      color: #94a3b8;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .recon-std-text {{
      font-size: 14px;
      color: #cbd5e1;
    }}
    .recon-pivot-box {{
      background: #0f172a;
      border-left: 3px solid #a855f7;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      line-height: 1.6;
    }}
    .recon-limits-list {{
      margin-left: 20px;
      font-size: 14px;
      line-height: 1.6;
    }}

    .probe-trap {{
      background: #4c0519;
      border-left: 3px solid #f43f5e;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      color: #fecdd3;
      margin-bottom: 8px;
    }}
    .probe-challenge {{
      background: #1e1b4b;
      border-left: 3px solid #818cf8;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      color: #c7d2fe;
      margin-bottom: 8px;
    }}
    .probe-resolution {{
      background: #064e3b;
      border-left: 3px solid #10b981;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      color: #a7f3d0;
    }}

    .ccm-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }}
    @media (max-width: 768px) {{
      .ccm-grid {{ grid-template-columns: 1fr; }}
    }}
    .ccm-misc {{
      background: #4c0519;
      border: 1px solid #e11d48;
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 14px;
      color: #fecdd3;
    }}
    .ccm-truth {{
      background: #064e3b;
      border: 1px solid #059669;
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 14px;
      color: #a7f3d0;
    }}
    .ccm-exp {{
      background: #0f172a;
      border: 1px solid #334155;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 14px;
      color: #cbd5e1;
    }}

    /* Global touch target floor */
    button, input, select, summary {{
      touch-action: manipulation;
    }}
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Non-occluding Relative Header -->
    <header class="app-header">
      <div class="header-top">
        <div class="header-title-box">
          <h1>Grade 9 Physics: Vectors &amp; Coordinate Frames</h1>
          <p>Tri-Modal Master Suite: Core 1A Textbook &bull; Core 1B Reconstruction &bull; Core 2 Practice Cards</p>
        </div>
        <div class="tri-tabs-row">
          <button class="tri-tab-btn tab-c2 active" onclick="showTab('core2')">
            Core 2 Practice (25 Cards)
          </button>
          <button class="tri-tab-btn tab-c1a" onclick="showTab('core1a')">
            Core 1A Textbook (11 Units)
          </button>
          <button class="tri-tab-btn tab-c1b" onclick="showTab('core1b')">
            Core 1B Recall &amp; Atlas
          </button>
        </div>
      </div>
    </header>

    <main class="main-wrap">
      <!-- TAB 1: CORE 2 PRACTICE CARDS -->
      <section id="tab-core2" class="tab-section active">
        <div class="filter-pills-row">
          <button class="filter-pill active" onclick="filterCards('ALL')">All (25)</button>
          <button class="filter-pill" onclick="filterCards('D1')">D1 Foundation (4)</button>
          <button class="filter-pill" onclick="filterCards('D2')">D2 Proficient (8)</button>
          <button class="filter-pill" onclick="filterCards('D3')">D3 Advanced (8)</button>
          <button class="filter-pill" onclick="filterCards('D4')">D4 Olympiad Challenge (5)</button>
        </div>
        <div class="cards-list">
          {practice_cards_html}
        </div>
      </section>

      <!-- TAB 2: CORE 1A LEARNER TEXTBOOK -->
      <section id="tab-core1a" class="tab-section">
        <div class="textbook-intro-box" style="background:#1e293b; border:1px solid #334155; border-radius:12px; padding:20px; margin-bottom:24px;">
          <h2 style="font-size:20px; font-weight:800; color:#fff; margin-bottom:8px;">Core 1A Foundation Ontology: Vectors &amp; Coordinate Frames</h2>
          <p style="font-size:15px; color:#94a3b8;">11 Comprehensive Learner Chapters. Build vector reasoning as a reusable physical system before applying mathematical equations: physical meaning &rarr; diagram &rarr; components &rarr; interpretation &rarr; check.</p>
        </div>
        <div class="textbook-units-list">
          {textbook_units_html}
        </div>
      </section>

      <!-- TAB 3: CORE 1B RECALL & RECONSTRUCTION -->
      <section id="tab-core1b" class="tab-section">
        <!-- First-Move Atlas Table -->
        <div class="atlas-table-box">
          <div class="atlas-title">Vector First-Move Atlas</div>
          <div class="atlas-desc">Answer-free reference for choosing the correct scientific representation immediately upon encountering problem cues.</div>
          <table class="atlas-table">
            <thead>
              <tr>
                <th>Comp</th>
                <th>When you see (Cue)</th>
                <th>Draw / mark first (Representation)</th>
                <th>First Executable Move</th>
                <th>Anti-Pattern to Avoid</th>
              </tr>
            </thead>
            <tbody>
              {atlas_rows_html}
            </tbody>
          </table>
        </div>

        <!-- Phenomenological Reconstruction Cycles -->
        <div class="section-title-box" style="margin:24px 0 12px 0;">
          <h2 style="font-size:20px; font-weight:800; color:#fff;">Phenomenological Reconstruction Cycles</h2>
          <p style="font-size:14px; color:#94a3b8;">Transforming mechanical formulas into intuitive geometric and observer-centered physical invariants.</p>
        </div>
        <div class="recons-list">
          {recons_html}
        </div>

        <!-- Cognitive Dissonance Probes -->
        <div class="section-title-box" style="margin:28px 0 12px 0;">
          <h2 style="font-size:20px; font-weight:800; color:#fff;">Cognitive Dissonance Probes</h2>
          <p style="font-size:14px; color:#94a3b8;">Socratic challenges targeting ingrained intuitive misconceptions.</p>
        </div>
        <div class="probes-list">
          {probes_html}
        </div>

        <!-- Cognitive Conflict Matrix -->
        <div class="section-title-box" style="margin:28px 0 12px 0;">
          <h2 style="font-size:20px; font-weight:800; color:#fff;">Cognitive Conflict Matrix</h2>
          <p style="font-size:14px; color:#94a3b8;">Contrasting intuitive student beliefs with decisive Newtonian experiments.</p>
        </div>
        <div class="ccm-list">
          {ccm_html}
        </div>
      </section>
    </main>
  </div>

  <script>
    // Tab switching
    function showTab(tabId) {{
      document.querySelectorAll('.tab-section').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tri-tab-btn').forEach(el => el.classList.remove('active'));

      const targetSection = document.getElementById('tab-' + tabId);
      if (targetSection) targetSection.classList.add('active');

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

    // Filter cards by difficulty band
    function filterCards(band) {{
      document.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');

      document.querySelectorAll('.question-card').forEach(card => {{
        if (band === 'ALL' || card.getAttribute('data-band') === band) {{
          card.style.display = 'block';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}
  </script>
</body>
</html>
    """

    # Write raw HTML for prerender engine
    raw_path = REPO_ROOT / "scratch/_raw_vectors_tri_modal.html"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[OK] Wrote raw HTML template: {raw_path} ({len(full_html)} bytes)")

    # Target destinations
    output_path = REPO_ROOT / "standalone/practice/core2-physics-vectors-grade9-master.html"
    public_path = REPO_ROOT / "public/standalone/practice/core2-physics-vectors-grade9-master.html"
    artifact_path = Path(r"C:\Users\reall\.gemini\antigravity\brain\40014ef9-8d66-475e-aff1-d6e53797ebbd\physics_vectors_master_app.html")

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
    print("VECTORS MASTER TABLET APP COMPILATION COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    compile_tri_modal_vectors()
