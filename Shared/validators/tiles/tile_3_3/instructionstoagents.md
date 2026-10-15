# Agent Authoring & Validation Instructions: Tile (3, 3) — `QRT-APPLY-D3`

**Target Tile:** `tile_3_3`  
**QRT Cell:** `QRT-APPLY-D3`  
**Cognitive Demand:** `APPLY` (Multi-Stage Advanced Algorithmic Execution & Operational Precision)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Number Theory (Extended Euclidean Inverses), Plane Geometry (Stewart's Theorem Cevians), Algebra (De Moivre Polar Complex Powers)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 3)**, you are NOT testing elementary formula recall (`RETRIEVE`), structural mechanism explanation (`EXPLAIN`), real-world verbal modeling (`MODEL`), or cross-topic synthesis (`SYNTHESIZE`). You are testing whether the student can **execute multi-stage advanced mathematical algorithms requiring rigorous operational precision across cascading intermediate states to evaluate the protected quantity $W$**.

### The Decisive Act:
The student must execute the complete multi-step algorithm (e.g. forward Euclidean division with backward Bézout back-substitution, Stewart's cevian segment balance arithmetic, or complex polar conversion with De Moivre trigonometric powers) without intermediate calculation prompting, sign errors, or premature rounding.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-APPLY-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The computational algorithm task: e.g. Executing Extended Euclidean Algorithm for modular inversion]",
  "Y": "[The given numerical configuration: e.g. Linear congruence 37x = 1 (mod 100)]",
  "Z": "[The governing algorithmic procedure: Forward Euclidean divisions followed by backward substitution expressing 1 = 100u + 37v]",
  "W": "[The Protected Work: The terminal evaluated scalar: e.g. 73]",
  "wrong_idea": "[Primary student calculation slip: e.g. Stopping at negative Bézout coefficient -29 or arithmetic slip during back-substitution]",
  "replacement_rule": "[Correct operational rule: Back-substitute division tableau to find 37(-29) = 1 (mod 100); add 100 to obtain unique positive residue x = 73]",
  "visual_job": "[Render Euclidean division tableau showing step-by-step quotients and remainders; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Direct multiplication check: 37 * 73 = 2701 = 27 * 100 + 1 = 1 (mod 100). Verified.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Provide all parameters and explicit equations required to initiate the computation.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical value or radical form.
   - 3 Distractors: Explicitly engineered from authentic intermediate calculation slips (e.g. sign slips in back-substitution, omitting $mn$ in Stewart's formula, or miscalculating $\cos n\theta$).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs attention to the governing theorem or algorithm (e.g. Bézout identity, Stewart's identity, polar conversion) without performing calculations.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Computes the first intermediate stage (e.g. forward division tableau, left-side sum $b^2 m + c^2 n$, or polar quotient $r e^{i\theta}$), stopping strictly before the final evaluation of $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the algorithmic pipeline **WITHOUT using the exact numerical parameters of Core 2**.
   - If Core 2 evaluates $37x \equiv 1 \pmod{100}$, Core 1A must demonstrate the algorithm on a different congruence, e.g. $29x \equiv 1 \pmod{100}$.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must complete an intermediate prediction prompt before full scaffolding unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's exact procedural path.
   - For example, if Core 1A used standard Euclidean division tableau, Core 1B prompts the calculation via **Euler's Totient exponentiation** ($x \equiv 37^{\phi(100)-1} \pmod{100}$) or matrix reduction.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical procedural crux** with different numbers (e.g. solve $43x \equiv 1 \pmod{100} \implies x = 67$).
- Must declare question-specific unit navigation: `data-core-unit-id="NT-APPLY-EXT-EUCLID-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the algorithmic execution to a broader Olympiad context (e.g. solving a system of linear congruences using Chinese Remainder Theorem with Extended Euclidean inverses).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Selection of advanced multi-stage algorithmic procedure)
- `representation_translation`: 0 or 1 (Polar translation or metric segment assignment)
- `reasoning_chain_length`: 2 (4+ step cascading intermediate states)
- `algebra_computational_load`: 2 (Heavy multi-digit arithmetic or modular back-substitution)
- `trap_exception_sensitivity`: 0 or 1 (Sign reduction, radical simplification, quadrant management)
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
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_3/test_self_mutations.py` $\implies$ 19/19 tests pass.
