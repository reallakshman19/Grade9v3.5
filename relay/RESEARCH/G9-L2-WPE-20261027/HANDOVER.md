# Grade9v3.5 · Level 2 Research and WPE Implementation Handover

**Packet:** G9-L2-WPE-REUSE-20261027  
**Date:** 2026-10-27  
**Status:** PREPARED_FOR_OWNER_AND_RESEARCH_DISPATCH — not researched, implemented, academically approved, or released  
**Authority:** Owner-requested research handover; read-only planning. This packet is NOT a V3.1 execution packet, lease, checkpoint, acceptance receipt or change to the current relay state.  
**Location:** `relay/RESEARCH/G9-L2-WPE-20261027/`  
**Repository baseline:** `main@7052691eb97351d1b7e8f22200f733adafb0f13c` (Owner-supplied immutable pin, confirmed at preparation).  
**Primary pilots:** Physics Work–Power–Energy (WPE); Mathematics parallel. JEE Main Chemistry follows.

## 1. Owner intent — preserve verbatim in downstream task briefs

The Owner wants to reuse existing Grade9v3.5 prototypes rather than rebuild the application. NLM was a pilot; **WPE replaces it as the primary Physics vertical slice**. Research JEE Main Physics and Mathematics first, Chemistry later, mapping backwards through explicit later-grade prerequisites to the applicable NCERT/CBSE Grade 9 Standard and Advanced/extension foundations. Olympiad, JEE Advanced and NEET are not active new question-harvesting scopes.

The Owner's operational experience is:

**Canonical Question Bank → Smart Labelling 1 → P1 initial independent assessment → Core2 source/answer exposure → Smart Labelling 2 → QRT primary demand and D1–D4 classification → 12-objective per-question QRT review → governed subject-neutral blueprint + topic adapter → Core1A / Core1B → new independent check.**

This is a *learner/operational sequence*, not a replacement for academic authority dependency: verified Core2 source custody must exist **before** source-backed P1 presentation, even when Core2 guidance is revealed only **after** the attempt. Canonical concept truth is independently owned by the subject library. Existing Core2A/Core2B supported practice and transfer remain available; no new seventh Core.

Success is valid, traceable learner reasoning and reproducible evidence—not harvested volume, cosmetic badge count, cell filling or simulated completion.

## 2. Level 1 is an input, not research to repeat

Owner supplied the preliminary report **“Grade 9 Physics–Mathematics–Chemistry Foundation to JEE/NEET: Auditable Research and Integration Architecture”**. It reports nine output files and the following findings:

| Level 1 finding / output | Mandatory carry-forward | New Level 2 duty |
| --- | --- | --- |
| `source_registry.v1.json` and `discovery_log.v1.json` | Official CBSE 2026–27 Standard/Advanced, NCERT, official JEE Main sources, third-party discovery versus authority distinction | Recover actual source bytes and verify WPE question identities; no full resurvey |
| `curriculum_competencies.v1.json` | Grade 9 Standard/extension versus later-grade bridge separation | Bind seven canonical WPE capabilities and validated Math prerequisites |
| `prerequisite_graph.v1.json` | Explicit edge justifications, bridge lessons, diagnostic criteria | Test WPE and Math edge closure |
| `candidates_manifest.v1.json` | Five-layer candidate structure, source versus academic versus learner versus promotion separation | Add narrow Smart1/P1/Core2/Smart2 handoffs; do not silently replace schema |
| `qrt_coverage_map.v1.json` | 7×4 = 28 QRT cells; candidate coverage is not assessed performance | Independent question-level QRT resolutions |
| `learning_units.v1.json` | First attempts, assistance and fresh-check model | Reconcile actual PR #307/#308 interaction mechanics |
| `quality_and_unresolved.v1.json` | Fifteen falsifier families, missing source hashes, absent full-bank dedup index, copyright, independent review gaps | Reproduce or carry forward unresolved state |
| `integration_contract.md` | Question/bank digest, identity, option permutation and migration expectations | Reconcile real repository contracts and old versus new paths |

**Critical input limitation:** the Level 1 *report text* is supplied in conversation. Its referenced nine-file ZIP is NOT independently mounted or inspected in this handover. Its earlier download link is not proof of present artifact custody. Phase 0 must obtain the original bytes or record `NOT_INSPECTED` per file; do not invent their contents or digests.

**Historical fixtures, not interchangeable WPE corpus:** Level 1 JEE Main Physics QID `695278253` is a rough-incline *prerequisite-boundary* challenge, not authenticated WPE coverage. Level 1 JEE Main Mathematics QID `695278232` is a candidate model/constraint regression; reported `MODEL-D3` remains an independently unreviewed hypothesis. The NEET Chemistry candidate is held and excluded from new JEE Main acquisition.

## 3. Repository and prototype evidence pinned for reuse

- [PR #307 P1 NLM learner page](https://github.com/reallakshman19/Grade9v3.5/pull/307), **draft, unmerged** at `2d6be853071daa10d858ac6edf88bac24eaaff81`. Main sources: `standalone/practice/nlm-p1.html`, `standalone/practice/tests/nlm-p1.test.mjs`. P1 interactive baseline/attempt/reason/confidence/hints/feedback patterns may be reusable; source at this head has 39 embedded NLM records with correct answer A for all 39, and hard-coded baseline/route question IDs.
- [PR #308 P2 session](https://github.com/reallakshman19/Grade9v3.5/pull/308), **draft, unmerged** at `87b49547c84f1cf2e59f5bf0d675b6de56df2f8a`. Sources: `standalone/practice/nlm-p2-session.html`, `standalone/practice/tests/nlm-p2.test.mjs`. Inherits #307; incremental comparison showed only two new P2 files. Seven-stage session flow, fresh attempt, summary and JSON import/export are candidate reuse. `evaluateSkills()` may default “independent” without verifying all underlying scientific claims; fresh check uses limited numeric comparisons; session import is not proven full state resume; learner-authored reflection is interpolated into HTML.
- At these pinned heads, four top-level CI workflows each had failed runs, and there were no submitted PR reviews in the connector review lists. These are **not** proofs that all prototype code is broken: individual failures must be diagnosed.

Use exact-head comparison `main → PR307` and `PR307 → PR308`; never duplicate inherited changes. Re-read live refs if moved.

Canonical grounding: `Physics/library/phy-work-energy-power.v1.json`, `Physics/matrices/phy-work-energy-power.rungs.json`, `Shared/roles/CORE-AUTHORITY-CONTRACT.md`, six Core contracts, `Shared/vocabularies/cognitive-demand.v1.json`, `Shared/vocabularies/learner-question-metadata.v1.json`, `docs/method/QUESTION-REVIEW-MATRIX.md` and subject `DemandReview`/blueprint paths **as actually verified**. Do not assert that the old missing `Physics/adapter/TopicAdapters.v1.json` exists.

## 4. Scope, invariants and red lines

1. No academic truth sourced solely from a model-generated solution or learner's wrong answer.
2. Source custody, normalized question identity, academic interpretation, learner evidence, and release/promotion authority are five different states.
3. One versioned question bank; immutable snapshot digest across JSON/embedded HTML/projection/session attempts. Answer-key changes require version-aware migration, not silent regrade.
4. Source-hint text differs from authored scaffold; reuse only where rights permit it.
5. Smart1 is question-level pre-attempt metadata, not learner diagnosis. Avoid cueing answers or protected W.
6. P1 here means **BASELINE_ASSESSMENT_P1**; QRT `P1` is an unrelated semantic-objective name.
7. Smart2 separates stable question cognition from learner observations; unsupported reasoning or hinted success is not independently demonstrated competence.
8. Primary QRT demands: RETRIEVE / EXPLAIN / APPLY / MODEL / REPRESENT / SYNTHESIZE / JUSTIFY; exactly one primary. Five 0–2 scores yield D1 0–2, D2 3–5, D3 6–7, D4 8–10.
9. QRT semantic review covers H1–H3, S1–S3, P1–P3 and M1–M3, preserving question crux and learner-owned W.
10. Core1A/1B cover the same canonical inferential jumps. Subject-neutral blueprint handles UI; subject adapter validates academic semantics. No 28 textbooks.
11. Research-only reports never confer CI PASS, non-author academic acceptance, merge rights or learner release.

## 5. Dispatchable independent research prompts

Each file is a **complete stand-alone Deep Research brief**. Execute Phase 0 first; then 1A and 1B in parallel; then 2→3→4; 5 checks portability; 6 independently falsifies. Read each file's mandatory inputs and return its named receipt.

| Wave | Prompt | Must consume | Required decision |
| --- | --- | --- | --- |
| 0 | [PHASE-0-EVIDENCE-REUSE.md](PHASE-0-EVIDENCE-REUSE.md) | Level 1 report/nine-file custody + pinned #307/#308 | Which evidence and components actually exist? |
| 1 parallel | [PHASE-1A-WPE-PHYSICS.md](PHASE-1A-WPE-PHYSICS.md) | Phase0 + Level1 sources/graph | WPE source-backed question families and readiness edges |
| 1 parallel | [PHASE-1B-MATHEMATICS.md](PHASE-1B-MATHEMATICS.md) | Phase0 + Level1 Math fixture | Verified Math model/family/bridge and portability baseline |
| 2 | [PHASE-2-SMART1-P1.md](PHASE-2-SMART1-P1.md) | 0 + 1A | Smart1 → PR307 P1 contract and immutable attempt |
| 3 | [PHASE-3-CORE2-SMART2.md](PHASE-3-CORE2-SMART2.md) | 0 + 1A + 2 | Core2 + PR308 Smart2 and evidence integrity |
| 4 | [PHASE-4-QRT-CORE.md](PHASE-4-QRT-CORE.md) | 1A + 3 | QRT reviewed crux → blueprint/adapter → Core1A/1B |
| 5 | [PHASE-5-PORTABILITY-SKILL.md](PHASE-5-PORTABILITY-SKILL.md) | 1B + 2–4 | Math/Chem proof; minimal harvesting-skill amendment |
| 6 | [PHASE-6-INDEPENDENT-AUDIT.md](PHASE-6-INDEPENDENT-AUDIT.md) | all delivered results | Evidence-backed challenge and implementable WBS |

An absent optional source file never triggers invented evidence. It remains an explicit `UNKNOWN` or `NOT_INSPECTED` claim with the next acquisition duty.

## 6. Research → implementation bridge

Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for full ownership, gates and candidate work packages. The proposed order is:

| Work package | Existing assets to reuse | Acceptance boundary |
| --- | --- | --- |
| WPE-REUSE-01 | Extract PR307 P1 and PR308 P2 subject-neutral mechanisms on separate candidate branch | Exact ancestry, no NLM semantic leakage, independent tests |
| WPE-REUSE-02 | P1 initial assessment engine | Smart1 eligibility, semantic options, immutable digest-bound first attempt, no answer leak |
| WPE-REUSE-03 | Core2 + PR308 seven-stage session | Separate custody, Smart2 question/learner evidence, checked reasoning and help status |
| WPE-REUSE-04 | Existing QRT, blueprint and Physics adapter | Reviewed 7×4 classification and H/S/P/M → complete Core1A/B concept mapping |
| WPE-REUSE-05 | Existing regression/browser pattern | Academic falsifiers, fresh transfer, browser/GPU, independent non-author review |

**No implementation, branch product edit, merge or learner acceptance has occurred in this handover.**

## 7. Handover receipt contract for each researcher

Each phase must return a machine-readable receipt with at least:

`phase_id`, `research_status`, `exact_repository_refs`, `level1_artifacts_consumed`, `level1_findings_reused`, `new_source_evidence`, `research_outputs`, `output_digests`, `independently_verified_claims`, `unresolved_claims`, `next_phase_inputs`, `research_only: true`.

Use separate `PASS/PARTIAL/FAIL/UNKNOWN` evidence verdicts versus `SPECIFIED_NOT_IMPLEMENTED` runtime state. Require file/line/URL source references, no fabricated exact digest or independent-review signature.

## 8. Open evidence duties at handover

- Original nine Level 1 files: **NOT_INSPECTED in this handover**, pending real receipt.
- Official original PDF byte digests absent in Level 1 artifact writer: **UNVERIFIED_BYTE_HASH**.
- The exact external JSON vs embedded HTML bank mismatch historical pair: **NOT_REPRODUCED**, despite demonstrated risk class.
- Full canonical dedup scan: **UNKNOWN / unresolved**.
- Authentic WPE JEE Main source/question-key identities and answer derivations: **not yet acquired in this packet**.
- WPE capability records are candidate status in inspected library; no automatic academic promotion.
- PR307/308 top-level workflows failed; CI root causes not independently established.
- Non-author review on #307/308: none recorded at the inspected heads.
- Old TopicAdapters and standalone practice paths in Level 1: missing/unverified as reported; verify actual replacement contracts.
- Rights-aware storage and publication permissions must be checked per source.
- Chemistry's earlier NEET candidate stays held, not silently reused as JEE Main.

## 9. Ownership / authority separation

This research packet is an Owner-requested proposed handover stored *beside* the live `relay/` tree. Existing `relay/PROTOCOL_SELECTION.yaml` selects V3.1; `relay/STATE.yaml` and `relay/GENERATED/HANDOVER.md` are operational/generated state. **Do not edit or claim to supersede them.** Prior `agents/relay/` is read-only history.

The current Owner instruction authorizes publication of this research handover, **not** dispatching an agent, creating a V3.1 execution plan, moving a lease, merging prototype PRs, or accepting teaching content.

**Immediate next action:** dispatch [Phase 0](PHASE-0-EVIDENCE-REUSE.md) to a bounded independent research worker with the real Level 1 artifacts if obtainable. Preserve Phase 0 receipt before starting Phases 1A/1B.
