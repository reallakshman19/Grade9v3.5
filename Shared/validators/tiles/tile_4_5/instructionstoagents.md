# Agent Authoring & Validation Instructions: Tile (4, 5) — `QRT-REPRESENT-D4`

**Target Tile:** `tile_4_5`  
**QRT Cell:** `QRT-REPRESENT-D4`  
**Cognitive Demand:** `REPRESENT` (Translating, encoding, and transforming mathematical structures across disparate domains and evaluating protected quantity $W$)  
**Difficulty Band:** `D4` (National & International Olympiad Elite, Score Range $[9, 10]$)  
**Subject Focus:** Trigonometry $\longleftrightarrow$ Cyclotomic Polynomials (Cotangent Square Sum), Combinatorics $\longleftrightarrow$ Linear Algebra over $\mathbb{F}_2$ (Oddtown Characteristic Vector Spaces), Geometry $\longleftrightarrow$ Coordinate Centers (Dual Apollonian Circles)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (4, 5)**, you are NOT testing elementary representations (`REPRESENT-D1/D2`) or standard regional Olympiad coordinates (`REPRESENT-D3`). You are testing whether the student can **execute deep, isomorphic cross-domain mathematical transformations between seemingly unrelated fields (such as mapping trigonometric rational angle identities to cyclotomic polynomial roots, translating set intersection parity into finite field inner product spaces, or converting metric distance ratios into Apollonian circle coordinate centers) under zero external prompting**.

### The Decisive Act:
The student must map the problem configuration to its dual representational domain (polynomial ring, $\mathbb{F}_2^n$ vector space, or Cartesian circle completion), use the structural invariants of that target domain (Vieta's relations, dimension bounds, or center coordinate distances), and evaluate the protected quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-REPRESENT-D4`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The elite representation transformation task: e.g. Translating regular heptagon angle relations into polynomial roots of de Moivre's formula]",
  "Y": "[The given configuration: e.g. Three acute angles theta_k = k*pi/7 for k in {1, 2, 3}]",
  "Z": "[The governing representational bridge: de Moivre expansion of sin(7*theta) = 0 in powers of cotangent yielding 7*u^3 - 35*u^2 + 21*u - 1 = 0]",
  "W": "[The Protected Work: The exact evaluated invariant quantity: e.g. 5 / 9 / 10]",
  "wrong_idea": "[Primary student misconception: e.g. Trying decimal approximations of trigonometric values or confusing tangent and cotangent Vieta sums]",
  "replacement_rule": "[Correct representation solution: The three cotangent squares are roots of the cubic, so Vieta's formula gives sum = 35/7 = 5]",
  "visual_job": "[Render cyclotomic roots on unit circle, F_2 incidence matrix, or Apollonian coordinate circles; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Verify reciprocal sum of tangent roots from 7 - 35*v + 21*v^2 - v^3 = 0 => 35/7 = 5. Verified.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all trigonometric angles, club intersection rules, or beacon coordinates stated unambiguously.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical quantity.
   - 3 Distractors: Explicitly engineered from authentic representational confusions (e.g. taking tangent sums instead of cotangent sums, subtracting $1$ from dimension, or evaluating beacon separation rather than circle centers).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Introduces the representational bridge (e.g. de Moivre polynomial expansion, characteristic incidence vectors in $\mathbb{F}_2^n$, or squaring distance ratios) without stating $W$.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Formulates the intermediate equation ($7u^3 - 35u^2 + 21u - 1 = 0$, linear independence in $\mathbb{F}_2^n$, or completed squares) without calculating $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the underlying representation **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 evaluates the cotangent square sum for $n = 7$, Core 1A must demonstrate cyclotomic polynomials on heptagon chord products or $n = 5$.
   - If Core 2 evaluates Oddtown in dimension $n = 9$, Core 1A must demonstrate linear algebraic methods via Eventown or Fisher's inequality.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an intermediate invariant before the full solution steps unlock.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's direct derivation.
   - If Core 1A used direct binomial expansions, Core 1B must analyze the problem via tangent polynomial reciprocals or complex exponential products.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical representational crux** (e.g. cotangent square sum for $n = 9$, or Eventown theorem).
- Must declare question-specific unit navigation: `data-core-unit-id="TRIG-REP-CYCLOTOMIC-POLYNOMIALS-04"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the representational method to an Olympiad competition setting (e.g. Graham-Pollak theorem or polynomial roots on the unit circle).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D4: [9, 10])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (National/International Elite Olympiad cross-domain representation selection)
- `representation_translation`: 2 (Cyclotomic polynomials / finite field vector spaces / Apollonian coordinate completion)
- `reasoning_chain_length`: 2 (Multi-phase representation reduction and algebraic solving)
- `algebra_computational_load`: 2 (Substantial binomial expansion, linear independence proofs, or quadratic completion)
- `trap_exception_sensitivity`: 1 or 2 (Symmetric root pairings, finite field characteristic 2 peculiarities, ratio $k=1$ degeneracies)
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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_4_5/test_self_mutations.py` $\implies$ 19/19 tests pass.
- [ ] 12. Tile validator reports hold: `QRT_REPRESENT_D4_DECISIVE_ACT_REVIEW_REQUIRED`.
