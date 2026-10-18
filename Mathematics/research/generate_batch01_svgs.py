import os

figures_dir = 'Mathematics/library/figures'
os.makedirs(figures_dir, exist_ok=True)

# SVG Q20
svg_q20 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 450" role="img" aria-label="Intersecting lines XY and MN with perpendicular ray OP" font-family="system-ui, sans-serif">
  <title>Geometry Diagram for Lines XY and MN</title>
  <desc>Lines XY and MN intersect at point O. Ray OP is perpendicular to line XY. Angle a and b are adjacent angles with ratio 2 to 3.</desc>
  <style>
    .line-main { stroke: #1e293b; stroke-width: 3.5; stroke-linecap: round; }
    .line-ray { stroke: #0284c7; stroke-width: 3.5; stroke-linecap: round; }
    .label { font-size: 22px; font-weight: 600; fill: #0f172a; }
    .angle-label { font-size: 20px; font-weight: 700; fill: #b91c1c; }
    .right-angle { fill: none; stroke: #0284c7; stroke-width: 2.5; }
  </style>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1e293b"/>
    </marker>
    <marker id="arrow-ray" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0284c7"/>
    </marker>
  </defs>

  <!-- Line XY -->
  <line x1="80" y1="280" x2="620" y2="280" class="line-main" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
  <text x="60" y="288" class="label">X</text>
  <text x="635" y="288" class="label">Y</text>

  <!-- Line MN -->
  <line x1="160" y1="120" x2="520" y2="420" class="line-main" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
  <text x="140" y="115" class="label">M</text>
  <text x="535" y="435" class="label">N</text>

  <!-- Point O -->
  <circle cx="340" cy="280" r="5" fill="#0f172a"/>
  <text x="348" y="308" class="label">O</text>

  <!-- Ray OP perpendicular to XY -->
  <line x1="340" y1="280" x2="340" y2="70" class="line-ray" marker-end="url(#arrow-ray)"/>
  <text x="330" y="55" class="label" fill="#0284c7">P</text>

  <!-- Right angle marker at POY -->
  <path d="M 340 250 L 370 250 L 370 280" class="right-angle"/>

  <!-- Angle a and b arcs & annotations -->
  <path d="M 285 280 A 55 55 0 0 1 296 235" fill="none" stroke="#b91c1c" stroke-width="2.5"/>
  <text x="260" y="245" class="angle-label">b</text>

  <path d="M 305 250 A 55 55 0 0 1 340 225" fill="none" stroke="#b91c1c" stroke-width="2.5"/>
  <text x="305" y="215" class="angle-label">a</text>

  <!-- Given Info Box -->
  <rect x="440" y="70" width="230" height="90" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <text x="455" y="105" font-size="18" fill="#334155" font-weight="600">∠POY = 90°</text>
  <text x="455" y="135" font-size="18" fill="#334155" font-weight="600">a : b = 2 : 3</text>
</svg>'''

with open(os.path.join(figures_dir, 'FIG-IMO-G09-2025-26-B-Q020.svg'), 'w', encoding='utf-8') as f:
    f.write(svg_q20)

# SVG Q23
svg_q23 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 420" role="img" aria-label="Rectangle with inscribed triangle and square cutout" font-family="system-ui, sans-serif">
  <title>Area Decomposition of Shaded Geometric Region</title>
  <desc>A rectangle of length 40 cm and breadth 20 cm containing two shaded triangular regions with a 2 cm by 2 cm square cutout.</desc>
  <style>
    .boundary { fill: #ffffff; stroke: #1e293b; stroke-width: 3.5; }
    .shaded-tri { fill: #e0f2fe; stroke: #0369a1; stroke-width: 3; }
    .cutout-square { fill: #fee2e2; stroke: #b91c1c; stroke-width: 2.5; stroke-dasharray: 6,4; }
    .dim-line { stroke: #64748b; stroke-width: 1.5; marker-start: url(#arrow-dim); marker-end: url(#arrow-dim); }
    .dim-text { font-size: 19px; font-weight: 600; fill: #1e293b; text-anchor: middle; }
  </style>
  <defs>
    <marker id="arrow-dim" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 2 L 7 5 L 0 8 z" fill="#64748b"/>
    </marker>
  </defs>

  <!-- Outer Rectangle 40 cm x 20 cm -->
  <rect x="120" y="90" width="500" height="250" class="boundary"/>
  <polygon points="120,90 620,90 120,215" class="shaded-tri"/>
  <polygon points="120,340 620,340 120,215" class="shaded-tri"/>
  <polygon points="620,90 620,340 120,215" fill="#ffffff" stroke="#1e293b" stroke-width="2"/>

  <!-- Square Cutout 2 cm x 2 cm at Left -->
  <rect x="140" y="195" width="40" height="40" class="cutout-square"/>

  <!-- Dimension 40 cm (Top) -->
  <line x1="120" y1="60" x2="620" y2="60" class="dim-line"/>
  <text x="370" y="50" class="dim-text">40 cm</text>

  <!-- Dimension 20 cm (Right) -->
  <line x1="655" y1="90" x2="655" y2="340" class="dim-line"/>
  <text x="700" y="222" class="dim-text">20 cm</text>

  <!-- Dimension 2 cm on square -->
  <text x="160" y="185" font-size="16" font-weight="600" fill="#b91c1c" text-anchor="middle">2 cm</text>
  <text x="110" y="222" font-size="16" font-weight="600" fill="#b91c1c" text-anchor="middle">2 cm</text>
</svg>'''

with open(os.path.join(figures_dir, 'FIG-IMO-G09-2025-26-B-Q023.svg'), 'w', encoding='utf-8') as f:
    f.write(svg_q23)

# SVG Q19: Circle with center O, chords/triangles with angles 50 and 35
svg_q19 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="Cyclic quadrilateral in circle with center O" font-family="system-ui, sans-serif">
  <title>Circle with Center O and Inscribed Quadrilateral ABCD</title>
  <desc>Points A, B, C, D lie on circle with center O. Angle OAB is 50 degrees, angle OCB is 35 degrees. Angle ADC is x.</desc>
  <style>
    .circle-boundary { fill: none; stroke: #1e293b; stroke-width: 3.5; }
    .quad-edge { stroke: #0284c7; stroke-width: 3; fill: none; }
    .radius-line { stroke: #94a3b8; stroke-width: 2; stroke-dasharray: 4,4; }
    .label { font-size: 20px; font-weight: 700; fill: #0f172a; text-anchor: middle; }
    .angle-text { font-size: 16px; font-weight: 600; fill: #b91c1c; text-anchor: middle; }
  </style>
  <circle cx="300" cy="300" r="220" class="circle-boundary"/>
  <circle cx="300" cy="300" r="5" fill="#0f172a"/>
  <text x="300" y="290" class="label">O</text>
  <!-- Vertices: B top, A left, C right, D bottom -->
  <!-- B=(300, 80), A=(110, 390), C=(490, 390), D=(300, 520) -->
  <polygon points="300,80 110,390 300,520 490,390" class="quad-edge"/>
  <line x1="300" y1="300" x2="300" y2="80" class="radius-line"/>
  <line x1="300" y1="300" x2="110" y2="390" class="radius-line"/>
  <line x1="300" y1="300" x2="490" y2="390" class="radius-line"/>
  
  <text x="300" y="60" class="label">B</text>
  <text x="85" y="405" class="label">A</text>
  <text x="515" y="405" class="label">C</text>
  <text x="300" y="555" class="label">D</text>
  
  <text x="175" y="360" class="angle-text">50°</text>
  <text x="425" y="360" class="angle-text">35°</text>
  <text x="300" y="480" class="angle-text" font-size="20">x</text>
</svg>'''

with open(os.path.join(figures_dir, 'FIG-IMO-G09-2025-26-B-Q019.svg'), 'w', encoding='utf-8') as f:
    f.write(svg_q19)

# SVG Q21: Bar chart for Families P, Q, R, S in 2010 and 2020
svg_q21 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 450" role="img" aria-label="Monthly expenditure of families P, Q, R, S" font-family="system-ui, sans-serif">
  <title>Bar Chart: Family Expenditure 2010 vs 2020</title>
  <style>
    .axis { stroke: #1e293b; stroke-width: 2.5; }
    .grid { stroke: #e2e8f0; stroke-width: 1; }
    .bar-2010 { fill: #1e293b; }
    .bar-2020 { fill: #94a3b8; }
    .label { font-size: 15px; font-weight: 600; fill: #334155; text-anchor: middle; }
    .axis-title { font-size: 16px; font-weight: 700; fill: #0f172a; text-anchor: middle; }
  </style>
  <!-- Y axis and title -->
  <line x1="100" y1="360" x2="620" y2="360" class="axis"/>
  <line x1="100" y1="60" x2="100" y2="360" class="axis"/>
  <text x="50" y="210" class="axis-title" transform="rotate(-90 50 210)">Expenditure (in thousands)</text>
  <text x="635" y="365" class="axis-title">X</text>
  <text x="100" y="45" class="axis-title">Y</text>
  
  <!-- Y ticks: 0, 4, 8, 12, 16, 20 -->
  <!-- 360 is 0, 60 is 20 -> 300px = 20 units -> 15px per unit -->
  <text x="80" y="365" class="label">0</text>
  <text x="80" y="305" class="label">4</text>
  <text x="80" y="245" class="label">8</text>
  <text x="80" y="185" class="label">12</text>
  <text x="80" y="125" class="label">16</text>
  <text x="80" y="65" class="label">20</text>
  
  <!-- Legend -->
  <rect x="450" y="40" width="20" height="15" class="bar-2010"/>
  <text x="495" y="53" class="label">2010</text>
  <rect x="540" y="40" width="20" height="15" class="bar-2020"/>
  <text x="585" y="53" class="label">2020</text>
  
  <!-- P: 2010=13 (195px high), 2020=14 (210px high) -->
  <rect x="150" y="165" width="30" height="195" class="bar-2010"/>
  <rect x="180" y="150" width="30" height="210" class="bar-2020"/>
  <text x="180" y="385" class="axis-title">P</text>
  
  <!-- Q: 2010=12 (180px), 2020=18 (270px) -->
  <rect x="260" y="180" width="30" height="180" class="bar-2010"/>
  <rect x="290" y="90" width="30" height="270" class="bar-2020"/>
  <text x="290" y="385" class="axis-title">Q</text>
  
  <!-- R: 2010=10 (150px), 2020=14 (210px) -->
  <rect x="370" y="210" width="30" height="150" class="bar-2010"/>
  <rect x="400" y="150" width="30" height="210" class="bar-2020"/>
  <text x="400" y="385" class="axis-title">R</text>
  
  <!-- S: 2010=14 (210px), 2020=16 (240px) -->
  <rect x="480" y="150" width="30" height="210" class="bar-2010"/>
  <rect x="510" y="120" width="30" height="240" class="bar-2020"/>
  <text x="510" y="385" class="axis-title">S</text>
  
  <text x="350" y="420" class="axis-title">Families</text>
</svg>'''

with open(os.path.join(figures_dir, 'FIG-IMO-G09-2025-26-B-Q021.svg'), 'w', encoding='utf-8') as f:
    f.write(svg_q21)

print('All Batch 1 SVGs generated and saved!')
