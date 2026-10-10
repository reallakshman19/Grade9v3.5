#!/usr/bin/env python3
"""Restricted SOF IMO document acquisition and non-admitting 68-item gap report.

Reuses Shared/tools/source_pipeline.py; never commits publisher bytes, text,
figures or private receipts. This tool cannot certify source authenticity,
component fidelity, reuse rights, mathematics or Core2 product admission.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from Shared.tools import source_pipeline  # noqa: E402

ROOT = REPO / "TEST/imo-research/intake"
CENSUS = ROOT / "core2-source-custody-eligibility.v1.json"
HANDOFF = ROOT / "core2-source-acquisition-handoff.v1.json"
SOURCE_IDS = {
    "SOF-IMO-G09-L1-2023-24-A": 24,
    "SOF-IMO-G09-L1-2024-25-B": 12,
    "SOF-IMO-G09-L1-2025-26-A": 22,
    "SOF-IMO-G09-SAMPLE-2026-27": 10,
}
# Exact pinned download targets are a network safety allowlist, NOT source authority.
SOURCE_URLS = {
    "SOF-IMO-G09-L1-2023-24-A": "https://iswkoman.com/uploads/olympiad/8919398-CL%20IX%20IMO%202023-24%20(1).pdf",
    "SOF-IMO-G09-L1-2024-25-B": "https://www.iswkoman.com/uploads/olympiad/2107431-CLASS%209-IMO24.pdf",
    "SOF-IMO-G09-L1-2025-26-A": "https://www.iswkoman.com/uploads/olympiad/9262492-IMO%2025-26%20CLASS%209.pdf",
    "SOF-IMO-G09-SAMPLE-2026-27": "https://sofworld.org/download/file/fid/73719",
}
FINGERPRINTS = ROOT / "core2-ephemeral-source-fingerprints.v1.json"
RIGHTS_NOTICE = ROOT / "core2-public-rights-notice.v1.json"
HISTORICAL_PROBE_ARCHIVE_SHA256 = "399e14a5f3f992ef47014ab3594c989dfe4cf9192cd95322b135978de7c3a486"
# Exact prior run observations; a new download may legitimately differ.
# A match proves byte equality to that temporary probe only, never rights.
HISTORICAL_PINS = {
    "SOF-IMO-G09-L1-2023-24-A": (7417747, "462d1dae6091a00bb3cfe685c8cdbe93077ec205f674f2c8873b5fe0c0f0c91c"),
    "SOF-IMO-G09-L1-2024-25-B": (3355199, "ee4b6060360e6c94eafd25c6bb0a9b15f2b81340f9b331d035056fe6c6bd8576"),
    "SOF-IMO-G09-L1-2025-26-A": (7765096, "766402d4245514d43d18fa6e9d1468df5f393464926923defe180dc012924f54"),
    "SOF-IMO-G09-SAMPLE-2026-27": (132856, "e1229c45cbecb13fe4e8ac65e83c1eec029e6eea83e601cc591e7ce97a65022f"),
}
HOLD = "HOLD_NO_CORE2_ADMISSION"
BUCKET = "BUCKET-TEST-IMO-G9-SOURCE-ACQUISITION"


class SourceGapError(ValueError):
    """An unsafe workspace, tampered input or fake acquisition was found."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SourceGapError(message)


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceGapError(f"invalid JSON input: {path.name}: {exc}") from exc
    require(isinstance(value, dict), "expected JSON object")
    return value


def inventory(census: dict, handoff: dict) -> tuple[list[dict], dict[str, dict]]:
    rows = census.get("records")
    queue = handoff.get("source_documents_queue")
    counts = census.get("source_census") or {}
    require(isinstance(rows, list) and len(rows) == 68
            and isinstance(queue, list) and len(queue) == 4
            and counts.get("source_seed_positions") == 66
            and counts.get("source_seed_fullpaper_positions") == 58
            and counts.get("source_seed_sample_positions") == 8
            and counts.get("additional_organizer_sample_positions") == 2
            and counts.get("total_distinct_source_positions") == 68,
            "frozen source denominator differs from 58+8+2")
    ids = [row.get("question_id") for row in rows if isinstance(row, dict)]
    require(len(ids) == len(set(ids)) == 68, "source question IDs missing or duplicated")
    docs = {d.get("source_id"): d for d in queue if isinstance(d, dict)}
    require(len(docs) == 4 and set(docs) == set(SOURCE_IDS),
            "four-document source identity or count altered")
    require(handoff.get("source_positions") == 68
            and handoff.get("source_documents") == 4
            and handoff.get("retained_pdf_documents") == 0
            and handoff.get("source_core2_admitted") == 0,
            "frozen handoff promoted without evidence")
    for source_id, doc in docs.items():
        url = doc.get("requested_pdf_url")
        parts = urlsplit(url if isinstance(url, str) else "")
        require(url == SOURCE_URLS[source_id]
                and parts.scheme == "https" and bool(parts.hostname)
                and parts.username is None and parts.password is None,
                "source URL is not a trusted HTTPS locator")
        require(doc.get("position_count_in_68") == SOURCE_IDS[source_id],
                "document counts changed")
        matches = [row for row in rows if row.get("source_id") == source_id]
        require(len(matches) == SOURCE_IDS[source_id]
                and all(row.get("source_document_url") == url
                        and row.get("core2_eligible") is False
                        and row.get("core2_admitted") is False
                        and row.get("learner_published") is False
                        and row.get("publisher_publication_rights") == "NOT_REVIEWED"
                        and row.get("document_retained_sha256") is None
                        for row in matches),
                "frozen question custody altered or source URL mismatched")
    return rows, docs


def private_workspace(path: Path, *, create: bool = False) -> Path:
    require(path.is_absolute() and path != Path("/"),
            "private workspace must be a non-root absolute path")
    require(not path.is_symlink(), "symlinked private workspace rejected")
    p = path.resolve(strict=False)
    repo = REPO.resolve()
    require(p != repo and repo not in p.parents,
            "restricted source bytes must stay outside Git checkout")
    if create and not p.exists():
        p.mkdir(mode=0o700, parents=False)
    require(p.is_dir(), "restricted workspace does not exist")
    st = p.stat()
    require(stat.S_ISDIR(st.st_mode)
            and st.st_uid == os.getuid()
            and not (stat.S_IMODE(st.st_mode) & 0o077),
            "restricted workspace must be owned by current user, mode 0700")
    return p


def basename(source_id: str) -> str:
    require(source_id in SOURCE_IDS, "unindexed source document")
    return source_id.lower()


def artifact_paths(workspace: Path, source_id: str) -> tuple[Path, Path]:
    base = basename(source_id)
    return workspace / (base + ".pdf"), workspace / (base + ".acquisition.json")


def _same_host(expected: str, observed: str) -> bool:
    want, got = urlsplit(expected), urlsplit(observed)
    return (want.scheme == got.scheme == "https"
            and (want.hostname or "").removeprefix("www.") == (got.hostname or "").removeprefix("www.")
            and got.username is None
            and got.password is None)


def receipt_status(doc: dict, workspace: Path | None) -> tuple[str, list[str]]:
    if workspace is None:
        return "NOT_ACQUIRED", ["RETAINED_DOCUMENT_RECEIPT_MISSING"]
    snapshot, receipt_path = artifact_paths(workspace, doc["source_id"])
    if snapshot.is_symlink() or receipt_path.is_symlink():
        return "INVALID", ["SYMLINKED_SOURCE_ARTIFACT"]
    if not snapshot.is_file() or not receipt_path.is_file():
        return "NOT_ACQUIRED", ["RETAINED_DOCUMENT_RECEIPT_MISSING"]
    try:
        receipt = load(receipt_path)
        required = {
            "acquisition_id", "version", "subject", "bucket_id",
            "resource_ref", "source_kind", "requested_locator",
            "resolved_locator", "acquired_at", "media_type",
            "byte_length", "sha256", "snapshot_ref",
        }
        require(set(receipt) == required, "receipt fields invalid")
        require(receipt.get("subject") == "TEST"
                and receipt.get("bucket_id") == BUCKET
                and receipt.get("source_kind") in ("URL", "FILE")
                and receipt.get("resource_ref") == doc["source_id"]
                and receipt.get("requested_locator") == doc["requested_pdf_url"]
                and (
                    (receipt["source_kind"] == "URL"
                     and _same_host(doc["requested_pdf_url"],
                                    receipt.get("resolved_locator") or ""))
                    or (receipt["source_kind"] == "FILE"
                        and isinstance(receipt.get("resolved_locator"), str)
                        and Path(receipt["resolved_locator"]).is_absolute()
                        and Path(receipt["resolved_locator"]).suffix.lower() == ".pdf"
                        and REPO.resolve() not in
                        Path(receipt["resolved_locator"]).resolve(strict=False).parents)
                )
                and receipt.get("snapshot_ref") == str(snapshot),
                "receipt/source identity mismatch")
        with snapshot.open("rb") as source_bytes:
            require(source_bytes.read(5) == b"%PDF-",
                    "snapshot does not contain PDF header")
        outcome = source_pipeline.verify_acquisition(receipt, repo=REPO)
        require(outcome.get("passed") is True, "retained bytes or digest invalid")
        if receipt["source_kind"] == "FILE":
            return "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED", [
                "LOCAL_FILE_SOURCE_ORIGIN_UNVERIFIED"
            ]
        return "VERIFIED_RETAINED_BYTES_ONLY", []
    except (OSError, SourceGapError, ValueError, TypeError) as exc:
        # Public report deliberately doesn't print local file names or exception text.
        return "INVALID", ["RETAINED_DOCUMENT_RECEIPT_INVALID"]



def historical_fingerprints(docs: dict[str, dict],
                            supplied: dict | None = None) -> dict[str, dict]:
    """Pin archived ephemeral CI observations; do NOT assert retained custody."""
    obj = load(FINGERPRINTS) if supplied is None else supplied
    required = {
        "schema", "classification", "source_repository", "source_workflow_run",
        "source_job_id", "source_artifact_id", "source_artifact_zip_sha256",
        "artifact_contains_pdf_bytes", "temporary_pdf_downloads",
        "retained_original_pdf_documents", "verified_source_item_custody",
        "rights_status", "source_positions", "documents",
    }
    require(isinstance(obj, dict) and set(obj) == required,
            "historical probe metadata envelope invalid")
    require(obj["schema"] == "imo-g9-ephemeral-source-fingerprints-v1"
            and obj["classification"] ==
            "HISTORICAL_CI_NETWORK_PROBE_ONLY_NOT_SOURCE_CUSTODY_OR_RIGHTS"
            and obj["source_repository"] == "reallaksh19/Grade9v3.5"
            and obj["source_workflow_run"] == 37868836390
            and obj["source_job_id"] == 113621920381
            and obj["source_artifact_id"] == 11588893886
            and obj["source_artifact_zip_sha256"] ==
            HISTORICAL_PROBE_ARCHIVE_SHA256
            and obj["artifact_contains_pdf_bytes"] is False
            and obj["temporary_pdf_downloads"] == 4
            and obj["retained_original_pdf_documents"] == 0
            and obj["verified_source_item_custody"] == 0
            and obj["rights_status"] == "NOT_REVIEWED"
            and obj["source_positions"] == 68,
            "historical ephemeral probe misrepresented as custody")
    entries = obj["documents"]
    require(isinstance(entries, list) and len(entries) == 4,
            "historical probe must describe exactly four documents")
    expected_keys = {
        "source_id", "requested_url", "positions", "byte_length", "sha256",
        "snapshot_retained", "local_byte_verification_passed_in_historical_run",
    }
    by_id = {}
    for row in entries:
        require(isinstance(row, dict) and set(row) == expected_keys,
                "historical probe document structure invalid")
        sid = row["source_id"]
        require(sid in HISTORICAL_PINS and sid not in by_id
                and sid in docs
                and row["requested_url"] == docs[sid]["requested_pdf_url"]
                and row["positions"] == SOURCE_IDS[sid]
                and (row["byte_length"], row["sha256"]) == HISTORICAL_PINS[sid]
                and row["snapshot_retained"] is False
                and row["local_byte_verification_passed_in_historical_run"] is True,
                "historical PDF fingerprint inconsistent with pinned job artifact")
        by_id[sid] = row
    require(set(by_id) == set(docs) == set(HISTORICAL_PINS),
            "historical source ID incomplete")
    return by_id


def compare_historical_fingerprint(
    doc: dict, workspace: Path | None, current_status: str,
    fingerprint: dict,
) -> str:
    """Compare *valid retained bytes* with a former ephemeral SHA/length."""
    if current_status == "NOT_ACQUIRED":
        return "NOT_CHECKED_NO_RETAINED_BYTES"
    if current_status == "INVALID":
        return "NOT_CHECKED_INVALID_RECEIPT"
    require(workspace is not None, "verified receipt needs a private workspace")
    _, receipt_path = artifact_paths(workspace, doc["source_id"])
    receipt = load(receipt_path)
    if (receipt.get("sha256") == fingerprint["sha256"]
            and receipt.get("byte_length") == fingerprint["byte_length"]):
        return "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY"
    return "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION"



def public_rights_notice(docs: dict[str, dict],
                         supplied: dict | None = None) -> dict:
    """Research notice, not a publisher licence or source ownership finding."""
    obj = load(RIGHTS_NOTICE) if supplied is None else supplied
    expected = {
        "schema": "imo-g9-public-rights-notice-observation-v1",
        "responsibility_issue": 130,
        "observation_date_utc": "2026-10-10",
        "organization": "SCIENCE_OLYMPIAD_FOUNDATION",
        "public_notice_url": "https://sofworld.org/",
        "general_contact_url": "https://sofworld.org/contact",
        "general_contact_email": "info@sofworld.org",
        "notice_summary": "GENERAL_SOF_SITE_NOTICE_REQUIRES_PRIOR_WRITTEN_CONSENT_FOR_COPY_OR_USE",
        "notice_scope": "GENERAL_OFFICIAL_SITE_FOOTER_NOT_SPECIFIC_FOUR_PDF_LICENSE_REVIEW",
        "written_reproduction_permission_received": False,
        "publisher_rights_holder_for_all_mirror_pdfs_verified": False,
        "permission_request_sent": False,
        "permission_request_receipt": None,
        "license_document_ref": None,
        "verbatim_question_reuse_authorized": False,
        "figure_reuse_authorized": False,
        "rights_to_publish_original_works": "NOT_EVIDENCED",
        "external_linking_authorization": "NOT_DETERMINED_BY_THIS_NOTICE",
        "canonical_source_admission_count": 0,
        "learner_original_question_publication_count": 0,
    }
    require(isinstance(obj, dict) and set(obj) == set(expected) | {"documents"}
            and all(type(obj.get(k)) is type(v) and obj[k] == v
                    for k, v in expected.items()),
            "general SOF public rights notice fabricated or overstated")
    documents = obj["documents"]
    require(isinstance(documents, list) and len(documents) == 4,
            "rights observation must preserve four source documents")
    seen = set()
    for row in documents:
        require(isinstance(row, dict) and set(row) == {
            "source_id", "rights_disposition",
            "policy_notice_applies_as_general_context_only",
            "publication_authorized",
        }, "rights observation document fields invalid")
        sid = row["source_id"]
        require(sid in docs and sid not in seen
                and row["rights_disposition"] == "NOT_GRANTED_OR_EVIDENCED"
                and row["policy_notice_applies_as_general_context_only"] is True
                and row["publication_authorized"] is False,
                "source rights authorization cannot be invented")
        seen.add(sid)
    require(seen == set(docs),
            "source rights notice must cover all four source document IDs")
    return obj


def report(census: dict, handoff: dict, workspace: Path | None = None) -> dict:
    rows, docs = inventory(census, handoff)
    fingerprints = historical_fingerprints(docs)
    rights = public_rights_notice(docs)
    states = {sid: receipt_status(doc, workspace) for sid, doc in docs.items()}
    version_checks = {
        sid: compare_historical_fingerprint(doc, workspace, states[sid][0],
                                            fingerprints[sid])
        for sid, doc in docs.items()
    }
    doc_rows = []
    for sid, doc in docs.items():
        status, findings = states[sid]
        doc_rows.append({
            "source_id": sid,
            "indexed_positions": SOURCE_IDS[sid],
            "receipt_status": status,
            "historical_probe_sha256": fingerprints[sid]["sha256"],
            "historical_probe_byte_length": fingerprints[sid]["byte_length"],
            "historical_version_comparison": version_checks[sid],
            "historical_provenance": "EPHEMERAL_CI_ONLY_NO_SOURCE_BYTES_RETAINED",
            "blocking_codes": findings + (
                ["REVIEW_SOURCE_DOCUMENT_VERSION_DRIFT"]
                if version_checks[sid] ==
                "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION"
                else []),
            "source_rights": "NOT_REVIEWED",
            "general_publisher_site_notice": rights["notice_summary"],
            "specific_pdf_reproduction_grant": "NOT_EVIDENCED",
            "independent_item_validation": "NOT_DONE",
        })
    question_rows = []
    for row in rows:
        status, doc_findings = states[row["source_id"]]
        codes = list(doc_findings)
        if version_checks[row["source_id"]] == "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION":
            codes.append("REVIEW_SOURCE_DOCUMENT_VERSION_DRIFT")
        if row.get("source_locator_pdf_page_index") is None:
            codes.append("ITEM_PAGE_LOCATOR_UNOBSERVED")
        else:
            codes.append("ITEM_PAGE_OBSERVATION_NOT_COMPONENT_CUSTODY")
        codes.append("NINE_CUSTODY_COMPONENTS_UNVERIFIED")
        codes.append("PRINTED_KEY_AND_MATH_SPOT_CHECK_NOT_ACCEPTED")
        if row.get("material_source_discrepancy_hold"):
            codes.append("RECORDED_SOURCE_DISCREPANCY_OPEN")
        codes.extend(["SOURCE_REUSE_RIGHTS_NOT_REVIEWED",
                      "PUBLIC_SOF_SITE_NOTICE_REQUIRES_PRIOR_WRITTEN_CONSENT",
                      "SOURCE_SPECIFIC_WRITTEN_PERMISSION_NOT_EVIDENCED",
                      "OWNER_CORE2_ADMISSION_NOT_GRANTED"])
        question_rows.append({
            "question_id": row["question_id"],
            "source_id": row["source_id"],
            "printed_position_claim": row["original_printed_position_claim"],
            "observed_pdf_page_index": row.get("source_locator_pdf_page_index"),
            "document_receipt_status": status,
            "status": HOLD,
            "blocking_codes": codes,
            "next_action": row["next_source_action"],
            "core2_eligible": False,
            "core2_admitted": False,
            "learner_published": False,
        })
    return {
        "schema": "imo-g09-private-source-gap-report-v1",
        "authority": "RESEARCH_GAP_PROJECTION_NOT_SOURCE_ADMISSION",
        "document_count": 4,
        "verified_retained_document_count": sum(
            x["receipt_status"] in {
                "VERIFIED_RETAINED_BYTES_ONLY",
                "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED",
            } for x in doc_rows),
        "local_import_document_count": sum(
            x["receipt_status"] ==
            "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED"
            for x in doc_rows),
        "historical_version_matches": sum(
            value == "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY"
            for value in version_checks.values()),
        "historical_probe_archive_sha256": HISTORICAL_PROBE_ARCHIVE_SHA256,
        "public_rights_notice": rights["notice_summary"],
        "source_specific_reproduction_grants_evidenced": 0,
        "question_count": 68,
        "source_custody_hold": 68,
        "core2_eligible": 0, "core2_admitted": 0, "learner_published": 0,
        "documents": doc_rows,
        "questions": question_rows,
    }


def _write_exclusive(path: Path, payload: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(payload)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def validate_local_source(path: Path, workspace: Path) -> Path:
    """Allow a browser-downloaded local file; never claim it is publisher-authentic."""
    require(path.is_absolute() and not path.is_symlink(),
            "local source must be an absolute, non-symlink file")
    source = path.resolve(strict=False)
    require(source.is_file() and source.suffix.lower() == ".pdf",
            "local source must exist and have a PDF file extension")
    require(REPO.resolve() not in source.parents
            and workspace.resolve() not in source.parents,
            "local source cannot be repository content or the custody workspace")
    require(source.stat().st_size <= 100 * 1024 * 1024,
            "local source exceeds 100 MiB import limit")
    return source


def acquire(doc: dict, workspace: Path,
            local_file: Path | None = None) -> dict:
    """One explicitly requested document; never overwrite a prior private receipt."""
    source_id = doc["source_id"]
    snapshot, receipt = artifact_paths(workspace, source_id)
    require(not snapshot.exists() and not receipt.exists()
            and not snapshot.is_symlink() and not receipt.is_symlink(),
            "source snapshot/receipt already exists: refuse overwrite")
    old_mask = os.umask(0o077)
    try:
        acquired_at = datetime.now(timezone.utc).isoformat()
        if local_file is None:
            result = source_pipeline.acquire_url(
                url=doc["requested_pdf_url"], subject="TEST", bucket_id=BUCKET,
                resource_ref=source_id, acquired_at=acquired_at,
                snapshot_output=snapshot,
            )
        else:
            source = validate_local_source(local_file, workspace)
            result = source_pipeline.acquire_file(
                path=source, subject="TEST", bucket_id=BUCKET,
                resource_ref=source_id,
                requested_locator=doc["requested_pdf_url"],
                acquired_at=acquired_at, snapshot_output=snapshot,
            )
        require(snapshot.is_file(), "downloaded response is not a PDF")
        with snapshot.open("rb") as source_bytes:
            require(source_bytes.read(5) == b"%PDF-",
                    "downloaded response is not a PDF")
        if local_file is None:
            require(_same_host(doc["requested_pdf_url"], result["resolved_locator"]),
                    "unexpected cross-domain redirect")
        else:
            require(result["source_kind"] == "FILE"
                    and result["requested_locator"] == doc["requested_pdf_url"]
                    and result["resolved_locator"] == str(source),
                    "operator file import identity mismatch")
        require(source_pipeline.verify_acquisition(result, repo=REPO)["passed"],
                "downloaded source cannot be independently rehashed")
        _write_exclusive(receipt, json.dumps(result, indent=2) + "\n")
        status, findings = receipt_status(doc, workspace)
        require(status in {
            "VERIFIED_RETAINED_BYTES_ONLY",
            "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED",
        }, "persisted private receipt cannot be read back")
        return {"source_id": source_id, "status": status,
                "byte_length": result["byte_length"], "sha256": result["sha256"],
                "source_origin_authenticated": False,
                "core2_eligible": False, "core2_admitted": False}
    except BaseException:
        # Never leave a partial or invalid "success" snapshot behind.
        receipt.unlink(missing_ok=True)
        snapshot.unlink(missing_ok=True)
        raise
    finally:
        os.umask(old_mask)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("operation", choices=("report", "acquire"))
    p.add_argument("--private-dir", type=Path)
    p.add_argument("--source-id", choices=sorted(SOURCE_IDS))
    p.add_argument("--local-file", type=Path, help="manual local PDF import (provenance unverified)")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        census, handoff = load(CENSUS), load(HANDOFF)
        rows, docs = inventory(census, handoff)
        if args.operation == "acquire":
            require(args.private_dir is not None and args.source_id is not None,
                    "acquire requires --private-dir and exactly one --source-id")
            require(args.output is None, "acquisition output must stay private")
            workspace = private_workspace(args.private_dir, create=True)
            result = acquire(docs[args.source_id], workspace,
                             local_file=args.local_file)
        else:
            require(args.local_file is None,
                    "--local-file is valid only for explicitly selected acquire")
            require(args.source_id is None, "report cannot filter source denominator")
            workspace = (private_workspace(args.private_dir)
                         if args.private_dir else None)
            result = report(census, handoff, workspace)
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            print(payload, end="")
        return 0
    except (SourceGapError, OSError, ValueError) as exc:
        p.exit(1, f"IMO_SOURCE_GAPS_FAILED: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
