# Concept Map — Grade 9 IMO Learning Pipeline, QRT, Rendering, Validation and Repair

**Purpose:** This file is the single orientation read for any new contributor entering the Grade 9 IMO learning workflow. It describes the **process map**, the authoritative artifacts, the end-to-end flow, the validation gates, and the correction loop.

**Important:** This is a **process map**, not an implementation approval, academic acceptance, golden designation, rights decision, merge authorization or release authorization.

---

## 1. What this system is trying to produce

The system exists to turn a governed set of mathematics questions and concept records into **native learner-facing Core pages** that are:

- source-faithful where source custody matters,
- pedagogically structured,
- QRT-classified,
- rendered through one governed pipeline,
- independently validated,
- benchmarked against the correct references,
- and only then considered for acceptance and release.

The workflow supports multiple Core roles, but all of them must pass through the same high-level chain:

**source/question identity → academic analysis → QRT classification → Core records → native rendering → benchmark + independent review → Owner decision**

---

## 2. The major process zones

The whole system can be understood as **seven connected zones**.

1. **Authority & Governance**
2. **Source & Identity**
3. **Academic Analysis & QRT**
4. **Core Record Authoring**
5. **Native Rendering**
6. **Independent Validation & Benchmarking**
7. **Correction, Revalidation and Decision**

These zones are described below.

---

## 3. Zone 1 — Authority & Governance

This zone defines what is allowed to enter the workflow and who can make binding decisions.

### 3.1 Authorities

The workflow is governed by a set of explicit authorities, each with a different role.

- **Owner intent / AIM contract**  
  Defines the target outcomes, boundaries, acceptance responsibilities and release control.

- **QRT specification**  
  Defines the semantic review model, including the 7 cognitive demands, 4 difficulty bands, X/Y/Z/W reasoning structure and H/S/P/M learning obligations.

- **Blueprint registry**  
  Defines the page architecture and required learner behavior for each Core role.

- **Golden / reference fixtures**  
  Provide comparison anchors for visual or behavioral benchmarking, but do not replace academic review.

- **Renderer contract**  
  Defines the native rendering pipeline that turns valid records and manifests into HTML.

- **Validation contracts**  
  Define what independent checks must be performed before any artifact can be considered trustworthy.

### 3.2 Distinct decision types

The following decisions must never be collapsed into one another:

- technical completeness,
- academic correctness,
- QRT acceptance,
- golden designation,
- source-rights clearance,
- product admission,
- merge authorization,
- release authorization.

A green test run is **not** equivalent to any of those final decisions.

---

## 4. Zone 2 — Source & Identity

This zone answers: **What exactly is the thing we are working on?**

There are two important populations in the wider workflow:

- a **research / intake population** of question records used for large-scope analysis,
- and a **frozen authentic product population** of source-governed question identities.

These populations may overlap, but they are not automatically interchangeable.

### 4.1 Required source facts

For each question or concept-bearing unit, the workflow needs:

- stable identity,
- source occurrence or source lineage,
- original stem / options / figure boundaries where applicable,
- source answer provenance where applicable,
- rights / custody status,
- and the exact commit or manifest defining the working baseline.

### 4.2 Source integrity rules

- Source identities must not drift silently.
- Duplicate collapse must not erase real occurrences.
- Research records must not be promoted to authentic product records without explicit proof.
- Source-supplied material must be distinguished from authored pedagogical additions.

---

## 5. Zone 3 — Academic Analysis & QRT

This zone answers: **What does the learner actually have to do, and why?**

### 5.1 Mathematical analysis

Each question or concept target requires academic analysis to identify:

- the decisive crux,
- the governing concept or relation,
- the primary learner-owned decision,
- the correct mathematical route,
- adjacent but less appropriate interpretations,
- likely misconceptions,
- and the correct final answer or justification.

### 5.2 QRT structure

The question is then interpreted through the QRT model.

#### 5.2.1 Cognitive demand

One primary demand is identified from the QRT vocabulary:

- RETRIEVE
- EXPLAIN
- APPLY
- MODEL
- REPRESENT
- SYNTHESIZE
- JUSTIFY

#### 5.2.2 Difficulty band

One difficulty band is assigned:

- D1
- D2
- D3
- D4

The band is derived from the canonical multi-factor difficulty logic, not from vague intuition or aggregate styling.

#### 5.2.3 QRT cell

Demand × band determines one QRT cell, such as:

- `QRT-MODEL-D2`
- `QRT-JUSTIFY-D4`
- `QRT-APPLY-D1`

#### 5.2.4 X / Y / Z / W

The semantic structure also identifies:

- **X** — what is directly given or already available,
- **Y** — the relevant relation or conceptual bridge,
- **Z** — the needed transformation or inference path,
- **W** — the protected decisive learner-owned move.

#### 5.2.5 H / S / P / M expectations

The QRT cell then constrains the learning support that can legitimately appear:

- **H** — hints,
- **S** — staged visuals / scaffolds,
- **P** — progression / page-stage behaviors,
- **M** — misconception / diagnosis / repair behavior.

These are semantic obligations, not decorative extras.

---

## 6. Zone 4 — Core Record Authoring

This zone answers: **What structured records are needed to teach or test this correctly?**

The system supports multiple Core roles, each with a different educational purpose.

### 6.1 Core-role family

The governed set includes:

- Core 1 Orientation
- Core 1A Construction
- Core 1B Reconstruction
- Core 2 Source Question
- Core 2A Supported Application
- Core 2B Transfer
- Explorer (separate non-Core interactive role)

### 6.2 Role purpose

Each role has a distinct job:

- **Core 1 Orientation** — situate the learner, prerequisites and entry bridge.
- **Core 1A Construction** — teach the underlying concept with worked construction.
- **Core 1B Reconstruction** — require the learner to reconstruct and repair understanding.
- **Core 2 Source Question** — preserve source-faithful attempt-first question experience.
- **Core 2A Supported Application** — apply with controlled support.
- **Core 2B Transfer** — test changed-demand or changed-given transfer.
- **Explorer** — separate exploratory/interactive function.

### 6.3 Core relationship rules

- A Core record must match the correct role blueprint.
- Core 1A and Core 1B may share conceptual truth, but not identical learner behavior.
- Core 2 must remain faithful to source-question boundaries where required.
- Shared concept records are allowed only when the underlying inferential jump truly matches.
- Topic similarity alone is not sufficient justification for sharing.

### 6.4 Research bank versus native product records

Research JSON and authored experimental records can be useful inputs, but they do not automatically satisfy native product requirements.

Any bridge from research records to product-grade records must preserve:

- identity,
- evidence,
- role correctness,
- and the distinction between authored support and source custody.

---

## 7. Zone 5 — Native Rendering

This zone answers: **How do validated records become actual learner pages?**

### 7.1 One governed rendering path

The intended workflow uses one governed native renderer:

**validated records + manifest + registered blueprint → `Shared/tools/render_core.py` → native HTML**

### 7.2 Rendering responsibilities

The renderer is responsible for producing the actual learner experience from structured records.

It is not responsible for deciding:

- whether the mathematics is correct,
- whether the QRT classification is accepted,
- whether the source is authentic,
- or whether the page is pedagogically sufficient.

It only turns accepted record structures into native page outputs.

### 7.3 Blueprint role in rendering

The blueprint controls:

- page structure,
- interaction boundaries,
- display sequencing,
- support staging,
- and role-specific learner flow.

The blueprint does **not** itself determine the mathematical truth or QRT acceptance.

---

## 8. Zone 6 — Independent Validation & Benchmarking

This zone answers: **Does the output actually satisfy the intended architecture, semantics and learner protections?**

This is where the validator belongs.

### 8.1 Validator purpose

The validator is an **independent assurance layer**. It does not author the learning content as its main function. It inspects and proves whether the content, structures and outputs are trustworthy.

### 8.2 What the validator must cover

The validator must span the whole process, not only the JSON bank.

#### 8.2.1 Intake and denominator checks

- all expected records are present,
- identities are stable,
- duplicates are handled correctly,
- no records are silently omitted,
- historical audits are not reused out of scope.

#### 8.2.2 Source and custody checks

- source fidelity,
- option integrity,
- figure provenance,
- source locator presence,
- rights/custody status,
- no silent source drift.

#### 8.2.3 Academic correctness checks

- final answer correctness,
- proof validity,
- derivation soundness,
- correct crux,
- correct model/strategy,
- no hidden contradictions between hint and solution.

#### 8.2.4 QRT checks

- primary demand defensibility,
- difficulty-band defensibility,
- QRT-cell consistency,
- X/Y/Z/W correctness,
- protection of W,
- correct H/S/P/M staging.

#### 8.2.5 Core-role checks

- correct blueprint-role alignment,
- correct Core 1A / Core 1B conceptual relation,
- correct Core 2 source-faithful behavior,
- justified shared concept reuse,
- correct application / transfer logic.

#### 8.2.6 Native rendering checks

- rendered output exists,
- blueprint structure is respected,
- no broken stage gating,
- no pre-attempt answer leakage,
- responsive/browser checks where required,
- print/A4/visual behavior where required.

#### 8.2.7 Benchmark and golden checks

- compare against the correct golden or reference,
- distinguish candidate fixtures from approved ones,
- verify scope of approval,
- do not treat a visual golden as universal academic approval.

#### 8.2.8 Validator-self benchmarking

The validator itself must be challenged with:

- known-good fixtures,
- known-bad fixtures,
- mutations,
- false-pass traps,
- false-fail traps.

A validator that cannot detect seeded defects is not trustworthy.

### 8.3 Validator outcomes

The validator should emit explicit states such as:

- PASS
- FAIL
- REVIEW_REQUIRED
- NOT_RUN
- NOT_APPLICABLE
- STALE

Critical failures must not be masked by aggregate scores.

---

## 9. Zone 7 — Correction, Revalidation and Decision

This zone answers: **What happens when the validator finds a problem?**

### 9.1 Repair principle

The content-correction stream is separate from the validator stream.

The correction stream consumes:

- frozen findings,
- exact question IDs,
- affected concepts,
- failed rules,
- and acceptance conditions.

It then produces bounded corrected artifacts.

### 9.2 Correction boundaries

The correction stream may fix:

- question records,
- Core records,
- SVGs or figures,
- shared concept links,
- staged supports,
- native output problems.

It must not silently change the validator’s rules simply to make findings disappear.

### 9.3 Revalidation

After a correction freeze, the validator performs independent revalidation.

This revalidation checks:

- the original defect,
- nearby shared dependencies,
- regression risk,
- updated outputs,
- and any changed benchmark references.

### 9.4 Final decision

Only after independent revalidation can the workflow move to qualified review and Owner decision.

That decision may cover:

- QRT acceptance,
- golden acceptance,
- source-right clearance,
- product admission,
- merge,
- release.

Those remain separate decisions.

---

## 10. End-to-end process flow

This is the full pipeline in one chain.

```text
Owner intent / AIM
        ↓
Canonical authorities loaded
(QRT spec, blueprint registry, renderer contract, golden references)
        ↓
Working baseline pinned
(commit SHA, manifests, research records, product records)
        ↓
Source & identity established
(question IDs, source lineage, figures, options, rights/custody state)
        ↓
Academic analysis
(crux, answer, reasoning, misconceptions)
        ↓
QRT resolution
(primary demand + difficulty band + QRT cell + X/Y/Z/W + H/S/P/M)
        ↓
Core record authoring / selection
(Core 1 / 1A / 1B / 2 / 2A / 2B / Explorer)
        ↓
Native rendering
(validated records + blueprint + renderer → HTML)
        ↓
Independent validation & benchmarking
(source, math, QRT, Core role, rendering, goldens, browser, validator benchmark)
        ↓
Findings ledger
(PASS / FAIL / REVIEW_REQUIRED / STALE / etc.)
        ↓
Bounded correction stream
(question/Core/SVG/relationship fixes)
        ↓
Independent revalidation
        ↓
Qualified review
        ↓
Owner decision
(QRT acceptance / golden / admission / merge / release)
```

---

## 11. Process dependencies

A few key dependencies govern the map.

### 11.1 QRT depends on academic analysis

A QRT cell must not be assigned only because a structural template fits. It depends on a correct reading of the first meaningful learner decision.

### 11.2 Core construction depends on QRT and concept truth

Core pages should not be authored only by chapter/topic grouping. They depend on the actual concept and inferential jump identified in analysis.

### 11.3 Rendering depends on validated records

The renderer should consume structured, governed records. It should not be used as a substitute for validation.

### 11.4 Golden comparison depends on correct scope

A golden can validate some aspects of a page, but not automatically all aspects. Visual golden approval does not equal full academic approval.

### 11.5 Release depends on independent review

No green pipeline or completed workpack is enough on its own.

---

## 12. Current known split in the working universe

There is a practical split between:

- a **research / intake validation universe** with a larger denominator of research question records,
- and a **frozen authentic delivery universe** with a smaller denominator of source-governed question journeys.

This means:

- a finding in the research universe is useful but does not automatically admit a product artifact,
- and a product-governed decision requires source and rights discipline beyond research structure.

Both universes still depend on the same process architecture:

**authority → source → analysis → QRT → Core → rendering → validation → correction → decision**

---

## 13. Minimum reading model for a new contributor

A new contributor should use this file as the primary orientation and then ask four questions before making changes:

1. **What artifact am I actually changing?**  
   Source record, Core record, blueprint-facing data, native output, benchmark, or validator logic?

2. **Which authority governs this artifact?**  
   Owner intent, QRT spec, blueprint registry, renderer, golden, or source custody rules?

3. **What process zone am I acting in?**  
   Source, analysis, authoring, rendering, validation, correction, or decision?

4. **What must remain separate?**  
   Technical completeness, academic correctness, QRT acceptance, golden status, source rights, merge, and release.

If these four questions are not answered first, the workflow is likely to drift.

---

## 14. Practical orientation for current work

At the present stage, the validator work should be understood as building and executing the **independent validation zone** across:

- research question records,
- QRT evidence,
- Core relationships,
- blueprint compliance,
- rendered outputs,
- and benchmark references.

The correction stream should remain separate and consume validator findings only after the validator has produced a stable, trustworthy evidence interface.

That separation is essential because the workflow is not just trying to render pages. It is trying to create **governed educational artifacts whose mathematics, learning behavior and source boundaries are all trustworthy**.

---

## 15. One-sentence summary

This system is a governed process that converts source-aware mathematical records into native learner pages through QRT-driven Core authoring and one renderer, and then subjects those outputs to independent validation, correction and Owner decision before any acceptance or release.

---

## 16. Current source-first entry points (verify live state)

- Governing issue and Owner intent: https://github.com/reallakshman19/Grade9v3.5/issues/249
- Research source/standalone product candidate: https://github.com/reallakshman19/Grade9v3.5/pull/240 (260 research records; source copyright/admission not granted)
- Independent QRT validator candidate: https://github.com/reallakshman19/Grade9v3.5/pull/250 (research intake and generated HTML assurance; not yet full academic signoff)
- Exclusive source repair contract: https://github.com/reallakshman19/Grade9v3.5/issues/254 (fix builder, pedagogical defects, regenerate four HTML files into source PR branch)
- Exact-head hosted negative-control evidence: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38616372230 (25/25 mutation/falsifier tests, 260/260 HTML failures on three independent pre-attempt disclosure categories)

These are navigational pointers and observed baseline, not authorization. Read latest GitHub state before writing. This file describes the process; issue #249 governs its current work scope.
