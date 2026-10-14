# Owner v3.1.0 — integrated five-Core page ↔ named QRT decision identity (UNSIGNED)

Outcome: O2 (prerequisite only)
For the user: No released learner experience changes. The existing five Owner-golden TEST pages now have one exact-source decision handoff distinguishing two assessed questions from three support roles; **no QRT verdict is inserted**.
Proof: [Sole renderer/frozen golden exact-head run 38219621844](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38219621844), [owner golden lock](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json), [identity regression](../../../tests/test_imo182_owner_v31_qrt_identity.py).

## Governing task and source boundary

Owner master: [Common/main `relay/AIM/IMO-CORE-BLUEPRINTS.yaml`](https://github.com/reallakshman19/Common/blob/main/relay/AIM/IMO-CORE-BLUEPRINTS.yaml), **v3.1.0 / label_sha `2ff9246` / git blob `5c8457bdef4a7019c29f90668fe3b51118a4a7ff`**.

> O2 Each page serves a named QRT cell and that cell has an accepted decision.

This file **does not** satisfy the second half of O2. It is a source-to-page nomination list with blank academic/Owner fields; an engineer cannot declare the cell accepted by detecting a string in HTML. The Owner's O1 task is to use the already registered blueprints and **only `Shared/tools/render_core.py`** against the immutable 12 October golden.

**Exact reviewed tree:** draft [#189](https://github.com/reallakshman19/Grade9v3.5/pull/189) `6307e5dd97f9ae72a052fc7f3e88c368a4cc5434` (unmerged). Golden source package [`TEST/imo-research/pilots/imo182-core2b-transfer-pilot.v1.json`](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/TEST/imo-research/pilots/imo182-core2b-transfer-pilot.v1.json), git blob **`cd5ef962f47808a05cfebec3a8a4f836ef0695cf`**, byte-identical to the Owner golden's frozen `records.json`. Actual role-selection [manifest](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/TEST/products/imo-182-five-core-integrated-review.manifest.json), git blob `61c139829a4663e43689de313eb25fa0f265386d`. Existing registered role goldens are under [`G-IMO-G9-FIVE-CORE-20261012`](https://github.com/reallakshman19/Grade9v3.5/tree/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/). Native renderer [hosted exact-byte replay](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38219621844) PASS; **5 Core role pages + index, 0 source-reference gaps**. Do not replace this with hand-made HTML.

## Exact question-bearing versus supportive roles

| Frozen role / registered blueprint | Frozen HTML SHA256 | Actual role source → proposed QRT link | Decision state |
| --- | --- | --- | --- |
| [Core1](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core1.html) — `BP-CORE1-ORIENTATION@1.1.0` | `f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e` | Concept orientation for the consecutive-factor proof family. **No separately selected assessed question**; whether this supports `QRT-JUSTIFY-D2` and can satisfy per-page O2 requires explicit human/Owner determination. | **PENDING association and decision** |
| [Core1A](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core1a.html) — `BP-CORE1A-CONSTRUCTION@1.8.0` | `c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004` | Teaches the 2-and-3 universal proof; authored worked anchor `Q-TEST-CORE1A-QUAL-G9-WORKED-DIVISIBILITY` (CORE1A exposure). **Support** for Core2A's proposed `QRT-JUSTIFY-D2`, not independent accepted Core1A question allocation. | **PENDING association, protected-exit and decision** |
| [Core1B](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core1b.html) — `BP-CORE1B-RECONSTRUCTION@1.1.0` | `3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562` | Reconstructs the changed ending-at-t divisibility, incorrect sample-proof and reduced two-factor boundary. **No separately selected Core2A/B question**; ask whether this support page may inherit an O2 cell association or needs separate explicit treatment. | **PENDING association and decision** |
| [Core2A](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core2a.html) — `BP-CORE2A-SUPPORTED-APPLICATION@1.1.0` | `e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777` | **Selected authored assessed question** `Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF`, declared primary JUSTIFY, *author-proposed* D2 score 4, `W=MOVE-TEST-CORE2A-WARRANT`: establish universal proof for `(m+1)(m+2)(m+3)` / 6. | **PENDING independently qualified decision** |
| [Core2B](https://github.com/reallakshman19/Grade9v3.5/blob/6307e5dd97f9ae72a052fc7f3e88c368a4cc5434/golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core2b.html) — `BP-CORE2B-TRANSFER@1.1.0` | `91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39` | **Selected authored transfer** `Q-TEST-CORE2B-FOUR-FACTOR-48-BOUNDARY`, declared primary JUSTIFY, *author-proposed* D2 score 4, `W=MOVE-TEST-CORE2B-COUNTERMODEL`: refute universal divisor 48, prove maximal universal divisor 24. **D2 vs D3 is unadjudicated**. | **PENDING independently qualified decision** |

The authored worked/primary/transfer questions are **three distinct IDs** in this one exact source package. `CORE1`/`CORE1A`/`CORE1B` being pedagogical support **does not automatically satisfy O2**. The Core2A/B task IDs are emitted by the respective frozen HTML; role selection is verified against source exposure and manifest by the new test.

**Do not conflate separate D2 streams.** The seven new D2 questions in [draft #191](https://github.com/reallakshman19/Grade9v3.5/pull/191) / [review evidence #205](https://github.com/reallakshman19/Grade9v3.5/pull/205) use distinct `Q-TEST-QRT-JUSTIFY-D2-...` IDs and different exact rendered HTML. They require their own H/S/P/M and qualified decision in [#214](https://github.com/reallakshman19/Grade9v3.5/issues/214); no verdict on those seven imports acceptance into this Owner-frozen five-page product. Likewise, the Owner-frozen Core2A original has an H3 pre-attempt historical state and the separately Owner-directed H3-after-attempt [#190](https://github.com/reallakshman19/Grade9v3.5/pull/190) is **not** allowed to overwrite old frozen bytes; successor designation is a different Owner decision.

## The short decision sequence that unlocks O2

1. **Name and verify an independent qualified reviewer** for *these exact source IDs*: Grade 9 mathematics, cognitive-demand/QRT qualifications, declared author/fixer separation, no conflict, and artifact access. The [#182 Owner decision docket](https://github.com/reallakshman19/Grade9v3.5/issues/182) has a JUSTIFY-D2 qualification question; seven-cell reviewer tasks [#211](https://github.com/reallakshman19/Grade9v3.5/issues/211) and [#214](https://github.com/reallakshman19/Grade9v3.5/issues/214) are **different exact candidate questions** unless a reviewer is explicitly assigned both scopes.
2. **Decide the source-specific cognitive facts**, not just proof arithmetic: Core2A offset from the worked triple and possible copying (JUSTIFY vs APPLY/EXPLAIN, D1/D2/D3); Core2B changed universal 48 claim and 24 maximality (D2 vs D3); whether the stem, worked Core1A, accessible stage, H1/H2/H3 or misconception diagnosis supplies the decisive W; all twelve `H1 H2 H3 S1 S2 S3 P1 P2 P3 M1 M2 M3` must cite the actual page and applicability. [Earlier Core2A direct H3 assessment](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38198786141) is **technical**, not academic.
3. **Owner only**, after independent recorded signoff: assign a per-cell accepted/revise/reclassify/reject decision **with ID/date/exact candidate SHA**; separately decide which of Core1/1A/1B support roles serve a named QRT cell under O2; decide any H3 successor-golden designation without mutating `G-IMO-G9-FIVE-CORE-20261012`. A reviewer can recommend, but cannot sign for the Owner.
4. Preserve scope: no authentic Core2 source rights, merger/publication, real learner data, linked A4 print compliance or whole-repo CI approval follows from an O1 golden match. Original Core1A linked PDF A4 is a known separate blocker; printer changes are not authorized here.

## Copyable unsigned decision receipt — one per question/page association

```text
Role and question ID (supporting role or selected assessed question):
Exact Owner golden snapshot SHA256 / manifest+source git blob:
Candidate QRT cell (PROPOSED, with independent rival/band analysis):
Reviewer name/affiliation/credentials and author/fixer independence:
Conflict-of-interest declaration and signed review date:
Actual role HTML/initial accessible text and H1/H2/H3 before/after attempt:
Independent main + worked + changed-case mathematics check:
Learner protected W, unaided decision, miscue from question/figure/hints:
Difficulty components (all five), primary demand and D1/D2/D3 rationale:
H1:   H2:   H3:   S1:   S2:   S3:
P1:   P2:   P3:   M1:   M2:   M3: (each verdict + exact evidence)
Qualified recommendation ACCEPT/REVISE/RECLASSIFY/REJECT: PENDING
OWNER per-role association and per-cell decision ID/date: PENDING
Successor-golden authority / print A4 / learner study / release: NOT GRANTED
```

**STOP condition:** This docket and its tests **do not alter the canonical accepted-coverage file**. Current snapshot accepted 0/28, no independent sign-off, no Owner QRT decision, no golden mutation; O2 academic acceptance remains **NOT MET**.

```text
LOG | 2026-10-14 | issue=182 | task=one-head-golden-question-role-identity | result=O2_SOURCE_TO_PAGE_PROPOSAL_PINNED; QUALIFIED_REVIEW_PENDING; ACCEPTED_0_OF_28 | aim=v3.1.0 | outcome=O2 | user=no | proof=https://github.com/reallakshman19/Grade9v3.5/actions/runs/38219621844
```
