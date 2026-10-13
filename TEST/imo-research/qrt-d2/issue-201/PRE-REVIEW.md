# Issue #201 — D2 mathematics and primary-demand pre-review (NOT qualified approval)
13 October 2026 · source SHA: PR #191 `eb3cf06646f00bf208084e794b41b4d8d83135b6` · draft PR #205

This is a **technical preparatory audit** of the seven wholly authored TEST candidates. It supplies independent arithmetic/combinatorial checks and falsifiable cognitive-demand questions for a future qualified mathematics/QRT reviewer. It is **not** a signed independent qualified academic verdict; there is no Owner ACCEPT/REVISE/REJECT decision, new golden designation, publisher right, merge, or release. Official QRT acceptance remains **0/28**.

## Reproducible independent-computation scope

Run `python -m unittest discover -s TEST/imo-research/qrt-d2/issue-201 -p math_oracle_201.py -v`. This uses `Fraction`, `isqrt`, exhaustive permutations, row/cell sets, full-domain ticket counts and residue/gcd checks. The separately-rendered native HTML benchmark `benchmark_201.py` tests blueprint/fixture structure and stateful browser commitment; **neither test suite observes real learner cognition**. Existing authored `*-review.md` packets are the claims being checked, not independent signatures.

| QRT candidate | Independently testable mathematical outcomes | Pending primary-demand/band judgment |
|---|---|---|
| RETRIEVE-D2 | 9–12–15 diagonal, boundary 21, max18 only direct, saving6. Reverse 5–12–13, boundary17, limit15 saving4. Core1B inaccessible diagonal despite geometric length17. | **HIGH-RISK RETRIEVE vs APPLY**: the stem explicitly names a right-triangle distance relation and directs both calculations/comparison. Most observable protected work is procedural execution and decision, not *selecting/reconstructing a fact* against near neighbors. Reviewer should consider `RECLASSIFY` or revise the item to test a genuine retrieval discriminant. Do not automatically occupy an accepted RETRIEVE-D2 slot. |
| EXPLAIN-D2 | For b≥2, positive t, `b^(t+1)=b×b^t`; with b=3/t=1 the additive claim gives 6 instead of 9. Core2B correct double-count identity `2^(2k)=(2^k)^2`; **k=1 is a coincidental match** for the false `2×2^k` rule, so use k=2 (16≠8) as counterexample. | Mechanism explanation is distinct from merely computing a power; D2 reasonable *provisional*, verify that H2/figures do not supply the final linking statement. |
| APPLY-D2 | 960→720→648, equivalent 32.5% original reduction; exit 500→450→360, 28% reduction; independent boundary 100×1.1×0.9=99; reverse 1080÷(1.2×0.9)=1000, +8%. | Fits APPLY if the **reference update and original-reference reconciliation** remain the learner's work. The stem already says second 10% applies to reduced price; distinguish cue recognition from deciding the base. |
| MODEL-D2 | Whole counts (5 small, 4 large) yield 5×4+4×7=48. Eleven 5/9-credit tickets yield totals `55+4x`; 74 impossible, immediate neighbors 71 (7+4) and 75 (6+5); impossible Core1B boundary 49 with 7 tickets. | Main stem **already specifies the unknown category: LARGE cups**. The claimed W should not be "choose which variable"; it is forming **the complement `9−x` and weighted sum**. D2 MODEL plausible, reviewer must judge whether formulation rather than algebraic APPLY remains decisive. |
| REPRESENT-D2 | 5×7 grid: disjoint left 2×5 and upper-right 2×5 removals gives 15; remainder 3×5 confirms. False overlapping full-row subtraction gives 11. Transfer row lengths 8,8,5,5,5,5 give 36; 6×8−4×3=36. | Preserving unit-cell meaning across shading/disjoint subtraction/row product supports REPRESENT-D2. However the prompt **names nonoverlapping subtraction**, so assess whether selecting the disjoint partition remains meaningful. |
| SYNTHESIZE-D2 | Exhaustive distinct-digit permutations prove primary maximum 432, concept worked 342, exit 732, Core1B 654. Core2B three swaps of 534 produce 354,435,543; 354 alone is smaller and divisible by 6. | Coordinate divisibility-by-2, divisibility-by-3 and maximality. D2 vs D3 depends on learner-relative familiarity with both tests; item already names both tests, so **not automatically D3** merely because three constraints appear. |
| JUSTIFY-D2 | Every consecutive triple product is divisible by 6; m=2 gives 3×4×5=60 but **no individual factor divisible by 6**. Four consecutive factor products divisible by 24; k=1 gives 24, disproving 48 and proving maximum possible universal divisor is no greater than 24. | Universal proof requires guaranteeing 2 and 3 separately, then coprime inference; a few examples cannot prove universal divisibility. D2 vs D3 remains subject-review judgment based on whether modular reasoning is already a held component. |

### Rigorous proof obligations not discharged by a finite test

For all positive `m`, one of `m+1,m+2` is even and one of the three `m+1,m+2,m+3` is divisible by 3 (three exhaustive residues). Since 2 and 3 are coprime, 6 divides the product. For all positive `k`, exactly one of four consecutive integers is a multiple of 4, and another is even, so the product contains at least three factors of 2; one term is a multiple of 3. Hence 24 always divides the four-product. At `k=1`, the product equals exactly 24, so no larger universal divisor exists. These are *mathematical proof outlines*, still requiring qualified academic review of presentation.

## Frozen golden/blueprint status

`G-IMO-G9-FIVE-CORE-20261012` remains untouched. Exact original HTML SHA locks and active Core1/Core1A/Core1B/Core2A/Core2B blueprint IDs match the new native renderer outputs by structural slot/component technique; the intentional Core2A H3-after-attempt behavior is a **post-golden semantic delta** that requires separate Owner successor-golden authority if designated. The first technical benchmark at [run #38378804196](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38378804196) succeeded for all 7, with 21 browser role checks; this does not establish all twelve H/S/P/M semantic objectives as academic passes.

## Exact failure-baseline classification (not release green)

GitHub canonical-assurance [PR #205 run #38378804024](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38378804024) uploaded [artifact 11802749104](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38378804024/artifacts/11802749104) with `head.json`, `base.json`, `pinned-main.json`. Its **head and stacked base have identical 153 failed test IDs, 1 identical load error and 2,992 tests run; head-only failures = 0**. The same three JSON objects are byte-equivalent in older [PR #191 artifact 11775029549](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547179/artifacts/11775029549). Both head and base still differ from pinned-main (166 failures on 2,379 tests; changed test population), which must not be misrepresented as a green overall baseline.

Similarly, failed `guardrails` [PR #205 run #38378804040](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38378804040) and [PR #191 run #38310547127](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547127) each report **119 failures, 34 errors and 7 skips**, and their 154 failure/error markers match exactly. Therefore this PR introduced **no observed new failing IDs in the compared shared jobs**; the shared workflows themselves remain **FAILED**, require upstream issue ownership, and cannot be bypassed or marked green.

## Next qualified-review requests

Ask an independent qualified mathematics/QRT reviewer (explicit identity, date, conflict disclosure) to review the seven primary-demand claims and D1/D2/D3 boundaries, all 12 H1–H3/S1–S3/P1–P3/M1–M3 objectives **against exact native HTML** and safe/hidden accessible representations, each changed-case solution and P1 learner-owned W. Prioritize RETRIEVE-D2's possible reclassification, then MODEL-D2's variable-choice framing. Each outcome should be `ACCEPT / REVISE / RECLASSIFY` with a reasoned signature, and **separately** an Owner cell decision ID. No cell is independently accepted on this document.

## Proposed academic alternatives — reviewer decision required, NOT adopted

These are source-safe **alternative authored stems only**, not new learner-page records, accepted QRT fixtures, verified rendered packages, or permission to replace the existing #191 artifacts. They preserve the old candidates as immutable evidence while providing concrete revision options.

### RETRIEVE-D2: primary-demand repair option

**Observed question:** current stem directs the learner to *retrieve the right-triangle relation*, calculate two route lengths, compare to a cap and compute a saving. The main product is the calculation/decision; independent subject reviewer must decide whether that is in fact **APPLY-D2**.

**Alternative stem for reviewer to challenge:**

> A rectangular playground has perpendicular sides of 9 m and 12 m. The route card shows three expressions: (A) `9 + 12`, (B) `9² + 12²`, and (C) `√(9² + 12²)`. Match the expressions to (i) a trip using two adjacent edges, (ii) the direct corner-to-corner **distance**, and (iii) the **square** of that direct distance. State the defining property of each match. A display accepts measurements in **metres**, not square metres: which of A, B and C are directly valid route-length entries, and why? Evaluate just one chosen length as a check.

**Target decisive act:** retrieve/classify physical path and unit/property across near-neighbour expressions, not primarily execute a known diagonal-and-cap algorithm. **W**: independently connect each route/quantity to its defining property and choose valid length dimensions, then execute one confirming evaluation. D1 control: classify metres versus square metres in one expression. D3 control: a path has obstacles/non-rectilinear access or unknown orientation requiring a different route model. H1 should orient route labels without matching letters; H2 should invoke the meaning of square units and route geometry without selecting A/B/C; H3 may only guide a match after a nonblank attempt. **Caution:** because the options already contain candidate relations, an independent reviewer might judge this too cued or still D1. Revise again or RECLASSIFY if it does not require a meaningful D2 connection.

**No automatic patch:** adopting this variant would require changing the five-role learner journeys, independent Core1A lesson and Core2B changed-demand transfer, plus creating new exact-head native HTML receipts; it must not be spliced into only CORE2A.

### MODEL-D2: learner-owned variable selection repair option

**Observed question:** the current stem specifically instructs *choose a variable for the LARGE-cup count*. That already selects the model's variable meaning, while its review packet says choosing the variable is part of protected W. Independent reviewer should decide whether complement/weighted sum alone is sufficient MODEL-D2.

**Minimal alternative stem for reviewer to challenge:**

> At a school stall, exactly 9 drinks were sold. Small cups cost 4 credits each, large cups cost 7 credits each, and the total collected was exactly 48 credits. Form a **one-variable model** for the unknown mix, clearly defining your own variable and explaining the other count from the total. Solve the model, show both whole-number counts, and check the count and revenue independently.

**W** now contains the learner's variable definition, complementary count, weighted sum and independent two-condition check. H1/H2 must not write the complement `9−x` or choose one category for the learner; H3 after written attempt may suggest the complement as a method, not supply the primary solution. The existing 11-ticket infeasible changed-demand transfer remains a potentially suitable independent Core2B task, subject to separate congruence/count verification. Before adopting, rerun actual renderer, source/manifest git SHA, visual/H2 protection and review of all five roles.

**Required qualified decision:** for each observed stem, record PRIMARY_DEMAND = ACCEPT_AS_D2 / RECLASSIFY / REVISE, band justification using the five canonical components, explicit conflict statement, date and name; then a distinct Owner decision ID. Neither alternative is approved or integrated by this document.
