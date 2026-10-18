# scripts/elevate_planar_motion_blueprints.py
"""
Elevate Upstream Planar Motion Blueprints to Schema v2.0.0 and reciprocally align with TopicAdapters.v1.json.
Authority: Golden Benchmark Fixtures (core1A-motion-in-a-plane-full-combined-fixed.pdf & Emailing physics-motion-2d-revised-core2-v2.pdf)
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 1. First-Move Atlas (11 rows, 1 per competency)
FIRST_MOVE_ATLAS = [
    {
        "competency_id": "PLANE-01",
        "cue": "2D position vector r(t) or velocity v(t) with orthogonal (x, y) coordinates",
        "representation": "Orthogonal Cartesian coordinate frame (x, y) with independent 1D projections",
        "first_executable_move": "Decompose motion into independent perpendicular components: r(t) = x(t) i + y(t) j and v(t) = v_x(t) i + v_y(t) j, linked solely by clock t",
        "anti_pattern": "Mixing horizontal and vertical kinematic variables inside a single 1D equation"
    },
    {
        "competency_id": "PLANE-02",
        "cue": "Constant acceleration in 2D with vector quantities u and a",
        "representation": "Vector UVATS table separating horizontal (i) and vertical (j) components",
        "first_executable_move": "Apply 2D vector kinematic quad equations: v = u + at and Delta r = ut + 0.5*a*t^2 independently along each orthogonal axis",
        "anti_pattern": "Adding vector magnitudes algebraically without resolving into orthogonal components"
    },
    {
        "competency_id": "PLANE-03",
        "cue": "Horizontal launch from cliff or tower with speed u and zero initial vertical velocity (u_y = 0)",
        "representation": "Origin at launch edge, +x horizontal, +y downward (or +y upward with launch at y = h)",
        "first_executable_move": "Solve vertical free-fall time first: t_fall = sqrt(2h / g), then determine horizontal range x = u * t_fall",
        "anti_pattern": "Believing higher horizontal launch velocity changes the vertical time of fall"
    },
    {
        "competency_id": "PLANE-04",
        "cue": "Oblique ground-to-ground projectile launch at elevation angle theta above horizontal",
        "representation": "Launch velocity decomposed into u_x = u cos theta and u_y = u sin theta; apex summit at v_y = 0",
        "first_executable_move": "Set vertical apex velocity v_y = u sin theta - gt = 0 => t_apex = (u sin theta) / g; total flight time T = (2u sin theta) / g",
        "anti_pattern": "Setting total velocity to zero at the apex (horizontal speed u_x = u cos theta remains strictly non-zero)"
    },
    {
        "competency_id": "PLANE-05",
        "cue": "Ground-to-ground horizontal range, maximum range, or landing impact coordinate",
        "representation": "Parabolic trajectory arc with landing coordinates (R, 0)",
        "first_executable_move": "Compute range R = u_x * T = (u^2 sin 2theta) / g; maximum range occurs at theta = 45 deg where R_max = u^2 / g",
        "anti_pattern": "Applying the level-ground range formula R = (u^2 sin 2theta)/g when launch and landing heights are unequal"
    },
    {
        "competency_id": "PLANE-06",
        "cue": "Two projectiles with equal launch speeds achieving identical horizontal range",
        "representation": "Dual trajectory arcs showing steep lob vs flat drive with complementary launch angles",
        "first_executable_move": "Apply complementary angle degeneracy: theta_1 + theta_2 = 90 deg => sin(2*theta_1) = sin(2*theta_2); ranges are identical, flight times scale as T1 / T2 = tan theta_1",
        "anti_pattern": "Assuming equal range implies equal flight times or equal maximum apex heights"
    },
    {
        "competency_id": "PLANE-07",
        "cue": "Trajectory profile curve, target clearance at (x, y), or path equation without time t",
        "representation": "Cartesian trajectory curve y(x) plotted on spatial (x, y) coordinate grid",
        "first_executable_move": "Substitute t = x / (u cos theta) into y(t) to form trajectory equation y = x tan theta - (g x^2) / (2 u^2 cos^2 theta) = x tan theta * (1 - x / R)",
        "anti_pattern": "Attempting multi-variable time quadratics when the Cartesian trajectory equation connects x and y directly"
    },
    {
        "competency_id": "PLANE-08",
        "cue": "Boat crossing river with stream current velocity v_r and engine speed v_b",
        "representation": "Vector velocity triangle: v_net = v_b/r + v_r across river width W",
        "first_executable_move": "For shortest time, steer perpendicular to bank (theta = 90 deg, t_min = W / v_b); for zero drift (v_b > v_r), steer upstream at sin alpha = v_r / v_b",
        "anti_pattern": "Steering upstream when asked for shortest crossing time (shortest time strictly requires heading directly across)"
    },
    {
        "competency_id": "PLANE-09",
        "cue": "Rain falling vertically while observer moves horizontally, or aircraft in crosswind",
        "representation": "Relative velocity vector subtraction triangle: v_rain/man = v_rain - v_man",
        "first_executable_move": "Construct relative velocity vector v_rel = -v_rain j - v_man i; tilt umbrella into oncoming relative rain at tan theta = v_man / v_rain from vertical",
        "anti_pattern": "Tilting umbrella backward or along walking direction instead of into the oncoming relative rain vector"
    },
    {
        "competency_id": "PLANE-10",
        "cue": "Particle moving along circular path of radius R at uniform speed v or angular velocity omega",
        "representation": "Circular orbit with tangent velocity vector v and radially inward normal acceleration a_c",
        "first_executable_move": "Apply centripetal acceleration invariant: a_c = v^2 / R = omega^2 * R = 4*pi^2*R / T^2 directed strictly toward orbit center",
        "anti_pattern": "Claiming uniform circular motion has zero acceleration because scalar speed |v| is constant"
    },
    {
        "competency_id": "PLANE-11",
        "cue": "Particle moving along general curved path with changing speed",
        "representation": "Intrinsic Frenet-Serret coordinate frame: unit tangent u_t and unit inward normal u_n",
        "first_executable_move": "Decouple acceleration into tangential a_t = dv/dt (changes speed) and normal a_n = v^2 / rho (changes direction); total |a| = sqrt(a_t^2 + a_n^2)",
        "anti_pattern": "Conflating total acceleration with centripetal acceleration in non-uniform curvilinear motion"
    }
]

# 2. Canonical Strategy (4 Stages)
CANONICAL_STRATEGY = {
    "stage_1_choose": {
        "name": "Orthogonal Frame & Origin Declaration",
        "action": "Declare mutually perpendicular spatial axes (x, y), reference directions (+x horizontal, +y vertical), and clock zero t = 0.",
        "invariant": "Physical trajectory geometry is invariant under spatial coordinate translation and rotation."
    },
    "stage_2_represent": {
        "name": "Decoupled Vector & Relative State Representation",
        "action": "Decompose vectors into orthogonal components (u_x = u cos theta, u_y = u sin theta) or construct Galilean relative velocity triangles (v_A/B = v_A - v_B).",
        "invariant": "Orthogonal independence: horizontal kinematics and vertical kinematics decouple completely and share only clock time t."
    },
    "stage_3_connect": {
        "name": "Trajectory Quad & Curvature Invariants",
        "action": "Select the governing 2D equations: Cartesian parabola y(x) = x tan theta - g*x^2 / (2*u^2*cos^2 theta), or Frenet-Serret decomposition a = a_t u_t + a_n u_n.",
        "invariant": "Under uniform gravity, horizontal acceleration is zero (a_x = 0) and vertical acceleration is strictly constant (a_y = -g)."
    },
    "stage_4_execute_and_check": {
        "name": "Algebraic Execution & Limiting Boundary Verification",
        "action": "Solve closed-form algebraic expressions; verify asymptotic limits (theta -> 0 deg, 90 deg, 45 deg, g -> 0, v_rel collinear) and base SI dimensional homogeneity.",
        "invariant": "All range/height formulas must have dimension [L]; velocities [L T^-1]; accelerations [L T^-2]; angles dimensionless [1]."
    }
}

# 3. Structural Pillars (5 Invariants)
STRUCTURAL_PILLARS = [
    {
        "id": "P1",
        "name": "Orthogonal Component Independence",
        "principle": "Perpendicular motions are completely independent and decouple into two separate 1D kinematic systems linked solely by shared clock t.",
        "canonical_expression": "a_x = 0 => x(t) = u_x*t; a_y = -g => y(t) = u_y*t - 0.5*g*t^2"
    },
    {
        "id": "P2",
        "name": "Galilean Relative Frame Transformation",
        "principle": "Velocity transforms via vector subtraction v_A/B = v_A - v_B. Under identical gravity, relative acceleration vanishes identically (a_rel = 0).",
        "canonical_expression": "v_AB = v_A - v_B; a_rel = a_A - a_B = (-g) - (-g) = 0"
    },
    {
        "id": "P3",
        "name": "Parabolic Geometry & Trajectory Envelopes",
        "principle": "Eliminating time yields a Cartesian parabola. Level-ground range satisfies complementary angle degeneracy theta <-> 90 deg - theta.",
        "canonical_expression": "y(x) = x tan theta - (g x^2) / (2 u^2 cos^2 theta); R = (u^2 sin 2theta) / g"
    },
    {
        "id": "P4",
        "name": "Normal vs Tangential Acceleration Duality",
        "principle": "Total acceleration resolves into a tangential component altering speed magnitude and a normal component altering direction of motion.",
        "canonical_expression": "a_t = dv/dt; a_n = v^2 / rho; |a| = sqrt(a_t^2 + a_n^2)"
    },
    {
        "id": "P5",
        "name": "Minimum Time vs Minimum Drift Extremization",
        "principle": "In river crossing, time minimization requires maximizing velocity component perpendicular to banks; drift minimization requires canceling downstream current.",
        "canonical_expression": "t_min = W / v_b (head straight across); sin alpha = v_r / v_b (zero drift for v_b > v_r)"
    }
]

# 4. Atomic Competencies Mapping (11 Competencies matching TopicAdapters)
ATOMIC_COMPETENCIES = {
    "PLANE-01": {
        "title": "2D Position & Velocity Component Independence",
        "definition": "Decomposition of 2D position and velocity vectors into mutually independent orthogonal Cartesian components.",
        "canonical_rules": [
            "Position vector r(t) = x(t) i + y(t) j.",
            "Velocity vector v(t) = v_x(t) i + v_y(t) j = (dx/dt) i + (dy/dt) j.",
            "Perpendicular motions decouple completely; changes in x have zero effect on y-motion."
        ],
        "operational_heuristics": [
            "Resolve all initial velocities into u_x = u cos theta and u_y = u sin theta immediately.",
            "Never mix horizontal and vertical quantities in a single 1D equation."
        ],
        "boundary_conditions": [
            "theta = 0 deg: pure horizontal motion u_x = u, u_y = 0.",
            "theta = 90 deg: pure vertical motion u_x = 0, u_y = u."
        ],
        "prerequisites": ["P1"],
        "transfer_targets": ["PHYS-MIP-001", "PHYS-MIP-010"]
    },
    "PLANE-02": {
        "title": "Constant-Acceleration Equations in Vector Form",
        "definition": "Vector extension of the kinematic quad under uniform 2D acceleration.",
        "canonical_rules": [
            "v(t) = u + at.",
            "Delta r(t) = ut + 0.5*a*t^2.",
            "v^2 = u^2 + 2 a . Delta r (scalar product form)."
        ],
        "operational_heuristics": [
            "Solve vector components independently along i and j.",
            "Equate components to find collision or landing times."
        ],
        "boundary_conditions": [
            "a = 0: recovers 2D uniform straight-line motion Delta r = ut.",
            "a_x = 0, a_y = -g: standard projectile equations recovered."
        ],
        "prerequisites": ["PLANE-01"],
        "transfer_targets": ["PHYS-MIP-002", "PHYS-MIP-012"]
    },
    "PLANE-03": {
        "title": "Horizontal Launch from Elevated Height",
        "definition": "Kinematics of a projectile launched horizontally from height h with initial velocity u i.",
        "canonical_rules": [
            "Initial vertical velocity is identically zero: u_y = 0.",
            "Vertical fall time is strictly t_fall = sqrt(2h / g), identical to dropping from rest.",
            "Horizontal range is x = u * sqrt(2h / g).",
            "Impact speed is v_impact = sqrt(u^2 + 2gh)."
        ],
        "operational_heuristics": [
            "Find flight time from vertical drop first, then substitute into horizontal range.",
            "Horizontal launch speed has zero effect on the time to hit the ground."
        ],
        "boundary_conditions": [
            "h -> 0: t_fall -> 0, range -> 0.",
            "u -> 0: recovers pure vertical free fall from height h."
        ],
        "prerequisites": ["PLANE-01", "PLANE-02"],
        "transfer_targets": ["PHYS-MIP-003", "PHYS-MIP-004"]
    },
    "PLANE-04": {
        "title": "Ground-to-Ground Oblique Projectile Flight Time & Apex",
        "definition": "Kinematic landmarks of an oblique projectile: apex turnaround, summit height, and symmetric flight time.",
        "canonical_rules": [
            "At apex summit, vertical velocity vanishes (v_y = 0) while horizontal speed remains v_x = u cos theta.",
            "Time to apex: t_apex = (u sin theta) / g.",
            "Total flight time on level ground: T = 2 * t_apex = (2u sin theta) / g.",
            "Maximum apex height: H_max = (u^2 sin^2 theta) / (2g)."
        ],
        "operational_heuristics": [
            "Remember that speed at the apex is NOT zero; it is u cos theta.",
            "Ascent time equals descent time on level ground."
        ],
        "boundary_conditions": [
            "theta = 90 deg: pure vertical toss, T = 2u/g, H = u^2/(2g).",
            "theta = 0 deg: zero height, zero flight time on level ground."
        ],
        "prerequisites": ["PLANE-01", "PLANE-02"],
        "transfer_targets": ["PHYS-MIP-005", "PHYS-MIP-006", "PHYS-MIP-014"]
    },
    "PLANE-05": {
        "title": "Horizontal Range & Maximum Range Invariant",
        "definition": "Formulation of horizontal range on level ground and extremization of launch angle.",
        "canonical_rules": [
            "Horizontal range: R = u_x * T = (u^2 sin 2theta) / g.",
            "Maximum range occurs at theta = 45 deg: R_max = u^2 / g.",
            "At theta = 45 deg, maximum height is exactly one quarter of range: H_max = R_max / 4."
        ],
        "operational_heuristics": [
            "Apply R = (u^2 sin 2theta)/g ONLY when launch and landing elevations are equal.",
            "For non-level landing, solve y(t) = h_landing for time t."
        ],
        "boundary_conditions": [
            "theta = 45 deg: R = R_max = u^2 / g.",
            "theta = 0 deg or 90 deg: R = 0."
        ],
        "prerequisites": ["PLANE-04"],
        "transfer_targets": ["PHYS-MIP-007", "PHYS-MIP-008", "PHYS-MIP-015"]
    },
    "PLANE-06": {
        "title": "Complementary Launch Angles & Trajectory Envelopes",
        "definition": "Degeneracy of horizontal range for complementary launch angles (theta and 90 deg - theta) at equal launch speeds.",
        "canonical_rules": [
            "Angles theta_1 and theta_2 = 90 deg - theta_1 yield identical horizontal range R.",
            "Ratio of flight times: T_1 / T_2 = tan theta_1.",
            "Ratio of maximum heights: H_1 / H_2 = tan^2 theta_1.",
            "Geometric mean height relation: sqrt(H_1 * H_2) = R / 4.",
            "Flight time product relation: T_1 * T_2 = 2R / g."
        ],
        "operational_heuristics": [
            "The steep trajectory has longer flight time and greater height; the flat trajectory has shorter flight time.",
            "Use sin(2*(90 deg - theta)) = sin(180 deg - 2*theta) = sin 2theta."
        ],
        "boundary_conditions": [
            "theta = 45 deg: self-complementary unique maximum range.",
            "theta -> 0 deg: flat trajectory with T -> 0, H -> 0."
        ],
        "prerequisites": ["PLANE-05"],
        "transfer_targets": ["PHYS-MIP-009", "PHYS-MIP-016"]
    },
    "PLANE-07": {
        "title": "Cartesian Trajectory Parabola Equation",
        "definition": "Spatial path equation y(x) obtained by eliminating time t between horizontal and vertical motions.",
        "canonical_rules": [
            "Cartesian trajectory equation: y(x) = x tan theta - (g x^2) / (2 u^2 cos^2 theta).",
            "Factored range form: y(x) = x tan theta * (1 - x / R).",
            "Path is a concave-down parabola with vertex at (R/2, H_max)."
        ],
        "operational_heuristics": [
            "Use the factored range form when horizontal range R is known to find height at any x instantly.",
            "To hit a target at (x, y), solve the quadratic in tan theta: (g x^2 / 2u^2)*(1 + tan^2 theta) - x tan theta + y = 0."
        ],
        "boundary_conditions": [
            "x = 0: y = 0 (launch).",
            "x = R: y = 0 (landing).",
            "x = R/2: y = H_max = (R/4) * tan theta."
        ],
        "prerequisites": ["PLANE-04", "PLANE-05"],
        "transfer_targets": ["PHYS-MIP-011", "PHYS-MIP-017"]
    },
    "PLANE-08": {
        "title": "Relative Velocity: River-Boat Shortest Time vs Zero Drift",
        "definition": "Galilean velocity addition applied to navigation in moving fluid media.",
        "canonical_rules": [
            "Resultant velocity relative to ground: v_ground = v_boat/water + v_water.",
            "Shortest crossing time: steer perpendicular to banks (theta = 90 deg); t_min = W / v_b; downstream drift x = v_r * t_min.",
            "Zero drift condition (v_b > v_r): steer upstream at sin alpha = v_r / v_b; effective crossing speed v_eff = sqrt(v_b^2 - v_r^2); time t = W / sqrt(v_b^2 - v_r^2).",
            "Minimum drift condition when v_b < v_r: steer at cos theta = v_b / v_r; minimum drift x_min = W * sqrt((v_r/v_b)^2 - 1)."
        ],
        "operational_heuristics": [
            "Crossing time depends strictly on the perpendicular velocity component v_y; current speed v_r cannot assist or hinder crossing time when heading perpendicular.",
            "If engine speed is less than river speed (v_b < v_r), zero drift is physically impossible."
        ],
        "boundary_conditions": [
            "v_r = 0 (still water): t = W/v_b, zero drift.",
            "v_b = v_r: zero drift angle alpha = 90 deg (heads directly upstream, stationary relative to ground)."
        ],
        "prerequisites": ["P2", "P5"],
        "transfer_targets": ["PHYS-MIP-013", "PHYS-MIP-018", "PHYS-MIP-019"]
    },
    "PLANE-09": {
        "title": "Relative Velocity: Rain-Man & Aircraft Wind Drift",
        "definition": "Relative frame transformation for observers moving through precipitation or wind currents.",
        "canonical_rules": [
            "Relative velocity of rain seen by moving observer: v_rain/man = v_rain - v_man.",
            "For vertical rain v_rain = -v_r j and observer moving at v_m i: v_rel = -v_m i - v_r j.",
            "Umbrella tilt angle from vertical: tan theta = v_man / v_rain (tilted forward in the direction of motion)."
        ],
        "operational_heuristics": [
            "Draw vector subtraction: -v_man points backward; adding to downward rain tilts resultant forward.",
            "Increasing running speed requires tilting the umbrella further forward."
        ],
        "boundary_conditions": [
            "v_man = 0: tan theta = 0 (hold umbrella vertically).",
            "v_man -> infinity: theta -> 90 deg (hold umbrella horizontally)."
        ],
        "prerequisites": ["P2"],
        "transfer_targets": ["PHYS-MIP-020", "PHYS-MIP-021", "PHYS-MIP-022"]
    },
    "PLANE-10": {
        "title": "Uniform Circular Motion: Centripetal Acceleration Invariant",
        "definition": "Kinematics of circular motion at constant speed, governed by continuous velocity vector rotation.",
        "canonical_rules": [
            "Scalar speed v is constant, but velocity direction continuously changes.",
            "Centripetal acceleration is strictly directed toward circle center: a_c = v^2 / R = omega^2 * R.",
            "Period T = 2*pi*R / v = 2*pi / omega; frequency f = 1/T.",
            "Velocity vector and acceleration vector are mutually perpendicular at all times (v . a_c = 0)."
        ],
        "operational_heuristics": [
            "Because v . a = 0, rate of change of speed is zero (dv/dt = 0); all acceleration is purely normal.",
            "Do not confuse uniform circular motion with zero acceleration."
        ],
        "boundary_conditions": [
            "R -> infinity: a_c -> 0 (straight-line uniform motion).",
            "omega -> 0: static rest."
        ],
        "prerequisites": ["PLANE-01"],
        "transfer_targets": ["PHYS-MIP-023", "PHYS-MIP-024"]
    },
    "PLANE-11": {
        "title": "Non-Uniform Curvilinear Motion: Tangential vs Normal Components",
        "definition": "General planar curvilinear kinematics decomposed into intrinsic Frenet-Serret coordinates.",
        "canonical_rules": [
            "Total acceleration vector: a = a_t u_t + a_n u_n.",
            "Tangential component alters speed magnitude: a_t = dv/dt = (v . a) / v.",
            "Normal component alters velocity direction: a_n = v^2 / rho = sqrt(|a|^2 - a_t^2).",
            "Radius of curvature of trajectory: rho = v^2 / a_n = v^3 / |v x a|."
        ],
        "operational_heuristics": [
            "At projectile apex: velocity is horizontal u_x = u cos theta, acceleration is vertical g => a_t = 0 and a_n = g => rho_apex = (u^2 cos^2 theta) / g.",
            "Speed is increasing when a_t > 0; decreasing when a_t < 0; instantaneous extremum when a_t = 0."
        ],
        "boundary_conditions": [
            "Straight line: rho -> infinity => a_n = 0, a = a_t.",
            "Circle: rho = R => a_n = v^2/R."
        ],
        "prerequisites": ["PLANE-10"],
        "transfer_targets": ["PHYS-MIP-025"]
    }
}

# 5. Dependency Graph
DEPENDENCY_GRAPH = {
    "layers": [
        {
            "layer_index": 1,
            "name": "Orthogonal Primitive Coordinates",
            "nodes": [
                {"id": "NODE-1.1", "term": "Cartesian Coordinate Frame", "description": "Mutually perpendicular spatial axes (x, y) with declared origin."},
                {"id": "NODE-1.2", "term": "2D Vector Decomposition", "description": "Resolving vector quantities into independent orthogonal components u_x = u cos theta, u_y = u sin theta."}
            ]
        },
        {
            "layer_index": 2,
            "name": "Component Kinematics & Relative Transformations",
            "nodes": [
                {"id": "NODE-2.1", "term": "Decoupled 2D Kinematics", "depends_on": ["NODE-1.1", "NODE-1.2"]},
                {"id": "NODE-2.2", "term": "Galilean Relative Velocity Triangles", "depends_on": ["NODE-1.2"]}
            ]
        },
        {
            "layer_index": 3,
            "name": "Standard Projectile & Media Models",
            "nodes": [
                {"id": "NODE-3.1", "term": "Horizontal Launch Free Fall", "depends_on": ["NODE-2.1"]},
                {"id": "NODE-3.2", "term": "Oblique Projectile Flight Landmarks (Apex, Time, Range)", "depends_on": ["NODE-2.1"]},
                {"id": "NODE-3.3", "term": "River-Boat Crossing Extremization", "depends_on": ["NODE-2.2"]},
                {"id": "NODE-3.4", "term": "Uniform Circular Motion Centripetal Invariant", "depends_on": ["NODE-2.1"]}
            ]
        },
        {
            "layer_index": 4,
            "name": "Coupled Olympiad Synthesis",
            "nodes": [
                {"id": "NODE-4.1", "term": "Cartesian Trajectory Parabola & Target Clearance", "depends_on": ["NODE-3.2"]},
                {"id": "NODE-4.2", "term": "Complementary Launch Range Degeneracy", "depends_on": ["NODE-3.2", "NODE-4.1"]},
                {"id": "NODE-4.3", "term": "Rain-Man Relative Vector Navigation", "depends_on": ["NODE-2.2", "NODE-3.3"]},
                {"id": "NODE-4.4", "term": "Frenet-Serret Curvature Decomposition (rho = v^2 / a_n)", "depends_on": ["NODE-3.4", "NODE-4.1"]}
            ]
        }
    ]
}

# 6. Cognitive Conflict Matrix
COGNITIVE_CONFLICT_MATRIX = [
    {
        "id": "CCM-01",
        "concept": "Apex Velocity vs Total Velocity Invariance",
        "intuitive_misconception": "At the highest point of an oblique projectile flight, velocity is zero because the projectile stops rising.",
        "newtonian_scientific_truth": "Only the vertical velocity component vanishes (v_y = 0). The horizontal velocity remains completely unchanged at v_x = u cos theta. The speed at the apex is strictly u cos theta > 0, and acceleration is still -g downward.",
        "decisive_experiment": "Strobe photography of oblique projectile: at apex, particle continues gliding horizontally at constant horizontal spacing Delta x = (u cos theta) Delta t."
    },
    {
        "id": "CCM-02",
        "concept": "Orthogonal Independence (Bullet Drop)",
        "intuitive_misconception": "A bullet fired horizontally at 500 m/s will take longer to hit the ground than a bullet dropped simultaneously from the same height.",
        "newtonian_scientific_truth": "Horizontal and vertical motions decouple completely. Both bullets experience identical vertical acceleration a_y = -g with identical initial vertical velocity u_y = 0, hitting the ground simultaneously at t = sqrt(2h/g).",
        "decisive_experiment": "A spring launcher simultaneously shoots one ball horizontally while dropping a second ball vertically from the same height; audio sensors record a single simultaneous ground impact click."
    },
    {
        "id": "CCM-03",
        "concept": "Complementary Launch Angle Range Degeneracy",
        "intuitive_misconception": "Launching at a steeper angle always yields greater range because the projectile stays airborne longer.",
        "newtonian_scientific_truth": "Range is the product of horizontal speed and flight time: R = u_x * T. While steeper angles increase flight time, they reduce horizontal speed. Complementary angles (theta and 90 deg - theta) achieve identical horizontal range.",
        "decisive_experiment": "Launching water jets at 30 deg and 60 deg with identical nozzle pressure: both land at the exact same horizontal coordinate."
    },
    {
        "id": "CCM-04",
        "concept": "River Crossing Shortest Time Direction",
        "intuitive_misconception": "To cross a river in the shortest possible time, the boat should steer angled slightly downstream to ride the current.",
        "newtonian_scientific_truth": "Crossing time depends strictly on the velocity component perpendicular to the riverbanks (v_y = v_b sin theta). The river current acts entirely parallel to the banks (v_x = v_r) and cannot assist or impede perpendicular progress. Maximum perpendicular speed requires steering directly across (theta = 90 deg).",
        "decisive_experiment": "Two identical motorized boats: boat A steers directly across; boat B steers downstream. Boat A reaches the opposite bank first every time."
    },
    {
        "id": "CCM-05",
        "concept": "Uniform Circular Motion Acceleration",
        "intuitive_misconception": "If an object moves in a circle at constant speed, its acceleration is zero because speed is not changing.",
        "newtonian_scientific_truth": "Acceleration is the time derivative of the velocity vector. Because the direction of velocity continuously changes, uniform circular motion requires a continuous inward centripetal acceleration a_c = v^2 / R.",
        "decisive_experiment": "Whirling a ball on a string: cutting the string releases the ball tangentially in a straight line, proving inward tension was continuously accelerating the ball."
    },
    {
        "id": "CCM-06",
        "concept": "Rain-Man Umbrella Tilt Direction",
        "intuitive_misconception": "When running forward into vertical rain, you should hold your umbrella vertically or tilted backward because rain comes from above.",
        "newtonian_scientific_truth": "In the runner's reference frame, the ground and air rush backward, so rain acquires an apparent backward horizontal velocity component: v_rel = -v_runner i - v_rain j. The rain appears to strike from in front, requiring the umbrella to be tilted forward.",
        "decisive_experiment": "Driving a car through vertical rain: rain streaks on the side windows slant diagonally backward from top to bottom."
    }
]

# Assemble Core 1A Blueprint
core1a_data = {
    "schema": "core1a-physics-ontology/v2",
    "version": "2.0.0",
    "subject": "Physics",
    "topic": "Motion in a Plane: Projectiles, Relative Frames & Curvilinear Motion",
    "title": "Grade 9 Olympiad Physics Core 1A Ontology: Motion in a Plane (Projectiles, Relative Frames & Curvilinear Motion)",
    "source_authority": "Golden Benchmark Fixtures (core1A-motion-in-a-plane-full-combined-fixed.pdf & Emailing physics-motion-2d-revised-core2-v2.pdf)",
    "canonical_topic_id": "phy-motion-in-a-plane",
    "canonical_strategy": CANONICAL_STRATEGY,
    "structural_pillars": STRUCTURAL_PILLARS,
    "atomic_competencies": ATOMIC_COMPETENCIES,
    "first_move_atlas": FIRST_MOVE_ATLAS,
    "dependency_graph": DEPENDENCY_GRAPH,
    "cognitive_conflict_matrix": COGNITIVE_CONFLICT_MATRIX
}

# 7. Core 1B Reconstruction Cycles & Dissonance Probes
RECONSTRUCTION_CYCLES = [
    {
        "cycle_id": "RECON-01",
        "phenomenon": "Zero-Acceleration Relative Frame of Two Freely Falling Projectiles",
        "competency_ref": "PLANE-02",
        "standard_derivation": "Particle 1: r1(t) = u1*t + 0.5*g*t^2. Particle 2: r2(t) = r2_0 + u2*t + 0.5*g*t^2. The relative position vector is r_rel(t) = r1(t) - r2(t) = -r2_0 + (u1 - u2)*t. Relative acceleration is a_rel = g - g = 0.",
        "phenomenological_reconstruction": {
            "perspective": "Moving Observer Geometric Rectification",
            "conceptual_pivot": "Ride on particle 2. Because both particles experience the identical acceleration vector g, this common acceleration cancels out completely from the relative equation of motion.",
            "rectified_path": "Seen from particle 2, particle 1 travels along an exact straight line with constant vector velocity v_rel = u1 - u2.",
            "collision_criterion": "Collision occurs if and only if the constant relative velocity vector v_rel points directly along the initial line-of-sight vector r2_0 - r1_0."
        },
        "limiting_boundary_checks": [
            {
                "limit": "u1 = u2 (parallel identical launch)",
                "physical_consequence": "v_rel = 0; separation distance remains strictly constant for all t"
            },
            {
                "limit": "v_rel directed along line-of-sight",
                "physical_consequence": "d_min = 0; collision is inevitable regardless of gravity"
            }
        ]
    },
    {
        "cycle_id": "RECON-02",
        "phenomenon": "Complementary Launch Angle Degeneracy & Geometric Mean Height",
        "competency_ref": "PLANE-06",
        "standard_derivation": "Let two projectiles be launched with speed u at angles theta and 90 - theta. Ranges are R1 = (u^2 sin 2theta)/g and R2 = (u^2 sin(180 - 2theta))/g = R1. Heights are H1 = (u^2 sin^2 theta)/(2g) and H2 = (u^2 cos^2 theta)/(2g). Their product is H1*H2 = (u^4 sin^2 theta cos^2 theta)/(4 g^2) = ((u^2 2 sin theta cos theta / g) / 4)^2 = (R/4)^2 => sqrt(H1*H2) = R/4. Flight time product is T1*T2 = (2u sin theta / g)*(2u cos theta / g) = 2R/g.",
        "phenomenological_reconstruction": {
            "perspective": "Trigonometric Duality & Kinetic Swap Invariant",
            "conceptual_pivot": "Replacing theta with 90 - theta exactly swaps the horizontal and vertical velocity components: u_x <-> u_y.",
            "root_decomposition": "Because horizontal range is proportional to the product u_x * u_y, swapping them leaves range R strictly invariant.",
            "geometric_mean": "The product of apex heights isolates the product (u_x * u_y)^2, proving sqrt(H1 * H2) = R/4 is a universal invariant independent of launch angle."
        },
        "limiting_boundary_checks": [
            {
                "limit": "theta = 45 deg",
                "physical_consequence": "H1 = H2 = R/4, self-complementary unique maximum range"
            },
            {
                "limit": "theta -> 0 deg",
                "physical_consequence": "H1 -> 0, H2 -> u^2/(2g), R -> 0, product identity holds trivially"
            }
        ]
    },
    {
        "cycle_id": "RECON-03",
        "phenomenon": "River Crossing Orthogonal Decoupling: Shortest Time vs Minimum Drift",
        "competency_ref": "PLANE-08",
        "standard_derivation": "Boat velocity relative to water is v_b at angle theta to downstream bank. Velocity components: v_x = v_r + v_b cos theta, v_y = v_b sin theta. Crossing time is t = W / v_y = W / (v_b sin theta). Downstream drift is x = v_x * t = (v_r + v_b cos theta) * W / (v_b sin theta).",
        "phenomenological_reconstruction": {
            "perspective": "Perpendicular Projection Decoupling",
            "conceptual_pivot": "River flow is strictly parallel to the banks. The width of the river is strictly perpendicular to the banks.",
            "shortest_time": "The river flow contributes zero velocity toward the opposing bank. To minimize time t = W / v_y, the boat must direct 100% of its engine effort across the river: sin theta = 1 => theta = 90 deg.",
            "zero_drift": "To achieve zero drift, the boat's upstream component must cancel river speed exactly: v_b cos theta + v_r = 0 => cos theta = -v_r / v_b. This is physically possible if and only if v_b > v_r."
        },
        "limiting_boundary_checks": [
            {
                "limit": "v_b < v_r",
                "physical_consequence": "Zero drift is impossible; boat is inevitably swept downstream"
            },
            {
                "limit": "v_r = 0 (still lake)",
                "physical_consequence": "t_min = W / v_b, drift is identically zero"
            }
        ]
    },
    {
        "cycle_id": "RECON-04",
        "phenomenon": "Frenet-Serret Curvature Decomposition: Projectile Apex Curvature Radius",
        "competency_ref": "PLANE-11",
        "standard_derivation": "Trajectory of projectile has velocity v(t) and acceleration a = -g j. Intrinsic acceleration components are a_t = dv/dt = (v . a) / v and a_n = sqrt(g^2 - a_t^2). Radius of curvature is rho = v^2 / a_n.",
        "phenomenological_reconstruction": {
            "perspective": "Osculating Circle & Centripetal Matching",
            "conceptual_pivot": "At any point on a smooth curve, the motion can be locally modeled as circular motion with instantaneous radius rho and normal acceleration a_n.",
            "apex_simplification": "At the highest point (apex), velocity is strictly horizontal v = u cos theta, and gravity is strictly vertical g. Therefore, velocity and acceleration are mutually perpendicular: a_t = 0 and a_n = g.",
            "apex_curvature": "The apex radius of curvature is simply rho_apex = (u cos theta)^2 / g."
        },
        "limiting_boundary_checks": [
            {
                "limit": "theta = 0 deg (horizontal launch)",
                "physical_consequence": "rho_apex = u^2 / g (maximum curvature radius)"
            },
            {
                "limit": "theta -> 90 deg (vertical toss)",
                "physical_consequence": "rho_apex -> 0 (path sharpens into a degenerate 1D line turnaround)"
            }
        ]
    }
]

COGNITIVE_DISSONANCE_PROBES = [
    {
        "probe_id": "CDP-01",
        "competency_ref": "PLANE-04",
        "student_trap": "At the highest point of an oblique projectile flight, velocity is zero because the ball momentarily stops.",
        "socratic_challenge": "If total velocity were zero at the top, which force halted the projectile's horizontal motion? Does gravity act horizontally?",
        "resolution": "Gravity acts strictly downward! Horizontal velocity u_x = u cos theta is completely untouched by gravity and continues unaffected. At the top, the speed is u cos theta > 0."
    },
    {
        "probe_id": "CDP-02",
        "competency_ref": "PLANE-03",
        "student_trap": "A bullet shot horizontally from a gun stays airborne longer than a dropped coin because its high speed lifts it.",
        "socratic_challenge": "Which upward force lifts the bullet in a vacuum? Both objects start with zero vertical speed and fall under g.",
        "resolution": "No upward force exists! Horizontal motion and vertical motion decouple completely. Both the bullet and coin experience vertical acceleration -g and hit the ground at the exact same instant."
    },
    {
        "probe_id": "CDP-03",
        "competency_ref": "PLANE-06",
        "student_trap": "Because launch at 30 deg and 60 deg achieve the same horizontal range, they must have the same flight time.",
        "socratic_challenge": "The 60 deg launch reaches a much higher peak. Can an object climb higher and return in the same time if acceleration is the same constant g?",
        "resolution": "No! Higher ascent requires longer flight time: T = 2 u sin theta / g. The 60 deg launch stays airborne longer (T_60 / T_30 = tan 60 deg = sqrt(3)), but travels slower horizontally, yielding the exact same range product."
    },
    {
        "probe_id": "CDP-04",
        "competency_ref": "PLANE-08",
        "student_trap": "To cross a river in the shortest time, you should aim downstream so the current pushes you across faster.",
        "socratic_challenge": "The current pushes you parallel to the riverbank. Does pushing you parallel help you reach the opposite bank one second sooner?",
        "resolution": "Not by a microsecond! River width is perpendicular to current. Progress across depends solely on v_boat * sin theta. Aiming perpendicular (theta = 90 deg) maximizes crossing speed."
    },
    {
        "probe_id": "CDP-05",
        "competency_ref": "PLANE-10",
        "student_trap": "A car rounding a curve at constant speed of 60 km/h has zero acceleration because speedometer is steady.",
        "socratic_challenge": "Is acceleration defined as change in speed or change in velocity? Is the direction of motion changing?",
        "resolution": "Velocity is a vector! Turning the steering wheel changes the direction of velocity, demanding a continuous inward normal acceleration a_c = v^2 / R provided by tire friction."
    },
    {
        "probe_id": "CDP-06",
        "competency_ref": "PLANE-09",
        "student_trap": "When walking forward in vertically falling rain, you should hold your umbrella vertically to block rain coming from above.",
        "socratic_challenge": "If you hold a vertical umbrella and walk forward, into which raindrops does your body walk?",
        "resolution": "You walk forward into the falling raindrops! In your moving reference frame, the rain appears to come diagonally from the front, so the umbrella must be tilted forward."
    }
]

# Assemble Core 1B Blueprint
core1b_data = {
    "schema": "core1b-physics-reconstruction/v2",
    "version": "2.0.0",
    "subject": "Physics",
    "topic": "Motion in a Plane: Projectiles, Relative Frames & Curvilinear Motion",
    "title": "Grade 9 Olympiad Physics Core 1B Phenomenological Reconstruction: Motion in a Plane",
    "canonical_topic_id": "phy-motion-in-a-plane",
    "reconstruction_cycles": RECONSTRUCTION_CYCLES,
    "cognitive_dissonance_probes": COGNITIVE_DISSONANCE_PROBES
}

# Write Blueprints to disk
bp_1a_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_planar_motion_ontology.v1.json"
bp_1b_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_planar_motion_reconstruction.v1.json"

with open(bp_1a_path, "w", encoding="utf-8") as f:
    json.dump(core1a_data, f, indent=2, ensure_ascii=False)
print(f"[OK] Wrote Core 1A Blueprint: {bp_1a_path}")

with open(bp_1b_path, "w", encoding="utf-8") as f:
    json.dump(core1b_data, f, indent=2, ensure_ascii=False)
print(f"[OK] Wrote Core 1B Blueprint: {bp_1b_path}")

# Update TopicAdapters.v1.json
adapters_path = REPO_ROOT / "Physics/adapter/TopicAdapters.v1.json"
with open(adapters_path, "r", encoding="utf-8") as f:
    all_adapters = json.load(f)

mip_adapter = all_adapters["topic_adapters"]["motion-in-a-plane"]

# Link blueprint_refs
mip_adapter["blueprint_refs"] = {
    "core1a_ontology": "TEST/physics-research/blueprints/core1a_physics_planar_motion_ontology.v1.json",
    "core1b_reconstruction": "TEST/physics-research/blueprints/core1b_physics_planar_motion_reconstruction.v1.json"
}

# Add canonical_reasoning_moves
mip_adapter["canonical_reasoning_moves"] = {
    "stage_1_choose": "Declare orthogonal coordinate axes (x, y), reference directions (+x horizontal, +y vertical), and clock zero t = 0.",
    "stage_2_represent": "Decompose vectors into orthogonal components (u_x = u cos theta, u_y = u sin theta) or construct Galilean relative velocity triangles (v_A/B = v_A - v_B).",
    "stage_3_connect": "Select the governing 2D equations: Cartesian parabola y(x) = x tan theta - g*x^2 / (2*u^2*cos^2 theta), or Frenet-Serret decomposition a = a_t u_t + a_n u_n.",
    "stage_4_execute_and_check": "Solve closed-form algebraic expressions; verify asymptotic limits (theta -> 0 deg, 90 deg, 45 deg, g -> 0, v_rel collinear) and base SI dimensional homogeneity."
}

# Add first_move_atlas (exact match)
mip_adapter["first_move_atlas"] = FIRST_MOVE_ATLAS

with open(adapters_path, "w", encoding="utf-8") as f:
    json.dump(all_adapters, f, indent=2, ensure_ascii=False)
print(f"[OK] Updated TopicAdapters.v1.json with blueprint_refs, canonical_reasoning_moves, and first_move_atlas for motion-in-a-plane.")
