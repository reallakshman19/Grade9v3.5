# Agent Authoring & Validation Instructions: Tile (3, 5) — `QRT-REPRESENT-D3`

**Target Tile:** `tile_3_5`  
**QRT Cell:** `QRT-REPRESENT-D3`  
**Cognitive Demand:** `REPRESENT` (Advanced Bi-Directional Mathematical Representations: Translating Across Symbolic, Geometric, Complex/Vector, and Functional Forms)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Complex Geometry & Coordinate Loci, Combinatorics & Plane Geometry (Roots of Unity), Algebra & Trigonometric Substitution  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 5)**, you are NOT testing elementary formula recall (`RETRIEVE`), structural mechanism explanation (`EXPLAIN`), mechanical calculation (`APPLY`), real-world verbal modeling (`MODEL`), or cross-topic synthesis (`SYNTHESIZE`). You are testing whether the student can **translate mathematical objects across distinct representations (complex quotients $\leftrightarrow$ orthogonal geometric vectors $\leftrightarrow$ Thales' circle; polygon chords $\leftrightarrow$ cyclotomic polynomial roots of unity; rational polynomial fractions $\leftrightarrow$ trigonometric triple-angle identities) to expose underlying invariants and evaluate the protected scalar $W$**.

### The Decisive Act:
The student must identify and execute the representational isomorphism that converts an intractable symbolic or geometric problem into a tractable dual formulation before solving for the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-REPRESENT-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The representational translation task: e.g. Translating a complex fraction with vanishing real part into an orthogonal vector circular locus]",
  "Y": "[The given configuration: e.g. Condition Re((z - 3)/(z + 4i)) = 0 for z in C \\ {-4i}]",
  "Z": "[The governing representational invariant: (z - 3) perp (z - (-4i)) implies Thales' circle with diameter segment between (3, 0) and (0, -4); diameter d = 5 -> radius R = 5/2]",
  "W": "[The Protected Work: The terminal evaluated quantity: e.g. \\frac{5}{2}]",
  "wrong_idea": "[Primary student representational misconception: e.g. Confusing diameter length 5 with radius R, reporting R = 5]",
  "replacement_rule": "[Correct representational rule: The segment connecting (3, 0) and (0, -4) is the circle diameter of length 5; radius is half the diameter: R = 5/2]",
  "visual_job": "[Render Argand plane diagram showing diameter endpoints (3, 0) and (0, -4) subtending right angle to z; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Let z = x + iy; expanding real part yields x^2 - 3x + y^2 + 4y = 0; completing squares gives (x - 3/2)^2 + (y + 2)^2 = (5/2)^2. Radius R = 5/2 confirmed.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem in its initial mathematical representation (symbolic, geometric, or complex).
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical answer or radical form.
   - 3 Distractors: Explicitly engineered from authentic representational misconceptions (e.g. diameter vs. radius, evaluating at wrong root branch, incomplete radical rationalization).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs attention to the dual representation (e.g. geometric orthogonality, roots-of-unity, or trigonometric substitution) without carrying out calculations.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: States the transformed intermediate relation (e.g. diameter endpoints, cyclotomic polynomial factor form, or $\tan 3\theta = 1$), stopping strictly before the final evaluation of $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the representational technique **WITHOUT using the exact parameters, numerical values, or answer of Core 2**.
   - If Core 2 represents $\text{Re}\left(\frac{z - 3}{z + 4i}\right) = 0$, Core 1A must demonstrate on $\text{Re}\left(\frac{z - 1}{z + 1}\right) = 0$.
   - If Core 2 has answer $W = 7$, the digit `7` must NOT appear as a word or answer in Core 1A text.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's exact verification path.
   - For example, if Core 1A uses geometric vector orthogonality, Core 1B verifies via algebraic Cartesian expansion.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical representational crux** under modified parameters (e.g. circular locus with diameter endpoints $(6, 0)$ and $(0, -8)$ yielding $R = 5$).
- Must declare question-specific unit navigation: `data-core-unit-id="COMP-REP-THALES-CIRCLE-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the representational demand to Apollonius circles ($|z - z_1| / |z - z_2| = k \ne 1$).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Selection of advanced representational isomorphism)
- `representation_translation`: 2 (Bi-directional translation across complex/geometric/trigonometric forms)
- `reasoning_chain_length`: 1 or 2 (Multi-step representation deduction)
- `algebra_computational_load`: 1 (Distance formula / polynomial evaluation / radical arithmetic)
- `trap_exception_sensitivity`: 0 or 1 (Diameter vs radius / branch root selection)
- **Total:** Sum must be strictly $\in [6, 8]$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[6, 8]$.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes.
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values or answer $W$.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_5/test_self_mutations.py` $\implies$ 19/19 tests pass.
