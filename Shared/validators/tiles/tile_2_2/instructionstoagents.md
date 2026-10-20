# Agent Authoring & Validation Instructions: Tile (2, 2) — `QRT-EXPLAIN-D2`

**Target Tile:** `tile_2_2`  
**QRT Cell:** `QRT-EXPLAIN-D2`  
**Cognitive Demand:** `EXPLAIN` (Conceptual Understanding & Invariant Articulation)  
**Difficulty Band:** `D2` (Standard Olympiad, Score Range $[3, 5]$)  
**Subject Focus:** Euclidean Geometry, Coordinate Geometry, Polynomial Invariants  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (2, 2)**, you are NOT testing numerical calculation (`APPLY`) or isolated recall (`RETRIEVE`). You are testing whether the student can **articulate the structural causal mechanism** explaining **WHY** a mathematical invariance holds.

### The Decisive Act:
The student must identify or verbalize the underlying mathematical reason that guarantees truth under variation (e.g. angle transfer via parallel transversals to a straight angle, or AA similarity of slope triangles along a linear graph).

---

## 2. The 8-Slot Cognitive Architecture for `QRT-EXPLAIN-D2`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The invariant relationship: e.g. Triangle interior angle sum = 180 deg / Slope ratio is constant]",
  "Y": "[The geometric/algebraic configuration: e.g. Auxiliary line l parallel to base / Two points on linear graph]",
  "Z": "[The causal mechanism: e.g. Alternate interior angles on a straight line / AA similar slope triangles]",
  "W": "[The Protected Work: Selection/formulation of the exact causal explanation statement]",
  "wrong_idea": "[Primary student misconception: e.g. Assuming special right-isosceles triangle / Confusing slope with point distance]",
  "replacement_rule": "[Corrective principle: Parallel transversals translate angles to straight line / Slope triangles are similar by AA]",
  "visual_job": "[Render clear diagram with auxiliary line or slope steps; avoid decorative or unmounted SVGs]",
  "check_job": "[Verify against straight angle sum 180 deg or ratio equality Δy/Δx]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the geometric or algebraic setup with the auxiliary construction clearly stated.
2. **Options:** 
   - 1 Keyed Option ($W$): Accurately articulates the causal invariant mechanism.
   - 3 Distractors: Explicitly engineered from known student misconceptions (never random values).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Reminds student of the governing principle (e.g. parallel lines cut by transversals) without naming the answer.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Directs focus to the intermediate configuration (e.g. the 3 adjacent angles at apex $A$), stopping strictly before the sum equation.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the underlying principle **WITHOUT using the exact problem parameters or stem text of Core 2**.
   - If Core 2 uses $\triangle ABC$ with line $l \parallel BC$, Core 1A must teach transversal angle transfer on a **generic two-rail parallel line system** ($\alpha = \beta$) or on a **convex polygon**.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The learner must predict a diagnostic property (e.g. straight-angle sum $= 180^\circ$) before the proof derivation is revealed.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's proof path.
   - If Core 1A used an auxiliary parallel line through the apex, Core 1B must reconstruct via the **Exterior Angle Theorem route** ($\angle ACD = \angle A + \angle B$, linear pair $= 180^\circ$).

### 3.4 `Core 2A` (Supported Practice)
- Author a scaffolded practice item sharing the **identical Crux Move** (e.g. consecutive interior angles in a trapezoid).
- Must declare question-specific unit navigation: `data-core-unit-id="GEO-TRIA-INVAR-02"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Perturb the surface topology (e.g. quadrilateral or pentagon triangulation) while preserving the angle-sum invariant, verifying that the student did not merely memorize the triangle card.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D2: [3, 5])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 1 (Auxiliary construction or transversal model)
- `representation_translation`: 1 (Diagram to algebraic sum)
- `reasoning_chain_length`: 1 (2-step deduction)
- `algebra_computational_load`: 0 (Pure explanation, zero arithmetic)
- `trap_exception_sensitivity`: 1 (Near-miss distractors)
- **Total:** $1 + 1 + 1 + 0 + 1 = 4 \in [3, 5]$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[3, 5]$.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes.
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific answer values.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_2_2/test_self_mutations.py` $\implies$ 19/19 tests pass.
