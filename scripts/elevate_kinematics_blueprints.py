# scripts/elevate_kinematics_blueprints.py
"""
Elevate Upstream Kinematics Blueprints to Schema v2.0.0 and reciprocally align with TopicAdapters.v1.json.
Authority: Golden Benchmark Fixtures (physics-motion-1d-revised-core1.pdf & physics-motion-1d-revised-core2.pdf)
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 1. First-Move Atlas (11 rows, 1 per competency)
FIRST_MOVE_ATLAS = [
    {
        "competency_id": "KIN-01",
        "cue": "Reversing direction, turnaround instant, or zigzag path along a straight line",
        "representation": "Signed 1D number line with start point x_i, turning coordinates x_turn, and end point x_f clearly marked",
        "first_executable_move": "Write displacement Delta x = x_f - x_i; write distance s = sum |Delta x_k| by summing absolute segment lengths",
        "anti_pattern": "Converting signed leg displacements to absolute values before computing net displacement"
    },
    {
        "competency_id": "KIN-02",
        "cue": "Complete round trip or returning to initial origin with known leg speeds",
        "representation": "Trajectory phase strip with individual segment times t_k = d_k / v_k and total clock Delta t_tot = sum t_k",
        "first_executable_move": "Immediately set net displacement Delta x = 0 to establish v_avg = 0; compute average speed s_avg = (total distance) / (total time)",
        "anti_pattern": "Confusing average speed with average velocity magnitude on round trips where displacement vanishes"
    },
    {
        "competency_id": "KIN-03",
        "cue": "Equal distance segments or equal time intervals covered at different uniform speeds v1 and v2",
        "representation": "Dual-segment diagram explicitly labeling equal interval variable (Delta t vs d) and calculating dependent parameter",
        "first_executable_move": "For equal distances, write t_tot = d/v1 + d/v2 to deduce harmonic mean v_avg = 2*v1*v2 / (v1 + v2); for equal times, write arithmetic mean (v1 + v2)/2",
        "anti_pattern": "Blindly computing the arithmetic mean (v1 + v2)/2 when equal distances are traversed"
    },
    {
        "competency_id": "KIN-04",
        "cue": "Particle moving with negative velocity u < 0 or experiencing negative acceleration a < 0",
        "representation": "1D coordinate axis with signed velocity and acceleration arrows placed at particle position",
        "first_executable_move": "Compare signs of v and a: if sgn(v) == sgn(a), the particle is speeding up; if sgn(v) != sgn(a), the particle is slowing down",
        "anti_pattern": "Equating negative acceleration directly to deceleration without checking the sign of velocity"
    },
    {
        "competency_id": "KIN-05",
        "cue": "Uniform acceleration motion with one omitted or unrequested variable among {u, v, a, t, s}",
        "representation": "UVATS 5-parameter state table listing known values, target quantity, and the single excluded parameter",
        "first_executable_move": "Select the exact kinematic equation that omits the unrequested parameter (e.g., v^2 = u^2 + 2as when time t is unmentioned)",
        "anti_pattern": "Solving multi-step quadratic systems for intermediate time t when a direct time-free equation exists"
    },
    {
        "competency_id": "KIN-06",
        "cue": "Multi-phase piecewise acceleration, delayed vehicle launch, or distance in the n-th second",
        "representation": "Multi-segment timeline with boundary state continuity (v_1,end = u_2,start) and local clocks tau = t - t_delay",
        "first_executable_move": "Carry forward boundary speed as initial velocity for next phase; for n-th second, apply s_n = u + 0.5*a*(2n - 1)",
        "anti_pattern": "Applying a single global kinematic formula across multiple distinct acceleration intervals"
    },
    {
        "competency_id": "KIN-07",
        "cue": "Vertical toss under gravity, apex summit turnaround, or symmetrical free fall",
        "representation": "Vertical axis +y upward with a_y = -g labeled continuously at launch, apex, and descent",
        "first_executable_move": "Set vertical apex velocity v_top = 0 while preserving acceleration a_y = -g; apply v^2 = u^2 - 2gH to find H_max = u^2 / (2g)",
        "anti_pattern": "Setting acceleration a = 0 at the highest point of flight where instantaneous velocity momentarily vanishes"
    },
    {
        "competency_id": "KIN-08",
        "cue": "2D projectile launched horizontally from elevated height or obliquely across level ground",
        "representation": "2D Cartesian coordinate frame with independent 1D horizontal (a_x = 0) and vertical (a_y = -g) projections",
        "first_executable_move": "Decouple into independent motions: x(t) = (u cos theta)*t and y(t) = (u sin theta)*t - 0.5*g*t^2, linked strictly by clock t",
        "anti_pattern": "Believing horizontal velocity influences the vertical time of fall or gravitational acceleration"
    },
    {
        "competency_id": "KIN-09",
        "cue": "Parabolic trajectory equation, maximum range condition, or complementary launch angles",
        "representation": "Parabolic path sketch showing apex coordinates (R/2, H_max), range landing (R, 0), and velocity vector tangents",
        "first_executable_move": "Substitute t = x / (u cos theta) into y(t) to form trajectory equation y = x tan theta - g*x^2 / (2*u^2*cos^2 theta)",
        "anti_pattern": "Using symmetric ground-to-ground range formula R = u^2 sin 2theta / g when launch and landing heights are unequal"
    },
    {
        "competency_id": "KIN-10",
        "cue": "Two bodies in simultaneous flight under gravity or relative pursuit/interception",
        "representation": "Relative reference frame anchored on body B with relative position r_rel = r_A - r_B and relative velocity v_rel = v_A - v_B",
        "first_executable_move": "Notice common acceleration cancellation: a_rel = a_A - a_B = (-g) - (-g) = 0, reducing relative motion to a constant-velocity straight line",
        "anti_pattern": "Retaining gravitational acceleration terms in the relative trajectory equation of two freely falling projectiles"
    },
    {
        "competency_id": "KIN-11",
        "cue": "Motion graphs (x-t, v-t, a-t), piecewise linear curves, or physical graph consistency checks",
        "representation": "Graph geometry inspection: identify curve tangent slope as derivative and signed area under curve as definite integral",
        "first_executable_move": "Extract physical rates: slope of x-t is v; slope of v-t is a; signed area under v-t is displacement Delta x; area under a-t is Delta v",
        "anti_pattern": "Confusing the vertical height coordinate of an x-t graph with the instantaneous speed of the particle"
    }
]

# 2. Canonical Strategy (4 Stages)
CANONICAL_STRATEGY = {
    "stage_1_choose": {
        "name": "Spatial-Temporal Invariant & Origin Setup",
        "action": "Declare spatial origin x = 0 (or launch level y = 0), define positive coordinate direction (+), and synchronize clock zero t = 0.",
        "invariant": "Physical events (collisions, turning points, apex heights) are strictly invariant under choice of origin."
    },
    "stage_2_represent": {
        "name": "Dual Kinematic Representation",
        "action": "Construct UVATS 5-parameter state table, signed number line, or motion graph (x-t / v-t) capturing phase boundaries.",
        "invariant": "Boundary state continuity: final velocity and position of phase k form the exact initial state of phase k+1."
    },
    "stage_3_connect": {
        "name": "Kinematic Quad & Decoupled Invariants",
        "action": "Select the unique kinematic equation eliminating the unmeasured variable, or decouple orthogonal 2D components.",
        "invariant": "Constant-acceleration equations apply IF AND ONLY IF da/dt = 0; perpendicular axes share only scalar time t."
    },
    "stage_4_execute_and_check": {
        "name": "Algebraic Execution & Limiting Boundary Verification",
        "action": "Solve closed-form algebraic expressions and verify asymptotic limits (a -> 0, g -> 0, t -> 0) and dimensional homogeneity.",
        "invariant": "All distance/displacement formulas must have dimension [L]; speeds [L T^-1]; accelerations [L T^-2]."
    }
}

# 3. Structural Pillars (5 Invariants)
STRUCTURAL_PILLARS = [
    {
        "id": "P1",
        "name": "Spatial-Temporal Coordinate Invariance",
        "principle": "Kinematic trajectories and physical intervals are invariant under translation of spatial origin and clock zero.",
        "canonical_expression": "Delta x = x_f - x_i; Delta t = t_f - t_i"
    },
    {
        "id": "P2",
        "name": "Geometric Calculus Slope-Area Duality",
        "principle": "Differentiation yields instantaneous rates (slope); integration accumulates physical displacement and velocity changes (area).",
        "canonical_expression": "v(t) = dx/dt, a(t) = dv/dt; Delta x = int v dt, Delta v = int a dt"
    },
    {
        "id": "P3",
        "name": "Kinematic Quad & Uniform Acceleration Constraint",
        "principle": "The four standard kinematic equations are mathematically exact if and only if acceleration is strictly time-invariant.",
        "canonical_expression": "v = u + at; s = ut + 0.5*a*t^2; v^2 = u^2 + 2as; s = 0.5*(u+v)*t"
    },
    {
        "id": "P4",
        "name": "Directional Sign Consistency & Inversion Dynamics",
        "principle": "Vectors along 1D axes are signed scalars. Speed magnitude |v| increases when v and a share signs; turnaround occurs at v = 0.",
        "canonical_expression": "d|v|/dt > 0 <=> sgn(v) == sgn(a); v_turn = 0 with a != 0"
    },
    {
        "id": "P5",
        "name": "Galilean Invariance & Relative Frame Transformation",
        "principle": "Under uniform gravity, relative acceleration between free bodies vanishes identically, rectifying relative trajectories into straight lines.",
        "canonical_expression": "a_rel = a_A - a_B = 0 => v_rel = const; r_rel(t) = r_rel,0 + v_rel*t"
    }
]

# 4. Atomic Competencies Mapping (11 Competencies matching TopicAdapters)
ATOMIC_COMPETENCIES = {
    "KIN-01": {
        "title": "Distance vs Displacement Invariant",
        "definition": "Distinction between scalar cumulative path length and vector net endpoint change on a signed 1D axis.",
        "canonical_rules": [
            "Displacement Delta x = x_f - x_i depends strictly on start and finish positions.",
            "Distance s = sum |Delta x_k| accumulates all forward and backward leg lengths.",
            "|Delta x| <= distance s, with equality holding if and only if motion is unidirectional without reversal."
        ],
        "operational_heuristics": [
            "Mark start, turn, and finish on one signed number line.",
            "Never convert signed displacement legs into absolute values prior to algebraic addition."
        ],
        "boundary_conditions": [
            "Unidirectional motion: |Delta x| = s.",
            "Closed round trip: Delta x = 0 while s = 2L > 0."
        ],
        "prerequisites": ["Spatial Coordinate Axis", "Signed Scalar Arithmetic"],
        "transfer_targets": ["PHYS-KIN-001"]
    },
    "KIN-02": {
        "title": "Average Speed vs Average Velocity",
        "definition": "Ratio of total displacement vs total distance to total elapsed clock time.",
        "canonical_rules": [
            "Average velocity v_avg = Delta x / Delta t.",
            "Average speed s_avg = (total distance) / Delta t.",
            "On any closed round trip, average velocity is identically zero while average speed is strictly positive."
        ],
        "operational_heuristics": [
            "Calculate total elapsed clock time Delta t_tot = sum t_k before forming any quotient.",
            "Instantaneous velocity is the limiting derivative v = dx/dt as Delta t -> 0."
        ],
        "boundary_conditions": [
            "Round trip: v_avg = 0, s_avg = 2d / (t1 + t2).",
            "Uniform speed motion: s_avg = |v_avg|."
        ],
        "prerequisites": ["KIN-01"],
        "transfer_targets": ["PHYS-KIN-010"]
    },
    "KIN-03": {
        "title": "Weighted Kinematic Averages",
        "definition": "Mathematical formulation of average speed over partitioned intervals with equal-time versus equal-distance weighting.",
        "canonical_rules": [
            "Equal-time intervals yield arithmetic mean: v_avg = (v1 + v2) / 2.",
            "Equal-distance intervals yield harmonic mean: v_avg = 2*v1*v2 / (v1 + v2).",
            "Harmonic mean is strictly less than arithmetic mean for distinct positive speeds (v1 != v2)."
        ],
        "operational_heuristics": [
            "Identify the equal parameter: if equal distance, longer time is spent at slower speed, pulling the average down.",
            "Never apply arithmetic average to equal-distance travel legs."
        ],
        "boundary_conditions": [
            "v1 = v2 = v: v_avg = v.",
            "v2 -> 0 on second half: v_avg -> 0 (trip never completes).",
            "v2 -> infinity: v_avg -> 2*v1 (bounded by twice the slower speed)."
        ],
        "prerequisites": ["KIN-02"],
        "transfer_targets": ["PHYS-KIN-002"]
    },
    "KIN-04": {
        "title": "Signs, Direction & Acceleration Reversal",
        "definition": "Interpretation of algebraic signs of velocity and acceleration along a chosen 1D axis.",
        "canonical_rules": [
            "Sign of velocity determines direction of motion (+x or -x).",
            "Sign of acceleration determines direction of velocity vector change (dv/dt).",
            "Speeding up occurs when v and a have identical signs; slowing down occurs when v and a have opposite signs."
        ],
        "operational_heuristics": [
            "Negative acceleration speeds up a body traveling in the negative direction.",
            "Turnaround instant occurs where v = 0; acceleration can remain constant and non-zero across the turnaround."
        ],
        "boundary_conditions": [
            "v > 0, a > 0: speeding up in +x direction.",
            "v < 0, a < 0: speeding up in -x direction.",
            "v > 0, a < 0: slowing down in +x direction prior to reversal."
        ],
        "prerequisites": ["Spatial Coordinate Axis"],
        "transfer_targets": ["PHYS-KIN-015"]
    },
    "KIN-05": {
        "title": "Constant Acceleration Equation Selection",
        "definition": "Systematic selection and execution of the kinematic quad under uniform acceleration.",
        "canonical_rules": [
            "The kinematic quad is valid IF AND ONLY IF acceleration is constant (da/dt = 0).",
            "v = u + at (omits displacement s).",
            "s = ut + 0.5*a*t^2 (omits final velocity v).",
            "v^2 = u^2 + 2as (omits elapsed time t).",
            "s = 0.5*(u + v)*t (omits acceleration a)."
        ],
        "operational_heuristics": [
            "Build UVATS state table: list {u, v, a, t, s}, identify the unknown target, and pick the equation omitting the 5th variable."
        ],
        "boundary_conditions": [
            "a = 0: recovers uniform motion s = ut, v = u.",
            "u = 0: s = 0.5*a*t^2, v = sqrt(2as)."
        ],
        "prerequisites": ["P3"],
        "transfer_targets": ["PHYS-KIN-004"]
    },
    "KIN-06": {
        "title": "Multiphase & Delayed-Start Motion",
        "definition": "Partitioning piecewise uniform motions and handling staggered clocks across multiple bodies.",
        "canonical_rules": [
            "Final velocity and position of phase k constitute initial state of phase k+1.",
            "Delayed start: if body B starts at clock time t_delay, elapsed time for B is tau = t - t_delay (tau >= 0).",
            "Displacement in n-th second: s_n = u + 0.5*a*(2n - 1)."
        ],
        "operational_heuristics": [
            "Reset local clock for each phase while carrying forward physical state variables.",
            "Set position functions equal x_A(t) = x_B(t) to solve catch-up / collision conditions."
        ],
        "boundary_conditions": [
            "t < t_delay: body B remains stationary at starting position.",
            "Catch-up condition: x_A(t) = x_B(t) must have real positive root t >= t_delay."
        ],
        "prerequisites": ["KIN-05"],
        "transfer_targets": ["PHYS-KIN-018"]
    },
    "KIN-07": {
        "title": "Vertical Free Fall & Apex Invariants",
        "definition": "1D motion under constant gravitational acceleration a_y = -g in vacuum.",
        "canonical_rules": [
            "Acceleration is strictly a_y = -g throughout ascent, apex, and descent.",
            "At apex summit, instantaneous velocity vanishes (v_y = 0) while acceleration remains exactly -g.",
            "Time of ascent equals time of descent to launch level: t_up = t_down = u / g.",
            "Maximum height reached: H_max = u^2 / (2g)."
        ],
        "operational_heuristics": [
            "Never set acceleration to zero at the apex.",
            "Use time-reversal symmetry: descent from apex is identical to release from rest."
        ],
        "boundary_conditions": [
            "y = H_max: v = 0, a = -g.",
            "Return to launch level: y = 0, t = 2u/g, v = -u."
        ],
        "prerequisites": ["KIN-05"],
        "transfer_targets": ["PHYS-KIN-003", "PHYS-KIN-007"]
    },
    "KIN-08": {
        "title": "2D Projectile Component Decoupling",
        "definition": "Orthogonal decomposition of 2D planar motion into independent 1D kinematic components.",
        "canonical_rules": [
            "Perpendicular motions (x and y) are completely independent and share only clock time t.",
            "Horizontal motion is uniform: a_x = 0, v_x = u cos theta, x(t) = (u cos theta)*t.",
            "Vertical motion is uniform free fall: a_y = -g, v_y = u sin theta - gt, y(t) = (u sin theta)*t - 0.5*g*t^2."
        ],
        "operational_heuristics": [
            "Horizontal launch speed has zero influence on vertical drop time.",
            "Solve for time t from vertical equation and substitute into horizontal equation."
        ],
        "boundary_conditions": [
            "Horizontal launch (theta = 0): v_x = u, v_y = -gt, t_fall = sqrt(2h/g).",
            "Landing on level ground: y(T) = 0 => T = 2u sin theta / g."
        ],
        "prerequisites": ["KIN-05", "KIN-07"],
        "transfer_targets": ["PHYS-KIN-006", "PHYS-KIN-014", "PHYS-KIN-022", "PHYS-KIN-023", "PHYS-KIN-025"]
    },
    "KIN-09": {
        "title": "Projectile Trajectory & Flight Landmarks",
        "definition": "Mathematical formulation of parabolic trajectory, horizontal range, and elevation envelope.",
        "canonical_rules": [
            "Trajectory is a Cartesian parabola: y(x) = x tan theta - (g / (2*u^2*cos^2 theta)) * x^2.",
            "Horizontal range on level ground: R = (u^2 sin 2theta) / g.",
            "Complementary launch angles (theta and 90 deg - theta) produce identical horizontal ranges at equal launch speeds.",
            "Maximum horizontal range occurs at theta = 45 deg: R_max = u^2 / g."
        ],
        "operational_heuristics": [
            "Symmetric range formula applies ONLY when launch height equals landing height.",
            "For cliff launch, determine flight time from quadratic equation in y(t) = -h."
        ],
        "boundary_conditions": [
            "theta = 45 deg: R = R_max = u^2/g, H = R_max / 4.",
            "theta = 90 deg: R = 0, pure vertical motion recovered."
        ],
        "prerequisites": ["KIN-08"],
        "transfer_targets": ["PHYS-KIN-008", "PHYS-KIN-009", "PHYS-KIN-017", "PHYS-KIN-021"]
    },
    "KIN-10": {
        "title": "Relative Velocity & Common Acceleration Cancellation",
        "definition": "Classical Galilean relative motion and cancellation of uniform gravitational acceleration.",
        "canonical_rules": [
            "Relative velocity: v_AB = v_A - v_B.",
            "When two bodies experience identical acceleration (a_A = a_B = -g), relative acceleration is identically ZERO (a_rel = 0).",
            "The relative trajectory of one freely falling projectile viewed from another is a uniform straight line."
        ],
        "operational_heuristics": [
            "Transform into the reference frame of one projectile to eliminate gravity completely.",
            "Collision occurs if and only if relative velocity points directly along initial line-of-sight vector."
        ],
        "boundary_conditions": [
            "Identical launch velocities (u_A = u_B): v_rel = 0, separation distance remains constant forever.",
            "Opposite colinear launch: relative approach speed is u_A + u_B."
        ],
        "prerequisites": ["KIN-08"],
        "transfer_targets": ["PHYS-KIN-011", "PHYS-KIN-013", "PHYS-KIN-016", "PHYS-KIN-019", "PHYS-KIN-020", "PHYS-KIN-024"]
    },
    "KIN-11": {
        "title": "Motion Graphs & Geometric Calculus",
        "definition": "Visual representation of kinematics through slope (derivative) and area (integral) duality.",
        "canonical_rules": [
            "Slope of x-t graph is instantaneous velocity v = dx/dt; concavity is acceleration d^2x/dt^2.",
            "Slope of v-t graph is instantaneous acceleration a = dv/dt.",
            "Signed area under v-t curve represents net displacement Delta x = int v dt.",
            "Absolute area under v-t curve represents cumulative distance s = int |v| dt.",
            "Signed area under a-t curve represents change in velocity Delta v = v_f - v_i."
        ],
        "operational_heuristics": [
            "Vertical line test: an x-t graph cannot loop or intersect a vertical line twice (single-valued physical history).",
            "A sharp corner in an x-t curve implies an infinite acceleration impulse."
        ],
        "boundary_conditions": [
            "Horizontal line on x-t: v = 0 (particle at rest).",
            "Horizontal line on v-t: a = 0 (uniform motion).",
            "Straight line on v-t: a = const (uniform acceleration)."
        ],
        "prerequisites": ["P2"],
        "transfer_targets": ["PHYS-KIN-005", "PHYS-KIN-012"]
    }
}

# 5. Dependency Graph
DEPENDENCY_GRAPH = {
    "layers": [
        {
            "layer_index": 1,
            "name": "Primitive Physical Definitions",
            "nodes": [
                {"id": "NODE-1.1", "term": "Reference Frame & Origin", "description": "Declared spatial origin and clock setting zero coordinates (x0, t0)."},
                {"id": "NODE-1.2", "term": "Position Vector & Scalar Distance", "description": "Position coordinate x(t) vs cumulative scalar path length s = int |v| dt."},
                {"id": "NODE-1.3", "term": "Vector Displacement", "description": "Net change in position coordinate: Delta x = x(t2) - x(t1)."}
            ]
        },
        {
            "layer_index": 2,
            "name": "Kinematic Rates & Graph Duals",
            "nodes": [
                {"id": "NODE-2.1", "term": "Average Rates (Speed vs Velocity)", "depends_on": ["NODE-1.2", "NODE-1.3"]},
                {"id": "NODE-2.2", "term": "Instantaneous Velocity (v = dx/dt)", "depends_on": ["NODE-1.3"]},
                {"id": "NODE-2.3", "term": "Instantaneous Acceleration (a = dv/dt)", "depends_on": ["NODE-2.2"]},
                {"id": "NODE-2.4", "term": "Motion Graph Slope & Area Duals", "depends_on": ["NODE-2.2", "NODE-2.3"]}
            ]
        },
        {
            "layer_index": 3,
            "name": "Constrained Motion Models (1D & 2D)",
            "nodes": [
                {"id": "NODE-3.1", "term": "Constant Acceleration Kinematic Quad", "depends_on": ["NODE-2.3", "NODE-2.4"]},
                {"id": "NODE-3.2", "term": "Free Fall & Vertical Apex Invariant", "depends_on": ["NODE-3.1"]},
                {"id": "NODE-3.3", "term": "Orthogonal Independence Principle", "depends_on": ["NODE-1.1", "NODE-3.1"]},
                {"id": "NODE-3.4", "term": "Multiphase Continuity & Staggered Clocks", "depends_on": ["NODE-3.1"]}
            ]
        },
        {
            "layer_index": 4,
            "name": "Coupled Olympiad Synthesis",
            "nodes": [
                {"id": "NODE-4.1", "term": "Projectile Trajectory & Parabolic Landmarks", "depends_on": ["NODE-3.2", "NODE-3.3"]},
                {"id": "NODE-4.2", "term": "Complementary Angle Range Degeneracy", "depends_on": ["NODE-4.1"]},
                {"id": "NODE-4.3", "term": "Relative Velocity Frame Cancellation (a_rel = 0)", "depends_on": ["NODE-3.3", "NODE-4.1"]},
                {"id": "NODE-4.4", "term": "Interval Motion & Graph Consistency Analysis", "depends_on": ["NODE-2.4", "NODE-3.4"]}
            ]
        }
    ]
}

# 6. Cognitive Conflict Matrix
COGNITIVE_CONFLICT_MATRIX = [
    {
        "id": "CCM-01",
        "concept": "Apex Acceleration Invariance",
        "intuitive_misconception": "When a vertically thrown projectile reaches its highest point (apex), its velocity is zero, so its acceleration must also be zero.",
        "newtonian_scientific_truth": "Velocity is zero momentarily at the turnaround instant, but acceleration is the derivative dv/dt = -g != 0. If acceleration were zero at the apex, the ball would remain suspended in mid-air indefinitely.",
        "decisive_experiment": "High-speed strobe photography and accelerometer attached to a vertical toss reveal constant -9.8 m/s^2 readout continuously through the apex."
    },
    {
        "id": "CCM-02",
        "concept": "Distance vs Displacement Distinctions",
        "intuitive_misconception": "Total distance traveled is always equal to the magnitude of displacement.",
        "newtonian_scientific_truth": "Displacement is the net vector change in position Delta x. Distance is the cumulative path length. In any round-trip or reverse motion, distance > 0 while displacement = 0.",
        "decisive_experiment": "A runner on a 400 m circular track completes one full lap: odometer reads 400 m, but displacement from start to finish is exactly 0 m."
    },
    {
        "id": "CCM-03",
        "concept": "Average Speed for Split Distances",
        "intuitive_misconception": "A car travelling half the distance at v1 and the remaining half at v2 has average speed (v1 + v2) / 2.",
        "newtonian_scientific_truth": "Average speed is total distance divided by total time. For equal distances, the car spends more time at the slower speed, yielding the harmonic mean v_avg = 2*v1*v2 / (v1 + v2). The arithmetic average applies only to equal time intervals.",
        "decisive_experiment": "Driving 60 km at 30 km/h (takes 2 hours) and 60 km at 60 km/h (takes 1 hour). Total distance = 120 km, total time = 3 hours => average speed = 40 km/h, not 45 km/h."
    },
    {
        "id": "CCM-04",
        "concept": "Orthogonal Independence (Bullet Drop)",
        "intuitive_misconception": "A bullet fired horizontally at 500 m/s will take longer to hit the ground than a bullet dropped simultaneously from the same height.",
        "newtonian_scientific_truth": "Horizontal and vertical motions decouple completely. Both bullets experience identical vertical acceleration a_y = -g with identical initial vertical velocity u_y = 0, hitting the ground simultaneously at t = sqrt(2h/g).",
        "decisive_experiment": "Classic physics apparatus: a spring-loaded launcher simultaneously shoots one ball horizontally while dropping a second ball vertically from the same height; audio sensors record a single simultaneous ground impact click."
    },
    {
        "id": "CCM-05",
        "concept": "Motion Graph Slope vs Height Conflation",
        "intuitive_misconception": "On a position-time graph, when the curve crosses the time axis (x = 0), the velocity is zero; or on a velocity-time graph, a negative velocity indicates deceleration.",
        "newtonian_scientific_truth": "On an x-t graph, velocity is the tangent slope dx/dt, not position x(t). On a v-t graph, sign indicates direction of motion; deceleration occurs if and only if velocity and acceleration have opposite signs (|v| is decreasing).",
        "decisive_experiment": "A car passing through x = 0 at 100 km/h has zero position but high speed. A ball tossed upward has v < 0 and a < 0 on the downward leg, meaning it is accelerating downward (speeding up in the negative direction)."
    },
    {
        "id": "CCM-06",
        "concept": "Same-g Relative Frame Cancellation",
        "intuitive_misconception": "Two objects falling freely near Earth accelerate toward each other because gravity pulls both of them.",
        "newtonian_scientific_truth": "Because both objects experience the identical acceleration a = -g, their relative acceleration is a_rel = a_1 - a_2 = 0. In their relative frame, gravity is completely eliminated, and their relative motion is uniform constant velocity.",
        "decisive_experiment": "Releasing two stones from different heights inside an Einstein free-falling elevator: both hover at constant separation distance relative to the elevator and each other."
    }
]

# Assemble Core 1A Blueprint
core1a_data = {
    "schema": "core1a-physics-ontology/v2",
    "version": "2.0.0",
    "subject": "Physics",
    "topic": "Kinematics: 1D Motion, 2D Projectiles & Relative Frames",
    "title": "Grade 9 Olympiad Kinematics Conceptual Ontology, First-Move Atlas & Subtopic Competencies",
    "source_authority": "Golden Benchmark Fixtures (physics-motion-1d-revised-core1.pdf & physics-motion-1d-revised-core2.pdf)",
    "canonical_topic_id": "phy-kinematics-1d-2d",
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
        "phenomenon": "Harmonic Mean Average Speed for Split Distance Trips",
        "competency_ref": "KIN-03",
        "standard_derivation": "Let total distance be 2d, split into two equal segments of length d traveled at constant speeds v1 and v2. Elapsed times are t1 = d/v1 and t2 = d/v2. Total time is t_tot = t1 + t2 = d*(v1 + v2)/(v1*v2). Average speed is v_avg = 2d / t_tot = 2*v1*v2 / (v1 + v2).",
        "phenomenological_reconstruction": {
            "perspective": "Time Budget Weighting Perspective",
            "conceptual_pivot": "Speed is distance per unit time. When distance is held fixed, time spent in each leg is inversely proportional to speed: t_k proportional to 1/v_k.",
            "harmonic_origin": "The driver spends a fraction v2/(v1 + v2) of total time at speed v1 and a fraction v1/(v1 + v2) at speed v2. The slower speed consumes more clock time, heavily skewing the average downward.",
            "limiting_consequence": "If v2 -> 0, t2 -> infinity, so v_avg -> 0 regardless of how arbitrarily fast v1 is. If v2 -> infinity (instantaneous transport), v_avg -> 2*v1, strictly bounded by twice the slower speed."
        },
        "limiting_boundary_checks": [
            {
                "limit": "v2 -> 0 (stalling on second half)",
                "physical_consequence": "v_avg -> 0 (Total time diverges to infinity; trip is never completed)"
            },
            {
                "limit": "v2 -> infinity (instant teleportation)",
                "physical_consequence": "v_avg -> 2*v1 (Average speed is strictly bounded by twice the slower speed)"
            },
            {
                "limit": "v1 = v2 = v",
                "physical_consequence": "v_avg = v (Uniform motion recovered identically)"
            }
        ]
    },
    {
        "cycle_id": "RECON-02",
        "phenomenon": "Parabolic Symmetry & Dual-Time Product Measuring Height",
        "competency_ref": "KIN-07",
        "standard_derivation": "From 1D constant-acceleration free fall: h = u*t - 0.5*g*t^2 => 0.5*g*t^2 - u*t + h = 0. Solving via quadratic formula yields roots t1, t2 = (u +- sqrt(u^2 - 2gh)) / g. The sum of roots is t1 + t2 = 2u / g = T (total flight time), and the product of roots is t1 * t2 = 2h / g => h = 0.5 * g * t1 * t2.",
        "phenomenological_reconstruction": {
            "perspective": "Apex Time-Reversal Symmetry Invariant",
            "conceptual_pivot": "Shift the temporal origin to the apex turnaround instant t_apex = u / g. At the apex, vertical velocity is exactly zero.",
            "ascent_descent_matching": "The climb from height h to apex takes time Delta t = sqrt(u^2 - 2gh) / g. By time-reversal symmetry of conservative gravitational acceleration, the descent from apex back to h takes the identical duration Delta t.",
            "root_decomposition": "Thus, the two passage times decompose as t1 = t_apex - Delta t and t2 = t_apex + Delta t. Adding them yields t1 + t2 = 2*t_apex = T. Multiplying them yields t1*t2 = t_apex^2 - (Delta t)^2 = (u/g)^2 - (u^2 - 2gh)/g^2 = 2h/g, directly proving h = 0.5*g*t1*t2 without quadratic formula memorization."
        },
        "limiting_boundary_checks": [
            {
                "limit": "h -> H_max = u^2 / (2g)",
                "physical_consequence": "t1 = t2 = u/g (Apex coincidence; discriminant vanishes)"
            },
            {
                "limit": "h -> 0 (ground level)",
                "physical_consequence": "t1 = 0 and t2 = T = 2u/g (Launch and landing)"
            },
            {
                "limit": "h > H_max",
                "physical_consequence": "Roots become complex; physically unattainable height"
            }
        ]
    },
    {
        "cycle_id": "RECON-03",
        "phenomenon": "Free-Fall Elevator Equivalence of Dropped vs Fired Projectiles",
        "competency_ref": "KIN-08",
        "standard_derivation": "Dropped ball has y1(t) = h - 0.5*g*t^2. Horizontally fired projectile has y2(t) = h - 0.5*g*t^2 and x2(t) = u*t. For both particles, the ground landing condition is y(T) = 0 => T = sqrt(2h/g), identical for both regardless of horizontal launch speed u.",
        "phenomenological_reconstruction": {
            "perspective": "Einstein Free-Fall Equivalence Principle",
            "conceptual_pivot": "Step inside an imaginary elevator falling freely alongside the cliff edge with acceleration g.",
            "effective_gravity": "Inside this frame, real gravity g is exactly cancelled by the upward inertial pseudo-acceleration -g. The effective gravity is g_eff = 0.",
            "motion_in_elevator": "Inside the elevator, the dropped ball is in static rest. The fired projectile travels in a uniform horizontal straight line at constant velocity u with zero vertical deflection.",
            "floor_motion": "The ground floor is accelerating upward at g toward the elevator with speed v_floor(t) = g*t. The upward rushing floor impacts both the stationary ball and the horizontally gliding projectile at the exact same instant, proving identical drop time."
        },
        "limiting_boundary_checks": [
            {
                "limit": "u -> 0",
                "physical_consequence": "Recovers two simultaneous identical 1D drops"
            },
            {
                "limit": "h -> 0",
                "physical_consequence": "T -> 0 (Instant ground contact)"
            },
            {
                "limit": "g -> 0 (zero gravity)",
                "physical_consequence": "T -> infinity; particles glide horizontally and remain suspended"
            }
        ]
    },
    {
        "cycle_id": "RECON-04",
        "phenomenon": "Zero-Acceleration Relative Frame of Two Free Projectiles",
        "competency_ref": "KIN-10",
        "standard_derivation": "Particle 1: r1(t) = u1*t + 0.5*g*t^2. Particle 2: r2(t) = r2_0 + u2*t + 0.5*g*t^2. The relative position vector is r_rel(t) = r1(t) - r2(t) = -r2_0 + (u1 - u2)*t. Relative acceleration is a_rel = g - g = 0.",
        "phenomenological_reconstruction": {
            "perspective": "Moving Observer Geometric Rectification",
            "conceptual_pivot": "Ride on particle 2. Because both particles experience the identical acceleration vector g, this common acceleration cancels out completely from the relative equation of motion.",
            "rectified_path": "Seen from particle 2, particle 1 travels along an exact straight line with constant vector velocity v_rel = u1 - u2.",
            "collision_criterion": "Collision occurs if and only if the constant relative velocity vector v_rel points directly along the initial line-of-sight vector r2_0 - r1_0.",
            "shortest_distance": "The shortest distance of approach between the two projectiles is simply the perpendicular distance from particle 2 to the straight line of relative motion: d_min = |r2_0 x v_rel| / |v_rel|."
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
    }
]

COGNITIVE_DISSONANCE_PROBES = [
    {
        "probe_id": "CDP-01",
        "competency_ref": "KIN-07",
        "student_trap": "At the highest point of a vertical throw, the ball stops moving, so its acceleration must be zero.",
        "socratic_challenge": "If acceleration were zero at the top when velocity is zero, what would happen to its velocity in the next millisecond? By definition, Delta v = a * Delta t = 0 * Delta t = 0. Would the ball remain suspended frozen in the sky?",
        "resolution": "Because acceleration is the non-zero rate of change dv/dt = -9.8 m/s^2, the velocity does not remain zero; it immediately shifts from 0 to negative values, pulling the ball downward."
    },
    {
        "probe_id": "CDP-02",
        "competency_ref": "KIN-03",
        "student_trap": "Driving half the distance at 40 km/h and half at 60 km/h gives an average speed of 50 km/h.",
        "socratic_challenge": "Suppose the trip is 120 km total (60 km each half). At 40 km/h, the first half takes 1.5 hours. At 60 km/h, the second half takes 1.0 hour. Total time is 2.5 hours. What is 120 km divided by 2.5 hours?",
        "resolution": "120 / 2.5 = 48 km/h! The driver spent 1.5 hours at 40 km/h and only 1.0 hour at 60 km/h. Slower travel consumes more time, lowering the average speed below the arithmetic mean."
    },
    {
        "probe_id": "CDP-03",
        "competency_ref": "KIN-08",
        "student_trap": "A high-speed bullet fired horizontally stays airborne longer because its high velocity opposes gravity.",
        "socratic_challenge": "Which force opposes gravity along the vertical axis? Is there any upward lift or vertical aerodynamic force in a vacuum?",
        "resolution": "None! Gravity acts strictly downward (-g j) and has zero component horizontally. The bullet falls vertically at the exact same rate as a dropped coin."
    },
    {
        "probe_id": "CDP-04",
        "competency_ref": "KIN-04",
        "student_trap": "A negative velocity on a motion graph always means the object is decelerating (slowing down).",
        "socratic_challenge": "If a ball is falling downward at -20 m/s and one second later is moving at -30 m/s, is its speed increasing or decreasing? What is the sign of its velocity?",
        "resolution": "Speed is the absolute magnitude |v|: it increased from 20 m/s to 30 m/s! The object is speeding up in the negative direction. Deceleration only occurs when velocity and acceleration have opposite signs."
    },
    {
        "probe_id": "CDP-05",
        "competency_ref": "KIN-10",
        "student_trap": "Two stones dropped simultaneously from different heights accelerate toward each other as they fall.",
        "socratic_challenge": "Both stones experience acceleration a = -9.8 m/s^2. In each millisecond, by how much does stone 1's speed change? By how much does stone 2's speed change? What is the change in their difference in speeds?",
        "resolution": "Both speeds change at the exact same rate (-g), so their velocity difference Delta v = v1 - v2 remains strictly constant! Their relative acceleration is exactly zero."
    },
    {
        "probe_id": "CDP-06",
        "competency_ref": "KIN-11",
        "student_trap": "An x-t curve can form a circular loop if a particle travels in a circle.",
        "socratic_challenge": "If an x-t graph forms a circle, draw a vertical line through the center. How many x-coordinates does the curve assign to that single instant in time?",
        "resolution": "Two positions at the exact same clock time! A single physical particle cannot be in two distinct spatial locations simultaneously. Spatial circular trajectory is in the (x, y) plane, NOT the (x, t) plane."
    }
]

# Assemble Core 1B Blueprint
core1b_data = {
    "schema": "core1b-physics-reconstruction/v2",
    "version": "2.0.0",
    "subject": "Physics",
    "topic": "Kinematics: 1D Motion, 2D Projectiles & Relative Frames",
    "title": "Core 1B Phenomenological Reconstruction Cycles, Cognitive Dissonance Dialog & First-Move Priming",
    "canonical_topic_id": "phy-kinematics-1d-2d",
    "reconstruction_cycles": RECONSTRUCTION_CYCLES,
    "cognitive_dissonance_probes": COGNITIVE_DISSONANCE_PROBES
}

# Write Blueprints to disk
bp_1a_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_kinematics_ontology.v1.json"
bp_1b_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_kinematics_reconstruction.v1.json"

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

kin_adapter = all_adapters["topic_adapters"]["kinematics-1d-2d"]

# Link blueprint_refs
kin_adapter["blueprint_refs"] = {
    "core1a_ontology": "TEST/physics-research/blueprints/core1a_physics_kinematics_ontology.v1.json",
    "core1b_reconstruction": "TEST/physics-research/blueprints/core1b_physics_kinematics_reconstruction.v1.json"
}

# Add canonical_reasoning_moves
kin_adapter["canonical_reasoning_moves"] = {
    "stage_1_choose": "Declare spatial origin x = 0 (or launch level y = 0), define positive coordinate direction (+), and synchronize clock zero t = 0.",
    "stage_2_represent": "Construct UVATS 5-parameter state table, signed number line, or motion graph (x-t / v-t) capturing phase boundaries.",
    "stage_3_connect": "Select the exact kinematic quad equation eliminating the unmeasured variable, or decouple orthogonal 2D components.",
    "stage_4_execute_and_check": "Solve closed-form algebraic expressions and verify asymptotic limits (a -> 0, g -> 0, t -> 0) and dimensional homogeneity."
}

# Add first_move_atlas (exact match)
kin_adapter["first_move_atlas"] = FIRST_MOVE_ATLAS

with open(adapters_path, "w", encoding="utf-8") as f:
    json.dump(all_adapters, f, indent=2, ensure_ascii=False)
print(f"[OK] Updated TopicAdapters.v1.json with blueprint_refs, canonical_reasoning_moves, and first_move_atlas for kinematics-1d-2d.")
