# Agent Authoring & Validation Instructions: Tile (3, 6) — `QRT-SYNTHESIZE-D3`

**Target Tile:** `tile_3_6`  
**QRT Cell:** `QRT-SYNTHESIZE-D3`  
**Cognitive Demand:** `SYNTHESIZE` (Cross-Disciplinary Integration: Fusing Alien Mathematical Domains into a Unified Multi-Stage Problem-Solving Pipeline)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Geometry + Number Theory, Algebra + Geometry, Combinatorics + Number Theory  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 6)**, you are NOT testing elementary formula recall (`RETRIEVE`), structural mechanism explanation (`EXPLAIN`), mechanical calculation (`APPLY`), real-world verbal modeling (`MODEL`), or visual representation (`REPRESENT`). You are testing whether the student can **integrate concepts across two or more distinct mathematical branches (Geometry + Number Theory, Algebra + Geometry, Combinatorics + Number Theory) to establish an integrated multi-stage problem-solving pipeline that evaluates the protected scalar $W$**.

### The Decisive Act:
The student must identify and construct the cross-topic bridge (e.g. geometric inradius formula inducing a Diophantine hyperbolic equation solved by divisor pairing; cubic Vieta polynomial coefficients coupled with the Pythagorean metric; or set-theoretic inclusion-exclusion synthesized with modular block residue classes) before solving for the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-SYNTHESIZE-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The synthesis task: e.g. Synthesizing geometric inradius formulation with Diophantine divisor pairing on integer right triangles]",
  "Y": "[The given configuration: e.g. Right-angled triangle with integer side lengths, Area = 3 * Perimeter]",
  "Z": "[The governing cross-topic invariant: Area = r * s = 3 * (2s) -> inradius r = 6; right triangle inradius r = (a + b - c)/2 = 6 induces Diophantine relation (a - 12)(b - 12) = 72; minimum perimeter at factor pair (8, 9) -> a = 20, b = 21, c = 29 -> P = 70]",
  "W": "[The Protected Work: The terminal evaluated scalar: e.g. 70]",
  "wrong_idea": "[Primary student cross-topic failure: e.g. Evaluating the extreme factor pair (1, 72) yielding perimeter 13 + 84 + 85 = 182 instead of the minimum perimeter]",
  "replacement_rule": "[Correct synthesis rule: The minimum perimeter occurs when sides a and b are closest, corresponding to factor pair (8, 9): a = 20, b = 21, c = 29 -> P = 70]",
  "visual_job": "[Render right triangle with inscribed circle of radius 6, showing tangent segments a - r and b - r; avoid unmounted SVGs]",
  "check_job": "[Independent verification: At a = 20, b = 21, c = 29, Area = (20 * 21)/2 = 210, Perimeter = 20 + 21 + 29 = 70. Area / Perimeter = 210 / 70 = 3. Integer conditions satisfied.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present a problem whose complete solution requires combining tools from at least two separate mathematical disciplines.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical answer or scalar constant.
   - 3 Distractors: Explicitly engineered from authentic partial-synthesis errors (e.g. stopping after the first discipline's deduction, choosing the wrong factor extremum, or modular block omission).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs attention to the initial discipline foundations (e.g. inradius formula, Vieta's formulas, or prime factorization) without revealing the cross-disciplinary bridge.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Formulates the governing unified equation connecting the two disciplines (e.g. Diophantine factor equation, hypotenuse expansion, or PIE set summation), stopping strictly before solving for $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the synthesis technique **WITHOUT using the exact parameters, numerical values, or answer of Core 2**.
   - If Core 2 synthesizes with $\text{Area} = 3 \times \text{Perimeter}$, Core 1A must demonstrate on $\text{Area} = \text{Perimeter}$.
   - If Core 2 has answer $W = 70$, the number $70$ must NOT appear in Core 1A text.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's exact verification path.
   - For example, if Core 1A uses inclusion-exclusion, Core 1B verifies via modular residue period partitioning.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical synthesis crux** under modified constants (e.g. Area $= 2 \times$ Perimeter $\implies r = 4 \implies (a - 8)(b - 8) = 32$).
- Must declare question-specific unit navigation: `data-core-unit-id="GEO-SYNTH-INRADIUS-DIOPHANTINE-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the synthesis to general integer Heronian triangles with integer inradius and circumradius.

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Fusing two distinct discipline frameworks)
- `representation_translation`: 1 (Geometric/algebraic condition to Diophantine/PIE form)
- `reasoning_chain_length`: 2 (Multi-stage cross-topic reasoning chain)
- `algebra_computational_load`: 1 or 2 (Divisor pairing / cubic Vieta expansion / multi-step PIE)
- `trap_exception_sensitivity`: 0 or 1 (Minimum vs maximum perimeter / boundary block handling)
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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_6/test_self_mutations.py` $\implies$ 19/19 tests pass.
