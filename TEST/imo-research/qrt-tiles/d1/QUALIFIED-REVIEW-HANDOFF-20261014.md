# IMO QRT D1 — qualified reviewer decision packet

**Issue:** [D1 #200](https://github.com/reallakshman19/Grade9v3.5/issues/200); [parent #182](https://github.com/reallakshman19/Grade9v3.5/issues/182).
**As of:** 2026-10-14 UTC.
**Scope:** Exactly **QRT-SYNTHESIZE-D1** and **QRT-JUSTIFY-D1**. This is a **source-safe authored TEST review handoff**, not an examiner question reproduction, academic conclusion, learner study, Owner acceptance, promotion, merge, or release.
**Current academic status:** two pending qualified reviewer verdicts; Owner QRT decisions **0/7 D1, 0/28 overall**. Reviewer identity, credentials, conflict declarations, actual learner observations, and Owner decision IDs are **NOT SUPPLIED**. No agent may fill them by inference from green CI.

## 1. Independent reviewer identity and evidence contract (must be filled by real reviewer)

| Required declaration | Reviewer entry |
|---|---|
| Name, contactable GitHub username | **UNASSIGNED** |
| Mathematics / grade-9 pedagogy / QRT demand qualifications, verification reference | **UNVERIFIED** |
| Did you author or fix either candidate question, scaffold, diagram, learner projection, or grading rubric? Describe all relevant work | **NOT DECLARED** |
| Independence / conflict-of-interest statement for *each* cell | **NOT DECLARED** |
| Learner/test population, prior teaching, item order, dated observation IDs, if behavioral claims are made | **NONE GATHERED** |
| Native artifact examined, device/viewport, source SHA, reviewer date and signature | **NOT EXAMINED BY QUALIFIED REVIEWER** |
| 12 H/S/P/M decisions + mathematical warrant + primary demand + D1/D2 verdict per cell | **PENDING** |
| Owner ACCEPT / REVISE / REJECT decision ID (separate from reviewer, requires Owner action) | **NULL** |

Review **source and rendered learner behavior separately**. A file passing JSON parsing, SHA comparison, H3 nonblank gating, or one of the existing math oracles cannot establish that the student has learned, justified, or synthesized. The signer must make a cell-specific, reasoned verdict; no blanket acceptance.

## 2. Exact evidence; authored/test-only, not current product release

| Cell | Immutable authored source at artifact-producing commit | Native five role + index artifact | Review records |
|---|---|---|---|
| SYNTHESIZE-D1 | [`synthesize.v1.json` at `c967ff2`](https://github.com/reallakshman19/Grade9v3.5/blob/c967ff226516de25d6235c6c0f1749b39ffced7d/TEST/imo-research/qrt-d1/synthesize.v1.json), Git blob `f9008c6dc4642d45798d23ddd06a51a4a33f540b` | [run 38427757190, artifact 11828784099](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38427757190/artifacts/11828784099) | [Demand contrast](synthesize-demand-contrast.v1.json), [bridge ablation](synthesize-bridge-ablation.v1.json), [tile](synthesize.tile.v1.json) |
| JUSTIFY-D1 | [`justify.v1.json` at `d28ac2b`](https://github.com/reallakshman19/Grade9v3.5/blob/d28ac2bea348412a0451d226e278d01531839932/TEST/imo-research/qrt-d1/justify.v1.json), Git blob `0738dcc7390cee08e03ec672a698fc8b4bc4ea2f` | [run 38393136211, artifact 11810416794](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38393136211/artifacts/11810416794) | [16 authored probes](justify-reasoning-probes.v1.json), [blank reviewer worksheet](justify-feedback-review-sheet.v1.json), [tile](justify.tile.v1.json) |

Both are bound to registered five-role blueprint techniques and original frozen Owner lock `G-IMO-G9-FIVE-CORE-20261012` (lock blob `888678554c41257e6d96c802f0009983ccbb5328`); compare **semantic technique** across different questions, not identical HTML bytes. Native HTML is created by the sole `Shared/tools/render_core.py`. Review records report six SHA-256 page digests and zero gaps; the reviewer must inspect the **actual** role pages and accessible/hidden/print behavior before any signoff. Separate review-only PR chain [#208](https://github.com/reallakshman19/Grade9v3.5/pull/208) → [#223](https://github.com/reallakshman19/Grade9v3.5/pull/223) → [#228](https://github.com/reallakshman19/Grade9v3.5/pull/228) → [#231](https://github.com/reallakshman19/Grade9v3.5/pull/231) is **not** the learner source stack [#213](https://github.com/reallakshman19/Grade9v3.5/pull/213).

## 3. SYNTHESIZE-D1: falsify the primary cognitive claim first

**Authored target:** four identical units, each with 3 blue and 2 red tiles, total 20; `4(3+2)=20` and `4·3+4·2=20` are both correct and must receive fair treatment. `3+2·4=11` only counts one of the three-blue contributions; **nine blue tiles** from the other three units are omitted. Computation alone is not the SYNTHESIZE W.

**Important source-specific challenge:** preceding Core1A already demonstrates `3(2+1)=9` with three identical badges, two circles and one triangle. Thus a student could be using a transferred **known equal-groups model** instead of independently coordinating a difficult dependency. The canonical distinction is SYNTHESIZE **dependent route/ordering decision** versus MODEL **governing model choice** versus APPLY **execute known model**. The claimed protected move and D1 rating are both **hypotheses**, not endorsed verdicts.

Run the existing [five-control bridge-ablation protocol](synthesize-bridge-ablation.v1.json) without giving B (intermediate = 5) before the original A in a way that teaches the answer:
- **A original** `4(3+2)=20`: ask the learner to explain an independent bridge; do not reward a number alone.
- **B supplied bridge** four groups of five, also 20: compare whether A contains any meaningful additional learner-owned choice after exposure is controlled.
- **C prior worked lesson** `3(2+1)=9`: explicitly record whether C was shown/taught, and whether the MODEL-D1 six-trays task preceded A.
- **D conceptual misconception** `3+2·4=11`: ask *which physical tiles are omitted*, not only where parentheses go.
- **E changed-composition counterfactual** three 5-tile units plus one 4-tile unit = 19: exploratory comparison only, not an adopted reauthoring or automatic D2 label.

**Required discriminating finding:** If A collapses to C plus trivial `3+2` and B is essentially identical once the unit size is stated, SYNTHESIZE as the *primary* protected demand is **not supported by that test**. If genuinely new coordination remains, state the precise dependency and why it cannot be explained as routine MODEL or APPLY. A performance difference alone may indicate basic addition difficulty. Count operations **never** determines D2.

Record one of `RETAIN_SYNTHESIZE_D1`, `RECLASSIFY_MODEL_D1`, `RECLASSIFY_APPLY_D1`, `RECLASSIFY_DIFFERENT_BAND`, `REAUTHOR_FOR_GENUINE_SYNTHESIZE`, `REJECT_TECHNICAL_CANDIDATE`, with observed evidence; leave **PENDING** until a qualified decision. No reassignment is authorized by this packet.

**Semantic checklist:** Judge H1/H2/H3, S1/S2/S3, P1/P2/P3, M1/M2/M3 **individually** using specific prompts in [the 84-ask dossier](semantic-challenge-20261013.v1.json). Special risk: Core1A might already perform the exact critical bridge; Core2A H2 must not tell learners to multiply both component counts; accessible SVG/title and print must not expose 20 before nonblank attempt; after-commit feedback must recognize both expressions. [Demand contrast](synthesize-demand-contrast.v1.json) contains six original falsifiability questions and three still-unresolved competing hypotheses.

**Reviewer result:** primary demand **PENDING**; D1/D2 band **PENDING**; twelve objectives **UNSIGNED**; participant observations **NONE**.

## 4. JUSTIFY-D1: assess actual reasoning, not a correct-looking number

**Authored target:** two triangles have the **same 12 cm base AB**, and their peaks may be shifted sideways but are **7 cm perpendicular distance to the straight line through AB**, including the *extension* beyond the endpoints. Mathematical equality warrant: `A=bh/2`, so each area is `12·7/2=42 cm²`. Independent proof by determinant or horizontal shear is acceptable. This is primarily JUSTIFY only if the student explains the reason; `42 cm²` alone is insufficient. The current author-side quality hold `ALTITUDE_WORDING_CLARITY` is **OPEN**.

Use [the 16 exact response probes](justify-reasoning-probes.v1.json) and [the blank R1–R5 manual worksheet](justify-feedback-review-sheet.v1.json). Deliberately test categories:
- `valid_direct`, `valid_det`, `valid_shear`: mathematically valid *different* warrants; don't keyword-match.
- `numeric_only`, `answer_without_reason`: correct output/conclusion without equality argument; request a warrant, don't mark full JUSTIFY.
- `same_base_only`: wrong generalization. Equal base with heights 5 vs 4 yields unequal areas; it is *not* repaired by checking units.
- `wrong_slanted`, `outside_foot`: the height is the perpendicular to the **infinite base line**, not a sloping segment; ask whether text and figure convey this.
- `wrong_number`, `wrong_unit`: separate valid argument from lost factor 1/2 or cm vs cm².
- `wrong_transfer`, `valid_transfer`, `counterexample`: a changed inverse problem `h=2A/b=6` or valid falsifier should not be rejected for unlike template wording.

**Human comprehension test:** show the current authored stem and the actual Core2A SVG at relevant viewports. Ask participants to identify the height line when the perpendicular foot is beyond AB. Record spontaneous explanation and any confusion; do not lead them with “extend AB” during the probe. Compare accessible SVG labels/alt text with text. Real session IDs, count, reviewer interpretation, confidence and wording-change decision must be entered. Do **not** fabricate a comprehension pass from static code inspection or test the change by silently altering the native stem.

**Feedback gate:** evaluate proposed *after-commit* responses case by case for correctness, specificity, valid proof alternatives and whether the student must supply an explanation. The renderer only gates H3 on a nonblank attempt; it is **not an AI proof evaluator**. Do not award human feedback quality based on that mechanism.

**Semantic checklist:** Individually record the twelve exact H/S/P/M questions in [the 84-ask dossier](semantic-challenge-20261013.v1.json); particularly H1–H3 timing, S1 extended baseline legibility, P1 accessible precommit leakage, P3 wrong/nonblank justification, and M2 distinction between number and proof.

**Reviewer result:** sixteen probe categories **AUTHOR-SUGGESTED, NOT HUMAN CONFIRMED**; student comprehension **NOT RUN**; academic JUSTIFY verdict **PENDING**; altitude-quality hold **OPEN**; Owner decision ID **NULL**.

## 5. Signoff structure and Owner decision queue

One signed record **per cell**, with:
1. Reviewer name, verified qualifications, contactable GitHub ID, full author/fixer/related-review conflict disclosures, scope and date.
2. Exact source commit/blob, actual six-role HTML artifact/sha and inspected 390/768/1366 viewports, accessible precommit and H3 after nonblank; explain exceptions.
3. Independent mathematics correctness, acceptable alternatives, false routes/counterexamples and changed-case behavior.
4. Primary QRT demand verdict against plausible MODEL/APPLY alternatives; D1-vs-D2 grounds, not operation count.
5. Twelve separately reasoned H1–H3/S1–S3/P1–P3/M1–M3 decisions with linked evidence; for JUSTIFY include 16 probe judgments and real altitude comprehension evidence, or explicitly *unresolved*.
6. Final **ACADEMIC_PASS / REVISIONS_REQUIRED / ACADEMIC_REJECT**, signature and supporting evidence IDs. An unresolved blocking quality concern cannot be silently waived.
7. Only **after** an eligible verdict, ask Owner for explicit cell-specific `ACCEPT / REVISE / REJECT` plus decision ID. Owner golden version, original source permissions, merging and publishing are separate later decisions.

**Current disposition as published:** HUMAN_REVIEW_NOT_STARTED; QUALIFIED_REVIEWER_UNVERIFIED; OWNER_QRT=0/7, 0/28; REVIEW_BRANCHES_UNMERGED; RELEASE_HOLD. Every link, test and author check here is a source for the human assessor—not a substitute for one.
