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
                and receipt.get("source_kind") == "URL"
                and receipt.get("resource_ref") == doc["source_id"]
                and receipt.get("requested_locator") == doc["requested_pdf_url"]
                and _same_host(doc["requested_pdf_url"], receipt.get("resolved_locator") or "")
                and receipt.get("snapshot_ref") == str(snapshot),
                "receipt/source identity mismatch")
        require(snapshot.open("rb").read(5) == b"%PDF-",
                "snapshot does not contain PDF header")
        outcome = source_pipeline.verify_acquisition(receipt, repo=REPO)
        require(outcome.get("passed") is True, "retained bytes or digest invalid")
        return "VERIFIED_RETAINED_BYTES_ONLY", []
    except (OSError, SourceGapError, ValueError, TypeError) as exc:
        # Public report deliberately doesn't print local file names or exception text.
        return "INVALID", ["RETAINED_DOCUMENT_RECEIPT_INVALID"]


def report(census: dict, handoff: dict, workspace: Path | None = None) -> dict:
    rows, docs = inventory(census, handoff)
    states = {sid: receipt_status(doc, workspace) for sid, doc in docs.items()}
    doc_rows = []
    for sid, doc in docs.items():
        status, findings = states[sid]
        doc_rows.append({
            "source_id": sid,
            "indexed_positions": SOURCE_IDS[sid],
            "receipt_status": status,
            "blocking_codes": findings,
            "source_rights": "NOT_REVIEWED",
            "independent_item_validation": "NOT_DONE",
        })
    question_rows = []
    for row in rows:
        status, doc_findings = states[row["source_id"]]
        codes = list(doc_findings)
        if row.get("source_locator_pdf_page_index") is None:
            codes.append("ITEM_PAGE_LOCATOR_UNOBSERVED")
        else:
            codes.append("ITEM_PAGE_OBSERVATION_NOT_COMPONENT_CUSTODY")
        codes.append("NINE_CUSTODY_COMPONENTS_UNVERIFIED")
        codes.append("PRINTED_KEY_AND_MATH_SPOT_CHECK_NOT_ACCEPTED")
        if row.get("material_source_discrepancy_hold"):
            codes.append("RECORDED_SOURCE_DISCREPANCY_OPEN")
        codes.extend(["SOURCE_REUSE_RIGHTS_NOT_REVIEWED",
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
            x["receipt_status"] == "VERIFIED_RETAINED_BYTES_ONLY" for x in doc_rows),
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


def acquire(doc: dict, workspace: Path) -> dict:
    """One explicitly requested document; never overwrite a prior private receipt."""
    source_id = doc["source_id"]
    snapshot, receipt = artifact_paths(workspace, source_id)
    require(not snapshot.exists() and not receipt.exists()
            and not snapshot.is_symlink() and not receipt.is_symlink(),
            "source snapshot/receipt already exists: refuse overwrite")
    old_mask = os.umask(0o077)
    try:
        result = source_pipeline.acquire_url(
            url=doc["requested_pdf_url"], subject="TEST", bucket_id=BUCKET,
            resource_ref=source_id,
            acquired_at=datetime.now(timezone.utc).isoformat(),
            snapshot_output=snapshot,
        )
        require(snapshot.is_file() and snapshot.open("rb").read(5) == b"%PDF-",
                "downloaded response is not a PDF")
        require(_same_host(doc["requested_pdf_url"], result["resolved_locator"]),
                "unexpected cross-domain redirect")
        require(source_pipeline.verify_acquisition(result, repo=REPO)["passed"],
                "downloaded source cannot be independently rehashed")
        _write_exclusive(receipt, json.dumps(result, indent=2) + "\n")
        return {"source_id": source_id, "status": "VERIFIED_RETAINED_BYTES_ONLY",
                "byte_length": result["byte_length"], "sha256": result["sha256"],
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
            result = acquire(docs[args.source_id], workspace)
        else:
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
