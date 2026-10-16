#!/usr/bin/env python3
"""Non-publishing Physics #289 proposed-source native preview.

Read a SHA-pinned *unapplied* #295 proposal, overlay one question in memory,
and render with the actual Shared renderer. Do not write Physics/library,
public/, docs/, golden/, or a release/canonical output.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from Shared.tools import render_core

QUESTION_ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"
ORIGINAL_BLOB = "62b8df106e83db03ac80fbb4002a611ac3d6e49a"
ORIGINAL_QUESTION_SHA = "32c5a4447dfdccf0de457ed6d07a12c448f995869699b02adeed2997feb76f50"
CANDIDATE_QUESTION_SHA = "fd6e5c259cff1b28d96ad76630df0549e0d7d0a893bc26fd50bdec19580fa15e"
PROPOSAL_COMMIT = "0a557b4929bd2d82920c6a8d2ae96fcb4d957f70"
ALLOWED_QUESTION_KEYS = {"stem", "conditions", "hints", "hint_ladder", "answer"}


def compact_sha(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def run(proposal_path: Path, out_dir: Path) -> dict:
    repo = render_core.REPO.resolve()
    out_dir = out_dir.resolve()
    build = (repo / "build").resolve()
    if not out_dir.is_relative_to(build):
        raise ValueError("ONLY_TEMPORARY_BUILD_DIR_ALLOWED")
    if any(out_dir.is_relative_to((repo / item).resolve()) for item in ("public", "docs", "golden")):
        raise ValueError("PUBLISHING_DIR_FORBIDDEN")
    source_path = repo / "Physics/library/phy-nlm-first-law.v1.json"
    source_before = source_path.read_bytes()
    if git_blob(source_before) != ORIGINAL_BLOB:
        raise ValueError("ORIGINAL_SOURCE_BLOB_DRIFT")
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    if proposal.get("source", {}).get("git_blob_sha") != ORIGINAL_BLOB:
        raise ValueError("PROPOSAL_SOURCE_NOT_PINNED")
    if proposal["source"]["question_sha256"] != ORIGINAL_QUESTION_SHA:
        raise ValueError("PROPOSAL_QUESTION_NOT_PINNED")
    if proposal["source"]["question_id"] != QUESTION_ID:
        raise ValueError("WRONG_PROPOSAL_QUESTION")
    if proposal["authority"]["source_write_authorized"] or proposal["authority"]["approval"] != "NOT_GRANTED":
        raise ValueError("NOT_AN_UNAPPROVED_TEST_ONLY_PROPOSAL")
    changes = proposal.get("patches", {})
    if set(changes) != ALLOWED_QUESTION_KEYS:
        raise ValueError("UNEXPECTED_PATCH_KEYS")

    manifest = repo / "products/physics/phy-nlm-first-law.manifest.json"
    unmodified_pages, old_gaps, old_render_digest = render_core.build(manifest, mode="PAGES")
    if "core2b.html" not in unmodified_pages:
        raise ValueError("REAL_CORE2B_PAGE_MISSING")

    ctx = render_core.context(manifest)
    matched = [q for p in ctx.packages for q in p.get("questions", []) if q.get("id") == QUESTION_ID]
    if len(matched) != 1:
        raise ValueError("TARGET_NOT_UNIQUE_IN_REAL_PRODUCT")
    original = copy.deepcopy(matched[0])
    if compact_sha(original) != ORIGINAL_QUESTION_SHA:
        raise ValueError("PRODUCT_QUESTION_IDENTITY_DRIFT")

    proposed = copy.deepcopy(original)
    for key in ("stem", "conditions", "hints", "hint_ladder"):
        proposed[key] = copy.deepcopy(changes[key])
    for key, value in changes["answer"].items():
        proposed["answer"][key] = copy.deepcopy(value)
    if compact_sha(proposed) != CANDIDATE_QUESTION_SHA:
        raise ValueError("RECONSTRUCTED_CANDIDATE_DRIFT")
    if proposed["transfer"] != original["transfer"]:
        raise ValueError("NOVELTY_CANNOT_BE_SILENTLY_RECLASSIFIED")

    # Mutate only deserialized JSON objects. Preserve the original object
    # identity where selection rows directly reference the package object.
    for selected in [*matched, *[q for q in ctx.selection_rows.get("core2b", [])
                                  if q.get("id") == QUESTION_ID]]:
        selected.clear()
        selected.update(copy.deepcopy(proposed))
    ctx.authority_hashes.append(("SIMULATED_UNAPPLIED_PR295_QUESTION", CANDIDATE_QUESTION_SHA))
    with patch.object(render_core, "context", return_value=ctx):
        candidate_pages, candidate_gaps, candidate_digest = render_core.build(manifest, mode="PAGES")
    if "core2b.html" not in candidate_pages:
        raise ValueError("CANDIDATE_CORE2B_PAGE_MISSING")
    if candidate_pages["core2b.html"] == unmodified_pages["core2b.html"]:
        raise ValueError("PROPOSAL_NOT_ACTUALLY_RENDERED")

    original_dir = out_dir / "original"
    candidate_dir = out_dir / "candidate"
    original_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    (original_dir / "core2b.html").write_text(unmodified_pages["core2b.html"], encoding="utf-8")
    (candidate_dir / "core2b.html").write_text(candidate_pages["core2b.html"], encoding="utf-8")
    if source_path.read_bytes() != source_before:
        raise ValueError("CANONICAL_SOURCE_CHANGED")
    report = {
        "schema": "physics-qrt.nlm289-native-preview/v1",
        "source_commit": "73c66b64158ee2ff57b099f990e1c2081d5c571f",
        "source_blob": ORIGINAL_BLOB,
        "proposal_commit": PROPOSAL_COMMIT,
        "proposal_question_sha": CANDIDATE_QUESTION_SHA,
        "original_question_sha": ORIGINAL_QUESTION_SHA,
        "original_render_digest": old_render_digest,
        "candidate_render_digest": candidate_digest,
        "original_core2b_html_sha256": hashlib.sha256(unmodified_pages["core2b.html"].encode()).hexdigest(),
        "candidate_core2b_html_sha256": hashlib.sha256(candidate_pages["core2b.html"].encode()).hexdigest(),
        "original_gaps": len(old_gaps),
        "candidate_gaps": len(candidate_gaps),
        "preview_only": True,
        "source_writer_authorized": False,
        "human_scientific_verdict": "NOT_ATTESTED",
        "new_transfer_verdict": "NOT_ESTABLISHED",
        "operational_grader_verdict": "NOT_IMPLEMENTED",
        "release": "HOLD",
    }
    (out_dir / "preview-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.proposal, args.out), indent=2))
