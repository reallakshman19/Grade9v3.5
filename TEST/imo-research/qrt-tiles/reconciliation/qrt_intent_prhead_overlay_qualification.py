#!/usr/bin/env python3
"""PR-head renderer candidate over the 21 independently SHA-pinned R8 TEST sources.

THIS IS A REVIEW-GATED HARNESS, NOT A GOLDEN UPDATE, OWNER ACCEPTANCE, OR RELEASE.
The old R8 21-cell original-source renderer run remains untouched. This distinct
manual-only qualification runs each pinned source in an isolated temporary git
worktree and overlays ONLY the current PR-head Shared/tools/render_core.py.
A count has NO admissible standing until Agent B checks this exact harness SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# Identical root/cell assignments to the pre-existing R8 P2b shell step.
CASES = (
    ("source-explain-d3", "explain-d3"),
    ("source-model-d2", "model-d2"),
    ("source-retrieve-d2", "retrieve-d2"),
    ("source-retrieve-d4", "retrieve-d4"),
    ("source-justify-d1", "justify-d1"),
    ("source-explain-d3", "retrieve-d3"),
    ("source-explain-d3", "model-d3"),
    ("source-d2-common", "explain-d2"),
    ("source-d2-common", "apply-d2"),
    ("source-d2-common", "synthesize-d2"),
    ("source-d2-common", "justify-d2"),
    ("source-explain-d3", "apply-d3"),
    ("source-explain-d3", "represent-d3"),
    ("source-d3-synthesize", "synthesize-d3"),
    ("source-explain-d3", "justify-d3"),
    ("source-d4-explain", "explain-d4"),
    ("source-d4-apply", "apply-d4"),
    ("source-d4-model", "model-d4"),
    ("source-d4-represent", "represent-d4"),
    ("source-d4-synthesize", "synthesize-d4"),
    ("source-d4-justify", "justify-d4"),
)
RECONCILIATION = Path("TEST/imo-research/qrt-tiles/reconciliation")
RENDERER = Path("Shared/tools/render_core.py")
WORKFLOW = Path(".github/workflows/imo182-r8-qrt-intent-contract.yml")


def call(args: list[str], *, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        # No copyrighted/learner question body is echoed into CI on failure.
        raise RuntimeError(
            f"qualifier subprocess exit {proc.returncode}: {args[0]} "
            f"{args[1] if len(args) > 1 else ''}"
        )
    return proc.stdout.strip()


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def verify_old_r8_assignments() -> None:
    """Fail if our mapping drifts from the existing, source-held R8 case list."""
    import re
    content = WORKFLOW.read_text(encoding="utf-8")
    start = content.index("- name: R8 P2b click actual native role routes")
    stop = content.index("- name: R8 P2c inspect all 21", start)
    rows = re.findall(r'"(source-[a-z0-9-]+)[|]([a-z0-9-]+)"', content[start:stop])
    if tuple(rows) != CASES or len(set(c for _, c in CASES)) != 21:
        raise AssertionError("PR_HEAD_CASE_MAP_DRIFT_FROM_FROZEN_R8")


def original_source_is_pinned(source: Path, witness: dict) -> None:
    pin = witness["source_pin"]
    if call(["git", "-C", str(source), "rev-parse", "HEAD"]) != pin["commit"]:
        raise AssertionError("SOURCE_COMMIT_CHANGED")
    for path_key, blob_key in (("source_path", "source_blob"),
                               ("manifest_path", "manifest_blob")):
        path = source / pin[path_key]
        if not path.is_file() or blob_sha(path) != pin[blob_key]:
            raise AssertionError("SOURCE_MANIFEST_OR_PACKAGE_BLOB_CHANGED")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_old_r8_assignments()
    witnesses = json.loads((RECONCILIATION / "qrt-intent-witnesses-pilot.v1.json")
                           .read_text(encoding="utf-8"))
    by_cell = {w["cell_id"]: w for w in witnesses["witnesses"]}
    if len(by_cell) != 28:
        raise AssertionError("ORIGINAL_QRT_28_WITNESSES_DRIFT")
    renderer = RENDERER.resolve()
    head = call(["git", "rev-parse", "HEAD"])
    renderer_digest = hashlib.sha256(renderer.read_bytes()).hexdigest()
    reports: list[dict] = []
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Isolated git worktrees preserve source checkouts and all original R8
    # native HTML, per-page render receipts and frozen golden SHA receipts.
    with tempfile.TemporaryDirectory(prefix="imo182-prhead-", dir=str(args.out.parent.resolve())) as td:
        temp = Path(td)
        overlays: dict[str, Path] = {}
        try:
            for root, slug in CASES:
                cid = "QRT-" + slug.upper()
                witness = by_cell[cid]
                original = Path(root).resolve()
                original_source_is_pinned(original, witness)
                expected_manifest = witness["source_pin"]["manifest_path"]
                if root not in overlays:
                    shadow = temp / root
                    call(["git", "-C", str(original), "worktree", "add",
                          "--detach", "-q", str(shadow), witness["source_pin"]["commit"]])
                    overlays[root] = shadow
                    (shadow / RENDERER).write_bytes(renderer.read_bytes())
                shadow = overlays[root]
                manifest = shadow / expected_manifest
                if blob_sha(manifest) != witness["source_pin"]["manifest_blob"]:
                    raise AssertionError("OVERLAY_MANIFEST_BLOB_CHANGED")
                if blob_sha(shadow / witness["source_pin"]["source_path"]) != (
                    witness["source_pin"]["source_blob"]
                ):
                    raise AssertionError("OVERLAY_QUESTION_SOURCE_BLOB_CHANGED")
                selected = json.loads(manifest.read_text(encoding="utf-8"))["selection"]
                if selected["core2a"] != [witness["primary_question_id"]]:
                    raise AssertionError("SELECTED_ORIGINAL_QUESTION_DRIFT")
                target = shadow / "build/imo182-qrt/prhead" / slug
                alternate = shadow / "build/imo182-qrt/prhead-repeat" / slug
                for where in (target, alternate):
                    call([sys.executable, str(shadow / RENDERER), "build",
                          "--manifest", expected_manifest, "--out", str(where),
                          "--mode", "PAGES", "--reference", "--draft"], cwd=shadow)
                candidate_contract = temp / (slug + "-prhead-native.json")
                call([sys.executable, str(RECONCILIATION / "qrt_intent_native_evidence.py"),
                      "--contract", str(Path("build/imo182-r8-intent") / (slug + ".json")),
                      "--source-root", str(shadow), "--native-output", str(target),
                      "--independent-rebuild", str(alternate), "--out", str(candidate_contract)])
                nav_path = temp / (slug + "-prhead-navigation.json")
                call([sys.executable, str(RECONCILIATION / "qrt_intent_real_navigation.py"),
                      "--native-contract", str(candidate_contract),
                      "--source-root", str(shadow), "--native-output", str(target),
                      "--out", str(nav_path)])
                nav = json.loads(nav_path.read_text(encoding="utf-8"))
                journey = nav["postcommit_native_journey"]
                observed = journey["observed"]
                if nav["cell_id"] != cid or journey["source_question_id"] != witness["primary_question_id"]:
                    raise AssertionError("PR_HEAD_SOURCE_QID_NOT_PINNED")
                if observed["independent_credit_claimed"]:
                    raise AssertionError("ASSISTED_RETURN_FALSE_INDEPENDENT_CREDIT")
                reports.append({
                    "cell_id": cid,
                    "source_commit": witness["source_pin"]["commit"],
                    "original_source_blob": witness["source_pin"]["source_blob"],
                    "original_manifest_blob": witness["source_pin"]["manifest_blob"],
                    "renderer_head_sha": head,
                    "renderer_sha256": renderer_digest,
                    "page_sha256": json.loads(candidate_contract.read_text(
                        encoding="utf-8"))["native_evidence"]["roles"]["CORE2A"]["native_sha256"],
                    "postcommit": {k: bool(observed[k]) for k in (
                        "attempt_blank_rejected", "nonempty_attempt_committed",
                        "precommit_solution_locked", "postcommit_context_link_present",
                        "context_link_is_pinned", "concept_reached", "concept_is_pinned",
                        "return_link_present", "return_link_is_pinned",
                        "same_question_reached", "attempt_text_restored",
                        "assistance_marked", "independent_credit_claimed")},
                    "candidate_round_trip": bool(journey["technical_round_trip_complete"]),
                    "finding_codes": list(journey["findings"]),
                    "academic_acceptance": False,
                    "owner_acceptance": False,
                })
                original_source_is_pinned(original, witness)
        finally:
            for root, shadow in overlays.items():
                call(["git", "-C", str(Path(root).resolve()), "worktree", "remove",
                      "--force", str(shadow)])
    if len(reports) != 21 or len({r["cell_id"] for r in reports}) != 21:
        raise AssertionError("PR_HEAD_EXACTLY_21_UNIQUE_CASES_REQUIRED")
    held = set(by_cell) - {r["cell_id"] for r in reports}
    if len(held) != 7:
        raise AssertionError("SOURCE_HELD_SEVEN_MUST_REMAIN_HELD")
    result = {
        "schema": "imo182-prhead-overlay-candidate/v1",
        "disposition": "PROVISIONAL_NO_COUNTS_BEFORE_AGENT_B_EXACT_COMMIT_PASS",
        "renderer_head_sha": head,
        "renderer_sha256": renderer_digest,
        "historical_r8_and_frozen_golden_unchanged": True,
        "source_pinned_original_cells": 21,
        "source_held_no_candidate_render": sorted(held),
        "academic_accepted": 0,
        "owner_qrt_accepted": 0,
        "release": "HOLD",
        "cells": reports,
    }
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("PRHEAD R14 candidate generated; NOT ADMISSIBLE until Agent B PASS "
          "on exact harness SHA; source/golden unmodified; academic/Owner HOLD")


if __name__ == "__main__":
    main()
