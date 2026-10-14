# #201 — qualified independent academic review request: RETRIEVE-D2 and MODEL-D2

**Review status: REQUESTED, NOT PERFORMED.** Prepared 13 October 2026. Scope is two high-risk **wholly authored TEST** exemplars, not an official IMO question or the authentic source Q003 (#183). Parent issue [#201](https://github.com/reallakshman19/Grade9v3.5/issues/201); draft adoption [PR #205](https://github.com/reallakshman19/Grade9v3.5/pull/205), based on authored [PR #191](https://github.com/reallakshman19/Grade9v3.5/pull/191). The requesting author/agent cannot confer an independent qualification or QRT acceptance.

## Exact evidence to review, not inferred status

- **Candidate source commit:** `eb3cf06646f00bf208084e794b41b4d8d83135b6` (PR #191 head, unchanged authored maths records).
- **Pinned technical-evidence commit:** `aa8659c23dbd5c82a2ec1b4c8c28e50cbbaf6af1` (PR #205).
- [Actual sole-renderer native HTML, 7 protocol tiles, precommit H2 text and screenshots — CI #38399681860](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38399681860); [download artifact 11814892965](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38399681860/artifacts/11814892965). Both relevant candidates have **five** native role pages, an index, no gaps, receipt SHA agreement, actual Chromium attempt/second-boundary/H3 pass. Browser checks do **not** certify that the cognitive operation was preserved.
- The original Owner golden `G-IMO-G9-FIVE-CORE-20261012` is **immutable and specific to different original content**. Here compare registered Core role semantics, page slots/components, protected W, and post-attempt behavior, **not unrelated HTML byte equality**. Core2A H3 AFTER_ATTEMPT is a known post-golden policy delta; Owner successor designation remains open.
- [Candidate math pre-review and unadopted rewrite alternatives](PRE-REVIEW.md); [all seven canonical unsigned evidence rows](evidence.v1.json). Review answers must explicitly cite the actual learner HTML, including displayed question, H1/H2, initial SVG/accessible alternatives, H3-after-attempt, Core1A changed-case exit, Core1B changed-boundary and Core2B transfer.

## Candidate A: QRT-RETRIEVE-D2 — **HIGH RISK: APPLY**

**Source:** [retrieve.v1.json](../retrieve.v1.json), [manifest](../../../products/imo182-qrt-d2-retrieve.manifest.json). Exact authored source git blob `15333326a90763160d2ff52a32ec579218ed9ac8`.

**Current learner primary stem (verbatim):**

> A rectangle has perpendicular sides 9m and12m. To get from one corner to the opposite one you may cross the straight diagonal or walk along TWO adjacent edges. Travel allowance is AT MOST18m. Retrieve the right-triangle distance relation and calculate BOTH routes. Which route(s) satisfy the allowance, and how many metres does the shorter route save? Explain why d² is not itself a measured length.

**Correct mathematical facts for independent examination:** direct `√(9²+12²)=15m`; along two edges `9+12=21m`; only direct satisfies `≤18m`; saving `21−15=6m`. `d²` is area-dimension `m²`, not the distance in `m`. An inverse transfer with diagonal 13m and one side 5m has missing side 12m, boundary17m, cap15m permits only diagonal13m and saves4m. Core1B access boundary closes the diagonal: a geometric 17m route is **unavailable**, edge-only 23m exceeds cap20m, so **no permissible route**. These results already have independently computed arithmetic oracles, which do not decide the **primary cognitive demand**.

**The unresolved question:** The original stem itself names a right-triangle distance relation, prescribes both computations, then asks to apply allowance and saving. The decisive act may be **APPLY**, whose canonical definition is *execute a known relation/procedure under the right conditions*, rather than **RETRIEVE**, whose decisive act is *select/reconstruct a fact, category, property, unit or condition*. Merely using the word “Retrieve” does not determine demand.

**Observed pre-attempt Core2A H2 (actual browser text):**

> Recall how the squares of two perpendicular sides relate to the squared diagonal; which operation returns a length? Keep numbers unknown.

**Request of the independent reviewer:** State what an unaided learner must *choose/reconstruct* to succeed; distinguish a true RETRIEVE decision from following a largely specified method; decide whether a **short connection/choice plus execution** remains (D2 versus D1), and whether enough independent strategy is required for D3. Review the [proposed RETRIEVE-focused alternative](PRE-REVIEW.md#retrieve-d2-primary-demand-repair-option) as a **non-adopted option**; it asks learners to classify three route/dimension expressions and could be too cued for D2. Choose **ACCEPT CURRENT / REVISE CURRENT / RECLASSIFY CURRENT** with rationale. If RECLASSIFY to APPLY, **do not count the RETRIEVE-D2 cell accepted** or silently reuse an APPLY-D2 acceptance.

**Author-proposed five difficulty components (not independent scores):** `concept_model_selection=1`, `representation_translation=1`, `reasoning_chain_length=1`, `algebra_computational_load=0`, `trap_exception_sensitivity=1`; total 4, proposed D2. Challenge each with evidence.

## Candidate B: QRT-MODEL-D2 — **MODEL versus APPLY; author-side variable-choice revision remains UNSIGNED**

**Source:** [model.v1.json](../model.v1.json), [manifest](../../../products/imo182-qrt-d2-model.manifest.json). Current revised authored source git blob `db87b5a4a7bc807e0680a64417f2c6ca5ca08cf3`; the original reviewed stem at historical Git blob `eabc0626c978989a7a40dcc1d2dd22adf611b359` explicitly preselected LARGE cups. That initial audit finding remains historical, not erased. A new exact-head native render/evidence run is required; historical screenshot/CI artifacts do not test this revision.

**Revised learner primary stem (verbatim; author-side 14 Oct 2026, NOT qualified review):**

> At a school stall exactly 9 drinks were sold: small cups cost 4 credits each and large cups 7 credits each. The stall collected exactly 48 credits. Decide which cup-size count your variable represents, form a one-variable model that links the number sold with the amount collected, solve both counts, and check they are whole and meet both givens.

**Correct independent mathematics:** If `x` large, `9−x` small, then `4(9−x)+7x=48` gives `x=4` large and 5 small. Equally if `x` small and `9−x` large, `4x+7(9−x)=48` gives `x=5` small, 4 large; check `4×7+5×4=48` and `4+5=9`. **Changed Core2B:** 11 tickets with prices 5 and 9, claimed 74; `55+4x=74` yields `x=19/4` not an integer, so impossible. Feasible neighbors: 71 (4 premium, 7 ordinary) and 75 (5 premium, 6 ordinary).

**The unresolved academic question after author revision:** The old stem preselected LARGE cups, contradicting the author claim that learners choose the count category; the 14 Oct revision now permits either cup size and the rubric accepts both. An **independent qualified** reviewer must still judge whether selecting the unknown and forming the complement/weighted revenue relation make MODEL the primary D2 demand rather than a familiar APPLY procedure. Assess whether H1/H2/H3 truly protect W. Do **not** mark the warning academically CLEARED or infer acceptance from the changed wording.

**Observed pre-attempt Core2A H2 (actual browser text):**

> Recall that each type contributes unit price times number of items. What total must the two contributions meet?

**Request of the independent reviewer:** Identify exactly which model terms the stem, H1, H2, diagram, and pre-attempt controls already disclose; determine if `9−x`, unit-price weights, combined linear equation and feasibility check remain learner-authored. Evaluate the [minimal alternative stem](PRE-REVIEW.md#model-d2-learner-owned-variable-selection-repair-option) which removes the category preselection without adding another blueprint. If the current stem fails the protected-W criterion, require **full five-role consistent revision and fresh native receipts**; do not modify just the stem in isolation.

**Author-proposed five difficulty components (not independent scores):** `concept_model_selection=1`, `representation_translation=1`, `reasoning_chain_length=1`, `algebra_computational_load=1`, `trap_exception_sensitivity=0`; total 4, proposed D2. Challenge each with evidence.

## Mandatory review judgments — separate academic evidence from renderer PASS

Review **each candidate independently** for: math answer, counterexample, inverse/changed-case mathematics; canonical PRIMARY_DEMAND and most credible alternative; D1/D2/D3 boundary supported by all five difficulty components; X/Y/Z/W and what remains learner-owned. Assess all **12** QRT asks against the *actual learner content*, recording a reason for each:

| Ask | Qualified reviewer evidence question |
|---|---|
| H1 | Clarifies what the question turns on without selecting W? |
| H2 | Connects held knowledge to question without supplying W? |
| H3 | After nonblank attempt, genuinely opens Z while W remains independently necessary? |
| S1 | Initial drawing, SVG title/desc/aria support X without answer leakage? |
| S2 | Stage linking known Y appears at meaningful time, not as a generic figure? |
| S3 | Later stage supports the bridge toward Z without completing W too early? |
| P1 | All *pre-attempt* panels and controls leave W intact (beyond numeric answer-sentinel tests)? |
| P2 | Concept link goes to this task's **specific** bridge/repair? |
| P3 | Full solution explains why each step holds and gives an independent check? |
| M1 | A plausible, task-specific misconception is represented? |
| M2 | Diagnosis discriminates misconception from a one-off arithmetic slip? |
| M3 | Repair demonstrates failure mechanism and establishes transferable replacement rule? |

Technical evidence only reports **BROWSER_AND_STATIC_PASS**, 7/7 source-safe native packages, 105/105 asset-loaded viewport checks, and real H2/H3 commitment controls. It is not evidence of an independent verdict on any ask. Rights, access to authentic Q003, print quality and public routes are separate gates.

## Reviewer response — copy and complete once per candidate

```text
Cell and exact source SHA:
Reviewer full name / institution / maths-QRT qualifications:
Independent of candidate author/fixer? YES / NO
Conflict-of-interest declaration and review date:
Primary demand: RETRIEVE / EXPLAIN / APPLY / MODEL / REPRESENT / SYNTHESIZE / JUSTIFY
Most plausible alternative and reason:
Five difficulty component evidence and scores (0/1/2) with band D1/D2/D3/D4:
X / Y / Z / protected W, including what stem/H1/H2 have already supplied:
Mathematical proof and exact changed-case correctness: PASS / REVISE + citation:
H1: ...  H2: ...  H3: ...
S1: ...  S2: ...  S3: ...
P1: ...  P2: ...  P3: ...
M1: ...  M2: ...  M3: ...
Cite actual HTML role, text, figure accessible description or artifact evidence:
Decision for this authored exemplar: ACCEPT CURRENT / REVISE / RECLASSIFY / REJECT
Required minimal change and independent replay conditions:
Signature (reviewer) and date:
```

**Owner gate is separate**: record explicit per-exemplar `ACCEPT / REVISE / REJECT` and a unique Owner decision ID **only after** the qualified review. A new successor golden requires a separate immutable fixture/version/rights designation; no existing golden bytes may be altered. Official QRT Owner-accepted tally remains **0/28**. All seven D2 artifacts and PRs remain **draft TEST, not public, not merged**. An agent's computation or unsupervised verdict does not substitute for a qualified reviewer.
