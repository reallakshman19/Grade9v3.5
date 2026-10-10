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

Acquire requires an explicitly selected one of four pinned HTTPS source documents and refuses an existing private PDF or receipt instead of silently overwriting. Source bytes and acquisition JSON are written only to the private workspace with restrictive permissions. Reconciliation checks PDF header, same-host HTTPS redirect, URL and resource identity, snapshot length and SHA-256. A failed fetch, invalid header, redirect or checksum removes any partial created files. A successful receipt is **verified retained bytes only**. It does not establish SOF publisher authenticity or redistribution rights merely because a school mirror/organizer URL responds.

If acquisition fails, record the failure as `NOT_ACQUIRED` and continue preparing the honest missing-evidence queue. Never invent a SHA256, publication licence, inspector, approved answer or missing question text. The tool never performs OCR, does not reproduce any source stem/figures in the report and never sends private snapshots to CI or GitHub.

## Required next acceptance work

For each printed position: inspect the exact PDF item; preserve exact source number, stem, conditions, option order, captions, figures, source hints and source answer independently of author's mathematical computation; resolve the ten known discrepancy cases affecting eleven positions; record a rights disposition and authentic question-level proof via existing source-custody structures. Engineering **self-check and spot review** remain distinct from genuine source rights and Owner/Core/QRT publication decisions.

Offline adversarial tests:

```sh
python -m unittest discover -s tests -p 'test_imo_core2_source_acquisition_gaps.py' -v
```

All test files synthesize *invented test-only PDF bytes*. Successful synthetic metadata does not authenticate a SOF paper or permit any learner Core2 publication.

REVIEW_MODE: SELF_REVIEW
PRINCIPAL_INDEPENDENCE: NONE
