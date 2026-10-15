# Agent Authoring & Validation Instructions: Tile (2, 4) — `QRT-MODEL-D2`

**Target Tile:** `tile_2_4`  
**QRT Cell:** `QRT-MODEL-D2`  
**Cognitive Demand:** `MODEL` (Real-World Invariant Mapping to Mathematical Systems)  
**Difficulty Band:** `D2` (Standard Olympiad, Score Range $[3, 5]$)  
**Subject Focus:** Algebra (Linear Systems in 2 Variables, Uniform Border/Perimeter Constraints, Mixture/Concentration Invariants)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (2, 4)**, you are NOT testing conceptual definitions (`EXPLAIN`), pure fact retrieval (`RETRIEVE`), or mechanical plug-and-chug arithmetic (`APPLY`). You are testing whether the student can **translate verbal real-world constraints into an explicit mathematical equation or system of equations** and solve for the primary model variable $W$.

### The Decisive Act:
The student must identify the underlying physical/economic/geometric conservation laws, assign unambiguous variable bindings (e.g. $x$ tickets at \$2, $y$ tickets at \$5), formulate the simultaneous system ($x + y = 50$, $2x + 5y = 160$), and extract the protected terminal quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-MODEL-D2`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The modeling task: e.g. Formulate linear system for two ticket tiers / Set up perimeter and inner area relation / Conservation of pure solute]",
  "Y": "[The given verbal & quantitative conditions: e.g. 50 tickets total, $160 total revenue, ticket prices $2 and $5]",
  "Z": "[The governing invariant law: Total tickets = x + y = 50, Total revenue = 2x + 5y = 160]",
  "W": "[The Protected Work: Primary model variable or system solution: e.g. 30 (five-dollar tickets) / 22 m length / 12 L]",
  "wrong_idea": "[Primary modeling trap: e.g. Inverting coefficients 5x + 2y = 160, or subtracting border twice instead of from both dimensions]",
  "replacement_rule": "[Correct formulation: Bind x=qty $2, y=qty $5; conservation of count x+y=50; conservation of value 2x+5y=160]",
  "visual_job": "[Render structured constraint table or schematic diagram showing system components; avoid decorative SVGs]",
  "check_job": "[Independent verification: Back-substitute into both equations: 20($2) + 30($5) = $40 + $150 = $190 != $160 -> catches inversion]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the real-world scenario with all verbal constraints clearly stated.
2. **Options:** 
   - 1 Keyed Option ($W$): The correct model quantity or system solution.
   - 3 Distractors: Explicitly engineered from modeling formulation errors (e.g. inverted coefficients, 1D border subtraction $(L-2)(W-2)$, arithmetic slip).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs the student to identify the two independent conservation laws (e.g. item count and total monetary value).
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: States the explicit system $x + y = 50$ and $2x + 5y = 160$ and indicates eliminating $x$, stopping strictly before evaluating $y = 30$ or disclosing the keyed choice.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach modeling of linear systems **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 uses $50$ tickets and $\$160$ revenue with $\$2$ and $\$5$ tickets, Core 1A must demonstrate the modeling technique using **coins ($40$ coins, $\$1.40$ total with $\$0.02$ and $\$0.05$ coins)** or **livestock legs ($35$ heads, $94$ legs)**.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must identify the correct equation formulation before the full solution is displayed.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's algebraic elimination approach.
   - If Core 1A solved the model by substitution/elimination, Core 1B must analyze the problem using the **Extreme Case / All-Item Hypothesis** (e.g. "If all 50 tickets were \$2, total would be \$100. The deficit of \$60 arises from \$3 per \$5-ticket $\implies 60/3 = 20$ or $30$").

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical Crux Move** (e.g. two-variable system modeling student and adult admission fees).
- Must declare question-specific unit navigation: `data-core-unit-id="ALG-MODEL-SYS-02"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the modeling demand to 3 variables or an inequality constraint (e.g. linear programming bounding condition or a mixture problem with 3 components).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D2: [3, 5])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 1 (Formulating 2-variable system from word description)
- `representation_translation`: 1 (Word statements to algebraic equations)
- `reasoning_chain_length`: 1 (Formulate $\to$ Solve intermediate)
- `algebra_computational_load`: 1 (2-variable linear elimination)
- `trap_exception_sensitivity`: 0 (Standard non-degenerate system)
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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_2_4/test_self_mutations.py` $\implies$ 19/19 tests pass.
