# Golden candidates

These are **CANDIDATE** examples for studying a method, not accepted products or scripts to copy. The Owner alone may mark an exemplar `OWNER_BLESSED`. Use `python3 Shared/tools/build_golden.py` to render them with the sole learner renderer; output under each `rendered/` folder is ignored.

| Core role | Technique to inspect | Candidate and location |
|---|---|---|
| Core1 orientation | T01 attempt-first stem, T14 prerequisite bridge | [G-MATH-LINEAR-CONSTRAINT](units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md), `core1.html` |
| Core1A construction | T02 one decision, T03 staged representation, T11 compact anchor | [G-MATH-LINEAR-CONSTRAINT](units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md), `core1a.html` |
| Core1B reconstruction | T06 failure signal, T10 boundary test, T12 new givens | [G-MATH-LINEAR-CONSTRAINT](units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md), `core1b.html` |
| Core2 source custody | T01 attempt first, T05 climbing hints, T13 key versus verified, T15 source options | [G-CORE2-R2](units/G-CORE2-R2/GOLDEN.md), `core2.html` |
| Core2A supported practice | T05 hints, T07 independent check | [G-MATH-LINEAR-CONSTRAINT](units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md), `core2a.html` |
| Core2B transfer | T08 closure from final transfer, T09 invariant plus changed demand | [G-MATH-LINEAR-CONSTRAINT](units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md), `core2b.html` |

[TECHNIQUES.md](TECHNIQUES.md) names the move and the defect it can prevent. [anti/](anti/) shows real review mechanisms. An author should research their own unit, then compare a prototype to these candidates in `SELF-CRITIQUE.md`; a reviewer should challenge both the exemplar and the new work.

## IMO Owner-reviewed UI golden (visual/interaction, not native product)

The Owner approved the **source-safe authored Core2 UI** in chat on **13 October 2026** as the IMO-specific visual/interaction golden. See [G-IMO-CORE2-UI-R1](units/G-IMO-CORE2-UI-R1/GOLDEN.md) and its frozen [review HTML](units/G-IMO-CORE2-UI-R1/core2_authored_demo.html), SHA-256 `90fa27ec928ef6121c0350cc469ef1bd98e13029d9f4e26b66b08813b4401ddb`. Use this as an **Owner-reviewed layout/learner interaction reference** for future IMO original Core2 produced exclusively with `Shared/tools/render_core.py`. This artifact is an authored demo, not a renderer input, a retained original IMO stem/options, or a per-question acceptance. Its navigation companion Core1A is **not** blessed as a generic teaching golden.

The existing renderer-native [G-CORE2-R2](units/G-CORE2-R2/GOLDEN.md) remains a **separate candidate** for examining source-custody structures and support moves; do not overwrite it. There is intentionally no `manifest.json` for the mock review fixture: `build_golden.py` must continue to work only on registered native manifests. Each actual IMO Core1A must instead be tailored to its independently reviewed question concept and specific [QRT primary demand × D-band](../Shared/quality/question-demand-matrix.v1.json); the reusable [Core1A authoring policy](../TEST/imo-research/core2-q003/core1a-qrt-demand-adaptation.v1.json) is a non-authoritative design aid, not 28 accepted cells.

This Owner blessing is limited to the reviewed Core2 **UI presentation**, not publisher rights, exact original Q003 source verification, print quality, QRT acceptance, public release, or reuse of the sample's authored numbers. The keyboard/accessibility follow-up remains deferred by user.
