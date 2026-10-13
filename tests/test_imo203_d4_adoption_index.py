"""Source-safe consistency checks for issue #203 D4 evidence; not academic acceptance."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "TEST/imo-research/qrt-tiles"
LEDGER = BASE / "d4-review/adoption.v1.json"
VIEWER = BASE / "d4-review/index.html"
MATRIX = BASE / "q003-model-d2/index.html"
INDEX = BASE / "q003-model-d2/band-issues.v1.json"
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
ROLES = ("core1.html", "core1a.html", "core1b.html", "core2a.html", "core2b.html", "index.html")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GITSHA = re.compile(r"^[0-9a-f]{40}$")


class D4AdoptionEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text())
        cls.cells = cls.ledger["cells"]
        cls.index = json.loads(INDEX.read_text())

    def test_seven_cells_five_immutable_worker_artifacts_two_missing(self):
        self.assertEqual([c["cell_id"] for c in self.cells],
                         ["QRT-" + d + "-D4" for d in DEMANDS])
        self.assertEqual(sum(bool(c["render"]) for c in self.cells), 5)
        self.assertEqual([c["demand"] for c in self.cells if c["render"] is None],
                         ["RETRIEVE", "SYNTHESIZE"])
        self.assertEqual(self.ledger["owner_qrt_accepted"], 0)
        self.assertEqual(len(self.index["cells"]), 28)

    def test_six_role_digests_and_pinned_worker_source(self):
        for cell in self.cells:
            with self.subTest(cell=cell["cell_id"]):
                self.assertFalse(cell["assessment"]["accepted"])
                self.assertIsNone(cell["assessment"]["owner_qrt_decision_id"])
                self.assertEqual(cell["assessment"]["release"], "NOT_AUTHORIZED")
                if not cell["render"]:
                    self.assertEqual(cell["source"]["classification"], "NOT_AUTHORED")
                    continue
                src = cell["source"]
                self.assertEqual(src["classification"], "AUTHORED_TEST_ONLY")
                for key in ("verified_worker_commit", "package_blob_sha", "manifest_blob_sha", "review_blob_sha"):
                    self.assertRegex(src[key], GITSHA)
                render = cell["render"]
                self.assertEqual(render["gaps"], 0)
                self.assertEqual(render["renderer"], "render_core/2")
                self.assertEqual(render["mode"], "PAGES")
                self.assertTrue(render["six_sha256_independently_verified"])
                self.assertEqual(tuple(render["six_html_sha256"]), ROLES)
                for digest in render["six_html_sha256"].values():
                    self.assertRegex(digest, SHA256)
                self.assertEqual(cell["golden"]["comparator_kind"], "SEMANTIC_CROSS_QUESTION")
                self.assertIsNone(cell["golden"]["owner_new_fixture"])

    def test_model_has_distinct_corrected_exact_head_evidence(self):
        model = next(c for c in self.cells if c["demand"] == "MODEL")
        repaired = model["repaired_evidence"]
        self.assertEqual(repaired["draft_pr"], 207)
        self.assertEqual(repaired["gaps"], 0)
        self.assertTrue(repaired["six_sha256_independently_verified"])
        self.assertEqual(tuple(repaired["six_html_sha256"]), ROLES)
        self.assertNotEqual(repaired["exact_head"], model["source"]["verified_worker_commit"])
        self.assertEqual(model["assessment"]["mathematics"], "PENDING_INDEPENDENT_QUALIFIED_REVIEW")

    def test_adoption_viewer_is_navigable_without_claiming_owner_acceptance(self):
        html = VIEWER.read_text()
        matrix = MATRIX.read_text()
        self.assertIn('id="d4-adoption-link"', matrix)
        self.assertIn('href="../d4-review/index.html"', matrix)
        self.assertIn('href="adoption.v1.json"', html)
        for cell in self.cells:
            with self.subTest(cell=cell["cell_id"]):
                self.assertIn('id="' + cell["cell_id"] + '"', html)
                indexed = next(c for c in self.index["cells"] if c["cell_id"] == cell["cell_id"])
                self.assertEqual(indexed["adoption_evidence_path"], "../d4-review/index.html#" + cell["cell_id"])
                self.assertEqual(indexed["owner_qrt_acceptance"], "PENDING")


if __name__ == "__main__":
    unittest.main()
