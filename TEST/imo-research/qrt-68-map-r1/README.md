# IMO Grade 9 — 68-position interactive QRT review matrix (research triage R1)

**User requirement (13 Oct 2026):** Before further batches, map all **68 distinct source positions** against the canonical **28 question-review templates**, and provide **a standalone interactive HTML page and JSON**. Do not treat any draft placement as academic or Owner acceptance.

## Open files

- [Interactive HTML](imo-qrt-68-interactive.html): **single offline file**, all 68 rows embedded, click any of the **7 demands × 4 difficulty bands** to filter, search by ID/concept/topic, filter by band/evidence/topic, question inspection panel, no external requests, JSON/CSV export buttons.
- [Full source-safe JSON](qrt-68-triage-map.v1.json): all 68 source identifiers, original source/research-census status, topic/microconcept summary, proposed QRT or null, classification evidence level and flags; 28 named cell definitions, protected-work band policies, complete H1–M3 review questions from generated canonical templates, input Git blobs and review conditions.
- This README is guidance; the canonical source remains `Shared/quality/question-demand-matrix.v1.json`, `Shared/quality/question-demand-templates.v1.json`, `Shared/vocabularies/cognitive-demand.v1.json`. This R1 triage never changes those contracts.

Open `imo-qrt-68-interactive.html` from the filesystem in a browser; everything is embedded. The HTML does not need `node_modules`, a server or access to the source PDF. JSON is separate for downstream review and independently exportable from the page.

## Source census and classification limitations

| Metric | R1 count |
| --- | ---: |
| Total unique source positions | **68** |
| Owner initial seed positions | 66 (58 full-paper, 8 sample) |
| Additional observed organizer sample positions | 2 |
| Canonical QRT cells | 28 |
| **Tentative proposals** placed into QRT cells | **67** |
| QRT-unclassified due to unresolved original figure | **1** (`SOF-IMO-G09-SAMPLE-2026-27-Q005`) |
| Prior source-inspected AI research-pilot QRT proposals | 7 (all **NOT_ACCEPTED**) |
| Existing issue #183 Q003 proposal | 1 (`QRT-MODEL-D2`, **NOT_ACCEPTED**) |
| New **metadata-only heuristic** triage labels | 59 (all **LOW_CONFIDENCE**) |
| Independently/Owner-accepted QRT cells | **0/28** |
| Authentic source Core2 admitted | **0/68** |
| Core1A admitted | **0** |
| Rights granted | **NO** |

The 59 metadata-derived proposals are **work-queue groupings, not academic conclusions**. They are generated from existing **source-safe concept summaries only**, not from the private original stem/options, a complete `answer.reasoning_route` crux binding, or five independently reviewed difficulty components. The assigned primary demand or D-band **may change substantially** when an academic reviewer checks the original question. This is why a 23-item `QRT-APPLY-D2` cluster is a **triage list**, not 23 interchangeable lessons or a batch authorized for native delivery.

Exactly one position, organizer sample 2026–27 Q005, remains **unclassified** because its source figure and underlying geometry have an explicit `SOURCE_FIGURE_INTERPRETATION_HOLD`. It is included in the 68-row register and surfaced as a hold rather than using an unfounded cell. An interactive matrix that claimed 68 accepted/verified cells would be misleading.

### How to review and change these labels

For each question, an independent academic reviewer/Owner must:

1. Verify source identity, page, stem, complete original options, figure and source key, preserving source/rights status (all 68 currently `core2_eligible=false`).
2. Solve/check the question and bind the canonical decisive learner move to `answer.crux_move_ref` in the existing `answer.reasoning_route[]`.
3. Independently select **one primary demand** from the seven and derive **D1–D4** from five difficulty components; secondary demands do not select a second cell.
4. Validate learner-relative X/Y/Z/W; H1–H3, S1–S3, P1–P3, M1–M3; concept-specific Core1A construction/diagnosis/new-givens exit.
5. Record Owner per-question review evidence and per-cell verdict. Only then move **accepted** counts; keep publisher rights and A4 separate.

No row is silently promoted by the presence of a cell. Never use the R1 matrix to relabel the private original Q003 source, admit all 68 at once, create a large generic Core1A lesson group, or overwrite the Owner-approved source-safe IMO Core2 UI reference. Keyboard/AX work remains **DEFERRED_BY_USER**.

## Technical verification

- Source census: exact 68 distinct source IDs from `TEST/imo-research/intake/core2-source-custody-eligibility.v1.json`, 58 full papers + 8 sample seed + 2 additional.
- Taxonomy: 66 pre-existing topic/learning-demand summaries from `seed-question-topic-map.v1.jsonl`; 2 additional figure-only summary labels from the organizer sample extension research overlay.
- Authority: 7 canonical cognitive demands, 4 bands, 28 named templates and all 12 H/S/P/M checks, without changing their source documents.
- Committed static verification: 19/19 map-and-HTML invariants (68 unique, 67 cell suggestions, 1 hold, 7 pilot, 1 Q003, 59 metadata, 28 templates, embedded rows, no remote fetch, JS syntax, no academic/rights acceptance).
- **No browser runtime or source-paper rerender is claimed for R1**. R1 HTML is a research-review tool, not an original-question Core2 learner product or the native renderer.

## Progression

The Owner expressly prioritized complete 68-position mapping **before further content batches**. Therefore stop promoting the earlier MODEL-D2 authored previews as academic evidence. Use this source-safe matrix for a reviewer to select a small cluster only after same QRT proposal **and** concept/prerequisite/inferential decision match. The issue #183 real native-Q003 and rights gates remain unchanged.
