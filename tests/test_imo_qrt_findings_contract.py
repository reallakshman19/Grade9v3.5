"""Direct v1 provenance/occurrence controls; independent M oracle is elsewhere."""
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from Shared.tools.imo_qrt_validator import (
    BANKS, ROOT, EXPECTED_TOTAL, FINDINGS_SCHEMA,
    build_question_findings, validate_bank_dir, verify_source_commit,
)

SOURCE_SHA = "40f9267bb81db20c55a98c40650fc3b7ac054b5c"
Q022 = "SOF-IMO-G09-L1-2024-25-B-Q022"


class FindingsInterfaceControls(unittest.TestCase):
    def test_valid_hex_wrong_source_commit_is_rejected(self):
        with patch("Shared.tools.imo_qrt_validator._git_bytes", return_value=b"b" * 40 + b"\n"):
            with self.assertRaisesRegex(ValueError, "SOURCE_COMMIT_NOT_PINNED"):
                verify_source_commit(Path("."), "a" * 40)

    def test_question_findings_contract_schema_is_versioned(self):
        path = ROOT / "TEST/imo-qrt-validator/question-findings.v1.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], FINDINGS_SCHEMA)
        self.assertEqual(schema["properties"]["actual_total"]["const"], EXPECTED_TOTAL)
        self.assertEqual(schema["properties"]["matrix"]["properties"]["expected_coordinates"]["const"], 28)
        self.assertIn("ERROR", schema["$defs"]["verdict"]["enum"])
        self.assertIn("STALE", schema["$defs"]["verdict"]["enum"])
        self.assertIn("NOT_RUN", schema["$defs"]["verdict"]["enum"])

    def test_pinned_q022_keeps_true_score_mismatch(self):
        # A V-only checkout has an older source: this is intentionally NOT_RUN
        # until the independently pinned 40f926 source plus V overlay is used.
        try:
            actual = subprocess.check_output(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("PINNED_SOURCE_NOT_AVAILABLE")
        if actual != SOURCE_SHA:
            self.skipTest("PINNED_SOURCE_NOT_AVAILABLE")
        report = validate_bank_dir(ROOT / "Mathematics/question-bank", baseline_sha=SOURCE_SHA)
        self.assertEqual((report["actual_total"], report["unique_ids"]), (260, 260))
        self.assertEqual(len(report["tiles"]), 28)
        match = [q for q in report["questions"] if q["id"] == Q022]
        self.assertEqual(len(match), 1)
        q = match[0]
        self.assertEqual((q["source_file"], q["source_array_index"]), (
            "sof-imo-2024-25-set-b.core2.json", 21,
        ))
        self.assertEqual((q["difficulty_evidence"]["stored_score"],
                          q["difficulty_evidence"]["derived_score"]), (2, 1))
        self.assertIn("FIVE_FACTOR_SCORE_MISMATCH",
                      {f["evidence"] for f in q["findings"] if f["verdict"] == "FAIL"})
        self.assertEqual(q["academic_verdict"], "REVIEW_REQUIRED")

    def test_mandatory_missing_source_records_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_260_DENOMINATOR_MISMATCH"):
            with patch("Shared.tools.imo_qrt_validator.verify_source_commit"):
                with patch("Shared.tools.imo_qrt_validator._git_bytes", return_value=b"commit\n"):
                    build_question_findings({
                        "baseline_commit": "a" * 40,
                        "actual_total": 259, "unique_ids": 259,
                        "expected_total": 260,
                    }, repo_root=Path("."), source_sha="a" * 40,
                       validator_sha="b" * 40)


if __name__ == "__main__":
    unittest.main()
