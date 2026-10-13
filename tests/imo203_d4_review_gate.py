"""Fail-closed, source-safe #203 review transition checks.

This validates evidence SHAPE, never reviewer expertise, truth of a decision,
mathematical correctness, or Owner authority. It grants no acceptance.
"""
from collections.abc import Mapping

OBJECTIVES = ("H1", "H2", "H3", "S1", "S2", "S3",
              "P1", "P2", "P3", "M1", "M2", "M3")
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
SEMANTIC_VERDICTS = {"MATCH", "CONTEXTUAL_DIFFERENCE", "DEFECT", "JUSTIFIED_NA"}
REVIEW_VERDICTS = {"PASS", "REVISE", "JUSTIFIED_NA"}
ACADEMIC_VERDICTS = {"ACADEMIC_PASS", "REVISIONS_REQUIRED", "ACADEMIC_REJECT"}
EMPTY = {"", "PENDING", "UNKNOWN", "UNASSIGNED", "NOT_RUN"}


def filled(value):
    """Nonempty evidence-bearing value, not a placeholder label."""
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return value.strip().upper() not in EMPTY
    return bool(value)


def promotion_errors(cell, handoff, golden):
    """Return reasons to reject proposed status advancement, without mutation."""
    errors = []
    assessment = cell.get("assessment") or {}
    tokens = {t.strip() for t in cell.get("adoption_status", "").split(";")}
    academic = (bool(tokens & {"ACADEMIC_REVIEWED", "OWNER_QRT_ACCEPTED", "RELEASED"})
                or assessment.get("academic_status") == "ACADEMIC_REVIEWED"
                or handoff.get("academic_verdict") in ACADEMIC_VERDICTS)
    owner = (bool(tokens & {"OWNER_QRT_ACCEPTED", "RELEASED"})
             or assessment.get("accepted") is True
             or handoff.get("accepted") is True
             or filled(assessment.get("owner_qrt_decision_id"))
             or filled(handoff.get("owner_decision_id"))
             or filled(golden.get("owner_qrt_decision_id")))
    if owner:
        academic = True

    if not academic:
        return errors

    profile = cell.get("learner_profile")
    if not isinstance(profile, Mapping):
        errors.append("X/Y/Z/W learner profile missing")
        profile = {}
    for key in ("X", "Y", "Z", "W"):
        item = profile.get(key)
        if not isinstance(item, Mapping) or not filled(item.get("status")):
            errors.append(f"{key} evidence status missing")
        elif not filled(item.get("statement")):
            errors.append(f"{key} explanation missing")
    y = profile.get("Y", {}) if isinstance(profile.get("Y"), Mapping) else {}
    if y.get("status") == "DEMONSTRATED" and not filled(y.get("learner_event_ref")):
        errors.append("Y DEMONSTRATED requires a real learner-event reference")
    elif y.get("status") == "UNKNOWN" and filled(y.get("learner_event_ref")):
        errors.append("Y UNKNOWN contradicts an asserted learner-event reference")
    elif y.get("status") not in ("UNKNOWN", "DEMONSTRATED"):
        errors.append("Y must explicitly be UNKNOWN or evidence-backed DEMONSTRATED")
    w = profile.get("W", {}) if isinstance(profile.get("W"), Mapping) else {}
    if not filled(w.get("move_ref")):
        errors.append("W protected move reference missing")

    if not filled(handoff.get("qualified_reviewer")):
        errors.append("qualified independent reviewer missing")
    if not filled(handoff.get("conflict_declaration")):
        errors.append("reviewer conflict-of-interest declaration missing")
    if handoff.get("academic_verdict") not in ACADEMIC_VERDICTS:
        errors.append("signed academic outcome missing")
    hspm = handoff.get("HSPM_review")
    if not isinstance(hspm, Mapping) or set(hspm) != set(OBJECTIVES):
        errors.append("exactly 12 H/S/P/M review objectives required")
        hspm = {}
    for key in OBJECTIVES:
        review = hspm.get(key, {})
        if not isinstance(review, Mapping):
            review = {}
        if review.get("verdict") not in REVIEW_VERDICTS:
            errors.append(f"{key} substantive verdict missing")
        if not filled(review.get("evidence")):
            errors.append(f"{key} evidence reference missing")
        if not filled(review.get("reviewer")):
            errors.append(f"{key} reviewer attribution missing")

    roles = golden.get("role_specific_semantic_differential")
    if not isinstance(roles, Mapping):
        roles = {}
    for role in ROLES:
        evidence = roles.get(role, {})
        if not isinstance(evidence, Mapping):
            evidence = {}
        if evidence.get("academic_semantics") not in SEMANTIC_VERDICTS:
            errors.append(f"{role} semantic golden verdict missing")
        if not filled(evidence.get("evidence")):
            errors.append(f"{role} semantic golden evidence missing")

    if handoff.get("academic_verdict") == "ACADEMIC_PASS":
        if cell.get("demand") == "RETRIEVE" and y.get("status") != "DEMONSTRATED":
            errors.append("RETRIEVE pass requires proven prior full-theorem mastery")
        if any(isinstance(hspm.get(key), Mapping)
               and hspm[key].get("verdict") == "REVISE" for key in OBJECTIVES):
            errors.append("academic PASS conflicts with H/S/P/M REVISE")

    if owner:
        decision = assessment.get("owner_qrt_decision_id")
        if not filled(decision):
            errors.append("Owner QRT decision ID missing")
        elif decision != handoff.get("owner_decision_id") or decision != golden.get("owner_qrt_decision_id"):
            errors.append("Owner decision ID differs across evidence files")
        if not assessment.get("accepted") or not handoff.get("accepted") or not golden.get("accepted"):
            errors.append("Owner-accepted state differs across evidence files")
        if handoff.get("academic_verdict") != "ACADEMIC_PASS":
            errors.append("Owner acceptance requires an independent academic PASS")
    return errors
