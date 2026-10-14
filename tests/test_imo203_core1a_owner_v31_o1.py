"""O1 Core1A from the registered renderer against the Owner frozen golden.

A question-specific TEST page, not an accepted QRT cell, release, or golden.
"""
import json
import re
import unittest
from pathlib import Path

from Shared.tools import render_core

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "TEST/products/imo203-qrt-d4-retrieve.manifest.json"
PKG = ROOT / "TEST/imo-research/qrt-d4/retrieve-d4.package.json"
GOLDEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core1a.html"
BLUEPRINT = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
ROLE_REF = "BP-CORE1A-CONSTRUCTION@1.8.0"
COMPONENTS = (
    "CONCEPT_HEADER", "UNIT_HEADER", "MODEL_CONTRACT", "CONSTRUCTION_STEPS",
    "STAGED_VISUAL", "KEY_STEP", "EQUATIONS", "WORKED_EXAMPLE",
    "TRAP_REPAIR", "QUICK_CHECK", "EXIT_RECALL"
)


class Core1AOwnerGoldenO1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.package = json.loads(PKG.read_text())
        cls.registry = json.loads(BLUEPRINT.read_text())
        cls.pages, cls.gaps, *_ = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        cls.actual = cls.pages["core1a.html"]
        cls.golden = GOLDEN.read_text()

    def test_registered_blueprint_and_actual_golden_role_structure(self):
        self.assertEqual(self.gaps, [])
        bp = next(x for x in self.registry["blueprints"]
                  if x["id"] == "BP-CORE1A-CONSTRUCTION")
        self.assertEqual(bp["version"], "1.8.0")
        self.assertEqual(bp["status"], "ACTIVE")
        self.assertEqual(bp["core_roles"], ["CORE1A"])
        self.assertEqual(self.manifest["output_roles"],
                         ["CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"])
        self.assertEqual(self.manifest["selection"]["core2"], [])
        self.assertIn('data-g9-role="CORE1A"', self.actual)
        self.assertIn('data-blueprint-ref="' + ROLE_REF + '"', self.actual)
        self.assertIn('data-blueprint-ref="' + ROLE_REF + '"', self.golden)
        pattern = r'<section class="blueprint-slot (slot-[a-z_]+)"'
        expected = re.findall(pattern, self.golden)
        self.assertEqual(expected,
                         ["slot-identity", "slot-construction",
                          "slot-repair_closure", "slot-repair_closure"])
        self.assertEqual(re.findall(pattern, self.actual), expected)

    def test_core1a_teaching_and_independent_exit_match_golden_affordances(self):
        # O1 compares the actual registered learner page, not a standalone
        # imitation or a cross-question exact-byte HTML equality assertion.
        for name in COMPONENTS:
            with self.subTest(component=name):
                marker = 'data-g9-component="' + name + '"'
                self.assertIn(marker, self.golden)
                self.assertIn(marker, self.actual)
        sequence = re.findall(r'data-g9-component="([A-Z_]+)"', self.actual)
        golden_sequence = re.findall(r'data-g9-component="([A-Z_]+)"', self.golden)
        # Compare the observable Core1A technique order, not unrelated roles
        # in the integrated frozen Owner fixture.
        self.assertEqual([name for name in sequence if name in COMPONENTS],
                         [name for name in golden_sequence if name in COMPONENTS])
        self.assertIn("Independently classify 5 and9", self.actual)
        self.assertIn("Every odd square is1 modulo8", self.actual)
        self.assertIn('data-g9-figure', self.actual)
        self.assertIn('data-g9-stages-total="3"', self.actual)
        self.assertIn('data-g9-reveal', self.actual)
        self.assertIn('data-g9-attempt-box', self.actual)
        self.assertIn('data-g9-commit', self.actual)
        exit_disclosures = [
            tag for tag in re.findall(r'<details\b[^>]*>', self.actual)
            if 'data-g9-payload-ref="CORE1A-MIC-D4-RETRIEVE-exit"' in tag
        ]
        self.assertEqual(len(exit_disclosures), 1)
        self.assertIn("data-requires-attempt", exit_disclosures[0])
        self.assertIn('data-g9-payload-slot', self.actual)
        self.assertFalse(self.package["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.package["extensions"]["grade9v3:learner_published"])

    def test_core1a_initial_visual_and_bridge_protect_later_core2a_decision(self):
        # A stage-1 image is a necessary-condition demonstration; it must not
        # disclose the full iff for powers >=3 before the main Core2A attempt.
        first_desc = re.search(r'<desc>(.*?)</desc>', self.actual, re.S)
        self.assertIsNotNone(first_desc, "No accessible SVG description")
        self.assertIn("No final answer or category", first_desc.group(1))
        for forbidden in ("120384", "9,17,33,49", "odd root exists iff",
                          "every odd class congruent 1 modulo8 lifts"):
            with self.subTest(cue=forbidden):
                self.assertNotIn(forbidden, first_desc.group(1).casefold())
        self.assertIn("necessary restriction", self.actual)
        self.assertIn("Do not claim a full classification rule", self.actual)


if __name__ == "__main__":
    unittest.main()
