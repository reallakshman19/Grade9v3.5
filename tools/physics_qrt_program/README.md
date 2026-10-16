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

- contracts.py: core schema checks, safe paths/leases, source/head/scope binding, proof-carrying receipts, convergence always HOLD for science/release
- cli.py: offline validation and JSON-only report, no network or writes
- work-lock.template.json: draft coordinator data, with full write HOLD
- receipt.template.json: output shape only; NOT a valid completed worker result
- tests/test_physics_qrt_program_contract.py: adversarial unit tests proving gate behavior
- ../test_physics_qrt_program_contract.py: focused local unit tests

Do not auto-launch agents using these files. For a true two-pass independent investigation use Handover Master and its native live standalone schema; do not expose the issue/task/solution in its blind Pass 1. For lifecycle under an actually approved Physics v3.6 AIM, use native v3.6 generators/EP controls instead of inventing a label. BuddyRunner only for predecessor→successor handovers.

## First real checkpoint for coordinator

Select a small, exact case set from Physics real-demand evidence: Vectors/Motion 2D/NLM and optional Relative Motion regression. Enumerate each actual canonical question ID and source path/sha256 (no guessing), give a separately reviewed scientific oracle, then freeze W0 work lock. Retest current baseline at the pinned head. Only after distinct Owner authority should each agent create a separate scoped implementation branch.
