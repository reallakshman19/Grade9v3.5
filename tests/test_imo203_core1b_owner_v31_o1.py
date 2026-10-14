"""O1 Owner v3.1: preserve the existing Core1B registry/golden reconstruction.

Benchmarks actual registered native renderer output on an authored TEST source;
does not authorize academic acceptance, source rights, changes to frozen golden,
or an optional new blueprint.
"""
import json
import re
import unittest
from pathlib import Path

from Shared.tools import render_core

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"TEST/products/imo203-qrt-d4-retrieve.manifest.json"
PACKAGE=ROOT/"TEST/imo-research/qrt-d4/retrieve-d4.package.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/core1b.html"
REGISTRY=ROOT/"Shared/web/interactive-page-blueprints.v1.json"
ROLE="BP-CORE1B-RECONSTRUCTION@1.1.0"
BLOCKS=(
    "predict", "stage_caption", "attempt_prompt", "prediction_answer",
    "reconstruct", "diagnose", "repair", "success_criteria",
    "model_response", "rejoin_jump", "representation_bridge",
    "boundary_test", "boundary_answer",
)


class Core1BRegisteredOwnerGoldenO1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg=json.loads(PACKAGE.read_text())
        cls.manifest=json.loads(MANIFEST.read_text())
        cls.registry=json.loads(REGISTRY.read_text())
        cls.pages,cls.gaps,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        cls.actual=cls.pages["core1b.html"]
        cls.golden=GOLDEN.read_text()

    def test_native_registered_blueprint_and_frozen_golden_roles(self):
        bp=next(x for x in self.registry["blueprints"] if x["id"]=="BP-CORE1B-RECONSTRUCTION")
        self.assertEqual((bp["version"],bp["status"],bp["core_roles"]),("1.1.0","ACTIVE",["CORE1B"]))
        self.assertEqual(self.gaps,[])
        self.assertEqual(set(self.pages),{"core1.html","core1a.html","core1b.html","core2a.html","core2b.html","index.html"})
        for page in (self.actual,self.golden):
            self.assertIn('data-g9-role="CORE1B"',page) if page is self.golden else self.assertIn('data-core="CORE1B"',page)
            self.assertIn('data-blueprint-ref="'+ROLE+'"',page)
        slots=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        expected=re.findall(slots,self.golden)
        self.assertEqual(expected,["slot-identity","slot-attempt","slot-reconstruction"])
        self.assertEqual(re.findall(slots,self.actual),expected)

    def test_predict_repair_boundary_technique_matches_owner_golden(self):
        pattern=r'data-g9-block="([^"]+)"'
        actual=re.findall(pattern,self.actual)
        golden=re.findall(pattern,self.golden)
        self.assertEqual(golden,list(BLOCKS))
        self.assertEqual(actual,golden)
        self.assertIn("a=5",self.actual)
        self.assertIn("modulo4",self.actual)
        self.assertIn("modulo8",self.actual)
        self.assertIn("modulo16",self.actual)
        self.assertNotEqual(self.actual,self.golden,"different authored TEST questions need semantic, not exact-byte equality")

    def test_main_and_boundary_answer_disclosures_are_attempt_gated(self):
        details=re.findall(r'<details\b[^>]*>',self.actual)
        gates=[x for x in details if 'data-requires-attempt' in x]
        self.assertEqual(len(gates),2)
        expected={"CORE1B-MIC-D4-RETRIEVE-reconstruct","CORE1B-MIC-D4-RETRIEVE-boundary"}
        for gate in gates:
            self.assertIn("data-g9-reveal",gate)
            self.assertIn("data-g9-payload-ref",gate)
            self.assertNotIn(" open",gate)
        for ref in expected:
            self.assertEqual(sum('data-g9-payload-ref="'+ref+'"' in g for g in gates),1)
            self.assertIn('data-g9-payload="'+ref+'"',self.actual)
        self.assertIn('data-g9-attempt-stage="boundary"',self.actual)
        self.assertEqual(self.actual.count('<div data-g9-payload-slot'),2)
        self.assertFalse(self.pkg["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.pkg["extensions"]["grade9v3:learner_published"])

    def test_reconstruction_stops_before_later_main_question_w(self):
        # The small a=5 example gives a necessary modulo8 restriction, not
        # the complete 2^k square-root iff condition or six-residue answer.
        visible=re.sub(r"<template\b[^>]*>.*?</template>"," ",self.actual,flags=re.S)
        for forbidden in ("9,17,33,49","criterion for k>=3: odd a≡1",
                          "every odd class congruent 1 modulo8 lifts"):
            self.assertNotIn(forbidden,visible.casefold())
        self.assertIn("boundary",visible.casefold())
        # Scope the mathematics: boundary output may confirm 5 mod4 is a
        # square, but must not make the false generalization at higher powers.
        self.assertIn("Yes modulo4; no modulo8 or16.",self.actual)


if __name__=="__main__":
    unittest.main()
