"""Real-source tests for the read-only Physics-to-Core crosswalk."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Physics.adapter.qrt_program.qrt_crosswalk import inspect_question

SOURCE = "Physics/library/phy-nlm-first-law.v1.json"
ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"


class SourceCrosswalkTests(unittest.TestCase):
    def test_existing_core2b_source_binding(self):
        row = inspect_question(SOURCE, ID)
        self.assertEqual(row["question_id"], ID)
        self.assertEqual(row["package_blob_sha"], "62b8df106e83db03ac80fbb4002a611ac3d6e49a")
        self.assertEqual(row["source_class"], "AUTHOR_CREATED_CANDIDATE")
        self.assertEqual(row["primary_capability_ref"], "CAP-NLM-FRICTION-QUANT")
        self.assertIn("CORE2B", row["declared_cores"])
        self.assertEqual(row["difficulty"]["band"], "D3")
        self.assertEqual(row["status"], "SOURCE_STRUCTURALLY_BOUND_NOT_ACCEPTED")
        self.assertEqual(row["qrt_demand"], "UNRESOLVED_RUN_CANONICAL_QRT")
        self.assertEqual(row["physics_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(row["render_verdict"], "NOT_ATTESTED")

    def test_four_real_candidates_report_independent_qrt_blockers(self):
        cases = [
            ("Physics/library/phy-vec-add-sub.v1.json",
             "Q-PHY-VEC-DECOMP-2A-QUADRANT-II-03", False),
            ("Physics/library/phy-kin-2d-motion.v1.json",
             "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04", True),
            ("Physics/library/phy-nlm-first-law.v1.json",
             "Q-PHY-NLM-2A-COV-03", False),
            (SOURCE, ID, True),
        ]
        for path, qid, has_crux in cases:
            with self.subTest(question=qid):
                row = inspect_question(path, qid)
                gate = row["qrt_source_gate"]
                self.assertEqual(gate["state"], "BLOCKED")
                self.assertEqual(gate["canonical_error"], f"COGNITIVE_DEMAND_MISSING: {qid}")
                self.assertIsNone(gate["declared_demand"])
                self.assertEqual(gate["crux_move_present"], has_crux)
                self.assertEqual(gate["review"], "NOT_RUN")
                self.assertEqual(row["qrt_demand"], "UNRESOLVED_RUN_CANONICAL_QRT")
                self.assertEqual(row["academic_verdict"], "REVIEW_REQUIRED")

    def test_fake_test_only_demand_cannot_claim_academic_or_qrt_approval(self):
        # A hypothetical classification is only an in-memory negative/positive
        # contract control, never an academically accepted Physics declaration.
        repo = Path(__file__).resolve().parents[1]
        package = json.loads((repo / SOURCE).read_text(encoding="utf-8"))
        question = next(q for q in package["questions"] if q.get("id") == ID)
        question["extensions"]["grade9v3:cognitive_demand"] = {
            "primary": "MODEL", "secondary": [], "basis": "TEST_ONLY_NOT_AUTHORIZED"
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / SOURCE
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(package), encoding="utf-8")
            row = inspect_question(SOURCE, ID, root=root)
        self.assertEqual(row["qrt_source_gate"]["state"], "SOURCE_METADATA_VALID_NOT_REVIEWED")
        self.assertIsNone(row["qrt_source_gate"]["canonical_error"])
        self.assertEqual(row["qrt_demand"], "UNRESOLVED_RUN_CANONICAL_QRT")
        self.assertEqual(row["academic_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(row["school_micro_demand"], "MICRO_TO_CONFIRM")

    def test_demand_field_alone_cannot_resolve_a_missing_reasoning_crux(self):
        repo = Path(__file__).resolve().parents[1]
        path = "Physics/library/phy-vec-add-sub.v1.json"
        qid = "Q-PHY-VEC-DECOMP-2A-QUADRANT-II-03"
        package = json.loads((repo / path).read_text(encoding="utf-8"))
        question = next(q for q in package["questions"] if q.get("id") == qid)
        question["extensions"]["grade9v3:cognitive_demand"] = {
            "primary": "REPRESENT", "secondary": [], "basis": "TEST_ONLY_NOT_AUTHORIZED"
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / path
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(package), encoding="utf-8")
            row = inspect_question(path, qid, root=root)
        self.assertEqual(row["qrt_source_gate"]["state"], "BLOCKED")
        self.assertEqual(row["qrt_source_gate"]["canonical_error"],
                         f"COGNITIVE_DEMAND_CRUX_MOVE_MISSING: {qid}")
        self.assertFalse(row["qrt_source_gate"]["crux_move_present"])

    def test_does_not_invent_question(self):
        row = inspect_question(SOURCE, "Q-NOT-REAL")
        self.assertEqual(row["errors"], ["QUESTION_MISSING"])
        self.assertEqual(row["status"], "HOLD")

    def test_rejects_escape_path(self):
        with self.assertRaisesRegex(ValueError, "PHYSICS_LIBRARY_PATH_REQUIRED"):
            inspect_question("../../etc/passwd", ID)

    def test_missing_transfer_is_not_a_pass(self):
        # Self-contained mutation of one canonical record; never write to repo.
        repo = Path(__file__).resolve().parents[1]
        value = json.loads((repo / SOURCE).read_text(encoding="utf-8"))
        question = next(q for q in value["questions"] if q.get("id") == ID)
        question["transfer"].pop("protected_move_ref", None)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / SOURCE
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(value), encoding="utf-8")
            report = inspect_question(SOURCE, ID, root=root)
        self.assertIn("CORE2B_TRANSFER_CONTRACT_INCOMPLETE", report["errors"])

    def test_duplicate_question_id_is_ambiguous(self):
        repo = Path(__file__).resolve().parents[1]
        value = json.loads((repo / SOURCE).read_text(encoding="utf-8"))
        row = next(q for q in value["questions"] if q.get("id") == ID)
        value["questions"].append(row)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / SOURCE
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(value), encoding="utf-8")
            report = inspect_question(SOURCE, ID, root=root)
        self.assertIn("AMBIGUOUS_QUESTION_ID", report["errors"])


if __name__ == "__main__":
    unittest.main()
