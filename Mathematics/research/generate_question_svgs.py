# scratch/generate_question_svgs.py
"""
Generates high-precision, mathematically authentic SVG figures for IMO Class 9 questions.
Each SVG is styled for optimal visibility in dark and light themes, with crisp lines,
clear text, angle arcs, and geometric notation.
"""

def get_svg_for_question(qid):
    svgs = {}

    # 1. SOF-IMO-G09-SAMPLE-2026-27-Q001: Three different positions of a dice
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q001'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Three different positions of a die (Sample Paper 2026-27, Q1)</div>
      <svg viewBox="0 0 540 180" width="100%" height="180" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Common Styles -->
        <defs>
          <linearGradient id="diceGradTop" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.10"/>
          </linearGradient>
          <linearGradient id="diceGradFront" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#818cf8" stop-opacity="0.20"/>
            <stop offset="100%" stop-color="#818cf8" stop-opacity="0.08"/>
          </linearGradient>
          <linearGradient id="diceGradRight" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#c084fc" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#c084fc" stop-opacity="0.10"/>
          </linearGradient>
        </defs>

        <!-- DIE 1 (Top=2, Front=4, Right=5) -->
        <g transform="translate(30, 20)">
          <!-- Top face -->
          <polygon points="50,10 110,10 80,45 20,45" fill="url(#diceGradTop)" stroke="#38bdf8" stroke-width="2"/>
          <text x="65" y="32" font-size="20" font-weight="bold" fill="#38bdf8" text-anchor="middle">2</text>
          <!-- Front face -->
          <polygon points="20,45 80,45 80,115 20,115" fill="url(#diceGradFront)" stroke="#818cf8" stroke-width="2"/>
          <text x="50" y="87" font-size="24" font-weight="bold" fill="#818cf8" text-anchor="middle">4</text>
          <!-- Right face -->
          <polygon points="80,45 110,10 110,80 80,115" fill="url(#diceGradRight)" stroke="#c084fc" stroke-width="2"/>
          <text x="96" y="70" font-size="22" font-weight="bold" fill="#c084fc" text-anchor="middle">5</text>
          <!-- Label -->
          <text x="65" y="142" font-size="13" font-weight="600" fill="#94a3b8" text-anchor="middle">Position (i)</text>
        </g>

        <!-- DIE 2 (Top=6, Front=?, Right=3) -->
        <g transform="translate(205, 20)">
          <!-- Top face -->
          <polygon points="50,10 110,10 80,45 20,45" fill="url(#diceGradTop)" stroke="#38bdf8" stroke-width="2"/>
          <text x="65" y="32" font-size="20" font-weight="bold" fill="#38bdf8" text-anchor="middle">6</text>
          <!-- Front face with Question Mark -->
          <polygon points="20,45 80,45 80,115 20,115" fill="rgba(251, 191, 36, 0.18)" stroke="#fbbf24" stroke-width="2.5"/>
          <text x="50" y="88" font-size="28" font-weight="bold" fill="#fbbf24" text-anchor="middle">?</text>
          <!-- Right face -->
          <polygon points="80,45 110,10 110,80 80,115" fill="url(#diceGradRight)" stroke="#c084fc" stroke-width="2"/>
          <text x="96" y="70" font-size="22" font-weight="bold" fill="#c084fc" text-anchor="middle">3</text>
          <!-- Label -->
          <text x="65" y="142" font-size="13" font-weight="600" fill="#fbbf24" text-anchor="middle">Position (ii)</text>
        </g>

        <!-- DIE 3 (Top=5, Front=6, Right=1) -->
        <g transform="translate(380, 20)">
          <!-- Top face -->
          <polygon points="50,10 110,10 80,45 20,45" fill="url(#diceGradTop)" stroke="#38bdf8" stroke-width="2"/>
          <text x="65" y="32" font-size="20" font-weight="bold" fill="#38bdf8" text-anchor="middle">5</text>
          <!-- Front face -->
          <polygon points="20,45 80,45 80,115 20,115" fill="url(#diceGradFront)" stroke="#818cf8" stroke-width="2"/>
          <text x="50" y="87" font-size="24" font-weight="bold" fill="#818cf8" text-anchor="middle">6</text>
          <!-- Right face -->
          <polygon points="80,45 110,10 110,80 80,115" fill="url(#diceGradRight)" stroke="#c084fc" stroke-width="2"/>
          <text x="96" y="70" font-size="22" font-weight="bold" fill="#c084fc" text-anchor="middle">1</text>
          <!-- Label -->
          <text x="65" y="142" font-size="13" font-weight="600" fill="#94a3b8" text-anchor="middle">Position (iii)</text>
        </g>
      </svg>
    </div>
    '''

    # 2. SOF-IMO-G09-SAMPLE-2026-27-Q003: Radial Number Pattern
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q003'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Radial number circle pattern (Sample Paper 2026-27, Q3)</div>
      <svg viewBox="0 0 320 280" width="100%" height="260" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <g transform="translate(160, 135)">
          <!-- Outer Circle -->
          <circle cx="0" cy="0" r="115" fill="none" stroke="#475569" stroke-width="2.5"/>
          <!-- Inner Circle -->
          <circle cx="0" cy="0" r="62" fill="rgba(56, 189, 248, 0.08)" stroke="#38bdf8" stroke-width="2"/>
          
          <!-- Cross dividing into 4 quadrants -->
          <line x1="-115" y1="0" x2="115" y2="0" stroke="#475569" stroke-width="2"/>
          <line x1="0" y1="-115" x2="0" y2="115" stroke="#475569" stroke-width="2"/>

          <!-- Diagonal radial dividers dividing the outer ring into 8 segments -->
          <line x1="-81" y1="-81" x2="-44" y2="-44" stroke="#475569" stroke-width="1.5"/>
          <line x1="81" y1="-81" x2="44" y2="-44" stroke="#475569" stroke-width="1.5"/>
          <line x1="-81" y1="81" x2="-44" y2="44" stroke="#475569" stroke-width="1.5"/>
          <line x1="81" y1="81" x2="44" y2="44" stroke="#475569" stroke-width="1.5"/>

          <!-- Inner Numbers (Half-sums squared) -->
          <!-- Top-Left: 121 -->
          <text x="-30" y="-22" font-size="18" font-weight="bold" fill="#38bdf8" text-anchor="middle">121</text>
          <!-- Top-Right: 81 -->
          <text x="30" y="-22" font-size="18" font-weight="bold" fill="#38bdf8" text-anchor="middle">81</text>
          <!-- Bottom-Left: 64 -->
          <text x="-30" y="34" font-size="18" font-weight="bold" fill="#38bdf8" text-anchor="middle">64</text>
          <!-- Bottom-Right: ? -->
          <text x="30" y="35" font-size="22" font-weight="bold" fill="#fbbf24" text-anchor="middle">?</text>

          <!-- Outer Numbers in the outer ring -->
          <!-- Top-Left outer pair: 14 and 8 -->
          <text x="-35" y="-85" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">14</text>
          <text x="-88" y="-32" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">8</text>

          <!-- Top-Right outer pair: 6 and 12 -->
          <text x="35" y="-85" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">6</text>
          <text x="88" y="-32" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">12</text>

          <!-- Bottom-Left outer pair: 3 and 13 -->
          <text x="-88" y="44" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">3</text>
          <text x="-35" y="95" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">13</text>

          <!-- Bottom-Right outer pair: 5 and 9 -->
          <text x="88" y="44" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">5</text>
          <text x="35" y="95" font-size="16" font-weight="600" fill="#f1f5f9" text-anchor="middle">9</text>
        </g>
      </svg>
    </div>
    '''

    # 3. SOF-IMO-G09-SAMPLE-2026-27-Q005: Angle relation across parallel families
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q005'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Parallel families $l_1 \parallel l_2$ and $l_3 \parallel l_4$ (Sample Paper 2026-27, Q5)</div>
      <svg viewBox="0 0 380 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#38bdf8"/>
          </marker>
        </defs>

        <!-- Vertical parallel lines l1 and l2 -->
        <line x1="100" y1="210" x2="100" y2="20" stroke="#38bdf8" stroke-width="2.2" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
        <text x="100" y="15" font-size="14" font-weight="bold" fill="#38bdf8" text-anchor="middle">l₁</text>

        <line x1="220" y1="210" x2="220" y2="20" stroke="#38bdf8" stroke-width="2.2" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
        <text x="220" y="15" font-size="14" font-weight="bold" fill="#38bdf8" text-anchor="middle">l₂</text>

        <!-- Slanted parallel lines l3 and l4 -->
        <line x1="50" y1="180" x2="280" y2="40" stroke="#c084fc" stroke-width="2" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
        <text x="290" y="38" font-size="14" font-weight="bold" fill="#c084fc">l₃</text>

        <line x1="50" y1="120" x2="280" y2="-20" stroke="#c084fc" stroke-width="2"/>
        <line x1="140" y1="230" x2="350" y2="90" stroke="#c084fc" stroke-width="2" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
        <text x="360" y="92" font-size="14" font-weight="bold" fill="#c084fc">l₄</text>

        <!-- Oblique dividing ray at l2/l3 intersection -->
        <line x1="170" y1="80" x2="300" y2="175" stroke="#fbbf24" stroke-width="2" marker-end="url(#arrow)"/>

        <!-- Angle x arc at l1/l3 intersection (x=100, y=149) -->
        <path d="M 85,158 A 20 20 0 0 1 100,170" fill="none" stroke="#f43f5e" stroke-width="2"/>
        <text x="78" y="172" font-size="15" font-weight="bold" fill="#f43f5e">x</text>

        <!-- Angle y arcs at intersection (x=220, y=76) -->
        <path d="M 240,64 A 25 25 0 0 1 245,86" fill="none" stroke="#34d399" stroke-width="2"/>
        <text x="252" y="74" font-size="14" font-weight="bold" fill="#34d399">y</text>

        <path d="M 245,86 A 25 25 0 0 1 230,105" fill="none" stroke="#34d399" stroke-width="2"/>
        <text x="242" y="108" font-size="14" font-weight="bold" fill="#34d399">y</text>

        <text x="190" y="215" font-size="12" fill="#94a3b8" text-anchor="middle">Relation: x + 2y = 180° ⇒ y = 90° − x/2</text>
      </svg>
    </div>
    '''

    # 4. SOF-IMO-G09-SAMPLE-2026-27-Q006: Euclid line segment axiom
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q006'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Collinear segment points $P, Q, R, S$ with $PQ = RS$ (Sample Paper 2026-27, Q6)</div>
      <svg viewBox="0 0 460 110" width="100%" height="110" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Main Line Segment -->
        <line x1="40" y1="60" x2="420" y2="60" stroke="#94a3b8" stroke-width="3"/>
        
        <!-- Points P, Q, R, S -->
        <circle cx="50" cy="60" r="5" fill="#38bdf8"/>
        <text x="50" y="85" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">P</text>

        <circle cx="160" cy="60" r="5" fill="#38bdf8"/>
        <text x="160" y="85" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">Q</text>

        <circle cx="300" cy="60" r="5" fill="#38bdf8"/>
        <text x="300" y="85" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">R</text>

        <circle cx="410" cy="60" r="5" fill="#38bdf8"/>
        <text x="410" y="85" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">S</text>

        <!-- Segment Brackets / Marks -->
        <path d="M 50,45 L 50,38 L 160,38 L 160,45" fill="none" stroke="#34d399" stroke-width="2"/>
        <text x="105" y="30" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">PQ</text>

        <path d="M 160,45 L 160,38 L 300,38 L 300,45" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="3,3"/>
        <text x="230" y="30" font-size="13" font-weight="bold" fill="#fbbf24" text-anchor="middle">QR (Common)</text>

        <path d="M 300,45 L 300,38 L 410,38 L 410,45" fill="none" stroke="#34d399" stroke-width="2"/>
        <text x="355" y="30" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">RS</text>

        <text x="230" y="105" font-size="11.5" fill="#94a3b8" text-anchor="middle">Axiom: Equals added to equals produce equal wholes (PQ + QR = RS + QR ⇒ PR = QS)</text>
      </svg>
    </div>
    '''

    # 5. SOF-IMO-G09-SAMPLE-2026-27-Q010: Triangle Median & Perpendiculars
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q010'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Triangle $PQR$ with median $PS$ and perpendiculars $QL, RM$ (Sample Paper 2026-27, Q10)</div>
      <svg viewBox="0 0 380 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Triangle PQR -->
        <!-- P at (140, 30), Q at (50, 150), R at (330, 150) -->
        <polygon points="140,30 50,150 330,150" fill="rgba(56, 189, 248, 0.05)" stroke="#38bdf8" stroke-width="2"/>
        <text x="140" y="22" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">P</text>
        <text x="38" y="155" font-size="16" font-weight="bold" fill="#38bdf8">Q</text>
        <text x="340" y="155" font-size="16" font-weight="bold" fill="#38bdf8">R</text>

        <!-- Median S at (190, 150) -->
        <circle cx="190" cy="150" r="4" fill="#fbbf24"/>
        <text x="190" y="172" font-size="15" font-weight="bold" fill="#fbbf24" text-anchor="middle">S</text>
        <!-- Tick marks for QS = SR -->
        <line x1="115" y1="145" x2="115" y2="155" stroke="#fbbf24" stroke-width="2"/>
        <line x1="120" y1="145" x2="120" y2="155" stroke="#fbbf24" stroke-width="2"/>
        <line x1="255" y1="145" x2="255" y2="155" stroke="#fbbf24" stroke-width="2"/>
        <line x1="260" y1="145" x2="260" y2="155" stroke="#fbbf24" stroke-width="2"/>

        <!-- Median Line PS and Extension -->
        <line x1="140" y1="30" x2="190" y2="150" stroke="#fbbf24" stroke-width="2"/>
        <line x1="190" y1="150" x2="215" y2="210" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="4,4"/>

        <!-- Perpendicular QL to PS: L around (160, 78) -->
        <line x1="50" y1="150" x2="160" y2="78" stroke="#34d399" stroke-width="2"/>
        <circle cx="160" cy="78" r="4" fill="#34d399"/>
        <text x="172" y="80" font-size="14" font-weight="bold" fill="#34d399">L</text>
        <!-- Right angle symbol at L -->
        <rect x="150" y="83" width="8" height="8" fill="none" stroke="#34d399" stroke-width="1.5" transform="rotate(-35 154 87)"/>

        <!-- Perpendicular RM to PS produced: M around (205, 185) -->
        <line x1="330" y1="150" x2="205" y2="185" stroke="#34d399" stroke-width="2"/>
        <circle cx="205" cy="185" r="4" fill="#34d399"/>
        <text x="215" y="200" font-size="14" font-weight="bold" fill="#34d399">M</text>
        <!-- Right angle symbol at M -->
        <rect x="208" y="174" width="8" height="8" fill="none" stroke="#34d399" stroke-width="1.5" transform="rotate(-15 212 178)"/>

        <text x="190" y="226" font-size="11.5" fill="#94a3b8" text-anchor="middle">ΔQLS ≅ ΔRMS ⇒ QL = RM</text>
      </svg>
    </div>
    '''

    # 6. SOF-IMO-G09-L1-2025-26-A-Q031: Multi-angle intersection diagram
    svgs['SOF-IMO-G09-L1-2025-26-A-Q031'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Intersecting lines $PQ, RS$ with ray $OT$ (2025-26 Set A, Q31)</div>
      <svg viewBox="0 0 380 250" width="100%" height="240" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <defs>
          <marker id="arr2" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#38bdf8"/>
          </marker>
        </defs>

        <!-- Intersection point O at (190, 120) -->
        <!-- Line PQ: from (60, 180) to (320, 60) -->
        <line x1="60" y1="180" x2="320" y2="60" stroke="#38bdf8" stroke-width="2.5" marker-start="url(#arr2)" marker-end="url(#arr2)"/>
        <text x="45" y="195" font-size="16" font-weight="bold" fill="#38bdf8">P</text>
        <text x="330" y="60" font-size="16" font-weight="bold" fill="#38bdf8">Q</text>

        <!-- Line RS: from (80, 50) to (300, 190) -->
        <line x1="80" y1="50" x2="300" y2="190" stroke="#c084fc" stroke-width="2.5" marker-start="url(#arr2)" marker-end="url(#arr2)"/>
        <text x="65" y="48" font-size="16" font-weight="bold" fill="#c084fc">R</text>
        <text x="312" y="200" font-size="16" font-weight="bold" fill="#c084fc">S</text>

        <!-- Ray OT: from (190, 120) downwards to (240, 230) -->
        <line x1="190" y1="120" x2="240" y2="230" stroke="#fbbf24" stroke-width="2.2" marker-end="url(#arr2)"/>
        <text x="245" y="245" font-size="16" font-weight="bold" fill="#fbbf24">T</text>

        <circle cx="190" cy="120" r="4" fill="#f1f5f9"/>
        <text x="180" y="112" font-size="14" font-weight="bold" fill="#f1f5f9">O</text>

        <!-- Angle arcs and labels -->
        <!-- Angle POR = 4b (left) -->
        <path d="M 145,140 A 45 45 0 0 1 150,95" fill="none" stroke="#38bdf8" stroke-width="2"/>
        <text x="125" y="125" font-size="15" font-weight="bold" fill="#38bdf8">4b</text>

        <!-- Angle ROQ = 2c (top) -->
        <path d="M 160,100 A 40 40 0 0 1 230,100" fill="none" stroke="#c084fc" stroke-width="2"/>
        <text x="190" y="85" font-size="15" font-weight="bold" fill="#c084fc" text-anchor="middle">2c</text>

        <!-- Angle QOS = a (right) -->
        <path d="M 235,100 A 45 45 0 0 1 228,145" fill="none" stroke="#34d399" stroke-width="2"/>
        <text x="248" y="125" font-size="16" font-weight="bold" fill="#34d399">a</text>

        <!-- Angle POT = 75° (bottom-left) -->
        <path d="M 155,135 A 45 45 0 0 1 200,165" fill="none" stroke="#f43f5e" stroke-width="2"/>
        <text x="165" y="170" font-size="14" font-weight="bold" fill="#f43f5e">75°</text>

        <!-- Angle TOS = b (bottom-right) -->
        <path d="M 205,165 A 45 45 0 0 1 225,142" fill="none" stroke="#fbbf24" stroke-width="2"/>
        <text x="220" y="175" font-size="14" font-weight="bold" fill="#fbbf24">b</text>
      </svg>
    </div>
    '''

    # 7. SOF-IMO-G09-L1-2025-26-A-Q032 & Q033: Examination Marks Pie Chart
    svgs['SOF-IMO-G09-L1-2025-26-A-Q032'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Subject marks distribution pie chart (Total = 720 Marks, 2025-26 Set A, Q32–33)</div>
      <svg viewBox="0 0 340 300" width="100%" height="280" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <g transform="translate(170, 140)">
          <!-- Pie Sectors: Total 360° -->
          <!-- 1. Hindi: 70° (start 0°, end 70°) -->
          <path d="M 0 0 L 110 0 A 110 110 0 0 1 37.6 103.3 Z" fill="#38bdf8" fill-opacity="0.25" stroke="#38bdf8" stroke-width="2"/>
          <text x="65" y="50" font-size="13" font-weight="bold" fill="#38bdf8" text-anchor="middle">Hindi</text>
          <text x="65" y="66" font-size="12" fill="#38bdf8" text-anchor="middle">70°</text>

          <!-- 2. Social Science: 55° (start 70°, end 125°) -->
          <path d="M 0 0 L 37.6 103.3 A 110 110 0 0 1 -63.1 90.1 Z" fill="#c084fc" fill-opacity="0.25" stroke="#c084fc" stroke-width="2"/>
          <text x="-12" y="90" font-size="12" font-weight="bold" fill="#c084fc" text-anchor="middle">Social Sci</text>
          <text x="-12" y="104" font-size="11" fill="#c084fc" text-anchor="middle">55°</text>

          <!-- 3. English: 75° (start 125°, end 200°) -->
          <path d="M 0 0 L -63.1 90.1 A 110 110 0 0 1 -103.4 -37.6 Z" fill="#34d399" fill-opacity="0.25" stroke="#34d399" stroke-width="2"/>
          <text x="-80" y="30" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">English</text>
          <text x="-80" y="46" font-size="12" fill="#34d399" text-anchor="middle">75°</text>

          <!-- 4. Science: 80° (start 200°, end 280°) -->
          <path d="M 0 0 L -103.4 -37.6 A 110 110 0 0 1 19.1 -108.3 Z" fill="#fbbf24" fill-opacity="0.25" stroke="#fbbf24" stroke-width="2"/>
          <text x="-40" y="-70" font-size="13" font-weight="bold" fill="#fbbf24" text-anchor="middle">Science</text>
          <text x="-40" y="-54" font-size="12" fill="#fbbf24" text-anchor="middle">80°</text>

          <!-- 5. Mathematics: 80° (start 280°, end 360°) -->
          <path d="M 0 0 L 19.1 -108.3 A 110 110 0 0 1 110 0 Z" fill="#f43f5e" fill-opacity="0.30" stroke="#f43f5e" stroke-width="2"/>
          <text x="65" y="-45" font-size="14" font-weight="bold" fill="#f43f5e" text-anchor="middle">Maths</text>
          <text x="65" y="-28" font-size="12" fill="#f43f5e" text-anchor="middle">80° (22 2/9%)</text>
        </g>
        <text x="170" y="280" font-size="12" fill="#94a3b8" text-anchor="middle">Total Marks = 720 (1° = 2 marks)</text>
      </svg>
    </div>
    '''
    svgs['SOF-IMO-G09-L1-2025-26-A-Q033'] = svgs['SOF-IMO-G09-L1-2025-26-A-Q032']

    # 8. SOF-IMO-G09-L1-2025-26-A-Q050: Two intersecting circles & parallel chords
    svgs['SOF-IMO-G09-L1-2025-26-A-Q050'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Intersecting circles with secants $AED, BFC$ and parallel chords $EF \parallel CD$ (2025-26 Set A, Q50)</div>
      <svg viewBox="0 0 380 260" width="100%" height="250" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Outer Circle (ABCD cyclic) -->
        <circle cx="190" cy="130" r="110" fill="none" stroke="#38bdf8" stroke-width="2.2"/>
        <text x="190" y="15" font-size="14" font-weight="bold" fill="#38bdf8" text-anchor="middle">Outer Circle</text>

        <!-- Inner Circle passing through A and B -->
        <!-- Center at (150, 130), radius = 70 -->
        <circle cx="160" cy="130" r="80" fill="rgba(192, 132, 252, 0.08)" stroke="#c084fc" stroke-width="2" stroke-dasharray="5,4"/>

        <!-- Common points A (top intersection) and B (bottom intersection) -->
        <!-- Coordinates: A around (180, 22), B around (180, 238) -->
        <circle cx="180" cy="22" r="5" fill="#f1f5f9"/>
        <text x="180" y="14" font-size="16" font-weight="bold" fill="#f1f5f9">A</text>

        <circle cx="180" cy="238" r="5" fill="#f1f5f9"/>
        <text x="180" y="254" font-size="16" font-weight="bold" fill="#f1f5f9">B</text>

        <!-- Common chord AB -->
        <line x1="180" y1="22" x2="180" y2="238" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="3,3"/>

        <!-- Secant AED passing through A: meets inner circle at E(225, 75), outer circle at D(275, 75) -->
        <line x1="180" y1="22" x2="285" y2="82" stroke="#34d399" stroke-width="2"/>
        <circle cx="225" cy="46" r="4" fill="#34d399"/>
        <text x="220" y="38" font-size="15" font-weight="bold" fill="#34d399">E</text>

        <circle cx="275" cy="74" r="4.5" fill="#38bdf8"/>
        <text x="288" y="72" font-size="16" font-weight="bold" fill="#38bdf8">D</text>

        <!-- Secant BFC passing through B: meets inner circle at F(225, 185), outer circle at C(275, 185) -->
        <line x1="180" y1="238" x2="285" y2="178" stroke="#34d399" stroke-width="2"/>
        <circle cx="225" cy="214" r="4" fill="#34d399"/>
        <text x="220" y="232" font-size="15" font-weight="bold" fill="#34d399">F</text>

        <circle cx="275" cy="186" r="4.5" fill="#38bdf8"/>
        <text x="288" y="196" font-size="16" font-weight="bold" fill="#38bdf8">C</text>

        <!-- Chord EF -->
        <line x1="225" y1="46" x2="225" y2="214" stroke="#fbbf24" stroke-width="2.5"/>
        <text x="210" y="135" font-size="14" font-weight="bold" fill="#fbbf24">EF</text>

        <!-- Chord DC -->
        <line x1="275" y1="74" x2="275" y2="186" stroke="#f43f5e" stroke-width="2.5"/>
        <text x="290" y="135" font-size="14" font-weight="bold" fill="#f43f5e">DC</text>

        <text x="190" y="130" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">EF ∥ DC</text>
      </svg>
    </div>
    '''

    # 9. SOF-IMO-G09-L1-2024-25-B-Q016: Student Subject Preferences Pie Chart (400 students)
    svgs['SOF-IMO-G09-L1-2024-25-B-Q016'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Subjects liked by school students (Total = 400 Students, 2024-25 Set B, Q16)</div>
      <svg viewBox="0 0 340 290" width="100%" height="270" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <g transform="translate(170, 135)">
          <!-- Mathematics: 35% (126°) from -90° to 36° -->
          <path d="M 0 0 L 0 -105 A 105 105 0 0 1 85 61.7 Z" fill="#38bdf8" fill-opacity="0.25" stroke="#38bdf8" stroke-width="2"/>
          <text x="45" y="-30" font-size="13" font-weight="bold" fill="#38bdf8" text-anchor="middle">Mathematics</text>
          <text x="45" y="-14" font-size="12" fill="#38bdf8" text-anchor="middle">35% (140)</text>

          <!-- English: 15% (54°) from 36° to 90° -->
          <path d="M 0 0 L 85 61.7 A 105 105 0 0 1 0 105 Z" fill="#34d399" fill-opacity="0.30" stroke="#34d399" stroke-width="2"/>
          <text x="55" y="65" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">English</text>
          <text x="55" y="80" font-size="12" fill="#34d399" text-anchor="middle">15% (60)</text>

          <!-- Science: 25% (90°) from 90° to 180° -->
          <path d="M 0 0 L 0 105 A 105 105 0 0 1 -105 0 Z" fill="#fbbf24" fill-opacity="0.25" stroke="#fbbf24" stroke-width="2"/>
          <text x="-55" y="60" font-size="13" font-weight="bold" fill="#fbbf24" text-anchor="middle">Science</text>
          <text x="-55" y="75" font-size="12" fill="#fbbf24" text-anchor="middle">25% (100)</text>

          <!-- Social Studies: 20% (72°) from 180° to 252° -->
          <path d="M 0 0 L -105 0 A 105 105 0 0 1 -32.4 -99.9 Z" fill="#c084fc" fill-opacity="0.25" stroke="#c084fc" stroke-width="2"/>
          <text x="-65" y="-35" font-size="12" font-weight="bold" fill="#c084fc" text-anchor="middle">Social Studies</text>
          <text x="-65" y="-20" font-size="11" fill="#c084fc" text-anchor="middle">20% (80)</text>

          <!-- Hindi: 5% (18°) from 252° to 270° -->
          <path d="M 0 0 L -32.4 -99.9 A 105 105 0 0 1 0 -105 Z" fill="#f43f5e" fill-opacity="0.30" stroke="#f43f5e" stroke-width="2"/>
          <text x="-18" y="-75" font-size="11" font-weight="bold" fill="#f43f5e" text-anchor="middle">Hindi</text>
          <text x="-18" y="-62" font-size="10" fill="#f43f5e" text-anchor="middle">5%</text>
        </g>
        <text x="170" y="275" font-size="12" fill="#94a3b8" text-anchor="middle">Total Population = 400 Students</text>
      </svg>
    </div>
    '''

    # 10. SOF-IMO-G09-L1-2023-24-A-Q019: Parallel line angle bisectors form rectangle
    svgs['SOF-IMO-G09-L1-2023-24-A-Q019'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Interior angle bisectors of parallel lines $APB \parallel CQD$ form rectangle $PRQS$ (2023-24 Set A, Q19)</div>
      <svg viewBox="0 0 420 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Top Parallel Line APB -->
        <line x1="30" y1="50" x2="390" y2="50" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="40" y="42" font-size="15" font-weight="bold" fill="#38bdf8">A</text>
        <text x="210" y="42" font-size="15" font-weight="bold" fill="#38bdf8">P</text>
        <text x="380" y="42" font-size="15" font-weight="bold" fill="#38bdf8">B</text>

        <!-- Bottom Parallel Line CQD -->
        <line x1="30" y1="180" x2="390" y2="180" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="40" y="198" font-size="15" font-weight="bold" fill="#38bdf8">C</text>
        <text x="210" y="198" font-size="15" font-weight="bold" fill="#38bdf8">Q</text>
        <text x="380" y="198" font-size="15" font-weight="bold" fill="#38bdf8">D</text>

        <!-- Transversal Line through P(210, 50) and Q(210, 180) - slightly oblique for realism -->
        <line x1="170" y1="20" x2="250" y2="210" stroke="#94a3b8" stroke-width="2"/>

        <!-- Shaded Inner Rectangle PRQS -->
        <!-- P at (195, 50), Q at (225, 180). Bisectors meet at R(140, 115) and S(280, 115) -->
        <polygon points="195,50 140,115 225,180 280,115" fill="rgba(52, 211, 153, 0.15)" stroke="#34d399" stroke-width="2.5"/>

        <!-- Bisector rays -->
        <circle cx="195" cy="50" r="4" fill="#f1f5f9"/>
        <circle cx="225" cy="180" r="4" fill="#f1f5f9"/>
        <circle cx="140" cy="115" r="4" fill="#34d399"/>
        <text x="122" y="120" font-size="15" font-weight="bold" fill="#34d399">R</text>

        <circle cx="280" cy="115" r="4" fill="#34d399"/>
        <text x="290" y="120" font-size="15" font-weight="bold" fill="#34d399">S</text>

        <!-- Right angle markers at R, S, P, Q -->
        <rect x="143" y="110" width="8" height="8" fill="none" stroke="#fbbf24" stroke-width="1.5" transform="rotate(45 143 110)"/>
        <rect x="272" y="110" width="8" height="8" fill="none" stroke="#fbbf24" stroke-width="1.5" transform="rotate(45 272 110)"/>

        <text x="210" y="120" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">Rectangle PRQS (4 Right Angles)</text>
      </svg>
    </div>
    '''

    # 11. SOF-IMO-G09-L1-2023-24-A-Q047: Cyclic Quadrilateral Diameter & Inscribed Triangle
    svgs['SOF-IMO-G09-L1-2023-24-A-Q047'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Cyclic quadrilateral $ABCD$ with diameter $AB$ and $\angle ADC = 140^\circ$ (2023-24 Set A, Q47)</div>
      <svg viewBox="0 0 360 250" width="100%" height="240" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Circle -->
        <circle cx="180" cy="125" r="105" fill="rgba(56, 189, 248, 0.05)" stroke="#38bdf8" stroke-width="2.2"/>
        
        <!-- Diameter AB: A at (75, 125), B at (285, 125) -->
        <line x1="75" y1="125" x2="285" y2="125" stroke="#f43f5e" stroke-width="2.5"/>
        <circle cx="75" cy="125" r="4.5" fill="#f43f5e"/>
        <text x="60" y="130" font-size="16" font-weight="bold" fill="#f43f5e">A</text>
        <circle cx="285" cy="125" r="4.5" fill="#f43f5e"/>
        <text x="295" y="130" font-size="16" font-weight="bold" fill="#f43f5e">B</text>
        <text x="180" y="142" font-size="12" fill="#f43f5e" text-anchor="middle">Diameter AB</text>

        <!-- Points C and D on top arc: D around (135, 30), C around (240, 45) -->
        <circle cx="135" cy="30" r="4.5" fill="#38bdf8"/>
        <text x="130" y="20" font-size="16" font-weight="bold" fill="#38bdf8">D</text>

        <circle cx="240" cy="45" r="4.5" fill="#38bdf8"/>
        <text x="250" y="40" font-size="16" font-weight="bold" fill="#38bdf8">C</text>

        <!-- Polygon ABCD -->
        <polygon points="75,125 135,30 240,45 285,125" fill="none" stroke="#38bdf8" stroke-width="2"/>
        
        <!-- Diagonal AC -->
        <line x1="75" y1="125" x2="240" y2="45" stroke="#34d399" stroke-width="2"/>

        <!-- Angle in semicircle: angle ACB = 90° -->
        <line x1="240" y1="45" x2="285" y2="125" stroke="#34d399" stroke-width="2"/>
        <rect x="230" y="52" width="10" height="10" fill="none" stroke="#fbbf24" stroke-width="1.5" transform="rotate(25 235 57)"/>
        <text x="245" y="70" font-size="12" font-weight="bold" fill="#fbbf24">90°</text>

        <!-- Angle ADC = 140° -->
        <text x="135" y="55" font-size="14" font-weight="bold" fill="#c084fc">140°</text>

        <!-- Target angle BAC = 50° -->
        <text x="110" y="118" font-size="14" font-weight="bold" fill="#34d399">50°</text>

        <text x="180" y="235" font-size="11.5" fill="#94a3b8" text-anchor="middle">∠ABC = 180°−140° = 40° ⇒ ∠BAC = 90°−40° = 50°</text>
      </svg>
    </div>
    '''

    # 12. SOF-IMO-G09-L1-2023-24-A-Q029: Right Triangle 24-32-40 and Altitude
    svgs['SOF-IMO-G09-L1-2023-24-A-Q029'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Right triangle with legs 24 cm, 32 cm and hypotenuse 40 cm (2023-24 Set A, Q29)</div>
      <svg viewBox="0 0 380 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Right Triangle ABC with right angle at B(80, 180) -->
        <!-- A at (80, 40), C at (280, 180) -->
        <polygon points="80,40 80,180 280,180" fill="rgba(56, 189, 248, 0.08)" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="80" y="30" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">A</text>
        <text x="65" y="195" font-size="16" font-weight="bold" fill="#38bdf8">B</text>
        <text x="290" y="195" font-size="16" font-weight="bold" fill="#38bdf8">C</text>

        <!-- Right angle symbol at B -->
        <rect x="80" y="165" width="15" height="15" fill="none" stroke="#fbbf24" stroke-width="2"/>

        <!-- Sides -->
        <!-- Side AB = 32 cm (Altitude to base BC) -->
        <text x="50" y="115" font-size="14" font-weight="bold" fill="#34d399">32 cm</text>
        <text x="50" y="130" font-size="11" fill="#94a3b8">(Altitude)</text>

        <!-- Base BC = 24 cm (Smallest side) -->
        <text x="180" y="205" font-size="14" font-weight="bold" fill="#fbbf24" text-anchor="middle">24 cm (Smallest Side)</text>

        <!-- Hypotenuse AC = 40 cm -->
        <text x="195" y="100" font-size="14" font-weight="bold" fill="#c084fc">40 cm</text>

        <text x="190" y="225" font-size="11.5" fill="#94a3b8" text-anchor="middle">24² + 32² = 576 + 1024 = 1600 = 40² ⇒ Altitude to 24 cm side is 32 cm</text>
      </svg>
    </div>
    '''

    # 13. SOF-IMO-G09-L1-2023-24-A-Q027: Linear graph intercept at x=0
    svgs['SOF-IMO-G09-L1-2023-24-A-Q027'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Linear graph $4x + y = 12$ crossing axes (2023-24 Set A, Q27)</div>
      <svg viewBox="0 0 340 240" width="100%" height="230" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Grid axes -->
        <line x1="40" y1="200" x2="300" y2="200" stroke="#94a3b8" stroke-width="2"/>
        <text x="310" y="205" font-size="14" font-weight="bold" fill="#94a3b8">X</text>

        <line x1="80" y1="220" x2="80" y2="20" stroke="#94a3b8" stroke-width="2"/>
        <text x="80" y="15" font-size="14" font-weight="bold" fill="#94a3b8" text-anchor="middle">Y</text>

        <!-- Origin -->
        <circle cx="80" cy="200" r="3" fill="#94a3b8"/>
        <text x="65" y="215" font-size="12" fill="#94a3b8">O(0,0)</text>

        <!-- Line 4x + y = 12: intersects y-axis at (0, 12), x-axis at (3, 0) -->
        <line x1="60" y1="40" x2="260" y2="220" stroke="#f43f5e" stroke-width="2.5"/>

        <!-- Y-intercept point (0, 12) at (80, 58) -->
        <circle cx="80" cy="58" r="5" fill="#38bdf8"/>
        <text x="92" y="62" font-size="14" font-weight="bold" fill="#38bdf8">(0, 12) [Y-Intercept]</text>

        <!-- X-intercept point (3, 0) at (238, 200) -->
        <circle cx="238" cy="200" r="5" fill="#34d399"/>
        <text x="238" y="220" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">(3, 0)</text>

        <text x="180" y="130" font-size="13" font-weight="bold" fill="#f43f5e">4x + y = 12</text>
      </svg>
    </div>
    '''

    # 14. SOF-IMO-G09-L1-2024-25-B-Q020: Abscissa and Ordinate on Cartesian Plane
    svgs['SOF-IMO-G09-L1-2024-25-B-Q020'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Cartesian coordinates of points $A(10, 5)$ and $B(-7, -4)$ (2024-25 Set B, Q20)</div>
      <svg viewBox="0 0 380 240" width="100%" height="230" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Axes -->
        <line x1="30" y1="120" x2="350" y2="120" stroke="#64748b" stroke-width="2"/>
        <text x="360" y="125" font-size="14" font-weight="bold" fill="#64748b">X</text>

        <line x1="170" y1="220" x2="170" y2="20" stroke="#64748b" stroke-width="2"/>
        <text x="170" y="15" font-size="14" font-weight="bold" fill="#64748b" text-anchor="middle">Y</text>

        <!-- Point A(10, 5) in Quadrant I: around (290, 60) -->
        <circle cx="290" cy="60" r="5" fill="#38bdf8"/>
        <text x="300" y="55" font-size="14" font-weight="bold" fill="#38bdf8">A(10, 5)</text>
        <line x1="290" y1="60" x2="290" y2="120" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3,3"/>
        <text x="290" y="138" font-size="12" font-weight="bold" fill="#38bdf8" text-anchor="middle">10 (Abscissa)</text>

        <!-- Point B(-7, -4) in Quadrant III: around (90, 175) -->
        <circle cx="90" cy="175" r="5" fill="#fbbf24"/>
        <text x="80" y="195" font-size="14" font-weight="bold" fill="#fbbf24" text-anchor="end">B(-7, -4)</text>
        <line x1="90" y1="175" x2="170" y2="175" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3,3"/>
        <text x="180" y="180" font-size="12" font-weight="bold" fill="#fbbf24">-4 (Ordinate)</text>

        <text x="190" y="230" font-size="12" fill="#34d399" text-anchor="middle">(Abscissa of A) − (Ordinate of B) = 10 − (-4) = 14</text>
      </svg>
    </div>
    '''

    # 15. SOF-IMO-G09-L1-2023-24-A-Q017: Two Cones with Heights Ratio 4:9
    svgs['SOF-IMO-G09-L1-2023-24-A-Q017'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Two cones with identical base radii $r$ and heights ratio $4:9$ (2023-24 Set A, Q17)</div>
      <svg viewBox="0 0 380 200" width="100%" height="190" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Cone 1 (Height = 4 units) -->
        <g transform="translate(60, 20)">
          <polygon points="50,60 10,140 90,140" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="2"/>
          <ellipse cx="50" cy="140" rx="40" ry="12" fill="rgba(56, 189, 248, 0.25)" stroke="#38bdf8" stroke-width="2"/>
          <!-- Height Line -->
          <line x1="50" y1="60" x2="50" y2="140" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="3,3"/>
          <text x="50" y="50" font-size="13" font-weight="bold" fill="#38bdf8" text-anchor="middle">Cone 1</text>
          <text x="50" y="170" font-size="13" font-weight="bold" fill="#fbbf24" text-anchor="middle">h₁ = 4k</text>
          <text x="50" y="186" font-size="11" fill="#94a3b8" text-anchor="middle">V₁ = 4π m³</text>
        </g>

        <!-- Cone 2 (Height = 9 units) -->
        <g transform="translate(220, 20)">
          <polygon points="50,15 10,140 90,140" fill="rgba(192, 132, 252, 0.15)" stroke="#c084fc" stroke-width="2"/>
          <ellipse cx="50" cy="140" rx="40" ry="12" fill="rgba(192, 132, 252, 0.25)" stroke="#c084fc" stroke-width="2"/>
          <!-- Height Line -->
          <line x1="50" y1="15" x2="50" y2="140" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="3,3"/>
          <text x="50" y="10" font-size="13" font-weight="bold" fill="#c084fc" text-anchor="middle">Cone 2</text>
          <text x="50" y="170" font-size="13" font-weight="bold" fill="#fbbf24" text-anchor="middle">h₂ = 9k</text>
          <text x="50" y="186" font-size="11" fill="#94a3b8" text-anchor="middle">V₂ = 9π m³</text>
        </g>
      </svg>
    </div>
    '''

    # 16. SOF-IMO-G09-SAMPLE-2026-27-Q008: Conical Tent Geometry
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q008'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Conical tent with ground area $44\\text{ m}^2$ and air volume $220\\text{ m}^3$ (Sample Paper 2026-27, Q8)</div>
      <svg viewBox="0 0 340 210" width="100%" height="200" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <g transform="translate(170, 20)">
          <!-- Cone Outline -->
          <polygon points="0,15 -80,140 80,140" fill="rgba(52, 211, 153, 0.12)" stroke="#34d399" stroke-width="2.2"/>
          <!-- Base Ellipse -->
          <ellipse cx="0" cy="140" rx="80" ry="20" fill="rgba(52, 211, 153, 0.22)" stroke="#34d399" stroke-width="2.2"/>
          
          <!-- Central Height h -->
          <line x1="0" y1="15" x2="0" y2="140" stroke="#fbbf24" stroke-width="2" stroke-dasharray="4,4"/>
          <text x="14" y="80" font-size="14" font-weight="bold" fill="#fbbf24">h = 15 m</text>

          <!-- Base Radius r -->
          <line x1="0" y1="140" x2="80" y2="140" stroke="#38bdf8" stroke-width="2"/>
          <text x="40" y="135" font-size="13" font-weight="bold" fill="#38bdf8">r</text>

          <text x="0" y="175" font-size="13" font-weight="bold" fill="#f1f5f9" text-anchor="middle">Base Area A = 44 m²</text>
          <text x="0" y="195" font-size="12" fill="#94a3b8" text-anchor="middle">Volume = (1/3) × 44 × h = 220 m³ ⇒ h = 15 m</text>
        </g>
      </svg>
    </div>
    '''

    # 17. SOF-IMO-G09-L1-2024-25-B-Q027: Two Dice Event Sample Space Grid
    svgs['SOF-IMO-G09-L1-2024-25-B-Q027'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Two dice sample space ($6 \\times 6 = 36$ outcomes) (2024-25 Set B, Q27)</div>
      <svg viewBox="0 0 380 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <g transform="translate(60, 25)">
          <!-- Axis labels -->
          <text x="130" y="-8" font-size="13" font-weight="bold" fill="#38bdf8" text-anchor="middle">Die 2 (1 to 6)</text>
          <text x="-35" y="85" font-size="13" font-weight="bold" fill="#c084fc" text-anchor="middle" transform="rotate(-90 -35 85)">Die 1 (1 to 6)</text>
          
          <!-- 6x6 Grid of Outcome Cells -->
          <!-- We draw grid with highlighted diagonal and sums -->
          <rect x="0" y="0" width="260" height="170" fill="rgba(30, 41, 59, 0.5)" stroke="#475569" stroke-width="1.5" rx="6"/>
          
          <!-- Sample representations -->
          <g font-size="11" fill="#94a3b8" text-anchor="middle">
            <text x="25" y="25">(1,1)</text><text x="70" y="25">(1,2)</text><text x="115" y="25">(1,3)</text><text x="160" y="25">(1,4)</text><text x="205" y="25">(1,5)</text><text x="245" y="25">(1,6)</text>
            <text x="25" y="55">(2,1)</text><text x="70" y="55">(2,2)</text><text x="115" y="55">(2,3)</text><text x="160" y="55">(2,4)</text><text x="205" y="55">(2,5)</text><text x="245" y="55">(2,6)</text>
            <text x="25" y="85">(3,1)</text><text x="70" y="85">(3,2)</text><text x="115" y="85">(3,3)</text><text x="160" y="85">(3,4)</text><text x="205" y="85">(3,5)</text><text x="245" y="85">(3,6)</text>
            <text x="25" y="115">(4,1)</text><text x="70" y="115">(4,2)</text><text x="115" y="115">(4,3)</text><text x="160" y="115">(4,4)</text><text x="205" y="115">(4,5)</text><text x="245" y="115">(4,6)</text>
            <text x="25" y="145">(5,1)</text><text x="70" y="145">(5,2)</text><text x="115" y="145">(5,3)</text><text x="160" y="145">(5,4)</text><text x="205" y="145">(5,5)</text><text x="245" y="145">(5,6)</text>
          </g>
          <text x="130" y="195" font-size="12" fill="#34d399" text-anchor="middle">Total Outcomes n(S) = 6 × 6 = 36</text>
        </g>
      </svg>
    </div>
    '''

    # 18. SOF-IMO-G09-L1-2024-25-B-Q035: Scalene Triangle with sides 13, 17, 20
    svgs['SOF-IMO-G09-L1-2024-25-B-Q035'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Triangle $ABC$ with sides $13\\text{ cm}, 17\\text{ cm}, 20\\text{ cm}$ (2024-25 Set B, Q35)</div>
      <svg viewBox="0 0 360 210" width="100%" height="200" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Triangle ABC: A at (110, 40), B at (50, 160), C at (290, 160) -->
        <polygon points="110,40 50,160 290,160" fill="rgba(56, 189, 248, 0.08)" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="110" y="30" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">A</text>
        <text x="35" y="170" font-size="16" font-weight="bold" fill="#38bdf8">B</text>
        <text x="300" y="170" font-size="16" font-weight="bold" fill="#38bdf8">C</text>

        <!-- Sides -->
        <!-- Side AB = 13 cm -->
        <text x="65" y="95" font-size="14" font-weight="bold" fill="#fbbf24">13 cm</text>
        <!-- Side AC = 17 cm -->
        <text x="215" y="95" font-size="14" font-weight="bold" fill="#c084fc">17 cm</text>
        <!-- Base BC = 20 cm -->
        <text x="170" y="185" font-size="14" font-weight="bold" fill="#34d399" text-anchor="middle">20 cm</text>

        <text x="170" y="205" font-size="11.5" fill="#94a3b8" text-anchor="middle">Semiperimeter s = (13+17+20)/2 = 25 cm ⇒ Area = √(25×12×8×5) = 20√30 cm²</text>
      </svg>
    </div>
    '''

    # 19. SOF-IMO-G09-L1-2023-24-A-Q050: Coordinate reflection across axes
    svgs['SOF-IMO-G09-L1-2023-24-A-Q050'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Reflection of point $P(x, y)$ across coordinate axes (2023-24 Set A, Q50)</div>
      <svg viewBox="0 0 360 240" width="100%" height="230" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Axes -->
        <line x1="30" y1="120" x2="330" y2="120" stroke="#64748b" stroke-width="2"/>
        <text x="340" y="125" font-size="14" font-weight="bold" fill="#64748b">X</text>

        <line x1="180" y1="220" x2="180" y2="20" stroke="#64748b" stroke-width="2"/>
        <text x="180" y="15" font-size="14" font-weight="bold" fill="#64748b" text-anchor="middle">Y</text>

        <!-- Point P(x, y) in Quadrant I -->
        <circle cx="260" cy="55" r="5" fill="#38bdf8"/>
        <text x="270" y="52" font-size="14" font-weight="bold" fill="#38bdf8">P(x, y)</text>

        <!-- Reflection across X-axis: P'(x, -y) in Quadrant IV -->
        <circle cx="260" cy="185" r="5" fill="#f43f5e"/>
        <text x="270" y="195" font-size="14" font-weight="bold" fill="#f43f5e">P'(x, -y)</text>
        <line x1="260" y1="55" x2="260" y2="185" stroke="#f43f5e" stroke-width="1.8" stroke-dasharray="3,3"/>

        <!-- Reflection across Y-axis: P''(-x, y) in Quadrant II -->
        <circle cx="100" cy="55" r="5" fill="#34d399"/>
        <text x="90" y="52" font-size="14" font-weight="bold" fill="#34d399" text-anchor="end">P''(-x, y)</text>
        <line x1="260" y1="55" x2="100" y2="55" stroke="#34d399" stroke-width="1.8" stroke-dasharray="3,3"/>

        <text x="180" y="232" font-size="11.5" fill="#94a3b8" text-anchor="middle">Reflection across X-axis negates ordinate; across Y-axis negates abscissa</text>
      </svg>
    </div>
    '''

    # 20. SOF-IMO-G09-L1-2023-24-A-Q033: Euclid's Parallel Postulate (Playfair's Axiom)
    svgs['SOF-IMO-G09-L1-2023-24-A-Q033'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Playfair's Axiom: Unique parallel line $m$ through external point $P$ (2023-24 Set A, Q33)</div>
      <svg viewBox="0 0 380 180" width="100%" height="170" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Given line l -->
        <line x1="40" y1="130" x2="340" y2="130" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="350" y="135" font-size="15" font-weight="bold" fill="#38bdf8">l</text>

        <!-- External point P -->
        <circle cx="190" cy="50" r="5" fill="#fbbf24"/>
        <text x="190" y="38" font-size="16" font-weight="bold" fill="#fbbf24" text-anchor="middle">P ∉ l</text>

        <!-- Unique parallel line m through P -->
        <line x1="40" y1="50" x2="340" y2="50" stroke="#34d399" stroke-width="2.5"/>
        <text x="350" y="55" font-size="15" font-weight="bold" fill="#34d399">m ∥ l</text>

        <!-- Intersecting non-parallel line n through P -->
        <line x1="70" y1="15" x2="310" y2="85" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>
        <text x="320" y="90" font-size="13" fill="#94a3b8">n</text>

        <text x="190" y="165" font-size="12" fill="#94a3b8" text-anchor="middle">Euclid Postulate 5 Equivalent: Exactly one line through P is parallel to l</text>
      </svg>
    </div>
    '''

    # 21. SOF-IMO-G09-SAMPLE-2026-27-Q004: Tabulated linear rule y = 2x - 1
    svgs['SOF-IMO-G09-SAMPLE-2026-27-Q004'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Linear equation $y = 2x - 1$ plotted through tabulated points (Sample Paper 2026-27, Q4)</div>
      <svg viewBox="0 0 360 220" width="100%" height="210" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Axes -->
        <line x1="30" y1="130" x2="330" y2="130" stroke="#64748b" stroke-width="2"/>
        <text x="340" y="135" font-size="14" font-weight="bold" fill="#64748b">X</text>

        <line x1="160" y1="205" x2="160" y2="15" stroke="#64748b" stroke-width="2"/>
        <text x="160" y="12" font-size="14" font-weight="bold" fill="#64748b" text-anchor="middle">Y</text>

        <!-- Line y = 2x - 1 -->
        <line x1="70" y1="195" x2="250" y2="35" stroke="#38bdf8" stroke-width="2.5"/>

        <!-- Points: (-1,-3) at (120, 170), (0,-1) at (160, 145), (1,1) at (200, 115), (2,3) at (240, 65) -->
        <circle cx="120" cy="170" r="4.5" fill="#fbbf24"/>
        <text x="110" y="185" font-size="12" font-weight="bold" fill="#fbbf24">(-1, -3)</text>

        <circle cx="160" cy="145" r="4.5" fill="#fbbf24"/>
        <text x="175" y="152" font-size="12" font-weight="bold" fill="#fbbf24">(0, -1)</text>

        <circle cx="200" cy="115" r="4.5" fill="#fbbf24"/>
        <text x="210" y="115" font-size="12" font-weight="bold" fill="#fbbf24">(1, 1)</text>

        <circle cx="240" cy="65" r="4.5" fill="#fbbf24"/>
        <text x="250" y="65" font-size="12" font-weight="bold" fill="#fbbf24">(2, 3)</text>

        <text x="210" y="40" font-size="14" font-weight="bold" fill="#38bdf8">y = 2x − 1</text>
      </svg>
    </div>
    '''

    # 22. SOF-IMO-G09-L1-2024-25-B-Q029: Ratio of Cone Curved Surface Areas
    svgs['SOF-IMO-G09-L1-2024-25-B-Q029'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Cones with curved area relation $\\pi r_1 l_1 = 2\\pi r_2 l_2$ and $l_2 = 2l_1$ (2024-25 Set B, Q29)</div>
      <svg viewBox="0 0 380 200" width="100%" height="190" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <!-- Cone 1: Wide base r1 = 4, slant height l1 = 1 -->
        <g transform="translate(60, 20)">
          <polygon points="60,30 -10,140 130,140" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="2"/>
          <ellipse cx="60" cy="140" rx="70" ry="16" fill="rgba(56, 189, 248, 0.25)" stroke="#38bdf8" stroke-width="2"/>
          <line x1="60" y1="140" x2="130" y2="140" stroke="#fbbf24" stroke-width="2"/>
          <text x="95" y="135" font-size="13" font-weight="bold" fill="#fbbf24">r₁ = 4</text>
          <text x="60" y="20" font-size="13" font-weight="bold" fill="#38bdf8" text-anchor="middle">Cone 1</text>
          <text x="60" y="180" font-size="12" fill="#94a3b8" text-anchor="middle">CSA₁ = 2 × CSA₂</text>
        </g>

        <!-- Cone 2: Slant height l2 = 2l1, radius r2 = 1 -->
        <g transform="translate(250, 20)">
          <polygon points="40,10 15,140 65,140" fill="rgba(192, 132, 252, 0.15)" stroke="#c084fc" stroke-width="2"/>
          <ellipse cx="40" cy="140" rx="25" ry="10" fill="rgba(192, 132, 252, 0.25)" stroke="#c084fc" stroke-width="2"/>
          <line x1="40" y1="140" x2="65" y2="140" stroke="#fbbf24" stroke-width="2"/>
          <text x="52" y="135" font-size="12" font-weight="bold" fill="#fbbf24">r₂ = 1</text>
          <text x="40" y="5" font-size="13" font-weight="bold" fill="#c084fc" text-anchor="middle">Cone 2</text>
          <text x="40" y="180" font-size="12" fill="#94a3b8" text-anchor="middle">l₂ = 2l₁ ⇒ r₁ : r₂ = 4 : 1</text>
        </g>
      </svg>
    </div>
    '''

    # 23. SOF-IMO-G09-L1-2025-26-A-Q046: Coordinate reflections & mirror image
    svgs['SOF-IMO-G09-L1-2025-26-A-Q046'] = r'''
    <div class="qb-figure-wrap">
      <div class="qb-figure-caption"><strong>Figure:</strong> Mirror image of $(4, 9)$ along $x$-axis giving $(4, -9)$ (2025-26 Set A, Q46)</div>
      <svg viewBox="0 0 340 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" class="qb-svg">
        <line x1="30" y1="115" x2="310" y2="115" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="320" y="120" font-size="14" font-weight="bold" fill="#38bdf8">X-axis (Mirror)</text>

        <line x1="120" y1="210" x2="120" y2="20" stroke="#64748b" stroke-width="1.8"/>
        <text x="120" y="15" font-size="14" font-weight="bold" fill="#64748b" text-anchor="middle">Y</text>

        <!-- Point (4, 9) -->
        <circle cx="210" cy="45" r="5" fill="#34d399"/>
        <text x="220" y="45" font-size="14" font-weight="bold" fill="#34d399">(4, 9)</text>

        <!-- Mirror reflection across x-axis: (4, -9) -->
        <circle cx="210" cy="185" r="5" fill="#f43f5e"/>
        <text x="220" y="195" font-size="14" font-weight="bold" fill="#f43f5e">(4, -9) [Mirror Image]</text>

        <line x1="210" y1="45" x2="210" y2="185" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="4,4"/>
        <text x="170" y="222" font-size="11.5" fill="#94a3b8" text-anchor="middle">Reflection across x-axis: (x, y) → (x, -y)</text>
      </svg>
    </div>
    '''

    return svgs.get(qid, '')

