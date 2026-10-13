# #201 — five remaining D2 academic review packets (unsigned authored TEST)

**Status: QUALIFIED REVIEW PENDING for all five.** Source-pinned to PR #205 commit `3ce42e25e6bcc5e2617faa6729db212ebac2ca48` stacked on authored PR #191 exact head `eb3cf06646f00bf208084e794b41b4d8d83135b6`. These are **five wholly-authored TEST candidates**, not authentic Core2 Q003 (#183), not newly designated Owner goldens, and not a declaration that either the mathematical content or the QRT classifications are independently accepted.

**Real evidence:** [Exact-head native seven-cell CI #38419413687](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38419413687) and [artifact 11825477458](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38419413687/artifacts/11825477458) contain the five native sole-renderer HTML roles and index per candidate, SHA256-verified page receipts, actual pre-attempt H2 visible text, attempt/H3 role-browser state, 105 local-HTTP 390/768/1280 screenshots and seven protocol tiles. All **7/7** technical records passed, but no independent H/S/P/M or Owner approval follows. Earlier [PRE-REVIEW.md](PRE-REVIEW.md), [ACADEMIC-REVIEW-REQUEST.md](ACADEMIC-REVIEW-REQUEST.md) and [issue #211](https://github.com/reallakshman19/Grade9v3.5/issues/211) handle the *other two* high-risk RETRIEVE/MODEL cases, so they are not represented as accepted by this packet.

Each excerpt below is from the immutable candidate package on PR #191. The author's answer/check and difficulty components are **proposals**, not qualified mathematical proof or ratings. The H2 quotation is from the actual browser `benchmark-results.json`, not hypothetical draft language. A qualified reviewer must inspect actual CORE1, CORE1A, CORE1B, CORE2A and CORE2B HTML and accessible figures, not solely this synopsis.

## QRT-EXPLAIN-D2

- **Exact source:** [`explain.v1.json`](../explain.v1.json); Git blob SHA-1 `6169016e7bfa87b582e2b38f356c769e66b0cf2e`. Source question `Q-TEST-QRT-EXPLAIN-D2-PRIMARY` (AUTHOR CANDIDATE). Native manifest: [`imo182-qrt-d2-explain.manifest.json`](../../../products/imo182-qrt-d2-explain.manifest.json).
- **Declared primary demand and band:** EXPLAIN / D2, **not reviewed**. Declared protected crux: `MOVE-TEST-QRT-EXPLAIN-D2-BRIDGE`.

**Actual primary learner stem (verbatim):**

> For every positive integer t, explain WHY 3^(t+1)=3×3^t rather than 3^t+3. Connect the exponent to repeated factors, and give an exact value of t that disproves addition.

**Author-proposed correct outcome:** 3^(t+1)=3×3^t for all positive integer t, and not generally 3^t+3.

**Author's independent-check statement (verify, not accept):** Check t=2: 27=3×9, not 9+3=12.

**Author five-component proposal** (order: model selection, representation translation, reasoning chain, computation, trap): `0 / 1 / 1 / 0 / 1`; total `3`, proposed `D2`. Qualified reviewer must independently score and justify each component, including D1/D2/D3 boundary.

**CORE2A H2 visible before any written attempt (from Chromium):**

> Recall how products of equal factors can be regrouped when the count changes.

**Prior WORKED stem in the authored package (review for W preteaching):**

> Explain why 2^3 is 2×2^2 rather than 2^2+2.

**Core2B changed-condition TRANSFER stem (separate independent correctness and W check):**

> A student claims that doubling the exponent always doubles the power: 2^(2k)=2×2^k for every positive integer k. Explain the correct relationship by grouping repeated factors and give an exact counterexample to the student's rule.

**Author-proposed transfer outcome:** 2^(2k)=(2^k)^2, not in general 2×2^k.

**Content risks to challenge, not pre-decided:**

- Is a general **EXPLAIN** warrant required, or can the learner simply execute the already-displayed identity? The stem supplies `3^(t+1)=3×3^t`; the learner still must explain associative grouping and falsify the additive alternative.
- For D1/D2/D3, decide whether connecting factor count to a general identity and a counterexample is a real D2 bridge, not two unrelated routine actions.

**Reviewer must report:** the dominant operation differentiating EXPLAIN from APPLY/EXPLAIN/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY nearest alternative; a counterfactual with direct evidence of learner-selected W; D1/D2/D3 five-component ratings; truth and changed-condition maths; all 12 H1–H3/S1–S3/P1–P3/M1–M3 outcomes; a specific citation to staged native HTML and accessible diagram or disclosure state; ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT, dated qualified signature and conflict disclosure. Each verdict requires separate later Owner decision ID.

## QRT-APPLY-D2

- **Exact source:** [`apply.v1.json`](../apply.v1.json); Git blob SHA-1 `5c50dc66c187a1be6b8fcd1cd844fd58be665536`. Source question `Q-TEST-QRT-APPLY-D2-PRIMARY` (AUTHOR CANDIDATE). Native manifest: [`imo182-qrt-d2-apply.manifest.json`](../../../products/imo182-qrt-d2-apply.manifest.json).
- **Declared primary demand and band:** APPLY / D2, **not reviewed**. Declared protected crux: `MOVE-TEST-QRT-APPLY-D2-SEQUENTIAL-BASE`.

**Actual primary learner stem (verbatim):**

> A bag's listed price is 960 credits. It is reduced by 25%, and then a further 10% is taken off the REDUCED price. Apply the two known percentage steps to find the final price. Find the equivalent single discount percent of the ORIGINAL listed price. Show why simply adding 25% and 10% gives a wrong answer.

**Author-proposed correct outcome:** Final 648 credits; equivalent single discount 32.5%, not 35%.

**Author's independent-check statement (verify, not accept):** Independent verification: 960×0.75×0.9=648=960×0.675; a single discount of 32.5% leaves 67.5%.

**Author five-component proposal** (order: model selection, representation translation, reasoning chain, computation, trap): `0 / 1 / 1 / 1 / 1`; total `4`, proposed `D2`. Qualified reviewer must independently score and justify each component, including D1/D2/D3 boundary.

**CORE2A H2 visible before any written attempt (from Chromium):**

> Use the familiar remaining-percent rule for a single discount. Decide which quantity would become the base of a later discount.

**Prior WORKED stem in the authored package (review for W preteaching):**

> A basket of 1000 credits is reduced 20%, then a further 20% of its NEW price. Apply the two percent steps; compare with one 40% discount.

**Core2B changed-condition TRANSFER stem (separate independent correctness and W check):**

> After a 20% INCREASE followed by a 10% DECREASE of the increased amount, the final price is 1080 credits. The original price is unknown. Apply the inverse of the known percentage steps to find the ORIGINAL price, then determine the net percent change from original to final. Justify why +20% and −10% cannot simply be combined as +10%.

**Author-proposed transfer outcome:** Original 1000 credits; net change +8%, not +10%.

**Content risks to challenge, not pre-decided:**

- **Task method largely cued:** the prompt specifies that the second 10% is on the **reduced** price. If the author claims choosing that base is protected W, record the contradiction; determine whether the remaining two-step execution + equivalent original-base comparison constitute D2 or D1.
- The inverse transfer is a meaningful different-direction step; check it independently without assigning an automatic higher difficulty band.

**Reviewer must report:** the dominant operation differentiating APPLY from APPLY/EXPLAIN/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY nearest alternative; a counterfactual with direct evidence of learner-selected W; D1/D2/D3 five-component ratings; truth and changed-condition maths; all 12 H1–H3/S1–S3/P1–P3/M1–M3 outcomes; a specific citation to staged native HTML and accessible diagram or disclosure state; ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT, dated qualified signature and conflict disclosure. Each verdict requires separate later Owner decision ID.

## QRT-REPRESENT-D2

- **Exact source:** [`represent.v1.json`](../represent.v1.json); Git blob SHA-1 `4cf21d3132537917b56ad441349fd5b009c8cb7d`. Source question `Q-TEST-QRT-REPRESENT-D2-PRIMARY` (AUTHOR CANDIDATE). Native manifest: [`imo182-qrt-d2-represent.manifest.json`](../../../products/imo182-qrt-d2-represent.manifest.json).
- **Declared primary demand and band:** REPRESENT / D2, **not reviewed**. Declared protected crux: `MOVE-TEST-QRT-REPRESENT-D2-GRID-TO-DISJOINT`.

**Actual primary learner stem (verbatim):**

> The diagram shows a 5-ROW ×7-COLUMN grid of identical unit-square tiles. ALL cells in the leftmost 2 columns are shaded; among the 5 columns to their right, ONLY the topmost 2 rows are shaded. You must represent the same number of UNSHADED cells in TWO ways: (1) subtract a pair of nonoverlapping shaded rectangles from the whole grid, and (2) read the remaining row-lengths and show an equivalent rectangle product. Write both expressions, the common value, and explain why subtracting 2 full columns plus 2 FULL rows from 35 would double-count.

**Author-proposed correct outcome:** 15 unshaded unit squares; 35−(2×5)−(2×5)=15, which equals 3×5.

**Author's independent-check statement (verify, not accept):** Independent enumerative check: classify each cell as left shade, upper-right shade or lower-right unshaded; counts 10+10+15=35.

**Author five-component proposal** (order: model selection, representation translation, reasoning chain, computation, trap): `0 / 2 / 1 / 0 / 1`; total `4`, proposed `D2`. Qualified reviewer must independently score and justify each component, including D1/D2/D3 boundary.

**CORE2A H2 visible before any written attempt (from Chromium):**

> If two shaded descriptions meet in a corner, do you subtract the shared cells twice? Sketch boundaries WITHOUT naming the sizes of the shaded pieces.

**Prior WORKED stem in the authored package (review for W preteaching):**

> In a 6×6 equal-unit square grid, shade the entire top 2 rows, and shade the rightmost 2 columns ONLY in the remaining 4 rows. Represent the unshaded count as (i) full grid minus disjoint bands and (ii) a remaining rectangle.

**Core2B changed-condition TRANSFER stem (separate independent correctness and W check):**

> There is NO drawing. A shape is built from unit squares, with all rows LEFT-ALIGNED. Reading from TOP to BOTTOM, its six row lengths are: 8, 8, 5, 5, 5, 5. Reconstruct a six-row grid description and represent its area in TWO genuinely different ways: first by grouping complete row bands, then as one surrounding rectangle with ONE rectangular corner cut out. Identify EXACTLY which rows and columns are missing; prove both expressions count the same squares. Explain why removing three columns from ALL six rows would be wrong.

**Author-proposed transfer outcome:** 36 squares: 2×8+4×5=36 and 6×8−4×3=36; missing lower-right 3 columns in rows 3 through 6.

**Content risks to challenge, not pre-decided:**

- **Method may be preselected:** primary explicitly says use **a pair of nonoverlapping shaded rectangles** and an equivalent rectangle product, while the author rationale claims choosing a disjoint decomposition is learner-owned W. Determine whether mapping the actual 5×7 shaded grid to the two specific regions remains a sufficiently independent REPRESENT act.
- Pre-commit H2 prompts the overlap decision; verify initial SVG accessible semantics do not reveal the two 10-cell blocks or the 15-cell result. Transfer has **no drawing** and requires reverse construction: compare bands fairly.

**Reviewer must report:** the dominant operation differentiating REPRESENT from APPLY/EXPLAIN/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY nearest alternative; a counterfactual with direct evidence of learner-selected W; D1/D2/D3 five-component ratings; truth and changed-condition maths; all 12 H1–H3/S1–S3/P1–P3/M1–M3 outcomes; a specific citation to staged native HTML and accessible diagram or disclosure state; ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT, dated qualified signature and conflict disclosure. Each verdict requires separate later Owner decision ID.

## QRT-SYNTHESIZE-D2

- **Exact source:** [`synthesize.v1.json`](../synthesize.v1.json); Git blob SHA-1 `e7af6505cf049b3231124df614ab273e55868a8d`. Source question `Q-TEST-QRT-SYNTHESIZE-D2-PRIMARY` (AUTHOR CANDIDATE). Native manifest: [`imo182-qrt-d2-synthesize.manifest.json`](../../../products/imo182-qrt-d2-synthesize.manifest.json).
- **Declared primary demand and band:** SYNTHESIZE / D2, **not reviewed**. Declared protected crux: `MOVE-TEST-QRT-SYNTHESIZE-D2-UNIFY-CHECKS-ORDER`.

**Actual primary learner stem (verbatim):**

> Using any THREE DISTINCT digits chosen from {1,2,3,4,5}, form a three-digit number with 4 in the HUNDREDS place. It must be divisible by 6 and be the LARGEST possible number under these rules. Decide which digits to put in the TENS and ONES places, justify your choice by combining BOTH the even-last-digit rule AND the digit-sum divisibility-by-three rule, and show why no larger number works.

**Author-proposed correct outcome:** 432 is the largest possible code.

**Author's independent-check statement (verify, not accept):** Compute 432÷6=72. The complete list of candidates ending2 with hundreds4 and distinct digits is {412,432,452}; only432 has digit sum divisible by3.

**Author five-component proposal** (order: model selection, representation translation, reasoning chain, computation, trap): `0 / 1 / 2 / 0 / 1`; total `4`, proposed `D2`. Qualified reviewer must independently score and justify each component, including D1/D2/D3 boundary.

**CORE2A H2 visible before any written attempt (from Chromium):**

> Divisible by six has TWO separate tests. When trying a large-looking candidate, how would each test be checked independently, without supplying any digits?

**Prior WORKED stem in the authored package (review for W preteaching):**

> Using exactly three DISTINCT digits from {1,2,3,4}, with hundreds digit fixed as 3, find the LARGEST three-digit multiple of six. Explain how two divisibility checks interact with the place-value order.

**Core2B changed-condition TRANSFER stem (separate independent correctness and W check):**

> A safe three-digit code is 534, which is divisible by 6. You MUST swap EXACTLY TWO digit positions ONCE (no digit may be changed or added). The new three-digit code must be SMALLER than 534 while STILL divisible by 6. Analyze ALL three possible single position swaps. Which swap works, and why do the other two fail? Combine the invariant DIGIT-SUM check with the change in the LAST digit and numerical order.

**Author-proposed transfer outcome:** Swap hundreds and tens: 354 is the only permissible result.

**Content risks to challenge, not pre-decided:**

- The stem already names **both** parity and digit-sum tests. Verify the learner must coordinate these with place-value maximality, rather than perform an overt algorithm (APPLY).
- D2 versus D3: decide whether bounding the candidate space and ruling out every larger valid number is a short connection or requires independent search strategy; use transfer's three swaps as a counterfactual.

**Reviewer must report:** the dominant operation differentiating SYNTHESIZE from APPLY/EXPLAIN/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY nearest alternative; a counterfactual with direct evidence of learner-selected W; D1/D2/D3 five-component ratings; truth and changed-condition maths; all 12 H1–H3/S1–S3/P1–P3/M1–M3 outcomes; a specific citation to staged native HTML and accessible diagram or disclosure state; ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT, dated qualified signature and conflict disclosure. Each verdict requires separate later Owner decision ID.

## QRT-JUSTIFY-D2

- **Exact source:** [`justify.v1.json`](../justify.v1.json); Git blob SHA-1 `37e24be0a24bd1a062107dd788ae6f3eb5e5059c`. Source question `Q-TEST-QRT-JUSTIFY-D2-PROOF` (AUTHOR CANDIDATE). Native manifest: [`imo182-qrt-d2-justify.manifest.json`](../../../products/imo182-qrt-d2-justify.manifest.json).
- **Declared primary demand and band:** JUSTIFY / D2, **not reviewed**. Declared protected crux: `MOVE-TEST-QRT-JUSTIFY-D2-A-WARRANT`.

**Actual primary learner stem (verbatim):**

> A learner claims that (m+1)(m+2)(m+3) is divisible by 6 for every positive integer m because ONE of these factors must itself be divisible by 6. Is that reasoning valid? Whether or not it is valid, prove the divisibility claim for every positive m. A few examples are not a proof.

**Author-proposed correct outcome:** The stated reason is invalid (m=2 is a counterexample to it), but the universal claim is true using guaranteed factors 2 and 3 and their coprimality.

**Author's independent-check statement (verify, not accept):** Countercheck m=2: no individual factor 3,4,5 is divisible by 6, yet the product is 60. Separately enumerate m modulo 6 to corroborate the universal proof.

**Author five-component proposal** (order: model selection, representation translation, reasoning chain, computation, trap): `1 / 1 / 1 / 0 / 1`; total `4`, proposed `D2`. Qualified reviewer must independently score and justify each component, including D1/D2/D3 boundary.

**CORE2A H2 visible before any written attempt (from Chromium):**

> How can the whole product have a property that no one factor must possess? Identify a valid general principle without selecting any factor for the learner.

**Prior WORKED stem in the authored package (review for W preteaching):**

> For any positive integer n, show that n(n+1)(n+2) is divisible by 6. Explain why a few numerical checks do not establish the claim for every n.

**Core2B changed-condition TRANSFER stem (separate independent correctness and W check):**

> A learner claims that for EVERY positive integer k, the product k(k+1)(k+2)(k+3) is divisible by 48. Decide whether the claim is true. Give a general justification or an exact counterexample, then find and prove the greatest positive integer that always divides this four-factor product.

**Author-proposed transfer outcome:** The 48 claim is false: k=1 gives 1×2×3×4=24. The greatest positive integer dividing every such four-factor product is 24.

**Content risks to challenge, not pre-decided:**

- **High teaching leakage risk:** the WORKED item itself proves the universal claim that three consecutive positive integers have a product divisible by 6; the PRIMARY is the **offset** triple `(m+1)(m+2)(m+3)` plus rejection of the 'one factor divisible by 6' rationale. Determine whether a learner can merely relabel `n=m+1` and copy the worked proof, or whether the misconception critique + valid warrant is an independent JUSTIFY-D2 W.
- H2 asks for a general principle; ensure it does not supply the exact coprime warrant. In transfer, 48 is false at k=1, but the greatest universal divisor is 24: proof requires 4! divisibility and k=1 upper bound; do not confuse this with a single worked example.

**Reviewer must report:** the dominant operation differentiating JUSTIFY from APPLY/EXPLAIN/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY nearest alternative; a counterfactual with direct evidence of learner-selected W; D1/D2/D3 five-component ratings; truth and changed-condition maths; all 12 H1–H3/S1–S3/P1–P3/M1–M3 outcomes; a specific citation to staged native HTML and accessible diagram or disclosure state; ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT, dated qualified signature and conflict disclosure. Each verdict requires separate later Owner decision ID.

## Cross-cell falsifiers, evidence provenance and response format

Reviewers must explicitly distinguish **prompt-provided steps**, **H1/H2 pre-attempt support**, **worked CORE1A examples**, **genuine learner-owned W**, **post-nonblank H3**, **CORE1B reconstructed boundary**, and **CORE2B changed-case transfer**. An accessible SVG label, overlay, alternate text, hints, or pre-attempt repair could supply conceptual W even when the browser's known-answer tokens are absent. A generic HTML matching test is not a substitute for checking cognitive semantics. Challenge near-neighbour demand and D1/D2/D3 level using the project's [QUESTION-REVIEW-MATRIX.md](../../../../docs/method/QUESTION-REVIEW-MATRIX.md) rather than label strings.

All twelve named judgments are mandatory: `H1,H2,H3,S1,S2,S3,P1,P2,P3,M1,M2,M3`. For each, return `ACCEPT / REVISE / REJECT` plus role, exact observed text/figure/behavior citation, reason, and any change required. Arithmetic oracles are **author-independent computations**, not professional QRT qualifications.

```text
Cell ID / PR source git SHA / native run artifact:
Reviewer full name, mathematics & QRT qualifications, institutional affiliation:
Independent of author/fixer? Conflict declaration / reviewer date:
True PRIMARY demand / closest competing demand + decisive learner-owned act:
Five component scores & reasons (model/representation/chain/load/trap), D1/D2/D3 boundary:
X / known Y / warranted Z / protected W, and all pre-attempt disclosure:
Worked Core1A versus primary novelty and Core1B boundary reconstruction:
Primary mathematics + Core2B changed-condition correctness, proof/counterexample:
H1: H2: H3: S1: S2: S3: P1: P2: P3: M1: M2: M3: (each with evidence)
Decision: ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT; exact remediation if needed:
Signer / date / exact reviewed native artifact:
```

**Hard stop:** academic acceptance must never be inferred from a self-review, math oracle, successful CI or this packet. Original frozen five-role golden is immutable. Owner accepts per cell with separate ID only after independent signoff. Owner acceptance numerator remains **0/28**; no source-rights/authentic Core2, production publication or merge permitted through these docs.
