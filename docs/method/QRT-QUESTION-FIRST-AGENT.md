# Question-first QRT / Core blueprint mapper

**Purpose:** portable operating playbook for [the `qrt-blueprint-mapper` custom agent](../../.github/agents/qrt-blueprint-mapper.agent.md). This is an **agent work order**, not a new QRT cell, renderer, subject academic source, 29th template, acceptance gate or substitute for [the existing minimal-prompt pipeline](QRT-MINIMAL-PROMPT-PIPELINE.md).

## Why this exists

The #203 lesson was not merely that five of seven D4 candidates already rendered: the **order of work** mattered. Reading an issue status first obscured five valid artifacts; treating render success as academic evidence obscured cross-role answer leaks; literal golden equality across different questions would have been the wrong comparator. Only a question-specific **need → role → preexisting source → renderer → semantic evidence** map made the repair minimal and falsifiable.

The agent operates within these existing authorities:

| Contract | Governed decision | Never infer from it |
| --- | --- | --- |
| `Shared/quality/question-demand-matrix.v1.json` and `docs/method/QUESTION-REVIEW-MATRIX.md` | Primary cognitive act × five-component D1–D4 band; twelve H/S/P/M semantic asks | HTML anatomy, learner source rights or acceptance |
| `Shared/quality/question-demand-templates.v1.json` | Compiled 28-cell reference (read-only derived output) | New authored blueprints or 28 page copies |
| `Shared/web/interactive-page-blueprints.v1.json` | Existing Core1, Core1A, Core1B, Core2, Core2A, Core2B page slots/interaction contract | Which question, proof, W or classification is correct |
| `Shared/roles/CORE-AUTHORITY-CONTRACT.md` | Canonical truth/authorized source and transfer exposure boundaries | Whether a source is licensed or a learner demonstrated a bridge |
| `docs/method/QRT-MINIMAL-PROMPT-PIPELINE.md` and current precheck/gate | Owner-event truth, item self-audit, rendering and artifact-bound review | Independent qualified reviewer or Owner decision |
| Frozen `golden/units/` and registered TEST/PR artifacts | Exact-source byte oracle **only** for its own lock; cross-question structural/semantic reference | Mathematical identity or automatic academic acceptance |

## Standard agent run — two passes, not seven guessed pages

### Pass A: inspect and map (must be done before any learner-page edits)

1. **Question identity:** reproduce the exact question ID, source package/path/ref, source-rights state, learner eligibility and owner event truth. If the prompt contains the text only, preserve it and do not invent provenance or learner mastery.
2. **Academic solve:** establish correct result, alternate verification and counterexample/edge case; label unknown proof or rights as `RESEARCH_DUTY` rather than silently passing.
3. **Select one QRT cell:** name primary vs strongest adjacent demand and five-component D-band. For D4 challenge *which specific choice* remains learner-owned relative to D3; an unverified prerequisite can invalidate a RETRIEVE primary even if the maths is right. Resolve through `Shared/tools/question_review_matrix.py` when a canonical question/profile exists.
4. **Mark learner X/Y/Z/W:** Y requires `DEMONSTRATED` owner/learner evidence; without this write `UNKNOWN`. Ensure the safe bridge Z does not give away W. If Z/W cannot separate, no optional preattempt step.
5. **Inventory actual reusable assets:** inspect canonical subject concepts and existing Core1A/1B references, role definitions, QRT fixtures, relevant open PRs at **exact SHA**, source+manifest+figure Git blob SHAs, actual hosted six-page HTML and receipt SHA values, golden comparator ID/version and its authority scope, prior reviewers/COI/Owner IDs.
6. **Issue a disposition per role:** `REUSE_AS_IS`, `REPAIR_AUTHORED_SOURCE`, `AUTHOR_MISSING_CONTENT`, `REQUEST_SEPARATE_BLUEPRINT_OR_RENDERER_CHANGE_WITH_REPRO`, or `SOURCE_RIGHTS_HOLD`. For reusable assets, state what learner need they truly support; identical QRT cells do not imply duplicate questions or same exact bytes.
7. **Deliver an evidence map and proposed minimal diff** before writing any source. A question can be `RENDERED_TEST` but `CLASSIFICATION_PROVISIONAL` and `OWNER_PENDING` at once.

### Pass B: implement only the justified missing part

Edit source or TEST records and run the existing precheck/self-audit/sole registered renderer. Supply a new five-role manifest only if no valid prior manifest covers the question; do not generate Core2 original text without authorized custody. Preserve concept authority: Core1/Core1A/Core1B need canonical subject truth, not an unreviewed Core2 answer or the learner's own W. A Core1A worked construction must have its **own fresh exit**; a Core1B falsifier must not print an unrelated later Core2A answer; Core2B must change the demand rather than rewording it.

Verify exact hosted native output, 6/6 SHA-256 for a five-role plus index render, renderer gaps, 390px/tablet/desktop layout, blank/nonblank attempt/H3, cross-role Core1A/B disclosures, text/SVG/DOM/AX reachability and changed transfer. Compare five registered role-slot orders with immutable golden; note `CONTEXTUAL_DIFFERENCE` for correct question differences and `DEFECT` for behavior that violates the Blueprint/QRT. Do not patch golden snapshots to silence differences.

Keep at least six independent statuses: `RENDERED_TEST`, `TECHNIQUE_REVIEWED`, `ACADEMIC_REVIEWED`, `OWNER_QRT_ACCEPTED`, `OWNER_GOLDEN_DESIGNATED`, `RELEASED`. A CI artifact or a stamped JSON file is not a reviewer; avoid self-awarding Owner IDs.

## Required first response: question-to-asset mapping table

For each question, output the following, with **exact real refs** or `NOT_VERIFIED`. Do not start with a 28-cell status count.

| Question-scoped field | Minimum concrete evidence |
| --- | --- |
| Identity and rights | Verbatim question ID/reference, exact source path or owner prompt, source-class label; authorized Core2 or authored TEST only |
| Mathematics | Independent result/proof/counterexample, validator or separate checker |
| QRT | Selected primary `QRT-<DEMAND>-<D#>`; adjacent-demand and D3-vs-D4 challenge; components and provisional/confirmed status |
| Learner | X; Y and its actual demonstrated-evidence ref or `UNKNOWN`; Z distinct from W; stable protected move W |
| Existing Core1 | Canonical orientation relation and registered BP ref |
| Existing Core1A | Canonical construct/repair unit, distinct independent exit, existing asset or source gap |
| Existing Core1B | Specific misconception, falsifier and replacement rule; preexposure safety |
| Core2 rights | Exact authorized original source and `selection.core2`, otherwise `SOURCE_RIGHTS_HOLD`/authored TEST `[]` |
| Existing Core2A | Actual question attempt/support and before/after protected W |
| Existing Core2B | Changed condition and distinct transfer W |
| Prior asset evidence | PR/branch/exact SHA, package/manifest/figure blob, native page URLs/receipt and SHA-256, reused vs stale |
| Frozen comparator | Owner-approved fixture ID+commit; role-specific technique vs exact-source byte equality |
| Proposed change | One disposition per role, smallest source repair, concrete reproduced defect or reason not to change |
| Verification | Actual tests run/results; exact-head artifacts, structural/golden differential, preattempt AX and screenshot result |
| Governance | Independent qualified reviewer/COI, H/S/P/M details, Owner QRT decision, separate golden/rights/release state |

### Mapping decision tree

```text
Question supplied (verbatim, owned source, or a pinned TEST item)
    |
    +-> solve independently; distinguish fact, explanation, routine apply,
    |   original model, representation, dependent synthesis, proof
    |
    +-> learner X + demonstrated Y? (UNKNOWN is permissible)
    +-> Z safe bridge vs W protected decisive action
    +-> primary demand × five difficulty components -> 1 of 28
    |
    +-> search existing Core1/A/B truth and repair/transfer material
    +-> search source package/PR/render/receipt + immutable fixture
    |
    +-> an existing role *actually* satisfies that question need?
    |      YES -> REUSE_AS_IS with exact SHA
    |      NO  -> source defect? -> REPAIR_AUTHORED_SOURCE
    |             missing question-specific content? -> AUTHOR_MISSING_CONTENT
    |             missing official source custody? -> SOURCE_RIGHTS_HOLD
    |             proven unexpressible in current role contract?
    |               -> isolated BLUEPRINT/RENDERER change request and repro
    |
    +-> registered renderer + browser/AX/structural golden differential
    +-> independent 12-ask semantic review, qualified reviewer/COI, Owner ID
```

## Three real #203 decision lessons (historic TEST exemplars, not approved standards)

| Case / owner decision state | Verified issue-specific math/learner W | Incorrect first instinct | Correct decision |
| --- | --- | --- | --- |
| [MODEL-D4 draft #207](https://github.com/reallakshman19/Grade9v3.5/pull/207), Owner pending | Learner formulates inaccessible-courtyard correction in a table-edge chair model | Assume a literal preattempt `c`/formula leak from an issue summary; rewrite shared Blueprint | Inspect latest native Core2A and AX: H2 semantically cues inaccessible edges. `REPAIR_AUTHORED_SOURCE` and exact-head regression, preserve golden |
| [RETRIEVE-D4 draft #210](https://github.com/reallakshman19/Grade9v3.5/pull/210), Owner pending | Odd a is square modulo `2^k` for k>=3 iff `a≡1 mod8`; modulus4 exception | Assign `RETRIEVE-D4` only from a correct answer or band score | `AUTHOR_MISSING_CONTENT` using existing five roles; **hold classification** until there is actual evidence theorem was taught; otherwise reconsider APPLY/discovery or D3 |
| [SYNTHESIZE-D4 draft #210](https://github.com/reallakshman19/Grade9v3.5/pull/210), Owner pending | Use digits0,1,2,3,4,8 once for min multiple of4,9,11 (`120384`), then add7 (`130284`) | Treat 6/6 HTML hash matches and correct maths as W-safe across all roles | First native Core1A/B leaked decisive totals and winning answers; `REPAIR_AUTHORED_SOURCE`, inspect previous-role DOM/AX, then exact-head rerender. Do not change registered Core blueprints |

At #203 handoff, native TEST parity was **7/7**, five-role slot ordering matched the frozen Owner reference **35/35**, but that is not academic/QRT acceptance. [Draft review/benchmark PR #209](https://github.com/reallakshman19/Grade9v3.5/pull/209) records the raw artifacts, historic superseded ZIPs, comparator and unsigned review asks. Actual current heads/states must always be refreshed rather than copied from these examples.

## Smoke test for the agent (human/agent behavior check, not a substitute for CI)

Give the agent each prompt and examine its **first** response before it edits files.

- "Map question QRT-MODEL-D4 in #203 using the latest PR and exact native HTML." **Expected:** source/GitHub evidence, what preattempt H2 actually says, `REPAIR_AUTHORED_SOURCE` where reproduced; no newly invented shared Blueprint; Owner pending.
- "Make a RETRIEVE-D4 tile out of the odd-square modulo128 question." **Expected:** calls out proof and missing evidence of **previously taught** theorem, attempts QRT classification honestly, reuses five registered roles; does not certify D4 or create a seventh novel blueprint.
- "The SYNTHESIZE-D4 Core2A CI passes. Can we mark the cell accepted?" **Expected:** **No**. Search prior Core1A/B leak and latest exact-head repair; compare golden techniques, require independently signed H/S/P/M and Owner QRT decision.

**Acceptance test for this new agent:** if its first output is a blanket matrix progress table, a fresh blueprint design, a list of hint counts, or an academic pass inferred solely from rendering, the agent did **not** follow this playbook.

## How to activate

After the draft agent-definition PR is reviewed and merged into the repository default branch, use GitHub Copilot's custom-agent selector in VS Code or the GitHub agents interface and choose `qrt-blueprint-mapper`. Give it a real question/issue and existing learner evidence if known. It must fetch repository data and produce the question-to-asset map first. Merely committing the `.agent.md` file **does not launch a background worker or grant it reviewer/Owner powers**. External Github Copilot availability/configuration remains controlled by the account.
