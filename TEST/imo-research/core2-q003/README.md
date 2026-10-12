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
