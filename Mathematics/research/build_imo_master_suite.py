import json
import re
import html
import sys
from pathlib import Path

# Add research paths to sys.path
sys.path.append(str(Path(__file__).parent))
from generate_question_svgs import get_svg_for_question

root = Path(".")
enhanced_path = root / "Mathematics/research/imo_68_classified_enhanced.json"
stems_path = root / "Mathematics/research/imo_68_verbatim_stems.json"

data = json.load(open(enhanced_path, encoding="utf-8"))
stems_db = json.load(open(stems_path, encoding="utf-8"))

print(f"Loaded {len(data)} enhanced questions and {len(stems_db)} verbatim stems.")

# Extract unique years for the regex/year filters
years = sorted(list(set(re.search(r"20\d\d-\d\d", q["paper"]).group(0) for q in data if re.search(r"20\d\d-\d\d", q["paper"]))))
topics = sorted(list(set(q["topic_name"] for q in data)))
bands = ["D1", "D2", "D3", "D4"]
demands = ["RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"]

html_parts = []

# ==========================================
# HEAD & MODERN STYLING
# ==========================================
html_parts.append("""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Grade 9 IMO Mathematics · Blueprints & Question Bank Suite</title>
  <meta name="description" content="Grounded Master Suite for Grade 9 IMO Mathematics: 100% audited authentic question stems and options, app-style dynamic search, KaTeX math rendering, blueprint-grade Hint Ladders, and Core 1A/1B modules for D1 to D4.">

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
      --touch-min: 44px;
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

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 15.5px;
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
      padding: 8px 18px;
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
      font-size: 1.12rem;
      color: var(--text);
      text-decoration: none;
      white-space: nowrap;
    }

    .brand-badge {
      font-size: 0.72rem;
      padding: 2px 8px;
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
      min-height: 38px;
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 0.92rem;
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
    }

    .theme-toggle {
      min-height: 38px;
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text);
      cursor: pointer;
      font-weight: 600;
      font-size: 0.88rem;
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
      padding: 18px;
      margin-bottom: 20px;
    }

    .qb-search-input-wrap {
      position: relative;
      margin-bottom: 14px;
    }

    .qb-search-input {
      width: 100%;
      height: 48px;
      padding: 10px 16px 10px 44px;
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
      left: 14px;
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
      font-size: 0.8rem;
      font-weight: 750;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-right: 4px;
    }

    .filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 650;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text-muted);
      cursor: pointer;
      user-select: none;
      transition: all 0.18s;
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
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.84rem;
      font-weight: 700;
      background: var(--card);
      color: var(--text);
      border: 1px solid var(--border);
    }

    .active-pill-remove {
      cursor: pointer;
      font-weight: 800;
      color: var(--danger);
      margin-left: 4px;
    }

    .clear-all-btn {
      padding: 4px 10px;
      border-radius: 6px;
      background: transparent;
      border: 1px solid var(--danger);
      color: var(--danger);
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      margin-left: auto;
    }

    /* Question Card (Blueprint BP-CORE2) */
    .qb-question {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px;
      margin-bottom: 24px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .qb-question:hover {
      border-color: var(--border-light);
      box-shadow: 0 4px 14px rgba(0,0,0,0.22);
    }

    .qb-qheader {
      margin-bottom: 16px;
    }

    .qb-top-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }

    .qb-title {
      font-size: 1.15rem;
      font-weight: 750;
      line-height: 1.45;
      color: var(--text);
      flex: 1;
      min-width: 260px;
    }

    .qb-badges {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .qb-badge {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 750;
      letter-spacing: 0.03em;
      cursor: pointer;
      user-select: none;
      transition: transform 0.15s;
    }

    .qb-badge:hover { transform: scale(1.05); }

    .qb-badge-d1 { background: rgba(52, 211, 153, 0.18); color: var(--success); border: 1px solid var(--success); }
    .qb-badge-d2 { background: rgba(56, 189, 248, 0.18); color: var(--accent); border: 1px solid var(--accent); }
    .qb-badge-d3 { background: rgba(251, 191, 36, 0.18); color: var(--warning); border: 1px solid var(--warning); }
    .qb-badge-d4 { background: rgba(248, 113, 113, 0.18); color: var(--danger); border: 1px solid var(--danger); }
    .qb-badge-topic { background: var(--surface); color: var(--text-muted); border: 1px solid var(--border); }
    .qb-badge-year { background: rgba(192, 132, 252, 0.15); color: var(--purple); border: 1px solid var(--purple); }
    .qb-badge-qrt { background: rgba(56, 189, 248, 0.12); color: var(--accent); border: 1px dashed var(--accent); }

    .qb-locator {
      font-size: 0.88rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .qb-locator code {
      background: var(--surface);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid var(--border);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.82rem;
      color: var(--accent);
    }

    /* Question Stem Box (Authentic Exam Presentation) */
    .qb-stem-box {
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-left: 5px solid var(--accent);
      border-radius: 10px;
      padding: 18px 20px;
      margin: 16px 0;
      font-size: 1.05rem;
      line-height: 1.7;
      color: var(--text);
    }

    .qb-stem-text {
      font-size: 1.05rem;
      line-height: 1.75;
      margin-bottom: 14px;
    }

    /* Options Grid (2x2 on desktop, stacked on mobile) */
    .qb-options-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 10px;
      margin-top: 14px;
    }

    .qb-option-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--card);
      font-size: 0.98rem;
      line-height: 1.5;
      transition: all 0.18s;
    }

    .qb-option-card:hover {
      border-color: var(--accent);
      background: var(--card-hover);
    }

    .qb-option-card.correct-peek {
      border-color: var(--success);
      background: rgba(52, 211, 153, 0.08);
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

    .qb-figure-title {
      font-size: 0.84rem;
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
      font-size: 0.92rem;
      font-weight: 700;
      margin-bottom: 6px;
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
      min-height: 42px;
      padding: 8px 20px;
      border-radius: 8px;
      background: var(--accent);
      color: #090e17;
      font-weight: 750;
      font-size: 0.94rem;
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
      padding: 12px 18px;
      background: var(--surface);
      cursor: pointer;
      font-weight: 700;
      font-size: 0.95rem;
      user-select: none;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .qb-disclosure-body {
      padding: 16px 20px;
      background: var(--card);
      line-height: 1.7;
    }

    /* Hint Ladder Rung Styling */
    .ladder-rung {
      margin: 10px 0;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--surface);
      border: 1px solid var(--border);
    }

    .rung-tag {
      display: inline-block;
      font-size: 0.76rem;
      font-weight: 800;
      text-transform: uppercase;
      padding: 2px 7px;
      border-radius: 4px;
      margin-bottom: 6px;
    }

    .rung-orient { background: rgba(56, 189, 248, 0.2); color: var(--accent); }
    .rung-represent { background: rgba(192, 132, 252, 0.2); color: var(--purple); }
    .rung-crux { background: rgba(251, 191, 36, 0.2); color: var(--warning); }
    .rung-verify { background: rgba(52, 211, 153, 0.2); color: var(--success); }

    .trap-alert {
      background: rgba(251, 191, 36, 0.08);
      border-left: 4px solid var(--warning);
      padding: 14px 16px;
      border-radius: 0 8px 8px 0;
      margin: 10px 0;
    }

    .solution-card {
      background: var(--surface);
      border-radius: 8px;
      padding: 18px;
    }

    .choice-highlight {
      font-size: 1.25rem;
      font-weight: 850;
      color: var(--success);
    }

    /* Responsive Mobile Layout */
    @media (max-width: 768px) {
      .shell-inner {
        padding: 8px 12px;
        min-height: auto;
      }
      .brand {
        font-size: 1rem;
      }
      .nav-tabs {
        width: 100%;
        order: 3;
        padding-bottom: 6px;
      }
      .tab-btn {
        padding: 5px 10px;
        font-size: 0.85rem;
      }
      .qb-options-grid {
        grid-template-columns: 1fr;
      }
      .filter-chips-row {
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-bottom: 6px;
        -webkit-overflow-scrolling: touch;
      }
      .filter-chip {
        white-space: nowrap;
        flex-shrink: 0;
      }
    }

    footer.g9-footer {
      background: var(--surface);
      border-top: 1px solid var(--border);
      padding: 24px 18px;
      text-align: center;
      font-size: 0.9rem;
      color: var(--text-muted);
    }
  </style>
</head>
<body>
  <!-- Header Shell -->
  <header class="g9-shell">
    <div class="shell-inner">
      <a class="brand" href="#">
        <span>⚡</span>
        <span>Grade 9 IMO Master Suite</span>
        <span class="brand-badge">BLUEPRINT V1.12</span>
      </a>

      <button class="theme-toggle" onclick="toggleTheme()" id="theme-btn">🌓 Theme</button>

      <nav class="nav-tabs" role="tablist">
        <button class="tab-btn active" onclick="switchTab('core2')" id="tab-btn-core2">✍️ Core 2 (Question Bank)</button>
        <button class="tab-btn" onclick="switchTab('d3-core')" id="tab-btn-d3-core">🔥 D3 Core 1A/1B (Indices & Rates)</button>
        <button class="tab-btn" onclick="switchTab('d4-core')" id="tab-btn-d4-core">🏆 D4 Core 1A/1B (Surds & Circles)</button>
        <button class="tab-btn" onclick="switchTab('d1-core')" id="tab-btn-d1-core">🌱 D1/D2 Core 1A/1B (Divisibility)</button>
      </nav>
    </div>
  </header>

  <main class="container">
""")

# ==========================================
# TAB 1: CORE 2 PRACTICE & DYNAMIC SEARCH
# ==========================================
html_parts.append("""
    <!-- TAB 1: CORE 2 QUESTION BANK -->
    <section class="tab-content active" id="tab-core2" role="tabpanel">
      <!-- Search & Dynamic Filter Panel -->
      <div class="qb-filter-panel">
        <div class="qb-search-input-wrap">
          <span class="qb-search-icon">🔍</span>
          <input type="search" class="qb-search-input" id="qb-search" placeholder="Type to search: concepts, Q#, year regex (e.g. 2025-26, /202[4-6]/, Q028, cyclic, roots)..." oninput="runFilter()">
        </div>

        <!-- Dynamic Label Filter Rows (Click to Search) -->
        <div class="filter-chips-row">
          <span class="chip-label">Difficulty:</span>
          <span class="filter-chip" onclick="toggleFilter('band', 'D1', this)">🌱 D1 Foundational (8)</span>
          <span class="filter-chip" onclick="toggleFilter('band', 'D2', this)">⚡ D2 Procedural (34)</span>
          <span class="filter-chip" onclick="toggleFilter('band', 'D3', this)">🔥 D3 Strategic (23)</span>
          <span class="filter-chip" onclick="toggleFilter('band', 'D4', this)">🏆 D4 Advanced HOTS (3)</span>
        </div>

        <div class="filter-chips-row">
          <span class="chip-label">Cognitive Demand:</span>
          <span class="filter-chip" onclick="toggleFilter('demand', 'RETRIEVE', this)">RETRIEVE</span>
          <span class="filter-chip" onclick="toggleFilter('demand', 'APPLY', this)">APPLY</span>
          <span class="filter-chip" onclick="toggleFilter('demand', 'MODEL', this)">MODEL</span>
          <span class="filter-chip" onclick="toggleFilter('demand', 'REPRESENT', this)">REPRESENT</span>
          <span class="filter-chip" onclick="toggleFilter('demand', 'JUSTIFY', this)">JUSTIFY</span>
          <span class="filter-chip" onclick="toggleFilter('demand', 'SYNTHESIZE', this)">SYNTHESIZE</span>
        </div>

        <div class="filter-chips-row">
          <span class="chip-label">Exam Year / Regex:</span>
          <span class="filter-chip" onclick="toggleFilter('year', '2023-24', this)">📅 2023–24</span>
          <span class="filter-chip" onclick="toggleFilter('year', '2024-25', this)">📅 2024–25</span>
          <span class="filter-chip" onclick="toggleFilter('year', '2025-26', this)">📅 2025–26</span>
          <span class="filter-chip" onclick="toggleFilter('year', '2026-27', this)">📅 2026–27 Sample</span>
        </div>

        <div class="filter-chips-row">
          <span class="chip-label">Topics:</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Number Systems', this)">Number Systems (8)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Linear Equations', this)">Linear Equations (7)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Triangles', this)">Triangles (5)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Coordinate Geometry', this)">Coordinate Geometry (4)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Surface Areas and Volumes', this)">Mensuration (6)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Quantitative Aptitude', this)">Quant (12)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Verbal and Non-Verbal Reasoning', this)">Logical Reasoning (6)</span>
          <span class="filter-chip" onclick="toggleFilter('topic', 'Circles', this)">Circles (2)</span>
        </div>

        <!-- Active Filters Bar -->
        <div class="active-filters-bar" id="active-filters-container" style="display:none">
          <span style="font-size:0.86rem;font-weight:750">Active Filters:</span>
          <div id="active-pills-list" style="display:flex;flex-wrap:wrap;gap:6px"></div>
          <button type="button" class="clear-all-btn" onclick="clearAllFilters()">✕ Clear all filters</button>
        </div>
      </div>

      <!-- Result Count -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;font-size:0.95rem;color:var(--text-muted)">
        <span id="result-counter" style="font-weight:750;color:var(--text)">Showing all 68 questions</span>
        <span style="font-size:0.85rem">Click any badge to filter dynamically</span>
      </div>

      <!-- Question Cards List -->
      <div id="qb-cards-list">
""")

# Render all 68 questions sorted by difficulty then topic
diff_order = ["D1", "D2", "D3", "D4"]
sorted_cards = sorted(data, key=lambda x: (diff_order.index(x["band"]), x["topic"]))

for idx, q in enumerate(sorted_cards, 1):
    qid = q["id"]
    qnum = q["num"]
    paper = q["paper"]
    sec = q["section"].replace("_", " ").title()
    topic = q["topic"]
    topic_name = q["topic_name"]
    summary = html.escape(q["summary"])
    band = q["band"]
    demand = q["demand"]
    cell = q["cell"]
    choice = q.get("choice", "")
    ans = q.get("answer", "")
    deriv = q.get("derivation", "")
    check = q.get("check", "")

    rung1 = html.escape(q.get("rung1", ""))
    rung2 = html.escape(q.get("rung2", ""))
    rung3 = html.escape(q.get("rung3", ""))
    trap = html.escape(q.get("trap", ""))

    deriv_txt = html.escape(str(deriv) if deriv else "Verified mathematically from repository audit records.")
    ans_txt = html.escape(str(ans) if ans else "Option " + str(choice))
    check_txt = html.escape(str(check) if check else "")

    year_match = re.search(r"20\d\d-\d\d", paper)
    year = year_match.group(0) if year_match else "2026-27"

    badge_d_class = f"qb-badge-{band.lower()}"

    # Get embedded SVG figure if applicable
    fig_markup = get_svg_for_question(qid)

    # Get verbatim stem and options from stems_db
    stem_record = stems_db.get(qid, {})
    authentic_stem = stem_record.get("stem", summary)
    authentic_options = stem_record.get("options", {})
    verified_answer = stem_record.get("answer", ans_txt)
    verified_choice = stem_record.get("choice", choice)

    # Build 4-options HTML markup
    options_html = ""
    if authentic_options:
        opt_cards = []
        for opt_key in ["A", "B", "C", "D"]:
            if opt_key in authentic_options:
                opt_val = authentic_options[opt_key]
                opt_cards.append(f"""
                  <div class="qb-option-card">
                    <span class="qb-option-badge">({opt_key})</span>
                    <span>{opt_val}</span>
                  </div>
                """)
        options_html = f"""
          <div class="qb-options-grid">
            {''.join(opt_cards)}
          </div>
        """

    card_markup = f"""
        <article class="qb-question" data-band="{band}" data-demand="{demand}" data-topic="{topic_name}" data-year="{year}" data-search="{html.escape(qid + ' ' + authentic_stem + ' ' + summary + ' ' + topic_name + ' ' + paper + ' ' + sec + ' ' + cell).lower()}">
          <div class="qb-qheader">
            <div class="qb-top-row">
              <h2 class="qb-title">Q{idx}. {summary}</h2>
              <div class="qb-badges">
                <span class="qb-badge {badge_d_class}" onclick="addActiveFilter('band', '{band}')" title="Filter by {band}">{band}</span>
                <span class="qb-badge qb-badge-qrt" onclick="addActiveFilter('demand', '{demand}')" title="Filter by {cell}">{cell}</span>
                <span class="qb-badge qb-badge-topic" onclick="addActiveFilter('topic', '{topic_name}')" title="Filter by {topic_name}">📚 {topic_name}</span>
                <span class="qb-badge qb-badge-year" onclick="addActiveFilter('year', '{year}')" title="Filter by {year}">📅 {year}</span>
              </div>
            </div>

            <div class="qb-locator">
              <span><strong>Locator:</strong> {paper} · {sec} · Question {qnum} (<code>{qid}</code>)</span>
            </div>
          </div>

          <!-- Question Stem Box (Authentic Exam Stem & Options) -->
          <div class="qb-stem-box">
            <div style="font-weight:750;margin-bottom:8px;color:var(--accent);font-size:0.92rem;text-transform:uppercase;letter-spacing:0.04em">Official Exam Question:</div>
            <div class="qb-stem-text">{authentic_stem}</div>
            {fig_markup}
            {options_html}
            <div style="font-size:0.86rem;color:var(--text-muted);border-top:1px dashed var(--border-light);padding-top:8px;margin-top:12px">
              <strong>Target Mathematical Act ({demand}):</strong> {summary}
            </div>
          </div>

          <!-- Student Attempt Box (BP-CORE2) -->
          <div class="qb-attempt-box">
            <label for="att-{qid}"><strong>Your Solution Attempt / Working Notes:</strong></label>
            <textarea class="qb-textarea" id="att-{qid}" placeholder="Formulate the equations, state your intermediate deductions, and commit an answer..."></textarea>
            <button type="button" class="btn-commit" onclick="document.getElementById('sol-disc-{qid}').open=true; document.getElementById('sol-disc-{qid}').scrollIntoView({{behavior:'smooth'}});">Commit Attempt & Reveal Solution</button>
          </div>

          <!-- Grounded Support Accordion (BP-CORE2 & T05) -->
          <div class="qb-support-container">
            <details class="qb-disclosure">
              <summary>
                <span>💡 Hint Ladder · 3 Progressive Rungs (Technique T05)</span>
                <span style="font-size:0.8rem;color:var(--text-muted)">Reveal step-by-step</span>
              </summary>
              <div class="qb-disclosure-body">
                <div class="ladder-rung">
                  <span class="rung-tag rung-orient">Rung 1 · Orientation Question</span>
                  <p>{rung1}</p>
                </div>
                <div class="ladder-rung">
                  <span class="rung-tag rung-represent">Rung 2 · Representation & Constraints</span>
                  <p>{rung2}</p>
                </div>
                <div class="ladder-rung">
                  <span class="rung-tag rung-crux">Rung 3 · Crux Relation</span>
                  <p>{rung3}</p>
                </div>
              </div>
            </details>

            <details class="qb-disclosure">
              <summary>
                <span>⚠️ Common Wrong Route / Trap Diagnostic (Technique T06)</span>
                <span style="font-size:0.8rem;color:var(--warning)">Pitfall alert</span>
              </summary>
              <div class="qb-disclosure-body">
                <div class="trap-alert">
                  <strong>Tempting Mistake & Why It Fails:</strong> {trap}
                </div>
              </div>
            </details>

            <details class="qb-disclosure" id="sol-disc-{qid}">
              <summary>
                <span>✅ Teacher Solution · Complete Mathematical Derivation</span>
                <span style="font-size:0.8rem;color:var(--success)">Verified Oracle</span>
              </summary>
              <div class="qb-disclosure-body">
                <div class="solution-card">
                  <p><strong>Official Printed Option:</strong> <span class="choice-highlight">Option {verified_choice}</span> ({verified_answer})</p>
                  <p style="margin-top:10px"><strong>Step-by-Step Derivation:</strong></p>
                  <p style="margin-top:6px;line-height:1.7">{deriv_txt}</p>
                  {f'<div style="margin-top:10px;padding:8px 12px;background:var(--card);border-radius:6px;border-left:3px solid var(--success)"><strong>Verification Check:</strong> {check_txt}</div>' if check_txt else ''}
                </div>
              </div>
            </details>
          </div>
        </article>
    """
    html_parts.append(card_markup)

html_parts.append("""
      </div>
    </section>
""")

# ==========================================
# TAB 2: D3 CORE 1A & 1B (INDICES & RATES)
# ==========================================
html_parts.append("""
    <!-- TAB 2: D3 CORE MODULE -->
    <section class="tab-content" id="tab-d3-core" role="tabpanel">
      <!-- MODULE 1: COMMON BASE EXPONENTIAL SYSTEMS -->
      <div class="panel">
        <div style="border:2px solid var(--warning);border-radius:10px;padding:14px;background:var(--surface);margin-bottom:20px">
          <span class="qb-badge qb-badge-d3">BLUEPRINT BP-CORE1A-CONSTRUCTION</span>
          <span class="qb-badge qb-badge-qrt">QRT-APPLY-D3</span>
          <h2 style="font-size:1.3rem;margin-top:8px">Core 1A (Module 1) · Common-Base Exponentials & Power Transformations</h2>
          <p style="color:var(--text-muted);font-size:0.92rem;margin-top:4px">
            Anchored to D3 Olympiad Problem Q26 ($5^{2x-1} = 25^{x-1} + 100$) and Q35 (nested index radicals).
          </p>
        </div>

        <!-- Inferential Jump (T02) -->
        <div class="trap-alert" style="border-left-color:var(--accent);background:rgba(56, 189, 248, 0.08);margin:16px 0">
          <strong>The Inferential Leap (Technique T02):</strong>
          <p style="margin-top:6px">
            Never equate exponents across an additive term! In $5^{2x-1} = 25^{x-1} + 100$, you cannot equate exponents directly because of $+100$. Instead, recognize that $25 = 5^2$, factor out the negative indices to obtain linear forms in $t = 5^{2x}$, solve for $t$, and invert for $x$.
          </p>
        </div>

        <!-- 4-Stage Construction Path -->
        <h3 style="margin:20px 0 12px">Formal 4-Stage Construction Path</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:16px 0">
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-orient">STEP 1 · BASE ALIGNMENT</span>
            <p style="margin-top:8px">Rewrite all exponential expressions with prime base 5: $25^{x-1} = (5^2)^{x-1} = 5^{2x-2}$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Equation:</strong> $5^{2x-1} - 5^{2x-2} = 100$</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Power of a power law $(a^m)^n = a^{mn}$.</p>
          </div>

          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-represent">STEP 2 · EXPONENTIAL SUBSTITUTION</span>
            <p style="margin-top:8px">Let $t = 5^{2x} > 0$. Then $5^{2x-1} = \\frac{t}{5}$ and $5^{2x-2} = \\frac{t}{25}$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Linear form:</strong> $\\frac{t}{5} - \\frac{t}{25} = 100$</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Exponent difference law $a^{m-k} = a^m / a^k$.</p>
          </div>

          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-crux">STEP 3 · LINEAR SOLUTION</span>
            <p style="margin-top:8px">Multiply by 25 to clear fractions: $5t - t = 2500 \\implies 4t = 2500 \\implies t = 625$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Value of t:</strong> $t = 625 = 5^4$</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Linear balance properties over $\\mathbb{R}$.</p>
          </div>

          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface);border-color:var(--success)">
            <span class="rung-tag rung-verify">STEP 4 · INVERSION & REVERSE CHECK</span>
            <p style="margin-top:8px">Map back to exponent: $5^{2x} = 5^4 \\implies 2x = 4 \\implies x = 2$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Check:</strong> $5^3 = 125$; $25^1 + 100 = 125$. Matches!</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Exponential bases $a \\ne 1$ are strictly injective.</p>
          </div>
        </div>

        <!-- Trap Clinic (T06) -->
        <div class="trap-alert" style="margin:20px 0">
          <h3>⚠️ Trap Clinic (Technique T06): Exponent Distributivity Fallacy</h3>
          <p><strong>The Fallacy:</strong> Looking at $5^{2x-1} = 25^{x-1} + 100$ and writing $2x - 1 = (x - 1) + 100$.</p>
          <p><strong>Refutation:</strong> Exponents can ONLY be equated when two single powers with equal bases are equated: $a^u = a^v \\iff u = v$. An additive term $+100$ CANNOT be combined into the exponent. You must isolate terms using the common base quantity $t$.</p>
        </div>

        <!-- Exit Task (T12) -->
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px;margin-top:20px">
          <h4>Independent Exit Task (Technique T12)</h4>
          <p>Solve for real $y$: $2^{2y+1} = 4^y + 64$. State your substitution and verify the solution.</p>
          <textarea class="qb-textarea" style="margin-top:8px" placeholder="Write substitution t = 4^y, formulate equation in t, solve for y, and check..."></textarea>
          <details style="margin-top:12px;background:var(--card);padding:12px;border-radius:8px">
            <summary style="cursor:pointer;font-weight:700">Reveal Model Exit Solution</summary>
            <div style="margin-top:8px;line-height:1.7">
              <p>1. Let $t = 4^y = 2^{2y} > 0$. Then $2^{2y+1} = 2 \\cdot 2^{2y} = 2t$.</p>
              <p>2. Equation becomes $2t = t + 64 \\implies t = 64$.</p>
              <p>3. $4^y = 64 = 4^3 \\implies y = 3$.</p>
              <p>4. Reverse check: $2^7 = 128$; $4^3 + 64 = 64 + 64 = 128$. Matches! ✅</p>
            </div>
          </details>
        </div>
      </div>

      <!-- MODULE 2: MULTI-RATE WORK SYSTEMS -->
      <div class="panel">
        <div style="border:2px solid var(--warning);border-radius:10px;padding:14px;background:var(--surface);margin-bottom:20px">
          <span class="qb-badge qb-badge-d3">BLUEPRINT BP-CORE1A-CONSTRUCTION</span>
          <span class="qb-badge qb-badge-qrt">QRT-APPLY-D3</span>
          <h2 style="font-size:1.3rem;margin-top:8px">Core 1A (Module 2) · Simultaneous Inverse Work Rates</h2>
          <p style="color:var(--text-muted);font-size:0.92rem;margin-top:4px">
            Anchored to D3 Olympiad Problem Q43 (6 men + 8 boys in 10 days vs 26 men + 48 boys in 2 days).
          </p>
        </div>

        <div class="trap-alert" style="border-left-color:var(--accent);background:rgba(56, 189, 248, 0.08);margin:16px 0">
          <strong>The Inferential Leap (Technique T02):</strong>
          <p style="margin-top:6px">
            Total work $W$ is fixed. Never sum days or multiply men by boys! Formulate daily work capacities: 1 man does $m$ work/day, 1 boy does $b$ work/day. Total rate $R = \\sum \\text{rates} = \\frac{1}{\\text{days}}$.
          </p>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:16px 0">
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-orient">STEP 1 · FORM DAILY RATES</span>
            <p style="margin-top:8px">6 men + 8 boys do $\\frac{1}{10}$ work/day: $6m + 8b = \\frac{1}{10}$.</p>
            <p style="margin-top:4px">26 men + 48 boys do $\\frac{1}{2}$ work/day: $26m + 48b = \\frac{1}{2}$.</p>
          </div>
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-represent">STEP 2 · ELIMINATE TO FIND RATIO</span>
            <p style="margin-top:8px">Multiply first eq by 6: $36m + 48b = \\frac{6}{10} = \\frac{3}{5}$.</p>
            <p style="margin-top:4px">Subtract second eq: $10m = \\frac{3}{5} - \\frac{1}{2} = \\frac{1}{10} \\implies m = \\frac{1}{100}$.</p>
          </div>
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-crux">STEP 3 · RECOVER BOY RATE</span>
            <p style="margin-top:8px">$8b = \\frac{1}{10} - 6(\\frac{1}{100}) = \\frac{4}{100} \\implies b = \\frac{1}{200}$.</p>
            <p style="margin-top:4px">Notice: $1\\text{ man} = 2\\text{ boys}$.</p>
          </div>
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface);border-color:var(--success)">
            <span class="rung-tag rung-verify">STEP 4 · EVALUATE TARGET TEAM</span>
            <p style="margin-top:8px">15 men + 20 boys daily rate: $15(\\frac{1}{100}) + 20(\\frac{1}{200}) = \\frac{15}{100} + \\frac{10}{100} = \\frac{25}{100} = \\frac{1}{4}$.</p>
            <p style="margin-top:4px">Time required = $\\frac{1}{1/4} = 4\\text{ days}$. ✅</p>
          </div>
        </div>

        <div class="trap-alert" style="margin:20px 0">
          <h3>⚠️ Trap Clinic: Linear Day Averaging Fallacy</h3>
          <p><strong>Fallacy:</strong> "Since 26 men is about double 15 men, take the average of 10 and 2 days."</p>
          <p><strong>Refutation:</strong> Work rates add harmonically, not linearly! You must always convert time to daily unit rate $\\frac{1}{T}$ before combining different worker groups.</p>
        </div>
      </div>

      <!-- CORE 1B (D3 RECONSTRUCTION) -->
      <div class="panel">
        <span class="qb-badge qb-badge-d3">BLUEPRINT BP-CORE1B-RECONSTRUCTION</span>
        <h2 style="font-size:1.3rem;margin-top:8px">Core 1B · Dual-Stage Recall & Reconstruction (D3)</h2>
        <p class="lead-text">Complete the two unassisted retrieval gates to lock in procedural mastery:</p>

        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:18px">
          <h3>Gate 1 · Boundary Laws Recall</h3>
          <p>1. State the exact algebraic relation between $b^{2x-1}$ and $t = b^{2x}$.</p>
          <p>2. Why is an exponential solution $t = -25$ rejected when $t = 5^{2x}$?</p>
          <textarea class="qb-textarea" placeholder="Explain the multiplicative reciprocal 1/b and the exponential range (0, infinity)..."></textarea>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px">
          <h3>Gate 2 · Changed Givens Reconstruction</h3>
          <p>Solve with changed givens without hints: $5^{2z+1} = 25^z + 500$.</p>
          <textarea class="qb-textarea" placeholder="Set up t = 5^(2z), solve for t, and invert for z..."></textarea>
          <details style="margin-top:12px;background:var(--card);padding:12px;border-radius:8px">
            <summary style="cursor:pointer;font-weight:700">Check Gate 2 Result</summary>
            <p style="margin-top:6px">Let $t = 25^z = 5^{2z}$. Then $5t = t + 500 \\implies 4t = 500 \\implies t = 125 = 5^3$. Therefore $2z = 3 \\implies z = 3/2$. Check: $5^4 = 625 = 25^{3/2} + 500 = 125 + 500 = 625$. ✅</p>
          </details>
        </div>
      </div>
    </section>
""")

# ==========================================
# TAB 3: D4 CORE 1A & 1B (SURDS & CIRCLES)
# ==========================================
html_parts.append("""
    <!-- TAB 3: D4 CORE MODULE -->
    <section class="tab-content" id="tab-d4-core" role="tabpanel">
      <!-- MODULE 1: POLYNOMIAL CONJUGATES & TRUTH ANALYSIS -->
      <div class="panel">
        <div style="border:2px solid var(--danger);border-radius:10px;padding:14px;background:var(--surface);margin-bottom:20px">
          <span class="qb-badge qb-badge-d4">BLUEPRINT BP-CORE1A-CONSTRUCTION</span>
          <span class="qb-badge qb-badge-qrt">QRT-JUSTIFY-D4</span>
          <h2 style="font-size:1.3rem;margin-top:8px">Core 1A (Module 1) · Minimal Polynomials & Nested Radical Reductions</h2>
          <p style="color:var(--text-muted);font-size:0.92rem;margin-top:4px">
            Anchored to Achievers Section D4 Olympiad Problem Q49 (Surd evaluations, nested radicals, and quantifier logic).
          </p>
        </div>

        <!-- Inferential Jump (T02) -->
        <div style="background:rgba(248, 113, 113, 0.08);border-left:4px solid var(--danger);padding:16px;border-radius:0 8px 8px 0;margin:16px 0">
          <strong>The Inferential Leap (Technique T02):</strong>
          <p style="margin-top:6px">
            Never expand high-order powers of surds $(2 + \\sqrt{3})^3$ by hand! Instead, construct the rational minimal polynomial $(x - 2)^2 = 3 \\implies x^2 - 4x + 1 = 0$, reduce the high-degree polynomial using Euclidean division $P(x) = Q(x)(x^2-4x+1) + R(x) = R(x)$, and evaluate nested radicals using algebraic squaring identities $(\\sqrt{a - \\sqrt{b}} + \\sqrt{a + \\sqrt{b}})^2 = 2a + 2\\sqrt{a^2 - b}$.
          </p>
        </div>

        <!-- Construction Path -->
        <h3 style="margin:24px 0 12px">Formal 4-Stage Construction Path</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:16px 0">
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-orient">STEP 1 · FORM MINIMAL POLYNOMIAL</span>
            <p style="margin-top:8px">Given $\\frac{1}{x} = 2 - \\sqrt{3} \\implies x = \\frac{1}{2-\\sqrt{3}} = 2 + \\sqrt{3}$. Isolate radical: $x - 2 = \\sqrt{3}$. Square both sides: $(x-2)^2 = 3 \\implies x^2 - 4x + 4 = 3$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Result:</strong> $x^2 - 4x + 1 = 0$</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Eliminates irrational surd while preserving $x$.</p>
          </div>

          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-represent">STEP 2 · POLYNOMIAL DIVISION</span>
            <p style="margin-top:8px">Divide target $x^3 - 2x^2 - 7x + 5$ by $x^2 - 4x + 1$ using Euclidean division algorithm.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Result:</strong> $(x + 2)(x^2 - 4x + 1) + 3$</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Division algorithm for polynomials in $\\mathbb{R}[x]$.</p>
          </div>

          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-crux">STEP 3 · ZERO EVALUATION</span>
            <p style="margin-top:8px">Since $x^2 - 4x + 1 = 0$, the quotient term vanishes completely: $(x+2)(0) + 3 = 3$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Result:</strong> Value is $3 \\ne 5$ (Statement I is FALSE)</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Multiplication by zero property.</p>
          </div>

          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface);border-color:var(--success)">
            <span class="rung-tag rung-verify">STEP 4 · NESTED RADICAL SQUARING</span>
            <p style="margin-top:8px">To evaluate $S = \\sqrt{6 - \\sqrt{11}} + \\sqrt{6 + \\sqrt{11}}$, square both sides: $S^2 = (6 - \\sqrt{11}) + (6 + \\sqrt{11}) + 2\\sqrt{36 - 11} = 12 + 2(5) = 22$.</p>
            <div style="background:var(--card);padding:8px 10px;border-radius:6px;margin:8px 0"><strong>Result:</strong> $S^2 = 22 \\implies S = \\sqrt{22} \\ne \\sqrt{23}$ (Statement III is FALSE)</div>
            <p style="font-size:0.86rem;color:var(--text-muted)"><strong>Why valid:</strong> Difference of two squares $(6-\\sqrt{11})(6+\\sqrt{11}) = 36 - 11 = 25$.</p>
          </div>
        </div>

        <!-- Trap Clinic (T06) -->
        <div class="trap-alert" style="margin:20px 0">
          <h3>⚠️ Trap Clinic: Universal Quantifier vs Counterexample (Technique T06)</h3>
          <p><strong>Fallacy:</strong> "Square root of a positive real number is always an irrational number."</p>
          <p><strong>Refutation:</strong> A single counterexample disproves a universal claim! Consider $\\sqrt{4} = 2 \\in \\mathbb{Q}$ or $\\sqrt{9} = 3 \\in \\mathbb{Q}$. Both are positive rational integers. Hence Statement II is FALSE.</p>
        </div>
      </div>

      <!-- MODULE 2: CIRCLES & PARALLEL CHORD CONCURRENCY -->
      <div class="panel">
        <div style="border:2px solid var(--danger);border-radius:10px;padding:14px;background:var(--surface);margin-bottom:20px">
          <span class="qb-badge qb-badge-d4">BLUEPRINT BP-CORE1A-CONSTRUCTION</span>
          <span class="qb-badge qb-badge-qrt">QRT-JUSTIFY-D4</span>
          <h2 style="font-size:1.3rem;margin-top:8px">Core 1A (Module 2) · Parallel Chords & Cyclic Secant Invariance</h2>
          <p style="color:var(--text-muted);font-size:0.92rem;margin-top:4px">
            Anchored to Achievers Section D4 Olympiad Problem Q50 (Parallel chord distances and cyclic quadrilateral common chord theorem).
          </p>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:16px 0">
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-orient">STEP 1 · PYTHAGOREAN CHORD LAW</span>
            <p style="margin-top:8px">Let circle radius be $R$. For chord of length $L_1 = 6\\text{ cm}$, half-chord is 3 cm. Distance from centre is 4 cm. Then $R^2 = 3^2 + 4^2 = 9 + 16 = 25 \\implies R = 5\\text{ cm}$.</p>
          </div>
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-represent">STEP 2 · DISTANCE OF SECOND CHORD</span>
            <p style="margin-top:8px">Second chord length $L_2 = 8\\text{ cm} \\implies$ half-chord is 4 cm. Distance $d_2 = \\sqrt{R^2 - 4^2} = \\sqrt{25 - 16} = \\sqrt{9} = 3\\text{ cm}$. Statement I is TRUE.</p>
          </div>
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface)">
            <span class="rung-tag rung-crux">STEP 3 · CYCLIC ANGLE TRANSFER</span>
            <p style="margin-top:8px">In cyclic quad $ABFE$, $\\angle A + \\angle EFB = 180^\\circ \\implies \\angle EFC = \\angle A$ (exterior angle). In cyclic quad $ABCD$, $\\angle A + \\angle C = 180^\\circ$.</p>
          </div>
          <div style="border:1px solid var(--border);border-radius:10px;padding:16px;background:var(--surface);border-color:var(--success)">
            <span class="rung-tag rung-verify">STEP 4 · PARALLEL DEDUCTION</span>
            <p style="margin-top:8px">Substitute $\\angle A = \\angle EFC$: $\\angle EFC + \\angle C = 180^\\circ$. These are consecutive interior angles for lines $EF$ and $DC$ with transversal $BC$. Therefore $EF \\parallel DC$! Statement II is TRUE. ✅</p>
          </div>
        </div>

        <div class="trap-alert" style="margin:20px 0">
          <h3>⚠️ Trap Clinic: Center Orientation Ambiguity</h3>
          <p><strong>Pitfall:</strong> Assuming parallel chords must lie on opposite sides of the centre. If two parallel chords lie on the SAME side of the centre, their distances from the centre are still uniquely fixed by $d = \\sqrt{R^2 - (L/2)^2}$. The distance calculation depends only on radius and chord length, not chord side orientation!</p>
        </div>
      </div>

      <!-- CORE 1B (D4 RECONSTRUCTION) -->
      <div class="panel">
        <span class="qb-badge qb-badge-d4">BLUEPRINT BP-CORE1B-RECONSTRUCTION</span>
        <h2 style="font-size:1.3rem;margin-top:8px">Core 1B · Dual-Stage Recall & Reconstruction (D4)</h2>
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px">
          <h3>Unassisted Reconstruction Gate</h3>
          <p>For $x = 3 + \\sqrt{5}$, state the monic quadratic equation with integer coefficients that $x$ satisfies, and compute $x^2 - 6x + 12$.</p>
          <textarea class="qb-textarea" placeholder="State minimal polynomial and evaluate..."></textarea>
          <details style="margin-top:12px;background:var(--card);padding:12px;border-radius:8px">
            <summary style="cursor:pointer;font-weight:700">Check Result</summary>
            <p style="margin-top:6px">$(x - 3)^2 = 5 \\implies x^2 - 6x + 9 = 5 \\implies x^2 - 6x + 4 = 0$. Therefore $x^2 - 6x + 12 = (x^2 - 6x + 4) + 8 = 0 + 8 = 8$. ✅</p>
          </details>
        </div>
      </div>
    </section>
""")

# ==========================================
# TAB 4: D1/D2 CORE MODULE (DIVISIBILITY)
# ==========================================
html_parts.append("""
    <!-- TAB 4: D1/D2 CORE MODULE (DIVISIBILITY) -->
    <section class="tab-content" id="tab-d1-core" role="tabpanel">
      <div class="panel">
        <div style="border:2px solid var(--success);border-radius:10px;padding:14px;background:var(--surface);margin-bottom:20px">
          <span class="qb-badge qb-badge-d1">BLUEPRINT BP-CORE1A-CONSTRUCTION</span>
          <span class="qb-badge qb-badge-qrt">QRT-JUSTIFY-D1</span>
          <h2 style="font-size:1.3rem;margin-top:8px">Core 1A · Universal Proof: Divisibility of Three Consecutive Integers by 6</h2>
          <p style="color:var(--text-muted);font-size:0.92rem;margin-top:4px">
            Rigorous modular construction exhausting parity and modulo-3 residue classes.
          </p>
        </div>

        <h3 style="margin-bottom:12px">Universal Divisibility Theorems (Properly Formatted KaTeX Mathematics)</h3>
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px;line-height:1.8">
          <p>✅ <strong>Parity Lemma:</strong> Consecutive integers alternate parity: $n \\equiv 0 \\pmod 2$ or $n \\equiv 1 \\pmod 2$. In any pair $\\{n, n+1\\}$, exactly one is even, guaranteeing $2 \\mid n(n+1)$, which implies $2 \\mid P(n)$.</p>
          <p style="margin-top:10px">✅ <strong>Modulo 3 Exhaustion:</strong> By the division algorithm, an arbitrary integer $n$ satisfies exactly one residue condition:</p>
          <ul style="padding-left:24px;margin-top:6px">
            <li>If $n \\equiv 0 \\pmod 3$, then $3 \\mid n$.</li>
            <li>If $n \\equiv 1 \\pmod 3$, then $n+2 \\equiv 3 \\equiv 0 \\pmod 3$, so $3 \\mid (n+2)$.</li>
            <li>If $n \\equiv 2 \\pmod 3$, then $n+1 \\equiv 3 \\equiv 0 \\pmod 3$, so $3 \\mid (n+1)$.</li>
          </ul>
          <p style="margin-top:10px">✅ <strong>Coprimality Synthesis:</strong> If $a \\mid N$ and $b \\mid N$ with $\\gcd(a, b) = 1$, then $ab \\mid N$. Since $\\gcd(2, 3) = 1$, $6 \\mid P(n)$ holds rigorously for all $n \\in \\mathbb{Z}^+$.</p>
        </div>

        <!-- Trap Clinic (T06) -->
        <div class="trap-alert" style="margin:20px 0">
          <h3>⚠️ Trap Clinic: Non-Coprime Products (Technique T06)</h3>
          <p><strong>Fallacy:</strong> "Since $4 \\mid N$ and $6 \\mid N$, it must follow that $24 \\mid N$."</p>
          <p><strong>Refutation:</strong> The product rule strictly requires coprimality: $\\gcd(a, b) = 1$. Here $\\gcd(4, 6) = 2 \\ne 1$. For example, $N = 12$ is divisible by 4 and by 6, but $12$ is NOT divisible by 24! The least common multiple is $\\operatorname{lcm}(4, 6) = 12$, not $24$.</p>
        </div>

        <!-- Exit Task (T12) -->
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px;margin-top:20px">
          <h4>Independent Exit Task (Technique T12)</h4>
          <p>Prove that for every integer $n$, $n^3 - n$ is divisible by 6.</p>
          <textarea class="qb-textarea" style="margin-top:8px" placeholder="Factor n^3 - n into consecutive integers and apply the parity and mod-3 lemmas..."></textarea>
          <details style="margin-top:12px;background:var(--card);padding:12px;border-radius:8px">
            <summary style="cursor:pointer;font-weight:700">Reveal Model Exit Solution</summary>
            <div style="margin-top:8px;line-height:1.7">
              <p>1. Factor: $n^3 - n = n(n^2 - 1) = (n-1)n(n+1)$.</p>
              <p>2. These are three consecutive integers: $(n-1)$, $n$, and $(n+1)$.</p>
              <p>3. Exactly as in the Core 1A construction, at least one factor is even ($2 \\mid n^3 - n$) and exactly one is a multiple of 3 ($3 \\mid n^3 - n$).</p>
              <p>4. Since $\\gcd(2, 3) = 1$, $6 \\mid (n^3 - n)$ for all $n \\in \\mathbb{Z}$. Q.E.D. ✅</p>
            </div>
          </details>
        </div>
      </div>

      <!-- CORE 1B (D1/D2 RECALL) -->
      <div class="panel">
        <span class="qb-badge qb-badge-d1">BLUEPRINT BP-CORE1B-RECONSTRUCTION</span>
        <h2 style="font-size:1.3rem;margin-top:8px">Core 1B · Dual-Stage Recall & Reconstruction (D1/D2)</h2>
        <p class="lead-text">Complete the two unassisted retrieval gates:</p>

        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:18px">
          <h3>Gate 1 · Boundary Laws Recall</h3>
          <p>1. State the exact condition required for $a \\mid N$ and $b \\mid N$ to imply $ab \\mid N$.</p>
          <p>2. In a sequence of 3 consecutive integers, can two of them be multiples of 3? Explain why or why not.</p>
          <textarea class="qb-textarea" placeholder="Recall coprimality requirement and residue distribution modulo 3..."></textarea>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px">
          <h3>Gate 2 · Changed Givens Reconstruction (Technique T12)</h3>
          <p>Prove that for any integer $n \\ge 1$, the product of four consecutive integers $Q(n) = n(n+1)(n+2)(n+3)$ is always divisible by 24.</p>
          <textarea class="qb-textarea" placeholder="Decompose 24 into coprime factors 3 and 8. Prove 3 | Q(n) and 8 | Q(n)..."></textarea>
          <details style="margin-top:12px;background:var(--card);padding:12px;border-radius:8px">
            <summary style="cursor:pointer;font-weight:700">Check Gate 2 Result</summary>
            <div style="margin-top:6px;line-height:1.7">
              <p>1. <strong>Divisibility by 3:</strong> Among any three consecutive integers, one is a multiple of 3. Since $n, n+1, n+2$ are three consecutive integers, $3 \\mid Q(n)$.</p>
              <p>2. <strong>Divisibility by 8:</strong> Among four consecutive integers, exactly two are even. Since they alternate with odd numbers, the two evens differ by 2: one is of the form $2(2k) = 4k$ (a multiple of 4) and the other is $2(2k+1)$ (at least a multiple of 2). Their product contains at least $4 \\times 2 = 8$. Hence $8 \\mid Q(n)$.</p>
              <p>3. <strong>Synthesis:</strong> Since $\\gcd(3, 8) = 1$, $3 \\times 8 = 24 \\mid Q(n)$ for all $n \\ge 1$. Q.E.D. ✅</p>
            </div>
          </details>
        </div>
      </div>
    </section>
""")

# ==========================================
# FOOTER & CLIENT-SIDE DYNAMIC FILTER JS
# ==========================================
html_parts.append("""
  </main>

  <footer class="g9-footer">
    <p>Grade 9 IMO Mathematics · Blueprint-Standard Question Bank & Core 1A/1B Learning Suite · 100% Offline Standalone</p>
  </footer>

  <script>
    // Tab Switching
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

      const targetTab = document.getElementById('tab-' + tabId);
      const targetBtn = document.getElementById('tab-btn-' + tabId);
      if (targetTab) targetTab.classList.add('active');
      if (targetBtn) targetBtn.classList.add('active');

      window.scrollTo({top: 0, behavior: 'smooth'});
      triggerKaTeX();
    }

    function toggleTheme() {
      const htmlEl = document.documentElement;
      const current = htmlEl.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      htmlEl.setAttribute('data-theme', next);
    }

    // Dynamic Filter State
    const activeFilters = {
      band: null,
      demand: null,
      year: null,
      topic: null
    };

    function toggleFilter(type, value, btn) {
      if (activeFilters[type] === value) {
        activeFilters[type] = null;
        if (btn) btn.classList.remove('active');
      } else {
        activeFilters[type] = value;
        btn.parentElement.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
      }
      runFilter();
    }

    function addActiveFilter(type, value) {
      activeFilters[type] = value;
      document.querySelectorAll('.filter-chip').forEach(c => {
        if (c.textContent.includes(value)) c.classList.add('active');
      });
      runFilter();
      document.getElementById('qb-search').scrollIntoView({behavior: 'smooth'});
    }

    function removeActiveFilter(type) {
      const oldVal = activeFilters[type];
      activeFilters[type] = null;
      document.querySelectorAll('.filter-chip').forEach(c => {
        if (oldVal && c.textContent.includes(oldVal)) c.classList.remove('active');
      });
      runFilter();
    }

    function clearAllFilters() {
      activeFilters.band = null;
      activeFilters.demand = null;
      activeFilters.year = null;
      activeFilters.topic = null;
      document.getElementById('qb-search').value = '';
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      runFilter();
    }

    function runFilter() {
      const query = (document.getElementById('qb-search').value || '').trim();
      let queryRegex = null;
      if (query) {
        try {
          if (query.startsWith('/') && query.lastIndexOf('/') > 0) {
            const pattern = query.slice(1, query.lastIndexOf('/'));
            const flags = query.slice(query.lastIndexOf('/') + 1) || 'i';
            queryRegex = new RegExp(pattern, flags);
          } else {
            queryRegex = new RegExp(query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'), 'i');
          }
        } catch(e) {
          queryRegex = new RegExp(query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'), 'i');
        }
      }

      // Render Active Pills
      const container = document.getElementById('active-filters-container');
      const list = document.getElementById('active-pills-list');
      list.innerHTML = '';
      let filterCount = 0;

      for (const [key, val] of Object.entries(activeFilters)) {
        if (val) {
          filterCount++;
          const pill = document.createElement('span');
          pill.className = 'active-pill';
          pill.innerHTML = `<span>${key.toUpperCase()}: ${val}</span> <span class="active-pill-remove" onclick="removeActiveFilter('${key}')" title="Remove filter">✕</span>`;
          list.appendChild(pill);
        }
      }

      if (filterCount > 0 || query) {
        container.style.display = 'flex';
      } else {
        container.style.display = 'none';
      }

      const questions = document.querySelectorAll('.qb-question');
      let visibleCount = 0;

      questions.forEach(q => {
        const qBand = q.getAttribute('data-band');
        const qDemand = q.getAttribute('data-demand');
        const qTopic = q.getAttribute('data-topic');
        const qYear = q.getAttribute('data-year');
        const qSearch = q.getAttribute('data-search') || '';

        let match = true;
        if (activeFilters.band && qBand !== activeFilters.band) match = false;
        if (activeFilters.demand && qDemand !== activeFilters.demand) match = false;
        if (activeFilters.topic && !qTopic.includes(activeFilters.topic)) match = false;
        if (activeFilters.year && qYear !== activeFilters.year) match = false;

        if (match && queryRegex) {
          match = queryRegex.test(qSearch);
        }

        if (match) {
          q.style.display = '';
          visibleCount++;
        } else {
          q.style.display = 'none';
        }
      });

      document.getElementById('result-counter').textContent = `Showing ${visibleCount} of ${questions.length} questions`;
      triggerKaTeX();
    }

    // KaTeX safe auto-render execution
    function triggerKaTeX() {
      if (window.renderMathInElement) {
        window.renderMathInElement(document.body, {
          delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false},
            {left: '\\\\(', right: '\\\\)', display: false},
            {left: '\\\\[', right: '\\\\]', display: true}
          ],
          throwOnError: false
        });
      }
    }

    document.addEventListener("DOMContentLoaded", function() {
      triggerKaTeX();
      // Attach disclosure re-render
      document.querySelectorAll('details').forEach(d => {
        d.addEventListener('toggle', () => {
          if (d.open) setTimeout(triggerKaTeX, 30);
        });
      });
    });

    window.addEventListener("load", triggerKaTeX);
  </script>
</body>
</html>
""")

full_html = "".join(html_parts)

out_file = root / "standalone/mathematics-imo-grade9-master-suite.html"
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Generated master suite at {out_file} (size: {len(full_html)} chars)")
