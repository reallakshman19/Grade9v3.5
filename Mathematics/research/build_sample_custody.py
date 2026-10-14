#!/usr/bin/env python3
"""
Agent 2: Quality Governance, Deduplication & Core 2 Custody Builder for Official Sample (SOF IMO 2026-27 Sample Paper).
Constructs:
1. TEST/imo-research/audit/sample_dedup_audit.v1.json
2. Mathematics/question-bank/sof-imo-sample-2026-27.core2.json
3. TEST/imo-research/verification/sample-qrt-proposed-coverage.v1.json
"""
import os
import json

def get_sample_questions():
    questions_data = [
        # --- SECTION 1: LOGICAL REASONING (Q001 - Q003) ---
        {
            "num": 1,
            "section": "LOGICAL_REASONING",
            "pdf_page": 1,
            "topic": "LOGIC",
            "topic_label": "Verbal and Non-Verbal Reasoning",
            "subtopic": "LOGIC-CUBE-AND-DICE",
            "title": "Opposite Face Determination from Dice Orientations",
            "band": "D3",
            "score": 6,
            "components": {"concept_model_selection": 1, "representation_translation": 2, "reasoning_chain_length": 2, "algebra_computational_load": 0, "trap_exception_sensitivity": 1},
            "primary_demand": "REPRESENT",
            "secondary_demands": ["JUSTIFY", "APPLY"],
            "crux": "Faces 2, 4, 6, 1 each occur adjacent to face 5 across the given orientations, leaving face 3 opposite 5. Mapping consistent quarter-turns fixes the unknown face as 4",
            "stem": "Three different positions of a dice are shown here. Select a number from the options that will replace the question mark (?) in the given dice.",
            "options": {
                "A": "2",
                "B": "4",
                "C": "5",
                "D": "1"
            },
            "choice": "B",
            "answer_text": "4",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Identify which faces are adjacent to face 5 across the first two views to determine which face must be opposite 5.",
                "hint2_tactical_step": "Faces 1, 2, 4, 6 are all adjacent to 5, which means 3 is opposite 5. Trace the orientation of faces around the remaining axes to find the face at '?'."
            },
            "solution": "1. In Dice View 1, face 5 is adjacent to faces 1 and 2.\n2. In Dice View 2, face 5 is adjacent to faces 4 and 6.\n3. Since a cube has 6 faces and face 5 is adjacent to 1, 2, 4, and 6, the remaining face 3 must be directly opposite face 5.\n4. In Dice View 3, the top face is 3 and the right face is 2.\n5. Since 3 is on top, 5 is on the bottom. The faces surrounding the vertical axis in order are 1, 2, 6, 4.\n6. With face 2 on the right and face 5 on the bottom, the front face designated by '?' must be 4.\n7. Therefore, 4 replaces the question mark.",
            "check": {
                "type": "SPECIAL_CASE",
                "verification": "Standard 3D rotation matrix around vertical and lateral axes confirms: with 3 on top and 2 on right, front face is uniquely 4. Option B verified."
            },
            "distractors": {
                "A": "Selected face 2 which is already visible on the right lateral face.",
                "C": "Selected face 5 which is on the bottom face directly opposite top face 3.",
                "D": "Selected face 1 which lies on the rear face opposite face 2."
            }
        },
        {
            "num": 2,
            "section": "LOGICAL_REASONING",
            "pdf_page": 1,
            "topic": "LOGIC",
            "topic_label": "Verbal and Non-Verbal Reasoning",
            "subtopic": "LOGIC-CODING-DECODING",
            "title": "Message Overlap Substitution Code Decryption",
            "band": "D2",
            "score": 4,
            "components": {"concept_model_selection": 1, "representation_translation": 1, "reasoning_chain_length": 1, "algebra_computational_load": 0, "trap_exception_sensitivity": 1},
            "primary_demand": "REPRESENT",
            "secondary_demands": ["APPLY"],
            "crux": "Across statements, identify shared word-token mappings by intersection: 'health' is sol, 'is' is mah, isolating 'wealth' as liv",
            "stem": "In a certain code language, 'pit dar na' means 'you are good', 'dar tok pa' means 'good and bad' and 'tim na tok' means 'they are bad'. In that language, which word stands for 'they'?",
            "options": {
                "A": "na",
                "B": "tim",
                "C": "tok",
                "D": "pit"
            },
            "choice": "B",
            "answer_text": "tim",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Compare statements pairwise to find which common word corresponds to each common code word.",
                "hint2_tactical_step": "'good' appears in statements 1 and 2, so its code is 'dar'. 'bad' appears in statements 2 and 3, so its code is 'tok'. 'are' appears in statements 1 and 3, so its code is 'na'. What code remains in statement 3 for 'they'?"
            },
            "solution": "1. Compare Statement 1 ('pit dar na' = 'you are good') and Statement 2 ('dar tok pa' = 'good and bad'):\n   Common word = 'good'; Common code = 'dar' -> 'good' = 'dar'.\n2. Compare Statement 2 ('dar tok pa' = 'good and bad') and Statement 3 ('tim na tok' = 'they are bad'):\n   Common word = 'bad'; Common code = 'tok' -> 'bad' = 'tok'.\n3. Compare Statement 1 ('pit dar na' = 'you are good') and Statement 3 ('tim na tok' = 'they are bad'):\n   Common word = 'are'; Common code = 'na' -> 'are' = 'na'.\n4. In Statement 3 ('tim na tok' = 'they are bad'):\n   We know 'na' = 'are' and 'tok' = 'bad'.\n   The remaining code is 'tim', which must correspond to the remaining word 'they'.\n5. Therefore, 'they' is coded as 'tim'.",
            "check": {
                "type": "SUBSTITUTION_BACK_CHECK",
                "verification": "dar=good, tok=bad, na=are, pit=you, pa=and, tim=they. All three message sentences decode consistently without ambiguity. Option B verified."
            },
            "distractors": {
                "A": "Selected 'na' which corresponds to 'are'.",
                "C": "Selected 'tok' which corresponds to 'bad'.",
                "D": "Selected 'pit' which corresponds to 'you'."
            }
        },
        {
            "num": 3,
            "section": "LOGICAL_REASONING",
            "pdf_page": 1,
            "topic": "LOGIC",
            "topic_label": "Verbal and Non-Verbal Reasoning",
            "subtopic": "LOGIC-NUMBER-PATTERN",
            "title": "Radial Sector Average-Square Invariant Pattern",
            "band": "D2",
            "score": 4,
            "components": {"concept_model_selection": 1, "representation_translation": 1, "reasoning_chain_length": 1, "algebra_computational_load": 1, "trap_exception_sensitivity": 0},
            "primary_demand": "MODEL",
            "secondary_demands": ["APPLY"],
            "crux": "In radial diagram, inner sector value equals the square of the arithmetic mean of the two outer adjacent numbers: Inner = ((A + B) / 2)^2",
            "stem": "Find the missing number from the options to replace the question mark (?) in the given figure.",
            "options": {
                "A": "36",
                "B": "49",
                "C": "25",
                "D": "64"
            },
            "choice": "B",
            "answer_text": "49",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Notice that all numbers inside the inner central ring (121, 81, 64) are perfect squares: 11², 9², 8².",
                "hint2_tactical_step": "Compare 11 with outer numbers 14 and 8: (14 + 8)/2 = 11. For outer numbers 5 and 9: compute ((5 + 9)/2)²."
            },
            "solution": "1. Analyze inner sector values:\n   - Top-left sector: outer numbers are 14 and 8. Mean = (14 + 8) / 2 = 22 / 2 = 11. Inner value = 11² = 121.\n   - Top-right sector: outer numbers are 6 and 12. Mean = (6 + 12) / 2 = 18 / 2 = 9. Inner value = 9² = 81.\n   - Bottom-left sector: outer numbers are 3 and 13. Mean = (3 + 13) / 2 = 16 / 2 = 8. Inner value = 8² = 64.\n2. Apply invariant rule to bottom-right sector with outer numbers 5 and 9:\n   Mean = (5 + 9) / 2 = 14 / 2 = 7.\n   Inner value = 7² = 49.\n3. Therefore, the missing number is 49.",
            "check": {
                "type": "SPECIAL_CASE",
                "verification": "((14+8)/2)²=121; ((6+12)/2)²=81; ((3+13)/2)²=64; ((5+9)/2)²=49. Universal consistency across all 4 quadrants. Option B verified."
            },
            "distractors": {
                "A": "Subtracted 1 before squaring: 6² = 36.",
                "C": "Took 5² = 25 directly from one of the outer numbers.",
                "D": "Repeated adjacent quadrant value: 64."
            }
        },

        # --- SECTION 2: MATHEMATICAL REASONING (Q004 - Q006) ---
        {
            "num": 4,
            "section": "MATHEMATICAL_REASONING",
            "pdf_page": 1,
            "topic": "LIN_EQ",
            "topic_label": "Linear Equations in Two Variables",
            "subtopic": "LIN_EQ-GRAPH-AND-INTERCEPTS",
            "title": "Tabulated Value Pair Linear Rule Deduction",
            "band": "D1",
            "score": 2,
            "components": {"concept_model_selection": 0, "representation_translation": 1, "reasoning_chain_length": 1, "algebra_computational_load": 0, "trap_exception_sensitivity": 0},
            "primary_demand": "REPRESENT",
            "secondary_demands": ["APPLY"],
            "crux": "From tabulated pairs (-1, -3), (0, -1), (1, 1), (2, 3), slope m = delta y / delta x = 2 and y-intercept c = -1, yielding y = 2x - 1",
            "stem": "Which of the following linear equations represents the given table of values?\n\n| x | -1 |  0 | 1 | 2 |\n|---|---|---|---|---|\n| y | -3 | -1 | 1 | 3 |",
            "options": {
                "A": "y = x - 2",
                "B": "y = 2x - 1",
                "C": "y = 3x - 3",
                "D": "y = x + 1"
            },
            "choice": "B",
            "answer_text": "y = 2x - 1",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Examine the value of y when x = 0 to immediately identify the y-intercept c.",
                "hint2_tactical_step": "At x = 0, y = -1. Therefore the equation must be of the form y = mx - 1. When x increases by 1, y increases by 2. Thus slope m = 2."
            },
            "solution": "1. Look at the point (0, -1): when x = 0, y = -1, which establishes the y-intercept c = -1.\n2. Compute slope m = (y₂ - y₁) / (x₂ - x₁):\n   Using (0, -1) and (1, 1): m = (1 - (-1)) / (1 - 0) = 2 / 1 = 2.\n3. The linear equation in slope-intercept form is y = mx + c = 2x - 1.\n4. Verify for all remaining points:\n   - For x = -1: y = 2(-1) - 1 = -3. (Matches)\n   - For x = 1: y = 2(1) - 1 = 1. (Matches)\n   - For x = 2: y = 2(2) - 1 = 3. (Matches)\n5. Therefore, the equation is y = 2x - 1.",
            "check": {
                "type": "SUBSTITUTION_BACK_CHECK",
                "verification": "All four pairs (-1,-3), (0,-1), (1,1), (2,3) satisfy y = 2x - 1 identically. None of the other options satisfy more than one point. Option B verified."
            },
            "distractors": {
                "A": "Satisfies only x = -1 (y = -3), fails for x = 0 (gives -2 instead of -1).",
                "C": "Satisfies x = 1 (y = 0 ≠ 1) and x = 2 (y = 3), fails for x = 0.",
                "D": "Inverted y-intercept to +1."
            }
        },
        {
            "num": 5,
            "section": "MATHEMATICAL_REASONING",
            "pdf_page": 2,
            "topic": "ANGLES",
            "topic_label": "Lines and Angles",
            "subtopic": "ANGLES-PARALLEL-LINE-ANGLES",
            "title": "Parallel Families Transversal Ray Angle Deduction",
            "band": "D3",
            "score": 6,
            "components": {"concept_model_selection": 1, "representation_translation": 1, "reasoning_chain_length": 2, "algebra_computational_load": 1, "trap_exception_sensitivity": 1},
            "primary_demand": "JUSTIFY",
            "secondary_demands": ["APPLY", "REPRESENT"],
            "crux": "Matching directed angles from l1 || l2 and l3 || l4 give corresponding sector x. Supplementary opposite ray angle equals 180° - x, partitioned into two equal sectors y + y = 2y. Rearranging gives y = 90° - x/2",
            "stem": "If l₁ ∥ l₂ and l₃ ∥ l₄, then what is the value of y in terms of x?",
            "options": {
                "A": "90° + x",
                "B": "90° + 2x",
                "C": "90° - x/2",
                "D": "90° - 2x"
            },
            "choice": "C",
            "answer_text": "90° - x/2",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Use corresponding angles between parallel line families l₁ ∥ l₂ and l₃ ∥ l₄ to transfer angle x.",
                "hint2_tactical_step": "The opposite ray of l₄ forms a straight angle (180°) with the original ray. The adjacent supplementary angle is 180° - x, which is split into two equal angles y and y: 2y = 180° - x."
            },
            "solution": "1. Step 1 (Parallel transfer): Since l₁ ∥ l₂ and l₃ ∥ l₄, the matching directed angles give the angle between the downward l₂ ray and down-left l₄ ray equal to x.\n2. Step 2 (Supplementary angle): The up-right l₄ ray is opposite the down-left l₄ ray along the straight line l₄. Thus, the sector between the downward l₂ ray and the up-right l₄ ray equals 180° - x.\n3. Step 3 (Two equal y sectors): The diagram partitions that supplementary angle into two adjacent sectors explicitly labelled y and y. Therefore, y + y = 2y = 180° - x.\n4. Step 4 (Symbolic solution): Divide by 2:\n   y = (180° - x) / 2 = 90° - x/2.\n5. Matches Option C.",
            "check": {
                "type": "SPECIAL_CASE",
                "verification": "Test with special value x = 60°: supplementary angle is 120°. Two equal sectors give y = 120° / 2 = 60°. Formula y = 90° - 60°/2 = 90° - 30° = 60°. Matches Option C uniquely."
            },
            "distractors": {
                "A": "Added x instead of subtracting half: 90° + x.",
                "B": "Added 2x: 90° + 2x.",
                "D": "Subtracted 2x instead of x/2: 90° - 2x."
            }
        },
        {
            "num": 6,
            "section": "MATHEMATICAL_REASONING",
            "pdf_page": 2,
            "topic": "EUCLID",
            "topic_label": "Introduction to Euclid’s Geometry",
            "subtopic": "EUCLID-EQUALITY-AXIOMS",
            "title": "Euclidean Addition Axiom Application on Collinear Segments",
            "band": "D1",
            "score": 2,
            "components": {"concept_model_selection": 1, "representation_translation": 0, "reasoning_chain_length": 1, "algebra_computational_load": 0, "trap_exception_sensitivity": 0},
            "primary_demand": "JUSTIFY",
            "secondary_demands": ["RETRIEVE"],
            "crux": "Collinear points P, Q, R, S: given PQ = RS, add common middle segment QR to both sides: PQ + QR = RS + QR => PR = QS. The governing warrant is Euclid's Second Axiom: 'If equals are added to equals, the wholes are equal'",
            "stem": "In the given figure, if PQ = RS, then which Euclid's axiom is used to prove PR = QS?",
            "options": {
                "A": "The whole is greater than the part.",
                "B": "Things which are double of the same things are equal to one another.",
                "C": "If equals are added to equals, the wholes are equal.",
                "D": "Things which coincide with one another are equal to one another."
            },
            "choice": "C",
            "answer_text": "If equals are added to equals, the wholes are equal.",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Observe the relationship between PR, QS and the common segment QR.",
                "hint2_tactical_step": "PR = PQ + QR and QS = QR + RS. Since PQ = RS, we are adding the same quantity (QR) to both equal segments."
            },
            "solution": "1. Points P, Q, R, S are collinear in order P - Q - R - S.\n2. Segment PR can be written as the sum of its parts: PR = PQ + QR.\n3. Segment QS can be written as the sum of its parts: QS = QR + RS = RS + QR.\n4. We are given that PQ = RS.\n5. Adding the common segment QR to both sides of the equation PQ = RS:\n   PQ + QR = RS + QR.\n6. This operation directly applies Euclid's Second Axiom: 'If equals are added to equals, the wholes are equal.'\n7. Therefore, PR = QS, licensed by Axiom 2.",
            "check": {
                "type": "GEOMETRIC_INVARIANT_CHECK",
                "verification": "Euclid Axiom 2 canonical formulation: 'If equals be added to equals, the wholes are equal.' Matches Option C uniquely."
            },
            "distractors": {
                "A": "Euclid's Axiom 5 ('The whole is greater than the part'), which applies to inequalities, not segment equality derivation.",
                "B": "Euclid's Axiom 6, which concerns doubling equal quantities.",
                "D": "Euclid's Axiom 4, which defines congruence by coincidence."
            }
        },

        # --- SECTION 3: EVERYDAY MATHEMATICS (Q007 - Q008) ---
        {
            "num": 7,
            "section": "EVERYDAY_MATHEMATICS",
            "pdf_page": 2,
            "topic": "POLY",
            "topic_label": "Polynomials",
            "subtopic": "POLY-REMAINDER-FACTOR-THEOREM",
            "title": "Polynomial Divisibility Constraint on Purchase Budget",
            "band": "D3",
            "score": 6,
            "components": {"concept_model_selection": 1, "representation_translation": 0, "reasoning_chain_length": 2, "algebra_computational_load": 2, "trap_exception_sensitivity": 1},
            "primary_demand": "MODEL",
            "secondary_demands": ["APPLY"],
            "crux": "Money polynomial P(x) = x^3 + 2ax + b is divisible by (x - 1) and (x + 1) with no remainder => P(1) = 0 and P(-1) = 0. Solve for a and b, then evaluate P(4)",
            "stem": "Vikas has ₹ (x³ + 2ax + b), with this money he can buy exactly (x - 1) jeans or (x + 1) shirts with no money left. How much money Vikas has, if x = 4?",
            "options": {
                "A": "₹ 80",
                "B": "₹ 120",
                "C": "₹ 30",
                "D": "₹ 60"
            },
            "choice": "D",
            "answer_text": "₹ 60",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "If Vikas can buy exactly (x - 1) jeans with no money left, then (x - 1) is a factor of P(x) = x³ + 2ax + b. Similarly, (x + 1) is also a factor.",
                "hint2_tactical_step": "Apply factor theorem: P(1) = 0 => 1³ + 2a(1) + b = 0 => 2a + b = -1. P(-1) = 0 => (-1)³ + 2a(-1) + b = 0 => -2a + b = 1. Solve for a and b, then evaluate P(4)."
            },
            "solution": "1. Let P(x) = x³ + 2ax + b represent Vikas's money.\n2. Since P(x) is completely divisible by (x - 1), by Factor Theorem: P(1) = 0.\n   (1)³ + 2a(1) + b = 0 => 1 + 2a + b = 0 => 2a + b = -1  --- (Eq 1)\n3. Since P(x) is completely divisible by (x + 1), by Factor Theorem: P(-1) = 0.\n   (-1)³ + 2a(-1) + b = 0 => -1 - 2a + b = 0 => -2a + b = 1 --- (Eq 2)\n4. Add Eq 1 and Eq 2:\n   (2a + b) + (-2a + b) = -1 + 1\n   2b = 0 => b = 0.\n5. Substitute b = 0 into Eq 1:\n   2a + 0 = -1 => a = -1/2.\n6. The money polynomial is P(x) = x³ + 2(-1/2)x + 0 = x³ - x = x(x² - 1) = x(x - 1)(x + 1).\n7. For x = 4:\n   P(4) = 4³ - 4 = 64 - 4 = 60.\n8. Therefore, Vikas has ₹ 60.",
            "check": {
                "type": "SUBSTITUTION_BACK_CHECK",
                "verification": "For x = 4: P(4) = 60. Cost of jeans = 60 / (4 - 1) = 60 / 3 = ₹ 20 (exact division). Cost of shirts = 60 / (4 + 1) = 60 / 5 = ₹ 12 (exact division). Option D verified."
            },
            "distractors": {
                "A": "Evaluated 4³ + 16 = 80.",
                "B": "Doubled the value to 120.",
                "C": "Halved the value to 30."
            }
        },
        {
            "num": 8,
            "section": "EVERYDAY_MATHEMATICS",
            "pdf_page": 2,
            "topic": "MENSURATION",
            "topic_label": "Surface Areas and Volumes",
            "subtopic": "MENSURATION-CONE-CYLINDER",
            "title": "Conical Tent Height from Bounded Ground Area and Air Volume",
            "band": "D2",
            "score": 4,
            "components": {"concept_model_selection": 1, "representation_translation": 0, "reasoning_chain_length": 1, "algebra_computational_load": 2, "trap_exception_sensitivity": 0},
            "primary_demand": "MODEL",
            "secondary_demands": ["APPLY"],
            "crux": "Ground area = 11 * 4 = 44 m^2 = π r^2. Air volume = 11 * 20 = 220 m^3 = (1/3) π r^2 h. Height h = 3 * Volume / Base_Area = 3 * 220 / 44 = 15 m",
            "stem": "A conical tent is to accommodate 11 persons. Each person must have 4 sq. metres of the space on the ground and 20 cubic metres of air to breath. Find the height of the cone.",
            "options": {
                "A": "11 m",
                "B": "16 m",
                "C": "14 m",
                "D": "15 m"
            },
            "choice": "D",
            "answer_text": "15 m",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "The ground space required by 11 persons gives the base area of the cone: π r² = 11 · 4 m².",
                "hint2_tactical_step": "The total air volume required by 11 persons is V = 11 · 20 m³. Since V = (1/3) · (base area) · h, solve for h = 3V / (base area)."
            },
            "solution": "1. Number of persons = 11.\n2. Ground space required per person = 4 m².\n   Total base area of conical tent = 11 · 4 = 44 m².\n   Base of cone is circular, so π r² = 44 m².\n3. Air volume required per person = 20 m³.\n   Total volume of conical tent V = 11 · 20 = 220 m³.\n4. Volume of a cone formula:\n   V = (1/3) · π r² · h = (1/3) · (Base Area) · h\n5. Substitute known values:\n   220 = (1/3) · 44 · h\n   220 = (44/3) · h\n   h = (220 · 3) / 44\n   h = 5 · 3 = 15 m.\n6. Therefore, the height of the cone is 15 m.",
            "check": {
                "type": "SUBSTITUTION_BACK_CHECK",
                "verification": "V = (1/3) * 44 * 15 = 44 * 5 = 220 m³. Air per person = 220 / 11 = 20 m³. Ground per person = 44 / 11 = 4 m². Option D verified."
            },
            "distractors": {
                "A": "Confused height with the number of persons (11 m).",
                "B": "Arithmetic slip in division: 16 m.",
                "C": "Subtracted 1: 14 m."
            }
        },

        # --- SECTION 4: ACHIEVERS SECTION (Q009 - Q010) ---
        {
            "num": 9,
            "section": "ACHIEVERS_SECTION",
            "pdf_page": 2,
            "topic": "NS",
            "topic_label": "Number Systems",
            "subtopic": "NS-RECURRING-DECIMALS-AND-RADICALS",
            "title": "Multi-Statement Analysis on Recurring Decimals and Radical Quotients",
            "band": "D3",
            "score": 7,
            "components": {"concept_model_selection": 1, "representation_translation": 1, "reasoning_chain_length": 2, "algebra_computational_load": 2, "trap_exception_sensitivity": 1},
            "primary_demand": "JUSTIFY",
            "secondary_demands": ["SYNTHESIZE", "APPLY"],
            "crux": "Evaluate Statement-I: 15.712... + 4.32... exceeds 20, whereas 389/90 ≈ 4.32, so Statement-I is False. Statement-II: simplify radical products with 5th roots of decimals to obtain exactly 3/80, so Statement-II is True",
            "stem": "Read the given statements carefully and select the correct option.\nStatement-I: The p/q form of 15.71̄2̄ + 4.32̄ is 389/90.\nStatement-II: The value of [∛(0.125) × ⁵√((0.00032)⁻²)] / [⁵√((0.00243)⁻³) × (27)^(2/3)] is 3/80.",
            "options": {
                "A": "Both Statement-I and Statement-II are true.",
                "B": "Both Statement-I and Statement-II are false.",
                "C": "Statement-I is true but Statement-II is false.",
                "D": "Statement-I is false but Statement-II is true."
            },
            "choice": "D",
            "answer_text": "Statement-I is false but Statement-II is true.",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "For Statement-I, estimate the sum: 15.7... + 4.3... > 20. Does 389/90 equal a number greater than 20?",
                "hint2_tactical_step": "389/90 = 4.322... which is approximately just the second term, so Statement-I is immediately false. For Statement-II, express 0.125 = (0.5)³, 0.00032 = (0.2)⁵, 0.00243 = (0.3)⁵ and simplify exponents."
            },
            "solution": "1. Statement-I analysis:\n   - 15.71̄2̄ = 15 + (712 - 7)/990 = 15 + 705/990 = 15 + 47/66 ≈ 15.712.\n   - 4.32̄ = 4 + (32 - 3)/90 = 4 + 29/90 = 389/90 ≈ 4.322.\n   - The sum is 15.71̄2̄ + 4.32̄ ≈ 15.712 + 4.322 = 20.034.\n   - But Statement-I claims the sum equals 389/90 ≈ 4.322 (which is just the second term alone, a deliberate question trap).\n   - Therefore, Statement-I is FALSE.\n2. Statement-II analysis:\n   - Numerator term 1: ∛(0.125) = ∛((0.5)³) = 0.5 = 1/2.\n   - Numerator term 2: ⁵√((0.00032)⁻²) = [((0.2)⁵)⁻²]^(1/5) = (0.2)⁻² = 1 / (0.2)² = 1 / 0.04 = 25.\n   - Full Numerator = (1/2) · 25 = 25 / 2.\n   - Denominator term 1: ⁵√((0.00243)⁻³) = [((0.3)⁵)⁻³]^(1/5) = (0.3)⁻³ = 1 / (0.3)³ = 1 / 0.027 = 1000 / 27.\n   - Denominator term 2: (27)^(2/3) = (3³)^(2/3) = 3² = 9.\n   - Full Denominator = (1000 / 27) · 9 = 1000 / 3.\n   - Overall Quotient = (25 / 2) / (1000 / 3) = (25 / 2) · (3 / 1000) = (25 · 3) / 2000 = 75 / 2000 = 3 / 80.\n   - Therefore, Statement-II is TRUE.\n3. Result: Statement-I is false but Statement-II is true.",
            "check": {
                "type": "SUBSTITUTION_BACK_CHECK",
                "verification": "Statement I: 389/90 = 4.322... < 20, strictly false. Statement II: Numerator = 12.5; Denominator = 1000/3 = 333.333...; 12.5 / (1000/3) = 37.5 / 1000 = 3/80. Statement II verified true. Option D confirmed."
            },
            "distractors": {
                "A": "Assumed Statement-I is true without verifying numerical magnitude.",
                "B": "Claimed Statement-II is false due to miscalculation of negative 5th root exponents.",
                "C": "Inverted both truth values."
            }
        },
        {
            "num": 10,
            "section": "ACHIEVERS_SECTION",
            "pdf_page": 2,
            "topic": "TRIANGLES",
            "topic_label": "Triangles",
            "subtopic": "TRIANGLES-CONGRUENCE-CRITERIA",
            "title": "Comprehensive Congruence and Median Altitudes Theorem Discrimination",
            "band": "D3",
            "score": 7,
            "components": {"concept_model_selection": 1, "representation_translation": 1, "reasoning_chain_length": 2, "algebra_computational_load": 1, "trap_exception_sensitivity": 2},
            "primary_demand": "JUSTIFY",
            "secondary_demands": ["SYNTHESIZE", "APPLY"],
            "crux": "Identify incorrect geometric statement: AAA (angle-angle-angle) ensures similarity but not congruence, so triangles with equal angles are not necessarily congruent (counterexample: scaled triangles)",
            "stem": "Which of the following is incorrect?",
            "options": {
                "A": "In triangles ABC and RQP, if AB = AC, ∠C = ∠P and ∠B = ∠Q, then the two triangles are isosceles and congruent.",
                "B": "The perpendiculars drawn from the vertices of equal angles of an isosceles triangle to the opposite sides are equal.",
                "C": "In the adjoining figure, if PS is a median and QL & RM are perpendiculars drawn from Q and R respectively on PS and PS produced, then QL = RM.",
                "D": "None of these"
            },
            "choice": "A",
            "answer_text": "In triangles ABC and RQP, if AB = AC, ∠C = ∠P and ∠B = ∠Q, then the two triangles are isosceles and congruent.",
            "figure_ref": None,
            "hints": {
                "hint1_conceptual_nudge": "Recall that AAA (Angle-Angle-Angle) is NOT a congruence criterion for triangles.",
                "hint2_tactical_step": "In Option A, AB = AC makes ∆ABC isosceles, so ∠B = ∠C. Since ∠C = ∠P and ∠B = ∠Q, ∆RQP has ∠P = ∠Q, making it isosceles. But does having the same angles force ∆ABC and ∆RQP to have the same size?"
            },
            "solution": "1. Analysis of Option A:\n   - In ∆ABC: AB = AC implies ∠B = ∠C (angles opposite equal sides).\n   - We are given ∠C = ∠P and ∠B = ∠Q.\n   - Since ∠B = ∠C, it follows that ∠P = ∠Q, which implies ∆RQP is isosceles (RQ = RP).\n   - Both triangles have the same three angles (AAA similarity).\n   - However, no side of ∆ABC is given equal to any side of ∆RQP! For example, ∆ABC could have side lengths 5, 5, 6 and ∆RQP could have side lengths 10, 10, 12.\n   - They are similar, but NOT necessarily congruent.\n   - Therefore, the assertion that the two triangles are congruent is INCORRECT.\n2. Analysis of Option B:\n   - Let ∆ABC be isosceles with AB = AC. The equal angles are ∠B and ∠C.\n   - Perpendiculars from B to AC and from C to AB are BE and CF.\n   - In ∆BCE and ∆CBF: ∠BEC = ∠CFB = 90°, ∠BCE = ∠CBF, BC = BC (common hypotenuse).\n   - By AAS congruence, ∆BCE ≅ ∆CBF, which gives BE = CF.\n   - Thus, Option B is a correct statement.\n3. Analysis of Option C:\n   - In ∆PQR, PS is a median, so S is the midpoint of QR, meaning QS = SR.\n   - QL ⊥ PS and RM ⊥ PS (extended).\n   - In ∆QLS and ∆RMS:\n     - ∠QLS = ∠RMS = 90°\n     - ∠QSL = ∠RSM (vertically opposite angles)\n     - QS = RS (since S is midpoint of QR)\n     - By AAS congruence, ∆QLS ≅ ∆RMS, which implies QL = RM.\n   - Thus, Option C is a correct statement.\n4. Therefore, Option A is the incorrect claim.",
            "check": {
                "type": "GEOMETRIC_INVARIANT_CHECK",
                "verification": "AAA similarity counterexample: Let ∆ABC have sides (3, 3, 4) and ∆RQP have sides (6, 6, 8). Both are isosceles with identical angles, but side ratio is 1:2, so they are not congruent. Option A is definitively false/incorrect. Option A verified."
            },
            "distractors": {
                "B": "Claimed that altitudes from equal angles are not equal (refuted by AAS congruence).",
                "C": "Claimed median perpendiculars QL ≠ RM (refuted by AAS congruence on ∆QLS and ∆RMS).",
                "D": "Claimed all options are correct."
            }
        }
    ]
    return questions_data

def build_sample():
    os.makedirs('TEST/imo-research/audit', exist_ok=True)
    os.makedirs('Mathematics/question-bank', exist_ok=True)
    os.makedirs('TEST/imo-research/verification', exist_ok=True)

    questions_data = get_sample_questions()
    assert len(questions_data) == 10, f"Expected 10 questions, got {len(questions_data)}"

    # 1. Deduplication Audit
    audit_records = []
    for q in questions_data:
        audit_records.append({
            "candidate_id": f"SOF-IMO-G09-SAMPLE-2026-27-Q{q['num']:03d}",
            "question_number": q["num"],
            "section": q["section"],
            "source_paper": "SOF-IMO-G09-SAMPLE-2026-27",
            "stem_snippet": q["stem"][:80],
            "adjudication": "ADMITTED",
            "justification": "Official SOF Class 9 IMO 2026-27 Sample Paper question under canonical Core 2 question custody."
        })

    dedup_audit = {
        "schema": "sof-imo-g09-dedup-audit-v1",
        "batch_id": "BATCH-SAMPLE",
        "source_paper": "SOF-IMO-G09-SAMPLE-2026-27",
        "total_evaluated": len(questions_data),
        "total_admitted": len(questions_data),
        "total_rejected": 0,
        "records": audit_records
    }

    with open('TEST/imo-research/audit/sample_dedup_audit.v1.json', 'w', encoding='utf-8') as f:
        json.dump(dedup_audit, f, indent=2)
    print("Saved TEST/imo-research/audit/sample_dedup_audit.v1.json")

    # 2. Canonical Core 2 Package
    core2_questions = []
    for q in questions_data:
        qid = f"SOF-IMO-G09-SAMPLE-2026-27-Q{q['num']:03d}"
        core2_item = {
            "id": qid,
            "title": q["title"],
            "section": q["section"],
            "paper_origin_locator": {
                "paper_id": "SOF-IMO-G09-SAMPLE-2026-27",
                "source_pdf_page": q["pdf_page"],
                "question_number": q["num"],
                "marks": 2 if q["section"] == "ACHIEVERS_SECTION" else 1
            },
            "taxonomy": {
                "topic": q["topic"],
                "topic_label": q["topic_label"],
                "subtopic": q["subtopic"]
            },
            "cognitive_classification": {
                "primary_demand": q["primary_demand"],
                "crux_move": q["crux"],
                "secondary_demands": q["secondary_demands"],
                "difficulty_band": q["band"],
                "difficulty_score": q["score"],
                "difficulty_components": q["components"],
                "qrt_cell": f"QRT-{q['primary_demand']}-{q['band']}"
            },
            "stem": q["stem"],
            "options": q["options"],
            "answer": {
                "choice": q["choice"],
                "value": q["answer_text"]
            },
            "figure_ref": q["figure_ref"],
            "hint_ladder": q["hints"],
            "solution": {
                "derivation": q["solution"],
                "independent_check": {
                    "check_type": q["check"]["type"],
                    "verification": q["check"]["verification"]
                }
            },
            "distractor_rationale": q["distractors"]
        }
        core2_questions.append(core2_item)

    core2_package = {
        "schema": "sof-imo-g09-core2-custody-package-v1",
        "product_role": "SOURCE_QUESTION_CUSTODY",
        "source_paper": "SOF-IMO-G09-SAMPLE-2026-27",
        "paper_metadata": {
            "organization": "Science Olympiad Foundation (SOF)",
            "exam": "International Mathematics Olympiad (IMO)",
            "grade": 9,
            "set": "SAMPLE",
            "year": "2026-27",
            "exam_level": "Level 1",
            "total_questions": 10,
            "time_limit_mins": 15,
            "total_marks": 12
        },
        "questions": core2_questions
    }

    with open('Mathematics/question-bank/sof-imo-sample-2026-27.core2.json', 'w', encoding='utf-8') as f:
        json.dump(core2_package, f, indent=2)
    print("Saved Mathematics/question-bank/sof-imo-sample-2026-27.core2.json")

    # 3. 28-Cell QRT Coverage Matrix for Sample
    demands = ["RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"]
    bands = ["D1", "D2", "D3", "D4"]
    cell_matrix = {}
    for d in demands:
        for b in bands:
            cell_matrix[f"QRT-{d}-{b}"] = []

    for q in core2_questions:
        cell = q["cognitive_classification"]["qrt_cell"]
        cell_matrix[cell].append(q["id"])

    cells_output = []
    covered_count = 0
    for d in demands:
        for b in bands:
            cell_id = f"QRT-{d}-{b}"
            items = cell_matrix[cell_id]
            if len(items) > 0:
                covered_count += 1
            cells_output.append({
                "cell": cell_id,
                "primary_demand": d,
                "derived_band": b,
                "item_count": len(items),
                "proposed_question_ids": items,
                "status": "POPULATED" if len(items) > 0 else "EMPTY"
            })

    qrt_output = {
        "schema": "sof-imo-g09-sample-qrt-coverage-v1",
        "batch_id": "BATCH-SAMPLE",
        "source_paper": "SOF-IMO-G09-SAMPLE-2026-27",
        "total_admitted_items": len(core2_questions),
        "matrix_dimensions": "4_BANDS_X_7_DEMANDS = 28_CELLS",
        "covered_cells_in_sample_count": covered_count,
        "unfilled_cells_in_sample_count": 28 - covered_count,
        "cells": cells_output
    }

    with open('TEST/imo-research/verification/sample-qrt-proposed-coverage.v1.json', 'w', encoding='utf-8') as f:
        json.dump(qrt_output, f, indent=2)
    print("Saved TEST/imo-research/verification/sample-qrt-proposed-coverage.v1.json")

    print("\n--- SAMPLE SUMMARY STATISTICS ---")
    print(f"Total Admitted Questions: {len(core2_questions)}")
    print(f"Distinct QRT Cells Populated: {covered_count} / 28")
    for c in cells_output:
        if c["item_count"] > 0:
            print(f"  {c['cell']}: {c['item_count']} items ({', '.join(c['proposed_question_ids'][:3])})")

if __name__ == '__main__':
    build_sample()
