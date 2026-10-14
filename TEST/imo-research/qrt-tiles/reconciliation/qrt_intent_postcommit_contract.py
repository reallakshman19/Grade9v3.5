#!/usr/bin/env python3
"""IMO #182 R12: pure evidence contract, not an academic or renderer validator.

The R11 native browser recorder and R8 P5 reviewer handoff share these
technical field definitions. No HTML is rendered, no reviewer is appointed,
and no QRT cell is accepted here.
"""
from __future__ import annotations

from qrt_intent_contract import ensure

POSTCOMMIT_CHECKS = {
    "attempt_blank_rejected": "NAV_POSTCOMMIT_BLANK_UNLOCKED",
    "nonempty_attempt_committed": "NAV_POSTCOMMIT_VALID_ATTEMPT_NOT_COMMITTED",
    "precommit_solution_locked": "NAV_POSTCOMMIT_PREATTEMPT_SOLUTION_LEAK",
    "postcommit_context_link_present": "NAV_POSTCOMMIT_CONTEXT_LINK_MISSING",
    "context_link_is_pinned": "NAV_POSTCOMMIT_CONTEXT_WRONG_CONCEPT",
    "concept_reached": "NAV_POSTCOMMIT_CONCEPT_NOT_REACHED",
    "concept_is_pinned": "NAV_POSTCOMMIT_CONCEPT_ID_DRIFT",
    "return_link_present": "NAV_POSTCOMMIT_RETURN_LINK_MISSING",
    "return_link_is_pinned": "NAV_POSTCOMMIT_RETURN_WRONG_QUESTION",
    "same_question_reached": "NAV_POSTCOMMIT_SOURCE_QUESTION_LOST",
    "attempt_text_restored": "NAV_POSTCOMMIT_SOURCE_DRAFT_NOT_RESTORED",
    "assistance_marked": "NAV_POSTCOMMIT_ASSISTANCE_UNMARKED",
}


def classify_postcommit_journey(probe: dict) -> list[str]:
    """One-way fail-closed technical negatives, never mathematical mastery."""
    findings = [code for field, code in POSTCOMMIT_CHECKS.items()
                if probe.get(field) is not True]
    if probe.get("independent_credit_claimed") is True:
        findings.append("NAV_POSTCOMMIT_FALSE_INDEPENDENT_CREDIT")
    return findings


def verify_native_postcommit_handoff(nav: dict, question_id: str,
                                     concept_id: str) -> dict:
    """Reject forged or stale browser evidence before the P5 reviewer packet.

    This validates the *reported* browser probe against its own source-pinned
    identities and claim boundary. It does not independently re-run Chromium.
    """
    report = nav.get("postcommit_native_journey")
    ensure(isinstance(report, dict) and
           report.get("schema") == "imo182-r11-native-postcommit-technical-probe/v1",
           "P5_R11_NATIVE_POSTCOMMIT_EVIDENCE_REQUIRED")
    ensure(nav.get("schema") == "imo182-r8-real-native-navigation/v1" and
           nav.get("assisted_return", {}).get("primary_question_id") == question_id and
           nav.get("assisted_return", {}).get("target_identity_expected_concept") == concept_id and
           report.get("source_question_id") == question_id and
           report.get("selected_concept_id") == concept_id,
           "P5_R11_NATIVE_SOURCE_IDENTITY_DRIFT")
    ensure(report.get("native_renderer_only") is True and
           report.get("source_bytes_changed") is False and
           report.get("meaningful_mathematical_answer_submitted") is False and
           report.get("human_academic_evidence") is False and
           report.get("release") == "HOLD" and
           nav.get("qualified_semantic_review") == "NOT_RUN" and
           nav.get("owner_acceptance") is False,
           "P5_R11_NATIVE_CLAIM_BOUNDARY_VIOLATED")
    observed = report.get("observed")
    expected_fields = set(POSTCOMMIT_CHECKS) | {"independent_credit_claimed"}
    ensure(isinstance(observed, dict) and
           set(observed) == expected_fields and
           all(type(observed[k]) is bool for k in expected_fields),
           "P5_R11_NATIVE_STATUS_SCHEMA_DRIFT")
    actual = classify_postcommit_journey(observed)
    ensure(report.get("findings") == actual and
           type(report.get("technical_round_trip_complete")) is bool and
           report["technical_round_trip_complete"] == (not actual),
           "P5_R11_NATIVE_FINDINGS_OR_STATUS_FORGED")
    # Never manufacture a successful postcommit path from old *precommit*
    # navigation flags, and never treat shell fallback as assistance.
    prior = nav.get("assisted_return", {})
    ensure(prior.get("target_identity_proven") is False or (
           prior.get("return_link_at_concept") is True and
           prior.get("context_link_at_source") is True and
           not prior.get("target_identity_findings") and
           not nav.get("target_identity_findings") and
           prior.get("return_state_assisted") is True and
           prior.get("source_attempt_restored") is True),
           "P5_R11_NATIVE_PRECOMMIT_TARGET_STATUS_FORGED")
    return {
        "name": "REAL_NATIVE_POSTCOMMIT_SAME_QUESTION_DIAGNOSTIC",
        "technical_state": ("ROUNDTRIP_TECHNICALLY_COMPLETE_NOT_QRT_APPROVED"
                            if not actual else "NATIVE_ROUNDTRIP_DEFECTS_OBSERVED"),
        "native_question_id": question_id,
        "selected_concept_id": concept_id,
        "distinct_technical_findings": list(actual),
        "technical_round_trip_complete": not actual,
        "manual_shell_fallback_is_not_assisted_navigation": True,
        "native_renderer_only": True,
        "separate_held_copy_not_authoritative": True,
        "academic_approved": False,
        "owner_approved": False,
        "release": "HOLD",
    }
