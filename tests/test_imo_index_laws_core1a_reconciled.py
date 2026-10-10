"""Single held Index Laws Core1A candidate reconciled from historical #308 and #312.

A TEST mathematical teaching product is not a source/Core2 admission,
approved subtopic mapping, publication decision or human academic signoff.
"""
from __future__ import annotations

import json
import math
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

from Shared.library.resolve import validate_library
from Shared.tools import product_manifest, render_core

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.test.manifest.json"
RECON = ROOT / "TEST/imo-research/intake/imo-index-laws-core1a-308-312-reconciliation.v1.json"
F01 = ROOT / "TEST/imo-research/intake/imo-index-laws-subtopic-pilot.v1.json"
CAP = "CAP-TEST-IMO-G9-COMMON-EXPONENTIAL-QUANTITY"
MIC = "MIC-TEST-IMO-G9-COMMON-BASE-RELATION"
ANCHOR = "Q-TEST-IMO-G9-Q26-CORE1A-WORKED-ANCHOR"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_general_solution(a: int, k: int) -> float | None:
    """a^(2x+1)=(a*a)^x+k for real x and integer a>1."""
    if a <= 1:
        raise ValueError("Positive base must exceed 1")
    t = k / (a - 1)
    if t <= 0:
        return None
    return math.log(t, a) / 2


class VisiblePreAttempt(HTMLParser):
    """Text visible on a fresh page; protected templates are inert."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.omit = 0
        self.lines = []

    def handle_starttag(self, tag, attrs):
        if tag in {"template", "script", "style"}:
            self.omit += 1

    def handle_endtag(self, tag):
        if tag in {"template", "script", "style"}:
            self.omit -= 1

    def handle_data(self, data):
        if not self.omit:
            self.lines.append(data)


class IndexLawsCore1AReconciled(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = read(PKG)
        cls.m = read(MANIFEST)
        cls.r = read(RECON)
        cls.crosswalk = read(F01)
        cls.mic = cls.p["microtopics"][0]

    def test_one_academic_identity_not_two_cherrypicked_draft_versions(self):
        self.assertEqual(self.p["package_id"], "TEST-IMO-G9-CORE1A-COMMON-BASE-PILOT")
        self.assertEqual(self.r["historical_prs"][0]["pr"], 308)
        self.assertEqual(self.r["historical_prs"][1]["pr"], 312)
        self.assertEqual(self.r["candidate_package_ref"], PKG.relative_to(ROOT).as_posix())
        self.assertEqual(self.crosswalk["authored_teaching_candidate"]["package_id"], self.p["package_id"])
        self.assertEqual(self.crosswalk["scope"]["subtopic_id"], "NS-INDEX-LAWS")
        self.assertEqual(self.r["status"], "ENGINEERING_CANDIDATE_PENDING_INDEPENDENT_ACADEMIC_REVIEW")
        self.assertFalse(self.r["route_approved"])
        self.assertIsNone(self.r["approved_microtopic_id"])
        self.assertEqual(self.r["academic_review"]["state"], "NOT_RUN")

    def test_no_source_assessment_or_unapproved_question_role_selected(self):
        self.assertEqual(self.p["subject"], "TEST")
        self.assertEqual(self.p["status"], "CANDIDATE")
        self.assertEqual(self.p["curriculum_mappings"], [])
        self.assertEqual(self.p["resources"][0]["origin"], "AUTHORED")
        self.assertEqual(self.p["resources"][0]["source_refs"], [])
        self.assertEqual(self.p["questions"][0]["origin"], "AUTHORED")
        self.assertEqual([q["id"] for q in self.p["questions"]], [ANCHOR])
        self.assertNotIn("SOF-IMO-G09", PKG.read_text(encoding="utf-8"))
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:learner_published"])
        self.assertFalse(self.p["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertFalse(self.r["canonical_acceptance"])
        self.assertFalse(self.r["core2a_admitted"])
        self.assertFalse(self.r["core2_custody_granted"])
        self.assertFalse(self.r["owner_product_decision"])

    def test_stage_a_core1a_only_selection_is_real_and_single(self):
        self.assertEqual(self.m["subject"], "TEST")
        self.assertEqual(self.m["output_roles"], ["CORE1A"])
        self.assertEqual(product_manifest.selected_output_roles(self.m), ["CORE1A"])
        self.assertEqual(self.m["package_refs"], [PKG.relative_to(ROOT).as_posix()])
        self.assertEqual(self.m["selection"]["microtopics"], [MIC])
        for role in ("core2", "core2a", "core2b"):
            self.assertEqual(self.m["selection"][role], [])
        self.assertEqual(self.m["bank_refs"], [])
        result = product_manifest.validate_selection(self.m, [self.p], [])
        self.assertEqual(len(result["microtopics"]), 1)
        self.assertEqual(len(result["core2"]), 0)

    def test_package_schema_and_resolver_real_graph(self):
        from jsonschema import Draft202012Validator
        schema = read(ROOT / "Shared/library/package.schema.json")
        errors = list(Draft202012Validator(schema).iter_errors(self.p))
        self.assertEqual(errors, [], [e.message for e in errors])
        graph = validate_library([self.p])
        self.assertEqual(graph["unresolved_references"], 0)

    def test_complete_core1a_teaching_worked_anchor_and_third_repair(self):
        m = self.mic
        self.assertEqual(m["primary_capability_ref"], CAP)
        self.assertEqual([step["id"] for step in m["teaching_path"]],
                         ["TC-01", "TC-02", "TC-03", "TC-04", "TC-05"])
        self.assertEqual(len(m["misconceptions"]), 3)
        c = m["construction_units"][0]
        self.assertEqual(c["worked_anchor_ref"], ANCHOR)
        self.assertEqual(c["misconception_indexes"], [0, 1, 2])
        self.assertEqual(c["step_refs"], [step["id"] for step in m["teaching_path"]])
        for step in m["teaching_path"]:
            self.assertGreater(len(step["action"]), 50)
            self.assertGreater(len(step["why_valid"]), 60)
        third = m["misconceptions"][2]
        self.assertIn("2x=4", third["repair"])
        self.assertIn("x=2", third["repair"])
        self.assertIn("x=4", third["repair"])
        self.assertIn("19683", third["repair"])
        self.assertIn("6723", third["repair"])
        self.assertIn("original", third["repair"])

    def test_original_equations_solved_and_false_inversion_rejected(self):
        for a, k, expected, exact_lhs in (
            (3, 162, 2, 243),
            (2, 64, 3, 128),
        ):
            with self.subTest(a=a, k=k):
                solution = exact_general_solution(a, k)
                self.assertIsNotNone(solution)
                self.assertAlmostEqual(solution, expected)
                self.assertEqual(a**(2*expected+1), exact_lhs)
                self.assertEqual((a*a)**expected+k, exact_lhs)
        self.assertEqual(3**(2*4+1), 19683)
        self.assertEqual(9**4+162, 6723)
        self.assertNotEqual(3**(2*4+1), 9**4+162)

    def test_power_offset_and_domain_falsifiers(self):
        for a in (2, 3, 4, 7):
            for x in (-2.25, -0.5, 0, 0.75, 2):
                t = a**(2*x)
                self.assertGreater(t, 0)
                self.assertTrue(math.isclose((a*a)**x, t, rel_tol=1e-12))
                self.assertTrue(math.isclose(a**(2*x+1), a*t, rel_tol=1e-12))
            for k in (-5, 0, -100):
                self.assertIsNone(exact_general_solution(a, k))
        self.assertIsNone(self.r["academic_review"]["decision"])

    def test_independent_exit_is_not_anchor_and_has_reasoned_verification(self):
        exit_task = self.mic["exit_task"]
        self.assertIn("2^(2y+1)=4^y+64", exit_task["prompt"])
        self.assertNotIn("3^(2x+1)=9^x+162", exit_task["prompt"])
        self.assertEqual(exit_task["answer"]["verification_status"], "CHECKED_BY_AUTHOR")
        self.assertEqual(len(exit_task["answer"]["reasoning"]), 4)
        self.assertIn("128", exit_task["answer"]["reasoning"][-1])
        self.assertIn("nonpositive", json.dumps(self.mic["misconceptions"]))
        self.assertNotEqual(self.p["questions"][0]["stem"], exit_task["prompt"])

    def test_three_stage_authored_figure_is_parseable_and_source_safe(self):
        rep = self.p["representations"][0]
        self.assertEqual(len(self.p["representations"]), 1)
        self.assertEqual([s["id"] for s in rep["reveal_stages"]],
                         ["Q26-BASE", "Q26-FACTOR", "Q26-SOLVE"])
        path = ROOT / rep["rendered_asset_refs"][0]
        svg = path.read_text(encoding="utf-8")
        root = ElementTree.fromstring(svg)
        self.assertIn("aria-label", root.attrib)
        self.assertIn("<title>", svg)
        self.assertIn("<desc>", svg)
        stage_ids = [node.attrib["data-g9-stage-id"]
                     for node in root.iter() if "data-g9-stage-id" in node.attrib]
        self.assertEqual(stage_ids, ["Q26-BASE", "Q26-FACTOR", "Q26-SOLVE"])
        self.assertNotIn("SOF-IMO-G09", svg)
        self.assertNotIn("16^u", svg)

    def test_independent_exit_answer_cannot_leak_via_quick_checks(self):
        checks = self.mic["construction_units"][0]["independent_checks"]
        self.assertEqual(len(checks), 2)
        self.assertNotIn("y=3", json.dumps(checks))
        self.assertIn("verify your own proposed y", checks[1]["statement"])
        pages, _, _, _, _ = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        html = pages["core1a.html"]
        visible = VisiblePreAttempt()
        visible.feed(html)
        raw = " ".join(visible.lines)
        self.assertNotRegex(raw, r"\\by\\s*=\\s*3\\b")
        self.assertNotIn("unique real solution y=3", raw)
        self.assertNotIn("2^7=128", raw)
        # The complete worked *teaching* example x=2 is permitted, but
        # the fresh base-2 exit model answer remains protected in template.
        self.assertIn("unique real solution is x=2", raw)
        self.assertIn('data-g9-payload="CORE1A-', html)
        self.assertIn("unique real solution y=3", html)

    def test_f01_source_roles_and_routing_remain_held(self):
        rows = self.crosswalk["source_questions"]
        self.assertEqual([r["question_id"] for r in rows],
                         ["SOF-IMO-G09-L1-2024-25-B-Q026",
                          "SOF-IMO-G09-L1-2025-26-A-Q035"])
        self.assertTrue(all(not q["source_core2_admitted"] and
                            q["disposition"] == "SOURCE_CUSTODY_HOLD"
                            for q in rows))
        self.assertIsNone(self.crosswalk["routing"]["core1a_product_url"])
        self.assertEqual(self.crosswalk["routing"]["learner_publication_status"],
                         "HELD_NOT_GENERATED")
        self.assertFalse(self.crosswalk["scope"]["launch_authorized"])
        self.assertIsNone(self.r["owner_product_decision"])

    def test_actual_renderer_build_core1a_only_without_publisher_core2(self):
        pages, gaps, digest, advisories, waived = render_core.build_report(
            MANIFEST, "PAGES", held_to="FLOOR")
        self.assertEqual(set(pages), {"index.html", "core1a.html"})
        self.assertEqual(len(digest), 16)
        html = pages["core1a.html"]
        for phrase in ("3^(2x+1)=9^x+162", "2^(2y+1)=4^y+64",
                       "Why valid", "Model answer", "Q26-BASE"):
            self.assertIn(phrase, html)
        self.assertNotIn("SOF-IMO-G09", html)
        self.assertNotIn("Original paper question", html)
        self.assertNotIn('href="core2.html"', html)
        self.assertEqual([g for g in gaps
                          if g["duty"] == "PRODUCT_SELECTION_UNRESOLVED"], [])
        self.assertIsInstance(advisories, list)


if __name__ == "__main__":
    unittest.main()
