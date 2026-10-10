#!/usr/bin/env python3
"""Build and check a private, non-admitting Q004 source inspection checklist.

The nine entries are operator assertions only, not automatic PDF text/figure
comparisons. A PDF byte/hash match and self-check do NOT convey SOF rights,
independent authenticity, academic/QRT or product admission.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import datetime, timezone
import os
import stat
from pathlib import Path

from core2_source_acquisition_gaps import (
    CENSUS, HANDOFF, SourceGapError, artifact_paths,
    compare_historical_fingerprint, historical_fingerprints,
    inventory, load, private_workspace, receipt_status, require,
)

QID = "SOF-IMO-G09-SAMPLE-2026-27-Q004"
DOC_ID = "SOF-IMO-G09-SAMPLE-2026-27"
KEY_PAGE = 1
ITEM_PAGE = 0
QUESTION_NUMBER = "4"
SOURCE_KEY = "B"
FIELDS = {
    "original_identifier": "PRESENT_SELF_CHECKED",
    "stem": "PRESENT_SELF_CHECKED",
    "subparts": "ABSENT_SELF_CHECKED",
    "options": "PRESENT_SELF_CHECKED",
    "conditions": "PRESENT_SELF_CHECKED",
    "figures": "PRESENT_SELF_CHECKED",
    "captions": "ABSENT_SELF_CHECKED",
    "hints": "ABSENT_SELF_CHECKED",
    "answer_or_rubric": "PRESENT_SELF_CHECKED",
}
NOT_CHECKED = "NOT_CHECKED"
SCHEMA = "imo-g9-q004-private-source-spotcheck-v1"
STATUS_MISSING = "HOLD_RETAINED_SOURCE_NOT_VERIFIED"
STATUS_VERSION = "HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE"
STATUS_INCOMPLETE = "HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE"
STATUS_SELF = "SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED"
ALLOWED_TOP = {
    "schema", "question_id", "source_id", "source_url",
    "source_page_index", "source_key_page_index", "printed_item_number",
    "printed_source_key_sighted", "derived_math", "snapshot_sha256",
    "snapshot_byte_length", "historical_version_comparison",
    "source_components", "spotcheck_actor_role", "spotcheck_timestamp_utc",
    "review_mode", "principal_independence", "source_rights",
    "core2_eligible", "core2_admitted", "learner_published",
}
MATH = {
    "source_table_x_sighted": [-1, 0, 1, 2],
    "computed_y_from_two_x_minus_one": [-3, -1, 1, 3],
    "derived_relation": "y = 2x - 1",
    "printed_choice_sighted": "B",
    "other_choice_outputs_at_x_zero": {"A": -2, "C": -3, "D": 1},
    "math_evidence_scope": "DERIVED_SELF_CHECK_NOT_SOURCE_ITEM_CUSTODY",
}


def _document(workspace: Path | None) -> tuple[dict, str, str | None, int | None]:
    census, handoff = load(CENSUS), load(HANDOFF)
    rows, docs = inventory(census, handoff)
    require(sum(row["question_id"] == QID for row in rows) == 1,
            "Q004 missing from frozen 68 position census")
    doc = docs[DOC_ID]
    status, _ = receipt_status(doc, workspace)
    digest = None
    length = None
    if status in {
        "VERIFIED_RETAINED_BYTES_ONLY",
        "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED",
    }:
        _, receipt_path = artifact_paths(workspace, DOC_ID)
        receipt = load(receipt_path)
        digest = receipt["sha256"]
        length = receipt["byte_length"]
    pin = historical_fingerprints(docs)[DOC_ID]
    version = compare_historical_fingerprint(doc, workspace, status, pin)
    return doc, version, digest, length


def make_template(workspace: Path | None) -> dict:
    doc, version, digest, length = _document(workspace)
    return {
        "schema": SCHEMA,
        "question_id": QID,
        "source_id": DOC_ID,
        "source_url": doc["requested_pdf_url"],
        "source_page_index": ITEM_PAGE,
        "source_key_page_index": KEY_PAGE,
        "printed_item_number": QUESTION_NUMBER,
        "printed_source_key_sighted": SOURCE_KEY,
        "derived_math": copy.deepcopy(MATH),
        "snapshot_sha256": digest,
        "snapshot_byte_length": length,
        "historical_version_comparison": version,
        "source_components": {name: NOT_CHECKED for name in FIELDS},
        "spotcheck_actor_role": None,
        "spotcheck_timestamp_utc": None,
        "review_mode": "SELF_REVIEW",
        "principal_independence": "NONE",
        "source_rights": "NOT_REVIEWED",
        "core2_eligible": False,
        "core2_admitted": False,
        "learner_published": False,
    }


def _valid_utc(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", value
    ):
        return False
    try:
        dt = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return dt.utcoffset() == timezone.utc.utcoffset(dt)


def evaluate(packet: dict, workspace: Path | None) -> dict:
    """Return a fail-closed result. Even COMPLETE retains all 68 source holds."""
    required = make_template(workspace)
    require(isinstance(packet, dict) and set(packet) == ALLOWED_TOP,
            "Q004 assessment missing fields or injecting unknown authority")
    findings: list[str] = []
    for field in (ALLOWED_TOP - {"source_components",
                                "spotcheck_actor_role",
                                "spotcheck_timestamp_utc"}):
        if packet[field] != required[field]:
            findings.append("PINNED_Q004_IDENTITY_DIGEST_KEY_OR_AUTHORITY_MISMATCH")
            break
    components = packet["source_components"]
    require(isinstance(components, dict) and set(components) == set(FIELDS),
            "Q004 requires exactly nine source component dispositions")
    if any(value not in (NOT_CHECKED, FIELDS[name])
           for name, value in components.items()):
        findings.append("UNRECOGNIZED_OR_FALSE_SOURCE_COMPONENT_STATUS")
    complete = all(components[name] == FIELDS[name] for name in FIELDS)
    if not complete:
        findings.append("NINE_COMPONENT_SELF_CHECK_INCOMPLETE")
    if packet["spotcheck_actor_role"] not in (None, "SELF_SPOT_CHECK"):
        findings.append("REVIEW_AUTHORITY_INVALID")
    if packet["spotcheck_timestamp_utc"] is not None and not _valid_utc(
        packet["spotcheck_timestamp_utc"]
    ):
        findings.append("SPOT_CHECK_TIMESTAMP_INVALID")
    if complete and (
        packet["spotcheck_actor_role"] != "SELF_SPOT_CHECK"
        or not _valid_utc(packet["spotcheck_timestamp_utc"])
    ):
        findings.append("COMPLETED_CHECK_REQUIRES_NAMED_SELF_ROLE_AND_UTC")
    _, version, digest, length = _document(workspace)
    if digest is None or length is None:
        findings.append("PRIVATE_RETAINED_PDF_RECEIPT_MISSING_OR_INVALID")
        state = STATUS_MISSING
    elif version != "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY":
        findings.append("SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED")
        state = STATUS_VERSION
    elif findings:
        state = STATUS_INCOMPLETE
    else:
        # The literal role and component states are operator declarations;
        # this is not third-party evidence of the quality of the inspection.
        state = STATUS_SELF
    return {
        "schema": "imo-g9-q004-spotcheck-verdict-v1",
        "question_id": QID,
        "status": state,
        "component_check_complete": complete,
        "historical_version_comparison": version,
        "blocking_codes": sorted(set(findings)),
        "self_attestation_not_source_certificate": True,
        "source_custody_hold": 68,
        "core2_eligible": False,
        "core2_admitted": False,
        "learner_published": False,
        "source_rights": "NOT_REVIEWED",
    }


def _assessment_path(workspace: Path, path: Path) -> Path:
    require(path.is_absolute() and not path.is_symlink(),
            "assessment input must be an absolute non-symlink file")
    p = path.resolve(strict=False)
    # A prepared two-page inspection bundle may keep its unchecked packet
    # alongside private page renders. Do not permit arbitrary subdirectories.
    private_bundle = workspace / "q004-private-review"
    bundled = (p.parent == private_bundle
               and p.name == "q004.inspection.json"
               and private_bundle.is_dir()
               and not private_bundle.is_symlink()
               and private_bundle.stat().st_uid == os.getuid()
               and stat.S_IMODE(private_bundle.stat().st_mode) == 0o700
               and p.is_file()
               and p.stat().st_uid == os.getuid()
               and stat.S_IMODE(p.stat().st_mode) == 0o600)
    require(p.is_file() and ((p.parent == workspace and
                             p.name.endswith(".json")) or bundled),
            "assessment must be a permitted private Q004 JSON file")
    return p


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("operation", choices=("template", "verify"))
    parser.add_argument("--private-dir", type=Path)
    parser.add_argument("--assessment", type=Path)
    args = parser.parse_args()
    try:
        require(args.private_dir is not None, "--private-dir required")
        workspace = private_workspace(args.private_dir)
        if args.operation == "template":
            require(args.assessment is None,
                    "template does not use --assessment")
            outcome = make_template(workspace)
        else:
            require(args.assessment is not None,
                    "verify requires --assessment in private directory")
            outcome = evaluate(load(_assessment_path(workspace, args.assessment)),
                               workspace)
        print(json.dumps(outcome, indent=2, sort_keys=True))
        return 0
    except (SourceGapError, OSError, ValueError) as exc:
        parser.exit(1, "IMO_Q004_SPOTCHECK_INVALID: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
