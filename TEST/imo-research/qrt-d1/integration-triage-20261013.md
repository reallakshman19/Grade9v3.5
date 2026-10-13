# Issue #200 — exact-branch broad-CI baseline triage (13 October 2026)

**Comparison purpose:** Separate source-specific QRT D1 acceptance from the unrelated repository-wide broken baseline. **Do not silence, waive, or overwrite gate results.**

## Evidence anchors

- `main` ref `4dbedc6773482bbecb146ff8959614b2c32dcc6e`:
  - [Main canonical assurance run 38287890826](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38287890826): FAILURE.
  - [Main guardrails run 38287890758](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38287890758): FAILURE.
  - Main commit check-runs: `Assurance (no worse than the baseline)=failure`, `Regression delta (exact test ids)=failure`, `guardrails=failure`, while `code-tests`, `blueprint-v2-render-snapshots`, `research-integrity`, `validate-v31` pass.
- PR #206 before 13 Oct wording correction, exact head `4e6928a2d5bb508bedcf64266f68f2a5ec90f796`: [Actions](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38387571299), [Guardrails](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38387571362), same three check **categories** FAIL; scoped JUSTIFY native renderer, frozen golden snapshot checks, code tests PASS.
- Last actual broad job logs inspected: guardrails job `115263018090`, regression delta job `115263017530`, assurance job `115263017247`. These are exact PR head records, not inferred from green renderer status.

## Concrete signatures seen

| Gate | PR #206 representative failing signal | Relevance to the D1 patch |
| --- | --- | --- |
| Canonical assurance | `REFERENCE_INTEGRITY ... LIB-MATH-LINEAR-EQUATIONS ... LIBRARY_UNRESOLVED_REFERENCE` with many `Q-MAT-LEQ-...` references; `STRUCTURAL_VALIDITY SCHEMA` for linear equations and polynomials; `62` page regressions vs ledger, e.g. Chemistry gas page and Physics thrust tablet `FONT_FLOOR` | Mathematics/Chemistry/Physics records/pages, not the TEST authored JUSTIFY item; main gate already red |
| Guardrails | `STALE_RUNTIME_AUDIT_RECEIPT` across six `public/physics/motion-2d/explorers/.../index.html` explorers; subject-independent identifier and Core1A/representation debts cited in the wider tree | Main guardrails already red; not a justification for global registry or renderer edits in #200 |
| Regression delta | Large existing Mathematics `EQUATION_SOURCE_MISMATCH: CORE1-REL-MATH-LINEAR-SOLUTION`, fixtures using obsolete values `VERIFIED_CANONICAL/PUBLISHED`, generated site-search/test projection mismatches, Browser Topic Atlas timeout, assurance ratchet failures | Main regression check already red; per-test **exact set** still needs a maintainer's baseline-delta comparison before declaring no regression |

**Scope check:** [PR #206 changed filenames](https://github.com/reallakshman19/Grade9v3.5/pull/206/files) are eleven TEST-authored QRT JUSTIFY files (source, four SVGs, manifest, math oracle, tests, scoped workflow, review packet, ledger). [PR #204](https://github.com/reallakshman19/Grade9v3.5/pull/204/files) alters four TEST/MODEL source-test/workflow/ledger files. Neither PR edits `Mathematics/library/linear-equations.v1.json`, Physics explorer pages, site-search compiled outputs, frozen Owner goldens, `Shared/web/interactive-page-blueprints.v1.json`, or `Shared/tools/render_core.py`.

## Conclusion bounded by evidence

- **Confirmed:** The three broad check **categories** failed on `main` before the D1 PR and failed again on #206. Exact failing signatures are outside changed QRT paths. Scoped native render and blueprint role tests pass.
- **Not confirmed:** Exact per-test finding-set identity/delta for every broad gate. A pre-existing category-level failure is not a blanket waiver or guaranteed absence of a new regression.
- **Action:** Keep checks red and visible. A maintainer should run baseline and head with identical toolchain and compare exact test IDs/findings before integration. Fix Mathematics/Physics/global generated artefacts on their own governed workstreams; do not smuggle unrelated repairs into issue #200.
