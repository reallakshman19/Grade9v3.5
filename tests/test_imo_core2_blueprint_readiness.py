"""Synthetic contract, negative-authority and privacy tests for Issue #165."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

FILE = Path(__file__).resolve().parents[1] / "TEST/imo-research/core2_blueprint_readiness.py"
spec = importlib.util.spec_from_file_location("core2_blueprint_readiness", FILE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class BlueprintReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.canonical_custody_pin = audit.CUSTODY_SCHEMA_BLOB_SHA
        self.canonical_blueprint_pin = audit.BLUEPRINT_REGISTRY_BLOB_SHA
        self.addCleanup(setattr, audit, "CUSTODY_SCHEMA_BLOB_SHA", self.canonical_custody_pin)
        self.addCleanup(setattr, audit, "BLUEPRINT_REGISTRY_BLOB_SHA", self.canonical_blueprint_pin)
        self.schema_dir = self.root / "Shared/library"
        self.bp_dir = self.root / "Shared/web"
        self.schema_dir.mkdir(parents=True)
        self.bp_dir.mkdir(parents=True)
        self.schema = {
            "$id": "https://grade9v3.local/source-question-custody.schema.json",
            "type": "object", "additionalProperties": False,
            "required": sorted(audit.PROOF_REQUIRED),
            "$defs": {"componentStatus": {"enum": [
                "PRESERVED", "NOT_PRESENT_IN_SOURCE", "EXTERNAL_REFERENCE_VERIFIED", "UNRESOLVED"]}},
            "properties": {
                "version": {"const": "1.0.0"},
                "acquisition_ref": {"type": "string"},
                "resource_ref": {"type": "string"},
                "source_item_locator": {"type": "string"},
                "source_digest": {"pattern": "^[0-9a-f]{64}$"},
                "custody_mode": {"enum": ["EMBEDDED_VERBATIM", "EXTERNAL_REFERENCE"]},
                "comparison_status": {"enum": ["ORIGINAL_EXACT", "ADAPTED_DECLARED", "UNRESOLVED"]},
                "demand_signature": {"pattern": "^[0-9a-f]{64}$"},
                "notes": {"type": "array"},
                "components": {
                    "type": "object", "additionalProperties": False,
                    "required": sorted(audit.NINE),
                    "properties": {k: {"$ref": "#/$defs/componentStatus"}
                                   for k in audit.NINE},
                },
            },
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
        custody = self.schema_dir / "source-question-custody.schema.json"
        blueprint = self.bp_dir / "interactive-page-blueprints.v1.json"
        custody.write_text(json.dumps(self.schema))
        blueprint.write_text(json.dumps(self.bp))
        # Synthetic mutation fixtures intentionally pin their own exact bytes.
        # The full-checkout test below separately re-enforces real main pins.
        audit.CUSTODY_SCHEMA_BLOB_SHA = audit._git_blob_sha(custody.read_bytes())
        audit.BLUEPRINT_REGISTRY_BLOB_SHA = audit._git_blob_sha(blueprint.read_bytes())

    def synthetic_cli(self, *args):
        # Each subprocess uses the same exact synthetic fixture pins as the
        # in-process tests. This is a TEST-ONLY bootstrap, never a production
        # environment override or a relaxation of the auditor's Git pins.
        bootstrap = (
            "import importlib.util,sys\n"
            "spec=importlib.util.spec_from_file_location('fixture_audit',sys.argv[1])\n"
            "mod=importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            "mod.CUSTODY_SCHEMA_BLOB_SHA=sys.argv[2]\n"
            "mod.BLUEPRINT_REGISTRY_BLOB_SHA=sys.argv[3]\n"
            "sys.argv=[sys.argv[1]]+sys.argv[4:]\n"
            "raise SystemExit(mod.main())\n"
        )
        return [sys.executable, "-c", bootstrap, str(FILE),
                audit.CUSTODY_SCHEMA_BLOB_SHA,
                audit.BLUEPRINT_REGISTRY_BLOB_SHA, *args]

    def test_production_cli_rejects_synthetic_contract_bytes(self):
        # Direct production entrypoint retains reviewed main contract pins.
        result = subprocess.run(
            [sys.executable, str(FILE), "report", "--repo-root", str(self.root)],
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CUSTODY_SCHEMA_BYTES_DRIFT", result.stderr)
        self.assertNotIn(str(self.root), result.stderr + result.stdout)

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
        row["historical_version_comparison"] = "NOT_CHECKED_NO_RETAINED_BYTES"
        out = audit.report(self.root, row)
        self.assertIn("SOURCE_OPERATOR_SELF_CHECK_NOT_COMPLETE", out["blockers"])

    def test_version_drift_status_stays_hold(self):
        row = self.verdict()
        row["status"] = "HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE"
        row["blocking_codes"] = ["SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED"]
        row["historical_version_comparison"] = "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION"
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

    def test_proof_top_level_requisite_drift_rejected(self):
        baseline = copy.deepcopy(self.schema)
        for mutation in (
            lambda schema: schema["required"].remove("source_digest"),
            lambda schema: schema["properties"]["custody_mode"].update(enum=["EMBEDDED_VERBATIM"]),
            lambda schema: schema["properties"]["comparison_status"].update(enum=["ORIGINAL_EXACT"]),
            lambda schema: schema["properties"]["source_digest"].update(pattern=".*"),
            lambda schema: schema.update(additionalProperties=True),
        ):
            with self.subTest(mutation=mutation):
                candidate = copy.deepcopy(baseline)
                mutation(candidate)
                self.schema = candidate
                self._write()
                with self.assertRaisesRegex(audit.AuditError, "CUSTODY_PROOF_TOP_LEVEL_DRIFT"):
                    audit.report(self.root)
        self.schema = baseline

    def test_required_blueprint_slot_reassignment_rejected(self):
        self.bp["blueprints"][0]["components"][0]["slot"] = "support"
        self._write()
        with self.assertRaisesRegex(audit.AuditError, "CORE2_BLUEPRINT_REQUIRED_COMPONENT_DRIFT"):
            audit.report(self.root)

    def test_repository_canonical_contracts_when_present(self):
        # Full-repository checkout executes this; isolated patch fixtures do not.
        checkout = Path(__file__).resolve().parents[1]
        if not (checkout / "Shared/web/interactive-page-blueprints.v1.json").is_file():
            strict = (os.environ.get("CI", "").lower() in ("1", "true", "yes")
                      or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
                      or os.environ.get("CORE2_REQUIRE_FULL_CHECKOUT") == "1")
            if strict:
                self.fail("full canonical registry missing in strict checkout validation")
            self.skipTest("full canonical registry not mounted in isolated patch test")
        self.assertTrue(
            (checkout / "Shared/library/source-question-custody.schema.json").is_file(),
            "full canonical custody schema missing")
        with (mock.patch.object(audit, "CUSTODY_SCHEMA_BLOB_SHA", self.canonical_custody_pin),
              mock.patch.object(audit, "BLUEPRINT_REGISTRY_BLOB_SHA",
                                self.canonical_blueprint_pin)):
            contracts = audit.canonical_contracts(checkout)
        self.assertEqual(contracts["blueprint_ref"],
                         "BP-CORE2-SOURCE-QUESTION@1.11.0")
        self.assertEqual(len(contracts["custody_component_names"]), 9)

    def test_production_cli_on_real_checkout_stays_hold(self):
        # Unlike synthetic subprocess fixtures, exercise the unmodified CLI
        # against the real checked-out canonical schema and blueprint bytes.
        checkout = Path(__file__).resolve().parents[1]
        registry = checkout / "Shared/web/interactive-page-blueprints.v1.json"
        custody = checkout / "Shared/library/source-question-custody.schema.json"
        if not (registry.is_file() and custody.is_file()):
            strict = (os.environ.get("CI", "").lower() in ("1", "true", "yes")
                      or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
                      or os.environ.get("CORE2_REQUIRE_FULL_CHECKOUT") == "1")
            if strict:
                self.fail("production CLI requires full canonical checkout")
            self.skipTest("real checkout unavailable to production CLI smoke test")
        result = subprocess.run(
            [sys.executable, str(FILE), "report", "--repo-root", str(checkout)],
            capture_output=True, text=True, check=False, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "HOLD_MISSING_EVIDENCE")
        self.assertEqual(data["spotcheck"]["state"], "NO_VERDICT_SUPPLIED")
        self.assertEqual(data["contracts"]["blueprint_ref"],
                         "BP-CORE2-SOURCE-QUESTION@1.11.0")
        self.assertEqual(len(data["contracts"]["custody_component_names"]), 9)
        for key in ("rights_granted", "independent_review_accepted",
                    "core2_eligible", "core2_admitted", "learner_published"):
            self.assertIs(data[key], False)
        self.assertNotIn(str(checkout), result.stdout + result.stderr)

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
            self.synthetic_cli("report", "--repo-root", str(self.root),
                               "--spotcheck-verdict", str(candidate)),
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(secret, result.stderr + result.stdout)
        self.assertNotIn(str(candidate), result.stderr + result.stdout)
        self.assertIn("SPOTCHECK_METADATA_INVALID", result.stderr)

    def test_cli_default_success_never_prints_raw_source(self):
        result = subprocess.run(
            self.synthetic_cli("report", "--repo-root", str(self.root)),
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

    def test_verdict_version_status_mismatch_is_rejected(self):
        samples = (
            ("SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED", "NOT_CHECKED_NO_RETAINED_BYTES", []),
            ("HOLD_RETAINED_SOURCE_NOT_VERIFIED", "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY",
             ["PRIVATE_RETAINED_PDF_RECEIPT_MISSING_OR_INVALID"]),
            ("HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE", "NOT_CHECKED_INVALID_RECEIPT",
             ["SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED"]),
            ("HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE", "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION",
             ["NINE_COMPONENT_SELF_CHECK_INCOMPLETE"]),
        )
        for status, version, codes in samples:
            with self.subTest(status=status):
                row = self.verdict()
                row.update(status=status, historical_version_comparison=version,
                           blocking_codes=codes)
                if status != "SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED":
                    row["component_check_complete"] = False
                with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_INCONSISTENT"):
                    audit.report(self.root, row)

    def test_unhashable_status_or_version_is_safe_hold(self):
        for key in ("status", "historical_version_comparison"):
            with self.subTest(key=key):
                row = self.verdict()
                row[key] = ["not", "a", "status"]
                with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_INVALID"):
                    audit.report(self.root, row)

    def test_verdict_unrecognized_version_is_rejected(self):
        row = self.verdict()
        row["historical_version_comparison"] = "ACTUALLY_LICENSED_AND_VERIFIED"
        with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_INVALID"):
            audit.report(self.root, row)

    def test_malformed_schema_shapes_return_safe_drift_code(self):
        baseline = copy.deepcopy(self.schema)
        variants = (
            ("required", ["invalid", {"bad": "unhashable"}]),
            ("$defs", ["invalid"]),
            ("properties", {**self.schema["properties"], "version": ["invalid"]}),
            ("properties", {**self.schema["properties"], "custody_mode": ["invalid"]}),
        )
        for field, value in variants:
            with self.subTest(field=field, shape=repr(value)[:40]):
                self.schema = copy.deepcopy(baseline)
                self.schema[field] = copy.deepcopy(value)
                self._write()
                with self.assertRaises(audit.AuditError):
                    audit.report(self.root)
        self.schema = baseline

    def test_blueprint_duplicate_nonrequired_and_malformed_slot_rejected(self):
        original = copy.deepcopy(self.bp)
        for transform in (
            lambda bp: bp["blueprints"][0]["components"].append(
                {"id": "IDENTITY", "level": "EXPECTED", "slot": "identity"}),
            lambda bp: bp["blueprints"][0]["slots"].append({"id": ["invalid"]}),
            lambda bp: bp["blueprints"][0]["components"][0].update(id=["invalid"]),
        ):
            self.bp = copy.deepcopy(original)
            transform(self.bp)
            self._write()
            with self.assertRaisesRegex(audit.AuditError, "CORE2_BLUEPRINT_REQUIRED_COMPONENT_DRIFT"):
                audit.report(self.root)
        self.bp = original

    def test_fifo_verdict_is_rejected_without_blocking(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO unsupported on this operating system")
        fifo = self.root / "blocked.fifo"
        os.mkfifo(fifo)
        result = subprocess.run(
            self.synthetic_cli("report", "--repo-root", str(self.root),
                               "--spotcheck-verdict", str(fifo)),
            capture_output=True, text=True, check=False, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SPOTCHECK_METADATA_UNAVAILABLE", result.stderr)
        self.assertNotIn(str(fifo), result.stdout + result.stderr)

    def test_json_reader_rejects_directory_and_nonobject(self):
        with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_UNAVAILABLE"):
            audit._read_json(self.root, "SPOTCHECK_METADATA_UNAVAILABLE", size_limit=1024)
        item = self.root / "list.json"
        item.write_text("[1,2,3]")
        with self.assertRaisesRegex(audit.AuditError, "SPOTCHECK_METADATA_UNAVAILABLE"):
            audit._read_json(item, "SPOTCHECK_METADATA_UNAVAILABLE", size_limit=1024)

    def test_duplicate_json_keys_and_nonfinite_values_fail_closed(self):
        candidate = self.root / "spoofed.json"
        for raw in ('{"schema":"a","schema":"b"}', '{"n":NaN}',
                    '{"n":Infinity}', '{"n":-Infinity}'):
            with self.subTest(raw=raw):
                candidate.write_text(raw)
                with self.assertRaisesRegex(audit.AuditError,
                                            "SPOTCHECK_METADATA_UNAVAILABLE"):
                    audit._read_json(candidate, "SPOTCHECK_METADATA_UNAVAILABLE",
                                     size_limit=audit.MAX_METADATA_BYTES)

    def test_deeply_nested_json_fails_without_traceback(self):
        candidate = self.root / "private-question-file.json"
        candidate.write_text('{' + '"a":' * 1200 + 'null' + '}' * 1200)
        result = subprocess.run(
            self.synthetic_cli("report", "--repo-root", str(self.root),
                               "--spotcheck-verdict", str(candidate)), capture_output=True,
            text=True, check=False, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SPOTCHECK_METADATA_UNAVAILABLE", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn(str(candidate), result.stderr + result.stdout)

    def test_unsafe_registry_version_never_reflected(self):
        sensitive = "private source text must stay private"
        self.bp["registry_version"] = {"untrusted": sensitive}
        self._write()
        with self.assertRaisesRegex(audit.AuditError,
                                    "CORE2_BLUEPRINT_MISSING_OR_DRIFTED"):
            audit.report(self.root)
        result = subprocess.run(
            self.synthetic_cli("report", "--repo-root", str(self.root)),
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(sensitive, result.stdout + result.stderr)

    def test_byte_exact_canonical_contract_pins_reject_cosmetic_drift(self):
        custody = self.schema_dir / "source-question-custody.schema.json"
        custody.write_bytes(custody.read_bytes() + b" ")
        with self.assertRaisesRegex(audit.AuditError, "CUSTODY_SCHEMA_BYTES_DRIFT"):
            audit.report(self.root)
        self._write()
        registry = self.bp_dir / "interactive-page-blueprints.v1.json"
        registry.write_bytes(registry.read_bytes() + b" ")
        with self.assertRaisesRegex(audit.AuditError, "CORE2_BLUEPRINT_BYTES_DRIFT"):
            audit.report(self.root)

    def test_upstream_spotcheck_statuses_are_only_reported_holds(self):
        # Mirrors the four statuses and four source-version tokens in draft
        # PR #145's q004_private_spotcheck.py. Not a live cross-branch test.
        cases = (
            ("HOLD_RETAINED_SOURCE_NOT_VERIFIED", "NOT_CHECKED_NO_RETAINED_BYTES",
             ["PRIVATE_RETAINED_PDF_RECEIPT_MISSING_OR_INVALID"], False),
            ("HOLD_RETAINED_SOURCE_NOT_VERIFIED", "NOT_CHECKED_INVALID_RECEIPT",
             ["PRIVATE_RETAINED_PDF_RECEIPT_MISSING_OR_INVALID"], False),
            ("HOLD_SOURCE_VERSION_DIFFERS_FROM_HISTORICAL_PROBE",
             "DIFFERS_FROM_HISTORICAL_EPHEMERAL_BYTES_REVIEW_VERSION",
             ["SOURCE_VERSION_MATCH_TO_HISTORICAL_PROBE_UNCONFIRMED"], False),
            ("HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE",
             "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY",
             ["NINE_COMPONENT_SELF_CHECK_INCOMPLETE"], False),
            ("SELF_SPOT_CHECK_COMPLETE_NOT_CORE2_OR_RIGHTS_AUTHORIZED",
             "MATCHES_HISTORICAL_EPHEMERAL_BYTES_ONLY", [], True),
        )
        for status, version, blockers, complete in cases:
            with self.subTest(status=status, version=version):
                row = self.verdict()
                row.update(status=status, historical_version_comparison=version,
                           blocking_codes=blockers, component_check_complete=complete)
                report = audit.report(self.root, row)
                self.assertEqual(report["decision"], "HOLD_MISSING_EVIDENCE")
                self.assertEqual(report["spotcheck"]["operator_self_check_claimed"], complete)
                for key in ("rights_granted", "independent_review_accepted",
                            "core2_eligible", "core2_admitted", "learner_published"):
                    self.assertIs(report[key], False)

    def test_untrusted_blocking_code_not_copied(self):
        row = self.verdict()
        row["status"] = "HOLD_SPOTCHECK_COMPONENTS_INCOMPLETE"
        row["component_check_complete"] = False
        row["blocking_codes"] = ["PRIVATE_METADATA_ONLY"]
        out = audit.report(self.root, row)
        self.assertNotIn("PRIVATE_METADATA_ONLY", json.dumps(out))


if __name__ == "__main__":
    unittest.main()
