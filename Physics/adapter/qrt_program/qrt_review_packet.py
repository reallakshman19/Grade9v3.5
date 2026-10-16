"""Reproducible Physics candidate-model review packet (NO academic approval).

The packet is a source-first review *request*: it provides precise question
identity, original authored claims, independent bounded recomputation, and
failure falsifiers. It never promotes candidate arithmetic to academic truth,
rewrites canonical content, or decides school/rights/release status.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from Physics.adapter.qrt_program.qrt_crosswalk import inspect_question
from Physics.adapter.qrt_program.qrt_oracle_candidates import (
    angled_static_friction_threshold,
    ideal_horizontal_launch,
    signed_quadrant_ii_components,
    vertical_magnet_force_balance,
)
from tools.physics_qrt_program.bootstrap import assemble, ROOT


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def recompute_packet_sha256(packet: dict) -> str:
    """Digest supplied packet content excluding its self-referential digest.

    A matching digest does not authenticate the sender or qualified reviewer.
    """
    if not isinstance(packet, dict):
        raise ValueError("PACKET_MUST_BE_OBJECT")
    return _canonical_digest({key: value for key, value in packet.items()
                              if key != "packet_sha256"})


# This is a fixed, bounded, non-authoritative test scenario registry.
# The evaluator must not claim the authored question is valid merely
# because these cases produce numerically plausible results.
SCENARIOS = {
    "Q-PHY-VEC-DECOMP-2A-QUADRANT-II-03": {
        "model": "SIGNED_VECTOR_COMPONENTS_QUADRANT_II",
        "assumptions": ["15-unit vector measured 40 degrees above negative x",
                        "positive x right; positive y up"],
        "inputs": {"magnitude": 15, "degrees_above_negative_x": 40},
        "claims_to_challenge": ["Correct nonnegative magnitude is insufficient",
                               "x negative, y positive",
                               "angle reference is negative x, not positive x"],
        "wrong_result_controls": ["flip the sign of x but preserve vector magnitude",
                                  "use sine for x when angle is measured from negative x"],
        "scientific_model_limits": ["Angles outside 0–90 degrees are outside this bounded quadrant-II adapter"],
    },
    "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04": {
        "model": "IDEAL_HORIZONTAL_PROJECTILE",
        "assumptions": ["g constant downward", "air resistance neglected",
                        "launch uy=0", "x and y share one time coordinate"],
        "inputs": {"ux": 15, "height": 20, "g": 10},
        "claims_to_challenge": ["t computed from vertical drop only",
                               "same t applied to horizontal displacement",
                               "impact vertical velocity negative for positive y upward"],
        "wrong_result_controls": ["use t=1 s in horizontal x only",
                                  "use vy=+20 m/s at impact",
                                  "apply an arbitrary horizontal acceleration"],
        "scientific_model_limits": ["Drag and variable-g fields are not modeled"],
    },
    "Q-PHY-NLM-2A-COV-03": {
        "model": "RESTING_MAGNET_FREE_BODY_DIAGRAM",
        "assumptions": ["magnet at rest on vertical door",
                        "magnetic pull horizontal 3 N",
                        "magnet mass 0.1 kg, g=10 m/s^2"],
        "inputs": {"mass": 0.1, "g": 10, "magnetic_pull": 3},
        "claims_to_challenge": ["four external forces ON magnet",
                               "weight and static friction sum to zero",
                               "magnetic and normal forces sum to zero",
                               "third-law partner of each acts on another body"],
        "wrong_result_controls": ["show third-law pair on same magnet diagram",
                                  "omit static friction",
                                  "treat horizontal magnetic pull as friction"],
        "scientific_model_limits": ["No maximum static-friction coefficient supplied: actual at-rest state is source premise"],
    },
    "Q-PHY-NLM-2B-FRICTION-STATE-01": {
        "model": "IMPENDING_SLIP_THRESHOLD_VARIABLE_NORMAL",
        "assumptions": ["mass 10 kg; g=10 m/s^2; mu_s=0.75",
                        "surface horizontal", "normal reaction N remains positive",
                        "upward rope force changes N; impending slide at limiting friction"],
        "inputs": {"mass": 10, "g": 10, "mu_s": 0.75},
        "angles_cos_sin": [
            {"label": "horizontal", "cosine": 1, "sine": 0},
            {"label": "37deg", "cosine": 0.8, "sine": 0.6},
            {"label": "53deg", "cosine": 0.6, "sine": 0.8}
        ],
        "claims_to_challenge": ["normal N=mg-P sin(theta), not constant mg",
                               "threshold P cos(theta)=mu_s N",
                               "worker limit of 61 N allows only 37 degree choice"],
        "wrong_result_controls": ["fix N=mg at tilted pull",
                                  "declare the steepest pull automatically best",
                                  "ignore loss of horizontal projection"],
        "scientific_model_limits": ["Contact and static-friction conditions required",
                                    "Supplied trigonometric approximations define 37/53 calculations"],
    },
}


def candidate_prediction(question_id: str) -> dict:
    s = SCENARIOS.get(question_id)
    if s is None:
        raise ValueError(f"UNSELECTED_SCIENTIFIC_SCENARIO:{question_id}")
    model = s["model"]
    if model == "SIGNED_VECTOR_COMPONENTS_QUADRANT_II":
        return signed_quadrant_ii_components(**s["inputs"])
    if model == "IDEAL_HORIZONTAL_PROJECTILE":
        return ideal_horizontal_launch(**s["inputs"])
    if model == "RESTING_MAGNET_FREE_BODY_DIAGRAM":
        result = vertical_magnet_force_balance(**s["inputs"])
        result["partner_bodies"] = sorted(result["partner_bodies"])
        return result
    if model == "IMPENDING_SLIP_THRESHOLD_VARIABLE_NORMAL":
        runs = {}
        for a in s["angles_cos_sin"]:
            runs[a["label"]] = angled_static_friction_threshold(
                **s["inputs"], cosine=a["cosine"], sine=a["sine"])
        runs["worker_limit_newtons"] = 61
        runs["can_start"] = {key: value["minimum_pull"] <= 61
                             for key, value in runs.items() if isinstance(value, dict)}
        return runs
    raise ValueError(f"MODEL_NOT_SUPPORTED:{model}")


def make_packet(*, root: Path = ROOT, candidates: dict | None = None,
                draft_lock: dict | None = None) -> dict:
    wave0 = assemble(root=root, candidates=candidates, draft_lock=draft_lock)
    findings = []
    for case in wave0["cases"]:
        question_id = case["question_id"]
        source_path = case["source_sha256"]
        package = next(w for w in wave0["lock"]["witnesses"]
                       if w["question_id"] == question_id)["source_path"]
        raw = (root / package).read_bytes()
        source = json.loads(raw)
        questions = [q for q in source.get("questions", [])
                     if isinstance(q, dict) and q.get("id") == question_id]
        if len(questions) != 1:
            raise ValueError(f"QUESTION_ID_NOT_UNIQUE:{question_id}")
        question = questions[0]
        # Source-binding is rechecked here; never trust duplicated fixture prose.
        detail = inspect_question(package, question_id, root=root)
        if detail["package_sha256"] != source_path:
            raise ValueError(f"SOURCE_CHANGED_DURING_PACKET:{question_id}")
        scenario = SCENARIOS[question_id]
        findings.append({
            "question_id": question_id,
            "source_package": package,
            "source_sha256": source_path,
            "question_sha256": _canonical_digest(question),
            "primary_capability_ref": detail["primary_capability_ref"],
            "core_exposure": detail["declared_cores"],
            "origin": detail["source_class"],
            "authored_question_stem": question.get("stem"),
            "authored_conditions": question.get("conditions", []),
            "authored_answer_claim": (question.get("answer") or {}).get("summary"),
            "proposed_physics_model": scenario["model"],
            "proposed_assumptions": scenario["assumptions"],
            "bounded_model_inputs": scenario["inputs"],
            "candidate_recomputed_prediction": candidate_prediction(question_id),
            "required_model_falsifiers": scenario["wrong_result_controls"],
            "model_limitations": scenario["scientific_model_limits"],
            "reviewer_questions": scenario["claims_to_challenge"],
            "scientific_approval": "NOT_OBTAINED",
            "item_correctness": "REVIEW_REQUIRED",
            "requested_reviewer_outcome": "ACCEPT / REVISE / REJECT with reasons and exact source digest",
        })
    result = {
        "schema": "physics-qrt.science-review-request/v1",
        "programme": wave0["lock"]["programme"],
        "base_sha": wave0["lock"]["base_sha"],
        "status": "PENDING_INDEPENDENT_PHYSICS_REVIEW",
        "packet_digest_kind": "CANONICAL_JSON_SHA256",
        "question_count": len(findings),
        "questions": findings,
        "source_authority": "AUTHOR_CREATED_CANDIDATE",
        "school_scope_authority": "NOT_ESTABLISHED_FOR_MICRO_DEMAND",
        "reviewer_identity": "UNASSIGNED",
        "review_verdict": "NOT_REVIEWED",
        "canonical_qrt_demand": "NOT_RUN",
        "rendered_product_proof": "NOT_RUN",
        "permission_to_write": False,
        "release_verdict": "HOLD",
    }
    result["packet_sha256"] = recompute_packet_sha256(result)
    return result



def make_independent_intake(*, root: Path = ROOT,
                            candidates: dict | None = None,
                            draft_lock: dict | None = None) -> dict:
    """Source-bound stem-only brief, without author's answers or model proposals.

    An actual independent reviewer must freeze their own derivation before
    seeing the full comparison packet. This formatting alone does not prove
    reviewer independence or scientific competency.
    """
    complete = make_packet(root=root, candidates=candidates, draft_lock=draft_lock)
    fields = (
        "question_id", "source_package", "source_sha256", "question_sha256",
        "primary_capability_ref", "core_exposure", "authored_question_stem",
        "authored_conditions"
    )
    intake = {
        "schema": "physics-qrt.independent-derivation-intake/v1",
        "programme": complete["programme"],
        "base_sha": complete["base_sha"],
        "full_comparison_packet_sha256": complete["packet_sha256"],
        "status": "DERIVATION_REQUEST_UNASSIGNED",
        "questions": [{key: item[key] for key in fields} for item in complete["questions"]],
        "protocol": ("Solve the stems and conditions independently and freeze your "
                     "own derivations before seeing the authors' answers, our candidate "
                     "computations or seeded falsifiers. Then compare and explain any "
                     "differences. Opening canonical JSON containing authored answers "
                     "breaks answer-withheld independence and must be disclosed."),
        "qualified_reviewer": "NOT_ASSIGNED",
        "scientific_verdict": "NOT_REVIEWED",
        "owner_authorization": False,
        "release_verdict": "HOLD",
    }
    intake["intake_sha256"] = _canonical_digest(intake)
    return intake


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blind-intake", action="store_true",
                        help="Withhold authored answers and candidate scientific calculations")
    parser.add_argument("--check-only", action="store_true",
                        help="Print digest/status only; no changes to sources or repo")
    args = parser.parse_args()
    packet = make_independent_intake() if args.blind_intake else make_packet()
    output = {"status": packet["status"], "question_count": len(packet["questions"]),
              "packet_sha256": packet.get("packet_sha256", packet.get("intake_sha256")),
              "permission_to_write": False}
    if not args.check_only:
        output = packet
    print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
