# B1 producer benchmark / frozen-candidate notes — NLM-PROD1

**Authority:** OTM-NLMP1-P1-2210 / Oracle G9O4-2-p1, WBS 1.1/M0, benchmark B1.
**Review target:** draft PR #306, branch `codex/nlm-first-interaction`, source base `7052691eb97351d1b7e8f22200f733adafb0f13c`.
**Status:** PRODUCER SELF-ASSESSED ONLY; independent IR-G9V35 review outstanding. This report is not an acceptance.
**Provenance:** personally usable questions from an **independently authored bank**; not verbatim exam questions. Benchmark exam PDF wording UNKNOWN.

## Covered experience

- Source IDs: `PHYS-NLM-001` (slowing descending lift), `PHYS-NLM-002` (force pair at robot A's strap connection); unique coverage **2 of 39**.
- First exposure: 001 unaided diagnostic, 002 unaided diagnostic, then 001 supported **already-seen repeat**; no unseen transfer inference.
- For each diagnostic: one selected letter, reason in learner's words, confidence/uncertainty, timestamp, with `assisted:false`; no hint/reveal or keyed feedback in the pre-diagnostic UI.
- Supported 001: repeat answer capture with assistance state, authored CLARIFY H1 / CORRELATE H2 / OPEN_THE_WAY H3, selected-option feedback after an attempt, explicit teacher reveal, original bank hint text only after deliberate teacher reveal, help-event timestamps, exported session JSON, reset confirmation.
- No learner observations have been supplied. Student use, learning, misconception diagnosis and mastery: **NOT_RUN / UNKNOWN**.

## Pinned custody

Original full rows are intact in `source-rows.v1.json`, including author, ID, stem, options, zero-figure fields, original bank hints, proof, answer and QRT metadata. Bank `TEST/physics-research/question_bank_mechanics_grade9.v1.json` is pinned at `455103ad312ab8b6627aa7a1199b0bd7d5b0af8e`: SHA-256 `c87ad141e4db355276b8ae4e2afb925663b12d5b0e55761df763ee1c7b387685`, 246304 bytes. Verified the **seven manifest files** against their stated SHA-256 and byte lengths through connector UTF-8 retrieval in this agent turn. Source per-row digest over compact JSON is checked by `benchmark.mjs`. Original bank and Shared were not modified.

Adaptation is explicit, one display variant per source ID:
- `PHYS-NLM-001-PU1`: source answer A stays A. Adapted options A “Toward the roof.”, B “Toward the floor.”, C “Zero net force.”, D “Cannot be determined.” Original longer reason-bearing options remain untouched in custody; original stem/conditions/figure unchanged.
- `PHYS-NLM-002-PU1`: options rewritten into parallel actor–action statements; source correct A maps to display C. New display order A gravity/A, B A/B both pull strap, C A pulls strap/strap pulls A, D strap/floor both on A. Original stem, 40 N force, left/right orientation and zero-figure fields unchanged; original full source choices preserved. No additional bank question counted.

## Science and demand review (SELF-ASSESSED, not a verdict)

001: A descending lift with diminishing downward speed has velocity `v_y < 0` increasing toward zero, so `a_y=Δv_y/Δt > 0`. With `m>0` and `ΣF_y=m a_y`, the net force is upward (toward roof). Under constant descending velocity, acceleration and net force would be zero. Source APPLY-D1 is provisionally plausible: execute two familiar signed-motion/Newton-II relations for one direction, with REPRESENT supporting the sign translation. H1–H3 avoid naming upward acceleration explicitly; the original bank H1 **does** reveal the decisive physics and is withheld until the deliberate solution reveal.

002: At A's connection the force of A on strap is left 40 N; the same connection produces strap on A right 40 N. Equal/opposite forces act on **different bodies**. Robot A-on-strap and B-on-strap are both forces on one recipient and cannot be that third-law pair. The source claims EXPLAIN-D1; the selection itself is a **classification** (proposed RETRIEVE-D1). A typed explanation may be inspected separately, not auto-graded. This disagreement is for Oracle reconciliation; original metadata is not overwritten. D1 plausibly fits one pair-identification decision; difficulty is not inferred from option length or number of clicks.

## Mechanical cue screen — equivalent to Common nd_item_cues.py

Tool algorithm: case-folded Unicode word-set overlap with question, key-only shared words; whitespace option word counts; longest-key and reasoning-marker (because/therefore/since/thus/hence) checks; no arbitrary max-words threshold. For the final **display** options:

| Variant | Correct | A/B/C/D word counts | SHARED_WORD_KEY_ONLY | LONGEST_KEY | REASONING_KEY_ONLY |
| --- | --- | --- | --- | --- | --- |
| 001-PU1 | A | 3/3/3/3 | no | no | no |
| 002-PU1 | C | 7/8/8/8 | no | no | no |

**Manual dispositions:** both option sets have parallel response forms and require applying signed-motion physics / two-body interaction ownership respectively; 001 options are neutral directional choices, 002 remains a conceptual pair classification rather than automatically becoming EXPLAIN because of the form. Position is varied (A then C), but no two-item pilot demonstrates immunity to guessing. A clean mechanical screen is **not** a subject-quality, demand, or learner verdict. IR should test for residual semantic cues and hint usefulness.

## Executed verification and required negative cases

**Executed (real GitHub readback, agent-side JavaScript assertions; not Node/Playwright):** 15 PASS, 0 FAIL. Checked source IDs, denominator, preserved original options, keys A/C, original stems/figure, scaffold roles, exact embedded data, separate source hints, pre-baseline disclosure guards, download/reset code, and no mechanical cue flags. Synthetic negative controls were deliberately introduced **in memory**: wrong display key and premature visible answer disclosure triggered the corresponding guards. Source ID/contents mutation controls are also retained in runnable `benchmark.mjs`.

**Reproducible command in a complete checkout:** `node Physics/content/nlm-personal-use/benchmark.mjs`. Runs per-row SHA-256 identity test, pinned-bank exact-row comparison through `git show` when S exists locally, payload fidelity, JS syntax, gated baseline/attempt hints, and four negative controls (ID, stem, early answer, changed display key). The `git show` comparison is labelled NOT_RUN if a shallow checkout lacks S. It does not fake a pass.

**Actual UI test command in a Python Playwright environment:** `python Physics/content/nlm-personal-use/benchmark-browser.py`. Opens `standalone/practice/nlm-core2-first-slice.html` from disk (no web server needed), performs synthetic baseline A/B choices with explanations and uncertainty, checks withheld hints, opens H1-H3, submits assisted repeat, reveals teacher/source hints, exports and inspects JSON, and confirms reset and absence of page script errors.

**NOT_RUN in producer environment:** Node executable invocation against an actual local repository checkout; Chromium/Playwright interaction of exact GitHub candidate; real learner attempts; CI/checker verdict. Cause: producer can read/write the public repository through a connected GitHub tool but cannot clone it into the local Linux execution container (outbound DNS unavailable). The separate remote browser connector reported not connected. The available local Chromium installation does not, on its own, establish that this *remote file* was executed. These are blockers to **verification claims**, not evidence the page works. Do not interpret the 15 static assertions as UI tests.

## Known falsifiers / hold

Wrong sign or force-pair ownership; any unannounced change from bank row to display; a correct answer visible before either baseline attempt; assistance marked independent; failure of the HTML in a real browser; any hint giving away the protected direction prematurely; or an independent reviewer showing answer-by-wording on a final option would overturn affected claims. The hint ladder's learner usefulness is unproven, and needs the independent IR walk. UI interactions and actual student learning remain NOT_RUN.

No change outside `Physics/content/nlm-personal-use/` or `standalone/practice/nlm-core2-first-slice.html`. No changes to the bank, Shared, parked PR #299, other subject, or Progress page. PR #306 is draft and must remain unmerged until separately checked.
