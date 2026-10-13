# Issue #201 — D2 adoption, not regeneration of seven new questions

This branch starts from PR #191 exactly at `eb3cf06646f00bf208084e794b41b4d8d83135b6`. It adds only TEST evidence/review assets and one scoped CI workflow. No Shared renderer, registered blueprint, frozen golden, authentic Core2 source, or public route is changed.

## Actual reusable evidence

The seven D2 worker workflows all passed on this exact PR #191 head and uploaded five Core HTML pages plus an index and `render-receipt.json`. See [evidence.v1.json](issue-201/evidence.v1.json) for source/manifest git blobs, exact CI runs and hosted artifacts. Original exam-source Core2 is not among these rendered pages (`selection.core2=[]`).

The original Owner snapshot `G-IMO-G9-FIVE-CORE-20261012` is checked against its locked SHA256 and reused as a **slot/component/reveal technique comparator**. Different questions must not be tested by literal HTML byte equality. The old frozen Core2A HTML predates the Owner-directed H3 AFTER_ATTEMPT adjustment; that is an **expected policy delta**, not permission to overwrite the golden.

## New checks

`.github/workflows/imo-201-d2-benchmark.yml` rerenders all seven packages with `Shared/tools/render_core.py`, then runs `benchmark_201.py` against the real generated HTML. The checker validates roles, page hashes against renderer receipts, zero gaps, active registered blueprint IDs, ordered structural slots/components against the immutable golden and inert after-attempt H3. With `--browser`, it checks actual Chromium commitment/blank blocking, independent Core1B boundary gating, Core2A deferred H3 disclosure, no JavaScript exceptions, and 390px page overflow. Its JSON results and all native pages are uploaded even when the comparator fails.

Run from repository root after rendering each package in `build/imo201/d2/<demand>/`:

```bash
python TEST/imo-research/qrt-d2/benchmark_201.py \
  --render-root build/imo201/d2 \
  --output build/imo201/d2/benchmark-results.json --browser
```

The [review page](issue-201/index.html) displays the 7×4 matrix with seven selectable D2 evidence tiles; all other bands link to their workstream issues. This is **not** another learner renderer or an accepted QRT fixture. The separate pre-existing Q003/#183 review UI remains authoritative for its private original source and may later link these source-safe records with normal review.

## Unresolved / explicit stop conditions

- Independent qualified mathematical and cognitive-demand adjudication, including RETRIEVE-vs-APPLY and D1/D2/D3 boundaries, the five difficulty components and all twelve H/S/P/M objectives.
- Compare all changed-case solution chains and learner-owned W for each question; passing structural browser checks does not decide whether hints are pedagogically appropriate.
- Exact-head PR #191 **shared guardrails and canonical-assurance failed**, despite seven scoped render successes. Determine new regression versus pre-existing stacked-base failure before merge.
- Post-H3 successor golden designation, Owner ACCEPT/REVISE/REJECT IDs, source rights and release authority are all **PENDING**. Accepted remains **0/28**.
- No new shared blueprint change is justified without a reproduced unexpressible mismatch, classified INPUT/RENDERER/BLUEPRINT/ORACLE and separately reviewed under #182.

Do not merge this stacked branch or PR #191 merely because the seven technical checks pass.
