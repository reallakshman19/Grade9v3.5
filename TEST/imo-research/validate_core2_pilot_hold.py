#!/usr/bin/env python3
"""Fail closed on the official SOF sample Q004 visual-sighting pilot.

The research observation does not authenticate a source Core2 product. A future
custody decision needs a separate rights-aware, independently reviewed receipt.
No publisher stem, options, figure, or PDF bytes are stored here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "intake" / "core2-pilot-q004-hold.v1.json"
CENSUS = ROOT / "intake" / "core2-source-custody-eligibility.v1.json"
QID = "SOF-IMO-G09-SAMPLE-2026-27-Q004"
SOURCE_ID = "SOF-IMO-G09-SAMPLE-2026-27"
SOURCE_URL = "https://sofworld.org/download/file/fid/73719"
COMPONENTS = (
    "original_identity", "original_stem", "subparts_conditions",
    "complete_option_order", "source_figures_and_captions",
    "source_hints", "source_answer_rubric",
)
FORBIDDEN_SOURCE_PAYLOAD_FIELDS = {
    "stem", "source_stem", "source_question_text", "options",
    "figure_bytes", "original_pdf_bytes", "source_figure_bytes",
    "source_hints", "publisher_figure", "source_pdf_base64",
}


class PilotHoldError(ValueError):
    """The research-only record is inconsistent or claims unearned authority."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise PilotHoldError(message)


def load(path: Path) -> dict:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PilotHoldError(f"unreadable input {path}: {exc}") from exc
    need(isinstance(obj, dict), "root must be an object")
    return obj


def no_copied_source_payload(obj: object, path: tuple[str, ...] = ()) -> None:
    """Forbid copied publisher bytes/text, while allowing one typed status label."""
    if isinstance(obj, dict):
        prohibited = set(FORBIDDEN_SOURCE_PAYLOAD_FIELDS)
        if path == ("observation", "visual_component_sightings"):
            # This is the *name* of a required nine-part status category, not
            # original stem text or a source choice list. Values are strictly checked below.
            prohibited.difference_update({"stem", "options"})
            need(obj.get("stem") == "SEEN_ON_RENDER_ONLY" and
                 obj.get("options") == "SEEN_ON_RENDER_ONLY",
                 "typed component statuses cannot embed original source wording")
        need(not (set(obj) & prohibited),
             "protected source content field is not allowed in pilot packet")
        for name, child in obj.items():
            no_copied_source_payload(child, path + (name,))
    elif isinstance(obj, list):
        for child in obj:
            no_copied_source_payload(child, path)


def exact_fields(record: object, fields: tuple[str, ...], name: str) -> None:
    """A closed schema prevents invented rights/publication evidence aliases."""
    need(isinstance(record, dict) and set(record) == set(fields),
         f"{name}: missing or unexpected fields")


def validate(packet: dict, census: dict) -> dict:
    need(packet.get("schema") == "imo-g9-core2-pilot-hold-v1",
         "incorrect pilot schema")
    need(packet.get("responsibility_issue") == 130 and
         packet.get("programme_issue") == 137,
         "pilot custody authority must remain destination #130 / #137")
    need(packet.get("governed_purpose") ==
         "RESEARCH_SIGHTING_NOT_SOURCE_CUSTODY_OR_LEARNER_ADMISSION",
         "visual observation was promoted into custody")
    need(packet.get("pilot_question_id") == QID,
         "pilot must be the specifically selected source position")
    no_copied_source_payload(packet)
    exact_fields(packet, (
        "schema", "responsibility_issue", "programme_issue",
        "governed_purpose", "pilot_question_id", "source", "math_check",
        "custody", "observation", "decision",
    ), "pilot packet")
    exact_fields(packet["source"], (
        "source_id", "source_document_url", "source_host_kind",
        "origin_scope", "pdf_page_index_zero_based", "printed_position",
        "source_key_page_index_zero_based", "printed_key_choice_sighted",
        "observation",
    ), "source identity")
    exact_fields(packet["math_check"], (
        "independently_computed_relation", "tested_input_values",
        "computed_output_values", "computed_choice",
        "math_reviewer_independent_approval", "mathematical_method",
        "distractor_exclusion_spotcheck",
    ), "math observation")
    exact_fields(packet["custody"], (
        "retained_restricted_document_receipt", "retained_document_sha256",
        "precise_item_byte_locator",
        "seven_component_custody_independently_verified",
        "official_key_custody_independently_verified",
        "rights_to_reproduce", "external_reference_rights",
        "independent_source_reviewer", "independent_rights_reviewer",
        "protected_bytes_embedded",
    ), "custody")
    exact_fields(packet["observation"], (
        "date_utc", "method", "document_pages_observed",
        "authority_limit", "scope",
        "visual_component_sightings", "source_sighting_review_mode",
        "principal_independence", "visual_component_custody_status",
    ), "visual observation")
    exact_fields(packet["decision"], (
        "status", "core2_eligible", "core2_admitted",
        "learner_published", "all_other_67_positions", "next_action",
    ), "decision")

    c = census.get("source_census", {})
    rows = census.get("records", [])
    need(isinstance(rows, list) and len(rows) == 68 and
         c.get("source_seed_positions") == 66 and
         c.get("source_seed_fullpaper_positions") == 58 and
         c.get("source_seed_sample_positions") == 8 and
         c.get("additional_organizer_sample_positions") == 2 and
         c.get("total_distinct_source_positions") == 68,
         "historical 66 + 2 source denominator changed")
    need(len({r.get("question_id") for r in rows if isinstance(r, dict)}) == 68,
         "source identities duplicated or lost")
    matches = [r for r in rows if r.get("question_id") == QID]
    need(len(matches) == 1, "pilot missing from exact census")
    row = matches[0]
    source = packet.get("source") or {}
    need(source.get("source_id") == SOURCE_ID and
         source.get("source_document_url") == SOURCE_URL and
         source.get("source_host_kind") == "SOF_ORGANIZER_HOSTED_PDF" and
         source.get("origin_scope") == "ORGANIZER_SAMPLE_SEED_POSITION" and
         source.get("pdf_page_index_zero_based") == 0 and
         source.get("source_key_page_index_zero_based") == 1 and
         source.get("printed_position") == "4" and
         source.get("printed_key_choice_sighted") == "B" and
         source.get("observation") == "PDF_VISUAL_SIGHTING_ONLY",
         "PDF identity/page/printed-key sighting changed")
    need(row.get("source_id") == source["source_id"] and
         row.get("source_document_url") == source["source_document_url"] and
         row.get("origin_scope") == source["origin_scope"] and
         row.get("source_host_kind") == source["source_host_kind"] and
         row.get("original_printed_position_claim") == source["printed_position"] and
         row.get("original_printed_position_observed") == source["printed_position"] and
         row.get("source_locator_pdf_page_index") == source["pdf_page_index_zero_based"] and
         row.get("source_discrepancy_case_id") is None and
         row.get("material_source_discrepancy_hold") is False,
         "pilot identity does not match original frozen research census")

    math = packet.get("math_check") or {}
    xs = math.get("tested_input_values")
    ys = math.get("computed_output_values")
    need(xs == [-1, 0, 1, 2] and ys == [-3, -1, 1, 3] and
         all(2 * x - 1 == y for x, y in zip(xs, ys)) and
         math.get("independently_computed_relation") == "y = 2x - 1" and
         math.get("computed_choice") == source["printed_key_choice_sighted"] and
         math.get("math_reviewer_independent_approval") is None,
         "independent arithmetic/key sighting inconsistent or improperly approved")

    spot = math.get("distractor_exclusion_spotcheck") or {}
    exact_fields(spot, (
        "witness_x", "source_output_at_witness", "other_choice_outputs_at_witness",
        "unique_matching_choice", "original_source_option_text_copied",
        "authority",
    ), "Q004 distractor exclusion arithmetic spot-check")
    exclusions = spot.get("other_choice_outputs_at_witness")
    need(isinstance(exclusions, dict)
         and set(exclusions) == {"A", "C", "D"}
         and exclusions == {"A": -2, "C": -3, "D": 1}
         and all(value != -1 for value in exclusions.values())
         and spot.get("witness_x") == 0
         and spot.get("source_output_at_witness") == -1
         and spot.get("unique_matching_choice") == "B"
         and spot.get("original_source_option_text_copied") is False
         and spot.get("authority") ==
         "SELF_CHECKED_DERIVED_ARITHMETIC_NOT_SOURCE_FIDELITY_OR_ADMISSION",
         "nonmatching answer choices or spot check authority were misrepresented")

    observation = packet.get("observation") or {}
    need(observation.get("date_utc") == "2026-10-10" and
         observation.get("method") == "VISUAL_PDF_RENDER_PAGE_0_AND_PAGE_1" and
         observation.get("document_pages_observed") == 2 and
         observation.get("authority_limit") ==
         "VISUAL_SIGHTING_NOT_DURABLE_BYTES_RIGHTS_OR_INDEPENDENT_APPROVAL",
         "unreviewed web-view scope changed")

    sight = observation.get("visual_component_sightings")
    expected_sight = {
        "original_identifier": "SEEN_ON_RENDER_ONLY",
        "stem": "SEEN_ON_RENDER_ONLY",
        "subparts": "NOT_PRESENT_ON_VIEWED_ITEM",
        "options": "SEEN_ON_RENDER_ONLY",
        "conditions": "SEEN_ON_RENDER_ONLY",
        "figures": "TABULAR_VISUAL_SEEN_ONLY",
        "captions": "NOT_PRESENT_ON_VIEWED_ITEM",
        "hints": "NOT_PRESENT_ON_VIEWED_ITEM",
        "answer_or_rubric": "PRINTED_KEY_SEEN_ON_RENDER_ONLY",
    }
    need(isinstance(sight, dict) and sight == expected_sight
         and observation.get("source_sighting_review_mode") ==
         "SELF_CHECK_AND_SPOT_REVIEW_ONLY"
         and observation.get("principal_independence") == "NONE"
         and observation.get("visual_component_custody_status") ==
         "SIGHTED_BUT_NOT_FULLY_VERIFIED_WITH_RETAINED_SOURCE_BYTES",
         "visual item components cannot be upgraded to full source custody")

    custody = packet.get("custody") or {}
    for key in ("retained_restricted_document_receipt",
                "retained_document_sha256", "precise_item_byte_locator",
                "independent_source_reviewer", "independent_rights_reviewer"):
        need(custody.get(key) is None,
             f"{key} cannot be asserted from a visual source sighting")
    need(custody.get("seven_component_custody_independently_verified") is False and
         custody.get("official_key_custody_independently_verified") is False and
         custody.get("rights_to_reproduce") == "NOT_REVIEWED" and
         custody.get("external_reference_rights") == "NOT_REVIEWED" and
         custody.get("protected_bytes_embedded") is False,
         "source custody, approval, or rights fabricated")
    decision = packet.get("decision") or {}
    need(decision.get("status") == "SOURCE_CUSTODY_HOLD" and
         decision.get("core2_eligible") is False and
         decision.get("core2_admitted") is False and
         decision.get("learner_published") is False and
         decision.get("all_other_67_positions") == "HOLD",
         "unauthorized source or learner promotion")
    need(all(r.get("core2_eligible") is False and
             r.get("core2_admitted") is False and
             r.get("learner_published") is False and
             r.get("document_retained_sha256") is None and
             r.get("publisher_publication_rights") == "NOT_REVIEWED" and
             r.get("external_reference_custody_authorized") is False and
             r.get("disposition") ==
             "HOLD_SOURCE_BYTE_DIGEST_COMPONENT_CUSTODY_AND_RIGHTS" and
             r.get("component_verification") ==
             {k: "NOT_FULLY_COMPONENT_VERIFIED" for k in COMPONENTS}
             for r in rows),
         "68-position census must remain unadmitted and without forged custody")
    return {
        "status": "SOURCE_CUSTODY_HOLD", "pilot": QID,
        "total_source_positions": 68, "core2_eligible": 0,
        "core2_admitted": 0, "learner_published": 0,
        "verification": "RESEARCH_INTEGRITY_ONLY_NOT_RIGHTS_OR_ACADEMIC_APPROVAL",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packet", type=Path, default=EVIDENCE)
    parser.add_argument("--census", type=Path, default=CENSUS)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(load(args.packet), load(args.census)),
                         sort_keys=True))
    except PilotHoldError as exc:
        parser.exit(1, f"IMO_CORE2_PILOT_HOLD_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
