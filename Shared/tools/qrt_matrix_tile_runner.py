#!/usr/bin/env python3
"""4x7 QRT Matrix Tile-by-Tile Runner & Inter-Core Checkpoint Orchestrator.

Manages the 28-cell grid (4 Bands x 7 Demands):
- Band Coordinate b in {1, 2, 3, 4} -> D1, D2, D3, D4
- Demand Coordinate d in {1, 2, 3, 4, 5, 6, 7} -> RETRIEVE, EXPLAIN, APPLY, MODEL, REPRESENT, SYNTHESIZE, JUSTIFY
Tile coordinate (b, d) maps to QRT-{DEMAND}-{BAND}.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any
from collections import defaultdict

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.audit_core_against_qrt import (
    audit_core2_question_card,
    audit_core1a_section,
    audit_core1b_section,
    audit_item_inter_core_checkpoint,
    load_json,
    QRT_MATRIX_PATH,
    DEFAULT_HOSTED_PAGE,
    DEFAULT_CORE1A_PAGE,
    DEFAULT_CORE1B_PAGE,
    VALID_DEMANDS,
    VALID_BANDS,
)

BANDS_ORDER = ("D1", "D2", "D3", "D4")
DEMANDS_ORDER = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")

BAND_TO_INT = {b: i + 1 for i, b in enumerate(BANDS_ORDER)}
INT_TO_BAND = {i + 1: b for i, b in enumerate(BANDS_ORDER)}

DEMAND_TO_INT = {d: i + 1 for i, d in enumerate(DEMANDS_ORDER)}
INT_TO_DEMAND = {i + 1: d for i, d in enumerate(DEMANDS_ORDER)}


def parse_tile_coord(tile_str: str) -> tuple[int, int, str, str]:
    """Parse '2,7' or '2.7' or 'D2,JUSTIFY' into (b_idx, d_idx, band, demand)."""
    cleaned = tile_str.strip().upper().replace(".", ",").replace("-", ",")
    if "," in cleaned:
        parts = [p.strip() for p in cleaned.split(",", 1)]
    else:
        parts = [cleaned[0], cleaned[1:]]

    p1, p2 = parts[0], parts[1]

    # Resolve band
    if p1.isdigit():
        b_idx = int(p1)
        if b_idx not in INT_TO_BAND:
            raise ValueError(f"Invalid band index: {b_idx}. Must be 1..4.")
        band = INT_TO_BAND[b_idx]
    elif p1 in BAND_TO_INT:
        band = p1
        b_idx = BAND_TO_INT[band]
    else:
        raise ValueError(f"Cannot resolve band from '{p1}'. Expected 1..4 or D1..D4.")

    # Resolve demand
    if p2.isdigit():
        d_idx = int(p2)
        if d_idx not in INT_TO_DEMAND:
            raise ValueError(f"Invalid demand index: {d_idx}. Must be 1..7.")
        demand = INT_TO_DEMAND[d_idx]
    elif p2 in DEMAND_TO_INT:
        demand = p2
        d_idx = DEMAND_TO_INT[demand]
    else:
        # Partial match
        matched = [d for d in DEMANDS_ORDER if d.startswith(p2)]
        if len(matched) == 1:
            demand = matched[0]
            d_idx = DEMAND_TO_INT[demand]
        else:
            raise ValueError(f"Cannot resolve demand from '{p2}'. Expected 1..7 or {DEMANDS_ORDER}.")

    return b_idx, d_idx, band, demand


def tile_cell_name(b_idx: int, d_idx: int) -> str:
    return f"QRT-{INT_TO_DEMAND[d_idx]}-{INT_TO_BAND[b_idx]}"


def inspect_grid_occupancy(html_path: Path) -> dict[str, Any]:
    """Scan HTML question suite and report complete 4x7 grid occupancy."""
    raw_html = html_path.read_text(encoding="utf-8")
    articles = re.findall(r'<article class="qb-question"(.*?)</article>', raw_html, re.DOTALL)

    grid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    topic_in_grid: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for idx, art in enumerate(articles):
        clean = html.unescape(art)
        search_m = re.search(r'data-search="([^"]+)"', clean)
        qid = search_m.group(1).split()[0] if search_m else f"Q{idx+1:03d}"
        band_m = re.search(r'data-band="([^"]+)"', clean)
        demand_m = re.search(r'data-demand="([^"]+)"', clean)
        topic_m = re.search(r'data-topic="([^"]+)"', clean)
        title_m = re.search(r'<h2 class="qb-title">([^<]+)</h2>', clean)

        band = band_m.group(1).strip() if band_m else "D?"
        demand = demand_m.group(1).strip() if demand_m else "UNKNOWN"
        topic = topic_m.group(1).strip() if topic_m else "Unclassified"
        title = title_m.group(1).strip() if title_m else qid

        cell = f"QRT-{demand}-{band}"
        b_idx = BAND_TO_INT.get(band, 0)
        d_idx = DEMAND_TO_INT.get(demand, 0)
        coord = f"({b_idx}, {d_idx})"

        item = {
            "qid": qid,
            "title": title,
            "topic": topic,
            "band": band,
            "demand": demand,
            "coord": coord,
            "raw_art": art,
        }
        grid[cell].append(item)
        topic_in_grid[cell][topic] += 1

    # Build 4x7 matrix table
    matrix_cells: dict[str, dict[str, Any]] = {}
    occupied_count = 0
    total_questions = len(articles)

    for b_idx, b in enumerate(BANDS_ORDER, 1):
        for d_idx, d in enumerate(DEMANDS_ORDER, 1):
            cell = f"QRT-{d}-{b}"
            items = grid.get(cell, [])
            count = len(items)
            if count > 0:
                occupied_count += 1
            matrix_cells[cell] = {
                "coord": f"({b_idx}, {d_idx})",
                "band_idx": b_idx,
                "demand_idx": d_idx,
                "band": b,
                "demand": d,
                "cell": cell,
                "question_count": count,
                "questions": [it["qid"] for it in items],
                "topics": dict(topic_in_grid[cell]),
            }

    return {
        "suite_path": str(html_path),
        "total_questions": total_questions,
        "occupied_cells": occupied_count,
        "total_cells": 28,
        "coverage_percentage": round(occupied_count / 28 * 100, 2),
        "grid": matrix_cells,
    }


def print_grid_table(grid_report: dict[str, Any]) -> None:
    print(f"\n=========================================================================================")
    print(f"                 4 x 7 QRT MATRIX OCCUPANCY REPORT (28 CELLS)                            ")
    print(f"  Suite Target: {grid_report['suite_path']}")
    print(f"  Total Questions: {grid_report['total_questions']} | Occupied Cells: {grid_report['occupied_cells']}/28 ({grid_report['coverage_percentage']}%)")
    print(f"=========================================================================================")

    # Table header
    header = f"{'Band':<6} | " + " | ".join([f"{d[:7]:<7} ({i+1})" for i, d in enumerate(DEMANDS_ORDER)])
    print(header)
    print("-" * len(header))

    grid = grid_report["grid"]
    for b_idx, b in enumerate(BANDS_ORDER, 1):
        row_str = f"{b:<6} | "
        cols = []
        for d_idx, d in enumerate(DEMANDS_ORDER, 1):
            cell = f"QRT-{d}-{b}"
            cnt = grid[cell]["question_count"]
            cols.append(f"{cnt:^11}" if cnt > 0 else f"{'.':^11}")
        print(row_str + " | ".join(cols))
    print("-" * len(header))


def execute_tile_questions(
    b_idx: int,
    d_idx: int,
    html_path: Path,
    core1a_path: Path | None = None,
    core1b_path: Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Settle an entire Tile (b, d) by executing question-by-question inter-checks."""
    band = INT_TO_BAND[b_idx]
    demand = INT_TO_DEMAND[d_idx]
    target_cell = f"QRT-{demand}-{band}"

    grid_report = inspect_grid_occupancy(html_path)
    tile_info = grid_report["grid"].get(target_cell, {})
    qids = tile_info.get("questions", [])

    print(f"\n=======================================================")
    print(f"   SETTLING TILE ({b_idx}, {d_idx}) -> [{target_cell}]")
    print(f"   Target Demand: {demand} | Target Band: {band}")
    print(f"   Question Count in Tile: {len(qids)}")
    print(f"=======================================================")

    results: list[dict[str, Any]] = []
    passed = 0
    flagged = 0
    misclassified = 0

    qrt_matrix = load_json(QRT_MATRIX_PATH)
    cell_spec = qrt_matrix.get("demands", {}).get(demand, {})
    band_policy = qrt_matrix.get("band_policies", {}).get(band, {})

    for idx, qid in enumerate(qids, 1):
        print(f"\n--- [{idx}/{len(qids)}] Running Inter-Core Checkpoint on {qid} ---")
        item_res = audit_item_inter_core_checkpoint(qid, html_path, core1a_path, core1b_path)
        verdict = item_res.get("item_checkpoint_verdict")
        delta = item_res.get("overall_item_delta_qrt", 1.0)
        c2 = item_res.get("core2_details", {})
        title = c2.get("title", qid)
        topic = c2.get("topic", "Unknown")

        # Academic Check: Validate if the question's decisive move genuinely belongs to this demand
        misclass_reason: str | None = None
        suggested_remap: str | None = None

        if demand == "JUSTIFY":
            # Justify requires establishing a conclusion from explicit warrants, counterexamples, or theorems
            trap_text = card_trap = ""
            if "raw_art" in c2:
                trap_text = c2["raw_art"]
            # Look for computational-only indicators
            if any(term in title.lower() for term in ["evaluate", "compute value", "find numerical", "direct calculation"]):
                misclass_reason = "Question is pure numerical evaluation; lacks claim-to-warrant justification structure."
                suggested_remap = f"QRT-APPLY-{band}"

        elif demand == "MODEL":
            # Model requires choosing or formulating variables, constraints, or governing equations
            if "solve direct" in title.lower():
                misclass_reason = "Equation already formulated in stem; does not demand model formulation."
                suggested_remap = f"QRT-APPLY-{band}"

        status_label = verdict
        if misclass_reason:
            status_label = "CORE2_MISMAPPED"
            misclassified += 1
            print(f"  ⚠️  Core 2 Mismapping Detected: {misclass_reason}")
            print(f"      Recommended Remap: {suggested_remap}")
        elif verdict == "PASS":
            passed += 1
            print(f"  ✅  PASS (Delta: {delta})")
        else:
            flagged += 1
            print(f"  ⚠️  {verdict} (Delta: {delta})")
            for cp_key, cp in item_res.get("checkpoints", {}).items():
                if cp.get("status") not in ("PASS",):
                    print(f"      - {cp.get('name')}: {cp.get('status')} -> {cp.get('findings', [])}")

        results.append({
            "qid": qid,
            "title": title,
            "topic": topic,
            "verdict": status_label,
            "delta_qrt": delta,
            "misclassification_detected": bool(misclass_reason),
            "misclass_reason": misclass_reason,
            "suggested_remap": suggested_remap,
            "checkpoint_details": item_res.get("checkpoints", {}),
        })

    summary = {
        "tile_coord": f"({b_idx}, {d_idx})",
        "cell": target_cell,
        "band": band,
        "demand": demand,
        "total_items": len(qids),
        "passed": passed,
        "flagged": flagged,
        "misclassified": misclassified,
        "settled": (passed == len(qids) and len(qids) > 0),
        "questions": results,
    }

    print(f"\n=======================================================")
    print(f"   TILE ({b_idx}, {d_idx}) SETTLEMENT SUMMARY")
    print(f"   Total: {len(qids)} | Passed: {passed} | Flagged: {flagged} | Mismapped: {misclassified}")
    print(f"=======================================================")

    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_HOSTED_PAGE, help="Path to HTML question suite")
    parser.add_argument("--core1a", type=Path, default=DEFAULT_CORE1A_PAGE, help="Path to core1a.html")
    parser.add_argument("--core1b", type=Path, default=DEFAULT_CORE1B_PAGE, help="Path to core1b.html")
    parser.add_argument("--grid", action="store_true", help="Print full 4x7 grid occupancy report")
    parser.add_argument("--tile", type=str, default=None, help="Execute specific tile e.g. '2,7' or 'D2,JUSTIFY'")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any item fails")
    args = parser.parse_args(argv)

    if args.grid or not args.tile:
        report = inspect_grid_occupancy(args.html)
        print_grid_table(report)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"Grid report written to {args.output}")
        if not args.tile:
            return 0

    if args.tile:
        b_idx, d_idx, band, demand = parse_tile_coord(args.tile)
        tile_summary = execute_tile_questions(b_idx, d_idx, args.html, args.core1a, args.core1b, args.strict)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(tile_summary, indent=2), encoding="utf-8")
            print(f"Tile settlement receipt written to {args.output}")

        if args.strict and (tile_summary["flagged"] > 0 or tile_summary["misclassified"] > 0):
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
