# Agent Authoring & Validation Instructions: Tile (2, 3) — `QRT-APPLY-D2`

**Target Tile:** `tile_2_3`  
**QRT Cell:** `QRT-APPLY-D2`  
**Cognitive Demand:** `APPLY` (Multi-Step Procedural Execution & Fluency)  
**Difficulty Band:** `D2` (Standard Olympiad, Score Range $[3, 5]$)  
**Subject Focus:** Mensuration (Heron's Formula), Coordinate Geometry (Midpoint & Distance Pipelines), Radical Simplification  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (2, 3)**, you are NOT testing conceptual explanations (`EXPLAIN`) or single-step fact recall (`RETRIEVE`). You are testing whether the student can **execute a multi-step standard algorithmic pipeline** to evaluate an exact numerical or symbolic quantity $W$ without procedural guidance.

### The Decisive Act:
The student must execute the sequential calculation steps (e.g. semi-perimeter calculation $\to$ side differences $\to$ prime factorization under radical) to produce the exact terminal result $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-APPLY-D2`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The procedural calculation: e.g. Triangle area via Heron's formula / Circle diameter to radius and center]",
  "Y": "[The given numerical parameters: e.g. Triangle sides 13, 14, 15 / Endpoints (-3, 2) and (5, -4)]",
  "Z": "[The governing algorithmic procedure: e.g. Evaluate sqrt(s(s-a)(s-b)(s-c)) via prime factors]",
  "W": "[The Protected Work: The exact numerical or algebraic terminal evaluated result: e.g. 84 / Center (1, -1), Radius 5]",
  "wrong_idea": "[Primary student calculation trap: e.g. Treating side as altitude (0.5*14*13=91) / Forgetting to divide diameter by 2]",
  "replacement_rule": "[Corrective algorithmic step: Calculate semi-perimeter s=21, evaluate differences, extract root via prime factors]",
  "visual_job": "[Render clear diagram with given dimensions labeled; avoid decorative or unmounted SVGs]",
  "check_job": "[Independent verification: verify altitude h = 84 / 7 = 12 via Pythagorean decomposition 5^2 + 12^2 = 13^2 and 9^2 + 12^2 = 15^2]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the numerical problem with all required parameters explicitly given.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical/algebraic result.
   - 3 Distractors: Explicitly engineered from procedural calculation slips (e.g. formula misapplication, missing square root, sign slip).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Reminds student of the governing formula (e.g. Heron's formula $\text{Area} = \sqrt{s(s-a)(s-b)(s-c)}$) without calculating values.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Directs focus to the intermediate state (e.g. semi-perimeter $s = 21$ and side differences), stopping strictly before extracting the root or revealing $84$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the algorithmic pipeline **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 uses triangle sides $13, 14, 15$, Core 1A must teach Heron's formula using sides **$5, 6, 7$** ($s = 9$, $\text{Area} = 6\sqrt{6}$) or an **isosceles triangle**.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The learner must predict an intermediate calculation (e.g. semi-perimeter of a $3, 4, 5$ triangle $s = 6$) before the worked derivation is revealed.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's calculation path.
   - If Core 1A used standard Heron's formula, Core 1B must reconstruct the area via **Pythagorean Altitude Decomposition** ($a^2 - x^2 = c^2 - (b - x)^2 \implies h = 12 \implies \text{Area} = \frac{1}{2}bh = 84$).

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical Crux Move** (e.g. triangle with sides $9, 10, 17 \implies s = 18 \implies \text{Area} = 36$).
- Must declare question-specific unit navigation: `data-core-unit-id="MENS-HERON-PROC-02"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Extend the procedural pipeline to a composite shape (e.g. quadrilateral field split by a known diagonal into two triangles), requiring two applications of Heron's formula.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D2: [3, 5])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 1 (Heron's formula selection over base-height formula)
- `representation_translation`: 0 (Pure numerical calculation)
- `reasoning_chain_length`: 1 (2-step procedural pipeline)
- `algebra_computational_load`: 2 (Multi-digit radical factoring: $\sqrt{7056} = 84$)
- `trap_exception_sensitivity`: 0 (Standard valid triangle)
- **Total:** $1 + 0 + 1 + 2 + 0 = 4 \in [3, 5]$.

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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_2_3/test_self_mutations.py` $\implies$ 19/19 tests pass.
