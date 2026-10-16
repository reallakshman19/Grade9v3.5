"""Unit tests for real-source candidate construction and fail-closed drift."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from tools.physics_qrt_program.bootstrap import BootstrapError, HERE, assemble
from tools.physics_qrt_program.contracts import validate_lock

class Wave0Tests(unittest.TestCase):
    def test_real_four_and_no_approval(self):
        packet = assemble()
        self.assertEqual(len(packet["cases"]), 4)
        self.assertEqual(validate_lock(packet["lock"]), [])
        self.assertIn("WORK_LOCK_NOT_APPROVED", validate_lock(packet["lock"], require_authorized=True))
        self.assertEqual(packet["release_verdict"], "HOLD")
        root = Path(__file__).resolve().parents[1]
        for w in packet["lock"]["witnesses"]:
            self.assertEqual(w["source_sha256"], hashlib.sha256((root / w["source_path"]).read_bytes()).hexdigest())

    def test_capability_drift(self):
        value = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
        value["cases"][0]["expected_capability"] = "NOT_THE_CAPABILITY"
        with self.assertRaisesRegex(BootstrapError, "CAPABILITY_DRIFT"):
            assemble(candidates=value)

    def test_core_drift(self):
        value = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
        value["cases"][0]["expected_core"] = "CORE2B"
        with self.assertRaisesRegex(BootstrapError, "CORE_DRIFT"):
            assemble(candidates=value)

    def test_duplicate_identity(self):
        value = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
        value["cases"].append(copy.deepcopy(value["cases"][0]))
        with self.assertRaisesRegex(BootstrapError, "DUPLICATE_QUESTION_ID"):
            assemble(candidates=value)

    def test_wrong_git_blob_sha_rejected(self):
        value = json.loads((HERE / "witnesses.candidate.v1.json").read_text())
        value["cases"][0]["source_blob_sha"] = "f" * 40
        with self.assertRaisesRegex(BootstrapError, "SOURCE_BLOB_DRIFT"):
            assemble(candidates=value)

    def test_authorized_lock_never_used_as_candidate(self):
        lock = json.loads((HERE / "work-lock.template.json").read_text())
        lock["governance"]["git_write_authorized"] = True
        with self.assertRaisesRegex(BootstrapError, "LOCK_NOT_DRAFT_HOLD"):
            assemble(draft_lock=lock)

if __name__ == "__main__":
    unittest.main()
