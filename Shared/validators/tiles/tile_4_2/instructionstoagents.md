# Agent Authoring & Validation Instructions: Tile (4, 2) — `QRT-EXPLAIN-D4`

**Target Tile:** `tile_4_2`  
**QRT Cell:** `QRT-EXPLAIN-D4`  
**Cognitive Demand:** `EXPLAIN` (Analyzing and articulating deep structural mechanisms, geometric/topological invariants, and failure barriers)  
**Difficulty Band:** `D4` (National & International Olympiad Elite, Score Range $[9, 10]$)  
**Subject Focus:** Geometry (Circular Inversion Conformal & Locus Mechanics), Number Theory (Eisenstein's Lattice Lemma for Quadratic Reciprocity), Combinatorics (Hall's Marriage Theorem Obstruction Mechanism)  

---

## 1. Cognitive Contract & The Agent's Thinking Objective

When generating, reviewing, or validating an item for **Tile (4, 2)**, you are NOT testing superficial factual recall (`RETRIEVE`), elementary explanations (`EXPLAIN-D1/D2`), or regional olympiad explanations (`EXPLAIN-D3`). You are testing whether the student can **dissect and rigorously articulate the deep structural mechanisms, projective/topological invariants, or geometric lattice partitions that govern national and international Olympiad theorems without external guidance**.

### The Decisive Act:
The student must identify that the problem requires an explanation of the core geometric projection invariance, prime-coprime lattice partition, or deficient set capacity bottleneck, articulate why the invariant forces the theorem to hold (or prevents a configuration from existing), and evaluate the protected work $W$.

---

## 2. The 8-Slot Cognitive Architecture for `QRT-EXPLAIN-D4`

Every item authored for this tile must explicitly fill these 8 cognitive slots:
```json
{
  "X": "[The elite structural explanation task: e.g. Explaining the mechanism by which circular inversion maps circles through the origin to straight lines]",
  "Y": "[The given configuration: e.g. Circle with diameter OA = d passing through inversion center O, inverted with radius R]",
  "Z": "[The governing invariant: Orthogonal projection invariance OP * cos(theta) = d implies OP' * cos(theta) = R^2 / d is constant]",
  "W": "[The Protected Work: The exact invariant mechanism statement: e.g. 'orthogonal projection of P' onto diameter ray OA is constant at R^2/d, forcing the locus to be a line perpendicular to OA']",
  "wrong_idea": "[Primary student misconception: e.g. Confusing conformality of tangents with the locus of inverted points]",
  "replacement_rule": "[Correct structural explanation: Inversion scales radius inversely to cosine, keeping the orthogonal projection onto diameter line OA fixed at R^2/d]",
  "visual_job": "[Render circle with diameter OA, chord OP, right angle at P, and projected inverted point A' on ray OA; avoid unmounted SVGs]",
  "check_job": "[Independent verification: Convert to Cartesian coordinates: x^2 + y^2 = dx. Inverted coordinates u = R^2 x / (x^2 + y^2) = R^2 / d. Verified.]"
}
```

---

## 3. Five-Core Authoring Protocol for Autonomous Agents

### 3.1 `Core 2` (Exam Custody & Pre-Commit Privacy)
1. **Stem:** Present the problem with all high-level geometric, arithmetic, or graph-theoretic configurations stated rigorously.
2. **Options:** 
   - 1 Keyed Option ($W$): The exact structural mechanism or invariant decomposition.
   - 3 Distractors: Explicitly engineered from authentic conceptual confusions (e.g. confusing conformality with radial displacement, confusing totient residue counts with lattice point partitions, or confusing degree sums with neighborhood capacity).
3. **Pre-Commit Isolation:**
   - Pre-commit buttons must use neutral classes: `<button class="qb-option-btn">`.
   - **STRICT PROHIBITION:** Never use `--success`, `correct_style`, `data-correct="true"`, or `is_correct` in pre-commit DOM.
   - Solution container must be locked: `<details class="qb-solution" inert hidden data-locked="true">`.
4. **Hint Ladder (Preserving $W$):**
   - `Hint 1 (ACTIVATE_INVARIANT)`: Introduces the structural perspective (e.g. projecting onto diameter ray, partitioning grid points across the diagonal, or restricting matched targets to adjacent neighborhood).
   - `Hint 2 (DECISIVE_INTERMEDIATE_FORMULATION)`: Formulates the intermediate mathematical relation without revealing the terminal mechanism statement $W$.
   - **Anti-Leak Sliding Window:** Must not share any 20-character substring with $W$.

### 3.2 `Core 1A` (Declarative Study — The Anti-Spoil Law)
1. **The Anti-Spoil Law:** Core 1A must teach the underlying mechanism **WITHOUT using the exact numbers or stem values of Core 2**.
   - If Core 2 evaluates circular inversion of a circle through the origin, Core 1A must explain inversion of a line not through the origin into a circle through the origin.
   - If Core 2 evaluates Eisenstein's lemma across odd primes $p, q$, Core 1A must explain the 1D Gauss lemma half-system sign count.
2. **Required 7 Blocks:** Must contain `entry_assumptions`, `inferential_jump`, `why_valid_derivation`, `three_way_bridge`, `representation_anchor`, `boundary_conditions`, and `worked_check`.

### 3.3 `Core 1B` (Interactive Tutor — Gating & Model Alternation)
1. **Predictive Gate:** Must enforce `answer_before_attempt: "FORBIDDEN"`. The student must predict an intermediate invariant before the full mechanism derivation unlocks.
2. **The Model Alternation Law (`differs_from_teaching_path: true`):**
   - Core 1B **must not** duplicate Core 1A's direct derivation.
   - If Core 1A used synthetic Euclidean geometry, Core 1B must analyze the problem via Cartesian coordinates.

### 3.4 `Core 2A` (Supported Practice)
- Author a practice item sharing the **identical structural explanation crux** (e.g. inversion of concentric circles, or lattice count in a triangle).
- Must declare question-specific unit navigation: `data-core-unit-id="GEO-EXP-INVERSION-MECHANISM-04"`.

### 3.5 `Core 2B` (Transfer Assessment)
- Transfer the structural mechanism to an Olympiad problem (e.g. orthogonal circles under inversion, or matching in hypergraphs).

---

## 4. 5-Factor Difficulty Calibration Standards (Band D4: [9, 10])

When scoring the difficulty components, ensure each component is an integer $\in \{0, 1, 2\}$ and their sum equals `difficulty_score`:
- `concept_model_selection`: 2 (National/International Elite Olympiad structural mechanism explanation)
- `representation_translation`: 2 (Advanced geometric locus / lattice partition / bipartite capacity representation)
- `reasoning_chain_length`: 2 (Multi-stage rigorous deductive justification)
- `algebra_computational_load`: 1 or 2 (Substantial trigonometric, algebraic, or combinatorial counting)
- `trap_exception_sensitivity`: 2 (Inversion pole singularities, coprime lattice boundary boundaries, bipartite matching vacuity)
- **Total:** Must be strictly in $\{9, 10\}$.

---

## 5. Agent Verification Checklist Before Release

- [ ] 1. All 3 Golden Fixtures pass with `verdict: PASS` when evaluated by `validator.py`.
- [ ] 2. Difficulty score is strictly within $[9, 10]$ and component sum equals `difficulty_score`.
- [ ] 3. Crux move reference is non-empty and declared in both `cognitive_classification` and `answer`.
- [ ] 4. Pre-commit HTML options contain zero answer-leaking classes or attributes.
- [ ] 5. Solution `<details>` has `inert`, `hidden`, and `data-locked="true"`.
- [ ] 6. Neither Hint 1 nor Hint 2 discloses Protected Work $W$ (verified by 20-character sliding window check) or the keyed option letter.
- [ ] 7. HTML card contains valid `data-core-unit-id` matching `core1a_unit_id`.
- [ ] 8. Core 1A text does not leak Core 2 specific numerical values or target formulas.
- [ ] 9. Core 1B declares `answer_before_attempt: "FORBIDDEN"`.
- [ ] 10. All KaTeX math formulas compile cleanly with zero `.katex-error` spans.
- [ ] 11. Run `python -m unittest Shared/validators/tiles/tile_4_2/test_self_mutations.py` $\implies$ 19/19 tests pass.
- [ ] 12. Tile validator reports hold: `QRT_EXPLAIN_D4_DECISIVE_ACT_REVIEW_REQUIRED`.
