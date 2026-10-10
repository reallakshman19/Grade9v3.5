#!/usr/bin/env python3
"""F02 source-backed QRT × blueprint contract; never awards academic acceptance.

The 7×4 matrix selects one cell for each selected item. H/S/P/M review asks
are semantic questions, not mechanical counts. A clean structural ledger does
NOT mean learner understanding, QRT review, or release approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
# The standalone CLI is invoked by path in CI; its script directory otherwise
# replaces the repository root on sys.path.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from Shared.tools import question_review_matrix as qrt
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
BLUEPRINTS = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
GOLDEN_NAMES = (
    "imo-327-explain-d2.v1.json",
    "imo-327-model-d3.v1.json",
    "imo-327-justify-d4.v1.json",
)
MODEL_CELL = "QRT-MODEL-D3"
EXPECTED_CELLS = ("QRT-EXPLAIN-D2", MODEL_CELL, "QRT-JUSTIFY-D4")
REPAIR_STAGES = (
    "NEUTRAL_DEMONSTRATION", "GENERAL_PRINCIPLE", "CONCEPT_CHECK",
    "GUIDED_APPLICATION", "FRESH_INDEPENDENT_EXIT",
)
# Product-schema hint_ladder purposes; QRT H1/H2/H3 verbs are independent.
PRODUCT_HINT_PURPOSES = ("ORIENT", "CONNECT", "CONNECT")
QRT_HINT_OBJECTIVES = ("CLARIFY", "CORRELATE", "OPEN_THE_WAY")
# Explicit source pointers for all 12 semantic questions. These are NOT grades.
# S2/S3 use a *different authored Core1A teaching example*, not the D3 item.
ASK_SOURCES = {
    "H1": ("selected_question.scaffolds[0].text",),
    "H2": ("selected_question.scaffolds[1].text",),
    "H3": ("selected_question.scaffolds[2].text",),
    "S1": ("selected_question.representation_roles.initial_ref",),
    "S2": ("microtopics[0].representation_refs", "microtopics[0].construction_units[0].reveal_stage_refs"),
    "S3": ("microtopics[0].construction_units[0].reveal_stage_refs",),
    "P1": ("selected_question.stem", "selected_question.representation_roles.safe_ref"),
    "P2": ("selected_question.repair_ref", "microtopics[0].teaching_path"),
    "P3": ("selected_question.answer.reasoning_route", "selected_question.independent_check"),
    "M1": ("selected_question.failure_signal", "microtopics[0].misconceptions"),
    "M2": ("microtopics[0].extensions.grade9v3:concept_checkpoint.diagnostic",),
    # Structured patterns now exist; they DO NOT determine cognitive cause.
    "M3": ("selected_question.repair_ref", "microtopics[0].teaching_path"),
}
ROLE_SLOT_SOURCES = {
    "CORE1A": {
        "identity": ("microtopics[0].title",),
        "construction": ("microtopics[0].teaching_path", "microtopics[0].construction_units"),
        "repair_closure": ("microtopics[0].misconceptions", "microtopics[0].exit_task"),
    },
    "CORE2A": {
        "identity": ("selected_question.id", "selected_question.origin"),
        "attempt": ("selected_question.stem",),
        "reasoning": ("selected_question.answer.reasoning_route",),
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: str) -> str:
    return "".join(value.lower().split()).replace("×", "*")


def audit(
    package: dict[str, Any],
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    vocabulary: dict[str, Any],
    blueprint_registry: dict[str, Any],
    goldens: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    review_gates: list[str] = []
    if package.get("subject") != "TEST" or package.get("status") != "CANDIDATE":
        errors.append("PRODUCT_NOT_TEST_CANDIDATE")
    if manifest.get("subject") != "TEST" or manifest.get("output_roles") != ["CORE1A", "CORE2A"]:
        errors.append("MANIFEST_ROLES_NOT_TEST_CORE1A_CORE2A")
    selection = manifest.get("selection") or {}
    if selection.get("core2") != [] or selection.get("core2b") != []:
        errors.append("AUTHENTIC_CORE2_OR_TRANSFER_SELECTED")
    qs = [x for x in package.get("questions", []) if x.get("id") in selection.get("core2a", [])]
    ms = [x for x in package.get("microtopics", []) if x.get("id") in selection.get("microtopics", [])]
    if len(qs) != 1 or len(ms) != 1 or len(selection.get("core2a", [])) != 1:
        errors.append("EXPECTED_EXACTLY_ONE_SELECTED_MODEL_D3_AND_MICROTOPIC")
    question = qs[0] if qs else {}
    microtopic = ms[0] if ms else {}

    golden_cells = [g.get("matrix", {}).get("expected_cell") for g in goldens]
    if golden_cells != list(EXPECTED_CELLS):
        errors.append("GOLDEN_CELL_SET_CHANGED_OR_REORDERED")
    for golden in goldens:
        if (golden.get("status") != "AUTHOR_REVIEW_FIXTURE_NOT_LEARNER_PRODUCT"
                or golden.get("governance", {}).get("published") is not False):
            errors.append("GOLDEN_FALSE_PRODUCT_AUTHORITY")
    golden_model = goldens[1] if len(goldens) > 1 else {}
    if (question.get("id") != golden_model.get("task", {}).get("candidate_question_id")
            or question.get("stem") != golden_model.get("task", {}).get("stem")):
        errors.append("MODEL_D3_GOLDEN_ITEM_MISMATCH")

    resolution: dict[str, Any] = {}
    try:
        if qrt.validate_contract(matrix, vocabulary):
            errors.append("SOURCE_QRT_MATRIX_CONTRACT_INVALID")
        else:
            cells = qrt.compile_templates(matrix, vocabulary)
            if len(cells) != 28:
                errors.append("QRT_MATRIX_NOT_28_REVIEW_CELLS")
            if question:
                resolution = qrt.resolve_review(
                    question, {"profile_id": "F02-SOURCE-AUDIT", "held": {}},
                    matrix, vocabulary,
                )
                if resolution["template_id"] != MODEL_CELL:
                    errors.append("SELECTED_ITEM_NOT_MODEL_D3")
                if (resolution["classification"]["demand"]["primary_move_ref"]
                        != (question.get("answer") or {}).get("crux_move_ref")):
                    errors.append("PROTECTED_DECISION_NOT_CANONICAL_CRUX")
    except (ValueError, KeyError, TypeError, StopIteration) as exc:
        errors.append("QRT_RESOLUTION_INVALID:" + type(exc).__name__)

    h_ledger = []
    hints = question.get("hint_ladder") or []
    scaffolds = question.get("scaffolds") or []
    if len(hints) < 3 or len(scaffolds) < 3:
        errors.append("D3_PROGRESSIVE_HINTS_INCOMPLETE")
    for index, target in enumerate(PRODUCT_HINT_PURPOSES):
        qrt_verb = (matrix.get("review_asks", {}).get(f"H{index + 1}", {})
                    .get("verb"))
        if qrt_verb != QRT_HINT_OBJECTIVES[index]:
            errors.append(f"QRT_H{index + 1}_OBJECTIVE_EXPECTED_{QRT_HINT_OBJECTIVES[index]}")
        row = hints[index] if index < len(hints) else {}
        scaffold = scaffolds[index] if index < len(scaffolds) else {}
        if row.get("order") != index + 1 or row.get("purpose") != target:
            errors.append(f"D3_H{index + 1}_PURPOSE_EXPECTED_{target}")
        if row.get("from") != f"scaffolds[{index}]" or not scaffold.get("text"):
            errors.append(f"D3_H{index + 1}_SOURCE_MISSING")
        text = str(scaffold.get("text") or "")
        for protected in golden_model.get("item_help", {}).get("must_not_reveal_before_attempt", []):
            if _norm(protected) and _norm(protected) in _norm(text):
                errors.append(f"D3_H{index + 1}_LEAKS_PROTECTED_WORK")
        h_ledger.append({
            "objective": f"H{index + 1}",
            "declared_purpose": row.get("purpose"),
            "product_hint_purpose": row.get("purpose"),
            "qrt_semantic_verb": qrt_verb,
            "source": f"selected_question.scaffolds[{index}].text",
            "status": "SOURCE_PRESENT_SEMANTICS_REQUIRE_REVIEW",
        })

    if question.get("repair_ref") not in [s.get("id") for s in microtopic.get("teaching_path", [])]:
        errors.append("P2_REPAIR_REF_UNRESOLVED")
    if not microtopic.get("exit_task", {}).get("prompt"):
        errors.append("CORE1A_FRESH_EXIT_ABSENT")
    concept = microtopic.get("extensions", {}).get("grade9v3:concept_checkpoint", {})
    if concept.get("status") != "LOCAL_TEACHING_FORMAT_CHECK_NOT_INDEPENDENT_MASTERY":
        errors.append("CONCEPT_CHECK_FALSE_MASTERY_STATUS")
    neutral = concept.get("diagnostic") or {}
    if (neutral.get("scope") != "NEUTRAL_NUMERICAL_COUNTEREXAMPLE_NOT_TARGET_ITEM"
            or neutral.get("status") != "LOCAL_STRUCTURED_NUMERICAL_PATTERN_NOT_MASTERY"
            or neutral.get("base") != 7 or neutral.get("exponent") != 2
            or not isinstance(neutral.get("prompt"), str)
            or "7³" not in neutral["prompt"]):
        errors.append("NEUTRAL_COUNTEREXAMPLE_MISSING_OR_NOT_AUTHORED")
    else:
        # This numerical case is independent of the source D3 question;
        # its expected outputs (343, 56) do not prove a general exponent law.
        if neutral["base"] ** (neutral["exponent"] + 1) == (
                neutral["base"] ** neutral["exponent"] + neutral["base"]):
            errors.append("NEUTRAL_COUNTEREXAMPLE_CANNOT_FALSIFY_ADDITION")
        forbidden = golden_model.get("item_help", {}).get("must_not_reveal_before_attempt", [])
        public_neutral = " ".join(str(neutral.get(k) or "") for k in (
            "prompt", "next_label", "add_label", "on_missing", "on_inconsistent",
            "on_additive_route", "on_conflict", "on_aligned",
        ))
        if any(_norm(token) in _norm(public_neutral) for token in forbidden):
            errors.append("NEUTRAL_COUNTEREXAMPLE_LEAKS_D3_PROTECTED_WORK")

    # The three author goldens contain a design sequence, NOT accepted runtime evidence.
    golden_steps = [s.get("stage") for s in golden_model.get("core1a_repair", {}).get("sequence", [])]
    if golden_steps != list(REPAIR_STAGES):
        errors.append("GOLDEN_D3_FIVE_STAGE_REFERENCE_INVALID")

    bps = {b.get("id"): b for b in blueprint_registry.get("blueprints", [])}
    slot_ledger: list[dict[str, str]] = []
    role_bps = {"CORE1A": "BP-CORE1A-CONSTRUCTION", "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION"}
    for role, bp_name in role_bps.items():
        bp = bps.get(bp_name)
        if not bp or role not in bp.get("core_roles", []):
            errors.append(f"BLUEPRINT_ROLE_UNRESOLVED_{role}")
            continue
        expected_slots = ROLE_SLOT_SOURCES[role]
        for slot in (s for s in bp.get("slots", []) if s.get("required")):
            sid = slot.get("id")
            if sid not in expected_slots:
                errors.append(f"BLUEPRINT_REQUIRED_SLOT_UNMAPPED_{role}_{sid}")
                continue
            slot_ledger.append({
                "role": role, "blueprint": bp_name, "slot": sid,
                "source": ", ".join(expected_slots[sid]),
                "status": "SOURCE_MAPPED_RENDER_AND_SEMANTICS_UNVERIFIED",
            })

    # Semantic H/S/P/M asks must be reviewed, not marked PASS by string matching.
    asks = []
    for name in qrt.ASKS:
        d = resolution.get("review", {}).get(name, {})
        if name == "M2":
            status = "STRUCTURED_RESPONSE_PATTERNS_COGNITIVE_CAUSE_UNVERIFIED"
        elif name == "P2":
            status = "SOURCE_ROUTE_DECLARED_PRECISE_STEP_NOT_VERIFIED"
        elif name in ("S2", "S3"):
            status = "DIFFERENT_CORE1A_EXAMPLE_ITEM_SEMANTICS_UNVERIFIED"
        else:
            status = "SOURCE_PRESENT_SEMANTICS_REQUIRE_REVIEW"
        asks.append({
            "ask": name, "question": d.get("question", ""),
            "objective": d.get("objective", ""),
            "source_pointers": list(ASK_SOURCES[name]), "status": status,
        })
    review_gates.extend([
        "H_S_P_M_INDEPENDENT_SEMANTIC_REVIEW_REQUIRED",
        "M2_CAUSAL_MISCONCEPTION_VS_EXECUTION_SLIP_NOT_VERIFIED",
        "P2_PRECISE_TC02_LEARNER_ROUTE_NOT_VERIFIED",
        "FRESH_UNASSISTED_POST_REPAIR_RETURN_NOT_ENFORCED",
        "FREE_TEXT_REASON_MATHEMATICAL_CORRECTNESS_NOT_GRADED",
        "BLUEPRINT_RENDERED_CONTENT_AND_WAIVERS_NOT_INDEPENDENTLY_REVIEWED",
    ])
    repair_sequence = [
        {"stage": "NEUTRAL_DEMONSTRATION",
         "source": "microtopics[0].extensions.grade9v3:concept_checkpoint.neutral_demo",
         "status": "SOURCE_DECLARED_NOT_PEDAGOGICALLY_GRADED"},
        {"stage": "GENERAL_PRINCIPLE",
         "source": "microtopics[0].teaching_path[0].why_valid",
         "status": "SOURCE_DECLARED_NOT_PEDAGOGICALLY_GRADED"},
        {"stage": "CONCEPT_CHECK",
         "source": "microtopics[0].extensions.grade9v3:concept_checkpoint.prompt",
         "status": "STRUCTURED_NUMERIC_CHECK_ONLY_FREE_TEXT_UNGRADED"},
        {"stage": "GUIDED_APPLICATION",
         "source": "microtopics[0].teaching_path[1..4]",
         "status": "DIFFERENT_AUTHORED_EXAMPLE_NOT_INDEPENDENT"},
        {"stage": "FRESH_INDEPENDENT_EXIT",
         "source": "microtopics[0].exit_task.prompt",
         "status": "PROMPT_PRESENT_UNASSISTED_RETURN_NOT_ENFORCED"},
    ]
    return {
        "schema": "imo-f02-qrt-blueprint-contract/v1",
        "subject": "TEST", "academic_status": "HOLD_NOT_ACCEPTED",
        "selected_item": question.get("id"),
        "selected_cell": resolution.get("template_id"),
        "crux_move_ref": (question.get("answer") or {}).get("crux_move_ref"),
        "protected_W": resolution.get("slots", {}).get("W", {}).get("text", ""),
        "golden_reference_cells": golden_cells,
        "rendered_coverage_cells": [resolution["template_id"]] if resolution else [],
        "source_hints": h_ledger,
        "semantic_review_asks": asks,
        "core1a_repair_reference_alignment": repair_sequence,
        "blueprint_required_slots": slot_ledger,
        "errors": sorted(set(errors)),
        "review_gates": review_gates,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="Fail until both source errors and independent semantic gates are closed.")
    ap.add_argument("--output", type=Path, help="Write deterministic evidence ledger JSON to this path.")
    args = ap.parse_args()
    result = audit(
        read_json(PACKAGE), read_json(MANIFEST),
        read_json(qrt.MATRIX_PATH), read_json(qrt.VOCAB_PATH),
        read_json(BLUEPRINTS),
        [read_json(ROOT / "TEST/imo-research/golden" / name) for name in GOLDEN_NAMES],
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 1 if result["errors"] or (args.strict and result["review_gates"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
