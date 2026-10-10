"""Alternative Core2B transfer mathematical falsifiers and academic HOLD — issue #164."""
from __future__ import annotations
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from Shared.tools import product_manifest, product_coverage, render_core

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
MANIFEST_FIVE = ROOT / "TEST/products/imo-g9-blueprint-first-five-transfer.manifest.json"
MANIFEST_BOUNDARY = ROOT / "TEST/products/imo-g9-blueprint-boundary-12-transfer.manifest.json"
COMPARISON = ROOT / "TEST/imo-research/pilots/transfer-comparison-164.v1.json"
SVG = ROOT / "TEST/imo-research/pilots/assets/triple-boundary-12-attempt-safe.svg"
FIVE = "Q-TEST-IMO-164-FIVE-CONSECUTIVE-120"
BOUNDARY = "Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY"

class Visible(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inert = 0
        self.output = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template"):
            self.inert += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "template"):
            self.inert -= 1
    def handle_data(self, value):
        if not self.inert:
            self.output.append(value)

class TransferComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.five_manifest = json.loads(MANIFEST_FIVE.read_text(encoding="utf-8"))
        cls.boundary_manifest = json.loads(MANIFEST_BOUNDARY.read_text(encoding="utf-8"))
        cls.review = json.loads(COMPARISON.read_text(encoding="utf-8"))
        cls.question = {q["id"]: q for q in cls.package["questions"]}

    def test_prove_exact_classification_with_complete_residue_classes(self):
        def p(n): return n * (n+1) * (n+2)
        # Each positive n is congruent to precisely one of 12 residues;
        # polynomial evaluation preserves congruence mod 12.
        for n in range(12):
            self.assertEqual(p(n) % 12 == 0, n % 4 != 1, n)
        self.assertEqual(p(1), 6)
        self.assertNotEqual(p(1) % 12, 0)
        # Extra falsifier range is corroboration, not a proof by sampling.
        for n in range(1, 601):
            self.assertEqual(p(n) % 12 == 0, n % 4 != 1, n)
        for n in range(4):
            factors = [n, n+1, n+2]
            if n == 1:
                self.assertTrue(all(x % 2 for x in (factors[0], factors[2])))
                self.assertEqual(factors[1] % 4, 2)
            else:
                self.assertTrue(any(x % 4 == 0 for x in factors))
        for n in range(120):
            self.assertEqual(p(n) * (n+3) * (n+4) % 120, 0)

    def test_distinct_protected_move_and_iff_reasoning(self):
        five, boundary = self.question[FIVE], self.question[BOUNDARY]
        self.assertEqual(five["transfer"]["dimension"], "reasoning_steps")
        self.assertEqual(boundary["transfer"]["dimension"], "model_choice")
        self.assertNotEqual(five["answer"]["crux_move_ref"],
                            boundary["answer"]["crux_move_ref"])
        self.assertEqual(boundary["transfer"]["protected_move_ref"],
                         boundary["answer"]["crux_move_ref"])
        solution = " ".join(boundary["answer"]["reasoning"])
        for necessary in ("n=1", "gcd(3,4)=1", "n mod 4", "necessity", "sufficiency"):
            self.assertIn(necessary, solution)
        self.assertIn("PROPOSED ONLY", boundary["difficulty"]["basis"])
        self.assertEqual(boundary["origin"], "AUTHORED")
        self.assertEqual(boundary["exposure"][0]["core"], "CORE2B")
        self.assertEqual(boundary["extensions"]["grade9v3:qrt_status"], "PROPOSED_NOT_ACCEPTED")
        self.assertEqual(boundary["hints"], [])
        self.assertEqual(boundary["scaffolds"], [])
        self.assertEqual(boundary["hint_ladder"], [])

    def test_two_manifests_select_one_transfer_and_explicitly_omit_the_other(self):
        for manifest in (self.five_manifest, self.boundary_manifest):
            with self.subTest(manifest=manifest["product_id"]):
                selected = set(manifest["selection"]["core2b"])
                omitted = set(manifest["coverage"]["omitted"])
                self.assertEqual(len(selected), 1)
                self.assertEqual(selected | omitted, {FIVE, BOUNDARY})
                self.assertFalse(selected & omitted)
                self.assertEqual(manifest["selection"]["core2"], [])
                self.assertEqual(manifest["bank_refs"], [])
                self.assertEqual(product_manifest.selected_output_roles(manifest),
                                 ["CORE2A","CORE1A","CORE2B"])
                product_manifest.validate_selection(manifest, [self.package], [])
                product_coverage.validate(manifest, product_manifest.derivable([self.package], []))
        self.assertEqual(self.five_manifest["selection"]["core2b"], [FIVE])
        self.assertEqual(self.boundary_manifest["selection"]["core2b"], [BOUNDARY])

    def test_safe_stages_do_not_expose_the_classification(self):
        asset = SVG.read_text(encoding="utf-8")
        root = ET.fromstring(asset)
        stages = [x.attrib["data-g9-stage-id"] for x in root.iter()
                  if "data-g9-stage-id" in x.attrib]
        self.assertEqual(stages, self.question[BOUNDARY]["representation_roles"]["stage_refs"])
        self.assertEqual(len(stages), 2)
        for leak in ("n mod 4 != 1", "n ≡ 1", "counterexample", "iff", "n=1", "false"):
            self.assertNotIn(leak, asset.lower())
        self.assertIn("12 divides P(n) for every n?", asset)

    def test_review_is_explicitly_not_academic_acceptance_or_sof_admission(self):
        r = self.review
        self.assertEqual(r["status"], "INDEPENDENT_ACADEMIC_REVIEW_PENDING")
        self.assertIsNone(r["selected_academic_variant"])
        self.assertIsNone(r["reviewer_name"])
        self.assertIsNone(r["reviewer_date"])
        self.assertFalse(r["independent_math_review"])
        self.assertFalse(r["qrt_accepted"])
        self.assertFalse(r["owner_publication_approved"])
        self.assertEqual(r["source_core2_admitted"], 0)
        self.assertEqual(r["source_positions_held"], 68)
        self.assertEqual({a["question_ref"] for a in r["alternatives"]}, {FIVE,BOUNDARY})

    @unittest.skipUnless(importlib.util.find_spec("jsonschema") is not None,
                         "full shared renderer requires jsonschema; dedicated CI installs it")
    def test_real_reference_render_two_variants_inert_proof_and_no_new_blueprint(self):
        for path, question_ref in ((MANIFEST_FIVE, FIVE), (MANIFEST_BOUNDARY, BOUNDARY)):
            with self.subTest(manifest=path.name):
                pages, gaps, digest, advisories, waivers = render_core.build_report(
                    path, "PAGES", held_to="REFERENCE")
                self.assertEqual(gaps, [], gaps)
                self.assertEqual(advisories, [], advisories)
                self.assertEqual(set(pages), {"index.html","core1a.html","core2a.html","core2b.html"})
                self.assertIn(question_ref, pages["core2b.html"])
                self.assertIn('data-g9-role="CORE2B"', pages["core2b.html"])
                self.assertIn('data-requires-attempt', pages["core2b.html"])
                self.assertIn("<template data-g9-payload=", pages["core2b.html"])
                parser = Visible()
                parser.feed(pages["core2b.html"])
                before = " ".join(parser.output)
                secret = "gcd(24,5)=1" if question_ref == FIVE else "n mod 4 != 1"
                self.assertIn(secret, pages["core2b.html"])
                self.assertNotIn(secret, before)
                self.assertNotIn("SOF-IMO-G09-", pages["core2b.html"])
                if question_ref == BOUNDARY:
                    self.assertIn('data-g9-stage="PRE_ATTEMPT"', pages["core2b.html"])
                    self.assertIn("BOUNDARY-TRIPLE-FACTORS", pages["core2b.html"])

if __name__ == "__main__":
    unittest.main()
