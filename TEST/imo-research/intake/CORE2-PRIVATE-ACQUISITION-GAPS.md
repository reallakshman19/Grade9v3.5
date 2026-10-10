# IMO Core2 — private PDF acquisition and 68-position gap report

Agent 1, [destination issue #130](https://github.com/reallakshman19/Grade9v3.5/issues/130). Scope: source-custody research only; SELF_CHECK + focused SPOT_REVIEW, principal independence NONE.

## Implementation

`TEST/imo-research/core2_source_acquisition_gaps.py` reuses the pre-existing `Shared/tools/source_pipeline.py` acquisition and `verify_acquisition` receipt verifier, and the original four-document queue `core2-source-acquisition-handoff.v1.json`. It never overwrites the frozen source census or converts an acquired document into an authenticated question.

To generate the **current baseline metadata-only gap report**, with no network access and no source bytes:

```sh
python TEST/imo-research/core2_source_acquisition_gaps.py report --output /tmp/imo-68-source-gaps.json
```

The default reports four missing durable source receipts; exactly 68 question rows; 58 full-paper, 8 previously seeded sample and 2 additionally observed organizer sample positions. Every item includes source identity, printed-position claim, observed PDF page if known, actionable missing-evidence codes, and the historical next source action. All 68 source questions remain **HOLD** and zero are Core2 admitted.

## Restricted acquisition (explicit operator action, one PDF at a time)

Choose a filesystem path **outside the Git repository**, owned by the current user and private to that user (directory mode 0700); it must have an existing parent. Do not use a Git checkout directory, cloud-hosted public folder, Docs/Pages, or artifact CI upload. Example:

```sh
install -d -m 700 /private/imo-g9-source-custody
python TEST/imo-research/core2_source_acquisition_gaps.py acquire \
  --private-dir /private/imo-g9-source-custody \
  --source-id SOF-IMO-G09-SAMPLE-2026-27
python TEST/imo-research/core2_source_acquisition_gaps.py report \
  --private-dir /private/imo-g9-source-custody \
  --output /tmp/imo-68-source-gaps.json
```

### Offline fallback — browser-downloaded PDF, source authenticity still unverified

If this execution environment cannot resolve the organizer's host but the operator can manually download the official PDF, import that **local file** without uploading it to GitHub or CI. Keep the manual download outside the repository, e.g. the operator's Downloads folder, then pass its **absolute** path:

```sh
python TEST/imo-research/core2_source_acquisition_gaps.py acquire \
  --private-dir /private/imo-g9-source-custody \
  --source-id SOF-IMO-G09-SAMPLE-2026-27 \
  --local-file /absolute/path/to/class-9-sample.pdf
python TEST/imo-research/core2_source_acquisition_gaps.py report \
  --private-dir /private/imo-g9-source-custody \
  --output /tmp/imo-68-source-gaps.json
```

The local file must be an existing, absolute non-symlink PDF (maximum 100 MiB), outside both the repository and custody workspace. The wrapper uses existing `source_pipeline.acquire_file` to make a private snapshot, rehashes the exact stored bytes and refuses every overwrite. The receipt explicitly records `source_kind: FILE` and a local resolved locator. It is **not proof that SOF supplied the file**. The report labels it `IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED`, counts the byte-verifiable retention separately, and includes `LOCAL_FILE_SOURCE_ORIGIN_UNVERIFIED` on all ten positions linked to that sample until genuine document identity/source-item custody and rights are established. The source PDF must still be inspected against the organizer's live version and version/rights evidence before any authentic Core2 approval. Do not tell downstream agents that a filename, PDF header, or SHA256 alone proves authenticity.

Acquire requires an explicitly selected one of four pinned HTTPS source documents and refuses an existing private PDF or receipt instead of silently overwriting. Source bytes and acquisition JSON are written only to the private workspace with restrictive permissions. Reconciliation checks PDF header, same-host HTTPS redirect, URL and resource identity, snapshot length and SHA-256. A failed fetch, invalid header, redirect or checksum removes any partial created files. A successful receipt is **verified retained bytes only**. It does not establish SOF publisher authenticity or redistribution rights merely because a school mirror/organizer URL responds.

If acquisition fails, record the failure as `NOT_ACQUIRED` and continue preparing the honest missing-evidence queue. Never invent a SHA256, publication licence, inspector, approved answer or missing question text. The tool never performs OCR, does not reproduce any source stem/figures in the report and never sends private snapshots to CI or GitHub.

## Historical PDF version fingerprint comparison (verified older evidence)

The original old-repository [source-acquisition-probe GitHub Actions run 37868836390](https://github.com/reallaksh19/Grade9v3.5/actions/runs/37868836390), job 113621920381, successfully downloaded and SHA-256-hashed four source documents on 2026-10-09. Its retained [artifact 11588893886](https://github.com/reallaksh19/Grade9v3.5/actions/runs/37868836390/artifacts/11588893886) was downloaded and independently SHA-256 checked as `399e14a5f3f992ef47014ab3594c989dfe4cf9192cd95322b135978de7c3a486`. The artifact contains **only** `source-probe-evidence.json`—not any source PDFs—and explicitly records zero durable PDF snapshots, zero canonical custody receipts and no reuse permission.

The four exact ephemeral byte hashes/sizes are now frozen as **historical comparison evidence** in `core2-ephemeral-source-fingerprints.v1.json`, with fail-closed code pins and tests. When the operator imports a PDF or network acquisition succeeds, the report shows the historical hash and one of:

- `MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY`: the **retained** source snapshot SHA-256 **and byte length** match the temporary file observed in the 2026-10-09 CI run; *not* independently signed publisher origin, question fidelity or permission
- `DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION`: retained, internally consistent PDF differs from that earlier version; requires a human source-version inspection (the publisher/mirror may have legitimately updated it)
- `NOT_CHECKED_NO_RETAINED_BYTES` or `NOT_CHECKED_INVALID_RECEIPT`: no trustworthy local receipt to compare

The report never marks a question eligible or published merely because the historic hashes match. The version mismatch adds `REVIEW_SOURCE_DOCUMENT_VERSION_DRIFT` to the ten/four/etc affected item rows so the operator can prioritize exact-version checks. This source-version comparison is **read-only observation**, not a new rights or academic authority.

## Q004 self-spot-check packet bound to a *real* retained PDF

After (and only after) a PDF snapshot and receipt exist in an operator-controlled restricted workspace, generate a closed-schema **metadata-only** Q004 inspection packet:

```sh
python TEST/imo-research/q004_private_spotcheck.py template \
  --private-dir /private/imo-g9-source-custody \
  > /private/imo-g9-source-custody/q004.inspection.json
```

The template captures source ID, zero-based PDF item/key pages 0 and 1, printed position 4, previously visually sighted printed answer **B**, derived numeric table relation and excluded distractors, *current exact snapshot SHA/size* when a real receipt exists, and the historical PDF-version comparison. It contains **zero original source PDF text, options or figure pixels**.

An authorized operator must open **that retained PDF** and compare all nine components themselves. The nine `source_components` entries start as `NOT_CHECKED`. For each component, record the appropriate *self-inspected disposition*, using exactly the defined statuses in `q004_private_spotcheck.py:FIELDS`; this includes checking the printed number, stem, options and order, conditions, tabular visual, source key and explicit absence of subparts/captions/hints when justified. Set `spotcheck_actor_role: SELF_SPOT_CHECK` and a real UTC timestamp such as `2026-10-10T04:59:00Z`. Never pre-fill confirmations from a rendered web observation alone or mark the reviewer independent. Do not add publisher wording, copied options or images to the packet.

Verify the operator's private assessment:

```sh
python TEST/imo-research/q004_private_spotcheck.py verify \
  --private-dir /private/imo-g9-source-custody \
  --assessment /private/imo-g9-source-custody/q004.inspection.json
```

The tool revalidates the snapshot and acquisition receipt at verification time. It fails closed on missing or altered SHA/byte length, a changed original question/item page/key, wrong math, missing nine-component self-checks, source-version mismatch, forged rights/reviewer/admission data or assessment outside the private workspace. A hypothetical exact historical byte match plus **all nine** operator attestations may return `SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED`; this is explicitly a **same-principal self-attestation, not independent source authenticity/correctness certification**. The source counter remains **68 HOLD**; legal rights and Owner Core2 acceptance remain external. Tests use **invented PDF bytes** and a mocked positive version-match branch; they never claim the original source was acquired.

Research-only test command:

```sh
python -m unittest discover -s tests -p 'test_imo_core2_q004_spotcheck.py' -v
```

## Q004 private visual inspection bundle (actual retained PDF only)

After acquiring and verifying the official sample's exact bytes in the
**restricted non-repository workspace**, prepare two local visual page renders and
a fresh, **unchecked** Q004 inspection packet:

```sh
python TEST/imo-research/q004_private_review_bundle.py \
  --private-dir /private/imo-g9-source-custody
```

The command requires an existing valid source snapshot and SHA-256 acquisition
receipt for `SOF-IMO-G09-SAMPLE-2026-27`. It uses the locally installed
`pdftoppm` (Poppler) to render the previously observed printed Q004 item page
(PDF index 0) and sample key page (PDF index 1), into a new private
`q004-private-review/` directory (mode 0700). It writes two mode-0600 PNGs,
`review-manifest.json` (exact snapshot digest, source/version status, PNG digests,
**zero** acceptance), and `q004.inspection.json` (all nine checks **NOT_CHECKED**).
It refuses missing/tampered receipts, non-private workspaces, forged accepted
statuses, missing page images, or any existing review directory; partial output
is deleted after rendering failure. The images and packet **must never be
committed, uploaded to CI, or copied into public/docs**.

Open the image files privately, compare them with the *actual stored PDF*, and
fill the nine source-component dispositions only from real observation. Then
execute the **existing verifier** against the exact generated packet path:

```sh
python TEST/imo-research/q004_private_spotcheck.py verify \
  --private-dir /private/imo-g9-source-custody \
  --assessment /private/imo-g9-source-custody/q004-private-review/q004.inspection.json
```

Both the old root-level private assessment and the *one fixed bundle path* are
accepted; arbitrary nested paths/symlink escapes are not. If the PDF was imported
from a local file, the manifest retains
`IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED`; a matching historic
hash, operator self-check, or rendered page is **not** independent SOF source
authentication. A different current source hash is a version-review hold, not a
reason to forge the old digest. This private inspection does not change any of
the 68 source Core2 HOLDS, licence status, canonical admissions, academic/QRT
acceptance, or learner release.

## Private-bundle source integrity and handoff verification

The review bundle validates source bytes *again after* rendering both page images.
If an original PDF changes between the first verified receipt read and the
completion of Poppler output, the bundle fails closed and removes incomplete
private output. The inspection verifier also refuses world-readable inspection
JSON: the mode-0700 review directory must contain owner-owned mode-0600
`q004.inspection.json`. This protects the operator workspace; it does **not**
certify the original SOF edition or grant reproduction rights.

The GitHub Actions one-shot generator for this branch completed at
[run #38067000492](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38067000492).
It regenerated only the seven governed derived projections, ran generator
read-back checks, and deleted its temporary workflow in the generated commit.
Because that commit was produced by GitHub Actions, separate normal PR CI
may require a fresh non-bot commit/approval; do not treat `action_required` as
a passing or failing verifier. Authentic Core2 remains held at 0/68 until
real retained original-source evidence and external decisions exist.

## Public publisher-rights notice — no licence asserted

SOF's [official website](https://sofworld.org/) publicly displays a copyright footer restricting copying/use without **prior written consent**. Its [official contact page](https://sofworld.org/contact) gives general enquiries email `info@sofworld.org`. These observations were checked on 2026-10-10. The public notice is general website language: it **does not** itself establish the rights holder or rights disposition for each school-mirrored past-paper PDF, nor does it supply a licence or explicit policy on mere linking to external original pages.

The versioned research-only `core2-public-rights-notice.v1.json` binds this observation to all four indexed source-document IDs while expressly recording **no permission requested**, **no licence received**, **no wording/figure reproduction authorized**, **no separate original-page-link permission determination**, and no accepted Core2/public original-paper product. The gap reporter adds `PUBLIC_SOF_SITE_NOTICE_REQUIRES_PRIOR_WRITTEN_CONSENT` and `SOURCE_SPECIFIC_WRITTEN_PERMISSION_NOT_EVIDENCED` to the 68 question-level blockers. Source-specific immutable historical ledger rows intentionally retain their existing `publisher_publication_rights: NOT_REVIEWED` because no signed licence/copyright review resolves an actual paper.

**Operator rights action:** Send a specific permission enquiry to SOF through the official contact address, asking separately about (a) exact stem/options/answers, (b) reproduced diagrams/tables/figures, (c) adapted/paraphrased questions, and (d) linking out to the official PDF without embedding protected material. Record recipient, date, exact reply and licensed scope in a *private/authorized* source-rights workflow; only then propose an update through a new reviewed rights decision. This engineering PR **did not send the enquiry** and never claims receipt of permission. In the absence of a grant, prefer **authored concept examples** or clearly attributed research-only external references; neither substitutes for authentic Core2 custody.

## Required next acceptance work

For each printed position: inspect the exact PDF item; preserve exact source number, stem, conditions, option order, captions, figures, source hints and source answer independently of author's mathematical computation; resolve the ten known discrepancy cases affecting eleven positions; record a rights disposition and authentic question-level proof via existing source-custody structures. Engineering **self-check and spot review** remain distinct from genuine source rights and Owner/Core/QRT publication decisions.

Offline adversarial tests:

```sh
python -m unittest discover -s tests -p 'test_imo_core2_source_acquisition_gaps.py' -v
```

All test files synthesize *invented test-only PDF bytes*. Successful synthetic metadata does not authenticate a SOF paper or permit any learner Core2 publication.

REVIEW_MODE: SELF_REVIEW
PRINCIPAL_INDEPENDENCE: NONE
