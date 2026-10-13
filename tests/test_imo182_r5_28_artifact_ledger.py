"""r5-01 source-safe reconciliation invariants; technical evidence != acceptance."""
import json
import re
import unittest
from pathlib import Path

LEDGER = (
    Path(__file__).resolve().parents[1]
    / "TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json"
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
ROLES = {"core1.html", "core1a.html", "core1b.html", "core2a.html", "core2b.html", "index.html"}
DEMANDS = {"RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"}


class ReconciledNativeArtifactLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_unique_28_demand_band_cells(self):
        rows = self.doc["rows"]
        self.assertEqual(len(rows), 28)
        ids = {r["cell_id"] for r in rows}
        self.assertEqual(len(ids), 28)
        self.assertEqual(ids, {f"QRT-{d}-{b}" for d in DEMANDS for b in ("D1", "D2", "D3", "D4")})

    def test_exact_sources_and_all_six_html_hashes_are_present(self):
        rows = self.doc["rows"]
        for r in rows:
            with self.subTest(cell=r["cell_id"]):
                self.assertTrue(r["source"]["path"].startswith("TEST/"))
                self.assertTrue(r["manifest"]["path"].startswith("TEST/"))
                self.assertRegex(r["source"]["commit"], SHA1)
                self.assertRegex(r["source"]["git_blob_sha"], SHA1)
                self.assertRegex(r["manifest"]["git_blob_sha"], SHA1)
                shas = r["artifact"]["native_html_sha256"]
                self.assertEqual(set(shas), ROLES)
                self.assertTrue(all(SHA256.fullmatch(s) for s in shas.values()))
                self.assertEqual(r["frozen_golden"]["structural_roles_matching"], 5)
                self.assertEqual(r["renderer"]["gaps"], [])
                self.assertTrue(
                    r["renderer"]["receipt_shas_matching"] == 6
                    or r["renderer"].get("adoption_ledger_sha256_matching") == 6
                )

    def test_academic_and_owner_gates_are_not_silently_accepted(self):
        self.assertEqual(self.doc["summary"]["owner_accepted"], 0)
        for r in self.doc["rows"]:
            self.assertFalse(r["owner_qrta_accepted"])
            self.assertFalse(r["owner_golden_designated"])
            self.assertFalse(r["release_authorized"])
            self.assertEqual(r["academic_review"], "QUALIFIED_INDEPENDENT_REVIEW_PENDING")
            self.assertEqual(r["frozen_golden"]["semantic_technique_verdict"], "UNREVIEWED")

    def test_separate_d4_ledger_and_corrected_d3_supersession(self):
        self.assertEqual(
            sum(r["renderer"].get("adoption_ledger_sha256_matching", 0) for r in self.doc["rows"]),
            30,
        )
        synth = next(r for r in self.doc["rows"] if r["cell_id"] == "QRT-SYNTHESIZE-D3")
        self.assertEqual(synth["artifact"]["id"], 11859035196)
        self.assertTrue(any("SUPERSEDED" in note for note in synth["do_not_adopt_original_leaking_or_superseded"]))


if __name__ == "__main__":
    unittest.main()
