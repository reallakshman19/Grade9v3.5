"""Owner v3.1 O1: native Core1 orientation + Core2B transfer golden witness.

The authored TEST source is not a real Core2 question or accepted QRT cell.
"""
import json
import re
import unittest
from html import unescape
from pathlib import Path

from Shared.tools import render_core
from tests.imo203_d4_w_guard import assert_no_protected_iff

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"TEST/products/imo203-qrt-d4-retrieve.manifest.json"
PACKAGE=ROOT/"TEST/imo-research/qrt-d4/retrieve-d4.package.json"
REGISTRY=ROOT/"Shared/web/interactive-page-blueprints.v1.json"
GOLDENS=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
EXPECTED={
 "core1": {
  "blueprint":"BP-CORE1-ORIENTATION@1.1.0",
  "slots":["slot-identity","slot-orientation"],
  "blocks":["scope","hard_transition","representation_bridge",
            "governing_relation","compact_anchor","exit_prompt"],
 },
 "core2b": {
  "blueprint":"BP-CORE2B-TRANSFER@1.1.0",
  "slots":["slot-identity","slot-attempt","slot-post_attempt"],
  "blocks":["provenance","stem","lineage","conditions","stage_caption",
            "safe_support","lineage_check","invariant_changed",
            "changed_demand","protected_move","answer","rubric",
            "independent_check","repair"],
 },
}
SLOT_RE=r'<section class="blueprint-slot (slot-[a-z_]+)"'
BLOCK_RE=r'data-g9-block="([^"]+)"'


class Core1AndCore2BRegisteredOwnerGoldenO1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads(MANIFEST.read_text())
        cls.package=json.loads(PACKAGE.read_text())
        cls.registry=json.loads(REGISTRY.read_text())
        cls.pages,cls.gaps,*_=render_core.build_report(
            MANIFEST,"PAGES",held_to="REFERENCE")

    def test_registered_blueprints_render_against_frozen_role_goldens(self):
        self.assertEqual(self.registry["registry_version"],"1.17.0")
        self.assertEqual(self.gaps,[])
        self.assertEqual(set(self.pages),{
            "core1.html","core1a.html","core1b.html",
            "core2a.html","core2b.html","index.html"})
        for role,expected in EXPECTED.items():
            with self.subTest(role=role):
                actual=self.pages[role+".html"]
                golden=(GOLDENS/(role+".html")).read_text()
                blueprint=expected["blueprint"]
                bp_id,version=blueprint.split("@")
                bp=next(x for x in self.registry["blueprints"] if x["id"]==bp_id)
                self.assertEqual(bp["status"],"ACTIVE")
                self.assertEqual(bp["version"],version)
                self.assertEqual(bp["core_roles"],[role.upper()])
                self.assertEqual(
                    ["slot-"+x["id"] for x in bp["slots"]],
                    expected["slots"])
                for html in (actual,golden):
                    self.assertIn('data-blueprint-ref="'+blueprint+'"',html)
                    self.assertEqual(re.findall(SLOT_RE,html),expected["slots"])
                    self.assertEqual(re.findall(BLOCK_RE,html),expected["blocks"])
                # Golden defines role/technique, not byte-identical prose
                # across unrelated authored mathematics and question stems.
                self.assertNotEqual(actual,golden)

    def test_core1_is_safe_prerequisite_orientation_not_full_question(self):
        html=self.pages["core1.html"]
        visible=re.sub(r"\s+"," ",unescape(re.sub(
            r"<[^>]+>"," ",re.sub(r"<template\b[^>]*>.*?</template>"," ",html,
                               flags=re.S))))
        self.assertIn("necessary modular-square property",visible)
        self.assertIn("sufficient classification rule",visible)
        self.assertIn("Independently classify 5 and9",visible)
        self.assertIn('data-g9-stage-id="D4-RET-STAGE-PLACE"',html)
        self.assertIn('data-g9-stage-id="D4-RET-STAGE-TWO"',html)
        self.assertIn('data-g9-stage-id="D4-RET-STAGE-SPLIT"',html)
        self.assertNotIn("9,17,33,49",visible)
        self.assertNotIn("the exact rule for k>=3",visible.casefold())
        assert_no_protected_iff(visible,"CORE1-OWNER-V31-O1")
        self.assertNotIn('data-g9-payload-ref="CORE2A-',html)

    def test_core2b_preserves_new_modulus_and_sealed_answer(self):
        html=self.pages["core2b.html"]
        self.assertIn('data-g9-role="CORE2B"',html)
        self.assertIn("The modulus is now 4 instead of 128",html)
        self.assertIn("a=5,9,13",html)
        self.assertIn("contrast the result for a=5 modulo8",html)
        self.assertIn('data-g9-block="lineage_check"',html)
        self.assertIn('data-g9-block="changed_demand"',html)
        self.assertIn('data-g9-block="independent_check"',html)
        gated=[d for d in re.findall(r'<details\b[^>]*>',html)
               if 'data-g9-payload-ref="CORE2B-Q-D4-RETRIEVE-TRANSFER-review"' in d]
        self.assertEqual(len(gated),1)
        self.assertIn("data-requires-attempt",gated[0])
        self.assertIn("data-g9-reveal",gated[0])
        self.assertNotIn(" open",gated[0])
        self.assertIn('data-g9-payload="CORE2B-Q-D4-RETRIEVE-TRANSFER-review"',html)
        self.assertIn("data-g9-attempt-box",html)
        self.assertIn("data-g9-commit",html)
        self.assertFalse(self.package["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.package["extensions"]["grade9v3:learner_published"])
        self.assertEqual(self.manifest["selection"]["core2"],[])

    def test_constructive_transfer_modulus4_and_changed_boundary_math(self):
        four={x*x%4 for x in range(1,4,2)}
        eight={x*x%8 for x in range(1,8,2)}
        self.assertEqual(four,{1})
        self.assertEqual(eight,{1})
        self.assertEqual([a for a in (5,9,13) if (a%4) in four],
                         [5,9,13])
        self.assertNotIn(5%8,eight)


if __name__=="__main__":
    unittest.main()
