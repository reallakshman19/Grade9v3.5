# Agent Authoring & Validation Instructions: Tile (2, 5) — `QRT-REPRESENT-D2`

**Target Tile:** `tile_2_5`  
**QRT Cell:** `QRT-REPRESENT-D2`  
**Cognitive Demand:** `REPRESENT` (Translating Across Mathematical Representations)  
**Difficulty Band:** `D2` (Standard Olympiad, Score Range $[3, 5]$)  
**Subject Focus:** Coordinate Geometry (Reflection across $y = x$), Functions & Graphs (Piecewise Modulus to Zeros), Statistics (Histogram Frequency Density)

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (2, 5)**, you are NOT testing conceptual definitions (`EXPLAIN`), pure fact retrieval (`RETRIEVE`), mechanical calculation (`APPLY`), or verbal modeling (`MODEL`). You are testing whether the student can **translate mathematical structures faithfully across distinct representational modalities** (e.g., Geometric Reflection $\leftrightarrow$ Coordinate Mapping $(x, y) \mapsto (y, x)$; Graph Geometry $\leftrightarrow$ Piecewise Zeros; Histogram Area $\leftrightarrow$ Frequency Counts) to determine the protected transformed object $W$.

### The Decisive Act:
The student must identify the representation invariant connecting the two mathematical worlds (such as coordinate transposition under reflection, root-splitting of a V-graph, or $\text{Area} = \text{Frequency}$ for density histograms) and execute the representational translation to evaluate $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-REPRESENT-D2`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The representational translation task: e.g. Translating line across geometric reflection axis y = x]",
  "Y": "[The given representation and parameters: e.g. Line 2x - 3y + 6 = 0 and reflection line y = x]",
  "Z": "[The governing invariant mapping rule: (x, y) |-> (y, x) under reflection in y = x]",
  "W": "[The Protected Work: The exact transformed equation or coordinates: e.g. 3x - 2y - 6 = 0]",
  "wrong_idea": "[Primary representational trap: e.g. Confusing reflection in y = x with reflection in axes, or treating bar height as frequency]",
  "replacement_rule": "[Correct translation rule: Substitute x -> y and y -> x yielding 2y - 3x + 6 = 0, rearrange to 3x - 2y - 6 = 0]",
  "visual_job": "[Render clear Cartesian grid or histogram with labeled axes; avoid decorative or unmounted SVGs]",
  "check_job": "[Independent verification: Test invariant intersection point (6, 6) or calculate slope reciprocal m -> 1/m]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the original mathematical representation with all geometric or visual parameters clearly defined.
2. **Options:** 
   - 1 Keyed Option ($W$): The correct translated equation, locus, or count.
   - 3 Distractors: Explicitly engineered from authentic representational traps (e.g. axis reflection sign inversion, slope neglect, taking bar height as frequency).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Reminds the student of the representational bridge principle without applying it to the specific problem parameters.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Provides the intermediate substituted expression or unsimplified product, stopping strictly before evaluated equations or values.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach representation translation **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 reflects $2x - 3y + 6 = 0$ across $y = x$, Core 1A must teach reflection across $y = x$ using **$x + 4y - 8 = 0$** or **$3x + y - 6 = 0$**.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an image point or intermediate relation before full derivation is shown.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's algebraic substitution method.
   - If Core 1A used algebraic coordinate substitution $(x, y) \mapsto (y, x)$, Core 1B must analyze the problem using **vector slope inversion** ($m \mapsto 1/m$ and $y$-intercept $(0, b) \mapsto (b, 0)$).

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical Crux Move** (e.g. reflecting $4x - 5y + 20 = 0$ across $y = x$).
- Must declare question-specific unit navigation: `data-core-unit-id="COORD-REPRESENT-REFL-02"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Extend the representation translation to a compound transformation or negative diagonal reflection $y = -x$ (mapping $(x, y) \mapsto (-y, -x)$).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D2: [3, 5])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 1 (Recognizing transformation/representation mapping rule)
- `representation_translation`: 2 (Multi-directional translation between visual/geometric and symbolic forms)
- `reasoning_chain_length`: 1 (2-step representational pipeline)
- `algebra_computational_load`: 0 (Standard algebraic simplification)
- `trap_exception_sensitivity`: 0 (Non-degenerate representation)
- **Total:** $1 + 2 + 1 + 0 + 0 = 4 \in [3, 5]$.

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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_2_5/test_self_mutations.py` $\implies$ 19/19 tests pass.
