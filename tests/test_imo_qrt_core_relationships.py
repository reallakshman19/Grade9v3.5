"""Synthetic source-safe relationship and navigation false-pass tests."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Shared.tools.imo_qrt_core_relationships import audit, topic_map_from_builder


class RelationshipEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/"Mathematics/question-bank").mkdir(parents=True)
        (self.root/"Mathematics/research").mkdir(parents=True)
        (self.root/"Mathematics/units/triangles").mkdir(parents=True)
        (self.root/"Mathematics/research/build_full_master_suite.py").write_text(
            "TOPIC_TO_UNIT_FOLDER = {'triangles': 'triangles'}\n", encoding="utf-8")
        self.question = {
            "id": "SYN-Q1", "taxonomy": {"topic_label": "Triangles"},
            "cognitive_classification": {
                "difficulty_band": "D2", "primary_demand": "APPLY",
                "qrt_cell": "QRT-APPLY-D2"
            }
        }
        self.core_a = {
            "package_id": "SYN-UNIT", "topic": "TRIANGLES", "subtopic": "SYNTHETIC",
            "target_band": "D2", "target_demand": "APPLY",
            "blueprint_ref": "BP-CORE1A-CONSTRUCTION",
            "linked_core2_refs": ["SYN-Q1"]
        }
        self.core_b = {
            "package_id": "SYN-UNIT-B", "topic": "TRIANGLES", "subtopic": "SYNTHETIC",
            "target_band": "D2", "target_demand": "APPLY",
            "blueprint_ref": "BP-CORE1B-RECONSTRUCTION",
        }
        self.a_path = self.root/"Mathematics/units/triangles/core1a-syn.v1.json"
        self.b_path = self.root/"Mathematics/units/triangles/core1b-syn.v1.json"
        self.flush()

    def flush(self):
        def put(p, d):
            p.write_text(json.dumps(d), encoding="utf-8")
        put(self.root/"Mathematics/question-bank/synthetic.json",
            {"questions": [self.question]})
        put(self.a_path, self.core_a)
        put(self.b_path, self.core_b)

    def inspect(self):
        return audit(root=self.root, baseline_sha="a"*40, bank_names=("synthetic.json",))

    def test_exact_source_link_is_not_academic_admission(self):
        r = self.inspect()
        self.assertEqual(r["status"], "REVIEW_REQUIRED")
        self.assertEqual(r["relationship_counts"]["EXPLICIT_UNIT_ID"], 1)
        self.assertEqual(r["questions"][0]["native_core_admission"], "NOT_GRANTED")
        self.assertEqual(r["academic_approval"], "NOT_GRANTED")

    def test_only_topic_route_is_not_exact_concept_link(self):
        self.core_a["linked_core2_refs"] = []
        self.flush()
        r = self.inspect()
        self.assertEqual(r["relationship_counts"]["TOPIC_NAV_ONLY"], 1)
        self.assertEqual(r["questions"][0]["explicit_unit_ids"], [])

    def test_unmapped_topic_fallback_is_not_considered_a_link(self):
        self.question["taxonomy"]["topic_label"] = "Unmapped mathematical topic"
        self.core_a["linked_core2_refs"] = []
        self.flush()
        r = self.inspect()
        self.assertEqual(r["status"], "FAIL")
        self.assertEqual(r["questions"][0]["builder_navigation_folder"], "polynomials")
        self.assertTrue(r["questions"][0]["navigation_fallback_used"])

    def test_missing_linked_id_fails(self):
        self.core_a["linked_core2_refs"] = ["SYN-UNKNOWN"]
        self.flush()
        r = self.inspect()
        self.assertEqual(r["status"], "FAIL")
        self.assertIn("CORE2_EXPLICIT_REF_NOT_IN_RESEARCH",
                      {row["rule"] for row in r["structural_findings"]})

    def test_pair_mismatch_fails(self):
        self.core_b["target_demand"] = "JUSTIFY"
        self.flush()
        r = self.inspect()
        self.assertIn("CORE1A_CORE1B_QRT_TARGET_MISMATCH",
                      {row["rule"] for row in r["structural_findings"]})

    def test_missing_core1b_subtopic_is_undeclared_not_contradiction(self):
        self.core_b.pop("subtopic")
        self.flush()
        r = self.inspect()
        points = {row["rule"] for row in r["structural_findings"]}
        self.assertIn("CORE1B_SUBTOPIC_UNDECLARED", points)
        self.assertNotIn("CORE1A_CORE1B_CONCEPT_ID_MISMATCH", points)

    def test_unit_vs_question_tile_difference_is_review_not_automatic_error(self):
        self.question["cognitive_classification"]["primary_demand"] = "MODEL"
        self.flush()
        r = self.inspect()
        self.assertEqual(r["relationship_counts"]["EXPLICIT_UNIT_QRT_DIFFERS_FROM_SOURCE_PROPOSAL"], 1)
        self.assertEqual(r["status"], "REVIEW_REQUIRED")

    def test_orphan_core1b_fails(self):
        self.a_path.unlink()
        r = self.inspect()
        self.assertEqual(r["status"], "FAIL")
        self.assertIn("CORE1B_ORPHAN",
                      {row["rule"] for row in r["structural_findings"]})

    def test_builder_source_not_a_guessed_mapping(self):
        p = self.root/"Mathematics/research/build_full_master_suite.py"
        self.assertEqual(topic_map_from_builder(p)["triangles"], "triangles")
        p.write_text("TOPIC_TO_UNIT_FOLDER = {}\nTOPIC_TO_UNIT_FOLDER = {}\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "NOT_UNIQUE"):
            self.inspect()

    def test_invalid_source_commit_ref_refused(self):
        with self.assertRaisesRegex(ValueError, "EXACT_COMMIT_SHA"):
            audit(root=self.root, baseline_sha="main", bank_names=("synthetic.json",))


if __name__ == "__main__":
    unittest.main()
