# Agent 1: receipt-derived readiness without source admission — #130

**Scope:** Research-only engineering for existing [#130](https://github.com/reallakshman19/Grade9v3.5/issues/130), as amended by the Owner on 2026-10-10 to use **SELF_CHECK + SPOT_REVIEW ONLY** for engineering. Do not represent this as a second independent principal. It does not remove source custody, publisher rights, question fidelity, protected academic/QRT, CI, or Owner release requirements.

## Why this exists

`intake/core2-source-custody-eligibility.v1.json` is a **frozen research census** of 68 original-paper references and zero Core2 admitted source questions. Its invariants must continue to reject silently changed source claims. But it is inappropriate to turn "all 68 always false" into an unchangeable **current** eligibility engine.

`project_core2_readiness.py` reads that historical ledger unchanged and optionally accepts a **local/private** evidence bundle. It reuses `Shared/tools/source_pipeline.py:verify_acquisition` to compare retained snapshot bytes to an acquisition receipt and `Shared/library/source_custody.py:validate_question` to validate the existing typed question-level proof. An exact PDF page/printed-item locator must match the historical observation where it exists. The original question's `id`, original number, resource and URL are crosschecked. The projection accepts no rights, reviewer, Core2 admission or publication claims.

**Vocabulary:** `READY_FOR_SPOT_CHECK_NOT_ADMITTED` means the mechanical receipt, identity and structural custody checks passed *against whatever private bytes/record the caller supplied*. It does not establish that supplied bytes are genuinely published by SOF, that source text/figures were correctly copied, that an answer is mathematically right, that permission exists, or that a reviewer approved anything. Authentic-source Core2 and learner publication remain **HOLD**. The old frozen research census remains unchanged.

## Run

Without private evidence (default), emits all 68 positions on hold with individual missing-proof codes:

```sh
python TEST/imo-research/project_core2_readiness.py --output /tmp/imo-core2-readiness.json
python -m unittest discover -s tests -p 'test_imo_core2_readiness_projection.py' -v
```

Future restricted custody can pass `--private-evidence /restricted/workspace/imo-evidence.json`. The input schema is `imo-g9-private-custody-evidence-v1` with `items[]` containing `question_id`, `acquisition`, `resource`, `question`, `supporting_resources`, `inspected_sections` and `access_status`. In the typed canonical question proof, `source_item_locator` must use `pdf_page_index=N;printed_item=K`; the same string is among `inspected_sections`. Each snapshot must remain outside the repository's public/docs/research-evidence trees and should be in a restricted workspace.

The `tests/test_imo_core2_readiness_projection.py` positive case constructs an **INVENTED minimal fixture PDF and INVENTED question** for mechanical testing only. That case must never become a genuine acquisition or source-question receipt. Mutations detect a missing/tampered snapshot, changed document identity/printed locator, absent/altered question components, forged review/rights fields and source-ledger tampering.

## Required subsequent work, not completed here

- Acquire legally accessible source bytes into a controlled restricted store; record actual digest, retrieval and retention evidence.
- Spot-check source identity and precise item vs PDF, printed key, all stem/options/conditions/media/hints/answer components, mathematical reasoning and any discrepancy; fail closed on conflicts.
- Seek a genuine rights disposition. Current code deliberately does not accept a rights boolean; self-check cannot establish permission to reproduce or publish someone else's source.
- Use separate applicable promotion/Owner authority to admit Core2; downstream learner projection must not infer release from this report.
- Keep the other 67 held until their *own* receipts and decisions are established.

**Self review:** `REVIEW_MODE: SELF_REVIEW`; `PRINCIPAL_INDEPENDENCE: NONE`. A manual spot check is evidence of checking, not independent certification. All required CI/engineering protections remain.
