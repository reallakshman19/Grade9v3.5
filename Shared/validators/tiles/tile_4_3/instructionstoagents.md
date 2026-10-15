# Agent Authoring & Validation Instructions: Tile (4, 3) — `QRT-APPLY-D4`

**Target Tile:** `tile_4_3`  
**QRT Cell:** `QRT-APPLY-D4`  
**Cognitive Demand:** `APPLY` (Executing complex multi-stage procedural machinery, algorithmic pipelines, and Diophantine ring calculations)  
**Difficulty Band:** `D4` (National & International Olympiad Elite, Score Range $[9, 10]$)  
**Subject Focus:** Geometry (Descartes' Circle Theorem Mutually Tangent Curvatures), Number Theory (Pell's Equation Fundamental Unit Ring Exponentiation), Combinatorics & Algebra (Bounded-Part Partition Generating Reduction)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (4, 3)**, you are NOT testing elementary formula substitution (`APPLY-D1/D2`) or standard regional Olympiad algorithms (`APPLY-D3`). You are testing whether the student can **execute multi-stage, high-precision national and international Olympiad algorithmic pipelines, resolving non-linear quadratic curvatures, computing periodic continued fraction convergents and ring powers, or tabulating generating series reductions under strict mathematical constraints**.

### The Decisive Act:
The student must map the problem configuration to the appropriate elite procedural framework, execute the multi-phase algebraic or computational steps, resolve branch or sign ambiguities (e.g. inner vs outer Soddy circle, or fundamental vs secondary Pell solution), and calculate the protected work quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-APPLY-D4`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The elite procedural application task: e.g. Evaluating the radius of an externally tangent circle via Descartes' Circle Theorem]",
  "Y": "[The given configuration: e.g. Three mutually externally tangent circles with radii 1, 2, 3]",
  "Z": "[The governing formula: Descartes' curvature relation (sum k)^2 = 2*sum(k^2) with k4 = sum(k1,k2,k3) + 2*sqrt(sum(ki*kj))]",
  "W": "[The Protected Work: The exact evaluated numerical quantity: e.g. 6/23 / 127 / 44]",
  "wrong_idea": "[Primary student misconception: e.g. Selecting the outer circumscribing circle branch, taking the fundamental rather than second solution, or missing a partition case]",
  "replacement_rule": "[Correct procedural execution: Solve the quadratic curvature equation selecting the positive root branch k4 = 11/6 + 2 = 23/6, yielding r4 = 6/23]",
  "visual_job": "[Render Apollonian mutual circle configuration, continued fraction table, or partition grid; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Verify center distances and tangential contact: sqrt((x1-x4)^2 + (y1-y4)^2) = r1 + r4. Evaluated and confirmed.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all high-level geometric radii, Diophantine equations, or partition bounds stated unambiguously.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical quantity.
   - 3 Distractors: Explicitly engineered from authentic procedural errors (e.g. taking the negative square root branch, stopping at the fundamental solution $x_1$, or omitting a boundary term in partition summation).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Introduces the algorithmic technique (e.g. Descartes' curvature formulation, continued fraction expansion, or reduction by largest part).
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Formulates the intermediate relation ($k_4 = k_1+k_2+k_3 \pm 2\sqrt{\sum k_i k_j}$, fundamental unit $(8, 3)$, or formula $\lfloor \frac{K}{2} \rfloor + 1$) without revealing the terminal numerical answer $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the underlying technique **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 evaluates Descartes' theorem for circles of radii $1, 2, 3$, Core 1A must demonstrate the theorem on circles of radii $1, 1, 1$.
   - If Core 2 evaluates Pell's equation $x^2 - 7y^2 = 1$, Core 1A must demonstrate ring exponentiation on $x^2 - 2y^2 = 1$ or $x^2 - 3y^2 = 1$.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an intermediate invariant before the full solution steps unlock.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's direct derivation.
   - If Core 1A used direct algebraic formulas, Core 1B must analyze the problem via matrix powers or Cartesian Apollonian coordinates.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical procedural application crux** (e.g. Descartes' theorem with a line $k=0$, or Pell's equation $x^2 - 5y^2 = 1$).
- Must declare question-specific unit navigation: `data-core-unit-id="GEO-APP-DESCARTES-CIRCLE-04"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the algorithmic technique to an Olympiad competition problem (e.g. Ford circles or higher-degree Diophantine equations).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D4: [9, 10])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (National/International Elite Olympiad algorithmic technique selection)
- `representation_translation`: 2 (Curvature algebra / quadratic ring representations / generating series systems)
- `reasoning_chain_length`: 2 (Multi-stage procedural pipeline execution)
- `algebra_computational_load`: 2 (Substantial radical, Diophantine, or combinatorial calculations)
- `trap_exception_sensitivity`: 1 or 2 (Inner vs outer Soddy branch, fundamental vs secondary unit, boundary terms)
- **Total:** Must be strictly in $\{9, 10\}$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[9, 10]$ and component sum equals `difficulty_score`.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes.
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values or target formulas.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_4_3/test_self_mutations.py` $\implies$ 19/19 tests pass.
- [ ] 12. Tile validator reports hold: `QRT_APPLY_D4_DECISIVE_ACT_REVIEW_REQUIRED`.
