# r5-02 · QRT-SYNTHESIZE-D3 exact-artifact technical audit (2026-10-14)

**Status: NEEDS_AUTHOR_FIX + QUALIFIED_ACADEMIC_REVIEW_PENDING.** Independent *technical* reproduction only; not a credentialed reviewer signature, Owner QRT acceptance, immutable successor golden or release.

## Evidence provenance

- Draft source [PR #193](https://github.com/reallakshman19/Grade9v3.5/pull/193) at PR head `40142fe06818e7a946d6296911d495f3f3323b12`. Actual [renderer run 38337028484](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028484) / [artifact 11785257881](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028484/artifacts/11785257881) records PR-event **merge checkout** `a458eb81e0cf40e8e767065583f3c10eb9923f3d`. The unchanged source Git blob `71830e1317595658e40819ee5fbc68ed140e9855` and manifest Git blob `a3c1d186a5e319717388bb55116ad65b1c8b566c` are identical at those two revisions.
- Sole renderer `render_core/2`; mode PAGES; five registered Core roles + index, `selection.core2=[]`, zero receipt gaps. Independently recalculated SHA-256 from the unmodified artifact ZIP, exact match with BOTH `render-receipt.json` and `synthesize-d3-sha256.json` (6/6).

| File | SHA-256 of actual original artifact |
| --- | --- |
| core1.html | `4c7e43f3c0047b16d026eb2d0a3d6b8c9a14d6e73009c4fb9a837761f3532801` |
| core1a.html | `94a4461820dd96c23300e13dabc847ebaf339983a0ba1e57ced9aea6e653e316` |
| core1b.html | `87ade789de1fcc3d739406703144a9b219fc6375b8f8a4fb2c9900cb10dcd44a` |
| core2a.html | `c4fe72dc54516e96765a53bf4a1cdb130eabeef18374de021a735660f610c51c` |
| core2b.html | `49cbfc223e849c53b77978e06e7d05ebef735059e1110dfe6a3bb268c5a329bc` |
| index.html | `ba2c2836a6ffabad5abb83292369047a92d1094086a173d7a895ee8b048113b5` |

## Mathematical and native-HTML checks

An independent Python enumeration of 100..999 with `H+U=2T` independently reproduces **14** divisible by 9, **20** divisible by 6, and **8** divisible by 9 with odd units. Analytically for divisor 9, `H+T+U=3T`, so `T∈{3,6,9}`, with disjoint signed-gap counts 6+7+1. Error probes: 246 is AP but not divisible by 9; 036 is not a three-digit integer. These confirm calculations, **not** QRT band/demand.

Inspected exact native Core2A preattempt H1/H2, HTML figure labels, postattempt H3, and CORE2B changed-divisor transfer. Core2A H2 asks learners to organize digit pattern, divisibility and place-value restrictions; it does not choose `T` cases or 6/7/1 counts. H3 is in an attempt-gated template. Actual ZIP HTML exercised in Chromium using `page.set_content` at **390/768/1280 px** for Core2A and Core2B: before attempt and after blank submission, attempted reveal produces empty payload; nonblank written attempt permits solution to reveal 14 (Core2A) and 20 (Core2B), and Core2A H3 yields AP/digit-bound reasoning only after commitment. No JS page exceptions or observed horizontal overflow in six inspected states. **Limit:** this isolated test did not load the site's external CSS and is not a complete published-site viewport/a11y verdict.

Compared the actual five role **slot orders** against Owner-frozen `G-IMO-G9-FIVE-CORE-20261012` snapshots at PR #189 head `6307e5dd97f9ae72a052fc7f3e88c368a4cc5434`: **5/5 orders matched**. This is structural, not byte equality across different questions or academic semantic equivalence. Core1 snapshot has attempt/hint affordances that this authored Core1 orientation lacks; log as `TECHNIQUE_REVIEW_REQUIRED`, not an assumed blueprint gap. Frozen fixtures stay unchanged.

## Measured defect, action and next gate

The prior rendered Core2A *postattempt* closure says **"Assisted REPRESENT question, academic acceptance pending."** This was traced to the authored source `questions[].family_exposure.closure` for the **SYNTHESIZE-D3** main question. It is a source-input classification mislabel, not a renderer/global-blueprint defect. This audit branch changes that *single* closure to a **provisional SYNTHESIZE-D3** description and adds a narrowly scoped regression unit test. The six old hashes above **do not** describe the patched descendant; re-render at the new exact head and pin six new hashes before adoption.

Independent qualified academic review must still adjudicate primary SYNTHESIZE vs MODEL/APPLY and D3 vs D2/D4, protected learner W and all 12 H/S/P/M criteria, COI and signed reviewer verdict, before any Owner per-cell ACCEPT/REVISE/REJECT ID or new golden version. **Owner accepted 0/28**. No release/source-rights/merge authority inferred.

**Disposition:** historical exact-head artifact `VERIFIED_WITH_AUTHOR_INPUT_DEFECT`; patch `PENDING_NEW_NATIVE_RENDER`; academic `UNREVIEWED`; Owner `NO_DECISION`.
