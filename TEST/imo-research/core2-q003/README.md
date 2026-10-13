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

## Q003 authored Core1A construction (issue #183, r7, chat 6acd1e6b)

This is a distinct **AUTHORED** private Core1A lesson candidate for the exact Q003 concept. The original stem/options remain in the SHA-gated Owner-local JSON only. The committed `core1a-authored.v1.json` contains the source-safe mathematical construction, two registered construction units, a new authored transfer worked anchor and a *different* authored independent exit. None is relabelled as the original IMO question. The Owner's private-TEST Core2 contextual/label approval does **not** bless this Core1A or establish publisher rights, A4 or QRT acceptance.

Use a **complete clean checkout of this isolated TEST branch at its exact commit**, with the existing private 3,835-byte Q003 JSON whose SHA-256 is `b263644cd1dd8aca689582232c9b8495f05ec07f3ffeaff3a18f414e6e1227f9`. Do not retype, reconstruct or publicly upload it. From repository root:

```sh
python -I TEST/imo-research/core2-q003/build_private_core1a.py --private-input "/PRIVATE/EXACT_Q003.json" --prepare-only
python -I TEST/imo-research/core2-q003/benchmark_core1a_native.py --private-input "/PRIVATE/EXACT_Q003.json"
```

The benchmark invokes `build_private_core1a.py` (which imports the existing `prepare_private.py` custody validator and calls only `Shared/tools/render_core.py` with registered **BP-CORE1A-CONSTRUCTION**, `--mode PAGES --draft --reference`) and `Shared/tools/build_golden.py --id G-MATH-LINEAR-CONSTRAINT` (same renderer, candidate golden). These commands generate no bespoke HTML. A 0-gap source-safe structural result is not visual or QRT acceptance.

Private files (ignored, never commit):
- `TEST/imo-research/core2-q003/.private/core1a/{records.json,bank.json,manifest.json}` (bank contains protected original text)
- `TEST/imo-research/core2-q003/.private/core1a/rendered/core1a.html` and `render-receipt.json`
- `golden/units/G-MATH-LINEAR-CONSTRAINT/rendered/core1a.html`

**Return only** the source-safe content of `TEST/imo-research/core2-q003/.private/core1a/native-core1a-golden-comparison.json` plus `source-safe-core1a-receipt.json`, and if nonzero gaps, a redacted first gap identifier/component without original stem/options, answer, source text, HTML or figures. Reports include renderer digests, both page SHA-256 values/bytes, exact native gap counts, component slot sets/differences and `STRUCTURAL_CHECK_ONLY` vs failure. A receipt alone cannot close actual learner browser/visual/A4 review or any Owner QRT cell. The original Owner question paper personal-inspection claim remains unconfirmed.

This changes only this isolated TEST branch. Shared/core and main remain governed by the serial issue #212 lease. If native rendering cannot run, report **BLOCKED**; do not ask any operator to compose HTML.

## Source-safe A4 technical preflight (r7 / 13 October 2026)

User explicitly **deferred the remaining staged-control keyboard/accessibility inspection**; do not run or claim it. The next independent technical gate is **actual A4 geometry and eventual Owner inspection of the same already-rendered native page**. Existing `tools/print/print-product.mjs` prints at **280×175 mm**, which is *not A4*. That established print-production tool, its registry and `Shared/tools/render_core.py` must not be edited under issue #183; source rights, page layout and Owner A4 approval remain separate.

`audit_private_a4.mjs` is **TEST-only QA**. It does not render the concept, regenerate Q003 source/HTML, or author a page. It reads the existing ignored `.private/core1a/rendered/core1a.html` only when its SHA-256 is **`d1fe23c43d1eeae67c69600beef1b5054c361854c3e5cd6742545859592998c0`** and its byte count is **76,401** (the Coordinator-reported browser-tested original at `f030a0a`). It requires the native `render-receipt.json` to identify `render_core/2` with zero gaps and the selected page. It uses local Playwright Chromium to print those same HTML bytes as A4 **portrait** with 10 mm margins, then uses **Node built-ins only** to traverse the resulting PDF page tree and check the count and A4 MediaBox of **every printed page**; it saves a **private**, source-safe hash/geometry receipt. Unsupported PDF structures fail closed with a sanitized error. Any missing page, digest mismatch, native receipt error, uncommitted answer reveal, malformed/unrecognised PDF page tree, incorrect MediaBox, or missing Playwright Chromium binary fails closed. It never materialises the source answer templates.

From repository root, where the original native output already exists:

```sh
node TEST/imo-research/core2-q003/audit_private_a4.mjs
# If the EXACT 62,277-byte frozen original Core2 page also exists in this checkout:
node TEST/imo-research/core2-q003/audit_private_a4.mjs --include-core2
```

Preconditions: Node 22 and local/global Playwright with an already installed Chromium executable. **No `pdfinfo`, Poppler, package download, `npm install`, or third-party executable installation is required**. The script falls back to the global Playwright path via `npm root -g`; if Chromium cannot launch, it returns `PLAYWRIGHT_CHROMIUM_UNAVAILABLE` and no A4 gate can be claimed. The tool does **not** fetch dependencies. The generated `.private/a4-audit/{core1a-native-a4.private.pdf,source-safe-a4-audit-receipt.json}` (and optional `core2-native-a4.private.pdf`) remain ignored on the Owner's machine. **Do not send or publish the PDFs, full source HTML, unredacted screenshot or original item.** Return only the source-safe receipt values/first sanitized error. An A4 MediaBox and PDF page count do not certify clipping, legibility, page breaks, the default public PDF link or Owner print approval; these remain `PENDING`. This is not a replacement for the registered production `print-product.mjs` (its PDF target integrity contract is separately enforced before deployment).

### A4 preflight resolution, 13 Oct 2026 (route B, no Poppler)

Coordinator reports clean clone at prior `c5afd5a`, Node 22.23.2, global Playwright 1.63.0 (Chromium binary availability NOT_YET_CHECKED), and no `pdfinfo`. The TEST script was narrowed to inspect Chromium-generated PDF page-tree `/Pages` counts and **all** leaf `/MediaBox` dimensions without external PDF tools or network dependencies. The preflight is no longer blocked by Poppler; it remains **NOT_RUN** until the Coordinator actually executes it with the existing exact Core1A SHA and local Chromium. No code was changed in `Shared/`, `tools/print/print-product.mjs`, native page, original source or registered blueprint. Test/PDF reports remain private; rights NOT_GRANTED, Owner same-page A4 visual verdict PENDING, independent QRT 0/28. Keyboard/accessibility follow-up remains DEFERRED_BY_USER.
