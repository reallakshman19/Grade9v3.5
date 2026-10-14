#!/usr/bin/env python3
"""Issue #182 R8 P5: 28-cell independent-academic -> Owner review handoff.

This generates an auditable *unapproved* disposition queue. It never assigns a
reviewer, validates academic expertise, issues a semantic MATCH, or accepts a
golden / original IMO item. Source classifications remain proposed until a
qualified independent adjudicator and the Owner separately decide.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from qrt_intent_contract import (
    BP, BANDS, DEMANDS, REVIEWS, ROLES, canonical, ensure, read_json, sha256
)

BLOCKS = {
    "RIVAL_NOT_GROUNDED_IN_SOURCE",
    "SOURCE_RIVAL_VOCAB_INVALID",
}
HOLD_TOKENS = ("PENDING", "NOT_RUN", "HOLD_REVIEW_REQUIRED")
REVIEW_VERDICTS = ("ACCEPT", "REVISE", "RECLASSIFY", "REJECT")
REVIEW_FIELDS = ("reasoned_math_warrant", "primary_vs_rival",
                 "canonical_band_assessment", "protected_W_observation",
                 "role_separation", "transfer_novelty",
                 "Y_prior_knowledge_evidence", "cumulative_exposure")


def make_packet(ledger: dict, bank: dict, evidence_dir: Path,
                coverage: dict, templates: dict) -> dict:
    ledger_rows = ledger["rows"]
    records = {x["cell_id"]: x for x in coverage["cells"]}
    witness_rows = bank["witnesses"]
    witness = {x["cell_id"]: x for x in witness_rows}
    ensure(len(ledger_rows) == 28 and len(records) == 28 and
           len(witness_rows) == 28 and len(witness) == 28,
           "P5_EXACT_28_SOURCE_RECORDS_REQUIRED")
    ensure({r["cell_id"] for r in ledger_rows} == set(records) == set(witness),
           "P5_LEDGER_COVERAGE_WITNESS_MISMATCH")
    templates_by_cell = {t["template_id"]: t for t in templates["templates"]}
    ensure(set(templates_by_cell) == set(witness),
           "P5_CANONICAL_TEMPLATES_MISSING")
    result = []
    for row in ledger_rows:
        cid = row["cell_id"]
        w = witness[cid]
        c = records[cid]
        slug = cid[len("QRT-"):].lower()
        file = evidence_dir / (slug + ".json")
        ensure(file.is_file(), "P5_SOURCE_CONTRACT_REPORT_MISSING", cid)
        evidence = read_json(file)
        actual_digest = sha256(file)
        ensure(c["evidence"]["qrt_contract_sha256"] == actual_digest,
               "P5_EVIDENCE_SHA_UNMATCHED", cid)
        ensure(evidence["cell_id"] == cid and
               evidence["owner_qrt_acceptance"] == "PENDING" and
               evidence["qualified_academic_review"] == "PENDING" and
               evidence["semantic_review"] == "HOLD_REVIEW_REQUIRED" and
               c["qualified_reviewer"] == "PENDING" and
               c["owner_qrt_acceptance"] is False,
               "P5_PREMATURE_ACCEPTANCE_PROHIBITED", cid)
        validated = evidence["technical_contract"] == "VALIDATED_PROPOSAL"
        blocked = evidence["technical_contract"] == "BLOCKED_RIVAL_REVIEW"
        ensure(validated != blocked, "P5_UNEXPECTED_CONTRACT_STATUS", cid)
        actual_block = evidence.get("blocking_error_code")
        ensure((validated and not actual_block) or
               (blocked and actual_block in BLOCKS),
               "P5_INVALID_HOLD_REASON", cid)
        ensure(evidence.get("strongest_rival", w["strongest_rival"])
               == w["strongest_rival"],
               "P5_RIVAL_HYPOTHESIS_DRIFT", cid)
        for key in ("primary_question_id", "transfer_question_id",
                    "primary_crux_move_ref", "transfer_crux_move_ref"):
            ensure(bool(w.get(key)), "P5_QUESTION_SPECIFIC_W_MISSING", cid)
        ensure(w["source_pin"]["source_path"] == row["source"]["path"] and
               w["source_pin"]["source_blob"] == row["source"]["git_blob_sha"] and
               w["source_pin"]["manifest_blob"] == row["manifest"]["git_blob_sha"],
               "P5_SOURCE_LEDGER_PIN_DRIFT", cid)
        primary_route = None
        transfer_route = None
        native_refs = {}
        browser_refs = []
        canonical_template = templates_by_cell[cid]
        reviews = []
        if validated:
            ensure(evidence["provenance"]["source_git_blob"] ==
                   row["source"]["git_blob_sha"] and
                   evidence["provenance"]["manifest_git_blob"] ==
                   row["manifest"]["git_blob_sha"],
                   "P5_VALIDATED_SOURCE_SHA_DRIFT", cid)
            primary_route = evidence["source_crux"]["primary"]
            transfer_route = evidence["source_crux"]["transfer"]
            ensure(primary_route["crux_move_ref"] ==
                   w["primary_crux_move_ref"] and
                   transfer_route["crux_move_ref"] ==
                   w["transfer_crux_move_ref"],
                   "P5_W_SOURCE_CRUX_DRIFT", cid)
            npath = evidence_dir / (slug + "-native.json")
            ensure(npath.is_file(), "P5_FIVE_NATIVE_PROOFS_REQUIRED", cid)
            n = read_json(npath)
            ensure(n["native_evidence"]["all_role_structure"] == "PASS" and
                   all(role in n["roles"] and
                       n["roles"][role]["semantic"] == "NOT_RUN"
                       for role in ROLES),
                   "P5_NATIVE_STRUCTURAL_NOT_SEMANTIC", cid)
            native_refs = {
                role: {
                    "blueprint": BP[role],
                    "native_sha256": n["roles"][role]["native_sha256"],
                    "golden_slot_component_match": "PASS",
                    "semantic": "NOT_RUN",
                    "instructional_role_decision": None,
                    "human_source_evidence": None,
                } for role in ROLES
            }
            apath = evidence_dir / (slug + "-w-audit.json")
            if apath.is_file():
                a = read_json(apath)
                ensure(a["owner_qrt_acceptance"] == "PENDING" and
                       a["semantic_review"] == "HOLD_REVIEW_REQUIRED",
                       "P5_BROWSER_NOT_OWNER_ACCEPTANCE", cid)
                browser_refs.append({
                    "name": "SCOPED_CHROMIUM_SENTINELS_NOT_ACADEMIC_ACCEPTANCE",
                    "sha256": sha256(apath),
                    "known_finding_ids":
                        a["whole_journey_W"]["known_finding_ids"],
                    "observed_paths":
                        a["whole_journey_W"]["paths_checked"],
                    "actual_end_to_end_navigation": False,
                })
            navpath = evidence_dir / (slug + "-real-navigation.json")
            if navpath.is_file():
                nav = read_json(navpath)
                ensure(nav.get("cell_id") == cid and
                       nav.get("owner_acceptance") is False and
                       nav.get("qualified_semantic_review") == "NOT_RUN" and
                       nav.get("status") == "HOLD_REVIEW_REQUIRED" and
                       len(nav.get("native_role_paths", {})) == 4 and
                       nav.get("clicked_actual_role_transitions") == 10,
                       "P5_REAL_NAV_CANNOT_RECLASSIFY_QRT", cid)
                browser_refs.append({
                    "name": "TEN_ACTUAL_NATIVE_SHELL_CLICKS_NOT_CONTEXTUAL_QRT_APPROVAL",
                    "sha256": sha256(navpath),
                    "clicked_actual_native_role_paths":
                        list(nav["native_role_paths"]),
                    "observed_integrity_gaps":
                        nav["observed_integrity_gaps"],
                    "assisted_return_verified": (
                        not nav["observed_integrity_gaps"] and
                        nav["assisted_return"]["return_state_assisted"] and
                        nav["assisted_return"]["source_attempt_restored"]
                    ),
                    "learner_independence_established": False
                })
            for rid in REVIEWS:
                r = evidence["semantic_objectives"][rid]
                ensure(r["verdict"] == "NOT_RUN" and not r["evidence"],
                       "P5_TWELVE_OBJECTIVES_NOT_REVIEWED", f"{cid}:{rid}")
                reviews.append({"id": rid, "objective": r["objective"],
                                "question": r["question"],
                                "verdict": "NOT_RUN",
                                "qualified_reviewer_rationale": None,
                                "source_and_role_evidence": [],
                                "justified_na": None})
        else:
            ensure(w.get("expected_source_hold_code") == actual_block or
                   (cid in ("QRT-MODEL-D1","QRT-SYNTHESIZE-D1")
                    and actual_block == "RIVAL_NOT_GROUNDED_IN_SOURCE"),
                   "P5_UNEXPECTED_AUTHOR_RIVAL_BLOCK", cid)
            ensure(canonical_template["review"].keys() == set(REVIEWS),
                   "P5_CANONICAL_REVIEWS_MISSING", cid)
            for rid in REVIEWS:
                objective = canonical_template["review"][rid]
                reviews.append({
                    "id": rid, "objective": objective["objective"],
                    "question": objective["question"], "verdict": "NOT_RUN",
                    "qualified_reviewer_rationale": None,
                    "source_and_role_evidence": [],
                    "justified_na": None
                })
        assert len(reviews) == 12
        assert all(x["verdict"] == "NOT_RUN" for x in reviews)
        issue = row["independent_reviewer_nomination_issue"]
        result.append({
            "cell_id": cid,
            "source": {
                "author_commit": row["source"]["commit"],
                "source_path": row["source"]["path"],
                "source_git_blob": row["source"]["git_blob_sha"],
                "manifest_path": row["manifest"]["path"],
                "manifest_git_blob": row["manifest"]["git_blob_sha"],
                "track": "AUTHORED_TEST_ONLY",
                "source_revision_authority": "SOURCE_AUTHOR_PLUS_REVIEWER",
            },
            "contract_report_sha256": actual_digest,
            "contract_status": evidence["technical_contract"],
            "blocking_source_author_action": (
                {"code": actual_block,
                 "required": ("Source author must create a reviewed new authored "
                              "source revision with a canonical rival demand, "
                              "then repin only after independent comparison.")
                } if blocked else None
            ),
            "qrt_hypothesis_not_a_verdict": {
                "primary_demand": row["demand"],
                "strongest_rival": w["strongest_rival"],
                "difficulty_band": row["band"],
                "protected_W": w["question_specific_W"],
                "Y_knowledge_basis": w.get("Y_evidence_status", "UNKNOWN"),
                "learner_success_hypothesis": w["success_evidence"],
                "falsifier_to_challenge": w["falsifier"],
                "primary_question_id": w["primary_question_id"],
                "primary_crux_move_ref": w["primary_crux_move_ref"],
                "primary_source_crux": primary_route,
                "transfer_question_id": w["transfer_question_id"],
                "transfer_crux_move_ref": w["transfer_crux_move_ref"],
                "transfer_source_crux": transfer_route,
                "canonical_band_policy": canonical_template["band_policy"],
            },
            "five_native_roles": native_refs or {
                role: {"blueprint": BP[role],
                       "semantic": "NOT_RUN",
                       "native_r8_structural_witness": "NOT_RUN"}
                for role in ROLES
            },
            "available_scoped_browser_proof": browser_refs,
            "twelve_separate_hspm_objectives": reviews,
            "qualified_independent_reviewer": {
                "nomination_issue": issue,
                "reviewer_identity": None,
                "qualification_evidence": None,
                "reviewer_conflict_disclosure": None,
                "source_checked_git_blobs": [],
                "written_findings": {field: None for field in REVIEW_FIELDS},
                "alternative_primary_demand": None,
                "alternative_band": None,
                "rival_discrimination_probes": [],
                "independent_math_oracle": None,
                "observed_learners_or_relevant_Y_evidence": None,
                "decision": None,
                "permitted_decisions": list(REVIEW_VERDICTS),
                "signed_verdict_id": None,
                "signed_at": None,
                "state": "NOT_NOMINATED_OR_NOT_SIGNED",
            },
            "owner_separate_disposition": {
                "owner_identity": None,
                "decision": None,
                "qualified_reviewer_verdict_prerequisite": True,
                "accepted_evidence_hash": None,
                "signed_at": None,
                "state": "PENDING_QUALIFIED_REVIEW",
                "permission_to_publish": False,
            },
            "unresolved_learner_journey": {
                "live_six_core_source": "TRACK_B_NOT_ADMITTED",
                "core1a_assisted_return_is_independent": False,
                "complete_real_browser_navigation_path": (
                    "NATIVE_SHELL_PATHS_CLICKED_CONTEXTUAL_ASSISTED_RETURN_HOLD"
                    if any(x["name"] ==
                           "TEN_ACTUAL_NATIVE_SHELL_CLICKS_NOT_CONTEXTUAL_QRT_APPROVAL"
                           for x in browser_refs) else "NOT_RUN"
                ),
                "semantic_human_role_review": "NOT_RUN",
            },
            "release": "HOLD",
        })
    validated = sum(x["contract_status"] == "VALIDATED_PROPOSAL"
                    for x in result)
    blocked = sum(x["contract_status"] == "BLOCKED_RIVAL_REVIEW"
                  for x in result)
    ensure((validated, blocked) == (21, 7),
           "P5_WRONG_QRT_DISPOSITION_COUNTS", repr((validated, blocked)))
    ensure(sum(x["qualified_independent_reviewer"]["decision"] is not None
               for x in result) == 0 and
           sum(x["owner_separate_disposition"]["decision"] is not None
               for x in result) == 0,
           "P5_NO_FABRICATED_APPROVALS")
    return {
        "schema": "imo182-qrt-independent-review-handoff/v1",
        "track": "TRACK_A_AUTHOR_TEST_28_CELLS_ONLY",
        "cells": result,
        "counts": {
            "source_bound_validated_proposals": validated,
            "source_rival_blocked": blocked,
            "role_structural_witnesses": validated * 5,
            "twelve_objective_records": len(result) * 12,
            "qualified_signed_verdicts": 0,
            "owner_acceptances": 0,
        },
        "claims_not_made": [
            "No QRT primary/band academic accuracy certified by this compiler",
            "No independent qualified academic/Owner signature exists",
            "No mathematical solution from source independently re-proved in P5",
            "No semantic cross-Core W preservation claimed by native structure",
            "No rights admission or original IMO Core2 release",
        ],
        "release": "HOLD"
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--authority-root", type=Path, default=Path("."))
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--witness-bank", type=Path, required=True)
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    _, templates, _ = canonical(args.authority_root)
    packet = make_packet(
        read_json(args.ledger), read_json(args.witness_bank),
        args.evidence_dir, read_json(args.coverage), templates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("P5 review handoff: 28 source-bound evidence packets, 336 distinct HSPM "
          "checks NOT_RUN; 21 proposed, seven source-author rival holds, "
          "0 qualified reviewer and 0 Owner verdicts, release HOLD")


if __name__ == "__main__":
    main()
