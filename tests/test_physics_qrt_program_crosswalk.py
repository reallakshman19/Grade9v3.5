"""Real-source tests for the read-only Physics-to-Core crosswalk."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.physics_qrt_program.crosswalk import inspect_question

SOURCE = "Physics/library/phy-nlm-first-law.v1.json"
ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"


class SourceCrosswalkTests(unittest.TestCase):
    def test_existing_core2b_source_binding(self):
        row = inspect_question(SOURCE, ID)
        self.assertEqual(row["question_id"], ID)
        self.assertEqual(row["source_class"], "AUTHOR_CREATED_CANDIDATE")
        self.assertEqual(row["primary_capability_ref"], "CAP-NLM-FRICTION-QUANT")
        self.assertIn("CORE2B", row["declared_cores"])
        self.assertEqual(row["difficulty"]["band"], "D3")
        self.assertEqual(row["status"], "SOURCE_STRUCTURALLY_BOUND_NOT_ACCEPTED")
        self.assertEqual(row["qrt_demand"], "UNRESOLVED_RUN_CANONICAL_QRT")
        self.assertEqual(row["physics_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(row["render_verdict"], "NOT_ATTESTED")

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
