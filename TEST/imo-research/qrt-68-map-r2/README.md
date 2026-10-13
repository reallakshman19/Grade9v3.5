# IMO Grade 9 — QRT R2 source-page validation workbench

**Issue:** [#183](https://github.com/reallakshman19/Grade9v3.5/issues/183), Owner priority: validate the tentative primary cognitive demand and five-factor D-band **against the actual original question** before more native Core2/Core1A batches. **Scope:** research/academic AI proposal, not production/source custody/Owner QRT approval.

## Read/open

- [Standalone interactive HTML R2](imo-qrt-68-interactive-r2.html) — all 68 original source positions, 28 canonical QRT cells, source-review evidence filters, full case detail, JSON/CSV export. Works offline, has no source exam stem/options/key/figure and makes no external network request.
- [Complete all-68 QRT R2 JSON](qrt-68-map-r2.v1.json) — proposed cells and five-dimension scores for 15 inspected positions, source-neutral concept summaries for remaining 52, one diagram hold; input blobs, canonical templates, source-academic checks, concept-grouping screens.
- [Review-level source-safe evidence](qrt-source-visual-review-r2.v1.json) — the 16 inspected positions, source page indices, 15 proposed demand/band/score classifications with explicit protected inferential move and independent check; the one unresolved source diagram, and comparative Core1A reuse decisions.

**Authority:** `Shared/quality/question-demand-matrix.v1.json` (`3779a53...`), `Shared/quality/question-demand-templates.v1.json` (28 canonical), `Shared/vocabularies/learner-question-metadata.v1.json` (`3d88b24...`) five scoring anchors and ranges D1=0–2, D2=3–5, D3=6–7, D4=8–10.

## R1 → R2 research evidence

| Field | R1 | R2 |
| --- | ---: | ---: |
| Distinct source positions | 68 | **68** |
| Source-page visually rechecked by this AI reviewer | 0 in R1 production | **16** (10 organizer sample and 6 original full-paper) |
| Source-checked with an AI-proposed QRT cell | R1 only prior pilot data | **15** |
| Summary-only LOW_CONFIDENCE heuristic candidates | 59 | **52** |
| Diagram source hold (not classified) | 1 | **1** (organizer sample Q005) |
| Tentatively placed in a QRT cell | 67 | **67** |
| Owner/academic accepted QRT cells | **0/28** | **0/28** |
| Authentic Core2 admitted | **0/68** | **0/68** |
| Core1A admitted | **0** | **0** |

The 16 inspected positions comprise organizer-sample 2026–27 Q001–Q010 (10) and 2023–24 full-paper Q003, Q006, Q017, Q018, Q036, Q038 (6). Source-witnessed via screenshots of both original organizer sample pages and 2023–24 scan printed pages 2, 4, and 6. **No original SOF stems, options, graphics, keys, PDF or screenshot bytes are copied to this repository**. Scans are independently accessed for research, but they are **not source custody receipts**: retained source PDF SHA = unknown, component-by-component verified copy = no, reproduction rights = NOT_GRANTED.

- **Concrete changed hypothesis:** 2023–24 original Q017 was classified `QRT-APPLY-D2` from metadata in R1; visual review supports `QRT-APPLY-D1`, five-component score `[0,1,0,0,1]=2`. Its task applies an already specified equal-radius cone-volume relationship, without selecting whether to model the context by area or volume. The original Owner-compilation distractor discrepancy remains independently unresolved, so this is **not** an admission.
- 2023–24 original Q003's preliminary `QRT-MODEL-D2` remains defensible as an AI proposal; source/rights/Owner original-Q003 acceptance still separate.
- 2023–24 full-paper Q006 and organizer sample Q002 were visually inspected and each independently assessed as `QRT-REPRESENT-D2`. Both require word-code overlap and invariant correspondence, making them a **potential same-concept Core1A reuse review pair**. This is not a reuse approval.
- **Same subject ≠ same cognitive demand:** 2023–24 cone Q017 `APPLY-D1` and organizer sample Q008 `MODEL-D2` require different teaching constructions. Do not clone cone lessons across the two.
- **Same QRT ≠ same exact microconcept:** 2023–24 numerical Q003 and organizer sample number-pattern Q003 are both `MODEL-D2` but use different representation/constructive inference. 2023–24 fixed-cost Q038 and organizer sample tent Q008 are both `MODEL-D2` yet have different model-selection contexts and prerequisites.
- Organizer sample Q005 remains **UNCLASSIFIED_SOURCE_FIGURE_HOLD**: don't infer a valid geometry proof or academic QRT cell from printed choice alone. Sample Q009 remains a source-vs-Owner transcription conflict even though the organizer source was visually inspected.

## Before approving even one QRT

Owner/independent academic reviewer must inspect each genuine original stem/figure privately, confirm the `answer.crux_move_ref` against reasoning route, five difficulty components, exact option/key distinctions, H1–H3, S1–S3, P1–P3 and M1–M3, approve learner-relative X/Y/Z/W and concept-specific Core1A construction. Source custody/retained page digest, publisher rights/display mode and A4 owner print-quality are **separate** gates.

The 52 remaining summary-only placements cannot be called validated or treated as a backlog of automatically batch-ready items. Review source pages in small groups; consider lesson reuse only for verified same microconcept + prerequisite + learner protected inferential move, never merely a matching 7×4 QRT cell.

## Checks and release guard

- 68 unique source IDs; 28 canonical matrix cells; 67 proposals + 1 source-figure hold; 15 source-review score vectors exactly recomputed against canonical D1–D4 ranges; 52 untouched low-confidence labels; none accepted/eligible, zero rights grants.
- Updated offline HTML embed exactly matches R2 map, all controls present, JavaScript compiles, no HTTP fetching; **browser interaction NOT_RUN**, do not upgrade to a real device/browser pass.
- Only additive `TEST/imo-research/qrt-68-map-r2/` source-safe files. No changes to `Shared/tools/render_core.py`, registered blueprints, native source protected artifacts, QRT authority templates, original R1 workbench, Shared/main, `relay/STATE.yaml`, #212 serial writer or subtopic release.
- Previous BuddyRunner #183 source-verification / G2 identity provenance HOLD remains separate from this **read-only academic research**. This R2 work is not Stage 2 or product custody/implementation.
- Keyboard/accessibility work remains **DEFERRED_BY_USER**.

**Next true admission gate:** Q003 Owner-private source-original component readback + independent crux/D-band + explicit QRT verdict, followed by Owner native A4 acceptance and rights/display decision. R2's source inspection does not silently satisfy this gate.
