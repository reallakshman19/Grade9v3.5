# Physics QRT — low-thinking multi-agent programme (draft)

This small read-only foundation supports the Option C **demand-first native** programme. It does not replace Physics/adapter, QRT, Core, or the existing renderer. It is not a v3.6 lifecycle registration or academic certificate.

Read [PROGRAMME_CONTRACT.md](PROGRAMME_CONTRACT.md) first. [AGENT_WORK_ORDERS.md](AGENT_WORK_ORDERS.md) gives four fixed four-step tasks; C0 coordinator freezes actual question IDs, source SHA-256, non-overlapping file leases, independent scientific oracles and Owner permission.

**Initial status:** DRAFT_HOLD, no frozen question set, no approved scientific oracle. The repository currently selects V3_1 in `relay/PROTOCOL_SELECTION.yaml`; no work-specific Physics v3.6 enrollment is established. These are intentional. The Owner's authorization to open this foundation draft PR does not authorize the four workers' later production edits.

## Run offline from repository root

\`\`\`sh
python3 -m unittest tests.test_physics_qrt_program_contract -v
python3 -m tools.physics_qrt_program.cli validate-lock tools/physics_qrt_program/work-lock.template.json
python3 -m tools.physics_qrt_program.cli validate-lock tools/physics_qrt_program/work-lock.template.json --require-authorized
python3 -m tools.physics_qrt_program.cli validate-receipt --lock LOCK.json RECEIPT.json
python3 -m tools.physics_qrt_program.cli converge --lock LOCK.json L1.json L2.json L3.json L4.json
\`\`\`

The first lock command should return STRUCTURE_VALID_NOT_PERMISSION with exit code 0. The --require-authorized check should **fail** on the committed draft template. Receipt template also deliberately cannot pass before work is frozen.

## File architecture

- Physics/adapter/qrt_crosswalk.py: dedicated subject-level question → source/capability/Core source probe; not a shared engine rule
- contracts.py: core schema checks, safe paths/leases, source/head/scope binding, proof-carrying receipts, convergence always HOLD for science/release
- cli.py: offline validation and JSON-only report, no network or writes
- work-lock.template.json: draft coordinator data, with full write HOLD
- receipt.template.json: output shape only; NOT a valid completed worker result
- tests/test_physics_qrt_program_contract.py: adversarial unit tests proving gate behavior
- ../test_physics_qrt_program_contract.py: focused local unit tests

Do not auto-launch agents using these files. For a true two-pass independent investigation use Handover Master and its native live standalone schema; do not expose the issue/task/solution in its blind Pass 1. For lifecycle under an actually approved Physics v3.6 AIM, use native v3.6 generators/EP controls instead of inventing a label. BuddyRunner only for predecessor→successor handovers.

## First real checkpoint for coordinator

Select a small, exact case set from Physics real-demand evidence: Vectors/Motion 2D/NLM and optional Relative Motion regression. Enumerate each actual canonical question ID and source path/sha256 (no guessing), give a separately reviewed scientific oracle, then freeze W0 work lock. Retest current baseline at the pinned head. Only after distinct Owner authority should each agent create a separate scoped implementation branch.

## Native source-to-Core crosswalk (read-only)

Run `python3 -m tools.physics_qrt_program.cli inspect-question --package Physics/library/phy-nlm-first-law.v1.json --question Q-PHY-NLM-2B-FRICTION-STATE-01` to inspect actual source custody, primary capability and five-factor difficulty using the canonical `question_difficulty.derive`. It explicitly reports QRT demand UNRESOLVED, published output NOT_ATTESTED and academic REVIEW_REQUIRED. It never infers official source identity from external-demand citations.

## Wave-0 source candidates

Run `python3 -m tools.physics_qrt_program.cli bootstrap-w0`. It reads four real authored Physics source questions listed in `witnesses.candidate.v1.json`, verifies question/capability/Core identities and emits computed source SHA-256s in a draft, strictly unapproved work-lock. Vectors, Motion 2D, NLM FBD and NLM transfer are included; Relative Motion remains optional extension regression. This does not supply an approved scientific oracle, owner decision, QRT demand or learner/render evidence.

## Candidate scientific cross-checks — independent review not yet complete

`Physics/adapter/qrt_oracle_candidates.py` has four **candidate-only** numerical/model reconstruction functions for the exact Wave-0 families, with positive and deliberately wrong-model tests in `tests/test_physics_qrt_program_oracle_candidates.py`. They check vector direction as well as magnitude, one time base for projectile x/y, force ownership for the magnet FBD, and changing-normal-reaction thresholds under angled pulling. These functions are NOT wired into production Physics validation, QRT scoring or learner content. An independent subject reviewer must confirm their applicability before C0 locks the scientific oracle and L2 is allowed to alter production adapters.


## Academic reviewer packet — next gate

Run \`python3 -m Physics.adapter.qrt_review_packet\` to export a fully source-bound review-request JSON. For each Wave-0 question it contains exact canonical stem/conditions/author-written claim, source and individual-question digests, a bounded candidate calculation, model assumptions, adversarial false-model controls, and expert review questions. The packet is always \`PENDING_INDEPENDENT_PHYSICS_REVIEW\`, \`NOT_REVIEWED\` and \`permission_to_write: false\`. There is no auto-approval pathway.

The domain reviewer must independently re-derive the equations and physical assumptions, inspect model applicability, alternate valid results, signed axes and transfer novelty. C0 must authenticate any reviewer declaration separately and retain precise source SHA and acceptance evidence; a code test of the review packet is not an academic review or Owner permission.


## Future reviewer-response validation

\`python3 -m Physics.adapter.qrt_review_response --packet FROZEN_PACKET.json --response REVIEW_RESPONSE.json\` checks a submitted response for exact packet/question SHAs, independent-derivation fields, model-applicability reasons, review of all seeded falsifiers and an explicit result for each selected question. Every accepted *shape* is marked \`REVIEW_SUBMITTED_FOR_AUTHENTICATION\`; it does **not** verify the identity/competence of the reviewer or authorize code, academic acceptance or release. The template at \`Physics/adapter/qrt_science_review.template.json\` intentionally fails this gate until a real review is submitted.

## Reviewer digest hardening and independent-derivation intake

Reviewer-response validation recomputes the canonical hash of the entire packet
(excluding its self-referential `packet_sha256`) before accepting the claimed
digest. Tampered stems, predictions or falsifiers with an old digest fail with
`PACKET_CONTENT_DIGEST_MISMATCH`. A digest is content integrity, not qualified
reviewer identity, provenance, or authority. C0 must authenticate the reviewer
and compare the hash to the independently frozen packet.

Use `python3 -m Physics.adapter.qrt_review_packet --blind-intake` to create a
source-question stem/conditions-only request without authored answers,
model predictions, or seeded falsifiers. An independent reviewer should freeze
their own derivation before accessing the full comparison packet.
Reading the canonical source files can expose authored answers and should be
disclosed by the reviewer. Neither route authorizes learner release or worker writes.
