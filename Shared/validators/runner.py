#!/usr/bin/env python3
"""28-Tile Smart Validator Matrix Runner & Checkpoint Orchestrator.

Manages execution across the 4x7 grid (4 Bands x 7 Demands):
- Band Coordinate b in {1, 2, 3, 4} -> D1, D2, D3, D4
- Demand Coordinate d in {1, 2, 3, 4, 5, 6, 7} -> RETRIEVE, EXPLAIN, APPLY, MODEL, REPRESENT, SYNTHESIZE, JUSTIFY
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BANDS = ("D1", "D2", "D3", "D4")
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")

TILES_DIR = Path(__file__).parent / "tiles"


def get_tile_module_name(b: int, d: int) -> str:
    return f"Shared.validators.tiles.tile_{b}_{d}.validator"


def run_tile_audit(b: int, d: int, root: Path | None = None) -> dict[str, Any] | None:
    tile_id = f"tile_{b}_{d}"
    tile_path = TILES_DIR / tile_id
    if not tile_path.is_dir():
        return None

    mod_name = get_tile_module_name(b, d)
    try:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "audit_tile"):
            return mod.audit_tile(root_path=root)
    except Exception as e:
        return {
            "tile_id": tile_id,
            "error": str(e),
            "golden_status": "ERROR"
        }
    return None


def run_all_tiles(root: Path | None = None) -> dict[str, Any]:
    implemented: list[dict[str, Any]] = []
    pending: list[str] = []

    for b_idx, band in enumerate(BANDS, start=1):
        for d_idx, demand in enumerate(DEMANDS, start=1):
            tile_cell = f"QRT-{demand}-{band}"
            res = run_tile_audit(b_idx, d_idx, root)
            if res:
                implemented.append(res)
            else:
                pending.append(f"tile_{b_idx}_{d_idx} ({tile_cell})")

    pass_count = sum(1 for r in implemented if r.get("golden_status") == "PASS")
    fail_count = sum(1 for r in implemented if r.get("golden_status") == "FAIL")

    return {
        "schema": "imo-qrt-matrix-runner-receipt/v1",
        "total_cells": 28,
        "implemented_count": len(implemented),
        "pending_count": len(pending),
        "summary": {
            "pass": pass_count,
            "fail": fail_count
        },
        "implemented_tiles": implemented,
        "pending_tiles": pending,
        "academic_approval": "REVIEW_REQUIRED"
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tile", help="Coordinate 'b,d' (e.g. '1,1' or '1,7')")
    parser.add_argument("--json", action="store_true", help="Output full JSON")
    args = parser.parse_args(argv)

    if args.tile:
        parts = [int(p.strip()) for p in args.tile.replace(".", ",").split(",")]
        res = run_tile_audit(parts[0], parts[1])
        if not res:
            print(f"Tile {parts[0]},{parts[1]} not implemented yet.")
            return 1
        print(json.dumps(res, indent=2))
        return 0 if res.get("golden_status") == "PASS" else 1

    summary = run_all_tiles()
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Matrix Status: {summary['implemented_count']}/28 tiles implemented.")
        print(f"Golden Fixtures Passing: {summary['summary']['pass']}/{summary['implemented_count']}")
        print(f"Pending: {summary['pending_count']} tiles.")
    return 0 if summary["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
