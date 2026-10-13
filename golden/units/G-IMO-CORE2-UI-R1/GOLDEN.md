# G-IMO-CORE2-UI-R1 — Owner-approved **visual/interaction reference**

**Owner direction, 13 October 2026:** “looks perfect. save this as IMO golden fixture, proceed next. For Core 1A, remember to change as per demand/concepts of each question see QRT.”

**Scope of Owner approval:** the in-chat **source-safe authored Core2 demonstration** as an **IMO-specific visual/interaction golden reference**. This is **not** a claim that the lost private authentic Core2 `core2.html` was inspected, that a new question or its mathematical solution was accepted, that the authoring UI mock is native-rendered, or that publisher rights/QRT/A4 have been approved. Its approval does **not** extend to the accompanying Core1A demonstration.

## Immutable HTML files

| File | Role | SHA-256 of exact UTF-8 bytes | Status |
| --- | --- | --- | --- |
| [core2_authored_demo.html](core2_authored_demo.html) | **Approved reference**: IMO Core2 page layout and learner attempt/hint/answer behavior | `90fa27ec928ef6121c0350cc469ef1bd98e13029d9f4e26b66b08813b4401ddb` (32,261 bytes) | OWNER_APPROVED_VISUAL_INTERACTION_REFERENCE |
| [core1a_authored_preview.html](core1a_authored_preview.html) | Source-safe concept demonstration linked from Core2; navigation works offline | `d0e0670007734ba738f12a5f4aa88e63ffaa140a540fb51b1cf41d9348a899a3` (21,109 bytes) | **NOT** an approved universal Core1A golden |
| [q003_preview_index.html](q003_preview_index.html) | Local navigation and comparison only | `4056c6f37b59c06d25c451a56ae51ea6d6c526f03b3d43101607b57957bdfa45` (10,736 bytes) | Context, NOT production |

The source-safe Core2 sample is wholly authored and uses **different** example data, not the original IMO 2023–24 Q003 stem, options, original answer, or question-page HTML. The three files preserve the exact Owner-reviewed presentation, with their relative links intact. Their role and safety assertions are machine-recorded in [reference-fixture.v1.json](reference-fixture.v1.json). Do not directly copy the markup into a learner product or label it a native rendering.

## Transferable teaching behavior, not fixed academic content

This golden's visual and interaction pattern follows the active [BP-CORE2-SOURCE-QUESTION@1.11.0](../../../Shared/web/interactive-page-blueprints.v1.json) and the existing **candidate** [G-CORE2-R2](../G-CORE2-R2/GOLDEN.md). It provides an easy-to-scan source/identity band, a clear **Attempt first** source-question column, a support column, typed option commitment, difficulty disclosure, question-aligned visual where useful, separate wrong-route warning, concept navigation, progressive hint ladder, and a deliberately opened post-commit solution with structured reasons and independent check.

- **T01:** visible source question and learner commitment before revealing decisive assistance.
- **T05:** requests expose **one rung at a time**; the sample has H0 safe orientation before commitment and H1/H2 only after attempt. **Three is not a generic rung target**; depth depends on the actual demand, protected move and question.
- **T13:** original printed key and independent reasoning must remain explicitly distinguishable when authentic source custody supports them; the authored demo cannot represent a publisher key.
- **T15:** preserve the **real** question's original option order and actual response type when applying this UI to authentic Core2.

The sample's guided rungs are authored, **never SOURCE hints**. A true original source hint must have real matching source provenance. Some blueprint slots are conditional (for example SOURCE_PDF or REPRESENTATION), and must be omitted/waived with truthful reasons rather than invented for parity.

**Implementation boundary:** `Shared/tools/render_core.py` remains the sole native learner renderer. No `manifest.json` is supplied under this visual reference because `build_golden.py` must not silently accept a second hand-composed native page. The existing renderer-built G-CORE2-R2 remains intact and CANDIDATE; the Owner's review blesses **this IMO UI reference only**, not every underlying fixture or the current private original item.

## Core1A must vary per **question's concept and QRT demand**

Use the canonical [4×7 question-demand matrix](../../../Shared/quality/question-demand-matrix.v1.json), [28 QRT templates](../../../Shared/quality/question-demand-templates.v1.json) and [cognitive-demand vocabulary](../../../Shared/vocabularies/cognitive-demand.v1.json). The companion Core1A is just one authored square-offset concept demonstration; **do not clone it for other IMO questions**.

For each question, first locate the decisive `answer.crux_move_ref`, concept/capability and prerequisites. An academic reviewer proposes **one primary demand** from RETRIEVE, EXPLAIN, APPLY, MODEL, REPRESENT, SYNTHESIZE, JUSTIFY, and derives D1–D4 from the five-component difficulty assessment. Record learner-relative X/Y/Z/W and H1–M3 semantic review, then author **construction decisions, stage representation, worked anchor, diagnostic and independent new-number/condition exit matching that demand**. An actual Owner-reviewed QRT cell is required before admission, but drafts may be labelled `PROPOSED`. If multiple questions truly share the same prerequisite, inferential decision and concept, a teaching unit may be reused; shared subject headings alone do not justify reuse.

The source-safe [Core1A QRT adaptation policy](../../../TEST/imo-research/core2-q003/core1a-qrt-demand-adaptation.v1.json) defines the seven teaching purposes and four band protections without inventing a per-question classification. The pre-existing tentative Q003 `QRT-MODEL-D2` is **only a proposal**, not automatically confirmed by this approval.

## Remaining issue #183 gates

Private original Core2 `render_core/2` output remains frozen and distinct; real QA there is Coordinator-reported LOCAL. Source paper Owner-personal readback **UNCONFIRMED**; A4 geometry **COORDINATOR LOCAL PASS** but Owner print page-break/legibility and production PDF policy **PENDING**; publisher rights **NOT_GRANTED**; QRT accepted **0/28**; admitted original Core2 **0/68** and Core1A **0**. Accessibility keyboard follow-up is **DEFERRED_BY_USER**. No PR, Shared/main writer bypass, merge, or released learner original item is authorized by this golden-reference approval.
