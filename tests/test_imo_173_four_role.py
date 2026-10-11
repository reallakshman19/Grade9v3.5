"""Track A #173: separate held A/B, genuine four-role authored journey.

Only candidate-golden structural/semantic checks, not visual, human or academic acceptance.
Never alters source Core2 admission or the original #166 manifests.
"""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from Shared.tools import product_coverage, product_manifest, render_core

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
ADDON = ROOT / "TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
FIVE = ROOT / "TEST/products/imo-g9-track-a-four-role-five-120.manifest.json"
BOUNDARY = ROOT / "TEST/products/imo-g9-track-a-four-role-boundary-12.manifest.json"
ORIGINALS = (
    ROOT / "TEST/products/imo-g9-blueprint-first-five-transfer.manifest.json",
    ROOT / "TEST/products/imo-g9-blueprint-boundary-12-transfer.manifest.json",
)
GOLDENS = (
    ROOT / "golden/units/G-MATH-LINEAR-CONSTRAINT/manifest.json",
    ROOT / "golden/units/G-CORE2-R2/manifest.json",
)
ROLES = ("CORE2A", "CORE1A", "CORE1B", "CORE2B")
PAGES = {"index.html", *(r.lower() + ".html" for r in ROLES)}
TRANSFER = (
    (FIVE, "Q-TEST-IMO-164-FIVE-CONSECUTIVE-120", "gcd(24,5)=1"),
    (BOUNDARY, "Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY", "n mod 4 != 1"),
)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class VisibleText(HTMLParser):
    """Exclude inert templates and script/style bodies from learner-visible text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.excluded = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("template", "script", "style"):
            self.excluded.append(tag)

    def handle_endtag(self, tag):
        if self.excluded and tag == self.excluded[-1]:
            self.excluded.pop()

    def handle_data(self, data):
        if not self.excluded:
            self.parts.append(data)

    def visible(self):
        return " ".join(self.parts)


@unittest.skipUnless(importlib.util.find_spec("jsonschema") is not None,
                     "full renderer needs jsonschema; Track A CI installs it")
class TrackAFourRoleTests(unittest.TestCase):
    def test_additive_role_selection_and_single_record_authority(self):
        addon, pilot = read(ADDON), read(PILOT)
        micro = addon["microtopics"][0]
        former = pilot["microtopics"][0]
        self.assertEqual(micro["id"], former["id"])
        for field in ("inferential_jump", "elicitation", "misconceptions"):
            self.assertEqual(micro[field], former[field], field)
        # Do not load both packages: the second copy is *not* a second owner.
        self.assertEqual(len(addon["microtopics"]), 1)
        for manifest_file, selected, _ in TRANSFER:
            with self.subTest(manifest=manifest_file.name):
                manifest = read(manifest_file)
                self.assertEqual(manifest["subject"], "TEST")
                self.assertEqual(manifest["package_refs"], [
                    "TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
                ])
                self.assertEqual(manifest["output_roles"], list(ROLES))
                self.assertEqual(manifest["selection"]["core2"], [])
                self.assertEqual(manifest["bank_refs"], [])
                self.assertEqual(manifest["coverage"]["sources"], [])
                self.assertEqual(manifest["selection"]["core2b"], [selected])
                resolved = product_manifest.validate_selection(manifest, [addon], [])
                self.assertEqual(len(resolved["microtopics"]), 1)
                product_coverage.validate(manifest, product_manifest.derivable([addon], []))
        for original in ORIGINALS:
            self.assertEqual(read(original)["output_roles"], ["CORE2A", "CORE1A", "CORE2B"])

    def test_existing_authored_figures_are_two_row_and_attempt_safe(self):
        # Historical #164 failure: scrollWidth stayed zero while a figure clipped.
        # A neutral three-factor representation must fit without weakening CSS
        # readability constraints or embedding any inference in a preattempt SVG.
        examples = (
            ("TEST/library/figures/core1b-three-factor-attempt-safe.svg",
             "CORE1B-GIVEN-FACTORS", ("t − 2", "t − 1", ">t<")),
            ("TEST/library/figures/core2a-three-consecutive-attempt-safe.svg",
             "PRACTICE-FACTORS-ONLY", ("m + 1", "m + 2", "m + 3")),
        )
        for filename, stage, symbols in examples:
            with self.subTest(asset=filename):
                source = (ROOT / filename).read_text(encoding="utf-8")
                root = ET.fromstring(source)
                self.assertEqual(root.attrib["viewBox"], "0 0 430 264")
                self.assertEqual(root.attrib.get("width"), "100%")
                self.assertTrue(all(term in source for term in symbols))
                self.assertNotIn("divisible by", source.lower())
                self.assertNotIn("remainder", source.lower())
                self.assertNotIn("coprime", source.lower())
                rectangles = [
                    item for item in root.iter()
                    if item.tag.endswith("rect")
                ]
                self.assertEqual(len(rectangles), 3)
                self.assertEqual(sum("data-g9-final-factor" in item.attrib
                                     for item in rectangles), 1)
                for item in rectangles:
                    x, y, width, height = (float(item.attrib[k])
                                            for k in ("x", "y", "width", "height"))
                    self.assertGreaterEqual(x, 0)
                    self.assertGreaterEqual(y, 0)
                    self.assertLessEqual(x + width, 430)
                    self.assertLessEqual(y + height, 264)
                self.assertEqual(
                    [item.attrib["data-g9-stage-id"] for item in root.iter()
                     if "data-g9-stage-id" in item.attrib],
                    [stage],
                )

    def test_staged_figures_preserve_governed_truth_and_safe_boundary(self):
        addon = read(ADDON)
        micro = addon["microtopics"][0]
        expected = micro["construction_units"][0]["reveal_stage_refs"]
        source = (ROOT / "TEST/library/figures/core1a-consecutive-divisibility-staged.svg").read_text(
            encoding="utf-8")
        root = ET.fromstring(source)
        self.assertEqual(root.attrib["viewBox"], "0 0 390 594")
        actual = [node.attrib["data-g9-stage-id"] for node in root.iter()
                  if "data-g9-stage-id" in node.attrib]
        self.assertEqual(actual, expected)
        for fact in ("one is even: factor 2.", "n mod 3 = 0", "n mod 3 = 1",
                     "n mod 3 = 2", "2 and 3 are coprime",
                     "so 6 divides the product", "for every n."):
            self.assertIn(fact, source)
        boundary = (ROOT / "TEST/imo-research/pilots/assets/triple-boundary-12-attempt-safe.svg"
                    ).read_text(encoding="utf-8")
        figure = ET.fromstring(boundary)
        self.assertEqual(figure.attrib["viewBox"], "0 0 430 302")
        stages = [node.attrib["data-g9-stage-id"] for node in figure.iter()
                  if "data-g9-stage-id" in node.attrib]
        self.assertEqual(stages, ["BOUNDARY-TRIPLE-FACTORS", "BOUNDARY-TARGET-12"])
        self.assertIn("12 divides P(n) for every n?", boundary)
        for answer_leak in ("n mod 4 != 1", "gcd(24,5)", "counterexample n=1"):
            self.assertNotIn(answer_leak, boundary)

    def test_candidate_goldens_are_real_fixtures_not_blessed_authority(self):
        for path in GOLDENS:
            with self.subTest(golden=path.parent.name):
                gold, gaps, digest, _, _ = render_core.build_report(path, "PAGES")
                self.assertEqual(gaps, [])
                self.assertEqual(len(gold), 7)
                self.assertEqual(len(digest), 16)
                self.assertTrue(all("<html" in html for html in gold.values()))
        for path in (
            ROOT / "golden/units/G-MATH-LINEAR-CONSTRAINT/GOLDEN.md",
            ROOT / "golden/units/G-CORE2-R2/GOLDEN.md",
        ):
            self.assertIn("CANDIDATE", path.read_text(encoding="utf-8"))

    def test_a_and_b_have_four_role_pages_in_golden_reference_mode(self):
        for manifest_path, selected, secret in TRANSFER:
            with self.subTest(manifest=manifest_path.name):
                pages, gaps, digest, advisories, waivers = render_core.build_report(
                    manifest_path, "PAGES", held_to="REFERENCE"
                )
                self.assertEqual(set(pages), PAGES)
                self.assertEqual((gaps, advisories, waivers), ([], [], []))
                self.assertEqual(len(digest), 16)
                route = pages["index.html"].split("<main>", 1)[1].split("<ol>", 1)[1]
                offsets = [route.index('href="' + role.lower() + '.html"') for role in ROLES]
                self.assertEqual(offsets, sorted(offsets))
                for role in ROLES:
                    page = pages[role.lower() + ".html"]
                    self.assertEqual(
                        re.findall(r'<article[^>]*data-g9-role="([^"]+)"', page),
                        [role],
                    )
                    self.assertNotIn("SOF-IMO-G09-", page)
                self.assertNotIn(selected, pages["core1b.html"])
                transfer = pages["core2b.html"]
                before = VisibleText()
                before.feed(transfer)
                self.assertIn(secret, transfer)
                self.assertNotIn(secret, before.visible())
                self.assertIn("data-requires-attempt", transfer)
                self.assertIn("<template data-g9-payload=", transfer)
                self.assertIn('data-g9-stage="PRE_ATTEMPT"', transfer)
                self.assertNotIn("SOF-IMO-G09-", " ".join(pages.values()))

    def test_core1b_reconstructs_before_revealing_and_separates_boundary(self):
        addon = read(ADDON)
        micro = addon["microtopics"][0]
        e = micro["elicitation"]
        self.assertEqual(set(e), {"predict", "attempt", "reconstruct", "boundary_test"})
        self.assertEqual(e["attempt"]["closure"], "RUBRIC")
        self.assertEqual(len(e["attempt"]["rubric"]), 4)
        self.assertGreaterEqual(len(e["reconstruct"]["route"]), 4)
        self.assertIn("(t−1)t", e["boundary_test"]["prompt"])
        for path, _, _ in TRANSFER:
            pages, gaps, _, _, _ = render_core.build_report(path, "PAGES", held_to="REFERENCE")
            self.assertFalse(gaps)
            b = pages["core1b.html"]
            self.assertIn("Check your prediction", b)
            self.assertIn("Boundary test", b)
            self.assertIn('data-g9-block="boundary_test"', b)
            self.assertIn("data-g9-attempt-box", b)
            self.assertEqual(len(re.findall(
                r'<(?:div|details)\b[^>]*data-g9-attempt-stage="boundary"', b
            )), 2)
            self.assertIn("<template data-g9-payload=", b)
            before = VisibleText()
            before.feed(b)
            self.assertNotIn("No. Three checks are instances", before.visible())
            self.assertIn("No. Three checks are instances", b)
            self.assertIn("t=2", b)


if __name__ == "__main__":
    unittest.main()
