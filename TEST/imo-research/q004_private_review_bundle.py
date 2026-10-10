#!/usr/bin/env python3
"""Prepare private, hash-bound source-page images for Q004 human inspection.

Consumes only an already-acquired PDF in the restricted workspace maintained by
core2_source_acquisition_gaps.py. Never sends PDF bytes, page images, source
wording, options, or assessment files to GitHub/CI. No source, rights, academic,
QRT or Core2 admission is granted by this operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from core2_source_acquisition_gaps import (
    CENSUS, HANDOFF, SourceGapError, artifact_paths, inventory, load,
    private_workspace, receipt_status, require,
)
from q004_private_spotcheck import DOC_ID, QID, ITEM_PAGE, KEY_PAGE, make_template

REVIEW_DIR = "q004-private-review"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 20 * 1024 * 1024


def _write_json_private(path: Path, value: dict) -> None:
    """Create a new private JSON file; never overwrite an inspection record."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        json.dump(value, out, indent=2, sort_keys=True)
        out.write("\n")


def _render_page(pdf: Path, page_zero_based: int, output: Path) -> None:
    """Invoke poppler without shell interpolation, writing only inside 0700 dir."""
    renderer = shutil.which("pdftoppm")
    require(renderer is not None, "pdftoppm is required for private review")
    stem = output.with_suffix("")
    try:
        done = subprocess.run(
            [renderer, "-f", str(page_zero_based + 1),
             "-l", str(page_zero_based + 1), "-singlefile", "-png",
             "-scale-to", "1600", str(pdf), str(stem)],
            check=False, capture_output=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SourceGapError("private source-page rendering failed or timed out") from exc
    require(done.returncode == 0 and output.is_file() and not output.is_symlink(),
            "private source-page rendering failed; inspect PDF locally")
    require(8 < output.stat().st_size <= MAX_PNG_BYTES,
            "rendered source-page image size is invalid")
    with output.open("rb") as f:
        require(f.read(8) == PNG_MAGIC, "rendered review file is not a PNG")
    output.chmod(0o600)


def prepare(workspace: Path) -> dict:
    """Render two pages and create an *unchecked* hash-bound assessment packet.

    All products remain in the preexisting private workspace. An imported local
    PDF may be inspected, but its source origin is explicitly NOT authenticated.
    """
    workspace = private_workspace(workspace)
    _, documents = inventory(load(CENSUS), load(HANDOFF))
    document = documents[DOC_ID]
    status, _ = receipt_status(document, workspace)
    require(status in {
        "VERIFIED_RETAINED_BYTES_ONLY",
        "IMPORTED_LOCAL_BYTES_ONLY_SOURCE_ORIGIN_UNVERIFIED",
    }, "valid private retained source PDF and digest required before review")
    snapshot, _ = artifact_paths(workspace, DOC_ID)
    template = make_template(workspace)
    require(template["question_id"] == QID
            and template["source_id"] == DOC_ID
            and template["snapshot_sha256"] is not None
            and template["snapshot_byte_length"] == snapshot.stat().st_size
            and template["source_page_index"] == ITEM_PAGE
            and template["source_key_page_index"] == KEY_PAGE
            and all(v == "NOT_CHECKED"
                    for v in template["source_components"].values())
            and template["core2_admitted"] is False,
            "inspection packet identity or held statuses are inconsistent")
    target = workspace / REVIEW_DIR
    require(not target.exists() and not target.is_symlink(),
            "private Q004 review already exists; never overwrite prior evidence")
    old_mask = os.umask(0o077)
    try:
        target.mkdir(mode=0o700)
        try:
            pages = []
            for page, name in (
                (ITEM_PAGE, "source-question-page.png"),
                (KEY_PAGE, "source-answer-key-page.png"),
            ):
                out = target / name
                _render_page(snapshot, page, out)
                h = hashlib.sha256(out.read_bytes()).hexdigest()
                pages.append({
                    "pdf_page_index_zero_based": page,
                    "private_filename": name,
                    "image_sha256": h,
                    "purpose": "VISUAL_SELF_INSPECTION_ONLY",
                })
            _write_json_private(target / "q004.inspection.json", template)
            _write_json_private(target / "review-manifest.json", {
                "schema": "imo-g9-q004-private-visual-inspection-bundle-v1",
                "question_id": QID,
                "source_id": DOC_ID,
                "source_pdf_sha256": template["snapshot_sha256"],
                "source_pdf_byte_length": template["snapshot_byte_length"],
                "source_retention_status": status,
                "source_version_comparison": template["historical_version_comparison"],
                "images": pages,
                "component_dispositions_completed": 0,
                "source_origin_authenticated": False,
                "independent_reviewer_approved": False,
                "rights_granted": False,
                "core2_eligible": False,
                "core2_admitted": False,
                "learner_published": False,
            })
        except BaseException:
            shutil.rmtree(target)
            raise
    finally:
        os.umask(old_mask)
    return {
        "status": "PRIVATE_INSPECTION_READY_NOT_ADMITTED",
        "question_id": QID,
        "source_retention_status": status,
        "private_page_count": 2,
        "component_dispositions_completed": 0,
        "core2_admitted": False,
        "source_rights_granted": False,
        "instruction": (
            "Open both PNGs privately; complete q004.inspection.json after "
            "comparing the actual retained PDF. Run q004_private_spotcheck.py "
            "verify with the private workspace. Never commit files in this directory."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--private-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = prepare(args.private_dir)
    except (SourceGapError, OSError, ValueError) as exc:
        parser.exit(1, "IMO_Q004_PRIVATE_REVIEW_FAILED: " + str(exc) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
