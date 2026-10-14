# IMO #182 · Agent A implementation plan: D1–D4 QRT × registered Core blueprints × existing goldens
**Date:** 14 October 2026 · **Mode:** implementation work order, not Owner acceptance · **Authority:** Common/main \`relay/AIM/IMO-CORE-BLUEPRINTS.yaml\` v3.1.0, label SHA \`2ff9246\`, blob \`5c8457bdef4a7019c29f90668fe3b51118a4a7ff\`.
**Owning programme:** [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182) · D1 [#200](https://github.com/reallakshman19/Grade9v3.5/issues/200), D2 [#201](https://github.com/reallakshman19/Grade9v3.5/issues/201), D3 [#202](https://github.com/reallakshman19/Grade9v3.5/issues/202)/[#217](https://github.com/reallakshman19/Grade9v3.5/issues/217), D4 [#203](https://github.com/reallakshman19/Grade9v3.5/issues/203).
**Existing takeover:** [Common Tab8 G1 r7](https://github.com/reallakshman19/Common/blob/0b7ccdf9edb9c888fa959e4459969da4958e9c69/coordination/Session_Oct09/Tab8_imo_182_integrator/plans/2026-10-14-g1-r7-d1-d4-cross-band-takeover.md). This extends that plan's substantive Core/fixture implementation order, not a competing 28-question authoring project or authority to edit another author's open PR.

## Executive decision: where to start now

**Start with a complete native-five-Core, role-specific golden *semantic* benchmark for one strong existing authored cell, \`QRT-EXPLAIN-D3\`, before touching shared code.** Reuse its already registered manifest/source and already green Core1A/Core1B/Core2B owner-golden technique witnesses. Complete the still-open Core1 orientation role, inspect Core2A reasoning/H2→H3 and both staged Core2A/Core2B SVG accessible names, then record all five role outcomes \`MATCH | CONTEXTUAL_DIFFERENCE | DEFECT | JUSTIFIED_NA\`. A generic stage label \`Stage 1\` is a known *authored metadata* issue; the renderer intentionally strips potentially answer-bearing whole-figure title/desc pre-attempt. Have the D3 author + protected-W reviewer choose **safe, descriptive authored \`reveal_stages[].label\`** values, not a universal renderer bypass. Re-render the entire five-role package and compare to frozen golden *techniques*. Do not count this pilot as independently qualified QRT approval or build a replacement golden.

**Why this cell first:** In #224, existing native O1 evidence already covers Core1A construction, Core1B reconstruction and Core2B changed-case attempt gates. The unresolved accessible figure stage label is a falsifiable actual learner defect. An immediate benchmark closes the untested Core1 role and checks the Core2A role, delivering meaningful O1 progress using current blueprints. It is lower-risk than modifying the D4 RETRIEVE original theorem hold, and it exposes the review protocol needed for 27 other cells. Respect the Owner task aim “Core2A done structurally, Core1A next, then 1B”: begin with **Core1A concept construction and independent exit** in the pilot's semantic comparison, then Core1B changed reconstruction, not a mass role-HTML count.

In parallel, route D1 #244's \`TABLE_OF_VALUES\`/typed-oracle generic contract and 40 new immediate-base test failures to its module owner. It is a **separate proposed TEST Core1A divisibility contract**, not the main answer to whether the D1 band's seven authored QRT learner journeys match blueprints/goldens; do not stop safe page-level semantic review while full CI stays red.

## 1. Source of truth and immutable authority

| Layer | Current exact source | Authority and comparison semantics |
|---|---|---|
| AIM O1/O2/O3 | Common \`relay/AIM/IMO-CORE-BLUEPRINTS.yaml\` v3.1.0 / 2ff9246 | O1 registered blueprint-generated golden-matching pages; O2 each named QRT cell needs accepted decision; O3 only a demonstrated golden-revealed blueprint gap |
| QRT demand and band | \`Shared/quality/question-demand-matrix.v1.json\`, \`docs/method/QUESTION-REVIEW-MATRIX.md\` | Exactly seven primary demands × four bands; X/Y/Z/W; five individually scored difficulty factors; 12 H/S/P/M semantic questions; never a new page template |
| Core blueprints | \`Shared/web/interactive-page-blueprints.v1.json\` registry v1.17.0, blob \`591ba061b8771c30fdffc4506aa720ca9ba89335\` | Reuse registered shape, disclosure and slot/component policy; preserve renderer \`Shared/tools/render_core.py\`; do not clone 28 blueprints |
| **Owner exact five-Core snapshot** | \`golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json\` blob \`888678554c41257e6d96c802f0009983ccbb5328\`; fixture source \`f87d2f6\`, frozen at #189 \`6307e5d\` | OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT **only for original five TEST pages**. Immutable bytes/digests; benchmark **role-specific semantic teaching behavior** on other questions. Lock has 5 SHA-256s and \`not_approved\` explicitly includes independent QRT, successor H3, rights and release |
| Candidate math technique library | \`golden/INDEX.md\`, \`golden/TECHNIQUES.md\`, \`G-MATH-LINEAR-CONSTRAINT/GOLDEN.md\` | Technique examples T01–T15; **CANDIDATE, Owner blessing none**; not accepted learner product |
| Candidate Core2 source method | \`G-CORE2-R2/GOLDEN.md\` | CANDIDATE Physics/JEE source question/hint technique; no implied IMO source custody |
| Owner **IMO Core2 UI reference** | \`G-IMO-CORE2-UI-R1/GOLDEN.md\` at \`c16e8bdb41c84a9d392d742a68fc4a860f099897\`, demo SHA \`90fa27ec...\` | Owner-approved authored Core2 visual/interaction example **only**; its Core1A companion preview expressly not universal/Owner-approved. Not a native original learner page |
| Exact Track A TEST evidence | #230 \`TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json\` | 28 authored TEST IDs, 168 independently checksum-confirmed HTML digests, 140 structural role slot matches; 8 elevated holds, semantic golden verdict \`UNREVIEWED\` throughout, no qualified reviewer/Owner acceptance |
| Authentic IMO originals | #183 / #218 | **Track B only**, 68 immutable source positions, original Core2 admitted 0/68, rights not granted; outside this implementation workpack |

**Exact role fixture check:** Before changing any source, re-fetch all five original snapshots and the lock; assert preserved SHA and expected role/slot/block sequences. Owner original exact snapshot data:
- \`core1.html\` SHA \`f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e\` — \`BP-CORE1-ORIENTATION@1.1.0\`, two role slots: identity/orientation.
- \`core1a.html\` SHA \`c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004\` — \`BP-CORE1A-CONSTRUCTION@1.8.0\`, identity/construction/repair_closure (renderer fixture includes repeated repair_closure slot).
- \`core1b.html\` SHA \`3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562\` — \`BP-CORE1B-RECONSTRUCTION@1.1.0\`, identity/attempt/reconstruction.
- \`core2a.html\` SHA \`e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777\` — \`BP-CORE2A-SUPPORTED-APPLICATION@1.1.0\`, identity/attempt/reasoning/support.
- \`core2b.html\` SHA \`91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39\` — \`BP-CORE2B-TRANSFER@1.1.0\`, identity/attempt/post_attempt.

**Do not confuse:** original five role snapshot SHA equality with another question's native SHA. Snapshot integrity and cross-question teaching-technique comparison are different tests. \`build_golden.py --check\` can pass for structure with a different embedded authority digest, so preserve the original lock as the exact-byte oracle.

## 2. Meaningful O1 implementation contract per Core (five-role testcase x 28)

| Core | Existing registered blueprint / essential slots | Specific learner and golden-technique test | Existing evidence / remaining gap |
|---|---|---|---|
| **Core1 orientation** | \`BP-CORE1-ORIENTATION@1.1.0\`; identity → orientation; original golden has scope, hard transition, representation bridge, governing relation, compact anchor, exit prompt | T14 prerequisite X→Y only where Y **DEMONSTRATED**, avoid fully teaching question-specific W; named exclusions, transition, no source-answer leakage; relevant learner exits, semantic match vs original Core1 | D4 RETRIEVE real Core1 golden/Chromium proof in #242; D3 EXPLAIN **Core1 O1 benchmark to complete**; structural 5/5 slots elsewhere is insufficient |
| **Core1A construction** | \`BP-CORE1A-CONSTRUCTION@1.8.0\`; identity/construction/repair_closure; required construction, key step, exit recall; staged visual and worked anchor per question when useful | T02 single inferential decision, T03 safe progressive representation, T11 compact worked anchor, correct maths, actual misconception repair and **independent changed numbers/condition exit**; distinguish teaching a concept here from disclosing later Core2A W early | D3 EXPLAIN source-specific real native Core1A golden proof; D4 RETRIEVE prior version leaked complete iff criterion in Core1A even when hashes matched. D1 #244 TABLE_OF_VALUES PROPOSED, not a rendered/accepted Core1A scene |
| **Core1B reconstruction** | \`BP-CORE1B-RECONSTRUCTION@1.1.0\`; identity/attempt/reconstruction | T06 diagnose tempting wrong route, T10 challenge boundary, T12 new givens rather than restate Core1A; blank commitment does not reveal main or separate boundary response; reconstruct/repair accurate maths | AIM names preexisting Core1B golden, but that does NOT certify 28 role pages. D3 EXPLAIN separate attempts were tested; recheck cross-role dependent answer leakage |
| **Core2A supported application** | \`BP-CORE2A-SUPPORTED-APPLICATION@1.1.0\`; identity/attempt/reasoning/support | T05 useful hint progression, T07 independent check, X→Y then H3 **after substantive attempt** where W would be handed over, H2 never supplies final model/theorem; real DOM/AX and source-vs-authored support labels | Existing structural O1 proof, D2 seven-current native checks; D3 EXPLAIN graph preattempt safe but generic “Stage 1” AX label; D4 RETRIEVE former H2 leakage example is counter-test |
| **Core2B changed-case transfer** | \`BP-CORE2B-TRANSFER@1.1.0\`; identity/attempt/post_attempt | T08 closure depends on final transfer case; T09 invariant vs changed decision, \`transfer.protected_move_ref\`; separate attempt and answer reveal, postattempt new warrant and independent transfer verification | D3 EXPLAIN current #224 native/golden success with changed \`sqrt(t+5)=|t-1|\`; D4 RETRIEVE #242 modulus 128→4 independent test; still need specialist check on actual W and misleading AX/copy |
| **Authentic Core2 (not a sixth TEST role)** | \`BP-CORE2-SOURCE-QUESTION@1.11.0\`, identity/attempt/representation/support/solution | Original source fidelity, learner commitment, separate printed-key vs independent reasoning, correct option response, Owner IMO UI-only comparator | #183 source custody and rights gates; do not fill \`selection.core2\` in authored TEST manifests or claim 68 originals implemented |

**Core1B is already structurally registered and golden-covered.** Reusing it still requires source-specific evidence, not a second Core1B blueprint. **No O3 blueprint change is planned initially.** An input defect, role projection bug, AX label, unsafe authored hint, wrong golden oracle or stale provenance is not by itself an unexpressible blueprint limitation.

## 3. Complete 7×4 D1–D4 backlog — concrete learner work and next disposition

Key: **H = elevated source/educational hold, not adoptable until independent resolution**; **R = remaining semantic/golden review**, not a passed academic verdict. Each action uses the existing one TEST source+manifest and five Core roles, not new question writing by default.

| Cognitive demand | D1 — preserve one learner decision | D2 — preserve choice/link plus execution | D3 — preserve dependency bridge | D4 — preserve decisive exception/strategy |
|---|---|---|---|---|
| **RETRIEVE** | R: divisor-25 defining criterion versus familiar but false odd→prime; H2 and Core1 anchor may not select W | **H:** right-triangle diagonal route: method is provided, compare APPLY primary and D1/D2 band (#211) | **H:** diagonal-square classification already cues applicability, compare APPLY-D2; revise authoring only on evidence (#217) | **H:** odd-square iff property; Y=UNKNOWN full theorem mastery; maintain clean #219/#242 and reject leaky zip; test if RETRIEVE truly primary (#234) |
| **EXPLAIN** | R: two-odd-leftovers mechanism, not restatement | R: exponent factors multiply, challenge whether explanation/connection is learner-created (#214) | **PILOT R:** signed-root loss on squaring, source-safe explanatory staged AX label + independent Core1/2A golden benchmark (#217/#224) | R: parity exception in cyclic digit rotation; independent changed mechanism/counterexample |
| **APPLY** | R: rectangle area 7×4, units cm² and inverse check | R: two-stage discount second-base already named; D1-vs-D2 decision (#214) | R: prime-valuation thresholds n²/n³, applicability and changed thresholds | R: compatible CRT phase before interval, exceptions and boundary |
| **MODEL** | **H:** six equal groups of four pre-cued; verify learner selects model and Core1A does not hand it over | **H:** corrected #245 gives either small or large count variable; verify MODEL vs APPLY, W/H2 and actual Core1A→Core2A continuity (#211) | **H:** shared positive power/offset multiplier explicitly suggested; author-source repair or reclassify before new clean adoption (#217) | R: courtyard accessible-perimeter correction, test earlier H2/source cue and D3/D4 strategy |
| **REPRESENT** | R: directional translation to signed coordinate pair with reverse check | R: shaded grid asks nonoverlapping rectangles up front; inspect mapping choice and SVG/AX (#214) | R: route-set intersection and overlap, valid reversible representation | R: domino adjacency invariant, local black/white shortage not supplied in hint |
| **SYNTHESIZE** | **H:** paired motif may simply execute a known formula/arrangement; compare APPLY/MODEL and D1/D2 | R: greatest candidate after named divisibility tests, genuinely dependent ordering vs APPLY (#214) | R: AP + digit constraints + divisibility, adopt only current TWO-field corrected #224 source; previous #193/#221 interim closures quarantined | R: alternating-position dependent bridge, test Core1A/B earlier answer leakage and full Core2B changed case |
| **JUSTIFY** | **H:** perpendicular baseline/altitude wording and learner-written warrant, not numeric verification only | R: offset triple independent proof; worked example may already supply the key universal factor (#214) | R: necessity/sufficiency triple product modular proof and falsifying converse | R: two obstruction exclusions + constructive sufficiency in new D4 scenario |

### Band execution tickets (not four new implementations)

**D1 #200 — repair three holds, then seven role-semantic rows.** Reuse current corrected TEST packages (#204/#206/#212/#213) and #208 tiles; retire old H2-leaking zips. Produce reviewer-ready MODEL-D1, SYNTHESIZE-D1 and JUSTIFY-D1 source/W/rival dossiers; keep four ordinary rows on independent audit. D1 #238/#244 is a **separate Core1A divisibility TEST contract dependency**: module owner must decide typed data/exit-oracle and proposed \`TABLE_OF_VALUES\`; no automatic renderer support. Current #244 immediate-base regression report: 40 NEW/2 FIXED/149 PERSISTENT exact test IDs; isolate cause instead of broad patching in this workpack.

**D2 #201 — fix classification, not rerender for its own sake.** Seven native authored candidates and browser/golden run available (#205/#245). RETRIEVE-vs-APPLY is the key demand challenge. MODEL source \`db87b5a4a7bc807e0680a64417f2c6ca5ca08cf3\` author-corrected variable choice and [native ZIP 11872590321](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197094/artifacts/11872590321) already checked six hashes; assess whether stem/Core1A H2 still decides the model. Five other D2 cells to #214 qualified reviewer. QRT-JUSTIFY-D2 signed AI math assessment is **not** verified credentialed independent human review; Owner decision separate.

**D3 #202/#217 — finish role-specific O1 and resolve two real semantic holds.** #224 already demonstrates existing Core1A, Core1B, Core2B golden techniques on EXPLAIN-D3. First add a question-specific Core1 native witness to that same proof chain; validate Core2A semantics and safe, descriptive author-controlled \`ED3-GRAPH/ED3-ABS\` stage labels. Re-render all five roles only upon authorized authored source change. RETRIEVE and MODEL remain source/primary-demand HOLD. SYNTHESIZE adopts final two-field source (not stale closure). Reuse M0/M1/M2/M3; do not reopen #193 or change Shared renderer.

**D4 #203 — use worst-case W as counterexample before qualifying seven.** Clean RETRIEVE source under #219 and role-specific Core1/Core1A/Core1B/Core2B proof under #235/#242 supersede old answer-leaking ZIP, but learner prior iff theorem Y=UNKNOWN and may make RETRIEVE-D4 hypothesis invalid. Independently test paraphrase leakage, stage timing, SVG/ARIA, changed modulus and academic D3-vs-D4; review MODEL-D4 H2 and SYNTHESIZE-D4 transfer. Existing five other older D4 receipts without native SHA map rely on a separate independently pinned #209 ledger; do not misrepresent them as five full native receipt matches.

## 4. Ordered implementation milestones and exact deliverables

### M0 — Baseline and scope lock (integrator, can begin now; O1 prerequisite)
**Inputs:** #230 latest draft head, #182 AIM, registry, five original golden snapshots/lock, candidate math/IMO UI comparators; all 28 source/manifest/native artifact digests and \`do_not_adopt\` history. Re-read GitHub heads before any new local run. Do not edit any role/fixture on this step.

**Build:** one immutable-source/role benchmark inventory keyed \`QRT-<DEMAND>-D<n>\` with five child role rows. Keep source blob, manifest blob, build ref, renderer digest, receipt, six HTML SHA, baseline golden ID/role SHA, prior browser/AX evidence, W hypothesis, status and mismatch owner. Explicitly distinguish \`not_run\` from \`match\`.

**Exit:** 28 unique IDs × five roles present in a **review worklist**; 140 **structural** receipts preserved; 140 **semantic** role comparisons remain \`NOT_RUN\` until measured; original five snapshot lock unchanged. Count non-reviewed rows honestly.

### M1 — Golden-first EXPLAIN-D3 vertical slice (D3 source author + integrator + reviewer)
1. **Core1A first:** open \`TEST/imo-research/qrt-d3/explain.v1.json\` (blob \`32fad7e3be4f806e43e5f44942434842ad10c25a\`) and \`TEST/products/imo182-qrt-d3-explain.manifest.json\` (blob \`2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e\`). Check signed principal-root versus squaring lesson, T02/T03/T11, actual changed-condition independent exit and no solution of Core2A primary in earlier education. Compare native Core1A blocks and pedagogy with Owner original \`core1a.html\`; do not duplicate generic Core1A for all demands.
2. **Core1B second:** compare original \`core1b.html\` predictor/attempt/reconstruction/repair/boundary behavior; require separate nonblank answer commitments for primary and boundary, matched math and failure signal.
3. **Core1 outstanding:** implement **test/evidence only** for native \`core1.html\` at EXPLAIN-D3: orientation/premise, signed-square distinction without final sign-case answer, golden role block order, no higher-role leakage; test actual page from same manifest.
4. **Core2A and Core2B:** inspect registered supported-application/transfer slot markup, rendered true SVG stages. The source's \`ED3-GRAPH\` and \`ED3-ABS\` \`reveal_stages[0].label="Stage 1"\` is demonstrably generic. Retain intentional preattempt scrub of whole SVG <title>/<desc>; request protected-W reviewed safe descriptive stage labels from source author. Do **not** introduce full-answer title/desc. Tests must check visually presented function/case context with an accessible name **without** inferred solutions/marked candidate intersections.
5. **Golden differential:** for each of five roles compare expected slots, applicable block semantics, role-specific golden techniques T01/T02/T03/T06/T07/T09/T10/T11/T12/T14 and actual learner order; record contextual differences separately from real defects. Rebuild exact source/manifest via \`render_core.py\`; rerun native SHA/zero-reference-gap and actual HTTP/Chromium at 390, 768, 1280, blank/nonblank attempt gates, AX tree and screenshots. Freeze before/after learner proof if authoring changes.
6. **Closure:** one **five-role** source-safe \`EXPLAIN-D3.owner-v31-o1-golden-diff.v1.json\` + human-readable benchmark + exact CI artifact SHA, with statuses \`MATCH/CONTEXTUAL_DIFFERENCE/DEFECT/JUSTIFIED_NA\`. Integrator reviews read-only; any source fix on the D3 author's branch requires applicable route and custody. **Do not** declare academic or Owner QRT ACCEPT.

**Exit:** every of the five EXPLAIN-D3 role-semantic comparisons has evidence (not a generic PASS count), real AX and attempt states checked, no newly disclosed W, any defect classified \`INPUT/RENDERER/BLUEPRINT/ORACLE\`, and no rewritten golden. Stop if the D3 author/reviewer rules the safe label itself answer-bearing.

### M2 — Targeted high-risk source/W repair (parallel band authors, O2 prerequisite)
- **D2 MODEL:** replay repaired #245 both model formulations and Core1A→Core1B→Core2A→Core2B sequencing; qualified reviewer challenges primary MODEL vs APPLY and whether hints leave x/complement/weighted equation to learner. Changed-case 11×5/9 credits claimed 74 must be disproved by integer feasibility. Render changes only when reviewer identifies a genuine source edit.
- **D4 RETRIEVE:** reopen no unsafe artifact; independently test the previous full odd-square iff leak and all paraphrases across Core1, Core1A/B, Core2A H2, SVG/ARIA, Core2B transfer. No infer Y=DEMONSTRATED without evidence. If full prior iff theorem required, hold RETRIEVE-D4 until human prior-knowledge and cognitive verdict; do not manufacture a D4 retrieval claim.
- **D1 MODEL/SYNTHESIZE/JUSTIFY:** question-first identify which act remains W after earlier Core1A/B teaching, source H2 and example; compare most credible rival/difficulty before any further authored patch.
- **D3 MODEL/RETRIEVE:** author/reviewer decide source repair or reclassification on already-cued modelling/diagonal bridge before calling old candidate suitable for review.
- Preserve all otherwise valid authored packages as a reusable starting point. **Eight elevated holds are not the only eight pending qualified review; all 28 require it.**

**Exit:** each elevated case has named \`ACCEPT_CURRENT_FOR_REVIEW / REPAIR_SOURCE / RECLASSIFY / HOLD\` engineering recommendation with evidence, old unsafe artifacts quarantined. No unsupervised academic decisions.

### M3 — Scale a validated role benchmark to the other 27 cells (integrator; O1)
Implement the role-specific semantic comparator as **TEST-only verifier and evidence format** using existing actual five-role HTML, not a second page generator and not a raw cross-question HTML digest check. For each role:
- Core1: question-specific prerequisite bridge and no completed W.
- Core1A: independent construction teaching, staged visual only if useful, changed-number/condition exit separate from primary.
- Core1B: main and boundary commitment separated; why-wrong diagnosis and repair.
- Core2A: progressive optional H/S support before/after attempt, independent worked check, source distinction.
- Core2B: changed demand/invariant and original attempt answer still withheld.
- All: real on-origin CSS/assets, 390/768/1280, screenshot/AX, 14px minimum learner text including SVG labels, no horizontal overflow, correct semantic figure visibility, no sealed payload before substantive commitment; zero renderer gaps; no fixture drift.

**Exit:** **140 role-specific semantic evidence records**, not \`140/140 academic passes\`; true defects have named owner and patch route. No new global blueprint exists unless O3 approved.

### M4 — Qualified QRT mathematical/educational decisions (human independent reviewer; O2)
For each of 28 authored TEST exemplars record: source ID/SHA; independent main and changed-case maths; strongest rival cognitive demand; D1–D4 adjacent band with five components individually scored 0–2; X/Y/Z/W with Y \`DEMONSTRATED/UNCERTAIN/MISSING\`; **12 separate** H1/H2/H3, S1/S2/S3, P1/P2/P3, M1/M2/M3 evidence-cited verdicts; responsive/AX/preattempt/changed-case transfer references; reviewer credentials, author/fixer independence, COI, dated signed \`ACCEPT_CURRENT/REVISE/RECLASSIFY/REJECT\`. No aggregate H/S/P/M score. Route #211 two risky D2 cells, #214 other five D2 cells, #234 D1+D3+D4 (21). Keep \`NOT_RUN\` if human has not inspected role content.

**Exit:** 28 distinct signed independent **dispositions** may include rejects/holds. An academically reclassified source does not automatically fill its old QRT cell.

### M5 — Owner QRT, golden and optional O3 decision docket (Owner; O2/O3)
After signed review, obtain explicit immutable **separate** \`ACCEPT/REVISE/REJECT\` + Owner decision ID for *each exact* QRT cell/source version. A successor H3 golden decision \`D-182-3\` and EXPLAIN-D3 \`D-182-6\` are not inherited from fixture lock or agent comments. Owner can designate a new per-cell candidate/example golden only by **new immutable** ID, source SHA, renderer SHA, HTML SHA, scope/rights and explicit exact/technique semantics. Never rewrite previous exact HTML fixture.

**O3 escalation rule:** submit a narrow gap packet *only* when after exact-source replay and golden differential the required teaching behavior cannot be represented through currently registered blueprint + authorized input/renderer. Name reproduction, defect owner \`INPUT | RENDERER | BLUEPRINT | ORACLE\`, alternative minimal fixes, before/after protected W, necessary BP registry version change, native CI and Owner authorization. No blueprint replacement from mere hint/stage count or visual preference.

### M6 — Integration and stop gates (integrator / module owners)
- **Separate parallel CI lane:** #244 proposed \`TABLE_OF_VALUES\` is not rendered; typed \`data[].id\` \`EQUATION\`/MathML and \`DATUM\` need module decision. #244 immediate-base 40 new test IDs, #224 one new and other lanes zero new against immediate bases but persistent broad failures: repair actual source-local or module-owned regressions only. Same 20 canonical library findings recur across stacks; do not label them independently introduced in all four PRs. Full branch CI must be judged at exact new head.
- Consolidate TEST-only approved/source-safe role reports into existing #230 28-row viewer/ledger after **serial integrator custody**. Original #230 scoped 16/16 invariants + 84/84 responsive tile checks are for the **administrative viewer**, not 140 native educational technique judgments.
- **Product release/merge:** remains held without separate applicable Owner authorization, rights and applicable gate conditions. Track B #183 source originals, rights, 68 original Core2, Core1A concept reuse admission are separate. No public route or main merge from this plan.

## 5. Minimal implementation commands on the *authorised pinned checkout*

\`\`\`bash
# Confirm local HEAD matches the explicit PR/source ref before running.
python Shared/tools/question_review_matrix.py check
python Shared/tools/question_review_matrix.py write --check

# First vertical slice — authored TEST source only:
MANIFEST=TEST/products/imo182-qrt-d3-explain.manifest.json
python Shared/tools/render_core.py gaps --manifest "$MANIFEST" --reference
python Shared/tools/render_core.py build --manifest "$MANIFEST" \
  --out build/imo182/qrt-d3-explain \
  --mode PAGES --reference --draft

# Compare SHA256 of the FIVE native HTML pages and index.html
# to actual render-receipt / current source+manifest artifact.
# Validate frozen snapshot-lock hashes separately.
# Execute role-specific browser/AX, blank/nonblank, W and golden
# comparisons from existing #217/#224 workflows on the same head.
\`\`\`

*These commands are an execution recipe, **not a claim they were run in this planning turn**. Use existing #217/#224 workflows and their tests instead of writing a new learner-page renderer.*

## 6. Evidence schema and review stop conditions

Every \`cell_id + role\` record should carry:
\`\`\`json
{
  "cell_id": "QRT-EXPLAIN-D3",
  "role": "CORE1A",
  "source_blob": "PINNED_SHA",
  "manifest_blob": "PINNED_SHA",
  "registry_blob": "591ba061b8771c30fdffc4506aa720ca9ba89335",
  "blueprint_ref": "BP-CORE1A-CONSTRUCTION@1.8.0",
  "renderer": "render_core/2",
  "native_html_sha256": "EXACT_SHA",
  "receipt_sha256_verified": false,
  "snapshot_lock_id": "G-IMO-G9-FIVE-CORE-20261012",
  "snapshot_role_sha256": "PINNED_ORIGINAL_ROLE_SHA",
  "techniques": [{"id":"T02","status":"NOT_RUN","evidence_ref":null}],
  "learner_w": "SOURCE_SPECIFIC_HYPOTHESIS",
  "learner_y_status": "UNCERTAIN",
  "math_changed_case": "NOT_RUN",
  "pre_attempt_w_leak": "NOT_RUN",
  "browser_390_768_1280": "NOT_RUN",
  "svg_aria": "NOT_RUN",
  "golden_semantic_verdict": "NOT_RUN",
  "defect_owner": null,
  "qualified_independent_reviewer": null,
  "signed_verdict_id": null,
  "owner_qrt_decision_id": null,
  "owner_accepted": false,
  "owner_golden_designated": false,
  "release_authorized": false
}
\`\`\`
Values above are **schema examples/placeholders**, not measurements for EXPLAIN-D3. Do not default missing booleans to PASS; use \`NOT_RUN\` or explicit unknown. Never conflate structural fixture parity with pedagogical technique match.

**Reject or hold a cell if:** a wrong mathematical warrant; source/manifest/receipt mismatch; missing required blueprint components; preattempt source, prior teaching, hidden/AX/SVG metadata or H1/H2 reveals W; H3/solution open without substantive required commitment; a needed changed-case result fails independent check; qualified reviewer unavailable; Owner cell ID absent; applicable rights or stage admission unavailable. Separate technical incompleteness from external approval.

**Programme progress measurement, unchanged by creating this plan:** native authored TEST technical provenance 28/28, five-role native pages 140, standalone index pages 28, 168 HTML SHA-256 historical proof, 140 role structural slot matches; **golden semantic technique review 0 completed in #230 ledger (\`UNREVIEWED\`)**, 8 elevated source/educational flags, 0/28 qualified signed verdicts, 0/28 Owner QRT accepts; no new golden designations and original Core2 0/68 admitted.

## 7. Handoff routing and the explicit first action

**Agent A / integrator immediately:** on existing #230 read-only compare \`QRT-EXPLAIN-D3\` exact source, manifest, source SHA, current five native role SHA and original golden lock; write a source-safe five-role **semantic gap checklist** with Core1A first, Core1B second, then Core1, Core2A, Core2B. Link earlier M1/M2/M3 actual evidence. In #217 ask the source author to propose safe \`ED3-GRAPH\` and \`ED3-ABS\` labels with actual before/after screen-reader and W proof; don't directly edit active #224 while another source author owns custody. Avoid adding new proposal-level \`OWNER_ACCEPT\` values. Stage this as an O1 implementation, not an abstract plan/CI statistic.

**Immediately parallel:** D1 #200 contacts TEST adapter/schema owner for \`TABLE_OF_VALUES\` and typed oracle compatibility; D2 #211 obtains human review of corrected #245; D4 #234 requests independent RETRIEVE prior-theorem check. The source owners' work can proceed without making the 28-row integration viewer wait for unrelated broad-CI resolution.

**Next formal checkpoint should answer five concrete questions:**
1. Which **actual EXPLAIN-D3 Core1A** concepts/representations and independent exit match Owner T02/T03/T11, and where do they differ?
2. Does Core1B force a fresh reasoning decision and genuinely independent boundary commitment?
3. Does the untested Core1 role merely orient, or does it reveal the signed-root choice?
4. Can Core2A/Core2B stage labels be made sufficiently descriptive **without revealing W** under the existing renderer scrub?
5. Does the final five-role comparison expose a true INPUT/RENDERER/BLUEPRINT/ORACLE defect, and what is the smallest authorized repair?

\`LOG | issue=182 | agent=A | plan=R7_BLUEPRINT_GOLDEN_D1_D4_IMPLEMENTATION_V1 | start=EXPLAIN_D3_FIVE_ROLE_GOLDEN_SEMANTIC_DIFF | parallel=D1_CONTRACT,D2_MODEL_QRT,D4_RETRIEVE_W | outputs=28x5_ROLE_REPORTS,28_HSPM_SIGNED_REVIEWS,28_OWNER_DECISIONS | baseline_native=28x5 | role_semantic=UNREVIEWED | special_holds=8 | qualified_signed=0/28 | Owner_QRT=0/28 | golden=FROZEN | O3=CONDITIONAL_ONLY | merger=HOLD | release=HOLD\`
