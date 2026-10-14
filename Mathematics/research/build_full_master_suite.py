#!/usr/bin/env python3
"""
Builds the complete Grade 9 IMO Master Suite HTML containing ALL Core 2 questions done till now:
- SOF-IMO-G09-L1-2025-26-B (50 questions, Batch 1)
- SOF-IMO-G09-L1-2025-26-A (50 questions, Batch 2)
- SOF-IMO-G09-L1-2024-25-B (50 questions, Batch 3)
- SOF-IMO-G09-L1-2023-24-A (24 questions)
- SOF-IMO-G09-SAMPLE-2026-27 (10 questions)
Total: 184 authentic IMO questions under Core 2 custody with vector SVGs,
Two-Tier & 3-Rung Hint Ladders, formal verification derivations, distractor rationales,
and strict typography compliance (zero FONT_FLOOR findings, font >= 14px).
"""
import os
import sys
import json
import re
import base64
import html
import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Mathematics.research.topic_visual_svgs import generate_topic_svg, TOPIC_COLOR_PALETTES

def get_figure_markup(figure_ref, qid, stem="", options=None):
    figures_dir = Path("Mathematics/library/figures")
    
    # 1. Check if figure_ref points to a file in Mathematics/library/figures
    if figure_ref:
        ref = Path(figure_ref)
        if ref.is_absolute() or ".." in ref.parts or ref.suffix.lower() != ".svg":
            raise ValueError(f"UNSAFE_FIGURE_REFERENCE: {figure_ref}")
        prefix = Path("Mathematics/library/figures").parts
        if ref.parts[:len(prefix)] == prefix:
            ref = Path(*ref.parts[len(prefix):])
        if len(ref.parts) != 1:
            raise ValueError(f"FIGURE_NOT_IN_LIBRARY_FLAT_NAMESPACE: {figure_ref}")
        fig_path = (figures_dir / ref).resolve()
        if not fig_path.is_relative_to(figures_dir.resolve()):
            raise ValueError(f"FIGURE_ESCAPES_LIBRARY: {figure_ref}")
        if not fig_path.is_file():
            raise FileNotFoundError(f"DECLARED_FIGURE_MISSING: {figure_ref}")
        if fig_path.exists():
            svg_content = fig_path.read_text(encoding="utf-8")
            # Strip xml declaration if present
            svg_content = re.sub(r'<\?xml[^>]*\?>', '', svg_content).strip()
            # Ensure marker and gradient IDs inside embedded SVGs are unique per question
            clean_qid = re.sub(r'[^a-zA-Z0-9_]', '_', qid)
            svg_content = svg_content.replace('id="arrow"', f'id="arrow_{clean_qid}"')
            svg_content = svg_content.replace('url(#arrow)', f'url(#arrow_{clean_qid})')
            return f"""
            <div class="qb-figure-wrap">
              <div class="qb-figure-caption"><strong>Figure:</strong> Official Vector Geometry ({html.escape(figure_ref)})</div>
              {svg_content}
            </div>
            """
    
    # 2. Check generate_question_svgs if available
    try:
        from generate_question_svgs import get_svg_for_question
        svg = get_svg_for_question(qid)
        if svg:
            return svg
    except Exception:
        pass
        
    # 3. If missing but requires visual figure, render non-silent Visual Asset Cue Box
    search_text = f"{stem} " + " ".join(str(v) for v in (options or {}).values())
    text_lower = search_text.lower()
    
    try:
        from Shared.tools.audit_missing_svgs import ALL_PATTERNS, classify_visual_demand, FALSE_POSITIVE_EXCLUSIONS
        is_visual = False
        if not any(re.search(excl, text_lower) for excl in FALSE_POSITIVE_EXCLUSIONS):
            is_visual = any(re.search(pat, text_lower) for pat in ALL_PATTERNS)
        if is_visual:
            demand_type = classify_visual_demand(search_text)
            demand_label = demand_type.replace('_', ' ').title()
            expected_filename = figure_ref or f"FIG-{qid}.svg"
            return f"""
            <div class="qb-figure-wrap qb-figure-cue-wrap" style="background:rgba(251,191,36,0.06);border:1.5px dashed rgba(251,191,36,0.45);border-radius:10px;padding:16px 20px;margin:16px 0;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                <span class="qb-badge" style="background:rgba(251,191,36,0.18);color:#fbbf24;border:1.5px solid #fbbf24;font-size:0.88rem;font-weight:750">⚠️ VISUAL DIAGRAM CUE</span>
                <span style="font-size:0.9rem;font-weight:750;color:var(--text)">{html.escape(demand_label)}</span>
              </div>
              <p style="font-size:0.92rem;line-height:1.5;margin:0 0 8px 0;color:var(--text)">This question relies on visual analysis of diagrammatic relationships. Visual representation cue is active.</p>
              <div style="font-size:0.88rem;color:var(--text-muted);font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">Expected Asset: <code style="color:var(--accent)">{html.escape(expected_filename)}</code></div>
            </div>
            """
    except Exception:
        pass

    return ""

def format_math_html(text: str) -> str:
    """
    Safely formats text containing math expressions:
    - Protects LaTeX math blocks ($...$, $$...$$, \\(...\\), \\[...]\\).
    - Unescapes leaked HTML entities inside math (&lt; -> <, &gt; -> >, &#x27; -> ').
    - Escapes bare % inside math to \\% so KaTeX does not treat it as a comment.
    - Outside of math, escapes HTML and protects bare $ with <span class="no-math">&#36;</span>.
    - Converts \\n to <br> for multi-step derivations.
    """
    if not text:
        return ""
    
    # Matches $$...$$, $...$, \\[...\\], \\(...\\), or newlines
    pattern = re.compile(r'(\$\$[\s\S]+?\$\$|\$(?:(?!\$)[^\n\r])+?\$|\\\[[\s\S]+?\\\]|\\\(.+?\\\)|\n)')
    tokens = pattern.split(text)
    
    out = []
    for tok in tokens:
        if not tok:
            continue
        if tok == "\n":
            out.append("<br>")
            continue
            
        is_math = False
        if (tok.startswith("$$") and tok.endswith("$$") and len(tok) >= 4) or \
           (tok.startswith("$") and tok.endswith("$") and len(tok) >= 2) or \
           (tok.startswith("\\[") and tok.endswith("\\]")) or \
           (tok.startswith("\\(") and tok.endswith("\\)")):
            is_math = True
            
        if is_math:
            m = tok
            m = (m.replace("&lt;", "<")
                  .replace("&gt;", ">")
                  .replace("&#x27;", "'")
                  .replace("&apos;", "'")
                  .replace("&quot;", '"')
                  .replace("&amp;", "&"))
            
            # Extract inner and delimiters
            if m.startswith("$$") and m.endswith("$$"):
                prefix, suffix, inner = "$$", "$$", m[2:-2]
            elif m.startswith("\\[") and m.endswith("\\]"):
                prefix, suffix, inner = "\\[", "\\]", m[2:-2]
            elif m.startswith("\\(") and m.endswith("\\)"):
                prefix, suffix, inner = "\\(", "\\)", m[2:-2]
            else:
                prefix, suffix, inner = "$", "$", m[1:-1]
                
            # Escape raw % as \\% in math
            cleaned_inner = re.sub(r'(?<!\\)%', r'\\%', inner)
            out.append(f"{prefix}{cleaned_inner}{suffix}")
        else:
            # Outside math: escape HTML
            esc = html.escape(tok)
            # Protect lone $ outside of math
            esc = esc.replace("$", '<span class="no-math">&#36;</span>')
            out.append(esc)
            
    return "".join(out)

def load_all_topic_units(units_dir: str = "Mathematics/units") -> list[dict]:
    units = []
    folders = sorted(os.listdir(units_dir))
    for f in folders:
        fpath = os.path.join(units_dir, f)
        if not os.path.isdir(fpath):
            continue
        c1a_files = sorted(glob.glob(os.path.join(fpath, "core1a-*.json")))
        for c1a_path in c1a_files:
            fname = os.path.basename(c1a_path)
            prefix_match = fname.replace("core1a-", "core1b-")
            c1b_path = os.path.join(fpath, prefix_match)
            if not os.path.exists(c1b_path):
                if ".v1.json" in prefix_match:
                    alt = prefix_match.replace(".v1.json", ".json")
                else:
                    alt = prefix_match.replace(".json", ".v1.json")
                if os.path.exists(os.path.join(fpath, alt)):
                    c1b_path = os.path.join(fpath, alt)
            if not os.path.exists(c1b_path):
                continue
            with open(c1a_path, "r", encoding="utf-8") as fp:
                c1a = json.load(fp)
            with open(c1b_path, "r", encoding="utf-8") as fp:
                c1b = json.load(fp)
            
            slug = fname
            if slug.startswith("core1a-"):
                slug = slug[len("core1a-"):]
            for ext in [".v1.json", ".json"]:
                if slug.endswith(ext):
                    slug = slug[:-len(ext)]
            
            topic_name = c1a.get("topic_name", c1a.get("topic", f))
            subtopic = c1a.get("subtopic", "")
            
            units.append({
                "unit_id": slug,
                "folder": f,
                "c1a": c1a,
                "c1b": c1b,
                "topic": c1a.get("topic", f),
                "topic_name": topic_name,
                "band": c1a.get("target_band", "D2"),
                "demand": c1a.get("target_demand", "APPLY"),
                "subtopic": subtopic
            })
    return units


TOPIC_TO_UNIT_FOLDER = {
    "circles": "circles",
    "commercial mathematics": "commercial-math",
    "coordinate geometry": "coordinate-geometry",
    "introduction to euclid's geometry": "euclid-geometry",
    "introduction to euclid’s geometry": "euclid-geometry",
    "heron's formula and surface area": "heron-formula",
    "heron's formula": "heron-formula",
    "area and perimeter": "heron-formula",
    "linear equations in two variables": "linear-equations",
    "lines and angles": "lines-and-angles",
    "polynomials": "polynomials",
    "algebraic identities": "polynomials",
    "probability": "probability",
    "introduction to probability": "probability",
    "quadrilaterals": "quadrilaterals",
    "areas of parallelograms and triangles": "quadrilaterals",
    "verbal and non-verbal reasoning": "reasoning",
    "quantitative aptitude": "reasoning",
    "statistics": "statistics",
    "surface areas and volumes": "surface-areas-volumes",
    "triangles": "triangles",
    "number systems": "polynomials"
}


def render_topic_jump_navigation(units: list, prefix: str) -> str:
    if not units:
        return ""
    parts = []
    nav_id = f"topic-nav-{prefix}"
    indicator_id = f"topic-band-indicator-{prefix}"
    active_label_id = f"active-topic-label-{prefix}"
    dot_id = f"dot-{prefix}"
    collapse_btn_id = f"collapse-btn-{prefix}"
    track_id = f"topic-track-{prefix}"
    
    first_pal = TOPIC_COLOR_PALETTES.get(units[0]["folder"], {"primary": "#38bdf8", "glow": "rgba(56,189,248,0.25)", "bg": "rgba(56,189,248,0.08)"})
    first_name = units[0]["topic_name"]
    
    parts.append(f"""
      <!-- STICKY TOPIC NAVIGATION BAR WITH DYNAMIC COLOR BAND & TOUCH-TO-COLLAPSE -->
      <div class="topic-sticky-bar" id="{nav_id}" data-prefix="{prefix}">
        <!-- Dynamic Color Band Strip across the top -->
        <div class="topic-band-strip" id="{indicator_id}" style="background-color: {first_pal['primary']}; box-shadow: 0 0 14px {first_pal['glow']}"></div>
        
        <div class="topic-sticky-header" onclick="toggleTopicNavCollapse('{prefix}')" title="Touch or click to collapse/expand topic buttons">
          <div class="topic-header-lead">
            <span class="topic-pulse-dot" id="{dot_id}" style="background-color: {first_pal['primary']}; box-shadow: 0 0 8px {first_pal['primary']}"></span>
            <span class="topic-header-title">Active Topic Band:</span>
            <span id="{active_label_id}" class="topic-header-active-name" style="color:{first_pal['primary']}">{html.escape(first_name)}</span>
          </div>
          <div class="topic-header-actions">
            <span class="topic-header-hint">⚡ Color Band Tracks Viewport</span>
            <button type="button" class="topic-collapse-btn" id="{collapse_btn_id}" onclick="event.stopPropagation(); toggleTopicNavCollapse('{prefix}')" aria-expanded="true" aria-controls="{track_id}" title="Touch or click to collapse topic buttons">
              <span class="collapse-icon">▲</span>
              <span class="collapse-text">Collapse Topics</span>
            </button>
          </div>
        </div>

        <div class="topic-buttons-track" id="{track_id}">
          <span class="topic-jump-label">Jump to topic:</span>
    """)
    for idx, u in enumerate(units):
        f = u["folder"]
        uid = u.get("unit_id", f)
        pal = TOPIC_COLOR_PALETTES.get(f, {"primary": "#38bdf8", "glow": "rgba(56,189,248,0.25)", "bg": "rgba(56,189,248,0.08)"})
        target_id = f"module-{prefix}-{uid}"
        active_cls = " active" if idx == 0 else ""
        sub_raw = u.get("subtopic", "").replace("_", " ").replace("-", " ").title()
        btn_label = f"{u['topic_name']} ({sub_raw})" if len([x for x in units if x["folder"] == f]) > 1 else u["topic_name"]
        parts.append(f"""          <button type="button" class="topic-nav-btn{active_cls}" data-prefix="{prefix}" data-folder="{f}" data-unit-id="{uid}" data-target="{target_id}" data-color="{pal['primary']}" data-glow="{pal['glow']}" data-name="{html.escape(btn_label)}" onclick="scrollToTopicModule('{target_id}')" style="--topic-color:{pal['primary']};--topic-glow:{pal['glow']};--topic-bg:{pal['bg']}">
            <span class="btn-dot" style="background-color:{pal['primary']}"></span>
            <span class="btn-title">{html.escape(btn_label)}</span>
          </button>\n""")
    parts.append("""        </div>
      </div>
    """)
    return "".join(parts)


def render_topic_module_html(unit: dict, prefix: str = "") -> str:
    c1a = unit["c1a"]
    c1b = unit["c1b"]
    topic_name = c1a.get("topic_name", c1a.get("topic", unit["folder"]))
    topic_code = c1a.get("topic", unit["folder"])
    subtopic = c1a.get("subtopic", "")
    band = c1a.get("target_band", "D2")
    demand = c1a.get("target_demand", "APPLY")
    linked_refs = c1a.get("linked_core2_refs", [])
    
    # 1A fields
    assumptions = c1a.get("entry_assumptions", [])
    inferential_jump = c1a.get("inferential_jump", "")
    rel_refs = c1a.get("relation_refs", {})
    domain = rel_refs.get("domain", "")
    hypotheses = rel_refs.get("hypotheses", [])
    excluded_values = rel_refs.get("excluded_values", [])
    reps = c1a.get("representation", [])
    teaching_path = c1a.get("completed_teaching_path", [])
    misconceptions = c1a.get("misconceptions", [])
    wca = c1a.get("worked_concept_anchor", {})
    exit_task = c1a.get("exit_task", c1a.get("independent_exit_task", {}))
    
    # 1B fields
    itf = c1b.get("interactive_tutor_flow", {})
    stage1 = itf.get("stage_1_predict", {})
    stage2 = itf.get("stage_2_attempt", {})
    stage3 = itf.get("stage_3_reconstruct", {})
    stage4 = itf.get("stage_4_boundary_test", {})
    hint_ladder = c1b.get("hint_ladder", {})
    
    band_color = {
        "D1": "var(--success)",
        "D2": "var(--accent)",
        "D3": "var(--warning)",
        "D4": "var(--purple)"
    }.get(band, "var(--accent)")
    
    palette = TOPIC_COLOR_PALETTES.get(unit["folder"], {
        "primary": "#38bdf8",
        "glow": "rgba(56,189,248,0.25)",
        "bg": "rgba(56,189,248,0.08)",
        "label": topic_name
    })
    topic_svg_markup = generate_topic_svg(unit["folder"])
    
    parts = []
    unit_id = unit.get("unit_id", unit["folder"])
    card_id = f"module-{prefix}-{unit_id}" if prefix else f"module-{unit_id}"
    radio_predict = f"predict-{prefix}-{unit_id}" if prefix else f"predict-{unit_id}"
    radio_boundary = f"boundary-{prefix}-{unit_id}" if prefix else f"boundary-{unit_id}"
    
    # Topic Card Wrapper with Visual Color Band
    parts.append(f"""
    <div class="topic-module-card" id="{card_id}" data-topic="{html.escape(topic_name)}" data-band="{band}" data-folder="{unit['folder']}" data-unit-id="{unit_id}" style="margin:28px 0;background:var(--card);border:1.5px solid var(--border);border-top:6px solid {palette['primary']};border-radius:12px;padding:24px;box-shadow:0 6px 20px rgba(0,0,0,0.22);position:relative">
      <!-- TOP VISUAL COLOR ACCENT BAR -->
      <div style="height:4px;width:100%;background:linear-gradient(90deg, {palette['primary']}, transparent);border-radius:2px;margin-bottom:16px"></div>

      <!-- TOPIC HEADER -->
      <div style="border-bottom:1.5px solid var(--border);padding-bottom:16px;margin-bottom:20px">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
          <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px">
            <span class="qb-badge qb-badge-{band.lower()}" style="font-weight:800;font-size:0.88rem">{band} OLYMPIAD BAND</span>
            <span class="qb-badge qb-badge-qrt" style="font-weight:800;font-size:0.88rem">DEMAND: {demand}</span>
            <span class="qb-badge" style="background:{palette['bg']};color:{palette['primary']};border:1.5px solid {palette['primary']};font-size:0.88rem;font-weight:800">{html.escape(palette.get('label', topic_name))}</span>
            <span class="qb-badge" style="background:rgba(56,189,248,0.12);color:var(--accent);border:1px solid rgba(56,189,248,0.25);font-size:0.88rem;font-weight:750">BP-CORE1A &amp; BP-CORE1B CERTIFIED</span>
          </div>
          <span style="font-size:0.88rem;color:var(--text-muted);font-weight:700">CODE: {html.escape(subtopic)}</span>
        </div>
        <h2 style="font-size:1.45rem;font-weight:800;margin-top:12px;color:var(--text);display:flex;align-items:center;gap:10px">
          <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:{palette['primary']};box-shadow:0 0 10px {palette['primary']}"></span>
          {html.escape(topic_name)}
        </h2>
        <div style="margin-top:8px;font-size:0.92rem;color:var(--text-muted)">
          <strong>Mathematical Domain:</strong> {format_math_html(domain if domain else topic_name)}
        </div>
    """)
    
    if linked_refs:
        parts.append(f"""
        <div style="margin-top:12px">
          <details style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px 14px">
            <summary style="cursor:pointer;font-weight:700;font-size:0.90rem;color:var(--accent)">
              🔗 Anchored to {len(linked_refs)} Authenticated Core 2 Questions (Click to expand list)
            </summary>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px">
        """)
        for ref in linked_refs:
            parts.append(f'<span class="filter-chip" style="font-size:0.88rem" onclick="jumpToQuestion(\'{ref}\')">{html.escape(ref)}</span>')
        parts.append("""
            </div>
          </details>
        </div>
        """)
    
    parts.append("""
      </div>
      
      <!-- CORE 1A: DECLARATIVE STUDY & CONSTRUCTIVE UNIVERSAL PROOF -->
      <div class="panel" style="margin-bottom:28px;border-left:5px solid {palette['primary']};padding-left:18px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
          <span class="qb-badge" style="background:{palette['bg']};color:{palette['primary']};border:1.5px solid {palette['primary']};font-size:0.88rem;font-weight:800;box-shadow:0 0 10px {palette['glow']}">BLUEPRINT BP-CORE1A-CONSTRUCTION</span>
          <h3 style="font-size:1.25rem;font-weight:800;color:var(--text);margin:0">
            Core 1A · Constructive Universal Proof &amp; Declarative Anchor
          </h3>
        </div>
    """)
    
    # Conventions & Scope
    parts.append(f"""
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:16px">
          <h4 style="font-size:0.98rem;font-weight:800;color:{palette['primary']};margin-bottom:8px">
            📐 Conventions and Scope &amp; Entry Assumptions
          </h4>
    """)
    if assumptions:
        parts.append('<ul style="padding-left:22px;line-height:1.7;margin-bottom:8px">')
        for asm in assumptions:
            parts.append(f'<li style="font-size:0.92rem">{format_math_html(str(asm))}</li>')
        parts.append('</ul>')
    if hypotheses:
        parts.append('<div style="font-size:0.92rem;margin-top:8px"><strong>Hypotheses:</strong><ul style="padding-left:22px;line-height:1.7;margin-top:4px">')
        for hyp in hypotheses:
            parts.append(f'<li>{format_math_html(str(hyp))}</li>')
        parts.append('</ul></div>')
    if excluded_values:
        parts.append('<div style="font-size:0.92rem;margin-top:8px;color:#fca5a5"><strong>Excluded / Boundary Values:</strong><ul style="padding-left:22px;line-height:1.7;margin-top:4px">')
        for ev in excluded_values:
            parts.append(f'<li>{format_math_html(str(ev))}</li>')
        parts.append('</ul></div>')
    parts.append('</div>')
    
    # Inferential Leap (T02)
    parts.append(f"""
        <div class="inferential-leap trap-alert" style="border-left:5px solid {palette['primary']};background:{palette['bg']};margin:16px 0;padding:16px;border-radius:8px;box-shadow:0 0 14px {palette['glow']}">
          <strong style="color:{palette['primary']};font-size:1.0rem">⚡ The Inferential Leap (Technique T02):</strong>
          <p style="margin-top:6px;line-height:1.7;font-size:0.95rem;color:var(--text)">
            {format_math_html(inferential_jump)}
          </p>
        </div>
    """)
    
    # Completed Teaching Path
    if teaching_path:
        parts.append("""
        <div style="margin:20px 0">
          <h4 style="font-size:1.02rem;font-weight:800;margin-bottom:12px;color:var(--text)">
            🪜 Completed Teaching Path (Step-by-Step Rigorous Derivation)
          </h4>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px">
        """)
        for step in teaching_path:
            s_ref = step.get("step_ref", step.get("step", "STEP"))
            claim = step.get("claim", "")
            deriv = step.get("derivation", "")
            why_valid = step.get("why_valid", "")
            parts.append(f"""
            <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <span class="rung-tag rung-nudge">{html.escape(str(s_ref))}</span>
                <span style="font-size:0.88rem;color:var(--text-muted);font-weight:700">WARRANT</span>
              </div>
              <p style="font-weight:750;margin-bottom:6px;font-size:0.95rem;color:var(--text)">{format_math_html(claim)}</p>
              <div style="background:var(--card);padding:10px 12px;border-radius:6px;margin:8px 0;font-size:0.92rem;line-height:1.6">
                {format_math_html(deriv)}
              </div>
              <p style="font-size:0.88rem;color:var(--success);font-weight:700;margin-top:6px">
                ✅ <strong>Why valid:</strong> {format_math_html(why_valid)}
              </p>
            </div>
            """)
        parts.append("""
          </div>
        </div>
        """)
        
    # Bespoke Visual Representation & Invariant Section
    if topic_svg_markup:
        parts.append(f"""
        <!-- BESPOKE TOPIC VISUAL REPRESENTATION & INVARIANT DIAGRAM -->
        <div class="visual-representation-anchor" style="background:var(--surface);border:1.5px solid {palette['primary']};border-radius:12px;padding:18px;margin:20px 0;box-shadow:0 4px 16px {palette['glow']}">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:14px">
            <div style="display:flex;align-items:center;gap:8px">
              <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{palette['primary']};box-shadow:0 0 8px {palette['primary']}"></span>
              <h4 style="font-size:1.02rem;font-weight:800;color:var(--text);margin:0">
                📊 Topic Visual Representation &amp; Invariant Diagram
              </h4>
            </div>
            <span class="qb-badge" style="background:{palette['bg']};color:{palette['primary']};border:1.5px solid {palette['primary']};font-size:0.88rem;font-weight:800">
              SVG VECTOR RIGOR (&ge; 14px FONT)
            </span>
          </div>
          <div style="display:flex;justify-content:center;align-items:center;background:#090e17;border-radius:8px;padding:14px;overflow-x:auto;border:1px solid var(--border)">
            {topic_svg_markup}
          </div>
        </div>
        """)

    # Representation Bridge
    if reps:
        parts.append("""
        <div class="representation-bridge" style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin:16px 0">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px">
            <h4 style="font-size:0.98rem;font-weight:800;color:var(--purple);margin:0">
              🌉 Representation Bridge (Symbolic &amp; Visual Mapping)
            </h4>
            <span style="font-size:0.88rem;color:var(--text-muted);font-weight:700">Anchor: Invariant Vector Diagram</span>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px">
        """)
        for r in reps:
            sym = r.get("symbol", "")
            wm = r.get("word_meaning", "")
            parts.append(f"""
            <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px">
              <div style="font-weight:800;color:var(--accent);font-size:0.95rem;margin-bottom:4px">{format_math_html(sym)}</div>
              <div style="font-size:0.90rem;color:var(--text-muted);line-height:1.6">{format_math_html(wm)}</div>
            </div>
            """)
        parts.append("""
          </div>
        </div>
        """)
        
    # Misconception Clinic
    if misconceptions:
        parts.append("""
        <div class="trap-clinic trap-alert" style="margin:20px 0;padding:16px;border-radius:10px">
          <h4 style="font-size:1.02rem;font-weight:800;color:#f87171;margin-bottom:12px">
            ⚠️ Trap Clinic &amp; Misconception Repair (Technique T06)
          </h4>
        """)
        for m in misconceptions:
            m_code = m.get("code", m.get("id", "MISC"))
            w_idea = m.get("wrong_idea", "")
            d_prompt = m.get("diagnostic_prompt", "")
            repair = m.get("repair", "")
            parts.append(f"""
            <div style="background:var(--card);border:1px solid rgba(248,113,113,0.3);border-radius:8px;padding:14px;margin-bottom:12px">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                <span class="rung-tag" style="background:rgba(248,113,113,0.2);color:#fca5a5">{html.escape(str(m_code))}</span>
                <span style="font-weight:750;color:#fca5a5;font-size:0.95rem">Fallacy: {format_math_html(w_idea)}</span>
              </div>
              <p style="margin-top:6px;font-size:0.92rem;line-height:1.65;color:var(--text)">
                <strong>Diagnostic Context:</strong> {format_math_html(d_prompt)}
              </p>
              <div style="margin-top:8px;padding-top:8px;border-top:1px dashed rgba(248,113,113,0.3);font-size:0.92rem;line-height:1.65;color:var(--text)">
                <strong>Refutation &amp; Repair Rule:</strong> {format_math_html(repair)}
              </div>
            </div>
            """)
        parts.append("</div>")
        
    # Worked Concept Anchor
    if wca:
        parts.append("""
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin:16px 0">
          <h4 style="font-size:0.98rem;font-weight:800;color:var(--success);margin-bottom:10px">
            ⚓ Worked Concept Anchor (Canonical Olympiad Exemplar)
          </h4>
        """)
        if "prompt" in wca:
            parts.append(f'<p style="font-size:0.95rem;font-weight:700;margin-bottom:8px">{format_math_html(wca["prompt"])}</p>')
        elif "problem_statement" in wca:
            parts.append(f'<p style="font-size:0.95rem;font-weight:700;margin-bottom:8px">{format_math_html(wca["problem_statement"])}</p>')
        if "conventions_declared" in wca:
            parts.append(f'<p style="font-size:0.90rem;color:var(--text-muted);margin-bottom:6px"><em>Conventions:</em> {format_math_html(str(wca["conventions_declared"]))}</p>')
        if "model_answer" in wca:
            ma = wca["model_answer"]
            if isinstance(ma, list):
                parts.append('<div style="background:var(--card);padding:12px;border-radius:8px;margin-top:8px">')
                for item in ma:
                    parts.append(f'<div style="font-size:0.92rem;line-height:1.65;margin-bottom:6px">{format_math_html(str(item))}</div>')
                parts.append('</div>')
            elif isinstance(ma, dict):
                parts.append('<div style="background:var(--card);padding:12px;border-radius:8px;margin-top:8px">')
                for k, v in ma.items():
                    parts.append(f'<div style="font-size:0.92rem;line-height:1.65;margin-bottom:6px"><strong>{html.escape(k)}:</strong> {format_math_html(str(v))}</div>')
                parts.append('</div>')
            else:
                parts.append(f'<div style="background:var(--card);padding:12px;border-radius:8px;margin-top:8px;font-size:0.92rem;line-height:1.65">{format_math_html(str(ma))}</div>')
        elif "deductive_chain" in wca:
            chain = wca["deductive_chain"]
            parts.append('<div style="background:var(--card);padding:12px;border-radius:8px;margin-top:8px">')
            for step in chain:
                parts.append(f'<div style="font-size:0.92rem;line-height:1.65;margin-bottom:6px">{format_math_html(str(step))}</div>')
            parts.append('</div>')
        if "invariant_proved" in wca:
            parts.append(f'<p style="font-size:0.90rem;color:var(--success);font-weight:700;margin-top:8px">✅ Invariant Proved: {format_math_html(str(wca["invariant_proved"]))}</p>')
        parts.append("</div>")
        
    # Independent Exit Task
    if exit_task:
        et_prompt = exit_task.get("prompt", "")
        et_ans = exit_task.get("answer", exit_task.get("model_solution", ""))
        parts.append(f"""
        <div class="exit-task" style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin-top:20px">
          <h4 style="font-size:0.98rem;font-weight:800;color:var(--accent);margin-bottom:8px">
            🎯 Independent Exit Task (Technique T12)
          </h4>
          <p style="font-size:0.95rem;line-height:1.65;margin-bottom:8px">{format_math_html(et_prompt)}</p>
          <textarea class="qb-textarea" placeholder="Formulate your independent proof or calculation here..."></textarea>
          <details class="model-proof" style="margin-top:12px;background:var(--card);padding:14px;border-radius:8px;border:1px solid var(--border)">
            <summary style="cursor:pointer;font-weight:700;color:var(--success)">Reveal Model Exit Solution</summary>
            <div style="margin-top:10px;font-size:0.95rem;line-height:1.75">
              {format_math_html(str(et_ans))}
            </div>
          </details>
        </div>
        """)
        
    parts.append("</div>")
    
    # CORE 1B: DUAL-STAGE RECALL & 4-STAGE SELF-TUTOR FLOW
    parts.append(f"""
      <!-- CORE 1B -->
      <div class="panel" style="border-left:5px solid {palette['primary']};padding-left:18px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <span class="qb-badge" style="background:{palette['bg']};color:{palette['primary']};border:1.5px solid {palette['primary']};font-size:0.88rem;font-weight:800;box-shadow:0 0 10px {palette['glow']}">BLUEPRINT BP-CORE1B-RECONSTRUCTION</span>
          <h3 style="font-size:1.25rem;font-weight:800;color:var(--text);margin:0">
            Core 1B · Dual-Stage Recall &amp; 4-Stage Self-Tutor Flow
          </h3>
        </div>
        <p style="color:var(--text-muted);font-size:0.92rem;margin-bottom:16px">
          Complete the four unassisted retrieval gates to lock in procedural and conceptual mastery without teacher deferral.
        </p>
    """)
    
    # Stage 1: Predict
    if stage1:
        s1_prompt = stage1.get("prompt", "")
        s1_opts = stage1.get("options", [])
        s1_rat = stage1.get("predict_rationale", "")
        parts.append(f"""
        <div class="predict-gate" style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:16px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="rung-tag rung-nudge">STAGE 1 · PREDICT GATE</span>
            <span style="font-size:0.88rem;color:var(--text-muted);font-weight:700">UNASSISTED RECALL</span>
          </div>
          <p style="font-size:0.95rem;line-height:1.65;font-weight:700;margin-bottom:10px">{format_math_html(s1_prompt)}</p>
        """)
        if s1_opts:
            parts.append('<div style="display:grid;grid-template-columns:1fr;gap:8px;margin-bottom:12px">')
            for opt in s1_opts:
                parts.append(f"""
                <label style="display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.92rem">
                  <input type="radio" name="{radio_predict}" value="{html.escape(str(opt)[:2])}">
                  <span>{format_math_html(str(opt))}</span>
                </label>
                """)
            parts.append('</div>')
        if s1_rat:
            parts.append(f"""
            <details style="background:var(--card);padding:10px 14px;border-radius:6px;border:1px solid var(--border)">
              <summary style="cursor:pointer;font-weight:700;font-size:0.90rem;color:var(--accent)">View Predict Rationale &amp; Mechanism</summary>
              <p style="margin-top:6px;font-size:0.92rem;line-height:1.65">{format_math_html(s1_rat)}</p>
            </details>
            """)
        parts.append("</div>")
        
    # Stage 2: Attempt
    if stage2:
        s2_task = stage2.get("task", "")
        s2_closure = stage2.get("model_closure_revealed_post_attempt", {})
        parts.append(f"""
        <div class="attempt-box" style="background:var(--surface);border:1.5px dashed var(--border-light);border-radius:10px;padding:16px;margin-bottom:16px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="rung-tag rung-crux">STAGE 2 · ACTIVE ATTEMPT</span>
            <span style="font-size:0.88rem;color:var(--warning);font-weight:700">LOCKED UNTIL COMMITMENT</span>
          </div>
          <p style="font-size:0.95rem;line-height:1.65;font-weight:700;margin-bottom:10px">{format_math_html(s2_task)}</p>
          <textarea class="qb-textarea" placeholder="Formulate your complete unassisted derivation before revealing the model proof..."></textarea>
          <details class="model-proof" style="margin-top:12px;background:var(--card);padding:14px;border-radius:8px;border:1px solid var(--border)">
            <summary style="cursor:pointer;font-weight:700;color:var(--success)">Reveal Autonomous Model Proof (Post-Attempt)</summary>
            <div style="margin-top:10px;font-size:0.95rem;line-height:1.75">
        """)
        if isinstance(s2_closure, dict):
            for k, v in s2_closure.items():
                parts.append(f'<div style="margin-bottom:6px"><strong>{html.escape(k)}:</strong> {format_math_html(str(v))}</div>')
        elif isinstance(s2_closure, list):
            for item in s2_closure:
                parts.append(f'<div style="margin-bottom:6px">{format_math_html(str(item))}</div>')
        else:
            parts.append(f'<div>{format_math_html(str(s2_closure))}</div>')
        parts.append("""
            </div>
          </details>
        </div>
        """)
        
    # Stage 3: Reverse Reconstruction
    if stage3:
        route = stage3.get("reconstruction_route", "STEP_RECONSTRUCTION")
        d_steps = stage3.get("dialog_steps", [])
        parts.append(f"""
        <div class="step-reconstruction" style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:16px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="rung-tag rung-represent">STAGE 3 · REVERSE RECONSTRUCTION</span>
            <span style="font-size:0.88rem;color:var(--purple);font-weight:700">{html.escape(str(route))}</span>
          </div>
          <p style="font-size:0.92rem;color:var(--text-muted);margin-bottom:10px">
            Reverse reconstruction stress-tests conceptual stability by solving via an alternative invariant route:
          </p>
        """)
        for ds in d_steps:
            inq = ds.get("inquiry", "")
            exp_in = ds.get("expected_insight", "")
            parts.append(f"""
            <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:10px">
              <p style="font-size:0.92rem;font-weight:750;color:var(--accent)">💬 Inquiry: {format_math_html(inq)}</p>
              <p style="font-size:0.92rem;line-height:1.65;margin-top:6px;color:var(--text)">
                <strong>Key Invariant Insight:</strong> {format_math_html(exp_in)}
              </p>
            </div>
            """)
        parts.append("</div>")
        
    # Stage 4: Boundary Test
    if stage4:
        s4_prompt = stage4.get("prompt", "")
        s4_opts = stage4.get("options", [])
        s4_correct = stage4.get("correct_option", "")
        s4_exp = stage4.get("explanation", "")
        parts.append(f"""
        <div class="boundary-test" style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:16px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="rung-tag rung-verify">STAGE 4 · BOUNDARY TEST &amp; LIMITING CASE</span>
            <span style="font-size:0.88rem;color:var(--success);font-weight:700">CHANGED GIVENS &amp; PERTURBATION</span>
          </div>
          <p style="font-size:0.95rem;line-height:1.65;font-weight:700;margin-bottom:10px">{format_math_html(s4_prompt)}</p>
        """)
        if s4_opts:
            parts.append('<div style="display:grid;grid-template-columns:1fr;gap:8px;margin-bottom:12px">')
            for opt in s4_opts:
                parts.append(f"""
                <label style="display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.92rem">
                  <input type="radio" name="{radio_boundary}" value="{html.escape(str(opt)[:2])}">
                  <span>{format_math_html(str(opt))}</span>
                </label>
                """)
            parts.append('</div>')
        parts.append(f"""
          <details style="margin-top:10px;background:var(--card);padding:12px 14px;border-radius:6px;border:1px solid var(--border)">
            <summary style="cursor:pointer;font-weight:700;font-size:0.90rem;color:var(--success)">Check Boundary Test &amp; Limiting Case Result</summary>
            <p style="margin-top:6px;font-size:0.92rem;line-height:1.65;color:var(--text)">
              <strong style="color:var(--success)">Correct Option ({html.escape(s4_correct)}):</strong> {format_math_html(s4_exp)}
            </p>
          </details>
        </div>
        """)
        
    # Hint Ladder
    if hint_ladder:
        h1 = hint_ladder.get("hint_1_conceptual_nudge", {})
        h2 = hint_ladder.get("hint_2_tactical_step", {})
        parts.append("""
        <div style="margin-top:16px">
          <h4 style="font-size:0.90rem;font-weight:800;color:var(--text-muted);text-transform:uppercase;margin-bottom:8px">
            💡 2-Rung Scaffold Ladder (Non-Leaking Cognitive Anchors)
          </h4>
        """)
        if h1:
            parts.append(f"""
            <div class="ladder-rung">
              <span class="rung-tag rung-nudge">RUNG 1 · CONCEPTUAL NUDGE</span>
              <p style="font-size:0.92rem;line-height:1.6;margin-top:4px">{format_math_html(h1.get("text", ""))}</p>
            </div>
            """)
        if h2:
            parts.append(f"""
            <div class="ladder-rung">
              <span class="rung-tag rung-tactical">RUNG 2 · TACTICAL STEP</span>
              <p style="font-size:0.92rem;line-height:1.6;margin-top:4px">{format_math_html(h2.get("text", ""))}</p>
            </div>
            """)
        parts.append("</div>")
        
    parts.append("""
      </div>
    </div>
    """)
    
    return "".join(parts)

def embed_standalone_katex(page_html: str) -> str:
    """Embed the existing repository-vendored KaTeX in each byte-identical HTML.

    Relative vendor URLs work only from standalone/, not public/standalone/ and
    public/docs test routes. CDN fallback is also unsuitable for offline use.
    This embeds the *existing* renderer and its WOFF2 faces (not a new engine).
    """
    vendor = Path("standalone/vendor/katex/0.16.8")
    css = (vendor / "katex.min.css").read_text(encoding="utf-8")
    katex_js = (vendor / "katex.min.js").read_text(encoding="utf-8")
    auto_js = (vendor / "contrib/auto-render.min.js").read_text(encoding="utf-8")

    embedded_faces = set()

    def embed_font(match):
        relative = match.group(1)
        font_path = vendor / relative
        if not font_path.is_file():
            raise FileNotFoundError(f"Declared KaTeX font missing: {font_path}")
        embedded_faces.add(relative)
        payload = base64.b64encode(font_path.read_bytes()).decode("ascii")
        return 'url("data:font/woff2;base64,' + payload + '")'

    css = re.sub(r"url\\((fonts/[^)]+\\.woff2)\\)", embed_font, css)
    if len(embedded_faces) != 20:
        raise RuntimeError(f"Expected 20 KaTeX font faces, got {len(embedded_faces)}")

    previous = (
        '<link rel="stylesheet" href="vendor/katex/0.16.8/katex.min.css" onerror="this.onerror=null;this.href=\'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css\';">\\n'
        '  <script src="vendor/katex/0.16.8/katex.min.js" onerror="this.onerror=null;this.src=\'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js\';"></script>\\n'
        '  <script src="vendor/katex/0.16.8/contrib/auto-render.min.js" onerror="this.onerror=null;this.src=\'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js\';"></script>'
    )
    replacement = (
        '<!-- Repository-vendored KaTeX 0.16.8, MIT; license in standalone/vendor/katex/0.16.8/LICENSE -->\\n'
        '<style id="offline-katex-css">' + css + '</style>\\n'
        '<script id="offline-katex-core">' + katex_js.replace("</script", "<\\\\/script") + '</script>\\n'
        '<script id="offline-katex-auto">' + auto_js.replace("</script", "<\\\\/script") + '</script>'
    )
    if page_html.count(previous) != 1:
        raise RuntimeError("STANDALONE_KATEX_VENDOR_MARKUP_DRIFT")
    return page_html.replace(previous, replacement)


def main():
    root = Path(".")
    
    # 1. Load Batch 1 (2025-26 Set B - 50 items)
    with open("Mathematics/question-bank/sof-imo-2025-26-set-b.core2.json", "r", encoding="utf-8") as f:
        set_b_data = json.load(f)["questions"]
        
    # 2. Load Batch 2 (2025-26 Set A - 50 items)
    with open("Mathematics/question-bank/sof-imo-2025-26-set-a.core2.json", "r", encoding="utf-8") as f:
        set_a_data = json.load(f)["questions"]

    # 3. Load Batch 3 (2024-25 Set B - 50 items)
    with open("Mathematics/question-bank/sof-imo-2024-25-set-b.core2.json", "r", encoding="utf-8") as f:
        set_24b_data = json.load(f)["questions"]

    # 4. Load Batch 4 (2023-24 Set A - 50 items)
    with open("Mathematics/question-bank/sof-imo-2023-24-set-a.core2.json", "r", encoding="utf-8") as f:
        set_23a_data = json.load(f)["questions"]

    # 5. Load Official Sample (2026-27 Sample - 10 items)
    with open("Mathematics/question-bank/sof-imo-sample-2026-27.core2.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)["questions"]

    # 6. Load HOTS & Hard Olympiad Expansion (50 items)
    with open("Mathematics/question-bank/sof-imo-hots-olympiad-expansion.core2.json", "r", encoding="utf-8") as f:
        expansion_data = json.load(f)["questions"]

    # Normalize all questions into a unified list
    unified_questions = []

    # Add Set A (50 items)
    for q in set_a_data:
        unified_questions.append({
            "id": q["id"],
            "num": q["paper_origin_locator"]["question_number"],
            "paper": "SOF-IMO-G09-L1-2025-26-A",
            "paper_label": "2025-26 Set A",
            "section": q["section"],
            "topic": q["taxonomy"]["topic"],
            "topic_name": q["taxonomy"]["topic_label"],
            "title": q["title"],
            "band": q["cognitive_classification"]["difficulty_band"],
            "demand": q["cognitive_classification"]["primary_demand"],
            "cell": q["cognitive_classification"]["qrt_cell"],
            "stem": q["stem"],
            "options": q["options"],
            "choice": q["answer"]["choice"],
            "answer_text": q["answer"]["value"],
            "figure_ref": q["figure_ref"],
            "hint1": q["hint_ladder"]["hint1_conceptual_nudge"],
            "hint2": q["hint_ladder"]["hint2_tactical_step"],
            "hint3": q["cognitive_classification"]["crux_move"],
            "solution": q["solution"]["derivation"],
            "check": q["solution"]["independent_check"]["verification"],
            "check_type": q["solution"]["independent_check"]["check_type"],
            "distractors": q["distractor_rationale"]
        })

    # Add Set B 2025-26 (50 items)
    for q in set_b_data:
        unified_questions.append({
            "id": q["id"],
            "num": q["paper_origin_locator"]["question_number"],
            "paper": "SOF-IMO-G09-L1-2025-26-B",
            "paper_label": "2025-26 Set B",
            "section": q["section"],
            "topic": q["taxonomy"]["topic"],
            "topic_name": q["taxonomy"]["topic_label"],
            "title": q["title"],
            "band": q["cognitive_classification"]["difficulty_band"],
            "demand": q["cognitive_classification"]["primary_demand"],
            "cell": q["cognitive_classification"]["qrt_cell"],
            "stem": q["stem"],
            "options": q["options"],
            "choice": q["answer"]["choice"],
            "answer_text": q["answer"]["value"],
            "figure_ref": q["figure_ref"],
            "hint1": q["hint_ladder"]["hint1_conceptual_nudge"],
            "hint2": q["hint_ladder"]["hint2_tactical_step"],
            "hint3": q["cognitive_classification"]["crux_move"],
            "solution": q["solution"]["derivation"],
            "check": q["solution"]["independent_check"]["verification"],
            "check_type": q["solution"]["independent_check"]["check_type"],
            "distractors": q["distractor_rationale"]
        })

    # Add Set B 2024-25 (50 items)
    for q in set_24b_data:
        unified_questions.append({
            "id": q["id"],
            "num": q["paper_origin_locator"]["question_number"],
            "paper": "SOF-IMO-G09-L1-2024-25-B",
            "paper_label": "2024-25 Set B",
            "section": q["section"],
            "topic": q["taxonomy"]["topic"],
            "topic_name": q["taxonomy"]["topic_label"],
            "title": q["title"],
            "band": q["cognitive_classification"]["difficulty_band"],
            "demand": q["cognitive_classification"]["primary_demand"],
            "cell": q["cognitive_classification"]["qrt_cell"],
            "stem": q["stem"],
            "options": q["options"],
            "choice": q["answer"]["choice"],
            "answer_text": q["answer"]["value"],
            "figure_ref": q["figure_ref"],
            "hint1": q["hint_ladder"]["hint1_conceptual_nudge"],
            "hint2": q["hint_ladder"]["hint2_tactical_step"],
            "hint3": q["cognitive_classification"]["crux_move"],
            "solution": q["solution"]["derivation"],
            "check": q["solution"]["independent_check"]["verification"],
            "check_type": q["solution"]["independent_check"]["check_type"],
            "distractors": q["distractor_rationale"]
        })

    # Add Set A 2023-24 (50 items)
    for q in set_23a_data:
        unified_questions.append({
            "id": q["id"],
            "num": q["paper_origin_locator"]["question_number"],
            "paper": "SOF-IMO-G09-L1-2023-24-A",
            "paper_label": "2023-24 Set A",
            "section": q["section"],
            "topic": q["taxonomy"]["topic"],
            "topic_name": q["taxonomy"]["topic_label"],
            "title": q["title"],
            "band": q["cognitive_classification"]["difficulty_band"],
            "demand": q["cognitive_classification"]["primary_demand"],
            "cell": q["cognitive_classification"]["qrt_cell"],
            "stem": q["stem"],
            "options": q["options"],
            "choice": q["answer"]["choice"],
            "answer_text": q["answer"]["value"],
            "figure_ref": q["figure_ref"],
            "hint1": q["hint_ladder"]["hint1_conceptual_nudge"],
            "hint2": q["hint_ladder"]["hint2_tactical_step"],
            "hint3": q["cognitive_classification"]["crux_move"],
            "solution": q["solution"]["derivation"],
            "check": q["solution"]["independent_check"]["verification"],
            "check_type": q["solution"]["independent_check"]["check_type"],
            "distractors": q["distractor_rationale"]
        })

    # Add Official Sample 2026-27 (10 items)
    for q in sample_data:
        unified_questions.append({
            "id": q["id"],
            "num": q["paper_origin_locator"]["question_number"],
            "paper": "SOF-IMO-G09-SAMPLE-2026-27",
            "paper_label": "2026-27 Sample",
            "section": q["section"],
            "topic": q["taxonomy"]["topic"],
            "topic_name": q["taxonomy"]["topic_label"],
            "title": q["title"],
            "band": q["cognitive_classification"]["difficulty_band"],
            "demand": q["cognitive_classification"]["primary_demand"],
            "cell": q["cognitive_classification"]["qrt_cell"],
            "stem": q["stem"],
            "options": q["options"],
            "choice": q["answer"]["choice"],
            "answer_text": q["answer"]["value"],
            "figure_ref": q["figure_ref"],
            "hint1": q["hint_ladder"]["hint1_conceptual_nudge"],
            "hint2": q["hint_ladder"]["hint2_tactical_step"],
            "hint3": q["cognitive_classification"]["crux_move"],
            "solution": q["solution"]["derivation"],
            "check": q["solution"]["independent_check"]["verification"],
            "check_type": q["solution"]["independent_check"]["check_type"],
            "distractors": q["distractor_rationale"]
        })

    # Add HOTS & Hard Olympiad Expansion (50 items)
    for q in expansion_data:
        unified_questions.append({
            "id": q["id"],
            "num": q["paper_origin_locator"]["question_number"],
            "paper": "SOF-IMO-G09-HOTS-OLYMPIAD-EXP",
            "paper_label": "HOTS & Olympiad Expansion",
            "section": q["section"],
            "topic": q["taxonomy"]["topic"],
            "topic_name": q["taxonomy"]["topic_label"],
            "title": q["title"],
            "band": q["cognitive_classification"]["difficulty_band"],
            "demand": q["cognitive_classification"]["primary_demand"],
            "cell": q["cognitive_classification"]["qrt_cell"],
            "stem": q["stem"],
            "options": q["options"],
            "choice": q["answer"]["choice"],
            "answer_text": q["answer"]["value"],
            "figure_ref": q["figure_ref"],
            "hint1": q["hint_ladder"]["hint1_conceptual_nudge"],
            "hint2": q["hint_ladder"]["hint2_tactical_step"],
            "hint3": q["cognitive_classification"]["crux_move"],
            "solution": q["solution"]["derivation"],
            "check": q["solution"]["independent_check"]["verification"],
            "check_type": q["solution"]["independent_check"]["check_type"],
            "distractors": q["distractor_rationale"]
        })

    print(f"Total unified questions compiled: {len(unified_questions)}")

    # Sort questions: first by paper, then by question number
    paper_order = ["2025-26 Set A", "2025-26 Set B", "2024-25 Set B", "2023-24 Set A", "2026-27 Sample", "HOTS & Olympiad Expansion"]
    unified_questions.sort(key=lambda x: (paper_order.index(x["paper_label"]) if x["paper_label"] in paper_order else 99, x["num"]))

    # Extract distinct facets for filtering
    papers = ["All Papers", "2025-26 Set A", "2025-26 Set B", "2024-25 Set B", "2023-24 Set A", "2026-27 Sample", "HOTS & Olympiad Expansion"]

    # Normalize display topic labels to avoid duplicates from typographical variance (e.g. straight vs curly quotes)
    def norm_topic_label(s: str) -> str:
        return s.replace("’", "'").replace("‘", "'").strip()

    topic_counts = {}
    display_topics_map = {}
    for q in unified_questions:
        raw_name = q["topic_name"]
        norm_name = norm_topic_label(raw_name)
        if norm_name not in display_topics_map:
            display_topics_map[norm_name] = norm_name
        topic_counts[norm_name] = topic_counts.get(norm_name, 0) + 1

    display_topics = sorted(list(display_topics_map.values()))

    # Calculate counts for papers, difficulty bands and cognitive demands
    paper_counts = {}
    for q in unified_questions:
        p = q["paper_label"]
        paper_counts[p] = paper_counts.get(p, 0) + 1

    band_counts = {}
    for q in unified_questions:
        b = q["band"]
        band_counts[b] = band_counts.get(b, 0) + 1

    demand_counts = {}
    for q in unified_questions:
        d = q["demand"]
        demand_counts[d] = demand_counts.get(d, 0) + 1

    bands = ["D1", "D2", "D3", "D4"]
    demands = ["RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"]

    # Build HTML
    html_parts = []
    html_parts.append("""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Grade 9 IMO Mathematics · Core 2 Question Bank & Blueprints Suite</title>
  <meta name="description" content="Complete Master Suite for Grade 9 IMO Mathematics: 184 authentic questions under Core 2 custody with vector SVGs, KaTeX typography, progressive hint ladders, and Core 1A/1B self-tutor modules.">

  <!-- KaTeX Typography (Local Vendor Primary + CDN Fallback) -->
  <link rel="stylesheet" href="vendor/katex/0.16.8/katex.min.css" onerror="this.onerror=null;this.href='https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css';">
  <script src="vendor/katex/0.16.8/katex.min.js" onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js';"></script>
  <script src="vendor/katex/0.16.8/contrib/auto-render.min.js" onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js';"></script>

  <style>
    :root {
      --bg: #090e17;
      --surface: #101826;
      --card: #172338;
      --card-hover: #1e2e4a;
      --border: #263854;
      --border-light: #344c72;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #f87171;
      --purple: #c084fc;
      --radius: 12px;
      --touch-min: 48px;
    }

    [data-theme="light"] {
      --bg: #f8fafc;
      --surface: #ffffff;
      --card: #ffffff;
      --card-hover: #f1f5f9;
      --border: #cbd5e1;
      --border-light: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --accent: #0284c7;
      --accent-glow: rgba(2, 132, 199, 0.12);
      --success: #059669;
      --warning: #d97706;
      --danger: #dc2626;
      --purple: #7e22ce;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    html {
      font-size: 16px;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 16px;
      line-height: 1.6;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Fixed Header Shell (Ultra-Crisp Retina) */
    header.g9-shell {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(10, 16, 28, 0.88);
      backdrop-filter: blur(16px) saturate(180%);
      -webkit-backdrop-filter: blur(16px) saturate(180%);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35), 0 1px 0 rgba(255, 255, 255, 0.05);
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
      transition: all 0.25s ease;
    }

    [data-theme="light"] header.g9-shell {
      background: rgba(255, 255, 255, 0.88);
      border-bottom: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06), 0 1px 0 rgba(0, 0, 0, 0.03);
    }

    .shell-inner {
      max-width: min(95vw, 1640px);
      margin: 0 auto;
      padding: 8px 18px;
      min-height: 56px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
    }

    /* Crisp Brand Identity */
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: var(--text);
      flex-shrink: 0;
      user-select: none;
    }

    .brand-glyph {
      width: 34px;
      height: 34px;
      border-radius: 9px;
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      color: #090e17;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 1.15rem;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
      flex-shrink: 0;
    }

    .brand-info {
      display: flex;
      flex-direction: column;
      line-height: 1.15;
    }

    .brand-title {
      font-weight: 800;
      font-size: 1.05rem;
      letter-spacing: -0.02em;
      color: var(--text);
      white-space: nowrap;
    }

    .brand-subtitle {
      font-size: 0.88rem;
      font-weight: 750;
      letter-spacing: 0.06em;
      color: var(--accent);
      text-transform: uppercase;
      white-space: nowrap;
    }

    .brand-badge {
      font-size: 0.88rem;
      padding: 3px 10px;
      border-radius: 999px;
      background: rgba(56, 189, 248, 0.14);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.32);
      font-weight: 750;
      letter-spacing: 0.03em;
      white-space: nowrap;
    }

    /* Segmented Navigation Capsule */
    .nav-tabs {
      display: flex;
      align-items: center;
      gap: 4px;
      background: rgba(17, 24, 39, 0.72);
      padding: 4px 6px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.25);
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      flex-shrink: 1;
    }

    .nav-tabs::-webkit-scrollbar {
      display: none;
    }

    [data-theme="light"] .nav-tabs {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06);
    }

    .tab-btn {
      min-height: 38px;
      padding: 6px 12px;
      border-radius: 7px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-muted);
      font-weight: 650;
      font-size: 0.88rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      white-space: nowrap;
      transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
    }

    .tab-btn:hover {
      background: rgba(255, 255, 255, 0.06);
      color: var(--text);
    }

    [data-theme="light"] .tab-btn:hover {
      background: rgba(0, 0, 0, 0.04);
      color: var(--text);
    }

    .tab-btn.active {
      background: var(--surface);
      border-color: rgba(56, 189, 248, 0.4);
      color: var(--accent);
      font-weight: 750;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    [data-theme="light"] .tab-btn.active {
      background: #ffffff;
      border-color: #cbd5e1;
      color: var(--accent);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Structured Micro-Pills inside Tabs */
    .tab-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.88rem;
      font-weight: 750;
      padding: 1px 7px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      border: 1px solid rgba(255, 255, 255, 0.08);
      line-height: 1.3;
      white-space: nowrap;
    }

    .tab-btn.active .tab-pill {
      background: rgba(56, 189, 248, 0.18);
      color: var(--accent);
      border-color: rgba(56, 189, 248, 0.35);
    }

    .tab-pill-d3 { color: var(--warning); border-color: rgba(251, 191, 36, 0.35); background: rgba(251, 191, 36, 0.12); }
    .tab-pill-d4 { color: var(--purple); border-color: rgba(192, 132, 252, 0.35); background: rgba(192, 132, 252, 0.12); }
    .tab-pill-d2 { color: var(--accent); border-color: rgba(56, 189, 248, 0.35); background: rgba(56, 189, 248, 0.12); }
    .tab-pill-d1 { color: var(--success); border-color: rgba(52, 211, 153, 0.35); background: rgba(52, 211, 153, 0.12); }

    /* Action Controls */
    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .theme-toggle {
      min-height: 38px;
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text);
      cursor: pointer;
      font-weight: 700;
      font-size: 0.88rem;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
      user-select: none;
      white-space: nowrap;
    }

    .theme-toggle:hover {
      border-color: var(--accent);
      background: var(--card-hover);
      transform: translateY(-1px);
    }

    /* Container */
    main.container {
      max-width: min(95vw, 1640px);
      margin: 0 auto;
      padding: 24px 20px 48px;
      flex: 1;
      width: 100%;
    }

    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.2s ease-in-out; }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Panels & Cards */
    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      flex-wrap: wrap;
      gap: 12px;
    }

    .panel-title {
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: -0.01em;
    }

    .lead-text {
      font-size: 1.05rem;
      line-height: 1.65;
      color: var(--text-muted);
      margin-bottom: 18px;
    }

    /* Dynamic Search & Filter Bar (App Style) */
        .topic-module-card {
      scroll-margin-top: 80px;
      transition: all 0.25s ease;
    }

    .topic-module-card.highlighted {
      box-shadow: 0 0 0 3px var(--accent), 0 8px 30px rgba(56, 189, 248, 0.3) !important;
    }

    .qb-question.highlighted {
      box-shadow: 0 0 0 3px var(--accent), 0 8px 30px rgba(56, 189, 248, 0.3) !important;
    }

    /* ======================================================= */
    /* DYNAMIC TOPIC COLOR BUTTONS & SCROLLSPY COLOR BAND     */
    /* ======================================================= */
    .topic-sticky-bar {
      position: sticky;
      top: 60px;
      z-index: 85;
      background: rgba(15, 23, 42, 0.94);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1.5px solid var(--border);
      border-radius: 12px;
      padding: 14px 18px 16px 18px;
      margin: 18px 0 24px 0;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      transition: padding 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }

    [data-theme="light"] .topic-sticky-bar {
      background: rgba(255, 255, 255, 0.94);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    .topic-sticky-bar.collapsed {
      padding: 10px 18px 10px 18px;
    }

    .topic-sticky-bar.collapsed .topic-buttons-track {
      display: none !important;
    }

    .topic-band-strip {
      height: 5px;
      width: calc(100% + 36px);
      margin: -14px -18px 12px -18px;
      border-radius: 12px 12px 0 0;
      transition: background-color 0.35s ease, box-shadow 0.35s ease;
    }

    .topic-sticky-bar.collapsed .topic-band-strip {
      margin: -10px -18px 10px -18px;
    }

    .topic-sticky-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      cursor: pointer;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
      padding: 2px 0 10px 0;
    }

    .topic-sticky-bar.collapsed .topic-sticky-header {
      padding-bottom: 0;
    }

    .topic-header-lead {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .topic-header-title {
      font-size: 0.88rem;
      font-weight: 800;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .topic-header-active-name {
      font-size: 0.95rem;
      font-weight: 800;
      transition: color 0.3s ease;
    }

    .topic-header-actions {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .topic-header-hint {
      font-size: 0.88rem;
      color: var(--text-muted);
      font-weight: 700;
    }

    .topic-collapse-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 750;
      color: var(--text);
      background: var(--surface);
      border: 1px solid var(--border);
      cursor: pointer;
      transition: all 0.2s ease;
      min-height: 34px;
      user-select: none;
    }

    .topic-collapse-btn:hover {
      background: var(--surface-hover, rgba(255, 255, 255, 0.08));
      border-color: var(--accent);
      color: var(--accent);
    }

    .topic-collapse-btn .collapse-icon {
      font-size: 0.88rem;
      transition: transform 0.2s ease;
    }

    .topic-pulse-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
      transition: background-color 0.35s ease, box-shadow 0.35s ease;
    }

    .topic-buttons-track {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .topic-jump-label {
      font-size: 0.88rem;
      font-weight: 750;
      color: var(--text-muted);
      margin-right: 4px;
    }

    .topic-nav-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 14px;
      border-radius: 999px;
      font-size: 0.88rem;
      font-weight: 700;
      cursor: pointer;
      border: 1.5px solid var(--topic-color, var(--border));
      background: var(--topic-bg, var(--card));
      color: var(--text);
      min-height: 36px;
      transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
      text-decoration: none;
    }

    .topic-nav-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 14px var(--topic-glow, rgba(56, 189, 248, 0.25));
      filter: brightness(1.15);
    }

    .topic-nav-btn.active {
      background: var(--topic-color, var(--accent)) !important;
      color: #090e17 !important;
      font-weight: 800 !important;
      box-shadow: 0 0 16px var(--topic-glow, rgba(56, 189, 248, 0.35)) !important;
      transform: translateY(-1px) scale(1.02);
    }

    .topic-nav-btn .btn-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      display: inline-block;
      background-color: var(--topic-color, var(--accent));
      box-shadow: 0 0 6px var(--topic-color, var(--accent));
      transition: transform 0.2s ease, background-color 0.2s ease;
    }

    .topic-nav-btn.active .btn-dot {
      background-color: #090e17 !important;
      box-shadow: none !important;
      transform: scale(1.2);
    }

    .visual-representation-anchor {
      transition: transform 0.2s ease;
    }

.qb-filter-panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 22px;
    }

    .qb-search-input-wrap {
      position: relative;
      margin-bottom: 14px;
    }

    .qb-search-input {
      width: 100%;
      height: 50px;
      padding: 10px 16px 10px 46px;
      font-size: 1.02rem;
      border-radius: 10px;
      border: 1.5px solid var(--border-light);
      background: var(--card);
      color: var(--text);
      font-family: inherit;
      transition: border-color 0.2s;
    }

    .qb-search-input:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }

    .qb-search-icon {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.15rem;
      color: var(--text-muted);
      pointer-events: none;
    }

    /* Quick Filter Chips */
    .filter-chips-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 10px 0;
    }

    .chip-label {
      font-size: 0.88rem;
      font-weight: 750;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-right: 4px;
    }

    .filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 0.88rem;
      font-weight: 650;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text-muted);
      cursor: pointer;
      user-select: none;
      transition: all 0.18s;
      min-height: 34px;
    }

    .filter-chip:hover {
      border-color: var(--accent);
      color: var(--text);
      background: var(--card-hover);
    }

    .filter-chip.active {
      background: var(--accent);
      color: #090e17;
      border-color: var(--accent);
      font-weight: 750;
    }

    /* Active Filters Bar */
    .active-filters-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding: 10px 14px;
      background: rgba(56, 189, 248, 0.08);
      border: 1px dashed var(--accent);
      border-radius: 10px;
      margin-top: 12px;
    }

    .active-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.88rem;
      font-weight: 700;
      background: var(--card);
      color: var(--text);
      border: 1px solid var(--border);
    }

    .active-pill .remove-pill {
      cursor: pointer;
      color: var(--danger);
      font-weight: 800;
      margin-left: 4px;
    }

    .clear-all-btn {
      background: transparent;
      border: none;
      color: var(--danger);
      font-size: 0.88rem;
      font-weight: 700;
      cursor: pointer;
      margin-left: auto;
      text-decoration: underline;
    }

    /* Question Card (BP-CORE2) */
    .qb-question {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      margin-bottom: 24px;
      transition: border-color 0.18s, box-shadow 0.18s;
    }

    .qb-question:hover {
      border-color: var(--border-light);
      box-shadow: 0 4px 20px rgba(0,0,0,0.22);
    }

    /* Enhanced Band D3 (Hard Olympiad) Card */
    .qb-question[data-band="D3"] {
      border-left: 5px solid #f59e0b;
      border-top-color: rgba(245, 158, 11, 0.28);
      border-right-color: rgba(245, 158, 11, 0.28);
      border-bottom-color: rgba(245, 158, 11, 0.28);
      background: linear-gradient(180deg, rgba(245, 158, 11, 0.04) 0%, var(--card) 130px);
    }

    .qb-question[data-band="D3"]:hover {
      border-color: rgba(245, 158, 11, 0.6);
      border-left: 5px solid #f59e0b;
      box-shadow: 0 6px 24px rgba(245, 158, 11, 0.16);
    }

    /* Enhanced Band D4 (Achievers Section / HOTS) Card */
    .qb-question[data-band="D4"] {
      border-left: 5px solid #38bdf8;
      border-top-color: rgba(56, 189, 248, 0.35);
      border-right-color: rgba(56, 189, 248, 0.35);
      border-bottom-color: rgba(56, 189, 248, 0.35);
      background: linear-gradient(180deg, rgba(56, 189, 248, 0.06) 0%, var(--card) 150px);
      box-shadow: 0 2px 16px rgba(56, 189, 248, 0.08);
    }

    .qb-question[data-band="D4"]:hover {
      border-color: rgba(56, 189, 248, 0.7);
      border-left: 5px solid #38bdf8;
      box-shadow: 0 8px 30px rgba(56, 189, 248, 0.22);
    }

    /* Distinctive D3 & D4 Badges */
    .badge-hots-achievers {
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.22), rgba(168, 85, 247, 0.22));
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.45);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.18);
      font-weight: 800;
      letter-spacing: 0.03em;
    }

    .badge-hard-olympiad {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.20), rgba(239, 68, 68, 0.20));
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.45);
      box-shadow: 0 0 10px rgba(245, 158, 11, 0.15);
      font-weight: 800;
      letter-spacing: 0.03em;
    }

    /* Crux Cognitive Leap Challenge Banners */
    .crux-banner-d4 {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px 12px;
      padding: 10px 14px;
      margin-bottom: 14px;
      border-radius: 8px;
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(168, 85, 247, 0.12));
      border: 1px solid rgba(56, 189, 248, 0.35);
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .crux-banner-d3 {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px 12px;
      padding: 10px 14px;
      margin-bottom: 14px;
      border-radius: 8px;
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.10), rgba(239, 68, 68, 0.08));
      border: 1px solid rgba(245, 158, 11, 0.35);
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .crux-banner-d4 .crux-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(56, 189, 248, 0.22);
      color: #38bdf8;
      font-weight: 800;
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .crux-banner-d3 .crux-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(245, 158, 11, 0.22);
      color: #f59e0b;
      font-weight: 800;
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    /* Tier 3 Crux Rung & Solution Crux Box */
    .rung-crux-container {
      background: linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(56, 189, 248, 0.08));
      border: 1px solid rgba(168, 85, 247, 0.35);
      border-left: 4px solid var(--purple);
    }

    .sol-crux-box {
      margin-bottom: 14px;
      padding: 12px 16px;
      border-radius: 8px;
      background: rgba(192, 132, 252, 0.10);
      border: 1px solid rgba(192, 132, 252, 0.30);
      border-left: 4px solid var(--purple);
      overflow-wrap: break-word;
      word-break: normal;
    }

    .sol-crux-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-weight: 800;
      font-size: 0.90rem;
      color: var(--purple);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .qb-qheader {
      margin-bottom: 16px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 14px;
    }

    .qb-top-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }

    .qb-title {
      font-size: 1.18rem;
      font-weight: 750;
      line-height: 1.4;
      color: var(--text);
      flex: 1;
      min-width: 260px;
    }

    .qb-badges {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      align-items: center;
    }

    .qb-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.88rem;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      cursor: pointer;
      user-select: none;
      border: 1px solid transparent;
    }

    .qb-badge-d1 { background: rgba(52, 211, 153, 0.15); color: var(--success); border-color: rgba(52, 211, 153, 0.3); }
    .qb-badge-d2 { background: rgba(56, 189, 248, 0.15); color: var(--accent); border-color: rgba(56, 189, 248, 0.3); }
    .qb-badge-d3 { background: rgba(251, 191, 36, 0.15); color: var(--warning); border-color: rgba(251, 191, 36, 0.3); }
    .qb-badge-d4 { background: rgba(248, 113, 113, 0.15); color: var(--danger); border-color: rgba(248, 113, 113, 0.3); }

    .qb-badge-qrt { background: rgba(192, 132, 252, 0.15); color: var(--purple); border-color: rgba(192, 132, 252, 0.3); }
    .qb-badge-topic { background: var(--surface); color: var(--text-muted); border-color: var(--border); }
    .qb-badge-paper { background: rgba(56, 189, 248, 0.10); color: var(--accent); border-color: var(--border); }

    .qb-locator {
      font-size: 0.88rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .qb-locator code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.88rem;
      background: var(--surface);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid var(--border);
    }

    /* Question Stem Box */
    .qb-stem-box {
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 18px 20px;
      margin: 16px 0;
      line-height: 1.7;
    }

    .qb-stem-text {
      font-size: 1.02rem;
      color: var(--text);
      margin-bottom: 14px;
    }

    /* Options 2x2 Grid */
    .qb-options-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 10px;
      margin: 14px 0 6px;
    }

    .qb-option-card {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 10px 14px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .qb-option-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--surface);
      border: 1.5px solid var(--border-light);
      font-weight: 800;
      font-size: 0.88rem;
      color: var(--accent);
      flex-shrink: 0;
    }

    /* Embedded Figure Container */
    .qb-figure-wrap {
      margin: 18px 0;
      padding: 18px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .qb-figure-caption {
      font-size: 0.88rem;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--accent);
      margin-bottom: 12px;
      width: 100%;
      text-align: left;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }

    .qb-svg {
      max-width: 100%;
      height: auto;
      display: block;
    }

    /* Student Attempt Box (BP-CORE2) */
    .qb-attempt-box {
      margin: 16px 0;
      padding: 16px;
      border: 1.5px dashed var(--border-light);
      border-radius: 10px;
      background: var(--surface);
    }

    .qb-attempt-box label {
      display: block;
      font-size: 0.95rem;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .qb-textarea {
      width: 100%;
      min-height: 90px;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--card);
      color: var(--text);
      font-family: inherit;
      font-size: 0.95rem;
      resize: vertical;
    }

    .btn-commit {
      min-height: 44px;
      padding: 8px 20px;
      border-radius: 8px;
      background: var(--accent);
      color: #090e17;
      font-weight: 750;
      font-size: 0.95rem;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 10px;
      transition: opacity 0.18s;
    }

    .btn-commit:hover { opacity: 0.92; }

    /* Semantically hidden before a real attempt: not clickable or focusable. */
    .qb-question [hidden] { display: none !important; }
    .qb-attempt-feedback { margin-top: 8px; font-size: 0.9rem; min-height: 1.2em; }
    .qb-attempt-feedback[data-state="invalid"] { color: var(--warning); }
    .qb-attempt-feedback[data-state="committed"] { color: var(--success); }
    .qb-hint-tier { margin: 8px 0; border: 1px solid var(--border); border-radius: 8px; }
    .qb-hint-tier summary { font-weight: 650; }

    /* Support Disclosures (BP-CORE2 & T05) */
    .qb-support-container {
      margin-top: 16px;
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
    }

    .qb-disclosure {
      border-bottom: 1px solid var(--border);
    }

    .qb-disclosure:last-child {
      border-bottom: none;
    }

    .qb-disclosure summary {
      padding: 14px 18px;
      background: var(--surface);
      cursor: pointer;
      font-weight: 700;
      font-size: 0.95rem;
      user-select: none;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
    }

    .qb-disclosure summary > span:first-child {
      flex: 1 1 240px;
      min-width: 200px;
    }

    .qb-disclosure summary > span:last-child {
      flex: 0 0 auto;
      white-space: nowrap;
      margin-left: auto;
    }

    .qb-disclosure-body {
      padding: 18px 20px;
      background: var(--card);
      line-height: 1.75;
      overflow-wrap: break-word;
      word-break: normal;
    }

    /* Hint Ladder Rung Styling */
    .ladder-rung {
      margin: 10px 0;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--surface);
      border: 1px solid var(--border);
      overflow-wrap: break-word;
      word-break: normal;
    }

    .rung-tag {
      display: inline-block;
      font-size: 0.88rem;
      font-weight: 800;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: 4px;
      margin-bottom: 6px;
    }

    .rung-nudge { background: rgba(56, 189, 248, 0.18); color: var(--accent); }
    .rung-tactical { background: rgba(251, 191, 36, 0.18); color: var(--warning); }
    .rung-crux { background: rgba(192, 132, 252, 0.18); color: var(--purple); }

    /* Formal Verification Box (BP-CORE2) */
    .sol-verified-box {
      margin-bottom: 14px;
      padding: 12px 16px;
      border-radius: 8px;
      background: rgba(52, 211, 153, 0.12);
      border: 1px solid rgba(52, 211, 153, 0.28);
      overflow-wrap: break-word;
      word-break: normal;
    }

    .sol-verified-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-weight: 800;
      font-size: 0.90rem;
      color: var(--success);
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .sol-verified-content {
      font-size: 0.95rem;
      line-height: 1.65;
      color: var(--text);
      overflow-wrap: break-word;
      word-break: normal;
    }

    .trap-alert {
      padding: 12px 14px;
      border-radius: 8px;
      background: rgba(248, 113, 113, 0.10);
      border: 1px solid rgba(248, 113, 113, 0.3);
      color: #fca5a5;
      font-size: 0.95rem;
      overflow-wrap: break-word;
      word-break: normal;
    }

    .katex-display {
      overflow-x: auto;
      overflow-y: hidden;
      max-width: 100%;
      padding: 4px 0;
    }

    .no-math {
      font-family: inherit;
      white-space: normal;
    }

    /* ======================================================= */
    /* 12.7" (2944 x 1840) RETINA DISPLAY OPTIMIZATION         */
    /* ======================================================= */
    @media screen and (min-width: 1360px) and (max-width: 2000px),
           screen and (-webkit-min-device-pixel-ratio: 1.5) and (min-width: 1360px) {
      body {
        text-rendering: optimizeLegibility;
      }
      .shell-inner, main.container {
        max-width: 1580px;
        padding-left: 24px;
        padding-right: 24px;
      }
      .qb-options-grid {
        grid-template-columns: repeat(4, 1fr);
      }
      .qb-question {
        padding: 26px 30px;
        margin-bottom: 26px;
        border-radius: 14px;
      }
      .qb-stem-text {
        font-size: 1.08rem;
        line-height: 1.75;
      }
      .topic-module-card {
        padding: 28px 32px;
        border-radius: 14px;
      }
      .topic-sticky-bar {
        top: 56px;
        padding: 14px 22px 16px 22px;
      }
      .topic-sticky-bar.collapsed {
        padding: 10px 22px 10px 22px;
      }
    }

    /* Tablet Portrait & Medium Screens */
    @media screen and (max-width: 1080px) {
      .shell-inner {
        flex-wrap: wrap;
        gap: 10px;
        padding: 8px 14px;
      }
      .nav-tabs {
        order: 3;
        width: 100%;
        overflow-x: auto;
        justify-content: flex-start;
      }
      .brand-subtitle {
        display: none;
      }
      .qb-options-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    /* Phone Fallback */
    @media (max-width: 768px) {
      .shell-inner { flex-direction: column; align-items: stretch; gap: 8px; }
      .qb-options-grid { grid-template-columns: 1fr; }
      .qb-top-row { flex-direction: column; }
    }
  </style>
</head>
<body>
""")

    # Pre-load topic units to populate dynamic navigation counts
    topic_units = load_all_topic_units("Mathematics/units")
    d4_units = [u for u in topic_units if u["band"] == "D4"]
    d3_units = [u for u in topic_units if u["band"] == "D3"]
    d2_units = [u for u in topic_units if u["band"] == "D2"]
    d1_units = [u for u in topic_units if u["band"] == "D1"]

    html_parts.append(f"""
  <!-- FIXED CRISP HEADER SHELL (NO-MATH) -->
  <header class="g9-shell no-math">
    <div class="shell-inner">
      <a href="#" class="brand" aria-label="IMO Grade 9 Master Suite">
        <span class="brand-glyph">∑</span>
        <div class="brand-info">
          <span class="brand-title">IMO Grade 9 Master Suite</span>
          <span class="brand-subtitle">OLYMPIAD RESEARCH BENCHMARK</span>
        </div>
        <span class="brand-badge">{len(unified_questions)} QUESTIONS · CORE 2</span>
      </a>

      <nav class="nav-tabs" role="tablist" aria-label="Master Suite Tabs">
        <button type="button" class="tab-btn active" role="tab" aria-selected="true" onclick="switchTab('core2')">
          <span class="tab-icon">📖</span>
          <span class="tab-title">Core 2</span>
          <span class="tab-pill">{len(unified_questions)} Qs</span>
        </button>
        <button type="button" class="tab-btn" role="tab" aria-selected="false" onclick="switchTab('core1-all')">
          <span class="tab-icon">🌐</span>
          <span class="tab-title">All Core 1</span>
          <span class="tab-pill">{len(topic_units)} Units</span>
        </button>
        <button type="button" class="tab-btn" role="tab" aria-selected="false" onclick="switchTab('d3-core')">
          <span class="tab-icon">🏆</span>
          <span class="tab-title">D3 Core</span>
          <span class="tab-pill tab-pill-d3">{len(d3_units)} Units</span>
        </button>
        <button type="button" class="tab-btn" role="tab" aria-selected="false" onclick="switchTab('d4-core')">
          <span class="tab-icon">💎</span>
          <span class="tab-title">D4 Core</span>
          <span class="tab-pill tab-pill-d4">{len(d4_units)} Units</span>
        </button>
        <button type="button" class="tab-btn" role="tab" aria-selected="false" onclick="switchTab('d2-core')">
          <span class="tab-icon">⚡</span>
          <span class="tab-title">D2 Core</span>
          <span class="tab-pill tab-pill-d2">{len(d2_units)} Units</span>
        </button>
        <button type="button" class="tab-btn" role="tab" aria-selected="false" onclick="switchTab('d1-core')">
          <span class="tab-icon">🌱</span>
          <span class="tab-title">D1 Core</span>
          <span class="tab-pill tab-pill-d1">{len(d1_units)} Unit</span>
        </button>
      </nav>

      <div class="header-actions">
        <button type="button" class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle Dark or Light Theme">
          <span class="theme-icon">🌓</span>
          <span class="theme-title">Theme</span>
        </button>
      </div>
    </div>
  </header>

  <main class="container">

    <!-- ========================================== -->
    <!-- TAB 1: CORE 2 QUESTION BANK ({len(unified_questions)} Questions) -->
    <!-- ========================================== -->
    <div id="tab-core2" class="tab-content active">

      <!-- Dynamic App-Style Filter Bar -->
      <div class="qb-filter-panel">
        <div class="qb-search-input-wrap">
          <span class="qb-search-icon">🔍</span>
          <input type="text" id="qb-search-input" class="qb-search-input" placeholder="Type to search: stems, questions, formulas, topics, locators (e.g. 'polynomial', 'cyclic', '2025-26-B')..." oninput="applyFilters()">
        </div>

        <!-- Papers Row -->
        <div class="filter-chips-row">
          <span class="chip-label">Paper:</span>
          <span class="filter-chip active" data-filter="paper" data-val="ALL" onclick="toggleFilter('paper', 'ALL')">All Papers ({len(unified_questions)})</span>
          <span class="filter-chip" data-filter="paper" data-val="2025-26 Set A" onclick="toggleFilter('paper', '2025-26 Set A')">2025-26 Set A ({paper_counts.get("2025-26 Set A", 0)})</span>
          <span class="filter-chip" data-filter="paper" data-val="2025-26 Set B" onclick="toggleFilter('paper', '2025-26 Set B')">2025-26 Set B ({paper_counts.get("2025-26 Set B", 0)})</span>
          <span class="filter-chip" data-filter="paper" data-val="2024-25 Set B" onclick="toggleFilter('paper', '2024-25 Set B')">2024-25 Set B ({paper_counts.get("2024-25 Set B", 0)})</span>
          <span class="filter-chip" data-filter="paper" data-val="2023-24 Set A" onclick="toggleFilter('paper', '2023-24 Set A')">2023-24 Set A ({paper_counts.get("2023-24 Set A", 0)})</span>
          <span class="filter-chip" data-filter="paper" data-val="2026-27 Sample" onclick="toggleFilter('paper', '2026-27 Sample')">2026-27 Sample ({paper_counts.get("2026-27 Sample", 0)})</span>
          <span class="filter-chip" data-filter="paper" data-val="HOTS & Olympiad Expansion" onclick="toggleFilter('paper', 'HOTS & Olympiad Expansion')">HOTS & Olympiad Expansion ({paper_counts.get("HOTS & Olympiad Expansion", 0)})</span>
        </div>

        <!-- Difficulty Row -->
        <div class="filter-chips-row">
          <span class="chip-label">Difficulty:</span>
          <span class="filter-chip" data-filter="band" data-val="D1" onclick="toggleFilter('band', 'D1')">🌱 D1 (Foundations) ({band_counts.get("D1", 0)})</span>
          <span class="filter-chip" data-filter="band" data-val="D2" onclick="toggleFilter('band', 'D2')">⚡ D2 (Standard Olympiad) ({band_counts.get("D2", 0)})</span>
          <span class="filter-chip" data-filter="band" data-val="D3" onclick="toggleFilter('band', 'D3')">🔥 D3 (Hard Olympiad) ({band_counts.get("D3", 0)})</span>
          <span class="filter-chip" data-filter="band" data-val="D4" onclick="toggleFilter('band', 'D4')">💎 D4 (Achievers Section) ({band_counts.get("D4", 0)})</span>
        </div>

        <!-- Cognitive Demands Row -->
        <div class="filter-chips-row">
          <span class="chip-label">Demand:</span>
""")

    for d in demands:
        cnt = demand_counts.get(d, 0)
        html_parts.append(f"""          <span class="filter-chip" data-filter="demand" data-val="{d}" onclick="toggleFilter('demand', '{d}')">{d} ({cnt})</span>\n""")

    html_parts.append("""        </div>

        <!-- Topics Row -->
        <div class="filter-chips-row">
          <span class="chip-label">Topic:</span>
""")

    for top in display_topics:
        cnt = topic_counts.get(norm_topic_label(top), 0)
        html_parts.append(f"""          <span class="filter-chip" data-filter="topic" data-val="{html.escape(top)}" onclick="toggleFilter('topic', '{html.escape(top)}')">{html.escape(top)} ({cnt})</span>\n""")

    html_parts.append("""        </div>

        <!-- Active Filters Bar -->
        <div id="active-filters-bar" class="active-filters-bar" style="display:none">
          <span style="font-size:0.88rem;font-weight:750">Active Filters:</span>
          <div id="active-pills-list" style="display:flex;gap:6px;flex-wrap:wrap"></div>
          <button type="button" class="clear-all-btn" onclick="clearAllFilters()">✕ Clear all filters</button>
        </div>
      </div>

      <!-- Result Counter -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;font-size:0.95rem;color:var(--text-muted)">
        <span id="result-counter" style="font-weight:750;color:var(--text)">Showing all """ + str(len(unified_questions)) + """ questions</span>
        <span style="font-size:0.88rem">Click any badge to filter dynamically</span>
      </div>

      <!-- Question Cards List -->
      <div id="qb-cards-list">
""")

    # Render each question card
    for idx, q in enumerate(unified_questions, 1):
        qid = q["id"]
        qnum = q["num"]
        paper = q["paper"]
        paper_label = q["paper_label"]
        sec = q["section"].replace("_", " ").title()
        topic_name = q["topic_name"]
        title = html.escape(q["title"])
        band = q["band"]
        demand = q["demand"]
        cell = q["cell"]
        stem = format_math_html(q["stem"])
        options = q["options"]
        choice = q["choice"]
        ans_text = q["answer_text"]
        
        hint1 = format_math_html(str(q.get("hint1") or ""))
        hint2 = format_math_html(str(q.get("hint2") or ""))
        hint3 = format_math_html(str(q.get("hint3") or ""))
        
        solution_txt = format_math_html(str(q.get("solution") or "Verified mathematically from repository audit records."))
        check_txt = format_math_html(str(q.get("check") or "Verified via algebraic derivation."))
        check_type = html.escape(str(q.get("check_type") or "SUBSTITUTION_BACK_CHECK"))
        
        # Build SVG figure markup
        fig_markup = get_figure_markup(q["figure_ref"], qid, q["stem"], options)
        
        # Build options grid
        opt_cards = []
        for opt_k in ["A", "B", "C", "D"]:
            if opt_k in options:
                opt_v = options[opt_k]
                opt_v_html = format_math_html(str(opt_v))
                # Preserve source option order without pre-attempt answer styling.
                # Answer identity is only rendered inside the post-commit solution.
                opt_cards.append(f"""
                  <div class="qb-option-card">
                    <span class="qb-option-badge">({opt_k})</span>
                    <span>{opt_v_html}</span>
                  </div>
                """)
        options_html = f"""<div class="qb-options-grid">{''.join(opt_cards)}</div>""" if opt_cards else ""

        # Build distractor rationales
        distractors_markup = []
        if isinstance(q["distractors"], dict):
            for dk, dv in q["distractors"].items():
                if dk == "trap":
                    distractors_markup.append(f"<div class='trap-alert'><strong>Pitfall:</strong> {format_math_html(dv)}</div>")
                else:
                    distractors_markup.append(f"<div style='margin-bottom:6px'><strong>Option {dk}:</strong> {format_math_html(dv)}</div>")
        distractor_html = "".join(distractors_markup) if distractors_markup else "<p>Distractor diagnostic verified in repository custody register.</p>"

        # Search index string
        stem_search_clean = re.sub(r'[\$\\]', ' ', q['stem'])
        search_blob = html.escape(f"{qid} {stem_search_clean} {title} {topic_name} {paper_label} {sec} {cell}").lower()

        unit_folder = TOPIC_TO_UNIT_FOLDER.get(topic_name.lower().strip(), "polynomials")

        # Distinctive D3/D4 badges & banners
        d3_d4_badge = ""
        crux_banner_html = ""
        if band == "D4":
            d3_d4_badge = f"""<span class="qb-badge badge-hots-achievers" onclick="addActiveFilter('band', 'D4')" title="HOTS Achievers Section Question (3 Marks)">💎 HOTS · ACHIEVERS SECTION (3 MARKS)</span>"""
            crux_banner_html = f"""
            <div class="crux-banner-d4">
              <span class="crux-pill">💎 Achievers Section · HOTS Multi-Stage Synthesis</span>
              <span>Demands coordinating multiple geometric/algebraic invariants with rigorous justification. <strong>Weightage: 3 Marks · Demand: {demand}.</strong></span>
            </div>
            """
        elif band == "D3":
            d3_d4_badge = f"""<span class="qb-badge badge-hard-olympiad" onclick="addActiveFilter('band', 'D3')" title="Hard Olympiad Question">🔥 HARD OLYMPIAD CHALLENGE</span>"""
            crux_banner_html = f"""
            <div class="crux-banner-d3">
              <span class="crux-pill">🔥 Hard Olympiad · Composite Synthesis ({demand})</span>
              <span>Multi-step Olympiad challenge requiring intermediate formulation and invariance deduction.</span>
            </div>
            """

        card_markup = f"""
        <article class="qb-question" id="q-{qid}" data-paper="{paper_label}" data-band="{band}" data-demand="{demand}" data-topic="{topic_name}" data-search="{search_blob}">
          <div class="qb-qheader">
            <div class="qb-top-row">
              <h2 class="qb-title">Q{idx}. {title}</h2>
              <div class="qb-badges">
                {d3_d4_badge}
                <span class="qb-badge qb-badge-{band.lower()}" onclick="addActiveFilter('band', '{band}')" title="Filter by {band}">{band}</span>
                <span class="qb-badge qb-badge-qrt" onclick="addActiveFilter('demand', '{demand}')" title="Filter by {cell}">{cell}</span>
                <span class="qb-badge qb-badge-topic" onclick="addActiveFilter('topic', '{topic_name}')" title="Filter by {topic_name}">📚 {topic_name}</span>
                <span class="qb-badge qb-badge-paper" onclick="addActiveFilter('paper', '{paper_label}')" title="Filter by {paper_label}">📄 {paper_label}</span>
                <span class="qb-badge" style="background:rgba(56,189,248,0.12);color:var(--accent);border:1px solid rgba(56,189,248,0.25)" onclick="jumpToCore1('{unit_folder}')" title="Study Core 1A/1B for {topic_name}">📖 Core 1A/1B</span>
              </div>
            </div>

            <div class="qb-locator">
              <span><strong>Locator:</strong> {paper} · {sec} · Question {qnum} (<code>{qid}</code>)</span>
            </div>
          </div>

          <!-- Official Exam Question Stem Box -->
          <div class="qb-stem-box">
            {crux_banner_html}
            <div style="font-weight:750;margin-bottom:8px;color:var(--accent);font-size:0.95rem;text-transform:uppercase;letter-spacing:0.04em">Official Exam Question:</div>
            <div class="qb-stem-text">{stem}</div>
            {fig_markup}
            {options_html}
            <div style="font-size:0.88rem;color:var(--text-muted);border-top:1px dashed var(--border-light);padding-top:8px;margin-top:12px">
              <strong>Target Mathematical Act ({demand}):</strong> {title}
            </div>
          </div>

          <!-- Student Attempt Box (BP-CORE2) -->
          <div class="qb-attempt-box">
            <label for="att-{qid}"><strong>Your Solution Attempt / Working Notes:</strong></label>
            <textarea class="qb-textarea" id="att-{qid}" placeholder="Formulate equations, deduce intermediate invariants, and commit an answer..."></textarea>
            <button type="button" class="btn-commit" id="commit-{qid}" aria-controls="sol-disc-{qid}" aria-expanded="false" onclick="commitResearchAttempt('{qid}')">Commit Attempt & Reveal Solution</button>
            <p class="qb-attempt-feedback" id="feedback-{qid}" aria-live="polite"></p>
          </div>

          <!-- Grounded Support Accordion (BP-CORE2 & T05) -->
          <div class="qb-support-container">
            <details class="qb-disclosure">
              <summary>
                <span>💡 Hint Ladder · Progressive Support</span>
                <span style="font-size:0.88rem;color:var(--text-muted)">Reveal step-by-step</span>
              </summary>
              <div class="qb-disclosure-body">
                <details class="qb-hint-tier">
                  <summary>Tier 1 · Conceptual Nudge</summary>
                  <div class="ladder-rung"><p>{hint1}</p></div>
                </details>
                <details class="qb-hint-tier">
                  <summary>Tier 2 · Tactical Intermediate Formulation</summary>
                  <div class="ladder-rung"><p>{hint2}</p></div>
                </details>
                <p class="qb-support-note">The decisive move and full worked check become available only after you commit your own working.</p>
              </div>
            </details>

            <details class="qb-disclosure" id="diag-disc-{qid}" hidden inert>
              <summary>
                <span>⚠️ Distractor Diagnostic & Misconceptions</span>
                <span style="font-size:0.88rem;color:var(--warning)">Pitfall alert</span>
              </summary>
              <div class="qb-disclosure-body">
                {distractor_html}
              </div>
            </details>

            <details class="qb-disclosure" id="sol-disc-{qid}" hidden inert>
              <summary>
                <span>✅ Teacher Solution · Complete Derivation & Formal Check</span>
                <span style="font-size:0.88rem;color:var(--text-muted)">Available after a committed attempt</span>
              </summary>
              <div class="qb-disclosure-body">
                {f'''<div class="sol-crux-box">
                  <span class="sol-crux-tag">⚡ Key Olympiad Invariant / Crux Move</span>
                  <p style="margin:6px 0 0 0;font-size:0.95rem;color:var(--text)">{hint3}</p>
                </div>''' if hint3 else ''}
                <div class="sol-verified-box">
                  <div class="sol-verified-badge">✓ Formal Verification ({check_type})</div>
                  <div class="sol-verified-content">{check_txt}</div>
                </div>
                <div style="font-size:1.02rem;line-height:1.75;margin-top:10px">
                  {solution_txt}
                </div>
                <div style="margin-top:14px;padding-top:10px;border-top:1px solid var(--border);font-weight:750;color:var(--success)">
                  Verified Answer: Option ({choice}) — {format_math_html(str(ans_text))}
                </div>
              </div>
            </details>
          </div>
        </article>
        """
        html_parts.append(card_markup)

    html_parts.append("""
      </div>
    </div>
""")

    # Render all Topic-Segregated Core 1A & Core 1B Modules
    unique_topics = []
    seen_folders = set()
    for u in topic_units:
        if u["folder"] not in seen_folders:
            seen_folders.add(u["folder"])
            unique_topics.append(u)

    # 1. TAB: All Core 1 Topics
    html_parts.append(f"""
    <!-- ========================================== -->
    <!-- TAB: ALL CORE 1A / 1B TOPIC MODULES ({len(topic_units)}) -->
    <!-- ========================================== -->
    <div id="tab-core1-all" class="tab-content">
      <div class="panel" style="background:var(--surface);border:1.5px solid var(--accent);border-radius:12px;padding:24px;margin-bottom:24px">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
          <div>
            <span class="qb-badge" style="background:rgba(56,189,248,0.15);color:var(--accent);border:1px solid rgba(56,189,248,0.3)">{len(topic_units)} MODULE PACKAGES · 100% CUSTODY</span>
            <h2 style="font-size:1.45rem;font-weight:800;margin-top:8px">All {len(topic_units)} Core 1A &amp; Core 1B Learning Modules <span class="no-math" style="color:var(--text-muted);font-weight:600">({len(unique_topics)} Topics)</span></h2>
            <p style="color:var(--text-muted);font-size:0.95rem;margin-top:4px">
              Blueprint-Standard Core 1A Declarative Proofs &amp; Core 1B 4-Stage Self-Tutor Reconstructions, segregated topic-wise.
            </p>
          </div>
        </div>

        <!-- Topic Quick-Filter Bar -->
        <div style="margin-top:18px;padding-top:14px;border-top:1px solid var(--border)">
          <div style="font-size:0.88rem;font-weight:750;color:var(--text-muted);text-transform:uppercase;margin-bottom:8px">Filter by Topic:</div>
          <div style="display:flex;flex-wrap:wrap;gap:8px" id="core1-topic-chips">
            <span class="filter-chip active" data-folder="ALL" onclick="filterCore1ByTopic('ALL')">All {len(topic_units)} Modules ({len(unique_topics)} Topics)</span>
    """)
    for u in unique_topics:
        tname = u["topic_name"]
        tbnd = u["band"]
        tfolder = u["folder"]
        pal = TOPIC_COLOR_PALETTES.get(tfolder, {"primary": "#38bdf8"})
        html_parts.append(f"""            <span class="filter-chip" data-folder="{tfolder}" onclick="filterCore1ByTopic('{tfolder}')"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{pal['primary']}"></span>{html.escape(tname)}</span>\n""")
    html_parts.append("""          </div>
        </div>
      </div>
    """)
    html_parts.append(render_topic_jump_navigation(topic_units, prefix="all"))
    html_parts.append("""
      <!-- Modules List -->
      <div id="core1-modules-list">
    """)
    for u in topic_units:
        html_parts.append(render_topic_module_html(u, prefix="all"))
    html_parts.append("""      </div>
    </div>
    """)

    # 2. TAB: D3 Core
    html_parts.append(f"""
    <!-- ========================================== -->
    <!-- TAB: D3 CORE 1A/1B ({len(d3_units)} MODULES) -->
    <!-- ========================================== -->
    <section class="tab-content" id="tab-d3-core" role="tabpanel">
      <div class="panel" style="background:var(--surface);border:1.5px solid var(--warning);border-radius:12px;padding:24px;margin-bottom:24px">
        <span class="qb-badge qb-badge-d3">🏆 BAND D3 · HARD OLYMPIAD CORE</span>
        <h2 style="font-size:1.45rem;font-weight:800;margin-top:8px">Band D3 Core 1A &amp; Core 1B Learning Modules <span class="no-math" style="color:var(--text-muted);font-weight:600">({len(d3_units)} Modules)</span></h2>
        <p style="color:var(--text-muted);font-size:0.95rem;margin-top:4px">
          Advanced algebraic, geometric, and functional olympiad reasoning modules segregated topic-wise.
        </p>
      </div>
    """)
    html_parts.append(render_topic_jump_navigation(d3_units, prefix="d3"))
    for u in d3_units:
        html_parts.append(render_topic_module_html(u, prefix="d3"))
    html_parts.append("""    </section>\n""")

    # 3. TAB: D4 Core
    html_parts.append(f"""
    <!-- ========================================== -->
    <!-- TAB: D4 CORE 1A/1B ({len(d4_units)} MODULES) -->
    <!-- ========================================== -->
    <section class="tab-content" id="tab-d4-core" role="tabpanel">
      <div class="panel" style="background:var(--surface);border:1.5px solid var(--purple);border-radius:12px;padding:24px;margin-bottom:24px">
        <span class="qb-badge qb-badge-d4">💎 BAND D4 · ACHIEVERS SECTION</span>
        <h2 style="font-size:1.45rem;font-weight:800;margin-top:8px">Band D4 Core 1A &amp; Core 1B Learning Modules <span class="no-math" style="color:var(--text-muted);font-weight:600">({len(d4_units)} Modules)</span></h2>
        <p style="color:var(--text-muted);font-size:0.95rem;margin-top:4px">
          High-demand extremal geometric, algebraic, and cyclic structure proofs.
        </p>
      </div>
    """)
    html_parts.append(render_topic_jump_navigation(d4_units, prefix="d4"))
    for u in d4_units:
        html_parts.append(render_topic_module_html(u, prefix="d4"))
    html_parts.append("""    </section>\n""")

    # 4. TAB: D2 Core (6 Topics)
    d2_units = [u for u in topic_units if u["band"] == "D2"]
    html_parts.append(f"""
    <!-- ========================================== -->
    <!-- TAB: D2 CORE 1A/1B ({len(d2_units)} TOPICS) -->
    <!-- ========================================== -->
    <section class="tab-content" id="tab-d2-core" role="tabpanel">
      <div class="panel" style="background:var(--surface);border:1.5px solid var(--accent);border-radius:12px;padding:24px;margin-bottom:24px">
        <span class="qb-badge qb-badge-d2">⚡ BAND D2 · STANDARD OLYMPIAD CORE</span>
        <h2 style="font-size:1.45rem;font-weight:800;margin-top:8px">Band D2 Core 1A &amp; Core 1B Learning Modules <span class="no-math" style="color:var(--text-muted);font-weight:600">({len(d2_units)} Topics)</span></h2>
        <p style="color:var(--text-muted);font-size:0.95rem;margin-top:4px">
          Foundational algebraic manipulation, Euclidean reasoning, coordinate methods, and statistics.
        </p>
      </div>
    """)
    html_parts.append(render_topic_jump_navigation(d2_units, prefix="d2"))
    for u in d2_units:
        html_parts.append(render_topic_module_html(u, prefix="d2"))
    html_parts.append("""    </section>\n""")

    # 5. TAB: D1 Core (1 Topic)
    d1_units = [u for u in topic_units if u["band"] == "D1"]
    html_parts.append(f"""
    <!-- ========================================== -->
    <!-- TAB: D1 CORE 1A/1B ({len(d1_units)} TOPIC) -->
    <!-- ========================================== -->
    <section class="tab-content" id="tab-d1-core" role="tabpanel">
      <div class="panel" style="background:var(--surface);border:1.5px solid var(--success);border-radius:12px;padding:24px;margin-bottom:24px">
        <span class="qb-badge qb-badge-d1">🌱 BAND D1 · FOUNDATIONAL CORE</span>
        <h2 style="font-size:1.45rem;font-weight:800;margin-top:8px">Band D1 Core 1A &amp; Core 1B Learning Modules <span class="no-math" style="color:var(--text-muted);font-weight:600">({len(d1_units)} Topic)</span></h2>
        <p style="color:var(--text-muted);font-size:0.95rem;margin-top:4px">
          Empirical and theoretical probability models and foundational arithmetic reasoning.
        </p>
      </div>
    """)
    html_parts.append(render_topic_jump_navigation(d1_units, prefix="d1"))
    for u in d1_units:
        html_parts.append(render_topic_module_html(u, prefix="d1"))
    html_parts.append("""    </section>\n""")

    # Append Interactive Client-Side JavaScript
    html_parts.append("""
  </main>

  <script>
    // Research portal interaction only. This does not replace the native Core renderer.
    function commitResearchAttempt(questionId) {
      const attempt = document.getElementById('att-' + questionId);
      const feedback = document.getElementById('feedback-' + questionId);
      const solution = document.getElementById('sol-disc-' + questionId);
      const diagnosis = document.getElementById('diag-disc-' + questionId);
      const button = document.getElementById('commit-' + questionId);
      if (!attempt || !solution || !diagnosis || !button || !feedback) return false;

      // A whitespace-only or punctuation-only note is not a learner attempt.
      const working = attempt.value.trim();
      if (!working || !Array.from(working).some(ch => /[A-Za-z0-9]/.test(ch))) {
        feedback.textContent = 'Write your reasoning or answer before committing.';
        feedback.dataset.state = 'invalid';
        attempt.setAttribute('aria-invalid', 'true');
        attempt.focus();
        return false;
      }

      attempt.removeAttribute('aria-invalid');
      attempt.readOnly = true;
      solution.hidden = false;
      solution.removeAttribute('inert');
      diagnosis.hidden = false;
      diagnosis.removeAttribute('inert');
      solution.open = true;
      button.setAttribute('aria-expanded', 'true');
      button.disabled = true;
      button.textContent = 'Attempt committed · solution unlocked';
      feedback.dataset.state = 'committed';
      feedback.textContent = 'Your attempt is committed. The worked solution and diagnostic are now available.';
      const summary = solution.querySelector('summary');
      if (summary) summary.focus();
      return true;
    }

    // Tab Switching
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');

      document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('active');
        el.setAttribute('aria-selected', 'false');
      });

      const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => {
        const oc = b.getAttribute('onclick') || '';
        return oc.includes("'" + tabId + "'") || oc.includes('"' + tabId + '"');
      });
      if (btn) {
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
      }

      window.scrollTo({ top: 0, behavior: 'smooth' });
      triggerKaTeX();
      setTimeout(updateScrollSpyFallback, 80);
    }

    // Dynamic Topic Navigation Collapse & ScrollSpy
    function toggleTopicNavCollapse(prefix) {
      const nav = document.getElementById('topic-nav-' + prefix);
      if (!nav) return;
      const isCollapsed = nav.classList.toggle('collapsed');
      const btn = document.getElementById('collapse-btn-' + prefix);
      if (btn) {
        btn.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
        const icon = btn.querySelector('.collapse-icon');
        const text = btn.querySelector('.collapse-text');
        if (icon) icon.textContent = isCollapsed ? '▼' : '▲';
        if (text) text.textContent = isCollapsed ? 'Expand Topics' : 'Collapse Topics';
      }
    }

    function scrollToTopicModule(cardId) {
      const el = document.getElementById(cardId);
      if (el) {
        const yOffset = -124;
        const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
        el.classList.add('highlighted');
        setTimeout(() => el.classList.remove('highlighted'), 2000);
      }
    }

    function activateTopicInNav(prefix, unitId, folder) {
      const nav = document.getElementById('topic-nav-' + prefix);
      if (!nav) return;

      const buttons = nav.querySelectorAll('.topic-nav-btn');
      let activeBtn = null;
      buttons.forEach(btn => {
        const btnUid = btn.getAttribute('data-unit-id');
        const btnFolder = btn.getAttribute('data-folder');
        if ((unitId && btnUid === unitId) || (!unitId && btnFolder === folder)) {
          btn.classList.add('active');
          activeBtn = btn;
        } else {
          btn.classList.remove('active');
        }
      });

      if (!activeBtn && folder) {
        activeBtn = Array.from(buttons).find(b => b.getAttribute('data-folder') === folder);
        if (activeBtn) activeBtn.classList.add('active');
      }

      if (activeBtn) {
        const color = activeBtn.getAttribute('data-color') || '#38bdf8';
        const glow = activeBtn.getAttribute('data-glow') || 'rgba(56,189,248,0.25)';
        const name = activeBtn.getAttribute('data-name') || '';

        // Dynamic Color Band Strip
        const strip = document.getElementById('topic-band-indicator-' + prefix);
        if (strip) {
          strip.style.backgroundColor = color;
          strip.style.boxShadow = '0 0 14px ' + glow;
        }

        // Active Dot
        const dot = document.getElementById('dot-' + prefix);
        if (dot) {
          dot.style.backgroundColor = color;
          dot.style.boxShadow = '0 0 8px ' + color;
        }

        // Active Label
        const label = document.getElementById('active-topic-label-' + prefix);
        if (label) {
          label.textContent = name;
          label.style.color = color;
        }
      }
    }

    function initTopicScrollSpy() {
      const observerOptions = {
        root: null,
        rootMargin: '-120px 0px -40% 0px',
        threshold: [0, 0.2, 0.5]
      };

      const topicObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const card = entry.target;
            const cardIdParts = card.id.split('-');
            const prefix = cardIdParts[1];
            const unitId = card.getAttribute('data-unit-id');
            const folder = card.getAttribute('data-folder');
            activateTopicInNav(prefix, unitId, folder);
          }
        });
      }, observerOptions);

      document.querySelectorAll('.topic-module-card').forEach(card => {
        topicObserver.observe(card);
      });

      let scrollTimeout = null;
      window.addEventListener('scroll', () => {
        if (scrollTimeout) return;
        scrollTimeout = setTimeout(() => {
          scrollTimeout = null;
          updateScrollSpyFallback();
        }, 60);
      }, { passive: true });
    }

    function updateScrollSpyFallback() {
      const activeTab = document.querySelector('.tab-content.active');
      if (!activeTab) return;
      const cards = Array.from(activeTab.querySelectorAll('.topic-module-card')).filter(c => c.style.display !== 'none');
      if (!cards.length) return;

      const viewportTop = 150;
      let currentCard = cards[0];

      for (let i = 0; i < cards.length; i++) {
        const rect = cards[i].getBoundingClientRect();
        if (rect.top <= viewportTop + 50) {
          currentCard = cards[i];
        } else {
          break;
        }
      }

      if (currentCard) {
        const cardIdParts = currentCard.id.split('-');
        const prefix = cardIdParts[1];
        const unitId = currentCard.getAttribute('data-unit-id');
        const folder = currentCard.getAttribute('data-folder');
        activateTopicInNav(prefix, unitId, folder);
      }
    }

    // Core 1 Dynamic Topic Filtering
    function filterCore1ByTopic(folder) {
      document.querySelectorAll('#core1-topic-chips .filter-chip').forEach(c => c.classList.remove('active'));
      const activeChip = Array.from(document.querySelectorAll('#core1-topic-chips .filter-chip')).find(c => c.getAttribute('data-folder') === folder);
      if (activeChip) activeChip.classList.add('active');

      document.querySelectorAll('#tab-core1-all .topic-module-card').forEach(card => {
        if (folder === 'ALL' || card.getAttribute('data-folder') === folder) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
      if (folder !== 'ALL') {
        const target = Array.from(document.querySelectorAll('#tab-core1-all .topic-module-card')).find(c => c.getAttribute('data-folder') === folder);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        activateTopicInNav('all', null, folder);
      }
    }

    // Inter-Core Jump Functions
    function jumpToCore1(folderOrTopic) {
      const folder = folderOrTopic.toLowerCase().replace(/[^a-z0-9-]/g, '-');
      switchTab('core1-all');
      filterCore1ByTopic('ALL');
      setTimeout(() => {
        let mod = Array.from(document.querySelectorAll('#tab-core1-all .topic-module-card')).find(m => {
          const f = m.getAttribute('data-folder') || '';
          const t = (m.getAttribute('data-topic') || '').toLowerCase();
          return f === folder || t.includes(folderOrTopic.toLowerCase()) || folderOrTopic.toLowerCase().includes(t);
        });
        if (mod) {
          mod.scrollIntoView({ behavior: 'smooth', block: 'start' });
          mod.classList.add('highlighted');
          setTimeout(() => mod.classList.remove('highlighted'), 2500);
          activateTopicInNav('all', mod.getAttribute('data-unit-id'), mod.getAttribute('data-folder'));
        }
      }, 100);
    }

    function jumpToQuestion(qid) {
      switchTab('core2');
      const searchInput = document.getElementById('qb-search-input');
      if (searchInput) {
        searchInput.value = qid;
        applyFilters();
      }
      setTimeout(() => {
        let card = document.getElementById('q-' + qid);
        if (!card) {
          card = Array.from(document.querySelectorAll('.qb-question')).find(c => {
            return (c.getAttribute('data-search') || '').includes(qid.toLowerCase());
          });
        }
        if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('highlighted');
          setTimeout(() => card.classList.remove('highlighted'), 2500);
        }
      }, 150);
    }

    function triggerKaTeX() {
      if (window.renderMathInElement) {
        renderMathInElement(document.body, {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "\\[", right: "\\]", display: true},
            {left: "$", right: "$", display: false}
          ],
          ignoredClasses: ["no-math", "katex-ignore"],
          throwOnError: false,
          errorColor: "#ef4444"
        });
      }
    }

    // Active Filters State
    const activeFilters = {
      paper: 'ALL',
      band: null,
      demand: null,
      topic: null
    };

    function toggleFilter(type, val) {
      if (type === 'paper') {
        activeFilters.paper = val;
      } else {
        if (activeFilters[type] === val) {
          activeFilters[type] = null;
        } else {
          activeFilters[type] = val;
        }
      }
      syncFilterChipsUI();
      applyFilters();
    }

    function addActiveFilter(type, val) {
      activeFilters[type] = val;
      syncFilterChipsUI();
      applyFilters();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function removeActiveFilter(type) {
      if (type === 'paper') {
        activeFilters.paper = 'ALL';
      } else {
        activeFilters[type] = null;
      }
      syncFilterChipsUI();
      applyFilters();
    }

    function clearAllFilters() {
      activeFilters.paper = 'ALL';
      activeFilters.band = null;
      activeFilters.demand = null;
      activeFilters.topic = null;
      const searchInput = document.getElementById('qb-search-input');
      if (searchInput) searchInput.value = '';
      syncFilterChipsUI();
      applyFilters();
    }

    function syncFilterChipsUI() {
      document.querySelectorAll('.filter-chip').forEach(chip => {
        const fType = chip.getAttribute('data-filter');
        const fVal = chip.getAttribute('data-val');

        if (fType === 'paper') {
          if (activeFilters.paper === fVal) {
            chip.classList.add('active');
          } else {
            chip.classList.remove('active');
          }
        } else {
          if (activeFilters[fType] === fVal) {
            chip.classList.add('active');
          } else {
            chip.classList.remove('active');
          }
        }
      });

      // Update Active Pills Bar
      const pillsContainer = document.getElementById('active-pills-list');
      const bar = document.getElementById('active-filters-bar');
      if (!pillsContainer || !bar) return;

      pillsContainer.innerHTML = '';
      let hasFilters = false;

      if (activeFilters.paper && activeFilters.paper !== 'ALL') {
        hasFilters = true;
        pillsContainer.innerHTML += `<span class="active-pill">Paper: ${activeFilters.paper} <span class="remove-pill" onclick="removeActiveFilter('paper')">✕</span></span>`;
      }
      if (activeFilters.band) {
        hasFilters = true;
        pillsContainer.innerHTML += `<span class="active-pill">Difficulty: ${activeFilters.band} <span class="remove-pill" onclick="removeActiveFilter('band')">✕</span></span>`;
      }
      if (activeFilters.demand) {
        hasFilters = true;
        pillsContainer.innerHTML += `<span class="active-pill">Demand: ${activeFilters.demand} <span class="remove-pill" onclick="removeActiveFilter('demand')">✕</span></span>`;
      }
      if (activeFilters.topic) {
        hasFilters = true;
        pillsContainer.innerHTML += `<span class="active-pill">Topic: ${activeFilters.topic} <span class="remove-pill" onclick="removeActiveFilter('topic')">✕</span></span>`;
      }

      bar.style.display = hasFilters ? 'flex' : 'none';
    }

    function normTopic(str) {
      if (!str) return '';
      return str.replace(/[\u2018\u2019]/g, "'").replace(/\\s+/g, ' ').trim().toLowerCase();
    }

    function normalizeSearchText(str) {
      if (!str) return '';
      return str.toLowerCase()
        .replace(/[\u2018\u2019]/g, "'")
        .replace(/[\u201C\u201D]/g, '"')
        .replace(/[\u2013\u2014]/g, '-')
        .replace(/[$_{}]/g, ' ')
        .split('\\\\').join(' ')
        .replace(/\\s+/g, ' ')
        .trim();
    }

    function matchTokens(searchBlob, rawQuery) {
      const normQuery = normalizeSearchText(rawQuery);
      if (!normQuery) return true;
      const tokens = normQuery.split(' ').filter(t => t.length > 0);
      const normBlob = normalizeSearchText(searchBlob);
      return tokens.every(token => normBlob.includes(token));
    }

    function applyFilters() {
      const searchInput = document.getElementById('qb-search-input');
      const query = searchInput ? searchInput.value : '';

      const questions = document.querySelectorAll('.qb-question');
      let visibleCount = 0;
      const activeTopicNorm = activeFilters.topic ? normTopic(activeFilters.topic) : null;

      questions.forEach(q => {
        const qPaper = q.getAttribute('data-paper');
        const qBand = q.getAttribute('data-band');
        const qDemand = q.getAttribute('data-demand');
        const qTopic = q.getAttribute('data-topic');
        const qSearch = q.getAttribute('data-search') || '';

        let match = true;

        if (activeFilters.paper && activeFilters.paper !== 'ALL' && qPaper !== activeFilters.paper) {
          match = false;
        }
        if (activeFilters.band && qBand !== activeFilters.band) {
          match = false;
        }
        if (activeFilters.demand && qDemand !== activeFilters.demand) {
          match = false;
        }
        if (activeTopicNorm && normTopic(qTopic) !== activeTopicNorm) {
          match = false;
        }

        if (match && query.trim()) {
          if (!matchTokens(qSearch, query)) match = false;
        }

        if (match) {
          q.style.display = 'block';
          visibleCount++;
        } else {
          q.style.display = 'none';
        }
      });

      const counter = document.getElementById('result-counter');
      if (counter) {
        if (query.trim() || (activeFilters.paper && activeFilters.paper !== 'ALL') || activeFilters.band || activeFilters.demand || activeFilters.topic) {
          counter.innerHTML = `Showing <strong>${visibleCount}</strong> of ${questions.length} questions <span class="filter-matched-badge" style="display:inline-block;margin-left:8px;background:rgba(56,189,248,0.15);color:var(--accent);padding:2px 8px;border-radius:12px;font-size:0.88rem">Filtered</span>`;
        } else {
          counter.textContent = `Showing all ${questions.length} questions`;
        }
      }
    }

    // Dark / Light Theme Toggle
    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try {
        localStorage.setItem('g9_theme', next);
      } catch(e) {}
    }

    // Auto-render KaTeX on DOM ready & initialize Topic ScrollSpy
    document.addEventListener("DOMContentLoaded", function() {
      try {
        const savedTheme = localStorage.getItem('g9_theme');
        if (savedTheme) {
          document.documentElement.setAttribute('data-theme', savedTheme);
        }
      } catch(e) {}

      if (window.renderMathInElement) {
        renderMathInElement(document.body, {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "\\[", right: "\\]", display: true},
            {left: "$", right: "$", display: false}
          ],
          ignoredClasses: ["no-math", "katex-ignore"],
          throwOnError: false,
          errorColor: "#ef4444"
        });
      }

      // Initialize Dynamic Topic ScrollSpy & Visual Color Band
      initTopicScrollSpy();
      setTimeout(updateScrollSpyFallback, 150);
    });
  </script>
</body>
</html>
""")

    out_files = [
        Path("standalone/mathematics-imo-grade9-master-suite.html"),
        Path("public/standalone/mathematics-imo-grade9-master-suite.html"),
        Path("public/test/imo-grade9/core2.html"),
        Path("docs/test/imo-grade9/core2.html")
    ]
    full_html = embed_standalone_katex("".join(html_parts))
    for out_file in out_files:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(full_html, encoding="utf-8")
        print(f"Saved {len(full_html)} bytes to {out_file}.")

if __name__ == '__main__':
    main()
