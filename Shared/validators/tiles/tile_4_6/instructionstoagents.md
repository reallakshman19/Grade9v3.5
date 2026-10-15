# Instructions to Authoring Agents: Tile (4, 6) `QRT-SYNTHESIZE-D4`

## Cell Identity & Cognitive Mandate
- **Tile ID:** `tile_4_6`
- **Cell:** `QRT-SYNTHESIZE-D4`
- **Difficulty Band:** Band 4 ($D4$), National / International Olympiad
- **Target Score Range:** $[9, 10]$
- **Cognitive Demand:** `SYNTHESIZE` (Cross-domain multi-branch mathematical bridge building)

## Decisive Act
Students must autonomously bridge at least two disparate, advanced Olympiad disciplines (e.g. Algebra $\times$ Combinatorics, Euclidean Geometry $\times$ Real Quadratic Field Diophantine Analysis, $p$-adic Hensel Lifting $\times$ Chinese Remainder Theorem) without intermediate scaffolding. The student must formulate an intermediate bridge invariant $Z$ and compute the exact value of protected work $W$.

## Prohibitions & Safeguards
1. **Pre-commit DOM Privacy:** Never include answer-revealing styling classes (`--success`, `correct_style`, `is_correct`) or data attributes (`data-correct="true"`, `data-answer="..."`) on option buttons.
2. **Locked Solution Container:** The details container MUST carry `class="qb-solution" inert hidden data-locked="true"`.
3. **No Solution Leaks in Summaries:** `<summary>` must only state pedagogical labels (e.g. `Show Complete Olympiad Derivation`), never the keyed letter or value.
4. **Hint Anti-Leak Rules:** Neither Hint 1 nor Hint 2 may disclose the keyed option letter or the value $W$. Hints must scaffold the two disparate domains separately (H1 conceptual nudge) and pose the bridge invariant $Z$ (H2 tactical step).
5. **KaTeX Delimiters:** Never use raw `$`. Use `\(` and `\)` for inline math, and `\[` and `\]` for display math. Properly escape KaTeX expressions in JSON.
6. **Difficulty Factor Sum:** The five component factors (`concept_model_selection`, `representation_translation`, `reasoning_chain_length`, `algebra_computational_load`, `trap_exception_sensitivity`) must sum exactly to `difficulty_score`, bounded by $[9, 10]$.
