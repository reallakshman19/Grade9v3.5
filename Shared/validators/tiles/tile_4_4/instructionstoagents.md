# Agent Authoring & Validation Instructions: Tile (4, 4) — `QRT-MODEL-D4`

**Target Tile:** `tile_4_4`  
**QRT Cell:** `QRT-MODEL-D4`  
**Cognitive Demand:** `MODEL` (Abstracting dynamic, physical, stochastic, or game-theoretic processes into formal mathematical structures and solving for protected quantity $W$)  
**Difficulty Band:** `D4` (National & International Olympiad Elite, Score Range $[9, 10]$)  
**Subject Focus:** Probability (Asymmetric Gambler's Ruin Difference Equations), Game Theory (Sprague-Grundy Multi-Pile Nim Invariants), Geometric Optimization (Fermat-Torricelli Minimal Steiner Tree via 60° Rotation)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (4, 4)**, you are NOT testing elementary word-to-equation setups (`MODEL-D1/D2`) or standard regional Olympiad models (`MODEL-D3`). You are testing whether the student can **abstract high-complexity real-world, stochastic, game-theoretic, or network optimization phenomena into rigorous national and international Olympiad mathematical models, establish governing invariant equations, and evaluate the protected quantity $W$**.

### The Decisive Act:
The student must formulate the formal difference equation, vector space XOR sum, or geometric rotation metric from the contextual prompt, solve the boundary value problem or kernel relation, and evaluate the protected numerical or radical quantity $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-MODEL-D4`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The elite mathematical modeling task: e.g. Formulating an asymmetric Markov random walk difference equation with absorbing boundaries]",
  "Y": "[The given configuration: e.g. Trading bot starting with $2, win probability 2/3, loss probability 1/3, target $4 before $0]",
  "Z": "[The governing model: Second-order linear difference equation P_k = p*P_{k+1} + q*P_{k-1} with P_0 = 0 and P_4 = 1]",
  "W": "[The Protected Work: The exact evaluated model output: e.g. 4/5 / 24 / \\sqrt{25 + 12\\sqrt{3}}]",
  "wrong_idea": "[Primary student misconception: e.g. Assuming symmetric random walk 2/4 = 1/2 or naive linear interpolation]",
  "replacement_rule": "[Correct model solution: Solve the characteristic polynomial to obtain P_k = (1 - (1/2)^k)/(1 - (1/2)^4), yielding P_2 = 4/5]",
  "visual_job": "[Render Markov chain transition graph, Nim binary expansion table, or rotated Steiner equilateral triangle; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Solve the tridiagonal matrix equation for [P_1, P_2, P_3]^T. P_2 = 4/5 confirmed.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all stochastic transition probabilities, token counts, or junction coordinates stated unambiguously.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact evaluated numerical or radical quantity.
   - 3 Distractors: Explicitly engineered from authentic modeling errors (e.g. assuming symmetry, reducing the wrong pile, or calculating orthogonal Manhattan distances instead of the Fermat point).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Introduces the mathematical modeling framework (e.g. state probability recurrence $P_k = p P_{k+1} + q P_{k-1}$, Bouton Nim-sum, or rotation of Fermat-Torricelli point).
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Formulates the intermediate equation without calculating the terminal quantity $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the underlying modeling method **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 evaluates an asymmetric random walk with $p = 2/3, N = 4$, Core 1A must demonstrate the method on a symmetric random walk ($p = 1/2$) or with different boundaries ($N = 3$).
   - If Core 2 evaluates a three-pile Nim game $(11, 19, 27)$, Core 1A must demonstrate Sprague-Grundy theory on a two-pile game or piles $(3, 5, 7)$.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an intermediate invariant before the full model solution unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's direct derivation.
   - If Core 1A solved the difference equation via characteristic roots, Core 1B must analyze the problem via tridiagonal matrix inversion or martingale stopping times.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical modeling crux** (e.g. Gambler's ruin with $p = 3/4, N = 3$).
- Must declare question-specific unit navigation: `data-core-unit-id="PROB-MOD-STOCHASTIC-RANDOM-WALK-04"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the modeling framework to an Olympiad competition setting (e.g. multi-dimensional random walks or games on directed acyclic graphs).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D4: [9, 10])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (National/International Elite Olympiad mathematical modeling)
- `representation_translation`: 2 (Stochastic difference / binary vector space / rotational metric representation)
- `reasoning_chain_length`: 2 (Multi-stage modeling and solution execution)
- `algebra_computational_load`: 2 (Substantial algebraic recurrence, bitwise XOR, or radical evaluation)
- `trap_exception_sensitivity`: 1 or 2 (Asymmetric drift, game normal play convention, obtuse angle Steiner collapse)
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
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_4_4/test_self_mutations.py` $\implies$ 19/19 tests pass.
- [ ] 12. Tile validator reports hold: `QRT_MODEL_D4_DECISIVE_ACT_REVIEW_REQUIRED`.
