# IMO #182 — R7-02 exact-head cross-band CI attribution (Agent A, 14 Oct 2026)

**Status:** SOURCE-SAFE READ-ONLY AUDIT committed on existing #230 integrator draft branch; NOT a repaired CI gate, academic approval, QRT admission, Owner decision, merged PR, or released learner page.
**Parent/authority:** [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182), `IMO-CORE-BLUEPRINTS` v3.1.0/`2ff9246`; execution workpack [Common G1 r7 takeover](https://github.com/reallakshman19/Common/blob/0b7ccdf9edb9c888fa959e4459969da4958e9c69/coordination/Session_Oct09/Tab8_imo_182_integrator/plans/2026-10-14-g1-r7-d1-d4-cross-band-takeover.md). No access or rights to Track B authentic 68 questions conferred.

## Exact source custody read-back

| Lane | Live draft head at audit | Immediate PR base | Scoped status | Full guardrails | Full canonical assurance |
|---|---|---|---|---|---|
| D1 [#244](https://github.com/reallakshman19/Grade9v3.5/pull/244) | `4caa228b3ac99964110ff4466c147c0253726cdd` | #238 `cbed195cdda74e8dcf7ff3c6bb450a392d6f6f40` | 451 focused source tests + research seed SUCCESS | [38515765785](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38515765785) FAILURE | [38515765833](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38515765833) FAILURE |
| D2 [#245](https://github.com/reallakshman19/Grade9v3.5/pull/245) | `d450d0f0cda25c51c0232db31e6592588634a90b` | `5a9a77416105c37fa716a5e72e8903392ca500c4` | [model native 38517197094](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197094) and [7-cell browser 38517197113](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197113) SUCCESS | [38517197091](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197091) FAILURE | [38517197043](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197043) FAILURE |
| D3 [#224](https://github.com/reallakshman19/Grade9v3.5/pull/224) | `dfe4bb6766b87132423b01ffaa914ade1145424f` | `40142fe06818e7a946d6296911d495f3f3323b12` | [Core2B native 38516946480](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38516946480) SUCCESS | [38516946736](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38516946736) FAILURE | [38516946572](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38516946572) FAILURE |
| D4 [#242](https://github.com/reallakshman19/Grade9v3.5/pull/242) | `fa0b34d1a5ee0a8a7188c2c4871854e0b087d75c` | `74274531456e1cdffc3ddb0b97bb67e07a6f3d90` | [RETRIEVE native 38514455419](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38514455419) SUCCESS | [38514455425](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38514455425) FAILURE | [38514455489](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38514455489) FAILURE |
| Integrator [#230](https://github.com/reallakshman19/Grade9v3.5/pull/230) | `0e3d06aeee2e1bd4acbe47caaf7cd6dfaf442bb4` (pre-audit) | `59031c2a9ea5cdfa71c6d195c3d20e807f3ddfc0` | [28-row viewer 38519253490](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38519253490) SUCCESS, 16 tests, 84 browser selections | [38519253486](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38519253486) FAILURE | [38519253483](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38519253483) FAILURE |

All four PR heads and #230 were independently refetched from GitHub at this audit; draft/open/unmerged. These CI results are tied to the **listed previous heads**. Any new audit commit requires a new exact-head check before discussing present-head CI.

## Completed canonical regression deltas: exact failed test IDs, not pass counts

Every entry comes from the **completed GitHub canonical-assurance regression-delta job logs**, not from an in-progress estimate. Columns `new/fixed/still` are **against the named comparison**, not unique defects or true code-causation proof.

| Lane | vs its actual immediate PR base | vs separately pinned main | Delta job |
|---|---|---|---|
| D1 #244 | **40 new / 2 fixed / 149 still** | **44 new / 21 fixed / 145 still** | [115694087677](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38515765833/job/115694087677) |
| D2 #245 | **0 new / 0 fixed / 153 still** | **7 new / 20 fixed / 146 still** | [115698542955](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197043/job/115698542955) |
| D3 #224 | **1 new / 15 fixed / 153 still** | **8 new / 20 fixed / 146 still** | [115697782149](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38516946572/job/115697782149) |
| D4 #242 | **0 new / 0 fixed / 153 still** | **7 new / 20 fixed / 146 still** | [115689989531](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38514455489/job/115689989531) |
| Integrator #230 | **0 new / 0 fixed / 153 still** | **7 new / 20 fixed / 146 still** | [115704929734](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38519253483/job/115704929734) |

**Causal caution:** D1 40/44 `NEW` is a genuine red gate requiring triage, but not evidence that all failures were *created* by the one-commit source change. Independent GitHub compare `cbed195c...4caa228b` is **ahead 1, seven touched paths exclusively in TEST**: `TEST/adapter/CoreContracts.json`, `TEST/library/imo-g9-divisibility-core1a.v1.json`, TEST candidate validator/reviewer/guide files, and one candidate test file. Many failing test IDs reference topic-atlas, core-learning templates, generated web data, tool manifests or workbench runtime outside these seven files. Their provenance must be separated among changed TEST inputs, stack/base differences, dependent generated projections, and runner nondeterminism before patching. In particular, new `setUpClass` failure IDs do not by themselves isolate a TEST source-contract fault.

**D3's one new immediate-base ID:** `test_renderer_inventory.RendererInventory.test_every_renderer_in_main_is_classified`; technical owner to reproduce independently and determine whether #224 added a source-local renderer inventory expectation or it is fixture/environment coupling. No assertion of cause yet.

**Recurring independent finding group:** all five canonical runs report **20 new canonical assurance findings against the installed ledger**: 18 `LIB-MATH-LINEAR-EQUATIONS` unresolved reference IDs, plus `STRUCTURAL_VALIDITY/SCHEMA` for `LIB-MATH-LINEAR-EQUATIONS` and `LIB-MATH-POLYNOMIALS`, and zero pages worse than ledger in the completion transcript. Repeated signatures across independent drafts are **not proof of a shared new commit**; identify which catalogue/fixture/baseline version owns them before making a change, never waive.

## D1 exact source contract — module-owner decision still required

Read `TEST/adapter/CoreContracts.json` at blob `60faad638b9d521dc72c56ba5dbe2eb7f90090f1`: `TABLE_OF_VALUES` status **PROPOSED**, explicitly no TEST renderer, publication or curriculum implementation. Source package `TEST/library/imo-g9-divisibility-core1a.v1.json` blob `9bea526da445d8c71a726228ffc10999f44c1d7e` contains **four author-created CANDIDATE `data` inputs** (MathML positive-integer domain; dimensionless 24 divisor; MathML residues 0–23; MathML symbolic product) and exit oracle bindings to their declared IDs, with local candidate checker and 24/24 residue proof. This is **not approval** that the generic library/renderer/adapter accepts the semantics; author-validator PASS and 451 scoped unit tests cannot promote PROPOSED to IMPLEMENTED. Its declared visual `scene_instances=[]` and `rendered_asset_refs=[]`: no drawn TABLE_OF_VALUES native scene is evidenced.

**Owner/action routing:** ask owning TEST adapter and canonical-schema maintainers for an explicit compatibility ruling: (a) may an unimplemented `TABLE_OF_VALUES` CANDIDATE reside in a contract that compiles, or must it remain quarantined outside admitted generic projection? (b) Which typed datum/oracle binding variants does canonical validation accept, and is MathML `EQUATION` appropriate for author-created domain/residue/expression? (c) If a real renderer is needed, specify a separate approved scoped implementation, actual golden and accessibility tests. The integrator must not silently loosen tests, add a second renderer, mark implementation delivered, or modify shared Core blueprints.

## Next bounded engineering / review actions (still open)

1. **D1 source-owner triage:** extract exact 40 newly failing IDs from [#244 full job](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38515765833/job/115694087677), group each as SOURCE_LOCAL / DEPENDENCY / BASELINE_OR_RUNNER / UNDETERMINED with reproducible one-test commands and failing stack traces. Prioritize honest TEST `TABLE_OF_VALUES` handling; rerun only after module authority. Do not mark 44 IDs fixed.
2. **D2 #245 review handoff:** corrected MODEL-QRT source blob `db87b5a4a7bc807e0680a64417f2c6ca5ca08cf3`, actual [native ZIP 11872590321](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38517197094/artifacts/11872590321) with 6/6 original SHA/receipt validated by prior integrator; the academic packet text that says a rerender is still required is superseded by these receipts. Correct source allows learner to select either count variable. Qualified reviewer must still adjudicate MODEL versus APPLY and all H/S/P/M before any Owner acceptance. Reuse existing [#211](https://github.com/reallakshman19/Grade9v3.5/issues/211), not a duplicate ticket.
3. **D3 #224:** separate Core1 O1 role proof from source-author safe SVG stage metadata. Generic accessible label “Stage 1” remains non-leaking but uninformative. No change to `Shared/tools/render_core.py` or frozen golden without a measured irreducible defect.
4. **D4 #242:** the corrected RETRIEVE old answer-leaking artifact remains DO_NOT_ADOPT, learner Y for full prior iff theorem UNKNOWN; #234 independent classification and H/S/P/M still pending.
5. **Whole-repo CI:** no merge while broad guardrails and canonical assurance remain failed. Reassess all new commits against their newly pinned heads, keeping historic results labelled historic.

## Immutable state at audit

`native_TEST=28/28; special_educational_holds=8/28; qualified_signed=0/28; Owner_QRT_accepted=0/28; owner_golden_designations=0; original_Core2_admitted=0/68; renderer=UNCHANGED; blueprints=UNCHANGED; fixture=FROZEN; rights=NOT_GRANTED; broad_CI=FAILED; all_PRs=DRAFT_UNMERGED; release=HOLD`.
