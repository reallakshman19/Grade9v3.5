#!/usr/bin/env python3
"""Issue #217: provenance/structural native audit for five provisional D3 sources.

This is an engineering evidence generator. It CANNOT certify pedagogical
H/S/P/M, independent academic review, Owner acceptance or public rights.
Original #193 source and frozen golden are immutable input comparators.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "TEST/imo-research/qrt-d3-successor/m0-adoption.v1.json"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
REGISTRY = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
ROLES = ["CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"]
EXPECTED_BLUEPRINTS = {
    "CORE1": ("BP-CORE1-ORIENTATION", "1.1.0"),
    "CORE1A": ("BP-CORE1A-CONSTRUCTION", "1.8.0"),
    "CORE1B": ("BP-CORE1B-RECONSTRUCTION", "1.1.0"),
    "CORE2A": ("BP-CORE2A-SUPPORTED-APPLICATION", "1.1.0"),
    "CORE2B": ("BP-CORE2B-TRANSFER", "1.1.0"),
}
SLOT = re.compile(r'data-blueprint-slot="([^"]+)"')
ASKS = ["H1", "H2", "H3", "S1", "S2", "S3",
        "P1", "P2", "P3", "M1", "M2", "M3"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    require(path.is_file(), f"missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob(path: Path) -> str:
    require(path.is_file(), f"missing source: {path}")
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT, text=True
    ).strip()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inventory = load(CATALOG)
    sup = load(ROOT / "TEST/imo-research/qrt-d3-successor/synthesize-source-supersession.v1.json")
    require(sup["cell"] == "QRT-SYNTHESIZE-D3" and sup["source_fix_pr"] == 221
            and sup["original_source_head"] == inventory["pinned_source_head"],
            "source supersession authority does not match pinned M0")
    require(sup["qrt_accepted"] is False and sup["owner_qrt_decision_id"] is None,
            "source correction cannot accept QRT")
    expected_checkout = os.environ.get("EXPECTED_SOURCE_HEAD")
    if expected_checkout:
        checkout = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        require(checkout == expected_checkout,
                f"checkout {checkout} differs from PR source HEAD {expected_checkout}")
    expected_cells = [r["demand"] for r in inventory["all_7_cells"]]
    selection = inventory["build_selection"]
    require(len(expected_cells) == 7 and len(set(expected_cells)) == 7,
            "need exactly seven original cells")
    require(len(selection) == 5 and set(selection).isdisjoint(inventory["holds"]),
            "unadjudicated MODEL/RETRIEVE cannot enter this build")
    require(set(expected_cells) == set(selection) | set(inventory["holds"]),
            "source inventory must partition into build and hold")
    require(blob(REGISTRY) == inventory["blueprint_registry_git_blob"],
            "registered blueprint blob changed: re-triage before builds")
    require(blob(FROZEN / "snapshot-lock.json") == inventory["golden_lock_git_blob"],
            "original golden lock changed")
    registry = load(REGISTRY)
    require(registry["registry_version"] == "1.17.0", "new registry: stop")
    active = {(bp["id"], bp["version"]) for bp in registry["blueprints"]
              if bp.get("status") == "ACTIVE"}
    require(set(EXPECTED_BLUEPRINTS.values()).issubset(active),
            "registered five-role blueprint identity/version changed")

    lock = load(FROZEN / "snapshot-lock.json")
    require(lock["fixture_id"] == inventory["golden_id"], "wrong original golden")
    require(lock["status"] == "OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT",
            "golden status changed")
    require(len(lock["snapshots"]) == 5, "original five-role snapshots missing")
    originals = {}
    for item in lock["snapshots"]:
        golden_page = FROZEN / item["path"]
        require(digest(golden_page) == item["sha256"],
                f"frozen golden altered: {item['role']}")
        originals[item["role"]] = {
            "sha256": item["sha256"],
            "slots": SLOT.findall(golden_page.read_text(encoding="utf-8"))
        }
    require(set(originals) == set(ROLES), "golden five roles differ")

    records = []
    for row in inventory["all_7_cells"]:
        demand = row["demand"]
        src = ROOT / row["source_path"]
        manifest_file = ROOT / row["manifest_path"]
        actual_source_blob = blob(src)
        if demand == "synthesize":
            require(row["source_blob_sha"] == sup["original_source_blob_sha"]
                    and actual_source_blob == sup["corrected_source_blob_sha"],
                    "SYNTHESIZE: only pinned PR #221 source correction is authorized")
        else:
            require(actual_source_blob == row["source_blob_sha"],
                    f"{demand}: original source blob changed")
        require(blob(manifest_file) == row["manifest_blob_sha"],
                f"{demand}: original manifest blob changed")
        require(row["source_rights"] == "WHOLLY_AUTHORED_TEST_ONLY",
                f"{demand}: unexpected source classification")
        require(row["academic_reviewer"] is None
                and row["owner_decision_id"] is None
                and row["qrt_accepted"] is False, f"{demand}: false acceptance")
        require([row["academic_asks"].get(ask) for ask in ASKS]
                == ["PENDING"] * 12, f"{demand}: invented H/S/P/M")
        pack, manifest = load(src), load(manifest_file)
        require(manifest["output_roles"] == ROLES, f"{demand}: unexpected roles")
        require(manifest["selection"]["core2"] == [], f"{demand}: unauthorized CORE2")
        require(manifest["selection"]["core2a"] == [row["primary_id"]],
                f"{demand}: wrong primary")
        require(len(manifest["selection"]["core2b"]) == 1,
                f"{demand}: missing transfer")
        question = next((q for q in pack["questions"] if q["id"] == row["primary_id"]), None)
        require(question is not None and question["origin"] == "AUTHORED",
                f"{demand}: missing wholly authored primary")
        require(pack["extensions"]["grade9v3:qrt_admitted"] is False,
                f"{demand}: QRT admission unexpectedly changed")
        if demand == "synthesize":
            require(question["family_exposure"]["closure"] == sup["corrected_field_value"]
                    and "REPRESENT question" not in question["family_exposure"]["closure"],
                    "SYNTHESIZE: stale or unauthorized post-attempt learner label")
        require(pack["extensions"]["grade9v3:core2_source_custody_granted"] is False,
                f"{demand}: source rights changed")
        require(pack["extensions"]["grade9v3:learner_published"] is False,
                f"{demand}: publication unexpectedly changed")
        # Only representations selected by the actual five-role source package
        # are required. A legacy record may describe a different, unselected
        # question: retain its missing-asset finding without falsifying M1.
        selected_question_ids = (manifest["selection"]["core2a"]
                                 + manifest["selection"]["core2b"])
        selected_questions = [q for q in pack["questions"]
                              if q["id"] in selected_question_ids]
        selected_rep_refs = {
            ref for q in selected_questions for ref in q.get("figure_refs", [])
        }
        selected_micro_refs = set(manifest["selection"]["microtopics"])
        selected_rep_refs.update(
            ref for micro in pack["microtopics"]
            if micro["id"] in selected_micro_refs
            for ref in micro.get("representation_refs", [])
        )
        all_reps = {rep["id"]: rep for rep in pack["representations"]}
        require(selected_rep_refs.issubset(all_reps),
                f"{demand}: missing selected representation definition")
        for ref in selected_rep_refs:
            for asset in all_reps[ref].get("rendered_asset_refs", []):
                require((ROOT / asset).is_file(),
                        f"{demand}: selected SVG asset missing {asset}")
        unused_missing_assets = [
            asset for rep in pack["representations"]
            if rep["id"] not in selected_rep_refs
            for asset in rep.get("rendered_asset_refs", [])
            if not (ROOT / asset).is_file()
        ]
        record = {
            "cell": row["cell"], "status": row["status"],
            "source_path": row["source_path"], "source_blob_sha": actual_source_blob,
            "original_pr193_source_blob_sha": row["source_blob_sha"],
            "source_supersession": {
                "fix_pr": 221, "previous_artifact": "DO_NOT_ADOPT_ORIGINAL_SHA",
                "corrected_source_blob": actual_source_blob,
            } if demand == "synthesize" else None,
            "manifest_path": row["manifest_path"], "manifest_blob_sha": row["manifest_blob_sha"],
            "original_main_question_id": row["primary_id"],
            "original_transfer_question_id": manifest["selection"]["core2b"][0],
            "candidate_primary_demand": question["extensions"]["grade9v3:cognitive_demand"]["primary"],
            "candidate_band": question["difficulty"]["band"],
            "unselected_missing_asset_refs": unused_missing_assets,
            "academic_asks": {k: "PENDING" for k in ASKS},
            "principal_independence": "NONE", "academic_reviewer": None,
            "owner_decision_id": None, "qrt_accepted": False,
        }
        if demand not in selection:
            record["build"] = "SEMANTIC_HOLD_NO_RENDER"
            records.append(record)
            continue

        out = ROOT / "build/imo182-qrt/d3" / demand
        receipt_file = out / "render-receipt.json"
        receipt = load(receipt_file)
        pages = [r.lower() + ".html" for r in ROLES] + ["index.html"]
        require(receipt["renderer"] == "render_core/2", f"{demand}: wrong renderer")
        require(receipt["mode"] == "PAGES", f"{demand}: wrong mode")
        require(receipt["gaps"] == [], f"{demand}: render gaps {receipt['gaps']}")
        require(receipt["output_roles"] == ROLES, f"{demand}: receipt roles")
        require(receipt["pages"] == pages, f"{demand}: missing/extra native pages")
        actual = {}
        slots = {}
        for name in pages:
            path = out / name
            actual[name] = digest(path)
            require(actual[name] == receipt["page_sha256"][name],
                    f"{demand}/{name}: SHA differs from native receipt")
            if name != "index.html":
                role = name[:-5].upper()
                html = path.read_text(encoding="utf-8")
                bp_name, bp_version = EXPECTED_BLUEPRINTS[role]
                require(f'data-blueprint-ref="{bp_name}@{bp_version}"' in html,
                        f"{demand}/{name}: wrong registered blueprint")
                slots[name] = SLOT.findall(html)
                require(slots[name] == originals[role]["slots"],
                        f"{demand}/{name}: golden role/slot technique mismatch")
                require("data-g9-render-digest" in html,
                        f"{demand}/{name}: not marked by renderer")
                require(actual[name] != originals[role]["sha256"],
                        f"{demand}/{name}: unrelated golden coincidentally identical")
        core2a = (out / "core2a.html").read_text(encoding="utf-8")
        require("data-g9-after-attempt-hint" in core2a and
                "data-requires-attempt" in core2a,
                f"{demand}: H3 after-attempt markup missing")
        for role in ("core1b", "core2b"):
            html = (out / (role + ".html")).read_text(encoding="utf-8")
            require("data-g9-commit" in html and "data-requires-attempt" in html,
                    f"{demand}/{role}: independent attempt markup missing")
        record.update({
            "build": "NATIVE_RENDER_RECEIPT_AND_GOLDEN_SLOT_PASS",
            "page_sha256": actual, "render_receipt_sha256": digest(receipt_file),
            "renderer": receipt["renderer"], "mode": receipt["mode"],
            "reference_depth_gaps": len(receipt["gaps"]),
            "actual_role_slots": slots,
            "golden_comparator": inventory["golden_id"],
            "golden_lock_sha": inventory["golden_lock_git_blob"],
            "technique_status": "STRUCTURAL_ROLE_AND_SLOT_PARITY_ONLY__QUALIFIED_SEMANTICS_PENDING",
            "h2_h3_browser_status": "EXISTING_SCOPED_TESTS_RUN_SEPARATELY__M2_NOT_ADJUDICATED",
            "academic_review_status": "PENDING",
        })
        records.append(record)

    result = {
        "schema": "imo217-d3-m1-native-audit/v1",
        "issue": 217,
        "source_head_pinned": inventory["pinned_source_head"],
        "stacked_base_pinned": inventory["pinned_stacked_base"],
        "ci_checkout_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "ci_github_sha": os.environ.get("GITHUB_SHA"),
        "ci_event": os.environ.get("GITHUB_EVENT_NAME"),
        "branch_source_rights": "WHOLLY_AUTHORED_TEST_ONLY",
        "builds_passed": selection,
        "held_unrendered": inventory["holds"],
        "immutable_golden_original_sha256": {
            name: original["sha256"] for name, original in originals.items()},
        "evidence": records,
        "mathematics_and_browser": "SEE_EXECUTED_SCOPED_TEST_OUTPUT;_NOT_INDEPENDENT_QRT_REVIEW",
        "quality_claim": "M1_NATIVE_STRUCTURAL_ONLY",
        "independent_academic_review": "PENDING",
        "owner_accepted_cells": 0,
        "owner_decision_ids": None,
        "public_release": False,
    }
    target = ROOT / "build/imo182-qrt/d3-successor/m1-evidence.v1.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"M1 native audit PASS: 5 render receipts, 30 HTML SHA checks, 2 semantic holds; {target}")


if __name__ == "__main__":
    main()
