# Agent Authoring & Validation Instructions: Tile (3, 4) — `QRT-MODEL-D3`

**Target Tile:** `tile_3_4`  
**QRT Cell:** `QRT-MODEL-D3`  
**Cognitive Demand:** `MODEL` (Translating Complex Verbal, Physical, and Computational Systems into Formal Mathematical Structures)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Combinatorics (Binary Sequence Recurrence), Applied Algebra (Distributed Rate Modeling with Bottleneck Degradation), Plane Geometry & Optics (Heron's Reflection Principle)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 4)**, you are NOT testing elementary formula recall (`RETRIEVE`), structural mechanism explanation (`EXPLAIN`), mechanical calculation (`APPLY`), visual translation (`REPRESENT`), or cross-topic synthesis (`SYNTHESIZE`). You are testing whether the student can **translate complex verbal, physical, or computational scenarios into formal mathematical equations or recurrence relations under non-trivial boundary and interaction constraints**.

### The Decisive Act:
The student must formulate the formal mathematical governing equation (e.g. partition sequence endings into disjoint terminal states to induce a recurrence relation, apply a contention penalty to combined throughput, or reflect coordinates across a boundary to model specular path minimization) before solving for the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-MODEL-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The modeling task: e.g. Formulating a coupled recurrence relation from binary transmission constraints]",
  "Y": "[The given scenario: e.g. Binary sequences of length n with no consecutive zeros (00), a1 = 2, a2 = 3]",
  "Z": "[The governing modeling structure: Terminal partition: sequences ending in 1 contribute a_{n-1}, sequences ending in 10 contribute a_{n-2}; recurrence a_n = a_{n-1} + a_{n-2}]",
  "W": "[The Protected Work: The terminal evaluated quantity: e.g. 55]",
  "wrong_idea": "[Primary student modeling misconception: e.g. Applying unconstrained binary powers 2^8 or off-by-one Fibonacci index slip evaluating a7 = 34]",
  "replacement_rule": "[Correct modeling rule: Establish recurrence a_n = a_{n-1} + a_{n-2} with base cases a1 = 2, a2 = 3; step forward iteratively to a8 = 55]",
  "visual_job": "[Render state transition tree showing valid branch endings 1 and 10; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Manually enumerate valid sequences for n = 3 (5 sequences) and n = 4 (8 sequences), confirming a_n = a_{n-1} + a_{n-2}.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Provide the full realistic/computational/physical context with constraints explicitly defined.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical answer or radical coordinate.
   - 3 Distractors: Explicitly engineered from authentic modeling errors (e.g. omitting contention loss, off-by-one recurrence index, inverted geometric ratios).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs attention to the modeling perspective (e.g. terminal state partitioning, contention factor, or boundary reflection) without providing the equation.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: States the governing mathematical equation or recurrence relation, stopping strictly before solving for $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the modeling technique **WITHOUT using the exact scenario, numerical parameters, or answer of Core 2**.
   - If Core 2 models binary sequences without $00$, Core 1A must model ternary sequences without $00$.
   - If Core 2 has answer $W = 18$, the number $18$ must NOT appear anywhere in Core 1A text.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's exact formulation path.
   - For example, if Core 1A uses scalar recurrences, Core 1B guides via state-transition matrix formulation or complementary counting.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical mathematical modeling crux** under modified numerical parameters (e.g. distributed nodes with rates $r$ and $r + 6$, $25\%$ bottleneck penalty, $600$ GB in $20$ minutes).
- Must declare question-specific unit navigation: `data-core-unit-id="ALG-MODEL-DISTRIBUTED-RATE-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the modeling demand to a higher-dimensional network (e.g. three interconnected computing nodes with pairwise link contentions).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Selection of governing recurrence, interaction discount, or specular reflection model)
- `representation_translation`: 2 (Translating verbal/physical constraints into mathematical formulation)
- `reasoning_chain_length`: 1 or 2 (Setting up equation and subsequent multi-step deduction)
- `algebra_computational_load`: 1 (Solving linear/recurrence equations)
- `trap_exception_sensitivity`: 0 or 1 (Managing boundary indexing or contention discounts)
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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_4/test_self_mutations.py` $\implies$ 19/19 tests pass.
