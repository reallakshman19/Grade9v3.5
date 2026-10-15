# Agent Authoring & Validation Instructions: Tile (2, 6) — `QRT-SYNTHESIZE-D2`

**Target Tile:** `tile_2_6`  
**QRT Cell:** `QRT-SYNTHESIZE-D2`  
**Cognitive Demand:** `SYNTHESIZE` (Cross-Topic Integration & Disciplinary Unification)  
**Difficulty Band:** `D2` (Standard Olympiad, Score Range $[3, 5]$)  
**Subject Focus:** Geometry + Polynomial Algebra, Sequences + Number Theory, Coordinate Geometry + Circle Mensuration  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (2, 6)**, you are NOT testing conceptual definitions (`EXPLAIN`), pure fact retrieval (`RETRIEVE`), single-topic algorithmic execution (`APPLY`), verbal modeling (`MODEL`), or representational translation (`REPRESENT`). You are testing whether the student can **synthesize two or more distinct mathematical frameworks into a single cohesive pipeline without intermediate scaffolding or hints**.

### The Decisive Act:
The student must independently establish the cross-topic conceptual bridge (e.g., translating geometric right-triangle constraints into an algebraic quadratic equation, or utilizing symmetric sequence formulations to simplify Diophantine products), resolve the resulting system, discard extraneous algebraic roots using physical/domain constraints, and evaluate the terminal synthesized quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-SYNTHESIZE-D2`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The cross-topic synthesis task: e.g. Unifying right-triangle geometry with quadratic polynomial factoring]",
  "Y": "[The given multi-domain conditions: e.g. Right triangle with legs x, x + 7 and hypotenuse x + 8]",
  "Z": "[The governing cross-topic invariant: a^2 + b^2 = c^2 combined with factoring (x - 5)(x + 3) = 0 and domain filter x > 0]",
  "W": "[The Protected Work: The terminal synthesized quantity: e.g. 30 (area) / 9 (largest AP term) / 9\\pi (circle area)]",
  "wrong_idea": "[Primary synthesis trap: e.g. Stopping at intermediate algebraic root x = 5 without computing area, or keeping negative root x = -3]",
  "replacement_rule": "[Correct synthesis pipeline: Discard x = -3; evaluate legs 5 and 12; compute Area = 0.5 * 5 * 12 = 30]",
  "visual_job": "[Render clear geometric figure or sequence schema with algebraic expressions labeled; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Verify 5^2 + 12^2 = 25 + 144 = 169 = 13^2 = (5+8)^2. Hypotenuse matches. Area = 30 verified.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all parameters specified mathematically across both disciplines.
2. **Options:** 
   - 1 Keyed Option ($W$): The correct terminal synthesized quantity.
   - 3 Distractors: Explicitly engineered from synthesis traps (e.g. omitting the $1/2$ factor in area, stopping at intermediate root $x$, confusing middle term with largest term).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs focus to the primary structural theorem (e.g. Pythagorean theorem or symmetric AP notation) without setting up the full algebra.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Provides the intermediate reduced equation (e.g. $x^2 - 2x - 15 = 0$ or $7(49 - d^2) = 315$), stopping strictly before stating the root or terminal result.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach cross-topic synthesis **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 synthesizes legs $x, x+7$ and hypotenuse $x+8$, Core 1A must demonstrate the technique using **legs $x, x+2$ and hypotenuse $x+4$** ($x = 6 \implies \text{Area} = 24$).
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must identify the key algebraic invariant before full synthesis derivation unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's standard binomial expansion.
   - If Core 1A expanded $(x+7)^2$ directly, Core 1B must analyze the problem using **difference of squares factorization**: $(x+8)^2 - (x+7)^2 = ((x+8)-(x+7))((x+8)+(x+7)) = 1(2x + 15) = x^2$.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical synthesis crux** (e.g. right triangle with legs $x$ and $x + 3$, hypotenuse $x + 6$).
- Must declare question-specific unit navigation: `data-core-unit-id="GEOM-SYNTH-PYTH-QUAD-02"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the cross-topic synthesis to a 3D rectangular box or a circle-parabola intersection.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D2: [3, 5])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 1 (Integrating 2 distinct mathematical concepts)
- `representation_translation`: 1 (Translating geometric/sequence relations to algebra)
- `reasoning_chain_length`: 1 (3-step pipeline: bridge $\to$ solve $\to$ synthesize)
- `algebra_computational_load`: 1 (Quadratic factoring / non-linear solve)
- `trap_exception_sensitivity`: 0 (Domain filter $x > 0$)
- **Total:** $1 + 1 + 1 + 1 + 0 = 4 \in [3, 5]$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[3, 5]$.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes.
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_2_6/test_self_mutations.py` $\implies$ 19/19 tests pass.
