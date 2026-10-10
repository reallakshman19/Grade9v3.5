"""F04 safe-summary route denial: executable locally without renderer or Actions."""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

from Shared.tools.imo_f04_route_gate import main, verdict, REQUIRED_ROUTES


def safe_report():
    return {
        "schema": "agent3-imo-f04-canonical-vertical-slice/v1",
        "blocking_findings": [], "blueprint_refs": {
            "CORE1A": "BP-CORE1A-CONSTRUCTION@1.8.0",
            "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0"},
        "qrt_cell": "QRT-MODEL-D3", "source_contract_status": "HOLD_NOT_ACCEPTED",
        "release_authorized": False, "render_status": "REAL_CANONICAL_TEST_RENDER",
        "integration_findings": [], "quality_gate_verdict": "FAIL",
        "state": "EVIDENCE_READY_REVIEW_HOLD",
    }


class RouteGateTests(unittest.TestCase):
    def test_structurally_valid_is_not_learner_acceptance(self):
        good, message = verdict(safe_report())
        self.assertTrue(good)
        self.assertIn("NO_LEARNER_ACCEPTANCE", message)

    def test_each_known_real_finding_blocks(self):
        for code in REQUIRED_ROUTES:
            with self.subTest(code=code):
                report = safe_report()
                report["integration_findings"] = [code]
                self.assertEqual(verdict(report), (False, "ROUTE_FINDINGS:" + code))

    def test_negative_missing_and_unknown_route_diagnostics_block(self):
        for value in (None, "", "secret", ["leakage-source-content"], [1]):
            with self.subTest(value=value):
                report = safe_report()
                report["integration_findings"] = value
                ok, message = verdict(report)
                self.assertFalse(ok)
                self.assertNotIn("leakage-source-content", message)

    def test_no_false_positive_on_lax_approval_or_blueprint(self):
        for field, bad in (
            ("release_authorized", True),
            ("source_contract_status", "APPROVED"),
            ("blueprint_refs", {}),
            ("blocking_findings", ["BLOCKED"]),
            ("render_status", "NOT_RUN"),
            ("qrt_cell", "QRT-MODEL-D2"),
        ):
            with self.subTest(field=field):
                report = safe_report()
                report[field] = bad
                self.assertFalse(verdict(report)[0])

    def test_actual_failure_codes_always_block_even_if_technical_audit_passed(self):
        old = safe_report()
        old["state"] = "INTEGRATION_GAPS_HELD"
        old["integration_findings"] = [
            "CORE1A_STEP_FRAGMENT_NOT_ADDRESSABLE",
            "CORE2A_NOT_LINKED_TO_EXACT_REPAIR_STEP",
            "CORE1A_AUTHORED_CORE2A_RETURN_ABSENT",
        ]
        good, reason = verdict(old)
        self.assertFalse(good)
        self.assertIn("CORE1A_STEP_FRAGMENT_NOT_ADDRESSABLE", reason)
        self.assertIn("CORE2A_NOT_LINKED_TO_EXACT_REPAIR_STEP", reason)
        self.assertIn("CORE1A_AUTHORED_CORE2A_RETURN_ABSENT", reason)

    def test_isolated_route_runner_checks_out_python_before_verdict(self):
        """Each GitHub Actions job has a fresh workspace; artifact != code checkout."""
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/imo-f04-canonical-qrt-blueprint.yml").read_text(
            encoding="utf-8")
        anchor = "\n  learner-route-acceptance:\n"
        self.assertEqual(workflow.count(anchor), 1,
                         "route gate must be tested as its own isolated runner")
        route = workflow.split(anchor, 1)[1]
        checkout = route.index("      - name: Check out route-gate source\n"
                               "        uses: actions/checkout@v4\n"
                               "        with:\n"
                               "          persist-credentials: false")
        artifact = route.index("uses: actions/download-artifact@v4")
        verdict = route.index("python -m Shared.tools.imo_f04_route_gate")
        self.assertLess(checkout, artifact)
        self.assertLess(artifact, verdict)
        self.assertIn("needs: canonical-qrt-blueprint", route)
        self.assertIn("if: always()", route)
        self.assertIn("contents: read", route)
        self.assertIn('name: imo-f04-canonical-safe-summary', route)
        self.assertIn('--summary "${{ runner.temp }}/imo-f04-route/imo-f04-summary.json"', route)
        # Changes to this gate or its own tests must not silently bypass CI.
        watched = workflow.split("\njobs:\n", 1)[0]
        self.assertIn('      - "Shared/tools/imo_f04_route_gate.py"', watched)
        self.assertIn('      - "tests/test_imo_f04_route_gate.py"', watched)

    def test_invalid_json_is_safe_failure(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "broken.json")
            path.write_text('{"secret":"protected solution"', encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["--summary", str(path)])
            self.assertEqual(code, 1)
            self.assertEqual(output.getvalue().strip(),
                             "F04_ROUTE_BLOCKED: UNREADABLE_SAFE_SUMMARY")


if __name__ == "__main__":
    unittest.main()
