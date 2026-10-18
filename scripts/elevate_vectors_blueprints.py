# scripts/elevate_vectors_blueprints.py
"""
Elevate Upstream Vectors Blueprints to Schema v2.0.0 and reciprocally align with TopicAdapters.v1.json.
Authority: Golden Benchmark Fixtures (Emailing physics-vectors-revised-core1.pdf & physics-vectors-revised-core2.pdf)
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 1. First-Move Atlas (11 rows, 1 per competency, exactly matching Golden PDF Page 25 & competencies)
FIRST_MOVE_ATLAS = [
    {
        "competency_id": "VEC-01",
        "cue": "signed 1D motion, direction reversal, or sign-convention declaration",
        "representation": "Declare + axis; mark signed displacement / velocity legs on 1D axis",
        "first_executable_move": "State coordinate frame (+x East/Right); write Delta x = sum(signed legs); translate final sign back to physical direction",
        "anti_pattern": "Treating negative sign as smaller physical magnitude rather than opposite direction"
    },
    {
        "competency_id": "VEC-02",
        "cue": "draw, compare, translate, or reverse free vectors",
        "representation": "Directed arrows with origin, length proportional to magnitude, and terminating arrowhead",
        "first_executable_move": "Verify equality: identical magnitude AND identical direction; translate free vector without rotating; reverse direction for opposite vector -A",
        "anti_pattern": "Assuming parallel vectors with different lengths or collinear opposite vectors are equal"
    },
    {
        "competency_id": "VEC-03",
        "cue": "components, quadrants, and angle reference relative to axes",
        "representation": "Cartesian coordinate axes (x, y) with vector arrow originating at origin and right projection triangle",
        "first_executable_move": "Identify adjacent side for cosine (A_adj = |A| cos theta) and opposite side for sine (A_opp = |A| sin theta); assign quadrant signs manually",
        "anti_pattern": "Blindly applying cos to horizontal and sin to vertical without checking the stated reference axis"
    },
    {
        "competency_id": "VEC-04",
        "cue": "two or more vectors added, resultant displacement, or polygon closure",
        "representation": "Head-to-tail polygon / component triangle with closing diagonal resultant arrow",
        "first_executable_move": "Place vectors head-to-tail; compute component sums R_x = sum(A_x) and R_y = sum(A_y); verify resultant |R| <= path length (triangle inequality)",
        "anti_pattern": "Adding scalar magnitudes directly when vectors act along non-parallel directions"
    },
    {
        "competency_id": "VEC-05",
        "cue": "change vector Delta v, momentum change Delta p, or vector subtraction",
        "representation": "Initial and final vectors drawn from common origin, with change vector pointing from tip of initial to tip of final",
        "first_executable_move": "Apply vector subtraction Delta v = v_f - v_i = v_f + (-v_i); subtract corresponding Cartesian components (Delta v_x = v_fx - v_ix, Delta v_y = v_fy - v_iy)",
        "anti_pattern": "Assuming Delta v = 0 when initial and final speeds are equal (|v_i| = |v_f|) despite a direction change"
    },
    {
        "competency_id": "VEC-06",
        "cue": "recover magnitude and compass direction from Cartesian components",
        "representation": "Right-angled component triangle with legs R_x, R_y and hypotenuse R",
        "first_executable_move": "Compute magnitude |R| = sqrt(R_x^2 + R_y^2); compute acute reference angle tan alpha = |R_y / R_x|; state compass direction from quadrant signs",
        "anti_pattern": "Reporting magnitude alone without stating direction, or leaving angle without a reference axis"
    },
    {
        "competency_id": "VEC-07",
        "cue": "relative velocity of object A with respect to observer B (v_A/B)",
        "representation": "Both velocity vectors plotted on common ground-frame axes; observer vector reversed",
        "first_executable_move": "Identify object A and observer B; subtract observer velocity: v_{A/B} = v_A - v_B; apply -v_B to all entities",
        "anti_pattern": "Reversing the subtraction order (computing v_B - v_A instead of v_A - v_B)"
    },
    {
        "competency_id": "VEC-08",
        "cue": "particle moving along circular path; tangential vs radial directions",
        "representation": "Circular orbit with radius vector, perpendicular tangent velocity v, and inward radial acceleration a_c",
        "first_executable_move": "Draw velocity tangent to curve in direction of motion; point centripetal acceleration radially inward toward center: a_c = v^2 / R",
        "anti_pattern": "Believing tangential velocity and radial centripetal acceleration act in the same direction"
    },
    {
        "competency_id": "VEC-09",
        "cue": "Newton-III interaction pairs vs single-body net force",
        "representation": "Two isolated free-body diagrams with body-on-body interaction labels (A on B vs B on A)",
        "first_executable_move": "Identify interacting bodies; write F_{A on B} = -F_{B on A}; ensure action-reaction pairs NEVER appear on the same isolated body FBD",
        "anti_pattern": "Cancelling action-reaction forces on a single object (e.g. normal force and gravity on a resting book)"
    },
    {
        "competency_id": "VEC-10",
        "cue": "angle between vectors, scalar dot product, or work sign determination",
        "representation": "Force vector F and displacement vector s originating from common origin with enclosed angle theta",
        "first_executable_move": "Measure true geometric tail-to-tail angle theta (0 <= theta <= 180 deg); compute W = F . s = |F||s| cos theta; sign follows cos theta",
        "anti_pattern": "Using angle with arbitrary axis instead of the true geometric angle between the two physical vectors"
    },
    {
        "competency_id": "VEC-11",
        "cue": "2D vector state bridging to motion in a plane or vector torque/cross product",
        "representation": "2D state vector v = v_x i + v_y j resolved into decoupled orthogonal evolution equations",
        "first_executable_move": "Decompose 2D vector state into two independent 1D scalar equations linked only by shared clock time t; or compute vector product magnitude |r x F| = r F sin theta",
        "anti_pattern": "Mixing orthogonal coordinates within a single 1D kinematic or dynamic equation"
    }
]

# 2. Canonical Strategy (4 Stages)
CANONICAL_STRATEGY = {
    "stage_1_choose": {
        "name": "System Demarcation & Coordinate Frame Declaration",
        "action": "Declare the physical entity or system boundary; establish reference frame (ground vs moving observer); define orthogonal axes (+x East/Right, +y North/Up) and clock zero t = 0.",
        "invariant": "Physical vector magnitude, relative velocity, and geometric dot products are invariant under rigid coordinate translation and rotation."
    },
    "stage_2_represent": {
        "name": "Free Vector & Geometric State Representation",
        "action": "Translate physical story into an exact geometric diagram: directed arrows drawn to scale, common-origin tail alignment, head-to-tail polygons, or orthogonal component projection triangles.",
        "invariant": "Typography floor: every diagram label, coordinate axis, and component notation must declare font-size >= 14px; free vectors may be translated parallel to themselves without alteration."
    },
    "stage_3_connect": {
        "name": "Governing Vector Laws & Invariant Constraints",
        "action": "Connect representation to fundamental vector algebra laws: component summation R_x = sum A_x, R_y = sum A_y; law of cosines R^2 = A^2 + B^2 + 2AB cos theta; Galilean relative shift v_{AB} = v_A - v_B; work dot product W = F . s.",
        "invariant": "Components along mutually perpendicular axes decouple completely; triangle inequality |A - B| <= |R| <= A + B strictly bounds all vector sums."
    },
    "stage_4_execute_and_check": {
        "name": "Algebraic Execution & Multi-Engine Verification",
        "action": "Execute algebra step-by-step; recover magnitude |R| = sqrt(R_x^2 + R_y^2) and compass quadrant direction; verify dimensional homogeneity [L], [L T^-1], [M L T^-2]; test dual limiting angles (theta = 0 deg, 90 deg, 180 deg).",
        "invariant": "Vector answers are incomplete without explicit direction and reference axis; signs must translate back to objective physical orientations."
    }
}

# 3. Structural Pillars (5 Invariants)
STRUCTURAL_PILLARS = [
    {
        "id": "P1",
        "name": "Geometric Invariance & Vector Identity",
        "principle": "A physical vector represents an objective geometric entity possessing magnitude and spatial orientation, invariant under rigid translations and rotations of Cartesian coordinates.",
        "canonical_expression": "|A|^2 = A_x^2 + A_y^2 = A_{x'}^2 + A_{y'}^2"
    },
    {
        "id": "P2",
        "name": "Orthogonal Basis Decomposition & Coordinate Projections",
        "principle": "Any coplanar vector A resolves uniquely into mutually perpendicular basis projections: A = A_x i + A_y j, where adjacent component uses cosine and opposite uses sine.",
        "canonical_expression": "A_x = |A| cos theta, A_y = |A| sin theta; i . j = 0, |i| = |j| = 1"
    },
    {
        "id": "P3",
        "name": "Linear Superposition & Triangle Inequality",
        "principle": "Vectors combine via geometric head-to-tail addition or component summation. Resultant magnitude is strictly bounded between antiparallel difference and parallel sum.",
        "canonical_expression": "R^2 = A^2 + B^2 + 2 A B cos theta; |A - B| <= |R| <= A + B"
    },
    {
        "id": "P4",
        "name": "Galilean Relative Kinematics & Observer Subtraction",
        "principle": "Velocity of object A perceived by observer B is obtained by subtracting observer velocity vector: v_{AB} = v_A - v_B. Shared acceleration cancels identically in relative motion.",
        "canonical_expression": "v_{AB} = v_A - v_B; v_{AB} = -v_{BA}; v_{AC} = v_{AB} + v_{BC}"
    },
    {
        "id": "P5",
        "name": "Metric Products: Scalar Projection & Vector Antisymmetry",
        "principle": "The scalar (dot) product evaluates parallel projection and work (W = F . s = |F||s| cos theta); the vector (cross) product evaluates perpendicular moment arm and rotational torque.",
        "canonical_expression": "A . B = B . A; A x B = -(B x A); A perp B <=> A . B = 0; A || B <=> A x B = 0"
    }
]

# 4. Atomic Competencies Mapping (11 Competencies matching Golden PDF & TopicAdapters)
ATOMIC_COMPETENCIES = {
    "VEC-01": {
        "title": "Scalars, Vectors & Signed Axis Conventions",
        "definition": "Distinction between scalar magnitudes and vector quantities possessing spatial orientation, encoded along 1D axes via positive and negative signs.",
        "canonical_rules": [
            "A scalar is complete with magnitude alone (distance, speed, mass, time).",
            "A vector requires magnitude and spatial direction (displacement, velocity, acceleration, force).",
            "In 1D, sign has physical meaning only after a positive axis convention is explicitly declared.",
            "Reversing the positive axis flips algebraic signs but leaves physical reality invariant."
        ],
        "operational_heuristics": [
            "Do not classify from units alone. Ask whether reversing spatial direction alters the physical state.",
            "Declare +x East/Right or +y North/Up before writing any numeric signs.",
            "Sum signed displacements algebraically: Delta x = sum(signed legs)."
        ],
        "boundary_conditions": [
            "Pure forward motion: Delta x > 0, distance = displacement.",
            "Complete round-trip: displacement = 0, distance = 2d > 0."
        ],
        "prerequisites": ["P1"],
        "transfer_targets": ["PHYS-VEC-001", "PHYS-VEC-002"]
    },
    "VEC-02": {
        "title": "Vector Equality, Opposite Vectors & Null Vector",
        "definition": "Geometric representation of free vectors as directed line segments invariant under rigid spatial translation.",
        "canonical_rules": [
            "Length of arrow represents magnitude; arrowhead indicates direction.",
            "Equal vectors must have both identical magnitude and identical spatial orientation.",
            "Translating a free vector parallel to itself without rotation leaves the vector unchanged.",
            "Opposite vector -A has identical magnitude |A| but points in the antiparallel direction (180 deg reversal)."
        ],
        "operational_heuristics": [
            "Draw free vectors with clear origins and distinct arrowheads.",
            "To form -A, invert the arrowhead while preserving line orientation and length."
        ],
        "boundary_conditions": [
            "Collinear opposite: A + (-A) = 0.",
            "Equal vectors: A - B = 0 <=> A = B."
        ],
        "prerequisites": ["P1", "VEC-01"],
        "transfer_targets": ["PHYS-VEC-003", "PHYS-VEC-004"]
    },
    "VEC-03": {
        "title": "Orthogonal Components, Quadrants & Angle References",
        "definition": "Orthogonal Cartesian decomposition of coplanar vectors into signed projection coordinates.",
        "canonical_rules": [
            "Components are signed projections of a vector onto chosen perpendicular coordinate axes.",
            "The side adjacent to stated angle theta receives cosine: A_adj = |A| cos theta.",
            "The side opposite to stated angle theta receives sine: A_opp = |A| sin theta.",
            "Cartesian quadrant determines algebraic signs: QI (+,+), QII (-,+), QIII (-,-), QIV (+,-)."
        ],
        "operational_heuristics": [
            "Mark coordinate axes (+x, +y) before calculating components.",
            "Trace right-angled projection triangle: adjacent side is cos, opposite side is sin.",
            "Verify Pythagorean reconstruction: A_x^2 + A_y^2 = |A|^2."
        ],
        "boundary_conditions": [
            "theta = 0 deg to x-axis: A_x = |A|, A_y = 0.",
            "theta = 90 deg to x-axis: A_x = 0, A_y = |A|."
        ],
        "prerequisites": ["P2", "VEC-02"],
        "transfer_targets": ["PHYS-VEC-005", "PHYS-VEC-006"]
    },
    "VEC-04": {
        "title": "Vector Addition, Triangle & Parallelogram Laws, Resultant",
        "definition": "Geometric and analytical superposition of concurrent vectors using head-to-tail polygon and component summation.",
        "canonical_rules": [
            "Head-to-tail rule: place tail of B at head of A; resultant R runs from tail of A to head of B.",
            "Component route: R_x = sum(A_x) and R_y = sum(A_y).",
            "Analytical magnitude: R^2 = A^2 + B^2 + 2 A B cos theta.",
            "Triangle inequality bound: |A - B| <= |R| <= A + B."
        ],
        "operational_heuristics": [
            "Resultant is the closing vector, not the arithmetic sum of path lengths.",
            "For perpendicular vectors (theta = 90 deg): |R| = sqrt(A^2 + B^2).",
            "For closed geometric loop returning to start: resultant is strictly zero."
        ],
        "boundary_conditions": [
            "Parallel vectors (theta = 0 deg): R = A + B (maximum).",
            "Antiparallel vectors (theta = 180 deg): R = |A - B| (minimum).",
            "Orthogonal vectors (theta = 90 deg): R = sqrt(A^2 + B^2)."
        ],
        "prerequisites": ["P3", "VEC-03"],
        "transfer_targets": ["PHYS-VEC-007", "PHYS-VEC-008", "PHYS-VEC-021"]
    },
    "VEC-05": {
        "title": "Vector Subtraction & Change Vectors",
        "definition": "Constructing change vectors Delta v = v_f - v_i and Delta p = p_f - p_i through addition of the opposite vector.",
        "canonical_rules": [
            "Vector subtraction means adding the opposite: A - B = A + (-B).",
            "Change vector Delta v = v_f - v_i connects the tip of v_i to the tip of v_f when drawn from a common origin.",
            "Component subtraction: Delta v_x = v_fx - v_ix and Delta v_y = v_fy - v_iy.",
            "Constant speed with changing direction yields a non-zero change vector: |Delta v| = 2v sin(theta/2) != 0."
        ],
        "operational_heuristics": [
            "Draw initial and final vectors from a common origin to visualize the change vector pointing from initial tip to final tip.",
            "Subtract x from x and y from y.",
            "Impulse direction matches change in momentum vector: J = Delta p = m Delta v."
        ],
        "boundary_conditions": [
            "No direction change, speed unchanged: Delta v = 0.",
            "180 deg reversal at speed v: Delta v = -2v, |Delta v| = 2v.",
            "90 deg turn at speed v: |Delta v| = v sqrt(2)."
        ],
        "prerequisites": ["P3", "VEC-04"],
        "transfer_targets": ["PHYS-VEC-009", "PHYS-VEC-010", "PHYS-VEC-022"]
    },
    "VEC-06": {
        "title": "Magnitude & Direction Angle Recovery",
        "definition": "Synthesis of net magnitude and compass orientation from Cartesian coordinate components.",
        "canonical_rules": [
            "Magnitude is hypotenuse of Cartesian component triangle: |R| = sqrt(R_x^2 + R_y^2).",
            "Acute reference angle: tan alpha = |R_y / R_x|.",
            "Physical orientation must declare reference axis and quadrant direction (e.g., 53.1 deg North of East).",
            "Magnitude alone is an incomplete vector response."
        ],
        "operational_heuristics": [
            "Sketch component rectangle to identify correct quadrant.",
            "State direction clearly: angle measured from stated cardinal direction (East, West, North, South).",
            "Check sanity: |R| must be greater than or equal to both |R_x| and |R_y| and strictly <= |R_x| + |R_y|."
        ],
        "boundary_conditions": [
            "R_x = 0: vector is purely vertical along y-axis.",
            "R_y = 0: vector is purely horizontal along x-axis.",
            "|R_x| = |R_y|: alpha = 45 deg, |R| = |R_x| sqrt(2)."
        ],
        "prerequisites": ["P2", "VEC-03"],
        "transfer_targets": ["PHYS-VEC-011", "PHYS-VEC-012"]
    },
    "VEC-07": {
        "title": "Relative Velocity in 1D & 2D Frames",
        "definition": "Kinematic transformation of velocities between reference frames via vector subtraction.",
        "canonical_rules": [
            "Relative velocity of object A with respect to observer B: v_{AB} = v_A - v_B.",
            "The observer is the vector you subtract: to shift to observer B's rest frame, apply -v_B to all entities.",
            "Antisymmetric reciprocity: v_{AB} = -v_{BA}.",
            "Transitive velocity chain: v_{AC} = v_{AB} + v_{BC}."
        ],
        "operational_heuristics": [
            "Name roles explicitly: object A, observer B.",
            "Express both ground-frame velocities in the same coordinate frame before subtracting.",
            "If A and B move with identical velocities (v_A = v_B), relative velocity vanishes: v_{AB} = 0."
        ],
        "boundary_conditions": [
            "Collinear same direction: v_{rel} = |v_A - v_B|.",
            "Collinear opposite direction: v_{rel} = v_A + v_B.",
            "Perpendicular velocities: v_{rel} = sqrt(v_A^2 + v_B^2)."
        ],
        "prerequisites": ["P4", "VEC-05"],
        "transfer_targets": ["PHYS-VEC-013", "PHYS-VEC-014", "PHYS-VEC-023"]
    },
    "VEC-08": {
        "title": "Radial & Tangential Decomposition in Curvilinear Paths",
        "definition": "Decomposition of curvilinear kinematics into orthogonal instantaneous tangent and centripetal radial directions.",
        "canonical_rules": [
            "Instantaneous velocity is strictly tangent to the curved path at all times.",
            "Centripetal acceleration points radially inward toward the instantaneous center of curvature.",
            "Tangent and radial directions are mutually perpendicular: v . a_c = 0.",
            "Cutting the radial constraint releases the particle tangentially along its instantaneous velocity vector."
        ],
        "operational_heuristics": [
            "Draw position radius vector from center to particle.",
            "Draw velocity tangent to circle perpendicular to radius.",
            "Point centripetal acceleration inward: a_c = v^2 / R.",
            "Never show centripetal acceleration pointing outward (centrifugal pseudo-force exists only in rotating frame)."
        ],
        "boundary_conditions": [
            "Straight path (R -> infinity): a_c -> 0, motion is 1D.",
            "String breaks: tension drops to zero instantly; particle flies along tangent with speed v."
        ],
        "prerequisites": ["P2", "VEC-05"],
        "transfer_targets": ["PHYS-VEC-015", "PHYS-VEC-016"]
    },
    "VEC-09": {
        "title": "Component Ownership & Inclined Plane Decomposition",
        "definition": "Newton's third law vector symmetry and isolation of single-body free-body diagrams.",
        "canonical_rules": [
            "Newton-III pairs are equal in magnitude and opposite in direction: F_{A on B} = -F_{B on A}.",
            "Action-reaction pairs act on different bodies and can NEVER appear on the same isolated body diagram.",
            "Net force on body B includes ONLY forces acting on B: sum F_B = m a_B.",
            "Forces acting on the same body that balance (e.g. N and mg on resting book) are NOT a third-law pair."
        ],
        "operational_heuristics": [
            "Always label forces with dual-body notation: 'Agent on Target'.",
            "To find Newton-III partner, swap agent and target: F_{table on book} <-> F_{book on table}.",
            "Verify partners belong to different FBDs."
        ],
        "boundary_conditions": [
            "Zero net acceleration: forces on chosen body balance (sum F = 0); action-reaction forces remain equal and opposite regardless of acceleration."
        ],
        "prerequisites": ["P1", "VEC-02"],
        "transfer_targets": ["PHYS-VEC-017", "PHYS-VEC-018"]
    },
    "VEC-10": {
        "title": "Scalar (Dot) Product, Projection & Work Mechanics",
        "definition": "Scalar dot product evaluation and geometric dependence of mechanical work on vector orientation.",
        "canonical_rules": [
            "Mechanical work is the scalar product of force and displacement: W = F . s = |F||s| cos theta.",
            "Angle theta is the geometric angle between the two arrows drawn from a common origin (0 <= theta <= 180 deg).",
            "Sign of work depends strictly on cos theta: acute angle (theta < 90 deg) => W > 0; perpendicular (theta = 90 deg) => W = 0; obtuse angle (theta > 90 deg) => W < 0.",
            "Braking or opposing forces act antiparallel (theta = 180 deg), doing negative work W = -F s."
        ],
        "operational_heuristics": [
            "Draw force and displacement arrows tail-to-tail to identify true enclosed angle theta.",
            "Check special angles: 0 deg (+Fs), 90 deg (0), 180 deg (-Fs).",
            "Centripetal force is always perpendicular to tangent displacement, doing zero work: W_c = 0."
        ],
        "boundary_conditions": [
            "theta = 0 deg: maximum positive work W = +F s.",
            "theta = 90 deg: zero work W = 0 (e.g., circular orbit gravity).",
            "theta = 180 deg: maximum negative work W = -F s (e.g., kinetic friction)."
        ],
        "prerequisites": ["P5", "VEC-03"],
        "transfer_targets": ["PHYS-VEC-019", "PHYS-VEC-020", "PHYS-VEC-024"]
    },
    "VEC-11": {
        "title": "Vector (Cross) Product, Torque & Planar Orthogonal Invariants",
        "definition": "Synthesis of vector states into decoupled component differential systems and introductory vector cross product.",
        "canonical_rules": [
            "A 2D vector state v = v_x i + v_y j splits into two independent component equations sharing clock time t.",
            "Perpendicular motions evolve independently: a_x alters only v_x; a_y alters only v_y.",
            "Vector cross product tau = r x F produces a perpendicular vector of magnitude |tau| = |r||F| sin theta.",
            "Torque vanishes when force is collinear with lever arm (theta = 0 deg or 180 deg)."
        ],
        "operational_heuristics": [
            "Separate 2D vector kinematics into independent x and y equations.",
            "Never cross terms between orthogonal axes in uniform field.",
            "For torque, use perpendicular lever arm r_perp = r sin theta: tau = r_perp F."
        ],
        "boundary_conditions": [
            "r || F (theta = 0 or 180 deg): tau = 0 (no rotational turning effect).",
            "r perp F (theta = 90 deg): tau = r F (maximum torque)."
        ],
        "prerequisites": ["P2", "P5", "VEC-06", "VEC-10"],
        "transfer_targets": ["PHYS-VEC-025"]
    }
}

# 5. Dependency Graph
DEPENDENCY_GRAPH = {
    "layers": [
        {
            "layer_index": 1,
            "name": "Primitive Geometric Primitives",
            "nodes": [
                {"id": "NODE-1.1", "term": "Scalar Magnitude", "description": "Non-negative real number representing quantity size with physical units."},
                {"id": "NODE-1.2", "term": "Spatial Directed Arrow", "description": "Geometric object possessing origin, orientation ray, and terminating arrowhead."},
                {"id": "NODE-1.3", "term": "Coordinate Frame & Signed Axes", "description": "Chosen origin and orthogonal basis vectors establishing positive orientation."}
            ]
        },
        {
            "layer_index": 2,
            "name": "Vector Decomposition & Algebra",
            "nodes": [
                {"id": "NODE-2.1", "term": "Orthogonal Projection & Trigonometric Components", "depends_on": ["NODE-1.1", "NODE-1.2", "NODE-1.3"]},
                {"id": "NODE-2.2", "term": "Head-to-Tail Triangle Addition", "depends_on": ["NODE-1.1", "NODE-1.2"]},
                {"id": "NODE-2.3", "term": "Vector Subtraction & Additive Inverse", "depends_on": ["NODE-1.2", "NODE-2.2"]}
            ]
        },
        {
            "layer_index": 3,
            "name": "Kinematic & Dynamic Projections",
            "nodes": [
                {"id": "NODE-3.1", "term": "Change Vector Delta v and Acceleration Direction", "depends_on": ["NODE-2.3"]},
                {"id": "NODE-3.2", "term": "Galilean Relative Motion Frames", "depends_on": ["NODE-2.3"]},
                {"id": "NODE-3.3", "term": "Curvilinear Normal & Tangential Decomposition", "depends_on": ["NODE-2.1", "NODE-3.1"]}
            ]
        },
        {
            "layer_index": 4,
            "name": "Advanced Invariants & Dual Metric Products",
            "nodes": [
                {"id": "NODE-4.1", "term": "Scalar Dot Product & Direction Cosines", "depends_on": ["NODE-2.1"]},
                {"id": "NODE-4.2", "term": "Vector Cross Product & Moment Arm Antisymmetry", "depends_on": ["NODE-2.1"]},
                {"id": "NODE-4.3", "term": "Planar 2D Decoupling (Bridge to Projectiles)", "depends_on": ["NODE-2.1", "NODE-3.1"]}
            ]
        }
    ]
}

# 6. Cognitive Conflict Matrix
COGNITIVE_CONFLICT_MATRIX = [
    {
        "id": "CCM-01",
        "concept": "Vector Addition vs Magnitude Summation",
        "intuitive_misconception": "If displacement A is 4 m and displacement B is 3 m, the resultant displacement must be 7 m.",
        "newtonian_scientific_truth": "The resultant depends strictly on the spatial angle theta: R = sqrt(4^2 + 3^2 + 2(4)(3) cos theta). It can range anywhere between 1 m (antiparallel) and 7 m (collinear). For orthogonal displacements, R = 5 m.",
        "decisive_experiment": "Walking 4 meters East then 3 meters North. Direct laser measurement to origin confirms 5 meters net displacement, not 7 meters."
    },
    {
        "id": "CCM-02",
        "concept": "Negative Signs in Vector Components",
        "intuitive_misconception": "A negative vector component (e.g., -10 m/s) represents a smaller physical magnitude or a 'defective' speed compared to +2 m/s.",
        "newtonian_scientific_truth": "The sign designates direction relative to an arbitrary declared coordinate axis. An object moving at -10 m/s has five times the speed (kinetic energy) of one moving at +2 m/s; it simply travels in the opposite direction.",
        "decisive_experiment": "Flipping coordinate convention (+x pointing West instead of East) instantly changes the sign of all velocity components without modifying the physical motion of vehicles."
    },
    {
        "id": "CCM-03",
        "concept": "Trigonometric Component Reference Fallacy",
        "intuitive_misconception": "Horizontal component is always cos theta and vertical component is always sin theta.",
        "newtonian_scientific_truth": "The trigonometric function is governed by the triangle geometry: the side adjacent to angle theta receives cos theta, while the side opposite receives sin theta. If theta is measured from the vertical, vertical component is A cos theta and horizontal is A sin theta.",
        "decisive_experiment": "Resolving gravity weight along an inclined plane where incline angle theta is measured from horizontal: normal force perpendicular to incline is mg cos theta, not mg sin theta."
    },
    {
        "id": "CCM-04",
        "concept": "Velocity Change at Constant Speed",
        "intuitive_misconception": "If an object travels along a circular path at a constant speed of 10 m/s, its change in velocity is zero because its speed does not change.",
        "newtonian_scientific_truth": "Velocity is a vector. Changing direction changes the vector state even if magnitude is constant: Delta v = v_f - v_i. For a 90-degree turn at speed v, |Delta v| = v sqrt(2) != 0, requiring a continuous net centripetal force.",
        "decisive_experiment": "Tracking accelerometer readings inside a vehicle rounding a curve at constant speedometer speed: accelerometer registers substantial lateral centripetal acceleration."
    },
    {
        "id": "CCM-05",
        "concept": "Action-Reaction vs Balanced Forces on One Body",
        "intuitive_misconception": "The normal force of a table pushing up on a book and the gravitational weight of the Earth pulling down on the book are an action-reaction pair because they are equal and opposite.",
        "newtonian_scientific_truth": "Both normal force and gravity act on the SAME body (the book). Action-reaction pairs must act on DIFFERENT bodies. The reaction to table-on-book is book-on-table; the reaction to Earth-on-book is book-on-Earth.",
        "decisive_experiment": "Placing the table in an accelerating elevator: normal force changes to m(g + a) while gravity remains mg; the forces no longer balance on the book, yet Newton-III partners remain exactly equal and opposite."
    },
    {
        "id": "CCM-06",
        "concept": "Sign of Work and Geometric Angle",
        "intuitive_misconception": "Braking force does positive work because the braking force is strong, or work is always positive because energy is a scalar.",
        "newtonian_scientific_truth": "Work is a signed scalar: W = F . s = |F||s| cos theta. When force opposes displacement (theta = 180 deg), cos(180) = -1, and work is strictly negative. Negative work removes kinetic energy from the object.",
        "decisive_experiment": "Measuring vehicle kinetic energy before and after braking: delta K = W_brake < 0; vehicle kinetic energy decreases by exactly the work done by friction."
    }
]

# Assemble Core 1A Blueprint
core1a_data = {
    "schema": "core1a-physics-ontology/v2",
    "version": "2.0.0",
    "subject": "Physics",
    "topic": "Vectors & Coordinate Frames: Components, Resultants & Geometric Invariants",
    "title": "Grade 9 Olympiad Physics Core 1A Ontology: Vectors & Coordinate Frames",
    "source_authority": "Golden Benchmark Fixtures (Emailing physics-vectors-revised-core1.pdf & physics-vectors-revised-core2.pdf)",
    "canonical_topic_id": "phy-vectors-and-components",
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
        "phenomenon": "Signed 1D Motion & Frame Orientation Invariance",
        "competency_ref": "VEC-01",
        "standard_derivation": "Choose +x East. Cart moves +7 m, -11 m, +2 m. Displacement is Delta x = (+7) + (-11) + (+2) = -2 m (2 m West). Total distance is d = |+7| + |-11| + |+2| = 20 m.",
        "phenomenological_reconstruction": {
            "perspective": "Coordinate Inversion & Orientation Duality",
            "conceptual_pivot": "The positive sign does not mean 'good' or 'increasing'; it designates alignment with a declared reference arrow. Flipping the reference axis (+x West) transforms the displacements to -7 m, +11 m, -2 m, yielding Delta x = +2 m (still 2 m West). Physical displacement is completely invariant under choice of axis orientation.",
            "scalar_vs_vector_boundary": "Distance accumulates total odometer path regardless of heading (scalar d = 20 m). Displacement preserves the net spatial translation between origin and terminal location (vector Delta x = 2 m West)."
        },
        "limiting_boundary_checks": [
            {
                "limit": "Pure unidirectional travel (all displacements collinear)",
                "physical_consequence": "Displacement magnitude equals total distance traveled: |Delta x| = d."
            },
            {
                "limit": "Closed circuit (returns exactly to starting coordinate)",
                "physical_consequence": "Net displacement vanishes identically (Delta x = 0), while path distance d > 0."
            }
        ]
    },
    {
        "cycle_id": "RECON-02",
        "phenomenon": "Parallelogram Superposition & Triangle Inequality Bounds",
        "competency_ref": "VEC-04",
        "standard_derivation": "Two vectors A and B act at angle theta. Analytical resultant: R^2 = A^2 + B^2 + 2 A B cos theta. Extreme bounds: theta = 0 deg gives R_max = A + B; theta = 180 deg gives R_min = |A - B|; theta = 90 deg gives Pythagoras R = sqrt(A^2 + B^2).",
        "phenomenological_reconstruction": {
            "perspective": "Geometric Superposition & Tethered Dynamometer Pull",
            "conceptual_pivot": "Imagine two students pulling a tethered ring with dynamometers of calibrated forces A and B. When pulling parallel, tensions add directly to maximum A + B. As one student walks in an arc around the ring, the net pull smoothly decreases. At 90 deg, the right-angle Pythagorean diagonal emerges. At 180 deg, they pull in direct opposition, yielding minimum tension |A - B|.",
            "geometric_closure": "For three vectors in equilibrium (A + B + C = 0), the three arrows must form a closed triangle head-to-tail, proving C = -(A + B)."
        },
        "limiting_boundary_checks": [
            {
                "limit": "Parallel forces (theta -> 0 deg)",
                "physical_consequence": "cos(0) = 1 => R = sqrt(A^2 + B^2 + 2AB) = A + B (algebraic sum)."
            },
            {
                "limit": "Antiparallel forces (theta -> 180 deg)",
                "physical_consequence": "cos(180) = -1 => R = sqrt(A^2 + B^2 - 2AB) = |A - B| (algebraic cancellation)."
            },
            {
                "limit": "Equal magnitude orthogonal forces (A = B, theta = 90 deg)",
                "physical_consequence": "cos(90) = 0 => R = A sqrt(2), bisecting the angle at exactly 45 deg."
            }
        ]
    },
    {
        "cycle_id": "RECON-03",
        "phenomenon": "Velocity Change Vector at Constant Speed (Geometric Turn)",
        "competency_ref": "VEC-05",
        "standard_derivation": "Particle moves with speed v turning through angle theta: v_i = v i, v_f = v cos theta i + v sin theta j. Change in velocity is Delta v = v_f - v_i = v(cos theta - 1) i + v sin theta j. Magnitude: |Delta v| = sqrt(v^2 (cos theta - 1)^2 + v^2 sin^2 theta) = sqrt(2 v^2 (1 - cos theta)) = 2v sin(theta/2).",
        "phenomenological_reconstruction": {
            "perspective": "Common Origin Vector Subtraction",
            "conceptual_pivot": "Novices confuse change in speed with change in velocity. Speed is constant (|v_i| = |v_f| = v), but velocity direction rotates. Reconstruct by drawing both vectors from a single point: Delta v is the directed vector pointing from the tip of v_i to the tip of v_f.",
            "dynamic_necessity": "Because Delta v != 0, Newton's second law dictates that a net force and impulse J = m Delta v must act continuously toward the interior of the turn to bend the trajectory."
        },
        "limiting_boundary_checks": [
            {
                "limit": "Zero turn (theta -> 0 deg)",
                "physical_consequence": "sin(0) = 0 => |Delta v| = 0 (no acceleration, uniform straight-line motion)."
            },
            {
                "limit": "90 deg perpendicular corner (theta = 90 deg)",
                "physical_consequence": "|Delta v| = 2v sin(45 deg) = v sqrt(2), directed at 45 deg inward."
            },
            {
                "limit": "180 deg U-turn reversal (theta = 180 deg)",
                "physical_consequence": "|Delta v| = 2v sin(90 deg) = 2v (doubled velocity change, antiparallel)."
            }
        ]
    },
    {
        "cycle_id": "RECON-04",
        "phenomenon": "The Observer as the Subtracted Vector (Galilean Relative Shift)",
        "competency_ref": "VEC-07",
        "standard_derivation": "Object A moves at v_A; observer B moves at v_B. Relative velocity of A with respect to B is v_{AB} = v_A - v_B. In components: v_{AB,x} = v_{Ax} - v_{Bx}, v_{AB,y} = v_{Ay} - v_{By}.",
        "phenomenological_reconstruction": {
            "perspective": "Moving Frame Superposition",
            "conceptual_pivot": "To see what observer B sees, we must bring observer B to rest. Bringing B to rest requires applying an opposing velocity -v_B to B. By Galilean invariance, we must apply this exact same transformation velocity -v_B to every other object in the universe.",
            "relative_reality": "Object A thus possesses its own ground velocity v_A plus the observer correction -v_B: v_{AB} = v_A + (-v_B) = v_A - v_B. If both objects travel with identical velocity vectors, the relative velocity vanishes identically."
        },
        "limiting_boundary_checks": [
            {
                "limit": "Identical velocities (v_A = v_B)",
                "physical_consequence": "v_{AB} = 0; objects appear stationary relative to each other."
            },
            {
                "limit": "Stationary observer (v_B = 0)",
                "physical_consequence": "v_{AB} = v_A; recovers standard ground-frame velocity."
            },
            {
                "limit": "Head-on collinear collision (v_A = v i, v_B = -u i)",
                "physical_consequence": "v_{AB} = v - (-u) = v + u (relative closing speed is the sum)."
            }
        ]
    },
    {
        "cycle_id": "RECON-05",
        "phenomenon": "Newton-III Action-Reaction vs Single-Body Net Force",
        "competency_ref": "VEC-09",
        "standard_derivation": "Body A exerts force F_{A on B} on body B; body B exerts force F_{B on A} on body A. Third law states F_{A on B} = -F_{B on A}. Net force on body B is sum F_B = F_{A on B} + F_{ext on B} = m_B a_B.",
        "phenomenological_reconstruction": {
            "perspective": "Body-Ownership Demarcation",
            "conceptual_pivot": "Equal-and-opposite forces can NEVER cancel each other unless they act on the EXACT SAME body. F_{A on B} acts on body B; F_{B on A} acts on body A. Because they live on separate free-body diagrams, they never enter the same net force equation.",
            "resting_book_fallacy": "A book resting on a table experiences downward gravity F_{Earth on book} and upward normal force F_{table on book}. These balance because sum F_{book} = 0 (first law), NOT because of the third law! Their third-law partners are F_{book on Earth} (upward on Earth) and F_{book on table} (downward on table)."
        },
        "limiting_boundary_checks": [
            {
                "limit": "Accelerating table (elevator accelerates upward with a)",
                "physical_consequence": "Normal force becomes N = m(g + a) != mg; forces on book no longer balance, yet F_{table on book} and F_{book on table} remain strictly equal and opposite."
            },
            {
                "limit": "Free fall in vacuum",
                "physical_consequence": "Normal force vanishes (N = 0); gravity accelerates book at g, with book pulling Earth upward with equal force mg."
            }
        ]
    },
    {
        "cycle_id": "RECON-06",
        "phenomenon": "Geometric Angle Control over Work Sign",
        "competency_ref": "VEC-10",
        "standard_derivation": "Force F acts on body while undergoing displacement s. Enclosed geometric angle is theta. Scalar work: W = F . s = |F||s| cos theta. cos theta > 0 for 0 <= theta < 90 deg; cos theta = 0 for theta = 90 deg; cos theta < 0 for 90 < theta <= 180 deg.",
        "phenomenological_reconstruction": {
            "perspective": "Energy Transfer Vector Geometry",
            "conceptual_pivot": "Work is energy transferred by a force acting through a displacement. When force possesses a component along the direction of motion, it speeds the particle up (positive work, energy added). When force opposes motion, it slows the particle down (negative work, energy extracted). When force is strictly perpendicular, it only turns the particle without changing kinetic energy (zero work).",
            "braking_invariant": "A braking force acts opposite to displacement (theta = 180 deg), giving cos(180) = -1 and W = -F s. The negative sign represents kinetic energy dissipated into thermal energy."
        },
        "limiting_boundary_checks": [
            {
                "limit": "Parallel alignment (theta = 0 deg)",
                "physical_consequence": "cos(0) = 1 => W = +F s (maximum energy delivered)."
            },
            {
                "limit": "Perpendicular alignment (theta = 90 deg)",
                "physical_consequence": "cos(90) = 0 => W = 0 (e.g., centripetal tension, normal force on level surface)."
            },
            {
                "limit": "Antiparallel alignment (theta = 180 deg)",
                "physical_consequence": "cos(180) = -1 => W = -F s (maximum energy extracted)."
            }
        ]
    }
]

COGNITIVE_DISSONANCE_PROBES = [
    {
        "probe_id": "CDP-01",
        "competency_ref": "VEC-01",
        "student_trap": "A velocity of -15 m/s is smaller than a velocity of +5 m/s because negative numbers are smaller than positive numbers on a number line.",
        "socratic_challenge": "If a car moving at -15 m/s crashes into a wall, does it cause less structural damage than a car moving at +5 m/s?",
        "resolution": "No! Kinetic energy is proportional to speed squared (v^2). The car moving at -15 m/s carries 9 times the kinetic energy of the car at +5 m/s. The negative sign merely indicates the car travels West instead of East."
    },
    {
        "probe_id": "CDP-02",
        "competency_ref": "VEC-04",
        "student_trap": "Adding a 6 N force and an 8 N force must always produce a 14 N force.",
        "socratic_challenge": "What happens if one person pulls a rope to the right with 8 N and another pulls to the left with 6 N? What happens if they pull at right angles?",
        "resolution": "Forces are vectors! They combine according to spatial geometry: R = sqrt(6^2 + 8^2 + 2(6)(8) cos theta). The resultant can be anything between 2 N (opposite) and 14 N (parallel). At right angles, R = 10 N."
    },
    {
        "probe_id": "CDP-03",
        "competency_ref": "VEC-05",
        "student_trap": "A cyclist travels around a corner at a steady 6 m/s. Because the speedometer stays at 6 m/s, the change in velocity is zero.",
        "socratic_challenge": "Is velocity just a speed number, or does it include heading? If you turn from East to North, did your direction change?",
        "resolution": "Velocity includes direction! v_i = 6 i m/s and v_f = 6 j m/s. The change vector is Delta v = 6 j - 6 i m/s, with magnitude |Delta v| = 6 sqrt(2) m/s. Turning requires an inward sideways push."
    },
    {
        "probe_id": "CDP-04",
        "competency_ref": "VEC-07",
        "student_trap": "If Cyclist A moves East at 8 m/s and Cyclist B moves East at 5 m/s, A sees B moving forward at 3 m/s.",
        "socratic_challenge": "Cyclist A is traveling faster than Cyclist B. As A looks over their shoulder at B, is B getting closer or falling farther behind?",
        "resolution": "B is falling behind! To find A's view of B, compute v_{B/A} = v_B - v_A = 5 - 8 = -3 m/s (3 m/s West). B appears to drift backward in A's frame."
    },
    {
        "probe_id": "CDP-05",
        "competency_ref": "VEC-09",
        "student_trap": "A book rests on a table. The normal force pushes up and gravity pulls down with equal magnitude. Therefore, normal force and gravity are a Newton-III action-reaction pair.",
        "socratic_challenge": "If you take the table away, gravity still pulls down on the book, but where did the normal force go? Can one partner of an action-reaction pair exist without the other?",
        "resolution": "Never! Action-reaction partners must be of the same physical interaction type and act on different bodies. Normal force is a contact electromagnetic force (table on book <-> book on table). Gravity is a mass attraction (Earth on book <-> book on Earth)."
    },
    {
        "probe_id": "CDP-06",
        "competency_ref": "VEC-10",
        "student_trap": "Work is defined as force times distance, so pushing against a moving sled always adds energy and does positive work.",
        "socratic_challenge": "If a sled slides toward you and you push against it to slow it down, does the sled speed up or lose kinetic energy?",
        "resolution": "It loses kinetic energy! When force opposes displacement (theta = 180 deg), cos(180) = -1, and work is negative: W = -F s. Negative work removes kinetic energy from the system."
    }
]

# Assemble Core 1B Blueprint
core1b_data = {
    "schema": "core1b-physics-reconstruction/v2",
    "version": "2.0.0",
    "subject": "Physics",
    "topic": "Vectors & Coordinate Frames: Components, Resultants & Geometric Invariants",
    "title": "Grade 9 Olympiad Physics Core 1B Phenomenological Reconstruction: Vectors & Coordinate Frames",
    "canonical_topic_id": "phy-vectors-and-components",
    "reconstruction_cycles": RECONSTRUCTION_CYCLES,
    "cognitive_dissonance_probes": COGNITIVE_DISSONANCE_PROBES
}

# Write Blueprints to disk
bp_1a_path = REPO_ROOT / "TEST/physics-research/blueprints/core1a_physics_vectors_ontology.v1.json"
bp_1b_path = REPO_ROOT / "TEST/physics-research/blueprints/core1b_physics_vectors_reconstruction.v1.json"

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

vec_adapter = all_adapters["topic_adapters"]["vectors-and-components"]

# Link blueprint_refs
vec_adapter["blueprint_refs"] = {
    "core1a_ontology": "TEST/physics-research/blueprints/core1a_physics_vectors_ontology.v1.json",
    "core1b_reconstruction": "TEST/physics-research/blueprints/core1b_physics_vectors_reconstruction.v1.json"
}

# Add canonical_reasoning_moves
vec_adapter["canonical_reasoning_moves"] = {
    "stage_1_choose": "Declare reference frame, orthogonal coordinate axes (+x East, +y North), and origin.",
    "stage_2_represent": "Construct directed vector arrows, component triangles, or head-to-tail polygon representations.",
    "stage_3_connect": "Apply governing vector laws: component sum R_x = sum A_x, law of cosines, Galilean relative shift v_{AB} = v_A - v_B, or scalar work product W = F . s.",
    "stage_4_execute_and_check": "Execute closed-form algebra; recover magnitude and compass direction; verify dimensional homogeneity and dual limiting boundary checks."
}

# Add first_move_atlas (exact match)
vec_adapter["first_move_atlas"] = FIRST_MOVE_ATLAS

with open(adapters_path, "w", encoding="utf-8") as f:
    json.dump(all_adapters, f, indent=2, ensure_ascii=False)
print(f"[OK] Updated TopicAdapters.v1.json with blueprint_refs, canonical_reasoning_moves, and first_move_atlas for vectors-and-components.")
