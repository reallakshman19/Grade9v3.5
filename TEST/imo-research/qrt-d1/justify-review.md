# QRT-JUSTIFY-D1 — sourced candidate, technical/academic review packet

**Issue:** #200 under #182 · **Aim:** Owner v3.1.0 / label_sha `2ff9246` · **candidate PR:** #206 (stacked on #204).  
**Source:** Existing `main/TEST/imo-research/original-practice/seven-cell-original-problems.v1.json`, record `IMO-G9-ORIGINAL-PRACTICE-003`; **model-authored practice, NOT original SOF paper**. Source-quality hold `ALTITUDE_WORDING_CLARITY` remains; not public/admitted. Core2 original source selection is `[]`. Registered blueprints / sole renderer only.

## Independent learner-owned mathematics — proposal, not qualification

- **Primary cell:** `QRT-JUSTIFY-D1` (proposed). Secondary APPLY means evaluating numbers is ancillary; the learner must establish a general warrant, not merely multiply.
- **X:** Establish why two triangles can have equal area even though apex positions and slanted side lengths differ.
- **Y:** Learner already knows `A=(base×perpendicular height)/2` and how to identify a perpendicular altitude to a *line*, including feet outside a base segment.
- **Z:** Match the common 12 cm base and two 7 cm perpendicular heights; decide if those measurements license the conclusion through the area law.
- **Protected W:** Independently select and apply **equal base + equal perpendicular height ⇒ equal area** as the decisive warrant in the presence of a distracting sideways peak offset. Then compute `12×7/2=42 cm²` for both. Initial figure and H1/H2 must not state this deduction or its result.
- **Counterexample:** common base 8 cm, altitudes 5 cm and 4 cm give areas 20 and 16 cm²; common base alone is not sufficient.
- **Independent oracle:** determinant area `|det(B−A,C−A)|/2`, tested against varied positive bases, heights and both horizontal peak positions including offsets outside AB. Converse transfer from `A=36 cm²,b=12 cm` gives both `h=6 cm`.
- **Why D1, provisionally:** base and altitudes are explicit and the required proof is one direct warrant. A D2 item would require selecting among non-equivalent model families, resolving an unstated altitude condition, or chaining additional independent relations. The D1/D2 distinction requires independent academic challenge.

## Role / immutable golden **technique** crosswalk

| Role | Present learner work | Correct technique comparator | Qualified verdict |
| --- | --- | --- | --- |
| CORE1 | Orient to perpendicular altitude vs slanted side and scope of claim | Frozen five-role Core1 T01/T14 | PENDING actual HTML review |
| CORE1A | Distinct 10×4 triangle construction; stages base/height, worked 20 cm², exit with shifted peaks at base 9 / height 6 | Frozen Core1A T02/T03/T11; independent changed-case exit | PENDING actual HTML review |
| CORE1B | Student's incorrect slanted-side dependence, reconstruct via perpendicular altitude, 8 cm base with unequal heights boundary | Frozen Core1B T06/T10/T12 | PENDING actual HTML review |
| CORE2A | Independently justify equal area for shared base 12 and equal altitude 7; H3 restricted until attempt; separate answer | Frozen Core2A T05/T07 (HTML technique not same question bytes) | PENDING browser audit |
| CORE2B | **Converse**: known area 36 and base 12, infer unknown perpendicular altitudes, not repeat area-equality claim | Frozen Core2B T08/T09 | PENDING academic novelty judgment |

Owner-designated `G-IMO-G9-FIVE-CORE-20261012` is immutable and a cross-question semantic comparator only. `G-IMO-CORE2-UI-R1` is **UI-only** and does not apply to this authored Core2A page as an authentic Core2 source-byte oracle. No new golden requested or self-designated.

## All twelve semantic questions — **author hypotheses, not independent passes**

| ID | Technical evidence to inspect on actual HTML | Status |
| --- | --- | --- |
| H1 | Does first help identify given common base and perpendicular altitudes without stating equality? | REVIEW_PENDING |
| H2 | Does second help retrieve the area law yet leave the *claim-to-warrant* application to the learner? | REVIEW_PENDING |
| H3 | After a written attempt, does the third open the route and keep provenance clear without leaking on blank input? | BROWSER_PENDING |
| S1 | Does initial two-peak diagram show only common base and altitude measurements and no `42 cm²`? | SOURCE_CHECKED; BROWSER_PENDING |
| S2 | Does staged 10×4 Core1A worked representation teach the area-height relation with different numbers? | BROWSER_PENDING |
| S3 | Does 9×6 exit test a changed diagram and proof independently? | ACADEMIC_PENDING |
| P1 | Does SVG title/desc, hidden state, AX text, print and preattempt hint DOM all protect W? | SOURCE_CHECKED; BROWSER_PENDING |
| P2 | Is the Core1A alternate worked law sufficient support for the identified gap, not a copy of target? | ACADEMIC_PENDING |
| P3 | Does nonblank commitment open decisive warrant and full solution distinctly, never prematurely? | BROWSER_PENDING |
| M1 | Is the slanted-side/sideways-offset misconception concrete and genuinely plausible? | ACADEMIC_PENDING |
| M2 | Can the wrong-side hypothesis be distinguished from simple arithmetic error rather than assumed diagnosed? | ACADEMIC_PENDING |
| M3 | Does the repair show a valid perpendicular-height relation and does the 8×5 versus 8×4 boundary falsify overgeneralisation? | ACADEMIC_PENDING |

## Stop conditions and classification

- **INPUT / academic:** A generic triangle area computation without a justified equality conclusion is not `JUSTIFY`. If target W is leaked by H2, alter this source-specific H2 first, not the global blueprint. If no meaningful learner decision remains, reclassify/re-author after qualified demand review.
- **RENDERER:** Only measured stage-gate failures or missing required roles with valid input justify renderer investigation. No generic blueprint optimization requested.
- **ORACLE:** Do not expect different question HTML to byte-match the frozen golden; compare staged techniques and actual learner work.
- **SOURCE RIGHTS:** Authored `IMO-G9-ORIGINAL-PRACTICE-003` is not SOF source material. Wording/altitude accessibility still requires QA, plus originality/rights review before any product admission.
- **OWNER:** Qualified independent reviewer name, conflict declaration, H/S/P/M verdict, Owner QRT decision ID, golden designation ID, rights decision and release decision are all **PENDING**. Academic accepted numerator stays **0/28**.

**Technical QA requirement:** Native five-role `render_core/2` PAGES artifact, independent index + five role SHA-256 receipt, immutable golden lock test, actual pre-/post-attempt browser and viewport screenshots. No claims from authored records alone.
