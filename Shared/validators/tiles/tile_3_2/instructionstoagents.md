# Agent Authoring & Validation Instructions: Tile (3, 2) — `QRT-EXPLAIN-D3`

**Target Tile:** `tile_3_2`  
**QRT Cell:** `QRT-EXPLAIN-D3`  
**Cognitive Demand:** `EXPLAIN` (Deep Structural Mechanisms, Invariant Preservation & Theoretical Justifications)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Geometry (Power of a Point Invariant), Number Theory (Wilson's Theorem Inverses), Combinatorics (Stars and Bars Bijective Partitioning)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 2)**, you are NOT testing elementary formula recall (`RETRIEVE`), mechanical calculation (`APPLY`), verbal modeling (`MODEL`), or cross-topic synthesis (`SYNTHESIZE`). You are testing whether the student can **explain the foundational structural mechanisms, invariant preserving transformations, and theoretical justifications behind advanced competition theorems**.

### The Decisive Act:
The student must identify and articulate the exact structural bridge (e.g., cyclic quadrilateral similarity $\triangle PAC \sim \triangle PDB$, field multiplicative inverse pairing leaving self-inverses $1$ and $-1$, or bijective divider placement among $n + k - 1$ slots) that makes the advanced theorem hold universally.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-EXPLAIN-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The theoretical explanation task: e.g. Structural explanation of Power of a Point theorem via cyclic similar triangles]",
  "Y": "[The given configuration: e.g. Two secants from external point P intersecting circle at A, B and C, D]",
  "Z": "[The governing invariant mechanism: Cyclic inscribed angle subtension angle PAC = angle PDB combined with shared angle P forces similarity PAC ~ PDB]",
  "W": "[The Protected Work: The terminal structural explanation: e.g. Similar triangles PAC ~ PDB sharing angle P with angle PAC = angle PDB]",
  "wrong_idea": "[Primary student misconception: e.g. Claiming collinear segments form congruent triangles or assuming perpendicularity]",
  "replacement_rule": "[Correct structural rationale: Opposite angles in cyclic quadrilateral sum to 180 deg, so exterior angle equals opposite interior angle; AA similarity yields PA/PD = PC/PB]",
  "visual_job": "[Render circle with secants, highlighting the pair of similar triangles PAC and PDB; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Test tangent limit case where C and D coincide at T, giving PA * PB = PT^2. Continuity verifies mechanism.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the theorem or configuration clearly with all geometric or algebraic conditions stated.
2. **Options:** 
   - 1 Keyed Option ($W$): The correct, rigorous structural explanation.
   - 3 Distractors: Explicitly engineered from authentic conceptual traps (e.g. collinear false congruences, additive vs. multiplicative confusion).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs attention to the underlying perspective (e.g. similar triangles or modular grouping) without revealing the specific similarity statement or pairing.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: States the angle equalities or self-inverse condition, stopping strictly before revealing the final explanatory synthesis.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the structural mechanism **WITHOUT using the exact configuration or numbers of Core 2**.
   - If Core 2 explains Power of a Point for external secants, Core 1A must teach Power of a Point for **intersecting chords inside the circle** ($\triangle PAC \sim \triangle PDB$ via vertical angles and subtended chords).
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must identify a key invariant parameter before derivation unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's angle-based similarity proof.
   - If Core 1A used similar triangles, Core 1B must analyze the problem using **distance to the circle center**: $PA \cdot PB = (d - r)(d + r) = d^2 - r^2$.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical structural explanation crux** (e.g. tangent-secant theorem $PT^2 = PA \cdot PB$ via similarity $\triangle PTA \sim \triangle PBT$).
- Must declare question-specific unit navigation: `data-core-unit-id="GEOM-EXPLAIN-POWER-POINT-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the explanatory demand to Radical Axes of two circles, explaining why the locus of points with equal powers forms a straight line perpendicular to the line of centers.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Advanced competition theorem mechanism isolation)
- `representation_translation`: 1 (Geometric angle relations $\leftrightarrow$ triangle similarity)
- `reasoning_chain_length`: 2 (Multi-step structural rationale chain)
- `algebra_computational_load`: 0 (Pure qualitative/structural reasoning)
- `trap_exception_sensitivity`: 1 (Identifying false collinear or degenerate pairings)
- **Total:** $2 + 1 + 2 + 0 + 1 = 6 \in [6, 8]$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[6, 8]$.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes.
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_2/test_self_mutations.py` $\implies$ 19/19 tests pass.
