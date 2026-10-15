# Agent Authoring & Validation Instructions: Tile (3, 1) — `QRT-RETRIEVE-D3`

**Target Tile:** `tile_3_1`  
**QRT Cell:** `QRT-RETRIEVE-D3`  
**Cognitive Demand:** `RETRIEVE` (Recalling & Instantiating Advanced Competition Theorems & Invariants)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Geometry (Brahmagupta's Cyclic Quadrilateral Formula), Number Theory (Euler's Totient Theorem), Algebra (Cubic Vieta Formulas)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 1)**, you are NOT testing elementary fact retrieval (`RETRIEVE-D1`), standard school formulas (`RETRIEVE-D2`), or multi-step procedural drills (`APPLY`). You are testing whether the student can **retrieve and instantiate specialized Olympiad mathematical theorems, advanced structural invariants, and competition identities directly from deep memory without intermediate prompts or formula sheets**.

### The Decisive Act:
The student must identify that the problem requires an advanced competition theorem (e.g., Brahmagupta's formula for cyclic quadrilaterals, Euler's totient modular reduction, or cubic Vieta root ratios), retrieve its exact symbolic formulation from memory, instantiate the given parameters, and evaluate the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-RETRIEVE-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The advanced theorem retrieval task: e.g. Retrieval of Brahmagupta's cyclic quadrilateral area theorem]",
  "Y": "[The given configuration: e.g. Cyclic quadrilateral with side lengths 2, 3, 4, 7]",
  "Z": "[The governing competition theorem: Area = sqrt((s-a)(s-b)(s-c)(s-d)) where s = (a+b+c+d)/2]",
  "W": "[The Protected Work: The exact evaluated radical, remainder, or quotient: e.g. 2\\sqrt{30} / 49 / 4/7]",
  "wrong_idea": "[Primary student misconception: e.g. Attempting to use triangle Heron's formula or assuming angles must be known]",
  "replacement_rule": "[Correct theorem instantiation: Calculate semi-perimeter s = 8, evaluate product sqrt(6*5*4*1) = sqrt(120) = 2*sqrt(30)]",
  "visual_job": "[Render inscribed cyclic quadrilateral with side lengths labeled; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Verify via Bretschneider's formula with supplementary opposite angles: Area = 2*sqrt(30) confirmed.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all geometric or algebraic conditions stated clearly.
2. **Options:** 
   - 1 Keyed Option ($W$): The correct simplified terminal quantity.
   - 3 Distractors: Explicitly engineered from authentic theorem misapplications (e.g. unsimplified radicals, factoring errors, sign inversions in Vieta's relations).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Reminds the student of the advanced competition theorem by name without providing its algebraic formula.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Provides the semi-perimeter and unsimplified radical expression (e.g. $\sqrt{120}$ or $82 = 2 \times 40 + 2$), stopping strictly before simplifying to $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the advanced competition theorem **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 evaluates cyclic quadrilateral sides $2, 3, 4, 7$, Core 1A must demonstrate Brahmagupta's formula using **sides $1, 2, 3, 4$** ($s = 5 \implies \text{Area} = 2\sqrt{6}$).
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an intermediate parameter (such as semi-perimeter $s$ or totient $\phi(m)$) before the derivation unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's direct formula substitution.
   - If Core 1A substituted into Brahmagupta's formula directly, Core 1B must reconstruct the area via **diagonal chord splitting & the Law of Cosines**: $BD^2 = a^2 + b^2 - 2ab\cos B = c^2 + d^2 + 2cd\cos B$.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical theorem retrieval crux** (e.g. cyclic quadrilateral with sides $2, 4, 5, 7 \implies \text{Area} = 2\sqrt{70}$).
- Must declare question-specific unit navigation: `data-core-unit-id="GEOM-RETRIEVE-BRAHMAGUPTA-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the theorem to bicentric quadrilaterals (both cyclic and tangential) where $a+c = b+d \implies \text{Area} = \sqrt{abcd}$.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Advanced competition theorem retrieval: Brahmagupta / Euler Totient / Cubic Vieta)
- `representation_translation`: 1 (Cyclic geometry / modular power representation)
- `reasoning_chain_length`: 1 (Multi-step calculation following theorem retrieval)
- `algebra_computational_load`: 2 (Radical factoring / modular arithmetic)
- `trap_exception_sensitivity`: 0 (Standard cyclic quadrilateral condition)
- **Total:** $2 + 1 + 1 + 2 + 0 = 6 \in [6, 8]$.

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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_1/test_self_mutations.py` $\implies$ 19/19 tests pass.
