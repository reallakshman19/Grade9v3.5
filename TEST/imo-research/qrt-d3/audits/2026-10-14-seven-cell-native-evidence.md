# r5-02 addendum · D3 seven-cell native artifact adoption evidence (2026-10-14)

**Scope: evidence audit, not academic review.** Source PR [#193](https://github.com/reallakshman19/Grade9v3.5/pull/193) original head `40142fe06818e7a946d6296911d495f3f3323b12`, PR-job checkout `a458eb81e0cf40e8e767065583f3c10eb9923f3d`. All 14 source/manifest Git blobs below were independently re-fetched at **both** revisions and matched. Seven archived native sole-renderer ZIPs downloaded independently. For each, all five learner role HTML and index recomputed SHA-256 matched **both** the receipt `page_sha256` map and that artifact's `*-sha256.json`; no renderer gaps: **42/42 SHA checks**. Exact six SHA-256 values remain in each linked ZIP's two independently matched records, not hand-typed viewer fields.

| D3 primary cell | Scoped run / native ZIP artifact | Authored source Git blob | Manifest Git blob | Technical state of archived original |
|---|---|---|---|---|
| RETRIEVE | [38337028397 / 11785168227](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028397/artifacts/11785168227) | `dda4ee58b80d1fd6bc8feb16c8986935bc9d92e8` | `45e6b6b8447672a127537f139c13e9bcdc753102` | 6/6 receipt-match |
| EXPLAIN | [38337028454 / 11785013511](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028454/artifacts/11785013511) | `32fad7e3be4f806e43e5f44942434842ad10c25a` | `2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e` | 6/6 receipt-match |
| APPLY | [38337028850 / 11784773266](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028850/artifacts/11784773266) | `18a56e28ed4b7c6a4001a69fb18d5f4adcd7a20a` | `4b91550bc228d4cfde218c5030aa225920f15dee` | 6/6 receipt-match |
| MODEL | [38337028737 / 11784558622](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028737/artifacts/11784558622) | `9025855dc36c0eaa486342c72ab66a211104bbca` | `4a294f3bbc9c08a6ca04ff9a30568eb1479b502e` | 6/6 receipt-match |
| REPRESENT | [38337028524 / 11785527143](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028524/artifacts/11785527143) | `61ccc3fe169f2ce8f5bbec5b0fd2e292d38e1a1b` | `09a43b1507b6a5e6dc103dd2e7796d8bc0b528dc` | 6/6 receipt-match |
| SYNTHESIZE (original) | [38337028484 / 11785257881](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028484/artifacts/11785257881) | `71830e1317595658e40819ee5fbc68ed140e9855` | `a3c1d186a5e319717388bb55116ad65b1c8b566c` | 6/6 receipt-match **but source label defect; DO NOT ADOPT** |
| JUSTIFY | [38337028537 / 11784849193](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38337028537/artifacts/11784849193) | `df495bfc6fdf87038fea518c016bf164748e5ed6` | `398d395dd78042616ebda5c09bc7b05e27d8d941` | 6/6 receipt-match |

## Browser and reasoning gate reproduction

Using **actual archived Core2A and Core2B HTML**, Chromium executed 7 cells × 2 roles × 3 widths (390/768/1280 px) = **42/42 technical gating checks passed**: no solution payload before attempt; no disclosure after blank commitment; payload available after nonblank typed attempt; no JS page exceptions; zero observed document-width overflow. The original Core2A H1/H2 were separately read in all seven cells; no obvious printed final answers were present in those hints. That is a *limited content inspection*, not a full protected-W/academic/a11y verdict. Browser setup used local HTML `page.set_content`; site's linked external CSS and assets were not fetched.

## Corrected SYNTHESIZE-D3 current descendant

This separate draft [PR #221](https://github.com/reallakshman19/Grade9v3.5/pull/221) corrected only the source-authored closure's obsolete **REPRESENT** label (plus a regression test and scoped workflow change).

- New draft source head `c21987d258111d6586585616e5cca2d6e077064c`; [scoped success run 38484157878](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38484157878) and [new ZIP artifact 11859035196](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38484157878/artifacts/11859035196). Workflow checkout `f7ab8a777cc004daff8b39f7d94468dd55651920` has same source Git blob `b852966af06a54b7a594f6ab12653af341f6d836` and manifest blob `a3c1d186a5e319717388bb55116ad65b1c8b566c` as draft branch.
- **New post-fix artifact verified 6/6 SHA across both receipt and checksum, zero gaps.** The *actual HTML* now prints: “Provisional SYNTHESIZE-D3: connect progression, divisibility and valid digit bounds; independent academic verdict and Owner acceptance pending.”
- New SHA-256 map (post-fix only): `core1.html=d846754cf98e83aec7c08b99df9426be59bf5b02ed888bfd380eaf98673aeec7`; `core1a.html=783fb7675af503c47baa4f1f45d93f8b56521bd0bb13a8d2697e429763277056`; `core1b.html=4d1a9a2406fb82d12069c7d81dffd1d958926cec59b58d5cb96cb3d2fee5c4dc`; `core2a.html=f25d7b5993ae087d4d1757f04cd4d56162bf7301f0f4fb5daad5c979b0a65698`; `core2b.html=3d47e055e57a2adf89b141ebad357267d4552cac40120676ff8a763130982ea3`; `index.html=99c0cd128671fa00332fca0c56bac009610dc0fb06aed9746eb6f482e75d07b8`.
- Post-fix Core2A/B browser gate re-run at 390/768/1280 px also had no early solution reveal or JS exceptions/overflow; source-specific defect corrected in TEST. **Not independently academically approved.**

**Status:** D3 7/7 original artifact technical provenance verified; SYNTHESIZE original `SUPERSEDED_DO_NOT_ADOPT`, corrected descendant `NEW_EXACT_HEAD_HTML_VERIFIED_ACADEMIC_HOLD`; all 7 `QUALIFIED_ACADEMIC_REVIEW_PENDING` and Owner acceptance 0/7 (programme 0/28). Do not claim 7 semantic/golden acceptances. Shared goldens and blueprints unchanged, no source rights, merge or release.
