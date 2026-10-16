#!/usr/bin/env python3
"""Read-only #182 crosswalk: 28 QRT semantics reuse five Core role blueprints.

Source is the existing TEST ledger. No new blueprint, page render, golden, human
academic attestation or Owner QRT acceptance is conferred by this inventory.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMPLATE = "Shared/quality/question-demand-templates.v1.json"
BLUEPRINT = "Shared/web/interactive-page-blueprints.v1.json"
LEDGER = "TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json"
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")
ROLES = ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
ASKS = ("H1", "H2", "H3", "S1", "S2", "S3", "P1", "P2", "P3", "M1", "M2", "M3")


class MapBlocked(ValueError):
    pass


def demand(ok, why):
    if not ok:
        raise MapBlocked(why)


def read(root, path):
    return json.loads((root / path).read_text(encoding="utf-8"))


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def compile_map(templates, blueprints, ledger, blueprint_sha):
    demand(templates.get("schema") == "question-demand-templates/v1", "TEMPLATE_SCHEMA")
    demand(ledger.get("schema") == "imo182-r5-01-reconciled-28-native-artifact-evidence/v1",
           "LEDGER_SCHEMA")
    demand(ledger.get("frozen_blueprint_registry_sha") == blueprint_sha,
           "BLUEPRINT_REGISTRY_STALE")
    expected = {f"QRT-{d}-{b}" for d in DEMANDS for b in BANDS}
    ts = templates.get("templates", [])
    rows = ledger.get("rows", [])
    tids = [t.get("template_id") for t in ts]
    rids = [r.get("cell_id") for r in rows]
    demand(len(tids) == 28 and len(set(tids)) == 28 and set(tids) == expected,
           "28_TEMPLATE_IDS_REQUIRED")
    demand(len(rids) == 28 and len(set(rids)) == 28 and set(rids) == expected,
           "28_LEDGER_ROWS_REQUIRED")
    for t in ts:
        demand(t["template_id"] == f"QRT-{t.get('demand')}-{t.get('band')}",
               "TEMPLATE_DEMAND_BAND_MISMATCH")
        demand(tuple(t.get("review", {})) == ASKS, "12_REVIEW_ASKS_REQUIRED")

    bps = blueprints.get("blueprints", [])
    by_role = {}
    for bp in bps:
        for role in bp.get("core_roles", []):
            demand(role not in by_role, "DUPLICATE_BLUEPRINT_ROLE")
            demand(bp.get("status") == "ACTIVE" and bp.get("id") and bp.get("version"),
                   "INACTIVE_BLUEPRINT")
            by_role[role] = bp["id"] + "@" + bp["version"]
    demand(set(ROLES + ("CORE2", "EXPLORER")).issubset(by_role),
           "REQUIRED_REGISTERED_BLUEPRINT_MISSING")

    by_id = {r["cell_id"]: r for r in rows}
    out = []
    for t in ts:
        cell = t["template_id"]
        row = by_id[cell]
        demand((t["demand"], t["band"]) == (row.get("demand"), row.get("band")),
               "TEMPLATE_LEDGER_CLASSIFICATION_DRIFT:" + cell)
        src, man = row["source"], row["manifest"]
        for item in (src, man):
            demand(item.get("path", "").startswith("TEST/") and
                   bool(re.fullmatch(r"[0-9a-f]{40}", item.get("git_blob_sha", ""))),
                   "TEST_SOURCE_OR_MANIFEST_CUSTODY:" + cell)
        demand(bool(re.fullmatch(r"[0-9a-f]{40}", src.get("commit", ""))) and
               src.get("classification") == "AUTHORED_TEST_ONLY",
               "NOT_TEST_SOURCE:" + cell)
        sha = row["artifact"]["native_html_sha256"]
        required = {r.lower() + ".html" for r in ROLES} | {"index.html"}
        demand(set(sha) == required and all(
            bool(re.fullmatch(r"[0-9a-f]{64}", v)) for v in sha.values()),
            "SIX_HTML_DIGESTS_REQUIRED:" + cell)
        demand(row.get("owner_qrta_accepted") is False and
               row.get("owner_golden_designated") is False and
               row.get("release_authorized") is False and
               row.get("qualified_independent_signed_verdict_id") is None,
               "UNSUPPORTED_OWNER_OR_ACADEMIC_APPROVAL:" + cell)
        out.append({
            "cell": cell,
            "semantic_template": TEMPLATE + "#" + cell,
            "question_specific_X_Y_Z_W": "NOT_RESOLVED_WITHOUT_REAL_LEARNER_PROFILE",
            "source": {k: src[k] for k in ("path", "commit", "git_blob_sha")},
            "manifest": {k: man[k] for k in ("path", "git_blob_sha")},
            "native_core_roles": [
                {"role": role, "registered_blueprint": by_role[role],
                 "filename": role.lower() + ".html",
                 "archived_html_sha256": sha[role.lower() + ".html"]}
                for role in ROLES
            ],
            "index_html_sha256": sha["index.html"],
            "archived_artifact_url": row["artifact"]["url"],
            "evidence_kind": "LEDGER_HASHES_NOT_INDEPENDENTLY_RECOMPUTED",
            "elevated_educational_hold": bool(row.get("critical_educational_review_hold")),
            "academic_review": "QUALIFIED_INDEPENDENT_REVIEW_PENDING",
            "owner_acceptance": "NOT_GRANTED",
            "release": "HOLD",
        })
    return {
        "schema": "imo182-qrt-reusable-blueprint-crosswalk/v1",
        "source_ledger": LEDGER, "template_registry": TEMPLATE,
        "blueprint_registry": BLUEPRINT, "blueprint_git_blob": blueprint_sha,
        "summary": {"semantic_cells": 28, "registered_blueprints": len(bps),
                    "five_reused_core_blueprints_per_cell": 5,
                    "recorded_core_html_files": 140, "recorded_index_html_files": 28,
                    "elevated_educational_holds": sum(r["elevated_educational_hold"] for r in out),
                    "qualified_or_owner_accepted": 0},
        "generates_new_page_or_blueprint": False,
        "cells": out,
    }


def run(root):
    return compile_map(read(root, TEMPLATE), read(root, BLUEPRINT),
                       read(root, LEDGER), git_blob((root / BLUEPRINT).read_bytes()))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--cell")
    args = p.parse_args()
    try:
        result = run(args.root)
        if args.cell:
            result["cells"] = [r for r in result["cells"] if r["cell"] == args.cell]
            demand(len(result["cells"]) == 1, "UNKNOWN_QRT_CELL")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (MapBlocked, KeyError, OSError, ValueError, TypeError) as err:
        print(json.dumps({"status": "BLOCKED", "error": str(err),
                          "owner_acceptance": "NOT_GRANTED", "release": "HOLD"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
