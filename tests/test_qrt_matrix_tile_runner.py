#!/usr/bin/env python3
"""Tests for the 4x7 QRT matrix tile runner (qrt_matrix_tile_runner.py)."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
from Shared.tools.qrt_matrix_tile_runner import (
    parse_tile_coord,
    tile_cell_name,
    inspect_grid_occupancy,
    execute_tile_questions,
)


class TestQRTMatrixTileRunner(unittest.TestCase):
    """Test suite for 4x7 QRT Matrix tile coordinate parsing and execution."""

    def setUp(self) -> None:
        self.hosted_core2 = REPO / "public" / "test" / "imo-grade9" / "core2.html"
        self.master_suite = REPO / "standalone" / "mathematics-imo-grade9-master-suite.html"

    def test_parse_tile_coord_numeric(self) -> None:
        b, d, band, demand = parse_tile_coord("2,7")
        self.assertEqual((b, d), (2, 7))
        self.assertEqual(band, "D2")
        self.assertEqual(demand, "JUSTIFY")

    def test_parse_tile_coord_named(self) -> None:
        b, d, band, demand = parse_tile_coord("D3,MODEL")
        self.assertEqual((b, d), (3, 4))
        self.assertEqual(band, "D3")
        self.assertEqual(demand, "MODEL")

    def test_parse_tile_coord_dot_notation(self) -> None:
        b, d, band, demand = parse_tile_coord("1.3")
        self.assertEqual((b, d), (1, 3))
        self.assertEqual(band, "D1")
        self.assertEqual(demand, "APPLY")

    def test_tile_cell_name(self) -> None:
        self.assertEqual(tile_cell_name(2, 7), "QRT-JUSTIFY-D2")
        self.assertEqual(tile_cell_name(4, 6), "QRT-SYNTHESIZE-D4")
        self.assertEqual(tile_cell_name(1, 1), "QRT-RETRIEVE-D1")

    def test_inspect_grid_occupancy_core2(self) -> None:
        if not self.hosted_core2.is_file():
            self.skipTest("core2.html not found")
        res = inspect_grid_occupancy(self.hosted_core2)
        self.assertEqual(res["total_cells"], 28)
        self.assertGreaterEqual(res["total_questions"], 68)
        self.assertGreater(res["occupied_cells"], 10)
        self.assertIn("QRT-APPLY-D2", res["grid"])
        self.assertEqual(res["grid"]["QRT-APPLY-D2"]["coord"], "(2, 3)")

    def test_inspect_grid_occupancy_master_suite(self) -> None:
        if not self.master_suite.is_file():
            self.skipTest("master suite not found")
        res = inspect_grid_occupancy(self.master_suite)
        self.assertEqual(res["total_cells"], 28)
        self.assertGreaterEqual(res["total_questions"], 184)
        self.assertGreaterEqual(res["occupied_cells"], 18)
        self.assertGreaterEqual(res["grid"]["QRT-JUSTIFY-D2"]["question_count"], 6)


if __name__ == "__main__":
    unittest.main()
