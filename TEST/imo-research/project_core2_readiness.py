#!/usr/bin/env python3
"""Project mechanical source-custody readiness without admitting any original IMO item.

Reads the frozen research census, and optionally PRIVATE evidence already acquired
through Shared/tools/source_pipeline.py. It does not fetch, publish, transcribe or
approve source material. READY_FOR_SPOT_CHECK is NOT authentic Core2 admission.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.library import source_custody  # noqa: E402
from Shared.tools import source_pipeline  # noqa: E402

CENSUS_PATH = REPO / "TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
ITEM_LOCATOR = re.compile(r"^pdf_page_index=(0|[1-9][0-9]*);printed_item=([1-9][0-9]*)$")
EVIDENCE_KEYS = {
    "question_id", "acquisition", "resource", "question",
    "supporting_resources", "inspected_sections", "access_status",
}
BUNDLE_KEYS = {"schema", "items"}


class ReadinessError(ValueError):
    """Invalid research input: do not emit a misleading projection."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ReadinessError(message)


def read_json(path: Path) -> dict:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReadinessError(f"cannot read {path}: {exc}") from exc
    require(isinstance(result, dict), "JSON root must be object")
    return result


def assert_frozen_census(census: dict) -> list[dict]:
    d = census.get("source_census") or {}
    rows = census.get("records")
    require(isinstance(rows, list) and len(rows) == 68,
            "frozen 68-position source denominator missing")
    require(
        d.get("source_seed_positions") == 66
        and d.get("source_seed_fullpaper_positions") == 58
        and d.get("source_seed_sample_positions") == 8
        and d.get("additional_organizer_sample_positions") == 2
        and d.get("total_distinct_source_positions") == 68,
        "historical 66+2 inventory changed")
    require(all(isinstance(row, dict) and isinstance(row.get("question_id"), str)
                and row.get("source_id") and row.get("source_document_url")
                and row.get("original_printed_position_claim") for row in rows),
            "incomplete historical source identity")
    require(len({row["question_id"] for row in rows}) == 68,
            "duplicate frozen source identity")
    require(all(row.get("core2_eligible") is False
                and row.get("core2_admitted") is False
                and row.get("learner_published") is False
                and row.get("document_retained_sha256") is None
                and row.get("publisher_publication_rights") == "NOT_REVIEWED"
                for row in rows),
            "frozen research holds must not be silently overwritten")
    return rows


def _private_snapshot(ref: object, repo: Path) -> bool:
    if not isinstance(ref, str) or not ref.strip():
        return False
    path = Path(ref)
    absolute = path if path.is_absolute() else repo / path
    absolute = absolute.resolve()
    # No publisher bytes under any public/site/generated document tree.
    forbidden = (repo / "public", repo / "docs", repo / "TEST/imo-research")
    return not any(absolute == root.resolve()
                   or root.resolve() in absolute.parents for root in forbidden)


def evaluate(row: dict, item: dict | None, repo: Path) -> dict:
    qid = row["question_id"]
    findings: list[str] = []
    if item is None:
        findings.append("NO_ITEM_ACQUISITION_OR_CUSTODY_PROOF")
    else:
        acquisition = item["acquisition"]
        resource = item["resource"]
        question = item["question"]
        if not all(isinstance(obj, dict)
                   for obj in (acquisition, resource, question)):
            findings.append("EVIDENCE_RECORD_INVALID")
        else:
            required_acquisition = {
                "acquisition_id", "version", "subject", "bucket_id",
                "resource_ref", "source_kind", "requested_locator",
                "resolved_locator", "acquired_at", "media_type",
                "byte_length", "sha256", "snapshot_ref",
            }
            required_components = {
                "original_identifier", "stem", "subparts", "options",
                "conditions", "figures", "captions", "hints", "answer_or_rubric",
            }
            proof = source_custody.proof_for(question) or {}
            components = proof.get("components")
            if (set(acquisition) != required_acquisition
                or not isinstance(acquisition.get("acquisition_id"), str)
                or not acquisition["acquisition_id"].strip()
                or acquisition.get("source_kind") not in {"FILE", "URL"}
                or not isinstance(acquisition.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", acquisition["sha256"])
                or not isinstance(acquisition.get("byte_length"), int)
                or acquisition["byte_length"] <= 0
            ):
                findings.append("ACQUISITION_METADATA_INVALID")
            if (not isinstance(components, dict)
                or set(components) != required_components
                or any(value not in {"PRESERVED", "NOT_PRESENT_IN_SOURCE",
                                     "EXTERNAL_REFERENCE_VERIFIED"}
                       for value in components.values())
                or not isinstance(proof.get("acquisition_ref"), str)
                or not proof["acquisition_ref"]
            ):
                findings.append("CUSTODY_COMPONENT_COVERAGE_INVALID")
            if acquisition.get("requested_locator") != row["source_document_url"]:
                findings.append("SOURCE_DOCUMENT_MISMATCH")
            if acquisition.get("resource_ref") != resource.get("id"):
                findings.append("SOURCE_RESOURCE_MISMATCH")
            if acquisition.get("media_type") != "application/pdf":
                findings.append("SOURCE_MEDIA_NOT_PDF")
            snap = acquisition.get("snapshot_ref")
            if not _private_snapshot(snap, repo):
                findings.append("RESTRICTED_SNAPSHOT_REQUIRED")
            else:
                verification = source_pipeline.verify_acquisition(acquisition, repo=repo)
                if not verification["passed"]:
                    findings.append("RETAINED_BYTES_DIGEST_OR_SCHEMA_FAILED")
            if resource.get("_collection") != "resources" or not resource.get("origin") or (
                resource.get("snapshot_digest") != acquisition.get("sha256")
                or resource.get("snapshot_ref") != snap
            ):
                findings.append("RESOURCE_PROVENANCE_MISMATCH")
            if question.get("id") != qid or question.get("origin") != "ORIGINAL":
                findings.append("CANONICAL_ITEM_IDENTITY_MISMATCH")
            if str(question.get("original_identifier")) != str(
                row["original_printed_position_claim"]
            ):
                findings.append("PRINTED_QUESTION_NUMBER_MISMATCH")
            proof = source_custody.proof_for(question) or {}
            locator = proof.get("source_item_locator")
            parsed = ITEM_LOCATOR.fullmatch(locator) if isinstance(locator, str) else None
            if parsed is None or parsed.group(2) != str(
                row["original_printed_position_claim"]
            ) or (
                row.get("source_locator_pdf_page_index") is not None
                and int(parsed.group(1)) != row["source_locator_pdf_page_index"]
            ):
                findings.append("PRECISE_SOURCE_ITEM_LOCATOR_MISMATCH")
            if item["access_status"] != "FULL_ITEM_INSPECTED":
                findings.append("FULL_ITEM_INSPECTION_NOT_RECORDED")
            records = {resource.get("id"): resource} if resource.get("id") else {}
            for figure in item["supporting_resources"]:
                if (isinstance(figure, dict) and isinstance(figure.get("id"), str)
                    and figure["id"] and figure["id"] not in records):
                    records[figure["id"]] = figure
                else:
                    findings.append("FIGURE_RESOURCE_RECORD_INVALID")
            # Existing canonical proof validator remains the sole question-custody checker.
            proof_errors = source_custody.validate_question(
                question, records=records, acquisition=acquisition,
                inspected_sections=item["inspected_sections"],
                access_status=item["access_status"], require_resolved=True,
                repo=repo,
            )
            if proof_errors:
                findings.append("CANONICAL_SOURCE_CUSTODY_PROOF_INVALID")
    return {
        "question_id": qid, "source_id": row["source_id"],
        "status": "HOLD" if findings else "READY_FOR_SPOT_CHECK_NOT_ADMITTED",
        "technical_spot_check_ready": not findings,
        "blocking_codes": findings,
        "core2_eligible": False, "core2_admitted": False,
        "learner_published": False, "rights_verified": False,
    }


def project(census: dict, evidence: dict | None = None, repo: Path = REPO) -> dict:
    rows = assert_frozen_census(census)
    evidence = evidence if evidence is not None else {
        "schema": "imo-g9-private-custody-evidence-v1", "items": []
    }
    require(isinstance(evidence, dict) and set(evidence) == BUNDLE_KEYS
            and evidence.get("schema") == "imo-g9-private-custody-evidence-v1"
            and isinstance(evidence.get("items"), list),
            "private input envelope invalid")
    ids = {row["question_id"] for row in rows}
    items: dict[str, dict] = {}
    for item in evidence["items"]:
        require(isinstance(item, dict) and set(item) == EVIDENCE_KEYS,
                "item input fields invalid; rights/admission aliases forbidden")
        qid = item["question_id"]
        require(isinstance(qid, str) and qid in ids and qid not in items,
                "duplicate or unindexed item input")
        require(isinstance(item["supporting_resources"], list)
                and isinstance(item["inspected_sections"], list)
                and all(isinstance(x, str) for x in item["inspected_sections"]),
                "invalid figure resources or inspected item locator list")
        items[qid] = item
    reports = [evaluate(row, items.get(row["question_id"]), repo) for row in rows]
    ready = sum(row["technical_spot_check_ready"] for row in reports)
    return {
        "schema": "imo-g9-readiness-projection-v1",
        "authority": "RESEARCH_ONLY_MECHANICAL_SPOT_CHECK_NOT_ADMISSION",
        "source_positions": 68,
        "technical_spot_check_ready": ready,
        "technical_spot_check_pending": 68 - ready,
        "source_custody_hold": 68,
        "core2_eligible": 0,
        "core2_admitted": 0,
        "rights_verified": 0,
        "learner_published": 0,
        "items": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--census", type=Path, default=CENSUS_PATH)
    parser.add_argument("--private-evidence", type=Path, default=None,
                        help="Local restricted workspace JSON; do not commit source bytes")
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional research-only report JSON path")
    args = parser.parse_args()
    try:
        result = project(read_json(args.census),
                         read_json(args.private_evidence) if args.private_evidence else None)
    except ReadinessError as exc:
        parser.exit(1, f"IMO_READINESS_INVALID: {exc}\n")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
