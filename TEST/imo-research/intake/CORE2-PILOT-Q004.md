# First source Core2 pilot — printed Q4 (2026–27 official sample)

Research scope only; destination custody owner: [#130](https://github.com/reallakshman19/Grade9v3.5/issues/130). IMO delivery dependency: [#137](https://github.com/reallakshman19/Grade9v3.5/issues/137).

This work selects **SOF-IMO-G09-SAMPLE-2026-27-Q004** as the first *review candidate*, not the first eligible or approved Core2 item. The other 67 positions remain unchanged and **HOLD**.

## Direct visual observation (2026-10-10)

The SOF organizer's [two-page 2026–27 Class 9 sample paper](https://sofworld.org/download/file/fid/73719) was viewed with PDF page rendering (zero-based page 0 question panel; page 1 printed answer-key panel). Printed Q4 presents a four-row input/output table, and the printed key identifies choice **B**. Independently substituting each of the four input values into **y = 2x - 1** reproduces the observed output column. This checks an arithmetic claim, not an independent professional review or a durable document receipt. The official organizer-hosted URL is first-party evidence of a question reference, not a source reuse licence.

The paper contains no retained byte SHA-256 in this destination. Earlier historical CI PDF downloads were ephemeral and **do not** supply this pilot with defensible retained source custody. The original source item/table, options, figure pixels, source-page images, and protected PDF are **not committed** here.

## Owner-directed self-check + focused spot review (2026-10-10)

Revisited the [first-party two-page PDF](https://sofworld.org/download/file/fid/73719) via remote PDF rendering. **Printed Q4 is on zero-based PDF page 0; its answer key is on page 1.** The question panel visibly has an original item number, stem, table of x/y values and four labelled answer choices. No separate subpart, figure caption or hints were visible for this item. The tabular layout is treated as **visually sighted**, not as reconstructed exact image/figure custody. The key panel visually identifies **B**. No source text, table pixels or original option formulas are committed.

The same-principal mathematical spot review checked the four input/output pairs already present as derived metadata: x = −1, 0, 1, 2 maps to y = −3, −1, 1, 3 under y = 2x − 1. More importantly, at x = 0 the three *other* labelled choices would give −2, −3 and 1, respectively, all different from the observed −1. Thus this is a **unique-choice arithmetic check** rather than merely confirming that choice B happens to fit. The new metadata packet stores these computed distractor witness values **without reproducing their original option text**.

The nine canonical custody *component categories* are each assigned an explicit **VISUAL ONLY** or **NOT PRESENT ON VIEWED ITEM** sighting status. This is not a source-fidelity proof against retained bytes; no genuine PDF was acquired in a restricted workspace and no digest, stable original item locator, rights grant or publication approval exists.

`REVIEW_MODE: SELF_REVIEW`; `PRINCIPAL_INDEPENDENCE: NONE`. Under the Owner's self-check/spot-review-only instruction, no independent reviewer is claimed or requested for this research/engineering pass. Authentic-source rights and protected product admission remain outside this spot-check.

## Custody decision: SOURCE_CUSTODY_HOLD

- Still absent: privately retained original bytes + SHA-256 + stable restricted receipt, verified item-level byte/page locator, independently checked seven source component classes, verified printed-key record reconciled with mathematics, reproduction or external-reference rights disposition, independent custodian/math/reviewer record and authorized product admission.
- The accompanying JSON explicitly records every absence. A visual page inspection is insufficient to mark any component **VERIFIED** or claim rights.
- No Core2 product, preview, public link, QRT approval, search/Atlas entry or release is created by this PR.

## Repeatable falsifiers

Run `python TEST/imo-research/validate_core2_pilot_hold.py` and
`python -m unittest discover -s tests -p 'test_imo_core2_pilot_hold.py' -v`.
The first crosschecks the immutable 68-position source ledger against the selected
pilot's PDF locator/printed-key observation and independent arithmetic.
The tests deliberately mutate the source ID, PDF page, key, arithmetic, unique-choice witness, all nine sighting categories,
source rights, digest, source components, publication and denominator; each
such mutation must **FAIL**. This check itself is research-only.

**Future continuation:** authorized restricted-source acquisition and rights review first; document-bound question/answer/figure fidelity comparison by authorized spot-check next. Replace the HOLD packet only through a separately reviewed custody decision and accompanying tests, never by changing this test's expected rights/key values to make promotion pass.

REVIEW_MODE: SELF_REVIEW
PRINCIPAL_INDEPENDENCE: NONE
