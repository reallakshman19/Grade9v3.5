# Instructions to Authoring Agents: Tile (4, 7) `QRT-JUSTIFY-D4`

## Cell Identity & Cognitive Mandate
- **Tile ID:** `tile_4_7`
- **Cell:** `QRT-JUSTIFY-D4`
- **Difficulty Band:** Band 4 ($D4$), National / International Olympiad
- **Target Score Range:** $[9, 10]$
- **Cognitive Demand:** `JUSTIFY` (Rigorous deductive proof discrimination, sharpness/equality bounds, and infinite descent)

## Decisive Act
Students must autonomously discriminate and justify unassailable mathematical proofs, probabilistic existence arguments (e.g. Caro-Wei via vertex permutations and linearity of expectation), algebraic reverse bounding with sharpness equality characterization (Cauchy Reverse Technique), and number-theoretic infinite descent contradiction arguments (Fermat's descent on $x^4+y^4=z^2$) without intermediate scaffolding.

## Prohibitions & Safeguards
1. **Pre-commit DOM Privacy:** Never include answer-revealing styling classes (`--success`, `correct_style`, `is_correct`) or data attributes (`data-correct="true"`, `data-answer="..."`) on option buttons.
2. **Locked Solution Container:** The details container MUST carry `class="qb-solution" inert hidden data-locked="true"`.
3. **No Solution Leaks in Summaries:** `<summary>` must only state pedagogical labels (e.g. `Show Complete Olympiad Derivation`), never the keyed letter or claim.
4. **Hint Anti-Leak Rules:** Neither Hint 1 nor Hint 2 may disclose the keyed option letter or the protected claim $W$. Hints must activate the foundational proof structure without completing the deduction.
5. **KaTeX Delimiters:** Never use raw `$`. Use `\(` and `\)` for inline math, and `\[` and `\]` for display math. Properly escape KaTeX expressions in JSON.
6. **Difficulty Factor Sum:** The five component factors (`concept_model_selection`, `representation_translation`, `reasoning_chain_length`, `algebra_computational_load`, `trap_exception_sensitivity`) must sum exactly to `difficulty_score`, bounded by $[9, 10]$.
