"""Synthetic contract, negative-authority and privacy tests for Issue #165."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "TEST/imo-research/core2_blueprint_readiness.py"
spec = importlib.util.spec_from_file_location("core2_blueprint_readiness", FILE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class BlueprintReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.schema_dir = self.root / "Shared/library"
        self.bp_dir = self.root / "Shared/web"
        self.schema_dir.mkdir(parents=True)
        self.bp_dir.mkdir(parents=True)
        self.schema = {
            "$id": "https://grade9v3.local/source-question-custody.schema.json",
            "$defs": {"componentStatus": {"enum": [
                "PRESERVED", "NOT_PRESENT_IN_SOURCE", "EXTERNAL_REFERENCE_VERIFIED", "UNRESOLVED"]}},
            "properties": {"components": {
                "type": "object", "additionalProperties": False,
                "required": sorted(audit.NINE),
                "properties": {k: {"$ref": "#/$defs/componentStatus"}
                               for k in audit.NINE},
            }},
        }
        self.bp = {
            "registry_version": "1.17.0",
            "blueprints": [{
                "id": audit.BLUEPRINT, "version": audit.BLUEPRINT_VERSION,
                "status": "ACTIVE", "core_roles": ["CORE2"],
                "slots": [{"id": k} for k in ("identity", "attempt", "representation", "support", "solution")],
                "components": [{"id": k, "slot": (
                    "identity" if k == "IDENTITY" else "attempt" if k in ("STEM", "ATTEMPT") else "solution"),
                    "level": "REQUIRED"} for k in sorted(audit.REQUIRED_BLUEPRINT_COMPONENTS)],
            }],
        }
        self._write()

    def _write(self):
        (self.schema_dir / "source-question-custody.schema.json").write_text(json.dumps(self.schema))
        (self.bp_dir / "interactive-page-blueprints.v1.json").write_text(json.dumps(self.bp))

    def verdict(self):
        return {
            "schema": audit.SPOTCHECK_SCHEMA,
            "question_id": audit.QUESTION,
            "status": "SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED",
            "component_check_complete": True,
            "historical_version_comparison": "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY",
            "blocking_codes": [],
            "self_attestation_not_source_certificate": True,
            "source_custody_hold": 68,
            "core2_eligible": False,
            "core2_admitted": False,
            "learner_published": False,
            "source_rights": "NOT_REVIEWED",
        }

    def test_default_contract_report_fails_closed(self):
        out = audit.report(self.root)
        self.assertEqual(out["contracts"]["blueprint_ref"],
                         "BP-CORE2-SOURCE-QUESTION@1.11.0")
        self.assertEqual(len(out["contracts"]["custody_component_names"]), 9)
        self.assertEqual(len(out["contracts"]["blueprint_required_components"]), 6)
        self.assertIn("PRIVATE_SOURCE_VERIFIER_RESULT_NOT_SUPPLIED", out["blockers"])
        self.assertEqual(out["decision"], "HOLD_MISSING_EVIDENCE")
        self.assertFalse(out["core2_eligible"])

    def test_self_check_never_grants_custody_or_rights(self):
        out = audit.report(self.root, self.verdict())
        self.assertEqual(out["spotcheck"]["state"], "SELF_CHECK_REPORTED_ONLY")
        self.assertIn("INDEPENDENT_CUSTODY_AND_MATH_REVIEW_REQUIRED", out["blockers"])
        for key in ("rights_granted", "independent_review_accepted", "core2_eligible",
                    "core2_admitted", "learner_published"):
            self.assertIs(out[key], False)

    def test_receipt_missing_status_stays_hold(self):
        row = self.verdict()
        row["status"] = "HOLD_RETAINED_SOURCE_NOT_VERIFIED"
        row["component_check_complete"] = False
        row["blocking_codes"] = ["PRIVATE_RETAINED_PDF_RECEIPT_MISSING_OR_INVALID"]
        out = audit.report(self.root, row)
        self.assertIn("SOURCE_OPERATOR_SELF_CHECK_NOT_COMPLETE", out["blockers"])

    def test_version_drift_status_stays_hold(self):
        row = self.verdict()
        row["status"] = "HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE"
        row["blocking_codes"] = ["SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED"]
        out = audit.report(self.root, row)
        self.assertEqual(out["decision"], "HOLD_MISSING_EVIDENCE")

    def test_forged_promotion_is_rejected(self):
        for key in ("core2_eligible", "core2_admitted", "learner_published"):
            with self.subTest(key=key):
                row = self.verdict()
                row[key] = True
                with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_INVALID"):
                    audit.report(self.root, row)

    def test_forged_review_or_rights_is_rejected(self):
        for key, value in (("self_attestation_not_source_certificate", False),
                           ("source_rights", "AUTHORIZED"),
                           ("source_custody_hold", 0)):
            with self.subTest(key=key):
                row = self.verdict()
                row[key] = value
                with self.assertRaises(audit.AuditError):
                    audit.report(self.root, row)

    def test_identity_and_extra_data_rejected(self):
        for key, value in (("question_id", "SYNTHETIC-Q4"),
                           ("original_source_stem", "PROTECTED TEXT"),
                           ("schema", "other")):
            with self.subTest(key=key):
                row = self.verdict()
                row[key] = value
                with self.assertRaises(audit.AuditError):
                    audit.report(self.root, row)

    def test_inconsistent_self_check_claim_rejected(self):
        for key, value in (("component_check_complete", False),
                           ("blocking_codes", ["FALSE_POSITIVE"])):
            row = self.verdict()
            row[key] = value
            with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_INCONSISTENT"):
                audit.report(self.root, row)

    def test_duplicate_schema_required_or_missing_component_ref_rejected(self):
        self.schema["properties"]["components"]["required"][-1] = "stem"
        self._write()
        with self.assertRaisesRegex(audit.AuditError, "CUSTODY_SCHEMA_COMPONENT_DRIFT"):
            audit.report(self.root)
        self.schema["properties"]["components"]["required"] = sorted(audit.NINE)
        self.schema["properties"]["components"]["properties"]["options"] = {"type": "string"}
        self._write()
        with self.assertRaisesRegex(audit.AuditError, "CUSTODY_SCHEMA_COMPONENT_DRIFT"):
            audit.report(self.root)

    def test_changed_schema_status_enum_rejected(self):
        self.schema["$defs"]["componentStatus"]["enum"].append("SELF_CHECKED")
        self._write()
        with self.assertRaises(audit.AuditError):
            audit.report(self.root)

    def test_blueprint_version_status_roles_and_required_set_rejected(self):
        base = copy.deepcopy(self.bp)
        for mutation in (
            lambda bp: bp["blueprints"][0].update(version="1.99.0"),
            lambda bp: bp["blueprints"][0].update(status="DRAFT"),
            lambda bp: bp["blueprints"][0].update(core_roles=["CORE2A"]),
            lambda bp: bp["blueprints"][0]["components"].pop(),
        ):
            self.bp = copy.deepcopy(base)
            mutation(self.bp)
            self._write()
            with self.assertRaises(audit.AuditError):
                audit.report(self.root)
        self.bp = base

    def test_duplicate_blueprint_rejected(self):
        self.bp["blueprints"].append(copy.deepcopy(self.bp["blueprints"][0]))
        self._write()
        with self.assertRaises(audit.AuditError):
            audit.report(self.root)

    def test_cli_uses_safe_metadata_only_no_paths(self):
        secret = "private question wording that must never be logged"
        candidate = self.root / "very-private-source-name.json"
        row = self.verdict()
        row["blocking_codes"] = [secret]
        candidate.write_text(json.dumps(row))
        result = subprocess.run(
            [sys.executable, str(FILE), "report", "--repo-root", str(self.root),
             "--spotcheck-verdict", str(candidate)],
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(secret, result.stderr + result.stdout)
        self.assertNotIn(str(candidate), result.stderr + result.stdout)
        self.assertIn("SPOTCHECK_METADATA_INVALID", result.stderr)

    def test_cli_default_success_never_prints_raw_source(self):
        result = subprocess.run(
            [sys.executable, str(FILE), "report", "--repo-root", str(self.root)],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        obj = json.loads(result.stdout)
        self.assertEqual(obj["decision"], "HOLD_MISSING_EVIDENCE")
        self.assertNotIn(str(self.root), result.stdout)

    def test_symlink_or_oversized_untrusted_verdict_rejected(self):
        rowpath = self.root / "verdict.json"
        rowpath.write_text("x" * (audit.MAX_METADATA_BYTES + 1))
        with self.assertRaises(audit.AuditError):
            audit._read_json(rowpath, "SPOTCHECK_METADATA_UNAVAILABLE",
                             size_limit=audit.MAX_METADATA_BYTES)
        rowpath.write_text(json.dumps(self.verdict()))
        link = self.root / "link.json"
        link.symlink_to(rowpath)
        with self.assertRaises(audit.AuditError):
            audit._read_json(link, "SPOTCHECK_METADATA_UNAVAILABLE",
                             size_limit=audit.MAX_METADATA_BYTES)

    def test_untrusted_blocking_code_not_copied(self):
        row = self.verdict()
        row["status"] = "HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE"
        row["component_check_complete"] = False
        row["blocking_codes"] = ["PRIVATE_METADATA_ONLY"]
        out = audit.report(self.root, row)
        self.assertNotIn("PRIVATE_METADATA_ONLY", json.dumps(out))


if __name__ == "__main__":
    unittest.main()
