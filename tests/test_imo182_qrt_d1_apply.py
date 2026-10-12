"""Issue 182 APPLY-D1 authored rectangle-area role, golden and protected W checks."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
import jsonschema
from Shared.tools import render_core, core2_v2
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d1/apply.v1.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d1-apply.manifest.json"
FROZEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"
class ApplyD1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package=json.loads(SRC.read_text())
        cls.pages,cls.gaps,cls.digest,_,_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
    def test_authored_schema_and_manifest(self):
        jsonschema.validate(self.package,json.loads(SCHEMA.read_text()))
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.package["questions"]))
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(m["selection"]["core2"],[])
        self.assertEqual(m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
    def test_actual_five_blueprints_and_no_depth_gaps(self):
        self.assertEqual(self.gaps,[],self.gaps)
        self.assertEqual(set(self.pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        ref={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,bp in ref.items():self.assertIn('data-blueprint-ref="'+bp+'"',self.pages[role+".html"])
    def test_qa_protected_area_application_h3(self):
        q=self.package["questions"][1]
        self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"],"APPLY")
        self.assertEqual(q["difficulty"]["band"],"D1")
        self.assertEqual(q["difficulty"]["score"],sum(q["difficulty"]["components"].values()))
        self.assertEqual(q["answer"]["crux_move_ref"],"APP-D1-QA-SUBSTITUTE")
        self.assertIn("28 cm",q["answer"]["summary"])
        self.assertEqual(q["extensions"]["grade9v3:core2_support_plan"]["protected_move_refs"],[q["answer"]["crux_move_ref"]])
        self.assertEqual([x["availability"] for x in core2_v2.project_support(q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])
        self.assertIn("data-requires-attempt",self.pages["core2a.html"])
    def test_unmarked_artwork_and_boundary(self):
        for r in self.package["representations"]:
            for asset in r["rendered_asset_refs"]:
                content=(ROOT/asset).read_text()
                self.assertIn("<desc>",content)
                self.assertIn("data-g9-stage-id=",content)
                self.assertNotIn("7 × 4 = 28",content)
                self.assertNotIn("24 ÷ 4 = 6",content)
        m=self.package["microtopics"][0]
        self.assertIn("4 cm by 4 cm",m["elicitation"]["boundary_test"]["prompt"])
        self.assertIn("5+3",m["elicitation"]["predict"]["prompt"])
    def test_inverse_core2b_is_changed_application(self):
        qa,qb=self.package["questions"][1:]
        self.assertEqual(qb["transfer"]["dimension"],"novelty")
        self.assertIn(qa["id"],qb["transfer"]["builds_on"])
        self.assertEqual(qb["transfer"]["protected_move_ref"],"APP-D1-QB-INVERSE")
        self.assertIn("24 cm",qb["stem"])
        self.assertIn("6 cm",qb["answer"]["summary"])
    def test_original_oracle_and_frozen_lock(self):
        spec=importlib.util.spec_from_file_location("verify_apply",ROOT/"TEST/imo-research/qrt-d1/verify_apply.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.verify()
        lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        for r in lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/r["path"]).read_bytes()).hexdigest(),r["sha256"])
        self.assertNotEqual(self.pages["core2a.html"],(FROZEN/"snapshots/core2a.html").read_text())
if __name__=="__main__":unittest.main()
