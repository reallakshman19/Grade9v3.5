# Agent Authoring & Validation Instructions: Tile (4, 1) — `QRT-RETRIEVE-D4`

**Target Tile:** `tile_4_1`  
**QRT Cell:** `QRT-RETRIEVE-D4`  
**Cognitive Demand:** `RETRIEVE` (Recalling & Instantiating National/International Olympiad Theorems & Invariants)  
**Difficulty Band:** `D4` (National/International Elite Olympiad, Score Range $[9, 10]$)  
**Subject Focus:** Geometry (Feuerbach's Nine-Point Circle Tangency Theorem), Number Theory (Kummer's Carry Valuation Theorem for $p$-adic powers), Combinatorics (Burnside's Lemma for group action orbits)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (4, 1)**, you are NOT testing elementary recall (`RETRIEVE-D1`), standard competition formulas (`RETRIEVE-D2`), or regional olympiad theorems (`RETRIEVE-D3`). You are testing whether the student can **retrieve and instantiate national and international Olympiad level theorems, high-order structural invariants, and advanced mathematical machinery directly from deep memory under zero external prompting**.

### The Decisive Act:
The student must identify that the problem requires an elite international Olympiad theorem (e.g., Feuerbach's tangency of the nine-point circle with incircle/excircles, Kummer's base-$p$ carry counting theorem for $v_p\binom{n}{k}$, or Burnside's Lemma for symmetry orbit counting), retrieve its exact symbolic formulation from memory, instantiate the given parameters, and evaluate the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-RETRIEVE-D4`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The elite theorem retrieval task: e.g. Retrieval of Feuerbach's Nine-Point Circle Tangency Theorem]",
  "Y": "[The given configuration: e.g. Triangle with incircle (I, r), excircles (I_A, r_A), (I_B, r_B), (I_C, r_C), and nine-point circle (N, R/2)]",
  "Z": "[The governing elite theorem: Feuerbach's Theorem states the nine-point circle is tangent internally to the incircle and externally to all three excircles]",
  "W": "[The Protected Work: The exact target statement, valuation, or orbit count: e.g. 'internally tangent to the incircle and externally tangent to the three excircles' / 8 / 11]",
  "wrong_idea": "[Primary student misconception: e.g. Confusing internal and external tangency points, or calculating standard Legendre formula without carries]",
  "replacement_rule": "[Correct theorem instantiation: In any non-equilateral triangle, the nine-point circle touches the incircle internally and the three excircles externally at Feuerbach points]",
  "visual_job": "[Render nine-point circle with incircle and excircles, highlighting points of tangency; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Verify distance formula IO_9 = R/2 - r and I_A O_9 = R/2 + r_A: Feuerbach tangency holds exactly.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all high-level geometric, arithmetic, or group-theoretic configurations stated rigorously.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact simplified terminal quantity, valuation, or theorem statement.
   - 3 Distractors: Explicitly engineered from authentic theorem misapplications (e.g., confusing internal/external tangency, omitting the identity permutation or miscounting cycle structures, base-$p$ carry calculation errors).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Reminds the student of the elite theorem by name (e.g., Feuerbach's Theorem, Kummer's Theorem, Burnside's Lemma) without providing the exact terminal calculation or statement.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Provides intermediate relations (e.g. Euler's distance relation $OI^2 = R(R-2r)$, base-$p$ digital expansions $n = \sum a_i p^i$, or group element cycle index breakdown), stopping strictly before disclosing $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the underlying theorem **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 evaluates $v_2\binom{1000}{357}$, Core 1A must demonstrate Kummer's theorem on $v_2\binom{20}{7}$ or $v_3\binom{27}{10}$.
   - If Core 2 evaluates 2-colorings of a regular hexagon under $D_6$, Core 1A must demonstrate Burnside's lemma on coloring vertices of a square under $D_4$.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an intermediate invariant (such as base-$p$ carry count or cycle decomposition) before the proof unfolds.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's direct formula substitution.
   - If Core 1A used base-$p$ digital subtraction $v_p\binom{n}{k} = \frac{S_p(k) + S_p(n-k) - S_p(n)}{p-1}$, Core 1B must analyze the problem via base-$p$ columnar addition with carries.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical theorem retrieval crux** (e.g. $v_2\binom{500}{123}$ or coloring faces of a cube under rotational symmetry).
- Must declare question-specific unit navigation: `data-core-unit-id="NT-RETRIEVE-KUMMER-D4"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the theorem to a related domain (e.g. Lucas' Theorem for binomial residues modulo $p$, or Polya's Enumeration Theorem with weight generating functions).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D4: [9, 10])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (National/International Elite Olympiad theorem retrieval: Feuerbach / Kummer / Burnside)
- `representation_translation`: 2 (Advanced geometric locus / base-$p$ representations / group action cycle decompositions)
- `reasoning_chain_length`: 2 (Deep multi-step reasoning following theorem retrieval)
- `algebra_computational_load`: 2 (High algebraic manipulation or intricate combinatorial counting)
- `trap_exception_sensitivity`: 1 or 2 (Non-equilateral degenerate cases, carry boundary conditions, rotational vs reflectional symmetries)
- **Total:** Must be strictly in $\{9, 10\}$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[9, 10]$ and component sum equals `difficulty_score`.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes (`--success`, `correct_style`, etc.).
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ (including 20-character sliding windows for long strings) or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values or target formulas.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_4_1/test_self_mutations.py` $\implies$ 19/19 tests pass.
- [ ] 12. Tile validator reports hold: `QRT_RETRIEVE_D4_DECISIVE_ACT_REVIEW_REQUIRED`.
