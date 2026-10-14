#!/usr/bin/env python3
"""#182 R8 P2c: all source-eligible five-Core native instructional gates.

This probes real registered-renderer PAGES in Chromium, never copied/held HTML,
at nine role/viewport combinations. Mechanical protected-payload, preattempt,
blank-attempt, H2/H3, Core1B boundary, SVG names, stylesheet and overflow gates
are distinct from cognitive demand, prior Y, W preservation and mathematics.

The four previously authored *narrow* leak oracles are carried over only where
a specific cell already has an oracle. The other 17 are explicitly NOT_RUN
for source-specific semantic leakage. Absence of flagged text is never a pass.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from qrt_intent_contract import ROLES, ensure, read_json, sha256
from qrt_intent_w_path_audit import (
    PATHS, capture, gate_check, known_exposure,
)

FOUR_NARROW_ORACLES = frozenset({
    "QRT-EXPLAIN-D3", "QRT-MODEL-D2",
    "QRT-RETRIEVE-D2", "QRT-RETRIEVE-D4",
})
GATE_MUTATIONS = {
    "CORE1B_MAIN_UNLOCKS_BOUNDARY":
        ("core1b_main_attempt_unlocked_boundary",
         "CORE1B_BOUNDARY_UNLOCKED_BY_MAIN_COMMIT"),
    "CORE1B_BLANK_UNLOCKS_BOUNDARY":
        ("core1b_blank_boundary_unlocked",
         "CORE1B_BLANK_BOUNDARY_UNLOCKED"),
    "CORE2A_H3_PRECOMMIT_UNLOCK":
        ("core2a_h3_unlocked_before_commit",
         "CORE2A_H3_PREATTEMPT_UNLOCKED"),
    "PRECOMMIT_SOLUTION_MATERIALIZED":
        ("precommit_payload_materialized",
         "PRECOMMIT_PROTECTED_PAYLOAD_MATERIALIZED"),
    "BLANK_ATTEMPT_UNLOCKS_PAYLOAD":
        ("blank_main_unlocked",
         "BLANK_MAIN_UNLOCKED_PROTECTED_PAYLOAD"),
}


def summarize(cell: str, states: dict, gates: dict,
              viewport_receipts: list[dict]) -> dict:
    ensure(set(states) == set(ROLES) and
           len(viewport_receipts) == 9,
           "P2C_FIVE_ROLES_NINE_VIEWPORTS_REQUIRED", cell)
    observed = {(p["role"],p["viewport"]) for p in viewport_receipts}
    expected = {(role, width)
                for role in ROLES
                for width in ((390,768,1280)
                              if role in ("CORE2A", "CORE2B")
                              else (390,))}
    ensure(observed == expected, "P2C_ROLE_VIEWPORT_MATRIX_DRIFT", cell)
    ensure(all(x["http"] == 200 and
               x["original_stylesheets_loaded"] is True and
               x["horizontal_overflow"] is False
               for x in viewport_receipts),
           "P2C_REAL_LAYOUT_STYLES_HTTP", cell)
    ensure(not gate_check(gates),
           "P2C_NATIVE_GATE_REGRESSION", cell+":"+repr(gate_check(gates)))

    # These five specific bad state mutations are tested against the SAME
    # executable predicate, with no modification to source/native HTML.
    mutants = []
    for mutation, (flag, expected_id) in GATE_MUTATIONS.items():
        bad = copy.deepcopy(gates)
        bad[flag] = True
        caught = gate_check(bad)
        ensure(expected_id in caught, "P2C_MUTATION_ESCAPED",
               cell+":"+mutation)
        mutants.append({
            "name": mutation,
            "expected_block": expected_id,
            "caught_by_same_gate_checker": True,
            "mutation_applied_to_evidence_only": True,
        })

    narrow = cell in FOUR_NARROW_ORACLES
    findings = []
    if narrow:
        for role in ROLES:
            findings.extend({"role":role,"finding":finding}
                            for finding in known_exposure(cell,role,states[role]))
    known = sorted({x["finding"] for x in findings})
    paths = []
    for key, roles in PATHS.items():
        paths.append({
            "name": key,
            "roles": list(roles),
            "mechanically_inspected_roles":
                list(dict.fromkeys(roles)),
            "cumulative_w_semantics":
                "KNOWN_NARROW_SENTINEL_ONLY" if narrow else
                "NOT_RUN_SOURCE_SPECIFIC_ORACLE",
            "independent_learner_math":
                False if "ASSISTED_RETURN" in key else "NOT_ESTABLISHED",
            "not_a_real_replay":
                True,
        })
    ensure(len(paths) == 5 and len(mutants) == 5,
           "P2C_PATH_OR_MUTATION_MISSING", cell)
    return {
        "schema": "imo182-r8-all-native-gates/v1",
        "cell_id": cell,
        "observed_real_native_browser_role_viewports": viewport_receipts,
        "original_native_rendered_pages": True,
        "nine_real_role_viewports": len(viewport_receipts),
        "technical_gate_flags": gates,
        "technical_gate_findings": gate_check(gates),
        "five_cumulative_exposure_hypotheses": paths,
        "simulated_exposure_paths_not_real_learner_journeys": 5,
        "five_deliberate_technical_gate_mutants_rejected": mutants,
        "narrow_known_source_semantic_oracle":
            "RAN_NARROW_SENTINELS_NOT_ACCEPTANCE" if narrow
            else "NOT_RUN_FOR_THIS_CELL",
        "narrow_semantic_finding_ids": known,
        "narrow_semantic_findings": findings,
        "accessible_text_svg_role_hashes": {
            role: {
                "sha256_visible": hashlib.sha256(
                    states[role]["visible"].encode("utf-8")).hexdigest(),
                "sha256_svg_accessible": hashlib.sha256(
                    states[role]["accessible_svg"].encode("utf-8")).hexdigest(),
                "sha256_h2_visible": hashlib.sha256(
                    states[role]["h2_visible"].encode("utf-8")).hexdigest(),
            } for role in ROLES
        },
        "qualified_academic_review": "NOT_RUN",
        "source_specific_w_preservation": "NOT_ESTABLISHED",
        "human_screen_reader_review": "NOT_RUN",
        "independent_learner_performance": "NOT_RUN",
        "owner_acceptance": False,
        "publication": "FORBIDDEN",
        "release": "HOLD",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("native-contract", "source-root", "native-output", "out"):
        ap.add_argument("--"+name, type=Path, required=True)
    args = ap.parse_args()
    evidence = read_json(args.native_contract)
    cell = evidence["cell_id"]
    ensure(evidence["technical_contract"] == "VALIDATED_PROPOSAL" and
           evidence["native_evidence"]["all_role_structure"] == "PASS" and
           evidence["qualified_academic_review"] == "PENDING" and
           evidence["owner_qrt_acceptance"] == "PENDING",
           "P2C_NEEDS_SOURCE_PINNED_UNACCEPTED_P1",cell)
    native = evidence["native_evidence"]["roles"]
    ensure(set(native) == set(ROLES), "P2C_NATIVE_FIVE_ROLES_REQUIRED",cell)
    for role in ROLES:
        original = args.native_output / (role.lower()+".html")
        ensure(sha256(original)==native[role]["native_sha256"],
               "P2C_NATIVE_ROLE_SHA_DRIFT",cell+":"+role)
    ensure(not (args.native_output/"held-adaptation-receipt.json").exists(),
           "P2C_REJECT_HELD_COPIES",cell)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,args=["--no-sandbox"])
        try:
            states, gates, viewport_receipts = capture(
                browser,args.source_root,args.native_output)
        finally:
            browser.close()
    result = summarize(cell, states, gates, viewport_receipts)
    ensure(result["owner_acceptance"] is False and
           result["source_specific_w_preservation"]=="NOT_ESTABLISHED" and
           result["release"]=="HOLD", "P2C_AUTO_APPROVAL_FORBIDDEN",cell)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                        encoding="utf-8")
    print(f"{cell}: 9 original-native browser role/viewports PASS technical "
          f"gates, 5 gate mutants rejected; semantic oracle="
          f"{result['narrow_known_source_semantic_oracle']}, "
          f"known findings={result['narrow_semantic_finding_ids']}; "
          "academic/Owner release HOLD")


if __name__=="__main__":
    main()
