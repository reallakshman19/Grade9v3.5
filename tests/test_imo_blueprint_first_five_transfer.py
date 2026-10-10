"""Issue #164: real three-Core authored learner journey via the shared renderer.

This is not an SOF question, QRT acceptance or learner release. Tests use the
actual blueprint registry, canonical package/manifest and page renderer.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser

from Shared.tools import product_manifest, product_coverage, render_core
from Shared.tools import question_review_matrix as qrt

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
ADDON = ROOT / "TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"
MANIFEST = ROOT / "TEST/products/imo-g9-blueprint-first-five-transfer.manifest.json"
SVG = ROOT / "TEST/imo-research/pilots/assets/five-consecutive-attempt-safe.svg"
QUESTION = "Q-TEST-IMO-164-FIVE-CONSECUTIVE-120"
GOLDEN = ROOT / "golden/units"


class VisibleLearnerText(HTMLParser):
    """Collect rendered learner text, excluding inert templates and scripts.

    This is a static disclosure check, not an interactive browser or AT audit.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inert = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag in {"template", "script", "style"}:
            self.inert += 1

    def handle_endtag(self, tag):
        if tag in {"template", "script", "style"}:
            self.inert -= 1

    def handle_data(self, data):
        if not self.inert:
            self.text.append(data)


class BlueprintFirstFiveTransferTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(PILOT.read_text(encoding="utf-8"))
        self.addon = json.loads(ADDON.read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.question = next(q for q in self.addon["questions"] if q["id"] == QUESTION)

    def test_real_shared_blueprint_contract_and_explicit_three_role_selection(self):
        registry = json.loads(render_core.BLUEPRINTS.read_text(encoding="utf-8"))
        present = {b["id"] for b in registry["blueprints"]}
        self.assertTrue({
            "BP-CORE1A-CONSTRUCTION", "BP-CORE2A-SUPPORTED-APPLICATION",
            "BP-CORE2B-TRANSFER",
        } <= present)
        self.assertEqual(
            product_manifest.selected_output_roles(self.manifest),
            ["CORE1A", "CORE2A", "CORE2B"],
        )
        self.assertEqual(self.manifest["selection"]["core2"], [])
        self.assertEqual(self.manifest["bank_refs"], [])
        self.assertEqual(
            self.manifest["package_refs"],
            ["TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json"],
        )
        resolved = product_manifest.validate_selection(
            self.manifest, [self.addon], []
        )
        self.assertEqual([q["id"] for q in resolved["core2b"]], [QUESTION])
        product_coverage.validate(
            self.manifest,
            product_manifest.derivable([self.addon], []),
        )

    def test_authored_unpublished_item_cannot_become_sof_core2_or_qrt_accepted(self):
        q = self.question
        self.assertEqual(q["origin"], "AUTHORED")
        self.assertEqual(q["exposure"][0]["core"], "CORE2B")
        self.assertEqual(q["exposure"][0]["role"], "NEW_TRANSFER")
        self.assertFalse(q["origin_ref"].startswith("SOF-"))
        self.assertFalse(self.addon["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertFalse(self.addon["extensions"]["grade9v3:learner_published"])
        self.assertFalse(self.addon["extensions"]["grade9v3:qrt_admitted"])
        self.assertEqual(q["extensions"]["grade9v3:qrt_status"], "PROPOSED_NOT_ACCEPTED")
        self.assertEqual(len(qrt.DEMANDS) * len(qrt.BANDS), 28)
        self.assertEqual(q["hints"], [])
        self.assertEqual(q["scaffolds"], [])
        self.assertEqual(q["hint_ladder"], [])
        self.assertEqual(q["transfer"]["protected_move_ref"], q["answer"]["crux_move_ref"])

    def test_actual_math_claim_is_true_for_exhaustive_residue_classes(self):
        for n in range(120):
            with self.subTest(residue=n):
                first_four = n * (n + 1) * (n + 2) * (n + 3)
                product = first_four * (n + 4)
                self.assertEqual(first_four % 24, 0)
                self.assertEqual(product % 5, 0)
                self.assertEqual(product % 120, 0)
        self.assertEqual(set(range(120)), set(n % 120 for n in range(120)))
        self.assertEqual(self.question["answer"]["verification_status"], "CHECKED_BY_AUTHOR")
        self.assertIn("gcd(24,5)=1", " ".join(self.question["answer"]["reasoning"]))

    def test_transfer_is_not_previously_worked_anchor_relabelled_as_new(self):
        q = self.question
        self.assertNotEqual(
            q["id"], self.base["questions"][1]["id"]
        )
        self.assertIn("factor 5", q["transfer"]["novelty"]["why_new"])
        self.assertEqual(q["transfer"]["dimension"], "reasoning_steps")
        self.assertEqual(q["difficulty"]["band"], "D3")
        self.assertIn("PROPOSED ONLY", q["difficulty"]["basis"])
        self.assertEqual(q["answer"]["crux_move_ref"], "MOVE-IMO-164-CRUX")

    def test_attempt_safe_svg_is_authored_and_withholds_the_proof(self):
        svg = SVG.read_text(encoding="utf-8")
        self.assertIn('data-g9-stage-id="FIVE-FACTORS-ONLY"', svg)
        self.assertIn("n+4", svg)
        self.assertIn("aria-labelledby=", svg)
        self.assertNotIn("120", svg)
        self.assertNotIn("divisible by 5", svg)
        rep = next(r for r in self.addon["representations"] if r["id"] == "REP-TEST-IMO-164-FIVE-NEUTRAL-FACTORS")
        self.assertEqual(rep["scene_instances"][0]["question_ref"], QUESTION)
        self.assertEqual(rep["rendered_asset_refs"], [
            "TEST/imo-research/pilots/assets/five-consecutive-attempt-safe.svg"
        ])

    @unittest.skipUnless(
        importlib.util.find_spec("jsonschema") is not None,
        "full shared renderer requires jsonschema; dedicated #164 CI installs it",
    )
    def test_actual_shared_renderer_outputs_selected_roles_in_draft(self):
        pages, gaps, digest, advisories, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE",
        )
        self.assertEqual(
            set(pages),
            {"index.html", "core1a.html", "core2a.html", "core2b.html"},
        )
        self.assertEqual(len(digest), 16)
        self.assertIn("n(n+1)(n+2)(n+3)(n+4)", pages["core2b.html"])
        self.assertIn("120", pages["core2b.html"])
        self.assertIn("CORE1A", pages["core1a.html"])
        self.assertIn("CORE2A", pages["core2a.html"])
        self.assertNotIn(QUESTION, pages["core1a.html"])
        self.assertNotIn(QUESTION, pages["core2a.html"])
        self.assertNotIn("SOF-IMO-G09-", " ".join(pages.values()))
        self.assertEqual(re.findall(
            r'<article[^>]*data-g9-role="([^"]+)"', pages["core2b.html"]
        ), ["CORE2B"])
        self.assertTrue(all({"core", "record", "duty", "detail"} <= set(g) for g in gaps))

    @unittest.skipUnless(
        importlib.util.find_spec("jsonschema") is not None,
        "full shared renderer requires jsonschema; dedicated #164 CI installs it",
    )
    def test_cli_emits_actual_candidate_html_and_readback_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            rc = render_core.main([
                "build", "--manifest", str(MANIFEST),
                "--out", str(folder), "--draft", "--reference",
            ])
            self.assertEqual(rc, 0)
            self.assertEqual(
                {p.name for p in folder.glob("*.html")},
                {"index.html", "core1a.html", "core2a.html", "core2b.html"},
            )
            receipt = json.loads((folder / "render-receipt.json").read_text())
            self.assertEqual(receipt["output_roles"], [
                "CORE1A", "CORE2A", "CORE2B"
            ])
            self.assertEqual(receipt["renderer"], render_core.RENDERER_VERSION)
            self.assertNotIn("accepted", receipt)
            self.assertTrue((folder / "core2b.html").read_text().strip())

    @unittest.skipUnless(
        importlib.util.find_spec("jsonschema") is not None,
        "full shared renderer requires jsonschema; dedicated #164 CI installs it",
    )
    @unittest.skipUnless(
        importlib.util.find_spec("jsonschema") is not None,
        "full shared renderer requires jsonschema; dedicated #164 CI installs it",
    )
    def test_two_existing_goldens_and_candidate_share_attempt_gate_primitives(self):
        """Golden T01/T09: use the same renderer and inert commitment grammar."""
        examples = (
            (GOLDEN / "G-CORE2-R2/manifest.json", "core2.html"),
            (GOLDEN / "G-MATH-LINEAR-CONSTRAINT/manifest.json", "core2b.html"),
            (MANIFEST, "core2b.html"),
        )
        for manifest, filename in examples:
            with self.subTest(exemplar=manifest.parent.name):
                pages, gaps, _ = render_core.build(manifest, "PAGES")
                self.assertFalse(gaps, gaps)
                html = pages[filename]
                self.assertIn("data-g9-attempt-box", html)
                self.assertIn("data-g9-commit", html)
                self.assertIn("data-requires-attempt", html)
                self.assertIn("<template data-g9-payload=", html)

    @unittest.skipUnless(
        importlib.util.find_spec("jsonschema") is not None,
        "full shared renderer requires jsonschema; dedicated #164 CI installs it",
    )
    def test_transfer_proof_is_in_inert_template_not_pre_attempt_text(self):
        """Golden T01/T03: question visible, mathematical warrant protected."""
        pages, gaps, _, _, _ = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE",
        )
        self.assertFalse(gaps, gaps)
        html = pages["core2b.html"]
        visible = VisibleLearnerText()
        visible.feed(html)
        text = " ".join(visible.text)
        self.assertIn(self.question["stem"][:42], text)
        self.assertIn("gcd(24,5)=1", html)
        self.assertNotIn("gcd(24,5)=1", text)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', html)
        self.assertIn('data-g9-stages="FIVE-FACTORS-ONLY"', html)
        self.assertIn('data-g9-repair-ref="TC-03"', html)
        self.assertIn(
            "core1a.html#CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF",
            html,
        )

    def test_invalid_source_selection_fails_closed_in_draft(self):
        modified = copy.deepcopy(self.manifest)
        modified["selection"]["core2"] = [QUESTION]
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "wrong-authority.manifest.json"
            invalid.write_text(json.dumps(modified), encoding="utf-8")
            with self.assertRaisesRegex(
                product_manifest.ProductSelectionError,
                "PRODUCT_SELECTION_WRONG_AUTHORITY",
            ):
                render_core.build_report(invalid, "PAGES", held_to="REFERENCE")


if __name__ == "__main__":
    unittest.main()
