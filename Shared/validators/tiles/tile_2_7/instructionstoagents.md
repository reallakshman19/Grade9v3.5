# Agent Authoring & Validation Instructions: Tile (2, 7) — `QRT-JUSTIFY-D2`

**Target Tile:** `tile_2_7`  
**QRT Cell:** `QRT-JUSTIFY-D2`  
**Cognitive Demand:** `JUSTIFY` (Deductive Proof, Counterexample Analysis & Invariant Justification)  
**Difficulty Band:** `D2` (Standard Olympiad, Score Range $[3, 5]$)  
**Subject Focus:** Number Theory (Prime Exponent Parity in Divisibility), Plane Geometry (Generalized Polygon Inequality Bounds), Algebra (AM-GM Inequality Proofs)

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (2, 7)**, you are NOT testing conceptual definitions (`EXPLAIN`), pure fact retrieval (`RETRIEVE`), mechanical arithmetic (`APPLY`), verbal modeling (`MODEL`), or representational translation (`REPRESENT`). You are testing whether the student can **construct a deductive logical proof, establish necessary and sufficient bounding inequalities, or identify precise counterexamples to refute false mathematical conjectures**.

### The Decisive Act:
The student must formulate a sound logical deduction (e.g., establishing that prime valuation parity $v_p(n^2) = 2v_p(n)$ forces $6 \mid n$ when $18 \mid n^2$, or establishing strict polygon inequality bounds $1 < x < 15$), explicitly rejecting intuitive false generalizations (such as assuming $18 \mid n$) to produce the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-JUSTIFY-D2`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The deductive justification task: e.g. Deducing minimal divisor via prime exponent parity]",
  "Y": "[The given hypothesis: e.g. Integer n satisfies 18 divides n^2]",
  "Z": "[The governing deductive theorem: 18 = 2 * 3^2 implies v_2(n^2) >= 2 and v_3(n^2) >= 2, so 6 must divide n]",
  "W": "[The Protected Work: The deduced divisor, interval, or extremum: e.g. 6 / 1 < x < 15 / Minimum is 6, attained at x = 3]",
  "wrong_idea": "[Primary logical fallacy: e.g. False generalization that m divides n^2 implies m divides n directly]",
  "replacement_rule": "[Correct deductive argument: Exponents in n^2 are even; 18 = 2^1 * 3^2 forces n to contain at least 2^1 * 3^1 = 6]",
  "visual_job": "[Render prime factor valuation diagram or geometric bounding schema; avoid unmounted SVGs]",
  "check_job": "[Counterexample verification: For n = 6, n^2 = 36 is divisible by 18, but 6 is not divisible by 18 or 12. Divisor 6 is verified.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the mathematical assertion or hypothesis with all quantifier conditions explicitly stated.
2. **Options:** 
   - 1 Keyed Option ($W$): The correct deduced condition, interval, or divisor.
   - 3 Distractors: Explicitly engineered from authentic logical fallacies (e.g. incomplete bounding conditions, false divisibility deductions).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Activates the fundamental deductive theorem (e.g. prime exponent parity or polygon inequality) without applying it to the specific parameters.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Provides the intermediate inequality or valuation constraints, stopping strictly before evaluating the terminal answer $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach deductive justification **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 analyzes $18 \mid n^2$, Core 1A must demonstrate prime exponent parity using **$20 \mid n^2$** ($20 = 2^2 \times 5^1 \implies 10 \mid n$) or **$45 \mid n^2$** ($45 = 3^2 \times 5^1 \implies 15 \mid n$).
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict a counterexample or intermediate deduction before full proof unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's formal $p$-adic valuation derivation.
   - If Core 1A used algebraic valuation $v_p(n)$, Core 1B must analyze the question using **counterexample elimination** (e.g. testing $n = 6$ to eliminate candidates $18, 12, 9$).

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical justification crux** (e.g. if $n^2$ is divisible by $72 = 2^3 \times 3^2$, deduce the smallest integer that must divide $n$).
- Must declare question-specific unit navigation: `data-core-unit-id="NT-JUSTIFY-DIV-PARITY-02"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the justification to higher prime powers (e.g. $n^3$ divisible by $72$) or to cyclic quadrilaterals with Ptolemy's inequality.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D2: [3, 5])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 1 (Selecting prime factorization parity or polygon inequality)
- `representation_translation`: 0 (Pure number theoretic reasoning)
- `reasoning_chain_length`: 2 (Multi-step deduction: factor $\to$ valuation parity $\to$ minimum necessity)
- `algebra_computational_load`: 0 (Minimal algebraic calculation)
- `trap_exception_sensitivity`: 1 (Logical fallacy avoidance and counterexample sensitivity)
- **Total:** $1 + 0 + 2 + 0 + 1 = 4 \in [3, 5]$.

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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_2_7/test_self_mutations.py` $\implies$ 19/19 tests pass.
