#!/usr/bin/env python3
"""Issue #182: 17 question-specific narrow precommit W-disclosure sentinels.

These are ONE-WAY falsifiers, not semantic validators. Source and transfer
contracts remain hypotheses. A detected complete answer/warrant before learner
commitment requires academic review. A detector miss is NOT an accept verdict.

Fragments match *together within one captured exposure surface*; incomplete
isolated mathematical concepts are negative decoys. Mutation tests inject
complete protected answers into an accessible SVG description (not HTML/source)
and assert the same detection path rejects them.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from qrt_intent_contract import ensure

@dataclass(frozen=True)
class Sentinel:
    code: str
    clauses: tuple[str, ...]
    bad_disclosure: str
    partial_decoy: str

# Every rule has an actual source-specific W target, not a generic
# formula/punctuation rule. Avoid using a question stem alone to infer
# cognition or assigning any academic MATCH outcome.
SENTINELS: dict[str, Sentinel] = {
    "QRT-JUSTIFY-D1": Sentinel(
        "JUSTIFY_D1_EQUAL_AREA_WARRANT_AND_VALUE_PREATTEMPT",
        (r"\b42\s*cm", r"\b(?:equal|same)\s+areas?\b",
         r"\bperpendicular\b"),
        "Both triangles have equal areas of 42 cm² because their perpendicular heights match despite sideways peaks.",
        "The triangles share a base; consider a perpendicular height."
    ),
    "QRT-RETRIEVE-D3": Sentinel(
        "RETRIEVE_D3_RHOMBUS_EXCLUSION_CLASSIFICATION_PREATTEMPT",
        (r"\brhombus\b", r"\bnot\s+(?:a\s+)?square\b",
         r"\bdiagonal.{0,75}\b8\b.{0,35}\b6\b"),
        "The correct class is rhombus, not a square: diagonal lengths are 8 and 6, while both midpoints coincide and diagonals are perpendicular.",
        "Check both diagonal midpoints and recall quadrilateral categories."
    ),
    "QRT-MODEL-D3": Sentinel(
        "MODEL_D3_COMPLETE_POWER_SUBSTITUTION_PREATTEMPT",
        (r"4\s*t\s*=\s*t\s*\+\s*192", r"\bt\s*=\s*64\b",
         r"\bu\s*=\s*3\s*/\s*2\b"),
        "Set t=16^u. Then 4t=t+192, so t=64 and u=3/2; both original sides equal 256.",
        "Powers with a shared base can sometimes be represented by one variable."
    ),
    "QRT-EXPLAIN-D2": Sentinel(
        "EXPLAIN_D2_EXTRA_FACTOR_AND_ADDITIVE_COUNTEREXAMPLE_PREATTEMPT",
        (r"\bone\s+extra\s+(?:copy|factor)\s+of\s+3\b",
         r"\bt\s*=\s*1\b", r"\b9\b.{0,70}\b6\b"),
        "The exponent t+1 means one extra factor of 3, not addition; at t=1 the two outcomes are 9 and 6.",
        "An exponent counts factors, not additions."
    ),
    "QRT-APPLY-D2": Sentinel(
        "APPLY_D2_SEQUENTIAL_DISCOUNT_FINAL_AND_NET_PREATTEMPT",
        (r"\b720\b", r"\b648\b", r"\b32(?:\.5|½)\s*%"),
        "After the first discount the base is 720; the updated-base final price is 648; the equivalent original-base discount is 32.5%.",
        "A second percentage should use the updated price."
    ),
    "QRT-SYNTHESIZE-D2": Sentinel(
        "SYNTHESIZE_D2_MAXIMAL_CODE_AND_EXCLUSION_PREATTEMPT",
        (r"\b452\b", r"\b(?:digit\s+)?sum\s*(?:is|=|of)\s*11\b",
         r"\b432\b"),
        "Reject 452 because its digit sum is 11; 432 meets both rules and is the largest possible code.",
        "A valid multiple of six has an even last digit and digit sum divisible by three."
    ),
    "QRT-JUSTIFY-D2": Sentinel(
        "JUSTIFY_D2_COMPLETE_COPRIME_FACTOR_WARRANT_PREATTEMPT",
        (r"\b(?:factor|divisor)\s+of\s+2\b",
         r"\b(?:factor|divisor)\s+of\s+3\b",
         r"\bcoprime\b"),
        "Three consecutive factors always contain a factor of 2 and a factor of 3; since these guarantees are coprime their product is divisible by six.",
        "Three successive integers have distinct residues modulo three."
    ),
    "QRT-APPLY-D3": Sentinel(
        "APPLY_D3_COMPLETE_VALUATION_VECTOR_AND_MINIMUM_PREATTEMPT",
        (r"\bv2\s*=\s*2\b", r"\bv3\s*=\s*1\b",
         r"\bv5\s*=\s*1\b", r"\bn\s*=\s*60\b"),
        "The minimum exponent vector is v2=2, v3=1, v5=1; hence the least possible n=60.",
        "For prime-power divisibility in n², consider integer exponent ceilings."
    ),
    "QRT-REPRESENT-D3": Sentinel(
        "REPRESENT_D3_FULL_OVERLAP_CORRECTION_PREATTEMPT",
        (r"\b70\s*[-−]\s*30\s*[-−]\s*30\s*\+\s*9\s*=\s*19\b",
         r"\b(?:overlap|both)\b"),
        "The routes through both points overlap, so 70-30-30+9=19 avoiding both.",
        "Paths through both marked vertices might overlap."
    ),
    "QRT-SYNTHESIZE-D3": Sentinel(
        "SYNTHESIZE_D3_EXHAUSTIVE_MIDDLE_DIGIT_COUNTS_PREATTEMPT",
        (r"\bt\s*=\s*3\b", r"\bt\s*=\s*6\b", r"\bt\s*=\s*9\b",
         r"\b14\b"),
        "For middle digit T=3 there are 6 cases, T=6 gives 7, and T=9 gives 1; the exhaustive total is 14.",
        "The digit sum of an arithmetic progression is three times its middle digit."
    ),
    "QRT-JUSTIFY-D3": Sentinel(
        "JUSTIFY_D3_MOD_FOUR_EXACT_IFF_PREATTEMPT",
        (r"\b(?:iff|if and only if)\b",
         r"\bn\s*(?:mod|modulo)\s*4\b",
         r"\b0\s*,\s*2\s*,\s*3\b"),
        "12 divides the consecutive product iff n mod 4 lies in 0,2,3; the residue 1 is excluded.",
        "Every three consecutive integers contain a multiple of three."
    ),
    "QRT-EXPLAIN-D4": Sentinel(
        "EXPLAIN_D4_EVEN_ODD_ROTATION_CAUSE_PREATTEMPT",
        (r"\beven\s+(?:original\s+)?(?:length|l)\b",
         r"\br\s*[≡=]\s*[-−]\s*n\b",
         r"\bodd\s+(?:original\s+)?(?:length|l)\b",
         r"\b2\s*a\b"),
        "For even length L, R≡-N mod11; for odd length L, R≡2a mod11 and cannot stay divisible by eleven.",
        "Moving the first digit changes its base-ten place weight."
    ),
    "QRT-APPLY-D4": Sentinel(
        "APPLY_D4_FULL_COMPATIBILITY_CLASS_AND_SLOTS_PREATTEMPT",
        (r"\bgcd\s*\(\s*36\s*,\s*20\s*\)\s*=\s*4\b",
         r"\bx\s*[≡=]\s*29\s*(?:mod(?:ulo)?\s*180|\+\s*180)",
         r"\b209\s*,\s*389\s*,\s*569\b"),
        "gcd(36,20)=4 confirms compatibility; x=29+180j gives eligible slots 209,389,569.",
        "For noncoprime moduli, test gcd compatibility before combining."
    ),
    "QRT-MODEL-D4": Sentinel(
        "MODEL_D4_COURTYARD_EXCLUSION_MODEL_PREATTEMPT",
        (r"\b4\s*n\s*[-−]\s*2\s*e\s*[-−]\s*c\b",
         r"\bc\s*=\s*8\b", r"\b(?:a\s*=\s*)?16\b"),
        "The exterior-accessible model is A=4n-2e-c, with c=8 inaccessible inner edges, giving A=16 chair sites.",
        "Outside-accessible chair sites are different from all unshared boundaries."
    ),
    "QRT-REPRESENT-D4": Sentinel(
        "REPRESENT_D4_LOCAL_THREE_VS_TWO_HALL_OBSTRUCTION_PREATTEMPT",
        (r"\b3\s+(?:black\s+)?(?:cells|vertices|squares)\b",
         r"\b2\s+(?:white\s+)?neighbors?\b",
         r"\b(?:no\s+(?:complete\s+)?tiling|impossible\s+to\s+tile)\b"),
        "Three black cells have only two white neighbors, so no complete tiling is possible for this specific board.",
        "Equal numbers of black and white squares are necessary but not sufficient."
    ),
    "QRT-SYNTHESIZE-D4": Sentinel(
        "SYNTHESIZE_D4_MINIMUM_PREFIX_COMPLETENESS_PREATTEMPT",
        (r"\b120384\b", r"\bprefix\s*10\b",
         r"\b(?:odd[- ]position|alternating)[^.\n]{0,85}\b9\b"),
        "The minimum is 120384: prefix 10 cannot work, and the odd-position digit sum must equal 9.",
        "Divisibility by eleven imposes an alternating-position constraint."
    ),
    "QRT-JUSTIFY-D4": Sentinel(
        "JUSTIFY_D4_EXACT_MOD_SIX_IFF_PREATTEMPT",
        (r"\b(?:iff|if and only if)\b",
         r"\bn\s*[≡=]\s*(?:1\s*(?:or|,)\s*5|1\s*,\s*5)\s*(?:mod|modulo)\s*6\b",
         r"\b(?:odd|even)\b",
         r"\b(?:not\s+divisible\s+by\s*3|3\s*(?:does\s+not\s+divide|∤))\b"),
        "24 divides n²−1 iff n≡1 or 5 mod6, because n must be odd and not divisible by 3.",
        "The difference of two squares factors as (n−1)(n+1)."
    ),
}


def visible_surfaces(state: dict[str, Any]) -> dict[str, list[str]]:
    # One surface/paragraph, not concatenating unrelated role/page data.
    return {
        key: [line.strip() for line in str(state.get(key, "")).splitlines()
              if line.strip()]
        for key in ("visible", "h2_visible", "accessible_svg",
                    "semantic_labels", "stem")
    }


def detect(cell: str, state: dict[str, Any]) -> list[dict[str, str]]:
    ensure(cell in SENTINELS, "SEMANTIC_SENTINEL_NOT_AUTHORED", cell)
    rule = SENTINELS[cell]
    results = []
    for surface, lines in visible_surfaces(state).items():
        for line in lines:
            normalized = re.sub(r"\s+", " ", line)
            if all(re.search(pattern, normalized, flags=re.IGNORECASE)
                   for pattern in rule.clauses):
                results.append({
                    "finding": rule.code,
                    "surface": surface,
                    # Deliberately do not duplicate copyrighted source text.
                    "source_bound_detection": "NARROW_COMPLETE_W_ANSWER_WARRANT",
                    "academic_validation": "REVIEW_REQUIRED",
                })
                break
    return results


def self_tests() -> dict:
    ensure(len(SENTINELS) == 17, "SEVENTEEN_SPECIFIC_RULES_REQUIRED")
    codes = [s.code for s in SENTINELS.values()]
    ensure(len(set(codes)) == len(codes), "DUPLICATE_SEMANTIC_SENTINEL_CODE")
    for cell, rule in SENTINELS.items():
        ensure(len(rule.clauses) >= 3 and
               len(rule.bad_disclosure) > 35 and
               len(rule.partial_decoy) > 22,
               "INCOMPLETE_SOURCE_W_SENTINEL", cell)
        good = detect(cell, {"accessible_svg": rule.bad_disclosure})
        ensure(len(good) == 1 and good[0]["finding"] == rule.code and
               good[0]["surface"] == "accessible_svg",
               "SEMANTIC_BAD_MUTATION_ESCAPED", cell)
        for carrier in ("visible","h2_visible","semantic_labels","stem"):
            res = detect(cell, {carrier:rule.bad_disclosure})
            ensure(len(res) == 1 and res[0]["finding"] == rule.code,
                   "SEMANTIC_DISCLOSURE_CARRIER_ESCAPED", cell+":"+carrier)
        ensure(not detect(cell, {"accessible_svg":rule.partial_decoy}),
               "PARTIAL_PRIOR_CONCEPT_FALSE_FLAGGED", cell)
        # A separate role or separate accessible line is not a complete
        # single-surface warrant: disjoint concepts must not be assembled into
        # an invented leak by concatenation.
        ensure(not detect(cell, {"visible":rule.partial_decoy,
                                 "semantic_labels":rule.partial_decoy}),
               "SEMANTIC_CROSS_SURFACE_FALSE_POSITIVE", cell)
    return {"specific_rules":len(SENTINELS),
            "bad_carrier_mutations_rejected":len(SENTINELS)*5,
            "partial_and_split_decoys_passed":len(SENTINELS)*2,
            "semantic_academic_verdicts":0,
            "caveat":"Known exact-answer falsifiers only; not paraphrase coverage"}


if __name__ == "__main__":
    import json
    print(json.dumps(self_tests(),sort_keys=True))
