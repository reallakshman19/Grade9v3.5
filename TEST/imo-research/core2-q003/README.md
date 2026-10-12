# Q003 private-source Core2 TEST staging

Issue [#183](https://github.com/reallakshman19/Grade9v3.5/issues/183), task 183-T2 (O1), chat 6acc303b, 2026-10-12.

The Owner authorized an isolated TEST development branch and approved private-input embedding of original Q003. This directory stores only an identity, printed-source page locator, two SHA-256 digests and instructions. The source text, ordered options, authored answer/support and full rendered learner HTML stay in private inputs and `.private/` ignored staging; they must not be committed, uploaded to Actions artifacts, merged or published.

Run from a **complete local checkout** with the uncommitted original-item and authored-response JSON:
```sh
python3 TEST/imo-research/core2-q003/prepare_private.py --private-input /private/location/q003.source.private.json --prepare-only
python3 TEST/imo-research/core2-q003/prepare_private.py --private-input /private/location/q003.source.private.json
```
The adapter rejects any discrepancy in private-input SHA-256, component SHA-256, paper URL, QID, printed page/position, number or order of the four options, or loss of an original figure. It then constructs a TEST package/isolated noncanonical private bank and calls **only** `Shared/tools/render_core.py` with `--mode PAGES --draft --reference`. The separate sandbox bank avoids falsely declaring a school mirror an official organizer archive. Current runtime's generic badge may say “Source unverified” for non-organizer custody; the separate Owner test verification status is retained in the private record.

Private fixture and output live under ignored `.private/`. Compare the actual rendered HTML with the original source and golden G-CORE2-R2 in T3; only a sanitized digest/count receipt can move to Git after byte audit. No PDF or A4 acceptance yet; no QRT acceptance; no publication right. An admitted Core2 page is NOT established by this branch or this README.

`custody-receipt.json` reports the source PDF digest as **null** (the byte stream was not retained). The pinned SHA-256 values separately represent exact private JSON bytes and the normalized source-item components, not a PDF digest. Never relabel these as a publisher hash.

## Private attempt-first disclosure correction (v2.2.0)

The original Q003's authored second rung identifies the decisive numerical model, and the third narrows the exception. A TEST-only `grade9v3:core2_support_plan` explicitly binds that protected reasoning move: rung 0 is neutral pre-attempt orientation; rungs 1 and 2 are available **only after a learner commitment**. The renderer's existing Core2-v2 projection enforces this availability—this branch does **not** add or invent a new blueprint. Recheck the actual HTML after the sole renderer is executable; this is contract-aware code staging, not a rendered/accepted page.

Preflight receipt `preflight-receipt.v2.json` contains **no** source text/options or answer: its local input SHA, component SHA, original ordering, arithmetic answer oracle, typed reasoning references, difficulty band, and three adversarial mutations were checked in a private Python run on 2026-10-12; its `renderer` is `NOT_RUN`. The full Git checkout remains unreachable from this tool environment due DNS resolution. The private source file itself is locally present and checksum verified; that earlier dependency is no longer missing.
