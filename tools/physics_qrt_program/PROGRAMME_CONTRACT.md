# Physics QRT low-thinking-agent programme — CORE CONTRACT v1

**Status:** DRAFT / NOT ENROLLED IN v3.6 / NO RELEASE AUTHORITY.
**Programme:** PHY-QRT-LTA-v1.
**Source pinned for the initial draft:** Grade9v3.5 main 73c66b64158ee2ff57b099f990e1c2081d5c571f.
**Goal:** One source-bound, independently falsifiable Grade-9 Physics learning/assessment evidence path with real rendered-product checks. Not a full-Physics acceptance claim and not a learner mastery declaration.

## Authority that cannot be recreated locally

1. Grade 9 scope derives from docs/grade9/GRADE9-PHYSICS-SCOPE-COVERAGE.md: 6 required-core, 2 support, 3 question-demand, 1 nondefault extension, 8 deferred. This document is a *derived audit*, not curricular authority. School chapter coverage != micro-demand.
2. Owner-approved ExamSIDE is question-demand evidence. It does not become Pinnacle school scope or rights to copy official stems, nor does an AUTHOR_CREATED candidate become an official exam question.
3. Existing Shared/tools/question_review_matrix.py and Shared/tools/question_difficulty.py own the 7 demand x 4 difficulty QRT and derived D-band. Never add tile-specific scorers or modify canonical D ranges.
4. Shared/roles/CORE-AUTHORITY-CONTRACT.md owns who may authorize CORE1/1A/1B/2/2A/2B. One source question cannot rewrite canonical conceptual truth.
5. Physics/library and Physics/adapter are academic/scientific candidates and subject adapters respectively. A magnitude check is not a vector-model proof. A code PASS is not scientific signoff.
6. Compiled Core and browser artifacts must trace to the declared library basis and exact rendered bytes. AUTHORED_OUTSIDE_THE_LIBRARY remains labelled honestly. Do not regenerate original publications to hide drift.
7. Learner evidence remains separate: source coverage, tests, routing and owner estimates never imply observed independent mastery.
8. The Handover Master in Common routes the correct native process. A Physics-specific approved v3.6 AIM + bound plan was not established at initial review; no v3.6 EP/label, legacy publication or merge entitlement may be inferred. The Owner's explicit request authorizes THIS draft foundation PR only. Future writes require their own approved boundaries.

## Decision separation

- **C0 coordinator / capable reasoning:** Own scope choice, actual authentic input rights, physical law/oracle choice, collision resolution, production writes, integration and final handoff.
- **Independent Physics reviewer:** Own correctness/model/assumption/transfer judgments and approved oracle receipt; cannot substitute CI green.
- **L1 low-thinking:** Extract honest question→source→capability→QRT→Core→render custody; output ledger only. Do not infer missing source.
- **L2 low-thinking:** Execute only coordinator-frozen scientific test cases; implement only reviewed bounded adapter checks after explicit authorized lease. No physics invention.
- **L3 low-thinking:** Run/extend read-only Core/visual/browser assertions against exact artifacts. No shared renderer or academic content edits.
- **L4 low-thinking:** Run seeded negative and true positive controls independently; no production code changes and no test self-approval.

## Wave contract

W0 COORDINATOR: Pin exact base commit + actual question IDs + source file SHA-256, scope class, scientific oracle, output authority, writer lease, Owner approval. Validate the lock; no worker writes.
W1 PARALLEL READ: Four agents independently inventory their assigned evidence. Freeze a single receipt per agent; never a chat ping-pong cycle.
W2 SCOPED WRITE: Only if work lock is FROZEN_APPROVED, recorded Owner write authorization and independently reviewed scientific oracle. Separate branches per writer; disjoint leases. If implementation needs a foreign writer's file return ESCALATE_WRITER.
W3 SINGLE CONVERGENCE: C0 evaluates all four role receipts on one exact basis; independent reviewer judges science and transfer; Owner separately decides merge/release.
Only C0 may change the frozen work-lock revision. Rebase invalidates dependent prior receipts unless proven unchanged; do not silently carry prior PASS to new head.

## Core data entities

work-lock/v1: repository, source base SHA, scope policy, actual selected_question_ids, witnessed authority class/path/SHA-256, capability, school_micro_demand, disjoint writer leases, governance approval/oracle SHA.

receipt/v1: agent, source SHA, candidate SHA or null, exact selected question scope, checks with command, expected, observed, exit code and evidence digest, owned artifacts with SHA, findings and uncertainties.

convergence/v1: mechanically detects invalid/missing agent receipts, duplicate writers, stale base, and authorization gaps. It is *always* REVIEW_REQUIRED for science/academic truth and HOLD for release. It cannot accept anything on the Owner's behalf.

## Mandatory acceptance gates

G0 source/Owner scope and write authority (HOLD if absent); G1 custody and external school-demand distinction; G2 independently reviewed scientific oracle; G3 canonical QRT/score/Core authority; G4 actual changed-demand Core2B/prior exposure and protected W; G5 exact-render Chromium/SVG and native output; G6 false-pass and false-alarm controls; G7 independent academic judgement; G8 exact-head CI, rights, Owner approval.

Do not equate G0–G6 envelope PASS with G7/G8. Neither a missing check nor a stale historical markdown count passes.

## Fixed pilot classes, NOT a fabricated admission corpus

- Motion 2D: existing approved preparation-demand cases and component model reasoning. Source docs/grade9/G9-PINNACLE-MOTION2D-EXAMSIDE-AUTHORING-AUDIT.md.
- NLM: actual model-choice, friction-state and existing transfer witnesses. Start by locating Q-PHY-NLM-2A-COV-03 and Q-PHY-NLM-2B-FRICTION-STATE-01 in current canonical source, not by assuming their fixture identity.
- Vectors: signed representation and mathematics bridge, only when required by witnessed learner action.
- Relative motion: extension regression only, not a default curriculum blocker. Legacy authored-outside publication stays excluded from source-bound proof.

## Standard read-only tests (run on exact selected head and retain logs)

python3 -m unittest tests.test_physics_qrt_program_contract -v
python3 Shared/tools/question_review_matrix.py check
python3 Shared/tools/matrix_conformance.py --enforce
python3 Shared/tools/publication_provenance.py --enforce
python3 Shared/tools/republish.py
python3 -m unittest tests.test_c6_examside_motion_in_plane tests.test_g9_nlm_examside_core2b_transfer

Chromium remains NOT_RUN unless browser executable is present and actual outputs are audited at their exact SHA. Never execute republish.py --write or alter protected goldens merely for a passing report.
