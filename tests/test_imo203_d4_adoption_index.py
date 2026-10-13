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
        self.assertEqual(sum(bool(c["render"]) for c in self.cells), 7)
        self.assertEqual([c["demand"] for c in self.cells if c["render"] is None], [])
        self.assertEqual(self.ledger["owner_qrt_accepted"], 0)
        self.assertEqual(len(self.index["cells"]), 28)

    def test_six_role_digests_and_pinned_worker_source(self):
        for cell in self.cells:
            with self.subTest(cell=cell["cell_id"]):
                self.assertFalse(cell["assessment"]["accepted"])
                self.assertIsNone(cell["assessment"]["owner_qrt_decision_id"])
                self.assertEqual(cell["assessment"]["release"], "NOT_AUTHORIZED")
                if not cell["render"]:
                    self.assertEqual(cell["source"]["classification"], "WHOLLY_AUTHORED_TEST_CANDIDATE")
                    self.assertIsNone(cell["source"]["manifest_path"])
                    self.assertEqual(cell["candidate_math_ci"], "SCOPED_PASS")
                    self.assertEqual(cell["candidate_math_workflow_run"], 38404571127)
                    self.assertTrue(cell["candidate_math_spec_link"].endswith("-d4.candidate.json"))
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

    def test_new_exact_head_native_evidence_and_supersession(self):
        for demand, run, artifact in (("RETRIEVE", 38413546614, 11823696124),
                                      ("SYNTHESIZE", 38413545923, 11824250043)):
            with self.subTest(cell=demand):
                cell = next(c for c in self.cells if c["demand"] == demand)
                self.assertEqual(cell["adoption_status"], "RENDERED_TEST; INDEPENDENT_ACADEMIC_REVIEW_PENDING")
                self.assertEqual(cell["render"]["workflow_run"], run)
                self.assertEqual(cell["render"]["artifact_id"], artifact)
                self.assertEqual(cell["source"]["worker_pr"], 210)
                self.assertEqual(cell["source"]["verified_worker_commit"], "9faa52d499e071e9e6d4c419b5afdf5fbc044455")
                self.assertTrue(cell["superseded_native_evidence"]["do_not_adopt"])
                self.assertNotEqual(cell["superseded_native_evidence"]["artifact_id"], artifact)
                self.assertIsNone(cell["assessment"]["owner_qrt_decision_id"])
                self.assertFalse(cell["assessment"]["accepted"])

    def test_owner_frozen_role_slot_differential_is_only_structural(self):
        report = json.loads((BASE / "d4-review/golden-technique-diff.v1.json").read_text())
        self.assertEqual(report["comparison_type"], "CROSS_QUESTION_ROLE_STRUCTURE_ONLY")
        self.assertEqual(report["comparator"]["owner_commit"],
                         "67c34dababb0da0ef7d5f4a532bfcf3119754961")
        self.assertEqual(report["summary"]["matched_role_sequences"], 35)
        self.assertEqual(report["summary"]["academic_reviewed_cells"], 0)
        self.assertEqual(report["summary"]["owner_qrt_accepted_cells"], 0)
        self.assertFalse(report["summary"]["release_authorized"])
        self.assertEqual({r["cell_id"] for r in report["cells"]},
                         {r["cell_id"] for r in self.cells})
        expected_roles = ("core1", "core1a", "core1b", "core2a", "core2b")
        for result in report["cells"]:
            cell = next(x for x in self.cells if x["cell_id"] == result["cell_id"])
            self.assertEqual(result["render_artifact_id"], cell["render"]["artifact_id"])
            self.assertIsNone(result["owner_qrt_decision_id"])
            self.assertEqual(tuple(result["registered_role_slot_order"]), expected_roles)
            for role, check in result["registered_role_slot_order"].items():
                self.assertEqual(check["status"], "MATCH")
                self.assertEqual(check["observed_slot_sequence"],
                                 check["expected_slot_sequence"])
                golden = report["comparator"]["role_slots"][role]
                self.assertEqual(check["expected_slot_sequence"], golden["sequence"])
                self.assertEqual(result["role_specific_semantic_differential"][role]["academic_semantics"],
                                 "PENDING_QUALIFIED_REVIEW")

    def test_reviewer_handoff_keeps_84_checks_unsigned(self):
        p = json.loads((BASE / "d4-review/qualified-review-handoff.v1.json").read_text())
        self.assertEqual(len(p["cells"]), 7)
        self.assertEqual(p["baseline"]["owner_qrt_accepted"], 0)
        self.assertEqual(p["common_hspm_objectives"],
                         ["H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3"])
        for item in p["cells"]:
            c = next(c for c in self.cells if c["cell_id"] == item["cell_id"])
            self.assertEqual(item["exact_render_artifact"], c["render"]["artifact_url"])
            self.assertEqual(item["worker_source_head"], c["source"]["verified_worker_commit"])
            self.assertEqual(len(item["HSPM_review"]), 12)
            self.assertTrue(all(v["verdict"] == "PENDING" for v in item["HSPM_review"].values()))
            self.assertIsNone(item["qualified_reviewer"])
            self.assertIsNone(item["academic_verdict"])
            self.assertIsNone(item["owner_decision_id"])
            self.assertFalse(item["accepted"])

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
