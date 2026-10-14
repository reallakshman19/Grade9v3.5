"""Validate the one reconciled administrative 7x4 QRT viewer.

This does NOT test native learner HTML, semantic academic criteria, or Owner approval.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "TEST/imo-research/qrt-tiles/reconciliation/index.html"
LEDGER = ROOT / "TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json"
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")


class ReconciledMatrixViewerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = VIEWER.read_text(encoding="utf-8")
        script = re.search(r'<script id="qrt-evidence" type="application/json">(.+?)</script>', cls.html, re.S)
        assert script, "viewer must embed current immutable, source-safe row projections"
        cls.rows = json.loads(script.group(1))
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))["rows"]

    def test_complete_current_28_cells(self):
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), 28)
        self.assertEqual(len(set(ids)), 28)
        self.assertEqual(set(ids), {f"QRT-{d}-D{b}" for d in DEMANDS for b in (1, 2, 3, 4)})
        self.assertEqual(set(ids), {r["cell_id"] for r in self.ledger})

    def test_exact_artifact_and_all_six_hashes_match_ledger(self):
        actual = {r["cell_id"]: r for r in self.ledger}
        for r in self.rows:
            with self.subTest(cell=r["id"]):
                p = actual[r["id"]]
                self.assertEqual(r["artifact"]["url"], p["artifact"]["url"])
                self.assertEqual(r["artifact"]["native_html_sha256"], p["artifact"]["native_html_sha256"])
                self.assertEqual(r["source"]["commit"], p["source"]["commit"])
                self.assertEqual(r["manifest"]["git_blob_sha"], p["manifest"]["git_blob_sha"])
                self.assertTrue(r["review_url"].startswith("https://github.com/reallakshman19/Grade9v3.5/"))

    def test_educational_holds_and_d3_source_watch_match_ledger(self):
        source = {r["cell_id"]: r for r in self.ledger}
        self.assertEqual(sum(bool(r["classification_hold"]) for r in self.rows),
                         sum(bool(r["critical_educational_review_hold"]) for r in self.ledger))
        for row in self.rows:
            with self.subTest(cell=row["id"]):
                expected = source[row["id"]]
                self.assertEqual(row["classification_hold"], expected["critical_educational_review_hold"])
                self.assertEqual(row["educational_hold_reason"], expected.get("educational_hold_reason"))
                self.assertEqual(row["source_supersession_watch"], expected.get("source_supersession_watch"))
        synth = next(r for r in self.rows if r["id"] == "QRT-SYNTHESIZE-D3")
        self.assertTrue(synth["classification_hold"])
        self.assertIn("a8168bb41f7133e40e3bcaa1389562361d68901e",
                      json.dumps(synth["source_supersession_watch"]))
        self.assertIn("New D3 source successor (CI-gated)", self.html)
        self.assertIn("Transfer closure is authored metadata", self.html)

    def test_not_falsely_adopted_or_source_exposed(self):
        self.assertIn("Original Q003", self.html)
        self.assertIn("Academic reviewer + conflict declaration", self.html)
        self.assertIn("Owner per-cell QRT decision ID", self.html)
        self.assertIn("Independent verdict pending", self.html)
        self.assertNotIn("6 rendered / 1 missing", self.html)
        self.assertNotIn("5 rendered / 2 missing", self.html)
        self.assertTrue(all(f'"{ask}"' in self.html for ask in ("H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3")))
        self.assertTrue(all(p["owner_qrta_accepted"] is False for p in self.ledger))
        self.assertTrue(all(p["owner_golden_designated"] is False for p in self.ledger))


if __name__ == "__main__":
    unittest.main()
