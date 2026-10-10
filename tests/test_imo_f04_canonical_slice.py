"""Agent 3 F04: test actual Agent 2 authored candidate with governing tools.

No synthetic question is substituted for the TEST authored MODEL-D3 item.
A green structural test is not a QRT reviewer YES or learner publication.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import redirect_stdout
import io
from unittest.mock import patch
import json
from pathlib import Path
import unittest

from Shared.tools import question_review_matrix as qrt, web_blueprint_contract
from Shared.tools.imo_f04_canonical_slice import (
    BLUEPRINT_REFS, CELL, MANIFEST, MID, PACKAGE, QID, ROLES, STEP,
    held_candidate_findings, inspect_real_candidate, inspect_rendered,
    navigation_findings, question_by_id,
)


class IMOCanonicalSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.report = inspect_real_candidate()

    def test_actual_qrt_uses_seven_by_four_and_twelve_qualitative_asks(self):
        result = self.report["qrt"]
        self.assertEqual(result["template_id"], CELL)
        self.assertEqual(result["classification"]["demand"]["primary"], "MODEL")
        self.assertEqual(result["classification"]["band"], "D3")
        self.assertEqual(tuple(result["review_objectives"]), qrt.ASKS)
        self.assertEqual(len(result["review_objectives"]), 12)
        self.assertEqual(result["reviewer_verdicts"], "NOT_PROVIDED")
        self.assertEqual(result["profile_fit"], "NOT_MEASURED_DESIGN_PREVIEW")
        self.assertFalse(self.report["academic_accepted"])
        self.assertFalse(self.report["release_authorized"])

    def test_existing_agent2_source_bound_qrt_ledger_is_consumed_not_scored(self):
        owned = self.report["f02_source_ledger"]
        self.assertEqual(owned["status"], "SOURCE_MAPPED_SEMANTICS_NOT_REVIEWED")
        self.assertEqual(owned["selected_cell"], CELL)
        self.assertEqual(owned["academic_status"], "HOLD_NOT_ACCEPTED")
        self.assertEqual(owned["golden_reference_cells"],
                         ["QRT-EXPLAIN-D2", "QRT-MODEL-D3", "QRT-JUSTIFY-D4"])
        self.assertEqual(owned["errors"], [])
        self.assertEqual([a["ask"] for a in owned["semantic_review_asks"]], list(qrt.ASKS))
        self.assertFalse(any(a["status"] == "PASS"
                             for a in owned["semantic_review_asks"]))
        self.assertIn("M2_MISCONCEPTION_VS_EXECUTION_SLIP_NOT_TESTED",
                      owned["review_gates"])
        self.assertIn("P2_PRECISE_TC02_LEARNER_ROUTE_NOT_VERIFIED",
                      owned["review_gates"])

    def test_real_blueprints_and_real_renderer_are_consumed(self):
        bp = self.report["blueprints"]
        self.assertTrue(bp["registry_audit_passed"])
        self.assertEqual({r: bp["bindings"][r]["ref"] for r in ROLES}, BLUEPRINT_REFS)
        self.assertEqual(self.report["render"]["status"], "REAL_CANONICAL_TEST_RENDER")
        self.assertEqual(self.report["render"]["receipt"]["output_roles"], list(ROLES))
        self.assertEqual(self.report["render"]["pages"]["CORE1A"]["root_roles"], ["CORE1A"])
        self.assertEqual(self.report["render"]["pages"]["CORE2A"]["root_roles"], ["CORE2A"])
        self.assertFalse(self.report["quality_gate"]["rendered_measured"])
        self.assertNotEqual(self.report["quality_gate"]["verdict"], "PASS")
        self.assertEqual(self.report["browser_qa"], "NOT_RUN")

    def test_actual_selected_authored_question_and_protected_template(self):
        question = question_by_id(self.package)
        self.assertEqual(question["id"], QID)
        self.assertEqual(question["answer"]["crux_move_ref"], "MOVE-IMO-R1-FACTOR")
        self.assertEqual(question["repair_ref"], STEP)
        self.assertEqual(self.manifest["selection"]["microtopics"], [MID])
        rendered = self.report["render"]["pages"]
        self.assertIn(QID, rendered["CORE2A"]["article_ids"])
        self.assertIn(MID, rendered["CORE1A"]["article_ids"])
        self.assertIn(f"CORE2A-{QID}-reasoning", rendered["CORE2A"]["templates"])
        self.assertIn(f"CORE2A-{QID}-reasoning", rendered["CORE2A"]["attempt_detail_refs"])
        self.assertNotIn("CORE2", self.manifest["output_roles"])
        self.assertFalse(self.report["source_core2_eligible"])

    def test_negative_forged_roles_publication_question_and_source(self):
        cases = [
            ("forged_role", lambda m, p: m.__setitem__("output_roles", ["CORE1A", "CORE2"]), "UNAPPROVED_ROLE_SELECTION"),
            ("forged_source", lambda m, p: m["selection"].__setitem__("core2", [QID]), "SOURCE_OR_TRANSFER_NOT_AUTHORIZED"),
            ("forged_transfer", lambda m, p: m["selection"].__setitem__("core2b", [QID]), "SOURCE_OR_TRANSFER_NOT_AUTHORIZED"),
            ("wrong_question", lambda m, p: m["selection"].__setitem__("core2a", ["UNKNOWN"]), "WRONG_CORE2A_QUESTION"),
            ("wrong_microtopic", lambda m, p: m["selection"].__setitem__("microtopics", ["UNKNOWN"]), "WRONG_TEACHING_MICROTOPIC"),
            ("fake_release", lambda m, p: p["extensions"].__setitem__("grade9v3:learner_published", True), "FORGED_PUBLICATION_OR_ACADEMIC_GRANT"),
            ("fake_qrt", lambda m, p: p["extensions"].__setitem__("grade9v3:qrt_admitted", True), "FORGED_PUBLICATION_OR_ACADEMIC_GRANT"),
            ("swapped_package", lambda m, p: m.__setitem__("package_refs", ["TEST/swap.json"]), "MANIFEST_PACKAGE_AUTHORITY_DRIFT"),
        ]
        for label, modify, expected in cases:
            with self.subTest(label=label):
                m, p = deepcopy(self.manifest), deepcopy(self.package)
                modify(m, p)
                self.assertIn(expected, held_candidate_findings(m, p))

    def test_wrong_demand_and_stale_blueprint_are_not_accepted(self):
        q = deepcopy(question_by_id(self.package))
        q["extensions"]["grade9v3:cognitive_demand"]["primary"] = "MADE_UP"
        matrix = qrt.load(qrt.MATRIX_PATH)
        vocab = qrt.load(qrt.VOCAB_PATH)
        with self.assertRaises(qrt.QRTContractError):
            qrt.resolve_review(q, {"profile_id": "PROBE", "held": {}}, matrix, vocab)
        with self.assertRaises(web_blueprint_contract.WebBlueprintContractError):
            web_blueprint_contract.resolve_blueprint("BP-CORE1A-CONSTRUCTION@99.0.0")

    def test_mutated_actual_html_cannot_fake_core_role_or_attempt_gate(self):
        # Operates on the *real rendered bytes* captured by canonical renderer.
        from Shared.tools import render_core
        pages, _gaps, _digest, _advisories, _waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        clean, _issues = inspect_rendered(pages, BLUEPRINT_REFS)
        self.assertIn(QID, clean["CORE2A"]["article_ids"])
        modified = dict(pages)
        modified["core2a.html"] = modified["core2a.html"].replace(
            f'data-g9-payload="CORE2A-{QID}-reasoning"',
            'data-g9-payload="OTHER"', 1)
        _facts, issues = inspect_rendered(modified, BLUEPRINT_REFS)
        self.assertIn("CORE2A_REASONING_TEMPLATE_MISSING", issues)
        modified["core2a.html"] = pages["core2a.html"].replace(
            'data-g9-role="CORE2A"', 'data-g9-role="CORE2"', 1)
        _facts, issues = inspect_rendered(modified, BLUEPRINT_REFS)
        self.assertIn("CORE2A_BLUEPRINT_ROLE_MISMATCH", issues)
        # Mutate the actual rendered *article* role, not just the shell.
        import re
        modified["core2a.html"], changed = re.subn(
            r'(<article\\b[^>]*\\bid="' + re.escape(QID)
            + r'"[^>]*data-g9-role=")CORE2A(")',
            r'\\g<1>CORE2\\2', pages["core2a.html"], count=1)
        self.assertEqual(changed, 1)
        _facts, issues = inspect_rendered(modified, BLUEPRINT_REFS)
        self.assertIn("CORE2A_SELECTED_ARTICLE_MISSING", issues)
        # There is no valid attempt gate if the learner cannot submit.
        modified["core2a.html"] = pages["core2a.html"].replace(
            '<div class="g9-attempt" data-g9-attempt-box',
            '<div class="g9-attempt" data-g9-broken-attempt', 1)
        _facts, issues = inspect_rendered(modified, BLUEPRINT_REFS)
        self.assertIn("CORE2A_ATTEMPT_CONTROLS_MISSING", issues)

    def test_cli_stdout_is_safe_json_and_cannot_expose_protected_w(self):
        # The canonical resolver's W is intentionally retained in an
        # uncommitted local receipt, never streamed into public Actions logs.
        from Shared.tools.imo_f04_canonical_slice import main
        out = io.StringIO()
        with patch("sys.argv", ["imo_f04_canonical_slice.py"]), redirect_stdout(out):
            exit_code = main()
        printed = out.getvalue()
        status = json.loads(printed)
        self.assertEqual(exit_code, 0 if self.report["state"] != "BLOCKED" else 1)
        self.assertEqual(status["state"], self.report["state"])
        self.assertFalse(status["release_authorized"])
        self.assertNotIn("protected_W", printed)
        self.assertNotIn("review_objectives", printed)
        self.assertNotIn("semantic_review_asks", printed)
        protected = self.report["f02_source_ledger"]["protected_W"]
        self.assertTrue(protected)
        self.assertNotIn(protected, printed)

    def test_navigation_is_reported_as_evidence_not_autofixed(self):
        real = self.report["render"]["pages"]
        self.assertEqual(self.report["integration_findings"], navigation_findings(real))
        self.assertFalse(self.report["owner_merge_authorized"])
        self.assertEqual(self.report["human_learner_qrt_review"], "NOT_RUN")
        self.assertEqual(len(self.report["goldens"]), 3)
        self.assertTrue(all(x["independent_acceptance"] == "NOT_GRANTED"
                            for x in self.report["goldens"]))


if __name__ == "__main__":
    unittest.main()
