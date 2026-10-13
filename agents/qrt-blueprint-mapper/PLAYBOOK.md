# QRT Blueprint Mapper — evidence-first operating playbook (v1)

This playbook is executable guidance for [the repository Copilot custom agent](../../.github/agents/qrt-blueprint-mapper.agent.md). It is **not** authority to accept QRT cells, rewrite Owner fixtures, use protected exam source, merge or publish.

## Before the first edit: the authority and evidence ladder

| What is known | Acceptable evidence | Never infer |
|---|---|---|
| The question is eligible for this activity | Authored TEST provenance or authorized real source inventory, rights/custody, current issue scope | “An olympiad-looking question is an official SOF question” |
| Question mathematics is correct | Independently worked oracle, alternative correct solutions, boundary counterexamples | Correct arithmetic implies correct primary cognitive demand |
| W is truly learner-owned | X/Y/Z/W and a preattempt *question-specific* leak audit in source and actual HTML | A locked H3 means H1/H2 are safe |
| A blueprint role is implemented | Existing registry contract, a source package and role selection, native renderer output | A visually similar HTML mock-up is a registered Core page |
| The golden technique is used | Named T01–T15 behavior and semantic/interaction comparison | Bytes of different questions should match an original golden |
| Technical output is verified | Exact-head artifact ZIP, six recomputed hashes, matched receipt, zero gaps, actual browser gates | Passing CI means the QRT cell is academically accepted |
| QRT status is accepted | Authorized Owner decision ID + qualified review / applicable *cell-specific* waiver | A seed-intake waiver or an author self-review grants QRT acceptance |

## The method that avoids rework

1. **Question dossier / source contract.** Record `question_id`, textual givens, any figure description, response modality, source license/custody, source Git blob and canonical original. Never silently improve an authentic stem while still labeling it verbatim original; amendments become explicitly authored practice.
2. **Solve without blueprints.** Calculate via one route, verify via another, list equivalent final methods and their units. For conceptual tasks, prove the rule and find a falsifying or boundary example. Test whether a “just the number” answer demonstrates the target demand. If not, specify the proof/mechanism/representation that **must** appear.
3. **QRT classification with contrastive counterfactuals.** Consult `Shared/quality/question-demand-matrix.v1.json` and `Shared/quality/question-demand-templates.v1.json`, locate the *primary* learner decision and its neighboring demands. Contrast bands D1–D4 rather than inheriting the current label. Write `X` (challenge), `Y` (known), `Z` (bridge), `W` (protected move) and a *competing explanation* for why another demand/band might be correct. Mark unresolved classification `ACADEMIC_PENDING`; do not self-promote an author label.
4. **Look up available registry roles.** Inspect current `Shared/web/interactive-page-blueprints.v1.json` and `Shared/tools/render_core.py`; select registered roles and versions. Basic five-role authored TEST layout:
   - **Core1:** orient to one prerequisite and the true question; T01/T14.
   - **Core1A:** construction of one inferential decision in a **different numeric/context case**, cumulative safe visual stages, concise anchor and new exit; T02/T03/T11.
   - **Core1B:** real learner misconception, concrete counterexample, reconstruction **with changed givens**, boundary that can falsify a copied procedure; T06/T10/T12.
   - **Core2A:** target independent problem, source-specific unsolved figure, H1→H2→H3, independent check; T04/T05/T07.
   - **Core2B:** genuine changed unknown, representation or inference direction, named invariant, closure built after the transfer; T08/T09.
   - **Core2:** only an authorized authentic source question with custody, true options/response form and separate key/readback; T13/T15. Omit CORE2 for synthetic TEST questions.
5. **Design backwards.** Start Core2B's truly changed decision and Core1A independent exit, then Core1B falsifying misconception, before authoring the Core2A hint ladder and the source diagram. Ask: “Would the learner solve the target with no new decision after the worked example?” If yes, redesign, not duplicate.
6. **Protect the protected move.** Build the hint/exposure matrix below and read it against *every* surface:

   | Surface | May provide | Must withhold before learner attempt |
   | --- | --- | --- |
   | Stem / original diagram | Stated givens and response format | Chosen model, correct category, sign, area-equality warrant, target result |
   | H1 | Clarify terminology and visible givens | The classification/model/warrant W |
   | H2 | Connect to prior learning with a **neutral question** | A decisive yes/no (“are BOTH copied?”), exact rule thresholds when retrieving that rule, a prechosen grouping |
   | H3 | Gated route/check after attempted response | Disclosure without nonblank commitment |
   | Core1A | Different worked example and legitimate prerequisite | Target numbers/result or identical disguised task |
   | Core1B | A false approach and repair with different givens | Target answer by copy-paste |
   | SVG / AX / print / hidden DOM | Accessible literal givens, progressive figure | Pre-marked conclusion in label/figure; content visible to learner before attempt |
   | Feedback | Clarified mathematical warrant and independent check **after attempt** | Unsupported claim that nonblank writing was graded as correct |

7. **Author as real data, not handcrafted HTML.** Use `Shared/library/package.schema.json` and repo manifests and tests as contract. Stage SVG groups cumulatively; do not redraw entire diagrams across stages. Ensure new figures are source-aligned, text legible at *scaled* viewport, AX label carries the givens (source SVG `<desc>` might not survive native rendering), text-only access when diagram unavailable. Test the actual browser disclosure behavior, not grep alone.
8. **Native render and proof.** Example invocation for a source-safe package (substitute exact paths):
   ```bash
   python Shared/tools/render_core.py build \
     --manifest TEST/products/imo182-qrt-d1-justify.manifest.json \
     --out build/qrt-check/justify --draft --reference
   ```
   Independently SHA-256 **core1.html, core1a.html, core1b.html, core2a.html, core2b.html, index.html**, assert exact equality with `render-receipt.json["page_sha256"]`, assert `gaps=[]`, confirm correct blueprint refs. If a different set of roles is legitimately selected, verify **every emitted page** and name the exception. **No hand-authored substitute renderer**.
9. **Browser interaction QA.** With Playwright/Chromium or equivalent actual browser, load local rendered pages. Test 390, 768, 1366 CSS px; count runtime errors and overflow; inspect figure stage 1→2→3, keyboard/AX labels, displayed math and units. For Core2A: no attempt → H3/solution locked, blank commit → still locked, nonblank commit → eligible reveal. H1/H2 may be opt-in; check their wording *after clicking*. A source document can contain protected solution text without the browser showing it, and a source can also leak it through a supposedly harmless H2. Both require real behavior measurement.
10. **Golden / original distinction.** Read `golden/INDEX.md`, `golden/TECHNIQUES.md` and the active Owner designation issue. `G-IMO-G9-FIVE-CORE-20261012` was Owner-designated with a frozen same-source comparator. Its separate-question use is **semantic technique comparison** only, not identical SHA; `G-IMO-CORE2-UI-R1` is UI-only. A new golden is a *candidate* until Owner approval; do not mutate snapshot locks or designate successors.
11. **Gate-by-gate disposition and conservative patch.** Classify a defect as `INPUT`, `SOURCE_RIGHTS`, `MATHEMATICS`, `ACADEMIC_DEMAND`, `RENDERER`, `BLUEPRINT`, `ORACLE`, `VIEWER`, or `REPOSITORY_BASELINE`. Fix source-local hint, figure, rubric or test first. Prove registry/renderer gap with unchanged valid source and measured failure before proposing global code. Broad CI that also fails on main requires **exact finding ID** comparison; do not suppress gates or assert full equivalence from equal red labels.
12. **Review and authority.** Write the evidence card before a review PR. Record all 12 H/S/P/M probes with clear observed/unknown separation. Reviewer identity/COI, independent academic verdict, alternate-band challenge, QRT Owner decision ID, source quality hold, rights and learner publish controls remain unsigned/unaccepted until actual human authorization. A research-intake waiver must not be repurposed as QRT waiver.

## Deliverable: mapping card, not a screenshot

Start from `agents/qrt-blueprint-mapper/EVIDENCE.template.json`. Create one file per question/cell under the appropriate TEST review path, with fields:

- `question`: provenance, source SHA and source classification; protected source details only in authorized places.
- `qrt`: primary/secondary demand, D1–D4 hypothesis, X/Y/Z/W and alternative primary/band argument.
- `role_mapping`: intended learner work per existing Core role, named frozen T01–T15 oracles, what **changes** from one role to another.
- `evidence`: latest source/manifest/registry blobs, exact source-committed renderer CI and genuine artifact, six HTML digests/receipt equality, golden comparator mode, measured browser QA.
- `review`: the twelve question-specific H/S/P/M rows, author-side results separate from independent academic verdicts, human quality holds and pending Owner decisions.
- `changes`: necessary file-level changes and **why the existing blueprint was sufficient or truly insufficient**.

If no code is required, issue a review-only packet. If the code path exists in an unmerged draft, link that *exact head* and never present it as main/released. Preserve minimal test reproducibility.

## Useful living references — verify before trusting

- `Shared/web/interactive-page-blueprints.v1.json` — source of truth for registered role IDs and versions.
- `Shared/quality/question-demand-matrix.v1.json` and `Shared/quality/question-demand-templates.v1.json` — QRT classification and the 12 review semantics.
- `golden/INDEX.md`, `golden/TECHNIQUES.md`, `golden/units/G-IMO-G9-FIVE-CORE-20261012/` — role technique and Owner lock; frozen source differs from new test cases.
- `Shared/tools/render_core.py` and `Shared/library/package.schema.json` — **sole** page renderer and source data contract.
- Issue [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182) and [#200](https://github.com/reallakshman19/Grade9v3.5/issues/200), source-specific draft PRs [#204](https://github.com/reallakshman19/Grade9v3.5/pull/204), [#206](https://github.com/reallakshman19/Grade9v3.5/pull/206), [#208](https://github.com/reallakshman19/Grade9v3.5/pull/208), [#212](https://github.com/reallakshman19/Grade9v3.5/pull/212), [#213](https://github.com/reallakshman19/Grade9v3.5/pull/213) — **historical examples**, not automatic merge or QRT approval.
- `TEST/imo-research/qrt-tiles/q003-model-d2/index.html` and `TEST/imo-research/qrt-tiles/d1/` may exist on a *separate unmerged review branch*. Do not assume they exist on main; discover refs and use actual sources. No Q003 confidential content.

## What the agent should say when the right next move is review, not code

> “The existing blueprint maps these steps and the actual native HTML has no demonstrated missing role. Mathematics is verified. The remaining uncertainty is **whether W makes this SYNTHESIZE-D1 rather than MODEL-D1**. I have prepared the alternate-demand challenge and real six-page technical evidence; only the qualified reviewer/Owner can decide the classification. I will not add a new blueprint or manufacture acceptance.”

This refusal to overbuild is a *successful* completion of the agent's task.
