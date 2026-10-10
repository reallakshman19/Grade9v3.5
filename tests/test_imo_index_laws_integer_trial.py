"""Separate, unpublished Core1A trial: integer exponents and protected boundary.

No academic acceptance or authentic SOF question admission is supplied by
a valid package, exact mathematical tests or a TEST-only renderer.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree

from Shared.library.resolve import validate_library
from Shared.tools import product_manifest, render_core

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "TEST/imo-research/candidates/imo-g9-index-laws-integer-core1a.v1.json"
M = ROOT / "TEST/imo-research/candidates/imo-g9-index-laws-integer-core1a.test.manifest.json"
FIG = ROOT / "TEST/imo-research/candidates/assets/REP-TEST-IMO-G9-COMMON-BASE-INTEGER.svg"
N = ROOT / "TEST/imo-research/intake/imo-index-laws-integer-domain-trial.v1.json"
ORIGINAL = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
REVIEW = ROOT / "TEST/imo-research/intake/imo-index-laws-core1a-curriculum-review-2026-27.v1.json"
STAGE = ROOT / "TEST/imo-research/intake/imo-index-laws-route-staging.v1.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class PreAttemptText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag in ("template", "script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("template", "script", "style"):
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


class IntegerIndexLawsCore1ATrial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = read(P)
        cls.m = read(M)
        cls.n = read(N)
        cls.original = read(ORIGINAL)
        cls.review = read(REVIEW)
        cls.mic = cls.p["microtopics"][0]

    def test_new_package_and_ids_are_isolated_from_real_domain_original(self):
        self.assertNotEqual(self.p["package_id"], self.original["package_id"])
        self.assertEqual(self.p["status"], "CANDIDATE")
        self.assertEqual(self.p["subject"], "TEST")
        for key in ("resources", "buckets", "capabilities", "microtopics",
                    "relations", "representations", "question_families",
                    "questions", "teaching_routes"):
            previous = {x["id"] for x in self.original[key]}
            current = {x["id"] for x in self.p[key]}
            self.assertFalse(previous & current, (key, previous & current))
        self.assertTrue(self.n["original_real_domain_package_unchanged"])
        self.assertEqual(self.n["original_real_domain_package_id"],
                         self.original["package_id"])
        self.assertEqual(self.n["pkg_ref"], P.relative_to(ROOT).as_posix())

    def test_proposal_packet_and_academic_gate_remain_unresolved(self):
        self.assertEqual(self.review["decision"]["status"],
                         "AWAITING_NAMED_INDEPENDENT_SUBJECT_REVIEW")
        self.assertIsNone(self.review["decision"]["human_reviewer_name"])
        self.assertTrue(all(v is None for v in self.review["decision"]["choices"].values()))
        self.assertIsNone(self.n["academic"]["independent_reviewer"])
        self.assertIsNone(self.n["academic"]["accepted_microtopic_id"])
        self.assertFalse(self.n["release"]["approved"])
        self.assertFalse(self.n["release"]["owner_product_acceptance"])
        self.assertFalse(self.n["release"]["merge_allowed"])
        self.assertEqual(read(STAGE)["status"], "DRAFT_NAVIGATION_STAGED_ACADEMIC_HOLD")

    def test_actual_schema_resolver_and_selection_no_source_core2(self):
        from jsonschema import Draft202012Validator
        schema = read(ROOT / "Shared/library/package.schema.json")
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(self.p)), [])
        graph = validate_library([self.p])
        self.assertEqual(graph["unresolved_references"], 0)
        self.assertEqual(self.m["package_refs"], [P.relative_to(ROOT).as_posix()])
        self.assertEqual(product_manifest.selected_output_roles(self.m), ["CORE1A"])
        selected = product_manifest.validate_selection(self.m, [self.p], [])
        self.assertEqual(len(selected["microtopics"]), 1)
        for role in ("core2", "core2a", "core2b"):
            self.assertEqual(self.m["selection"][role], [])
        self.assertEqual(self.m["bank_refs"], [])
        self.assertEqual(self.p["questions"][0]["origin"], "AUTHORED")
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:learner_published"])
        self.assertFalse(self.p["extensions"]["grade9v3:academic_acceptance"])

    def test_worked_anchor_exact_equivalence_over_nonnegative_integers(self):
        self.assertEqual([n for n in range(0, 700)
                          if 3 ** (2 * n + 1) == 9 ** n + 162], [2])
        self.assertEqual(3**5, 9**2 + 162)
        for n in range(0, 30):
            self.assertEqual(9 ** n, 3 ** (2 * n))
            self.assertEqual(3 ** (2 * n + 1), 3 * 9 ** n)
        self.assertEqual(len(self.mic["teaching_path"]), 5)
        for step in self.mic["teaching_path"]:
            self.assertGreater(len(step["action"]), 50)
            self.assertGreater(len(step["why_valid"]), 55)
        self.assertIn("non-negative integer n", self.mic["teaching_path"][0]["action"])
        self.assertIn("2n=4", self.mic["teaching_path"][3]["action"])

    def test_independent_exit_a_and_boundary_b_are_distinct_from_anchor(self):
        self.assertEqual([m for m in range(0, 300)
                          if 2 ** (2 * m + 1) == 4 ** m + 64], [3])
        self.assertEqual([m for m in range(0, 300)
                          if 2 ** (2 * m + 1) == 4 ** m + 8], [])
        self.assertEqual(2**7, 4**3 + 64)
        self.assertEqual(2**4, 4**1.5 + 8)
        exit_task = self.mic["exit_task"]
        self.assertIn("BOTH", exit_task["prompt"])
        self.assertIn("2^(2m+1)=4^m+64", exit_task["prompt"])
        self.assertIn("2^(2m+1)=4^m+8", exit_task["prompt"])
        self.assertEqual(exit_task["answer"]["verification_status"], "CHECKED_BY_AUTHOR")
        self.assertEqual(len(exit_task["answer"]["reasoning"]), 5)

    def test_positive_t_is_not_a_whole_number_power_membership_oracle(self):
        self.assertTrue(12 > 0)
        self.assertNotIn(12, [4**m for m in range(0, 40)])
        self.assertEqual(4**1, 4)
        self.assertEqual(4**2, 16)
        self.assertEqual(len(self.mic["misconceptions"]), 3)
        diagnostic = self.mic["misconceptions"][1]
        self.assertIn("t=12", diagnostic["diagnostic_prompt"])
        self.assertIn("insufficient", diagnostic["repair"])
        self.assertIn("2n=4", self.mic["misconceptions"][2]["repair"])

    def test_original_svg_stages_are_distinct_and_no_exit_answer_leaks(self):
        root = ElementTree.fromstring(FIG.read_text(encoding="utf-8"))
        ids = [x.attrib["data-g9-stage-id"]
               for x in root.iter() if "data-g9-stage-id" in x.attrib]
        expected = ["Q26-BASE-INTEGER", "Q26-FACTOR-INTEGER",
                    "Q26-SOLVE-INTEGER"]
        self.assertEqual(ids, expected)
        self.assertEqual([s["id"] for s in self.p["representations"][0]["reveal_stages"]], expected)
        self.assertEqual(self.mic["construction_units"][0]["reveal_stage_refs"], expected)
        svg = FIG.read_text(encoding="utf-8")
        for banned in ("2^(2m+1)", "m=3", "m=3/2", "4^m=8"):
            self.assertNotIn(banned, svg)
        self.assertIn('role="img"', svg)
        self.assertIn("<title>", svg)
        self.assertIn("<desc>", svg)

    def test_preattempt_open_content_cannot_reveal_independent_answer(self):
        open_records = [
            self.p["resources"][0]["supports_claims"],
            self.mic["teaching_path"],
            self.mic["misconceptions"],
            self.mic["construction_units"],
            self.p["representations"],
            self.p["relations"],
            self.p["teaching_routes"]
        ]
        visible = json.dumps(open_records)
        for leaked in ("m=3", "m=3/2", "2m=3", "4^m=8"):
            self.assertNotIn(leaked, visible)
        checks = self.mic["construction_units"][0]["independent_checks"]
        self.assertIn("After attempting", checks[1]["statement"])
        self.assertNotIn("m=3", json.dumps(checks))

    def test_actual_core1a_html_uses_protected_attempt_gate(self):
        pages, gaps, digest, advisories, waived = render_core.build_report(
            M, "PAGES", held_to="REFERENCE")
        self.assertEqual(set(pages), {"index.html", "core1a.html"})
        self.assertEqual(len(digest), 16)
        self.assertEqual(gaps, [])
        html = pages["core1a.html"]
        parser = PreAttemptText()
        parser.feed(html)
        raw = " ".join(parser.text)
        for leaked in ("m=3/2", "2m=3", "real m gives",
                       "m=3 is the unique", "For the distinct real domain"):
            self.assertNotIn(leaked, raw)
        self.assertIn("2^(2m+1)=4^m+64", raw)
        self.assertIn("2^(2m+1)=4^m+8", raw)
        self.assertIn("Q26-BASE-INTEGER", html)
        self.assertIn("m=3/2", html)  # Gated model closure exists, not initially visible.
        self.assertIn("n=2", raw)  # Authored worked anchor is pedagogically public.
        self.assertNotIn("SOF-IMO-G09-L1", raw)

    def test_public_and_owner_release_are_unchanged(self):
        self.assertIsNone(read(STAGE)["core1a"]["public_product_url"])
        self.assertFalse(read(STAGE)["release"]["owner_channel_authorized"])
        self.assertEqual(self.n["selection_policy"].startswith("Selected only"), True)
        self.assertEqual(self.n["source_core2_admitted"], 0)
        self.assertEqual(self.n["source_positions_held"], 68)
        self.assertEqual(self.n["qrt_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
