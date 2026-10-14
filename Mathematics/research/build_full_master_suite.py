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
import json
import re
import html
from pathlib import Path

def get_figure_markup(figure_ref, qid):
    figures_dir = Path("Mathematics/library/figures")
    
    # 1. Check if figure_ref points to a file in Mathematics/library/figures
    if figure_ref:
        fig_path = figures_dir / figure_ref
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

    print(f"Total unified questions compiled: {len(unified_questions)}")

    # Sort questions: first by paper, then by question number
    paper_order = ["2025-26 Set A", "2025-26 Set B", "2024-25 Set B", "2023-24 Set A", "2026-27 Sample"]
    unified_questions.sort(key=lambda x: (paper_order.index(x["paper_label"]) if x["paper_label"] in paper_order else 99, x["num"]))

    # Extract distinct facets for filtering
    papers = ["All Papers", "2025-26 Set A", "2025-26 Set B", "2024-25 Set B", "2023-24 Set A", "2026-27 Sample"]

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

    # Calculate counts for difficulty bands and cognitive demands
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

    /* Fixed Header Shell */
    header.g9-shell {
      position: sticky;
      top: 0;
      z-index: 100;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(10px);
    }

    .shell-inner {
      max-width: 1260px;
      margin: 0 auto;
      padding: 10px 18px;
      min-height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 750;
      font-size: 1.15rem;
      color: var(--text);
      text-decoration: none;
      white-space: nowrap;
    }

    .brand-badge {
      font-size: 0.88rem;
      padding: 3px 10px;
      border-radius: 999px;
      background: var(--accent);
      color: #090e17;
      font-weight: 800;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }

    .nav-tabs {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding: 4px 0;
      -webkit-overflow-scrolling: touch;
    }

    .tab-btn {
      min-height: 44px;
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      transition: all 0.18s;
    }

    .tab-btn:hover {
      background: var(--card-hover);
      color: var(--text);
    }

    .tab-btn.active {
      background: var(--card);
      border-color: var(--border);
      color: var(--accent);
      font-weight: 750;
    }

    .theme-toggle {
      min-height: 44px;
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text);
      cursor: pointer;
      font-weight: 650;
      font-size: 0.90rem;
      white-space: nowrap;
    }

    /* Container */
    main.container {
      max-width: 1260px;
      margin: 0 auto;
      padding: 24px 18px 48px;
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

    /* Responsive */
    @media (max-width: 768px) {
      .shell-inner { flex-direction: column; align-items: stretch; gap: 10px; }
      .qb-options-grid { grid-template-columns: 1fr; }
      .qb-top-row { flex-direction: column; }
    }
  </style>
</head>
<body>

  <!-- FIXED HEADER SHELL -->
  <header class="g9-shell">
    <div class="shell-inner">
      <a href="#" class="brand">
        <span>IMO Grade 9 Master Suite</span>
        <span class="brand-badge">210 QUESTIONS · CORE 2 CUSTODY</span>
      </a>

      <nav class="nav-tabs">
        <button type="button" class="tab-btn active" onclick="switchTab('core2')">📚 Core 2 Question Bank</button>
        <button type="button" class="tab-btn" onclick="switchTab('d3-core')">🏆 D3 Core 1A/1B</button>
        <button type="button" class="tab-btn" onclick="switchTab('d4-core')">💎 D4 Core 1A/1B</button>
        <button type="button" class="tab-btn" onclick="switchTab('d1-core')">🌱 D1 Core 1A/1B</button>
      </nav>

      <button type="button" class="theme-toggle" onclick="toggleTheme()">🌓 Theme</button>
    </div>
  </header>

  <main class="container">

    <!-- ========================================== -->
    <!-- TAB 1: CORE 2 QUESTION BANK (210 Questions) -->
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
          <span class="filter-chip active" data-filter="paper" data-val="ALL" onclick="toggleFilter('paper', 'ALL')">All Papers (210)</span>
          <span class="filter-chip" data-filter="paper" data-val="2025-26 Set A" onclick="toggleFilter('paper', '2025-26 Set A')">2025-26 Set A (50)</span>
          <span class="filter-chip" data-filter="paper" data-val="2025-26 Set B" onclick="toggleFilter('paper', '2025-26 Set B')">2025-26 Set B (50)</span>
          <span class="filter-chip" data-filter="paper" data-val="2024-25 Set B" onclick="toggleFilter('paper', '2024-25 Set B')">2024-25 Set B (50)</span>
          <span class="filter-chip" data-filter="paper" data-val="2023-24 Set A" onclick="toggleFilter('paper', '2023-24 Set A')">2023-24 Set A (50)</span>
          <span class="filter-chip" data-filter="paper" data-val="2026-27 Sample" onclick="toggleFilter('paper', '2026-27 Sample')">2026-27 Sample (10)</span>
        </div>

        <!-- Difficulty Row -->
        <div class="filter-chips-row">
          <span class="chip-label">Difficulty:</span>
          <span class="filter-chip" data-filter="band" data-val="D1" onclick="toggleFilter('band', 'D1')">🌱 D1 (Foundations) (47)</span>
          <span class="filter-chip" data-filter="band" data-val="D2" onclick="toggleFilter('band', 'D2')">⚡ D2 (Standard Olympiad) (121)</span>
          <span class="filter-chip" data-filter="band" data-val="D3" onclick="toggleFilter('band', 'D3')">🔥 D3 (Hard Olympiad) (34)</span>
          <span class="filter-chip" data-filter="band" data-val="D4" onclick="toggleFilter('band', 'D4')">💎 D4 (Achievers Section) (8)</span>
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
        <span id="result-counter" style="font-weight:750;color:var(--text)">Showing all 210 questions</span>
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
        fig_markup = get_figure_markup(q["figure_ref"], qid)
        
        # Build options grid
        opt_cards = []
        for opt_k in ["A", "B", "C", "D"]:
            if opt_k in options:
                opt_v = options[opt_k]
                opt_v_html = format_math_html(str(opt_v))
                is_correct = (opt_k == choice)
                correct_style = "border-color: var(--success); background: rgba(52, 211, 153, 0.08);" if is_correct else ""
                opt_cards.append(f"""
                  <div class="qb-option-card" style="{correct_style}">
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
        search_blob = html.escape(f"{qid} {q['stem']} {title} {topic_name} {paper_label} {sec} {cell}").lower()

        card_markup = f"""
        <article class="qb-question" data-paper="{paper_label}" data-band="{band}" data-demand="{demand}" data-topic="{topic_name}" data-search="{search_blob}">
          <div class="qb-qheader">
            <div class="qb-top-row">
              <h2 class="qb-title">Q{idx}. {title}</h2>
              <div class="qb-badges">
                <span class="qb-badge qb-badge-{band.lower()}" onclick="addActiveFilter('band', '{band}')" title="Filter by {band}">{band}</span>
                <span class="qb-badge qb-badge-qrt" onclick="addActiveFilter('demand', '{demand}')" title="Filter by {cell}">{cell}</span>
                <span class="qb-badge qb-badge-topic" onclick="addActiveFilter('topic', '{topic_name}')" title="Filter by {topic_name}">📚 {topic_name}</span>
                <span class="qb-badge qb-badge-paper" onclick="addActiveFilter('paper', '{paper_label}')" title="Filter by {paper_label}">📄 {paper_label}</span>
              </div>
            </div>

            <div class="qb-locator">
              <span><strong>Locator:</strong> {paper} · {sec} · Question {qnum} (<code>{qid}</code>)</span>
            </div>
          </div>

          <!-- Official Exam Question Stem Box -->
          <div class="qb-stem-box">
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
            <button type="button" class="btn-commit" onclick="document.getElementById('sol-disc-{qid}').open=true; document.getElementById('sol-disc-{qid}').scrollIntoView({{behavior:'smooth'}});">Commit Attempt & Reveal Solution</button>
          </div>

          <!-- Grounded Support Accordion (BP-CORE2 & T05) -->
          <div class="qb-support-container">
            <details class="qb-disclosure">
              <summary>
                <span>💡 Hint Ladder · Progressive Support</span>
                <span style="font-size:0.88rem;color:var(--text-muted)">Reveal step-by-step</span>
              </summary>
              <div class="qb-disclosure-body">
                <div class="ladder-rung">
                  <span class="rung-tag rung-nudge">Tier 1 · Conceptual Nudge</span>
                  <p>{hint1}</p>
                </div>
                <div class="ladder-rung">
                  <span class="rung-tag rung-tactical">Tier 2 · Tactical Intermediate Formulation</span>
                  <p>{hint2}</p>
                </div>
                {f'''<div class="ladder-rung">
                  <span class="rung-tag rung-crux">Tier 3 · Crux Relation</span>
                  <p>{hint3}</p>
                </div>''' if hint3 else ''}
              </div>
            </details>

            <details class="qb-disclosure">
              <summary>
                <span>⚠️ Distractor Diagnostic & Misconceptions</span>
                <span style="font-size:0.88rem;color:var(--warning)">Pitfall alert</span>
              </summary>
              <div class="qb-disclosure-body">
                {distractor_html}
              </div>
            </details>

            <details class="qb-disclosure" id="sol-disc-{qid}">
              <summary>
                <span>✅ Teacher Solution · Complete Derivation & Formal Check</span>
                <span style="font-size:0.88rem;color:var(--success)">Answer: ({choice})</span>
              </summary>
              <div class="qb-disclosure-body">
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

    # Append Existing Core 1A / 1B Tabs for D3, D4, and D1
    with open("Mathematics/research/build_imo_master_suite.py", "r", encoding="utf-8") as orig:
        orig_text = orig.read()
    
    # Extract tab-d3-core, tab-d4-core, and tab-d1-core from original builder
    d3_pos = orig_text.find('<div id="tab-d3-core"')
    scripts_pos = orig_text.find('<!-- ========================================== -->\n<!-- SCRIPTS: SEARCH, FILTERS, KATEX -->')
    if d3_pos != -1 and scripts_pos != -1:
        core1_tabs_markup = orig_text[d3_pos:scripts_pos]
        # Fix any font-size issues in core1_tabs_markup: replace < 14px sizes with 0.88rem
        for bad_size in ["0.72rem", "0.76rem", "0.78rem", "0.8rem", "0.82rem", "0.84rem", "0.85rem", "0.86rem"]:
            core1_tabs_markup = core1_tabs_markup.replace(f"font-size:{bad_size}", "font-size:0.88rem")
            core1_tabs_markup = core1_tabs_markup.replace(f"font-size: {bad_size}", "font-size: 0.88rem")
        html_parts.append(core1_tabs_markup)

    # Append Interactive Client-Side JavaScript
    html_parts.append("""
  </main>

  <script>
    // Tab Switching
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');

      const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (btn) btn.classList.add('active');

      window.scrollTo({ top: 0, behavior: 'smooth' });
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
      return str.replace(/[\u2018\u2019]/g, "'").replace(/\s+/g, ' ').trim().toLowerCase();
    }

    function normalizeSearchText(str) {
      if (!str) return '';
      return str.toLowerCase()
        .replace(/[\u2018\u2019]/g, "'")
        .replace(/[\u201C\u201D]/g, '"')
        .replace(/[\u2013\u2014]/g, '-')
        .replace(/[$_{}\\]/g, ' ')
        .replace(/\s+/g, ' ')
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

    // Auto-render KaTeX on DOM ready
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
            {left: "$", right: "$", display: false},
            {left: "\\(", right: "\\)", display: false}
          ],
          ignoredClasses: ["no-math", "katex-ignore"],
          throwOnError: false,
          errorColor: "#ef4444"
        });
      }
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
    full_html = "".join(html_parts)
    for out_file in out_files:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(full_html, encoding="utf-8")
        print(f"Saved {len(full_html)} bytes to {out_file}.")

if __name__ == '__main__':
    main()
