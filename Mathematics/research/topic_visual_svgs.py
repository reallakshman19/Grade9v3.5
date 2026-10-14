"""
Bespoke Responsive Vector SVG Visual Representations for Grade 9 IMO Core 1 Topics.
Every SVG is crafted with:
- Strict typography floor (all text elements have font-size >= 14px)
- Responsive viewBox (scaling cleanly on all viewports)
- High-contrast, theme-adaptive colors
- Authentic mathematical diagrams matching each topic's core invariant
"""
from typing import Dict

TOPIC_COLOR_PALETTES = {
    "circles": {"primary": "#a855f7", "glow": "rgba(168,85,247,0.25)", "bg": "rgba(168,85,247,0.08)", "label": "Circles & Cyclic Quads"},
    "commercial-math": {"primary": "#10b981", "glow": "rgba(16,185,129,0.25)", "bg": "rgba(16,185,129,0.08)", "label": "Commercial Math & Rates"},
    "coordinate-geometry": {"primary": "#06b6d4", "glow": "rgba(6,182,212,0.25)", "bg": "rgba(6,182,212,0.08)", "label": "Coordinate Geometry"},
    "euclid-geometry": {"primary": "#f59e0b", "glow": "rgba(245,158,11,0.25)", "bg": "rgba(245,158,11,0.08)", "label": "Euclid's Geometry"},
    "heron-formula": {"primary": "#f43f5e", "glow": "rgba(244,63,94,0.25)", "bg": "rgba(244,63,94,0.08)", "label": "Heron's Area Formula"},
    "linear-equations": {"primary": "#3b82f6", "glow": "rgba(59,130,246,0.25)", "bg": "rgba(59,130,246,0.08)", "label": "Linear Equations"},
    "lines-and-angles": {"primary": "#14b8a6", "glow": "rgba(20,184,166,0.25)", "bg": "rgba(20,184,166,0.08)", "label": "Lines & Angles"},
    "polynomials": {"primary": "#8b5cf6", "glow": "rgba(139,92,246,0.25)", "bg": "rgba(139,92,246,0.08)", "label": "Polynomials & Identities"},
    "probability": {"primary": "#84cc16", "glow": "rgba(132,204,22,0.25)", "bg": "rgba(132,204,22,0.08)", "label": "Probability Models"},
    "quadrilaterals": {"primary": "#f97316", "glow": "rgba(249,115,22,0.25)", "bg": "rgba(249,115,22,0.08)", "label": "Quadrilaterals"},
    "reasoning": {"primary": "#d946ef", "glow": "rgba(217,70,239,0.25)", "bg": "rgba(217,70,239,0.08)", "label": "Reasoning Patterns"},
    "statistics": {"primary": "#2563eb", "glow": "rgba(37,99,235,0.25)", "bg": "rgba(37,99,235,0.08)", "label": "Statistics & Charts"},
    "surface-areas-volumes": {"primary": "#ef4444", "glow": "rgba(239,68,68,0.25)", "bg": "rgba(239,68,68,0.08)", "label": "Surface Areas & Volumes"},
    "triangles": {"primary": "#eab308", "glow": "rgba(234,179,8,0.25)", "bg": "rgba(234,179,8,0.08)", "label": "Triangles & Congruence"}
}

def generate_topic_svg(topic_folder: str) -> str:
    """Returns an inline, self-contained, responsive SVG visualization for the specified topic."""
    
    if topic_folder == "circles":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Cyclic Quadrilateral with Parallel Chords and Inscribed Angles">
          <defs>
            <marker id="arr-purple" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a855f7"/></marker>
          </defs>
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#a855f7" stroke-width="1.5" stroke-dasharray="none"/>
          <!-- Outer Circle -->
          <circle cx="160" cy="130" r="95" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
          <circle cx="160" cy="130" r="3.5" fill="#f8fafc"/>
          <text x="165" y="125" fill="#94a3b8" font-size="14" font-weight="700">O (Center)</text>
          
          <!-- Inscribed Cyclic Quadrilateral ABCD -->
          <!-- A(100, 60), B(240, 85), C(220, 195), D(80, 180) -->
          <polygon points="100,60 240,85 220,195 80,180" fill="rgba(168,85,247,0.14)" stroke="#a855f7" stroke-width="2.5"/>
          
          <!-- Parallel Chords AB and DC -->
          <line x1="100" y1="60" x2="240" y2="85" stroke="#fbbf24" stroke-width="2.5"/>
          <line x1="80" y1="180" x2="220" y2="195" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="4,3"/>
          <text x="170" y="55" fill="#fbbf24" font-size="14" font-weight="750">Chord AB ∥ Chord DC</text>
          
          <!-- Vertex Dots & Labels -->
          <circle cx="100" cy="60" r="5" fill="#f43f5e"/><text x="82" y="55" fill="#f8fafc" font-size="14" font-weight="800">A</text>
          <circle cx="240" cy="85" r="5" fill="#f43f5e"/><text x="250" y="88" fill="#f8fafc" font-size="14" font-weight="800">B</text>
          <circle cx="220" cy="195" r="5" fill="#f43f5e"/><text x="230" y="208" fill="#f8fafc" font-size="14" font-weight="800">C</text>
          <circle cx="80" cy="180" r="5" fill="#f43f5e"/><text x="62" y="192" fill="#f8fafc" font-size="14" font-weight="800">D</text>
          
          <!-- Inscribed Angle Arc indicators -->
          <path d="M 115,75 A 20,20 0 0,0 95,85" fill="none" stroke="#34d399" stroke-width="2"/>
          <path d="M 205,185 A 20,20 0 0,0 205,170" fill="none" stroke="#34d399" stroke-width="2"/>
          
          <!-- Explanatory Invariant Panel on Right -->
          <rect x="290" y="20" width="250" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="306" y="48" fill="#a855f7" font-size="14" font-weight="800">CYCLIC INVARIANTS</text>
          <text x="306" y="80" fill="#f1f5f9" font-size="14" font-weight="650">1. Opposite Angles Supplementary:</text>
          <text x="320" y="105" fill="#34d399" font-size="14" font-weight="750">∠B + ∠D = 180°</text>
          <text x="320" y="128" fill="#34d399" font-size="14" font-weight="750">∠A + ∠C = 180°</text>
          <text x="306" y="160" fill="#f1f5f9" font-size="14" font-weight="650">2. Parallel Transversal Law:</text>
          <text x="320" y="185" fill="#fbbf24" font-size="14" font-weight="700">AB ∥ DC ⇒ AD = BC</text>
          <text x="306" y="218" fill="#38bdf8" font-size="14" font-weight="700">Trapezoid ABCD is Isosceles</text>
        </svg>
        """

    elif topic_folder == "commercial-math":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Commercial Math Rate Balance & Growth Curves">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
          <!-- Rate Balance System on Left -->
          <rect x="20" y="20" width="245" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="35" y="48" fill="#10b981" font-size="14" font-weight="800">SIMULTANEOUS WORK RATES</text>
          
          <rect x="35" y="65" width="215" height="42" rx="6" fill="#090e17" stroke="#38bdf8"/>
          <text x="45" y="91" fill="#38bdf8" font-size="14" font-weight="750">Team 1: 6m + 8b = 1/10 per day</text>
          
          <rect x="35" y="118" width="215" height="42" rx="6" fill="#090e17" stroke="#fbbf24"/>
          <text x="45" y="144" fill="#fbbf24" font-size="14" font-weight="750">Team 2: 26m + 48b = 1/2 per day</text>
          
          <path d="M 140,165 L 140,185" stroke="#10b981" stroke-width="2" marker-end="url(#arr-green)"/>
          <text x="50" y="210" fill="#34d399" font-size="14" font-weight="800">Ratio: 1 Man Rate = 2 Boy Rates</text>
          
          <!-- Compound vs Simple Growth Graph on Right -->
          <!-- Axes -->
          <line x1="300" y1="210" x2="520" y2="210" stroke="#94a3b8" stroke-width="2"/>
          <line x1="300" y1="210" x2="300" y2="40" stroke="#94a3b8" stroke-width="2"/>
          <text x="500" y="230" fill="#94a3b8" font-size="14" font-weight="700">Time (t)</text>
          <text x="290" y="32" fill="#94a3b8" font-size="14" font-weight="700">Amount (A)</text>
          
          <!-- Simple Interest Line: A = P(1 + rt) -->
          <line x1="300" y1="180" x2="510" y2="105" stroke="#fbbf24" stroke-width="2.5"/>
          <text x="430" y="125" fill="#fbbf24" font-size="14" font-weight="700">Simple: P(1+rt)</text>
          
          <!-- Compound Interest Curve: A = P(1 + r)^t -->
          <path d="M 300,180 Q 420,165 510,55" fill="none" stroke="#10b981" stroke-width="3"/>
          <text x="360" y="60" fill="#10b981" font-size="14" font-weight="800">Compound: P(1+r/n)^nt</text>
          
          <circle cx="300" cy="180" r="4" fill="#f43f5e"/>
          <text x="250" y="185" fill="#f8fafc" font-size="14" font-weight="750">P (Principal)</text>
        </svg>
        """

    elif topic_folder == "coordinate-geometry":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Cartesian Reflections & Lattice Area Polygon">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#06b6d4" stroke-width="1.5"/>
          <!-- Coordinate Axes -->
          <line x1="40" y1="130" x2="280" y2="130" stroke="#64748b" stroke-width="2"/>
          <line x1="160" y1="20" x2="160" y2="240" stroke="#64748b" stroke-width="2"/>
          <text x="268" y="124" fill="#94a3b8" font-size="14" font-weight="750">X</text>
          <text x="165" y="35" fill="#94a3b8" font-size="14" font-weight="750">Y</text>
          <text x="145" y="145" fill="#94a3b8" font-size="14" font-weight="700">O</text>
          
          <!-- Point P(3, 2) in Q1 -->
          <circle cx="220" cy="80" r="5" fill="#38bdf8"/>
          <text x="228" y="78" fill="#38bdf8" font-size="14" font-weight="800">P(a, b)</text>
          
          <!-- Reflection across Y-axis: P'(-a, b) in Q2 -->
          <circle cx="100" cy="80" r="5" fill="#f59e0b"/>
          <text x="45" y="78" fill="#f59e0b" font-size="14" font-weight="800">P'(-a, b)</text>
          <line x1="100" y1="80" x2="220" y2="80" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,4"/>
          
          <!-- Reflection across X-axis: P''(a, -b) in Q4 -->
          <circle cx="220" cy="180" r="5" fill="#34d399"/>
          <text x="228" y="195" fill="#34d399" font-size="14" font-weight="800">P''(a, -b)</text>
          <line x1="220" y1="80" x2="220" y2="180" stroke="#34d399" stroke-width="1.5" stroke-dasharray="4,4"/>
          
          <!-- Reflection across Origin: P'''(-a, -b) in Q3 -->
          <circle cx="100" cy="180" r="5" fill="#c084fc"/>
          <text x="40" y="195" fill="#c084fc" font-size="14" font-weight="800">P'''(-a, -b)</text>
          
          <!-- Shaded Lattice Rectangle -->
          <polygon points="100,80 220,80 220,180 100,180" fill="rgba(6,182,212,0.12)" stroke="#06b6d4" stroke-width="2"/>
          
          <!-- Invariant Info Panel on Right -->
          <rect x="310" y="20" width="230" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="325" y="48" fill="#06b6d4" font-size="14" font-weight="800">REFLECTION RULES</text>
          <text x="325" y="80" fill="#f1f5f9" font-size="14" font-weight="650">Reflection across X-axis:</text>
          <text x="340" y="104" fill="#34d399" font-size="14" font-weight="750">(x, y) ➔ (x, -y)</text>
          <text x="325" y="134" fill="#f1f5f9" font-size="14" font-weight="650">Reflection across Y-axis:</text>
          <text x="340" y="158" fill="#f59e0b" font-size="14" font-weight="750">(x, y) ➔ (-x, y)</text>
          <text x="325" y="190" fill="#f1f5f9" font-size="14" font-weight="650">Area of Bounding Enclosure:</text>
          <text x="340" y="214" fill="#38bdf8" font-size="14" font-weight="750">Area = (2a) × (2b) = 4ab</text>
        </svg>
        """

    elif topic_folder == "euclid-geometry":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Euclid's Axiom Subtraction of Overlapping Segments">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
          <text x="40" y="42" fill="#f59e0b" font-size="14" font-weight="800">EUCLID'S AXIOM 3 · SUBTRACTION OF EQUALS</text>
          
          <!-- Collinear Segment Line P - Q - R - S -->
          <line x1="50" y1="120" x2="510" y2="120" stroke="#94a3b8" stroke-width="4"/>
          
          <!-- Points P, Q, R, S -->
          <circle cx="70" cy="120" r="7" fill="#f43f5e"/><text x="65" y="150" fill="#f8fafc" font-size="14" font-weight="800">P</text>
          <circle cx="200" cy="120" r="7" fill="#38bdf8"/><text x="195" y="150" fill="#f8fafc" font-size="14" font-weight="800">Q</text>
          <circle cx="360" cy="120" r="7" fill="#38bdf8"/><text x="355" y="150" fill="#f8fafc" font-size="14" font-weight="800">R</text>
          <circle cx="490" cy="120" r="7" fill="#f43f5e"/><text x="485" y="150" fill="#f8fafc" font-size="14" font-weight="800">S</text>
          
          <!-- Segment PR Top Bracket -->
          <path d="M 70,105 L 70,85 L 360,85 L 360,105" fill="none" stroke="#fbbf24" stroke-width="2.5"/>
          <text x="185" y="78" fill="#fbbf24" font-size="14" font-weight="800">Segment PR (Given: PR = QS)</text>
          
          <!-- Segment QS Bottom Bracket -->
          <path d="M 200,165 L 200,185 L 490,185 L 490,165" fill="none" stroke="#34d399" stroke-width="2.5"/>
          <text x="315" y="205" fill="#34d399" font-size="14" font-weight="800">Segment QS (Given: PR = QS)</text>
          
          <!-- Shared Segment QR Highlight -->
          <rect x="200" y="112" width="160" height="16" fill="rgba(244,63,94,0.35)" rx="4"/>
          <text x="235" y="105" fill="#fca5a5" font-size="14" font-weight="750">Shared QR Subtracted</text>
          
          <!-- Conclusion Box -->
          <rect x="60" y="215" width="440" height="32" rx="6" fill="#1e293b" stroke="#f59e0b"/>
          <text x="75" y="236" fill="#f8fafc" font-size="14" font-weight="750">Deduction: PR - QR = QS - QR ➔ Exactly PQ = RS (Axiom 3 Verified)</text>
        </svg>
        """

    elif topic_folder == "heron-formula":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Heron's Formula Triangle and Composite Area Partition">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#f43f5e" stroke-width="1.5"/>
          <!-- Triangle ABC: A(140, 45), B(50, 205), C(250, 205) -->
          <polygon points="140,45 50,205 250,205" fill="rgba(244,63,94,0.12)" stroke="#f43f5e" stroke-width="2.5"/>
          
          <!-- Incircle & Incenter I -->
          <circle cx="145" cy="155" r="45" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="3,3"/>
          <circle cx="145" cy="155" r="4" fill="#fbbf24"/>
          <text x="152" y="152" fill="#fbbf24" font-size="14" font-weight="800">I (Incenter)</text>
          <line x1="145" y1="155" x2="145" y2="205" stroke="#fbbf24" stroke-width="1.5"/>
          <text x="148" y="185" fill="#fbbf24" font-size="14" font-weight="700">r</text>
          
          <!-- Vertices & Side Labels -->
          <circle cx="140" cy="45" r="5" fill="#f8fafc"/><text x="135" y="35" fill="#f8fafc" font-size="14" font-weight="800">A</text>
          <circle cx="50" cy="205" r="5" fill="#f8fafc"/><text x="32" y="215" fill="#f8fafc" font-size="14" font-weight="800">B</text>
          <circle cx="250" cy="205" r="5" fill="#f8fafc"/><text x="258" y="215" fill="#f8fafc" font-size="14" font-weight="800">C</text>
          
          <text x="80" y="120" fill="#38bdf8" font-size="14" font-weight="800">side c</text>
          <text x="205" y="120" fill="#38bdf8" font-size="14" font-weight="800">side b</text>
          <text x="140" y="225" fill="#38bdf8" font-size="14" font-weight="800">side a</text>
          
          <!-- Right Panel: Formulas & Invariant -->
          <rect x="290" y="20" width="250" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="306" y="48" fill="#f43f5e" font-size="14" font-weight="800">HERON'S FORMULATION</text>
          <text x="306" y="78" fill="#f1f5f9" font-size="14" font-weight="650">Semiperimeter:</text>
          <text x="325" y="102" fill="#38bdf8" font-size="14" font-weight="750">s = (a + b + c) / 2</text>
          <text x="306" y="132" fill="#f1f5f9" font-size="14" font-weight="650">Area Formula:</text>
          <text x="325" y="156" fill="#34d399" font-size="14" font-weight="750">Δ = √[s(s - a)(s - b)(s - c)]</text>
          <text x="306" y="186" fill="#f1f5f9" font-size="14" font-weight="650">Inradius Invariant:</text>
          <text x="325" y="210" fill="#fbbf24" font-size="14" font-weight="750">r = Δ / s  ➔  Δ = r · s</text>
        </svg>
        """

    elif topic_folder == "linear-equations":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Linear Constraint System Intersection">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
          <!-- Axes -->
          <line x1="40" y1="210" x2="300" y2="210" stroke="#64748b" stroke-width="2"/>
          <line x1="80" y1="20" x2="80" y2="230" stroke="#64748b" stroke-width="2"/>
          <text x="290" y="204" fill="#94a3b8" font-size="14" font-weight="750">x</text>
          <text x="65" y="35" fill="#94a3b8" font-size="14" font-weight="750">y</text>
          
          <!-- Line 1: 2x + y = 10 -->
          <line x1="80" y1="45" x2="260" y2="210" stroke="#38bdf8" stroke-width="3"/>
          <text x="180" y="90" fill="#38bdf8" font-size="14" font-weight="750">Line 1: 2x + y = 10</text>
          
          <!-- Line 2: x - y = -1 -->
          <line x1="80" y1="195" x2="270" y2="60" stroke="#f59e0b" stroke-width="3"/>
          <text x="200" y="165" fill="#f59e0b" font-size="14" font-weight="750">Line 2: x - y = -1</text>
          
          <!-- Unique Intersection Point (3, 4) -->
          <circle cx="170" cy="127" r="7" fill="#f43f5e"/>
          <circle cx="170" cy="127" r="14" fill="none" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="2,2"/>
          <text x="110" y="120" fill="#f8fafc" font-size="14" font-weight="800">P(x₀, y₀)</text>
          
          <!-- Solution Invariant Box on Right -->
          <rect x="320" y="20" width="220" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="336" y="48" fill="#3b82f6" font-size="14" font-weight="800">LINEAR SYSTEM LAWS</text>
          <text x="336" y="80" fill="#f1f5f9" font-size="14" font-weight="650">Determinant Condition:</text>
          <text x="350" y="105" fill="#34d399" font-size="14" font-weight="750">a₁/a₂ ≠ b₁/b₂</text>
          <text x="336" y="138" fill="#f1f5f9" font-size="14" font-weight="650">Unique Olympiad Solution:</text>
          <text x="350" y="163" fill="#38bdf8" font-size="14" font-weight="750">(x₀, y₀) = (3, 4)</text>
          <text x="336" y="196" fill="#f1f5f9" font-size="14" font-weight="650">Simultaneous Consistency:</text>
          <text x="350" y="218" fill="#fbbf24" font-size="14" font-weight="750">Rank = 2 (Independent)</text>
        </svg>
        """

    elif topic_folder == "lines-and-angles":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Parallel Lines Cut by Transversal Angle Transfer">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#14b8a6" stroke-width="1.5"/>
          <!-- Parallel Line 1 -->
          <line x1="40" y1="85" x2="320" y2="85" stroke="#38bdf8" stroke-width="3"/>
          <text x="270" y="75" fill="#38bdf8" font-size="14" font-weight="800">Line L₁</text>
          
          <!-- Parallel Line 2 -->
          <line x1="40" y1="185" x2="320" y2="185" stroke="#38bdf8" stroke-width="3"/>
          <text x="270" y="175" fill="#38bdf8" font-size="14" font-weight="800">Line L₂ (L₁ ∥ L₂)</text>
          
          <!-- Transversal Line t -->
          <line x1="80" y1="25" x2="280" y2="235" stroke="#fbbf24" stroke-width="3"/>
          <text x="260" y="245" fill="#fbbf24" font-size="14" font-weight="800">Transversal (t)</text>
          
          <!-- Angles at Upper Intersection (137, 85) -->
          <!-- Angle 1 (top-right): alternate interior partner -->
          <path d="M 160,85 A 25,25 0 0,0 148,65" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
          <text x="165" y="75" fill="#f43f5e" font-size="14" font-weight="800">∠1 = θ</text>
          
          <!-- Angles at Lower Intersection (233, 185) -->
          <!-- Alternate Interior Angle 2 (bottom-left) -->
          <path d="M 210,185 A 25,25 0 0,0 222,205" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
          <text x="180" y="210" fill="#f43f5e" font-size="14" font-weight="800">∠2 = θ</text>
          
          <!-- Co-Interior Angle (top-left) -->
          <path d="M 210,185 A 25,25 0 0,1 220,165" fill="none" stroke="#34d399" stroke-width="2.5"/>
          <text x="150" y="175" fill="#34d399" font-size="14" font-weight="800">180° - θ</text>
          
          <!-- Right Side Summary -->
          <rect x="340" y="20" width="200" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="355" y="48" fill="#14b8a6" font-size="14" font-weight="800">ANGLE TRANSFER</text>
          <text x="355" y="78" fill="#f43f5e" font-size="14" font-weight="700">Alternate Interior:</text>
          <text x="370" y="100" fill="#f1f5f9" font-size="14" font-weight="650">∠1 = ∠2 = θ</text>
          <text x="355" y="130" fill="#38bdf8" font-size="14" font-weight="700">Corresponding:</text>
          <text x="370" y="152" fill="#f1f5f9" font-size="14" font-weight="650">∠Top = ∠Bottom</text>
          <text x="355" y="182" fill="#34d399" font-size="14" font-weight="700">Co-Interior Sum:</text>
          <text x="370" y="204" fill="#f1f5f9" font-size="14" font-weight="650">θ + (180° - θ) = 180°</text>
        </svg>
        """

    elif topic_folder == "polynomials":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Polynomial Division and Factor Theorem Identity Bridge">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#8b5cf6" stroke-width="1.5"/>
          <text x="35" y="40" fill="#8b5cf6" font-size="14" font-weight="800">FACTOR THEOREM &amp; EUCLIDEAN IDENTITY BRIDGE</text>
          
          <!-- Division Decomposition Visual -->
          <rect x="35" y="65" width="490" height="55" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="50" y="100" fill="#38bdf8" font-size="14" font-weight="800">P(x) = (x - a) · Q(x) + R</text>
          <text x="320" y="100" fill="#94a3b8" font-size="14" font-weight="650">(where remainder R is a scalar)</text>
          
          <!-- Evaluation Vanish Gate at x = a -->
          <path d="M 160,120 L 160,150" stroke="#8b5cf6" stroke-width="2.5" marker-end="url(#arr-purple)"/>
          <text x="175" y="142" fill="#fbbf24" font-size="14" font-weight="750">Evaluate at root: x = a</text>
          
          <!-- Identity at x = a -->
          <rect x="35" y="155" width="490" height="45" rx="8" fill="#1e293b" stroke="#fbbf24" stroke-width="2"/>
          <text x="50" y="183" fill="#fbbf24" font-size="14" font-weight="800">P(a) = (a - a) · Q(a) + R  ➔  P(a) = 0 + R  ➔  R = P(a)</text>
          
          <!-- Factor Theorem Biconditional -->
          <rect x="35" y="210" width="490" height="38" rx="8" fill="rgba(52,211,153,0.12)" stroke="#34d399" stroke-width="2"/>
          <text x="50" y="235" fill="#34d399" font-size="14" font-weight="800">FACTOR THEOREM: (x - a) divides P(x)  ⟺  P(a) = 0 (Zero Remainder)</text>
        </svg>
        """

    elif topic_folder == "probability":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Probability Venn Sample Space and Outcome Lattice">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#84cc16" stroke-width="1.5"/>
          <!-- Universal Sample Space S -->
          <rect x="40" y="35" width="260" height="190" rx="10" fill="#1e293b" stroke="#64748b" stroke-width="2.5"/>
          <text x="55" y="60" fill="#94a3b8" font-size="14" font-weight="800">Sample Space (S)</text>
          
          <!-- Event E Circle -->
          <circle cx="160" cy="135" r="60" fill="rgba(132,204,22,0.22)" stroke="#84cc16" stroke-width="3"/>
          <text x="135" y="130" fill="#84cc16" font-size="14" font-weight="800">Event (E)</text>
          <text x="130" y="155" fill="#f8fafc" font-size="14" font-weight="700">n(E) Outcomes</text>
          
          <!-- Complementary Region E' -->
          <text x="210" y="205" fill="#fbbf24" font-size="14" font-weight="750">Complement E'</text>
          
          <!-- Right Panel: Probability Axioms & Invariants -->
          <rect x="320" y="20" width="220" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="335" y="48" fill="#84cc16" font-size="14" font-weight="800">PROBABILITY INVARIANTS</text>
          <text x="335" y="80" fill="#f1f5f9" font-size="14" font-weight="650">Theoretical Measure:</text>
          <text x="350" y="104" fill="#38bdf8" font-size="14" font-weight="750">P(E) = n(E) / n(S)</text>
          <text x="335" y="134" fill="#f1f5f9" font-size="14" font-weight="650">Bounded Domain:</text>
          <text x="350" y="158" fill="#34d399" font-size="14" font-weight="750">0 ≤ P(E) ≤ 1</text>
          <text x="335" y="188" fill="#f1f5f9" font-size="14" font-weight="650">Exhaustion Law:</text>
          <text x="350" y="212" fill="#fbbf24" font-size="14" font-weight="750">P(E) + P(E') = 1</text>
        </svg>
        """

    elif topic_folder == "quadrilaterals":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Parallelogram with Interior Angle Bisectors Forming a Rectangle">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#f97316" stroke-width="1.5"/>
          <!-- Parallelogram ABCD: A(60, 205), B(280, 205), C(340, 55), D(120, 55) -->
          <polygon points="60,205 280,205 340,55 120,55" fill="rgba(249,115,22,0.10)" stroke="#f97316" stroke-width="2.5"/>
          
          <!-- Vertices Labels -->
          <text x="45" y="225" fill="#f8fafc" font-size="14" font-weight="800">A</text>
          <text x="285" y="225" fill="#f8fafc" font-size="14" font-weight="800">B</text>
          <text x="345" y="50" fill="#f8fafc" font-size="14" font-weight="800">C</text>
          <text x="105" y="50" fill="#f8fafc" font-size="14" font-weight="800">D</text>
          
          <!-- Angle Bisector Rays -->
          <line x1="60" y1="205" x2="230" y2="55" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4,3"/>
          <line x1="280" y1="205" x2="110" y2="55" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4,3"/>
          <line x1="120" y1="55" x2="220" y2="205" stroke="#34d399" stroke-width="2" stroke-dasharray="4,3"/>
          <line x1="340" y1="55" x2="170" y2="205" stroke="#34d399" stroke-width="2" stroke-dasharray="4,3"/>
          
          <!-- Enclosed Rectangle PQRS -->
          <polygon points="175,105 220,135 185,170 140,140" fill="rgba(56,189,248,0.30)" stroke="#38bdf8" stroke-width="2.5"/>
          <text x="155" y="142" fill="#fbbf24" font-size="14" font-weight="800">PQRS</text>
          
          <!-- Invariant Info Panel on Right -->
          <rect x="360" y="20" width="185" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="372" y="48" fill="#f97316" font-size="14" font-weight="800">BISECTOR THEOREM</text>
          <text x="372" y="76" fill="#f1f5f9" font-size="14" font-weight="650">Adjacent Angles:</text>
          <text x="382" y="98" fill="#38bdf8" font-size="14" font-weight="750">∠A + ∠B = 180°</text>
          <text x="372" y="126" fill="#f1f5f9" font-size="14" font-weight="650">Half Angles:</text>
          <text x="382" y="148" fill="#34d399" font-size="14" font-weight="750">½∠A + ½∠B = 90°</text>
          <text x="372" y="176" fill="#f1f5f9" font-size="14" font-weight="650">Enclosed Form:</text>
          <text x="382" y="200" fill="#fbbf24" font-size="14" font-weight="800">PQRS is a Rectangle</text>
          <text x="382" y="222" fill="#f8fafc" font-size="14" font-weight="700">All 4 Angles = 90°</text>
        </svg>
        """

    elif topic_folder == "reasoning":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Dual Axis Pattern Matrix Invariant">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#d946ef" stroke-width="1.5"/>
          <!-- 3x3 Grid Puzzle Matrix -->
          <g transform="translate(40, 30)">
            <!-- Rows & Cols -->
            <rect x="0" y="0" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="25" y="36" fill="#f8fafc" font-size="14" font-weight="800">12</text>
            <rect x="70" y="0" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="95" y="36" fill="#f8fafc" font-size="14" font-weight="800">15</text>
            <rect x="140" y="0" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="165" y="36" fill="#f8fafc" font-size="14" font-weight="800">18</text>
            
            <rect x="0" y="70" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="25" y="106" fill="#f8fafc" font-size="14" font-weight="800">17</text>
            <!-- Center Target -->
            <rect x="70" y="70" width="60" height="60" fill="rgba(217,70,239,0.25)" stroke="#fbbf24" stroke-width="3"/>
            <text x="92" y="106" fill="#fbbf24" font-size="14" font-weight="800">20</text>
            <rect x="140" y="70" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="165" y="106" fill="#f8fafc" font-size="14" font-weight="800">23</text>
            
            <rect x="0" y="140" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="25" y="176" fill="#f8fafc" font-size="14" font-weight="800">22</text>
            <rect x="70" y="140" width="60" height="60" fill="#1e293b" stroke="#d946ef" stroke-width="2"/>
            <text x="95" y="176" fill="#f8fafc" font-size="14" font-weight="800">25</text>
            <rect x="140" y="140" width="60" height="60" fill="#1e293b" stroke="#34d399" stroke-width="3"/>
            <text x="160" y="176" fill="#34d399" font-size="14" font-weight="800">[ ? ]</text>
          </g>
          
          <!-- Invariant Synthesis on Right -->
          <rect x="270" y="20" width="270" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="286" y="48" fill="#d946ef" font-size="14" font-weight="800">DUAL-AXIS NUMBER PATTERNS</text>
          <text x="286" y="78" fill="#38bdf8" font-size="14" font-weight="750">Horizontal Step: ΔH = +3</text>
          <text x="300" y="100" fill="#94a3b8" font-size="14" font-weight="650">12 ➔ 15 (+3) ➔ 18 (+3)</text>
          <text x="286" y="130" fill="#fbbf24" font-size="14" font-weight="750">Vertical Step: ΔV = +5</text>
          <text x="300" y="152" fill="#94a3b8" font-size="14" font-weight="650">12 ➔ 17 (+5) ➔ 22 (+5)</text>
          <text x="286" y="182" fill="#34d399" font-size="14" font-weight="750">Target Deduction: [ ? ]</text>
          <text x="300" y="206" fill="#34d399" font-size="14" font-weight="800">25 + 3 = 23 + 5 = 28</text>
        </svg>
        """

    elif topic_folder == "statistics":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Statistics Pie Chart and Frequency Histogram">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#2563eb" stroke-width="1.5"/>
          <!-- Pie Chart on Left (Center: 140, 130, Radius: 85) -->
          <!-- Slice 1: 144 deg (40%) -->
          <path d="M 140,130 L 140,45 A 85,85 0 0,1 216,173 Z" fill="#3b82f6"/>
          <!-- Slice 2: 108 deg (30%) -->
          <path d="M 140,130 L 216,173 A 85,85 0 0,1 68,175 Z" fill="#10b981"/>
          <!-- Slice 3: 72 deg (20%) -->
          <path d="M 140,130 L 68,175 A 85,85 0 0,1 80,70 Z" fill="#f59e0b"/>
          <!-- Slice 4: 36 deg (10%) -->
          <path d="M 140,130 L 80,70 A 85,85 0 0,1 140,45 Z" fill="#ef4444"/>
          
          <text x="145" y="110" fill="#f8fafc" font-size="14" font-weight="800">40%</text>
          <text x="135" y="170" fill="#f8fafc" font-size="14" font-weight="800">30%</text>
          <text x="85" y="130" fill="#f8fafc" font-size="14" font-weight="800">20%</text>
          <text x="105" y="65" fill="#f8fafc" font-size="14" font-weight="800">10%</text>
          
          <!-- Right Panel: Angular Conversion Law -->
          <rect x="280" y="20" width="260" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="296" y="48" fill="#38bdf8" font-size="14" font-weight="800">ANGULAR PROPORTION LAWS</text>
          <text x="296" y="78" fill="#f1f5f9" font-size="14" font-weight="650">Central Angle Formula:</text>
          <text x="312" y="104" fill="#fbbf24" font-size="14" font-weight="750">θᵢ = (fᵢ / Σf) × 360°</text>
          <text x="296" y="134" fill="#f1f5f9" font-size="14" font-weight="650">Exhaustion Invariant:</text>
          <text x="312" y="158" fill="#34d399" font-size="14" font-weight="750">Σθᵢ = 360° (Full Circle)</text>
          <text x="296" y="188" fill="#f1f5f9" font-size="14" font-weight="650">Class Midpoint &amp; Mean:</text>
          <text x="312" y="212" fill="#38bdf8" font-size="14" font-weight="750">x̄ = (Σfᵢxᵢ) / Σfᵢ</text>
        </svg>
        """

    elif topic_folder == "surface-areas-volumes":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Inscribed Sphere Inside Cube Extremum">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#ef4444" stroke-width="1.5"/>
          <!-- Cube Isometric / Front Cross Section (x: 50, y: 35, width: 180, height: 180) -->
          <rect x="50" y="35" width="180" height="180" fill="rgba(56,189,248,0.10)" stroke="#38bdf8" stroke-width="2.5"/>
          
          <!-- Inscribed Sphere Cross-Section (Center: 140, 125, Radius: 90) -->
          <circle cx="140" cy="125" r="90" fill="rgba(239,68,68,0.20)" stroke="#ef4444" stroke-width="3"/>
          <circle cx="140" cy="125" r="4" fill="#f8fafc"/>
          
          <!-- Radius line -->
          <line x1="140" y1="125" x2="230" y2="125" stroke="#fbbf24" stroke-width="2"/>
          <text x="165" y="120" fill="#fbbf24" font-size="14" font-weight="800">r = a/2</text>
          
          <!-- Side length label -->
          <text x="120" y="235" fill="#38bdf8" font-size="14" font-weight="800">Side a</text>
          
          <!-- Right Panel: Volume & Area Ratios -->
          <rect x="280" y="20" width="260" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="296" y="48" fill="#ef4444" font-size="14" font-weight="800">INSCRIBED EXTREMUM</text>
          <text x="296" y="78" fill="#f1f5f9" font-size="14" font-weight="650">Diameter Constraint:</text>
          <text x="312" y="102" fill="#fbbf24" font-size="14" font-weight="750">2r = a  ➔  r = a / 2</text>
          <text x="296" y="132" fill="#f1f5f9" font-size="14" font-weight="650">Volume Ratio:</text>
          <text x="312" y="156" fill="#38bdf8" font-size="14" font-weight="750">V_sphere / V_cube = π / 6 ≈ 52.4%</text>
          <text x="296" y="186" fill="#f1f5f9" font-size="14" font-weight="650">Surface Area Ratio:</text>
          <text x="312" y="210" fill="#34d399" font-size="14" font-weight="750">A_sphere / A_cube = π / 6 ≈ 52.4%</text>
        </svg>
        """

    elif topic_folder == "triangles":
        return """
        <svg viewBox="0 0 560 260" class="qb-svg" style="max-height:260px;width:100%" aria-label="Triangle Congruence Criteria vs AAA Counterexample">
          <rect width="560" height="260" rx="12" fill="#0f172a" stroke="#eab308" stroke-width="1.5"/>
          <!-- Valid Congruent Triangles (SAS) -->
          <polygon points="50,160 130,160 100,80" fill="rgba(52,211,153,0.18)" stroke="#34d399" stroke-width="2.5"/>
          <polygon points="170,160 250,160 220,80" fill="rgba(52,211,153,0.18)" stroke="#34d399" stroke-width="2.5"/>
          <text x="90" y="180" fill="#34d399" font-size="14" font-weight="800">ΔABC ≅ ΔDEF (Congruent)</text>
          
          <!-- AAA Non-Congruence Counterexample Dilated -->
          <!-- Dilated Triangle sharing identical angles but scaled -->
          <polygon points="50,230 110,230 85,190" fill="none" stroke="#f43f5e" stroke-width="2"/>
          <polygon points="140,240 240,240 200,185" fill="none" stroke="#f43f5e" stroke-width="2"/>
          <text x="65" y="255" fill="#fca5a5" font-size="14" font-weight="750">AAA Fallacy: Similar but NOT Congruent!</text>
          
          <!-- Right Panel: Criteria Decision Matrix -->
          <rect x="290" y="20" width="250" height="220" rx="8" fill="#1e293b" stroke="#334155"/>
          <text x="306" y="48" fill="#eab308" font-size="14" font-weight="800">CONGRUENCE CRITERIA</text>
          <text x="306" y="78" fill="#34d399" font-size="14" font-weight="750">✅ Valid Criteria:</text>
          <text x="320" y="102" fill="#f1f5f9" font-size="14" font-weight="650">• SSS, SAS, ASA, AAS, RHS</text>
          <text x="306" y="132" fill="#f43f5e" font-size="14" font-weight="750">❌ Invalid Criteria (Traps):</text>
          <text x="320" y="156" fill="#fca5a5" font-size="14" font-weight="650">• AAA (dilation scale invariance)</text>
          <text x="320" y="178" fill="#fca5a5" font-size="14" font-weight="650">• SSA / ASS (ambiguous 2 triangles)</text>
          <text x="306" y="210" fill="#38bdf8" font-size="14" font-weight="700">Strict Side Warrant is Mandatory</text>
        </svg>
        """
        
    return ""
