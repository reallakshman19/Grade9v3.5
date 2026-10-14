# Issue #217 D3 M1 — isolated successor native audit (unsigned)

Authority: Issue #217, parent #202; source TEST draft PR #193 at 40142fe06818e7a946d6296911d495f3f3323b12, stacked on #190 at 1964703636e998b8c5975e4859a711e8ba3edff7. This draft must target branch agent-d3/imo182-qrt-model-d3, not main. The original authored questions and immutable Owner fixture are read-only.

M0 report: https://github.com/reallakshman19/Grade9v3.5/issues/217#issuecomment-6153426477

The seven entries in m0-adoption.v1.json pin exact source/manifest blob SHAs and the original scoped CI run/artifact. All entries are wholly authored TEST-only, with five Core roles and no Core2. Every H1–M3 ask remains PENDING, principal independence NONE, owner_decision_id null.

## M1 eligible native work

EXPLAIN, APPLY, REPRESENT, SYNTHESIZE, JUSTIFY: reuse the exact source/manifest and sole Shared/tools/render_core.py. The workflow imo217-d3-provisional-native.yml validates the QRT matrix, runs zero-reference-gap checks, builds five actual Core HTML roles plus index per manifest, executes the original math/visual/browser unit tests, and runs native_audit_217.py. It archives the actual native HTML, native SHA256 receipts, and machine evidence into a downloadable Actions artifact.

native_audit_217.py verifies source+manifest Git blob hashes, active registry, five immutable Owner original HTML snapshot digests, exact native receipt/page SHA256, active blueprint ID and version, role slot sequence against the golden, and presence of after-attempt markup. Structural technique match does NOT establish semantic/academic pedagogical suitability or compare unrelated question HTML bytes for equivalence. It never changes golden bytes.

## Explicit semantic holds

RETRIEVE-D3 remains RECLASSIFY_REVIEW_HOLD: its stem supplies the diagonal test strategy, making APPLY-D2 a plausible competitor. Do not adopt before qualified semantic review.

MODEL-D3 remains REPAIR_SOURCE_HOLD: the original stem itself prompts the shared positive quantity and offset multiplier claimed as learner-owned model-selection W. Do not re-render, source-patch or call its D3 classification accepted without source-level adjudication. Retain original #193 as comparator.

## Local reproduction on the pinned checkout

    python Shared/tools/question_review_matrix.py check
    python Shared/tools/question_review_matrix.py write --check
    for d in explain apply represent synthesize justify; do
      python Shared/tools/render_core.py gaps --manifest "TEST/products/imo182-qrt-d3-$d.manifest.json" --reference
      python Shared/tools/render_core.py build --manifest "TEST/products/imo182-qrt-d3-$d.manifest.json" --out "build/imo182-qrt/d3/$d" --mode PAGES --reference --draft
    done
    python -m unittest -v tests.test_imo182_qrt_d3_explain tests.test_imo182_qrt_d3_apply tests.test_imo182_qrt_d3_represent tests.test_imo182_qrt_d3_synthesize tests.test_imo182_qrt_d3_justify
    python TEST/imo-research/qrt-d3-successor/native_audit_217.py

## Still PENDING

M1 exact-head GitHub Actions evidence must be inspected, not inferred. M2: on-origin browser checks of 390/768/1280 across native pages, H1/H2 before commit and H3 after a nonblank attempt, blank submit protection, SVG/ARIA and changed-case transfer; independently verified golden pedagogical technique. M3: seven source-safe 7x4 matrix tiles (including two HELD). M4: unsigned review packets, qualified independent specialist verdicts and distinct Owner decision IDs. The JUSTIFY-specific source review note is missing; do not fabricate its prior review. No merge, new Core2, 68-question admission, public release, blueprint/Shared modification or frozen golden rewrite.

## r5-02 source-specific supersession (post-M3 reviewer finding; 14 Oct 2026)

Original #193 **SYNTHESIZE-D3** source Git blob 71830e1317595658e40819ee5fbc68ed140e9855 contains the false post-attempt text “Assisted REPRESENT question, academic acceptance pending.” The original source and its previous native role bundle are **DO_NOT_ADOPT** for present SYNTHESIZE-D3. Owner-independent technical PR #221 reproduced that defect and validated an exactly one-field corrected source at blob b852966af06a54b7a594f6ab12653af341f6d836 with scoped rendered artifact run 38484157878 / artifact 11859035196. This successor includes **only that specific source edit**, with immutable original blob/record preserved in the M0 baseline and explicit overlay in synthesize-source-supersession.v1.json. The new audit checks current source blob and actual rendered Core2A text, and the dedicated closure regression test is part of M1 and M3 CI. No change to original #193, five Core roles, renderer, manifest, blueprint registry, golden lock, or academic status. Re-run exact-branch-head M1, M2, M3; prior #224 artifacts remain technically hash-valid but their original SYNTHESIZE role must not be adopted.

Reviewer nominations are already centralized under existing open Issue #234 covering D1/D3/D4; do not create competing requests or pretend the Owner/author of the fixture can sign an independent review. Submit source-safe M4 results and any actual assigned reviewer to #234 and #217. Qualified maths/QRT signatures and Owner IDs remain wholly PENDING.
