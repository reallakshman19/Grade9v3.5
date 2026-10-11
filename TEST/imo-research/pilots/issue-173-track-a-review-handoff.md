# IMO Track A #173 — held four-role authored candidate review packet

**Status: DRAFT / TEST / CANDIDATE / HOLD.** This is an engineering author handoff, **not** mathematics review, QRT acceptance, independent learner AT review or Owner product authorization. Source Core2 admission 0/68; accepted source QRT 0/28. [Track B #174](https://github.com/reallakshman19/Grade9v3.5/issues/174) and source operator #163 are outside this work.

## Immutable dependencies and responsibility

| Input | Identity | Meaning |
| --- | --- | --- |
| `main` | `778eb35a70517a46108ad0a5dc01dfc89f61c0e3` | pinned comparison only; no write |
| Draft authored PR #166 | `48007ccf962ed03f9f6a5423fe7525eaba9cfdf1` | 3-role A/B, additive TEST package and generic opt-in hint behavior |
| Draft print evidence PR #172 | `835f1f717db9aebf232a8e7f2807a11f7878b63e` | two-state A4 gates; stacked base for Track A |
| Draft Track A PR #175 | branch `agent/issue-173-authored-four-role` | use the exact **head SHA and uploaded matrix** from current CI; not a static earlier-head receipt |
| Active coordination | `relay/PROTOCOL_SELECTION.yaml` V3_1; `relay/STATE.yaml` lease #212 | untouched. No integration permission assumed |

The package `TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json` already owns the same `microtopic.inferential_jump`, elicitation and misconceptions as the separate `core1a-render-qualified-divisibility.v1.json` Core1B prototype. Adding both package refs would duplicate record authority. The new Track A manifests intentionally contain **one** package ref. Original #166 A/B manifests are unmodified and remain three-role baselines. There are no new math source records and no second renderer.

## Two held alternatives (A/B, academically unselected)

| Dimension | Candidate A: five adjacent factors | Candidate B: triple iff boundary |
| --- | --- | --- |
| Manifest | `TEST/products/imo-g9-track-a-four-role-five-120.manifest.json` | `TEST/products/imo-g9-track-a-four-role-boundary-12.manifest.json` |
| Selection | `Q-TEST-IMO-164-FIVE-CONSECUTIVE-120` | `Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY` |
| Earlier teaching | Every triple has a 2 and a 3 ⇒ divisible by 6; Core1A exit also establishes four consecutive factors divisible by 24 | Same triple divisibility-by-6 construction, and four-factor proof |
| Independent mathematical author check (not a signed review) | Every four consecutive integers include one multiple of 4 and another even factor ⇒ 8; a multiple of 3 ⇒ 24. Every five consecutive integers include a multiple of 5; since gcd(24,5)=1, the five-factor product is divisible by 120 for every positive n | For P(n)=n(n+1)(n+2), divisibility by 6 is universal. For n mod 4 = 0,2,3, the triple contains a multiple of 4; for n mod 4 = 1, only n+1 contributes one power of 2, so 12 does not divide P(n). Therefore 12 divides P(n) **iff** n mod 4 != 1 |
| Mathematical falsifier | Merely checking the first five values is not proof for arbitrary n; inferring 120 from 24 alone misses the 5 warrant | n=1 gives 1·2·3=6, not 12; a mere “some starts work” observation misses necessity/sufficiency |
| Proposed learner-owned change | Supply and combine the additional 5-divisor universal warrant | Replace the previously taught universal triple property with counterexample + complete residue classification + both iff directions |
| Difficulty and selection | **PROPOSED, NOT REVIEWED** — #168 to decide D3 and twelve H/S/P/M questions | **PROPOSED, NOT REVIEWED** — #168 to decide D3 and twelve H/S/P/M questions |

## Four-role learning journey and leakage boundaries

1. **Core2A** is a prior-attempt diagnostic: it asks whether finite examples prove the triple statement. Its answer/repair pathway is gated and links to Core1A.
2. **Core1A** explicitly constructs the inference using an arbitrary n, exhaustive parity/modulo-3 cases, and coprime factor combination. It is the teaching role and holds the separately declared four-factor exit.
3. **Core1B** uses the *same* concept, but elicits a proof with changed notation t−2,t−1,t. Its attempt requires an actual learner response before the self-check; it has a four-criterion rubric, rejected routes and concrete repairs. A second, independent attempt guards the two-factor boundary case at t=2. Merely following the repair link is **not** mastery evidence.
4. **Core2B** withholds the new warrant/classification until commitment. A Core1B attempt must not unlock Core2B. Both variants remain unselected TEST transfer tasks.

Both new manifests explicitly declare `CORE2A → CORE1A → CORE1B → CORE2B`, empty `core2`, empty `bank_refs` and empty source coverage. No SOF source item, source-rights status, 68-position admission or released Mathematics route is changed.

## Candidate-golden and real evidence programme

**Candidate golden exemplars only:** `G-MATH-LINEAR-CONSTRAINT` demonstrates T01/T02/T03/T06/T07/T09/T10/T12 across roles; `G-CORE2-R2` informs source-question attempt/hint closure technique T01/T05/T13/T15 but **cannot imply sourced IMO content**. Neither is Owner-blessed. Golden builds use `Shared/tools/build_golden.py` and the one `render_core.py`.

The proposed exact-head [workflow](../../.github/workflows/imo-track-a-173.yml) does the following:

- Builds both **actual candidate golden HTML families** using the canonical renderer and records role-page anatomy and output digests, then renders both four-role variants at `REFERENCE` depth.
- Saves `imo-173-golden-semantic-matrix.json` with per-variant checks and statuses `PASS | FAIL | NOT_RUN`, the current PR HEAD, main pin, manifest/golden/blueprint/renderer digests. It compares semantic criteria, **not** cross-domain HTML byte identities.
- Runs 320/390/768/1280 Chromium evidence over all four authored role pages, including Core1B independent boundary commitment, Core2B fail-closed navigation and reveal; creates labelled pre/post screenshots.
- Produces **real** browser A4 previews of Core2A and Core1A, plus locked/revealed Core1B and Core2B A4 PDF pairs for each alternative. Structural receipt tests inspect MediaBoxes, extractable text and absent precommit protected answers.
- Stores evidence as a **temporary CI artifact**; artifacts and automation do not replace visual inspection, browser-zoom/keyboard human audit, screen-reader test or actual physical A4 signoff.

**Reproducer** (requires `jsonschema`, `pypdf`, and Playwright Chromium):
```bash
python -m unittest discover -s tests -p 'test_imo_173_four_role.py' -v
python Shared/tools/build_golden.py --id G-MATH-LINEAR-CONSTRAINT
python Shared/tools/build_golden.py --id G-CORE2-R2
python tests/benchmark_imo_173_golden.py "$(git rev-parse HEAD)" /tmp/imo-173-golden-matrix.json
python Shared/tools/render_core.py build --manifest TEST/products/imo-g9-track-a-four-role-five-120.manifest.json --out /tmp/imo-173-five --draft --reference
python Shared/tools/render_core.py build --manifest TEST/products/imo-g9-track-a-four-role-boundary-12.manifest.json --out /tmp/imo-173-boundary --draft --reference
```
The workflow is authoritative for its own pinned run and sets up required CSS/JS paths for browser tests.

## Six independent status dimensions

| Dimension | Present status | Exit requirement |
| --- | --- | --- |
| IMPLEMENTED | **PROPOSED** in draft PR #175; manifest/code committed | reviewer inspects actual four-role outputs |
| CI VERIFIED | **QUEUED/NOT YET VERIFIED** at initial handoff | current exact-head tests + required broad checks; baseline delta interpretation |
| GOLDEN VISUAL CHECKED | **NOT_RUN** by a human; semantic automated matrix proposed | per-page A/B and golden screenshot/typographic/figure comparison + independent visual acceptance |
| MATH ACCEPTED | **NO** — alternatives unselected; QRT 0/28 | named #168 independent mathematics/QRT verdict |
| HUMAN ACCEPTED | **NO** | dated #169 NVDA/VoiceOver, keyboard, true 200% zoom, mobile and physical A4 evidence |
| RELEASE AUTHORIZED | **NO / HOLD** | coordinator/Owner merging and separate reviewed product publication decision |

Do not promote provisional automated results into accepted product truth. The active V3.1 #212 lease, all original-source custody/admission and all protected/public routes remain untouched.
