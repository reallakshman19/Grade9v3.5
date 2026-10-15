# QRT249 — Dedicated Standalone Repair Helper Execution Prompt

## Your assignment

You are the **independent coding helper for the Grade 9 IMO research standalone suite**. Your task is to make the source PR's real learner-facing standalone HTML safe and mathematically coherent, without becoming another validator, changing the shared education architecture or granting any academic/release decision. **Start now; do not wait for all 260 academic audits.**

Single process orientation (read once first): https://github.com/reallakshman19/Grade9v3.5/blob/main/conceptmap.md

- Work order: https://github.com/reallakshman19/Grade9v3.5/issues/254
- Owner aim: https://github.com/reallakshman19/Grade9v3.5/issues/249
- Source PR: https://github.com/reallakshman19/Grade9v3.5/pull/240
- Independent validator PR: https://github.com/reallakshman19/Grade9v3.5/pull/250
- Coding method: https://github.com/reallakshman19/Common/tree/main/skills/engineering-pr-delivery-v3.6

Source PR #240 was last independently pinned at commit **27a35c50b0e976b6f6112fc953aec5445f078caf**, branch **feat/imo-grade9-68-questions-master-suite**, DRAFT/unmerged. Validator PR #250 last head: **7dc6b653ead8dcf471906a3188916b1881b37e6c**. **Verify the live heads again before beginning.** These are source receipts, not forever-fixed assumptions.

## 1. Vertical split — what I give you, what you own

**Independent validation workstream (my responsibility):**
- Supplies source-safe exact-head defect evidence, the 28-cell QRT semantic framework, the known failing cases and a frozen pass/fail interface.
- Owns three READ-ONLY validator tools currently on PR #250: Shared/tools/imo_qrt_validator.py; Shared/tools/imo_qrt_standalone_gate.py; Shared/tools/imo_qrt_canonical_evidence.py.
- Owns all their synthetic mutation tests, benchmark rules, independent revalidation and PASS/FAIL/HOLD recommendation. I do **not** edit your research source, generator, concept records, SVGs or generated HTML.
- Will inspect one frozen repair PR head, not provide a succession of per-item approvals. I do not grant Owner QRT acceptance, source rights, publication or release.

**Independent helper (your exclusive implementation responsibility):**
- Own Mathematics/research/build_full_master_suite.py and source-side tests.
- Own authorized changes to the six research-bank records, authored academic hints/solutions/crux, necessary concept Core1A/1B packages and research figure assets.
- Own the FOUR checked-in standalone HTML outputs, reproducible actual generator rebuild, exact-head browser checks and SHA-256 receipts.
- Deliver ONE source-correct repair PR targeting the current **source PR #240 feature branch** (NOT main). Make all four HTML files actually change and verify them inside that branch after an authorized independent-reviewed integration.
- DO NOT modify the independent validator code/tests to get a passing verdict, do not invent new QRT/Blueprint engines, do not silently change original source material, and do not modify frozen goldens.

**Interface:** I supply numbered findings + scope + oracle + evidence; you supply corrected exact source files + 4 HTML artifacts + tests + receipts + academic HOLD ledger; I perform one independent revalidation. **No chat-by-chat back-and-forth or overlapping file writers.**

## 2. Start with actual source and record lineage

PR #240's research suite has **260 unique question IDs in six files**, with 19 of 28 declared QRT tiles occupied. Its larger research population is NOT the distinct **68 frozen authentic question identities** governed for product admission. Avoid silently transferring research fields, options, paper rights or scores into original product Core2.

On the pinned live source branch, inspect:
- Mathematics/question-bank/sof-imo-2023-24-set-a.core2.json
- Mathematics/question-bank/sof-imo-2024-25-set-b.core2.json
- Mathematics/question-bank/sof-imo-2025-26-set-a.core2.json
- Mathematics/question-bank/sof-imo-2025-26-set-b.core2.json
- Mathematics/question-bank/sof-imo-hots-olympiad-expansion.core2.json
- Mathematics/question-bank/sof-imo-sample-2026-27.core2.json
- Mathematics/research/visual_cues_manifest.json
- Mathematics/library/figures/
- Mathematics/units/ (14 research topic directories)
- Mathematics/research/build_full_master_suite.py

Track question ID, exact original-source lineage, original stem/options/figures/answer provenance, authored support, current five-factor difficulty, and exact file/commit hashes. Protect copyrighted source text: GitHub issue comments should cite IDs, problem categories and paths, not reproduce the original exam materials.

## 3. How to use QRT and Blueprints correctly

**QRT is the semantic contract. Reuse, do not reimplement:**
- Shared/tools/question_review_matrix.py: resolve_review, specialize_resolution, X/Y/Z/W, canonical H1–M3 questions.
- Shared/tools/question_difficulty.py: five-factor score and D1–D4 derivation.
- Shared/quality/question-demand-matrix.v1.json and question-demand-templates.v1.json.
- Shared/vocabularies/cognitive-demand.v1.json.
- Mathematics/adapter/DemandReview.json and Mathematics/adapter/QualityVocabulary.json.
- tests/test_question_review_matrix.py (self-authored synthetic canonical resolver examples).

For each changed record, justify one actual first decisive learner-owned act and primary demand among RETRIEVE, EXPLAIN, APPLY, MODEL, REPRESENT, SYNTHESIZE, JUSTIFY. Derive difficulty from 5 genuine factor values plus explanation, not a HOTS label, title keyword or HTML styling. Preserve the protected learner work W and the intent of the H/S/P/M support sequence. The research JSON does not itself satisfy native reasoning_route/crux_move_ref, mastery profile or Core binding fields; NEVER fabricate those to claim admission.

**Blueprints govern Core page structure and behavior; they do NOT certify mathematics:**
- Registry: Shared/web/interactive-page-blueprints.v1.json (verified v1.17.0).
- Validator: Shared/tools/web_blueprint_contract.py.
- Sole native renderer: Shared/tools/render_core.py.
- Relevant refs: BP-CORE2-SOURCE-QUESTION@1.11.0; BP-CORE1A-CONSTRUCTION@1.8.0; BP-CORE1B-RECONSTRUCTION@1.1.0; BP-CORE1-ORIENTATION@1.1.0; BP-CORE2A-SUPPORTED-APPLICATION@1.1.0; BP-CORE2B-TRANSFER@1.1.0.

Use the **Core2 source-question Blueprint intent** to check the research portal: faithful source/option identity; visible attempt first; meaningful commitment; properly staged hints; the full teacher solution only after that commitment; an independent mathematical check. The current research HTML is generated by a separate existing research builder, NOT by render_core.py; do not mislabel it native product or hand-copy golden HTML into the generator. For actual native Core records, the only allowed learner renderer remains render_core.py.

Core1A must teach the actual concept/inference for that question, with meaningful construction, staged representation if useful, worked anchor and a new independent exit. Core1B must reconstruct and diagnose/repair, not clone Core1A or disclose protected reasoning. Core2A supported practice and Core2B changed-demand transfer are distinct. Reuse lessons only when the decisive concept AND learner decision and prerequisites match, not merely the chapter heading. You do not need 28 new Blueprints.

### Fixture hierarchy: use only the approved scope of each

1. **Owner-approved IMO Core2 visual/interaction reference:** golden/units/G-IMO-CORE2-UI-R1/GOLDEN.md at immutable commit c16e8bdb41c84a9d392d742a68fc4a860f099897, with core2_authored_demo.html and reference-fixture.v1.json. Use its attempt-first layout, source band, staged hint interaction, concept navigation, and deliberate post-commit answer reveal as design guidance. It is **hand-authored reference HTML**, NOT a native rendered product or math/source-rights approval. Its core1a_authored_preview.html is NOT a universally approved Core1A golden.
2. **Owner-designated five-Core exact HTML snapshot:** golden/units/G-IMO-G9-FIVE-CORE-20261012/GOLDEN.md at immutable commit 67c34dababb0da0ef7d5f4a532bfcf3119754961, plus snapshots/, snapshot-lock.json, manifest.json and records.json. Benchmark Core1, Core1A, Core1B, Core2A, Core2B structure ONLY. Check with: python Shared/tools/build_golden.py --id G-IMO-G9-FIVE-CORE-20261012 --check . Do NOT change locked snapshot bytes; not authentic Core2/rights/QRT acceptance.
3. **Core2 method CANDIDATE:** golden/units/G-CORE2-R2/GOLDEN.md and its manifest. Build for inspection with: python Shared/tools/build_golden.py --id G-CORE2-R2 . This illustrates hint staging and typed commit, but is NOT Owner-blessed.
4. **Concept construction method CANDIDATE:** golden/units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md and its manifest. Build for inspection with: python Shared/tools/build_golden.py --id G-MATH-LINEAR-CONSTRAINT . It illustrates construction, diagnostic, boundary/changed-given exit; not Owner-blessed or transferable math.
5. **Golden index and techniques:** golden/INDEX.md and golden/TECHNIQUES.md. Use T01 attempt first, T02 one real construction decision, T03/04 question-grounded figures, T05 progressive non-spoiling hints, T06/T10/T12 reconstruction and boundary checks, T07 independent verification, T13 original key versus independent result, T15 faithful source option order/response type. These are teaching moves, not fields to fill for a count.

Never promote a golden candidate to Owner-approved, change a golden snapshot, clone its maths, or assert an exact HTML match proves mathematical validity.

## 4. Fix the P0 learner-facing defect first — all 260 cards

At PR #240's baseline generator, all **260/260** rendered questions have each of these:
- PREATTEMPT_CORRECT_OPTION_EMPHASIZED: is_correct/correct_style initially paints the known right choice green (builder near lines 2422–2427).
- PREATTEMPT_ANSWER_IN_VISIBLE_SOLUTION_SUMMARY: the solution's native details summary visibly says Answer: (letter) before a student's attempt (near 2540–2544).
- SOLUTION_DIRECTLY_OPENABLE_BEFORE_ATTEMPT: closing a details body does NOT stop a user opening it directly, bypassing the Commit Attempt button.

Independent exact-head falsifier: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38616372230 . Its synthetic tests were green precisely because they detected this **FAILED real HTML**.

**P0 done conditions:**
1. Four answer options render neutrally before learner commitment (no selected/success styles, answer-carrying data attributes, aria text, tooltip, search text or default checked state).
2. All visible solution summaries are neutral. Do not cosmetically CSS-hide a still present answer letter.
3. Before meaningful nonempty attempt commitment, the solution panel is genuinely hidden and not focus/click openable. After commitment, allow a clearly labeled intentional reveal, keyboard/accessibility operation and reasonable focus/state. Empty notes do not count. HTML devtools secrecy is not achievable; protect actual normal learner UI.
4. Hints, distractor guidance, crux banners, figures/SVG descriptions and navigation/search must not leak W either. Do not merely relocate the answer.
5. Test early and late cards, 260/260 coverage, reload/filter/tab switching, phone/tablet layout and actual JavaScript runtime. This is a real source-template/interaction fix, not 260 copied question edits.

## 5. Academic corrections and what must remain HOLD

**HOTS Q046:** stem flow speed 0.35 m/s; authored hint and derivation incorrectly use 3.5 m/s before a self-correction. The recorded final 85.71 minutes is correct. Fix hint/derivation with independent units/rate checks and correct the crux claiming half the hemisphere when the task fills the entire tank. Do not rewrite original source wording without source authority.

**HOTS Q024:** the arbitrary five-point-star proof lacks a general figure-grounded justification; a regular star sanity check is not a proof. Supply a rigorous warrant or HOLD awaiting academic/source review.

**HOTS Q035:** currently SYNTHESIZE-D4 despite apparent direct Ptolemy substitution. Independently review actual demand/band with five-factor evidence; do not relabel automatically.

**Whole suite intake:** 27 five-factor score mismatches, six band mismatches, one invalid component, 50 HOTS records lacking components; investigate per ID. These are **evidence defects, not permission for a mechanical 260-question mass rewrite**. Mark unresolved academic claims REVIEW_REQUIRED. Figure reference tests (including tests/test_imo_figure_reference_resolution.py) validate path safety, NOT original diagram correctness. Maintain source/copyright rights HOLD and **0 automatic Owner QRT acceptances**.

## 6. The deliverable is updated standalone HTML inside source PR #240

From your separately created branch based on the LIVE #240 feature head, run the existing real builder from repository root:

    python Mathematics/research/build_full_master_suite.py

Commit **all FOUR** generated files alongside the generator and tests:
- standalone/mathematics-imo-grade9-master-suite.html
- public/standalone/mathematics-imo-grade9-master-suite.html
- public/test/imo-grade9/core2.html
- docs/test/imo-grade9/core2.html

Verify all four have 260 unique IDs, consistent declared QRT occupancy (currently 19 cells unless independently justified correction), **identical SHA-256**, functioning multi-tab Core1 navigation, no stale original bytes and no math/font regression. Example checks:

    git rev-parse HEAD
    sha256sum standalone/mathematics-imo-grade9-master-suite.html public/standalone/mathematics-imo-grade9-master-suite.html public/test/imo-grade9/core2.html docs/test/imo-grade9/core2.html
    python -m unittest discover -s tests -p 'test_imo_*.py'

**External independent validator use, without edits:** Pin a separate checkout of PR #250 and run its Shared/tools/imo_qrt_standalone_gate.py with --root pointing at YOUR source checkout, --baseline-sha pointing at YOUR checked-out 40-character source commit and --output pointing to a build evidence file. Expect zero on all three named disclosure findings, four identical output hashes and REVISED structural result REVIEW_REQUIRED. That still does not grant academic clearance. Do not cherry-pick changes to validator rules into your content PR.

Run applicable source figure tests, QRT matrix tests, build determinism and author synthetic regression cases that reproduce the three leaks on uncorrected code. Test Chromium at 320, 390, 768, 1280 px: fresh question, empty commitment, meaningful typed attempt, hints, solution reveal, keyboard focus, tab/filter and reload. If unable to execute genuine browser tests, record NOT_RUN rather than PASS.

## 7. Exact implementation and handback sequence — no ping-pong

**R0 Baseline:** Verify live PR #240 head, issue #254 and source code; pin file blobs and receipt counts; create a new isolated repair branch from #240 HEAD. Open a **DRAFT repair PR with base branch feat/imo-grade9-68-questions-master-suite**. Re-GET verify base/head; NEVER create a PR targeting main.

**R1 Learner leak:** Add source-side negative tests, repair the builder and attempt-first behavior, regenerate four outputs and prove 260/260 × all three leak conditions now **ZERO**.

**R2 Academic evidence:** Fix justified authored content errors, including Q046; investigate Q024/Q035 and the 27/6/1/50 evidence queue. Preserve original source identity and log unresolved academic/rights Holds. Avoid broad relabeling.

**R3 Contract/fixture alignment:** Check QRT classification with canonical engine, Core1A/B concept-specific behavior and applicable fixture scopes; use Blueprint contracts to prevent structural drift. Do not fork render_core.py or overwrite goldens.

**R4 Reproducible outputs:** Build again; independently count IDs/tiles and compare four HTML SHA-256s. Execute source unit tests, external gate, Chromium/keyboard/Math/font/figure checks at exact HEAD. Report commands, logs, artifact URLs and any NOT_RUN.

**R5 One frozen handback:** Post a complete source-safe table on issue #254 and your DRAFT repair PR: base and head SHA, changed files, four HTML hashes, 260 IDs, QRT tile counts, three before/after leak counts, fixed question IDs, academic HOLD IDs, test/CI/browser receipts, source-rights and golden status. **STOP editing the PR and request one independent validator review.** No back-and-forth on every question. Any necessary rework after that review is one bounded correction, not an open-ended loop.

Only after independent verification and required approval may the repair PR be merged into **#240's source feature branch**, thereby updating #240's generator and four HTML blobs. Verify the resulting new PR #240 head and exact files by GET. Do not merge source PR #240 into main, release exam content, promote golden fixtures, or grant QRT/source-rights acceptance.

## 8. Required final return from you

Return a compact, self-contained handback containing:
- Repair PR link, exact BASE/HEAD commit SHAs and confirmation it targets #240's branch.
- P0 root cause and fixed code locations, 260/260 zero-disclosure evidence.
- Actual four generated HTML SHA-256s with byte parity proof and source builder command.
- Evidence-backed per-question academic fixes versus unresolved HOLD decisions.
- QRT demand/five-factor/Blueprint/Golden comparison method and exact fixture references used.
- Real tests and browser/keyboard results with links, plus NOT_RUN or remaining blockers.
- Explicit status: **CANDIDATE FOR INDEPENDENT REVALIDATION, NOT OWNER-ACCEPTED OR RELEASED**.

The validation workstream will then conduct one exact-head independent revalidation. Do not mark this task complete because a PR exists: success requires verified **source changes + all four rebuilt HTML outputs + evidence + clean handback**.
