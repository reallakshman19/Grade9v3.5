# Agent Authoring & Validation Instructions: Tile (3, 7) — `QRT-JUSTIFY-D3`

**Target Tile:** `tile_3_7`  
**QRT Cell:** `QRT-JUSTIFY-D3`  
**Cognitive Demand:** `JUSTIFY` (Rigorous Deductive Proofs, Invariant Arguments, Extremal Principles, Monovariant/Coloring Impossibility Proofs, and Counterexample Construction)  
**Difficulty Band:** `D3` (Advanced Olympiad, Score Range $[6, 8]$)  
**Subject Focus:** Combinatorics (Modulo-3 Invariant Coloring), Number Theory (Method of Infinite Descent), Algebra (Cauchy-Schwarz Inequality Bound)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (3, 7)**, you are NOT testing elementary formula recall (`RETRIEVE`), structural mechanism explanation (`EXPLAIN`), mechanical calculation (`APPLY`), real-world verbal modeling (`MODEL`), visual representation (`REPRESENT`), or cross-topic synthesis (`SYNTHESIZE`). You are testing whether the student can **formulate rigorous deductive justifications, invariant impossibility arguments, or extremal equality conditions across advanced Olympiad structures to evaluate the protected claim $W$**.

### The Decisive Act:
The student must construct a formal non-constructive deductive argument (e.g. diagonal 3-coloring invariant proving tiling impossibility via color imbalance, Fermat's infinite descent proving the non-existence of non-trivial integer solutions, or Cauchy-Schwarz variable substitution proving an inequality bound and its strict equality conditions) before selecting or verifying the protected claim $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-JUSTIFY-D3`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The justification task: e.g. Proving that an 8x8 chessboard with one corner square removed cannot be tiled by 1x3 straight trominoes]",
  "Y": "[The given configuration: e.g. 8x8 chessboard with corner (1, 1) removed, leaving 63 squares, candidate tiling by twenty-one 1x3 trominoes]",
  "Z": "[The governing invariant structure: Coloring invariant: color (i, j) with (i + j) mod 3; every 1x3 tromino covers exactly one square of each color; full board has counts (22, 21, 21); removing corner (1, 1) of color 2 leaves (22, 21, 20), violating the necessary condition of 21 of each color]",
  "W": "[The Protected Work: The terminal evaluated justification: e.g. Every 1x3 tromino covers exactly one square of each color, but removing corner (1, 1) leaves color counts 22, 21, 20 instead of 21, 21, 21]",
  "wrong_idea": "[Primary student justification failure: e.g. Claiming that since 63 is divisible by 3, a valid tiling must exist, or using a 2-color checkerboard which cannot constrain 1x3 trominoes]",
  "replacement_rule": "[Correct justification rule: Apply diagonal 3-coloring (i + j) mod 3; every straight 1x3 tromino covers {0, 1, 2}; color imbalance (22, 21, 20) rigorously precludes tiling]",
  "visual_job": "[Render 8x8 grid colored with 3 alternating diagonal colors, highlighting removed corner square; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Rotating the coloring by 90 degrees yields a symmetrical color discrepancy, confirming tiling impossibility.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present an impossibility claim, existence condition, or extremal bound requiring formal deductive justification.
2. **Options:** 
   - 1 Keyed Option ($W$): The complete, mathematically rigorous deductive justification.
   - 3 Distractors: Explicitly engineered from authentic proof traps (e.g. confusing necessary with sufficient conditions, pseudo-modular proofs, or omitting equality requirements).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Directs attention to the proof framework (e.g. invariant coloring, infinite descent hypothesis, or Cauchy-Schwarz substitution) without developing the proof.
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: States the intermediate contradiction step or inequality evaluation, stopping strictly before the final deductive conclusion $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the justification technique **WITHOUT using the exact scenario, board dimensions, Diophantine equation, or answer of Core 2**.
   - If Core 2 justifies tromino tiling impossibility on $8 \times 8$, Core 1A must demonstrate on $5 \times 5$.
   - If Core 2 uses $x^3 + 2y^3 = 4z^3$, Core 1A must demonstrate infinite descent on $x^2 = 2y^2$.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's exact justification path.
   - For example, if Core 1A uses diagonal coloring $(i + j) \pmod 3$, Core 1B verifies via horizontal/vertical line parity or polynomial coloring.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical deductive justification crux** (e.g. $7 \times 7$ board with one square removed tiled by $1 \times 3$ trominoes).
- Must declare question-specific unit navigation: `data-core-unit-id="COMB-JUS-COLORING-INVARIANT-03"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the justification to 3D grid cube decomposition ($2 \times 2 \times 2$ vs $1 \times 1 \times 4$).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D3: [6, 8])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (Selection of advanced invariant coloring, infinite descent, or Cauchy-Schwarz)
- `representation_translation`: 1 or 2 (Translating spatial/algebraic configurations into invariant partitions)
- `reasoning_chain_length`: 2 (Multi-step deductive contradiction or bound chain)
- `algebra_computational_load`: 0 or 1 (Minimal arithmetic, focused on deductive logic)
- `trap_exception_sensitivity`: 1 (Managing parity of removed cell or equality conditions)
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
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values or answer text.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_3_7/test_self_mutations.py` $\implies$ 19/19 tests pass.
