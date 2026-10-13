"""Original QRT RETRIEVE-D1 five-role source-bound renderer regression."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
import jsonschema
from Shared.tools import render_core, core2_v2
import importlib.util
V=ROOT if False else None

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"TEST/imo-research/qrt-d1/retrieve.v1.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d1-retrieve.manifest.json"
FROZEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"

class D1Retrieve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SOURCE.read_text())
        cls.pages,cls.gaps,cls.digest,_,_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
    def test_schema_original_rights_and_single_cell(self):
        jsonschema.validate(self.source,json.loads(SCHEMA.read_text()))
        manifest=json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["selection"]["core2"],[])
        self.assertEqual(manifest["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.source["questions"]))
        self.assertEqual(self.source["questions"][1]["extensions"]["grade9v3:cognitive_demand"]["primary"],"RETRIEVE")
        self.assertEqual(self.source["questions"][1]["difficulty"]["band"],"D1")
    def test_five_blueprints_reference_depth(self):
        self.assertEqual(self.gaps,[],self.gaps)
        self.assertEqual(set(self.pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,ref in refs.items(): self.assertIn('data-blueprint-ref="'+ref+'"',self.pages[role+".html"])
    def test_25_w_and_h3_gate(self):
        q=self.source["questions"][1]
        plan=q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[q["answer"]["crux_move_ref"]])
        self.assertEqual([x["availability"] for x in core2_v2.project_support(q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])
        self.assertIn("data-requires-attempt",self.pages["core2a.html"])
        self.assertEqual(q["answer"]["summary"],"25 is COMPOSITE.")
    def test_retrieve_h2_does_not_recite_protected_classification_rule(self):
        q=self.source["questions"][1]
        self.assertEqual(q["answer"]["crux_move_ref"],"RET-D1-QA-DECIDE")
        safe_hints=[s["text"] for s in q["scaffolds"][:2]]
        self.assertEqual(len(safe_hints),2)
        all_pre_attempt=" ".join(safe_hints).lower()
        for leaked in ("exactly two for prime", "more than two for composite",
                       "one for neither", "three means composite", "25 is composite",
                       "composite because it has three"):
            self.assertNotIn(leaked,all_pre_attempt)
        self.assertIn("Recall the rule",q["scaffolds"][1]["text"])
        self.assertIn(q["scaffolds"][1]["text"],self.pages["core2a.html"])
        self.assertEqual([s["availability"] for s in core2_v2.project_support(q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        # The AFTER_ATTEMPT hint may discuss checking thresholds, but not on initial display.
        self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])

    def test_unmarked_figure_and_new_transfer(self):
        for record in self.source["representations"]:
            for asset in record["rendered_asset_refs"]:
                s=(ROOT/asset).read_text()
                self.assertIn("<desc>",s)
                self.assertIn("data-g9-stage-id",s)
                self.assertNotIn("25 is COMPOSITE",s)
                self.assertNotIn("Card B is correct",s)
        q=self.source["questions"][2]
        self.assertIn(self.source["questions"][1]["id"],q["transfer"]["builds_on"])
        self.assertEqual(q["transfer"]["dimension"],"novelty")
        self.assertIn("category PRIME",q["stem"])
        self.assertIn("Card B",q["answer"]["summary"])
        self.assertIn("RETR-ERROR-CARD",self.pages["core1b.html"])
    def test_independent_math(self):
        path=ROOT/'TEST/imo-research/qrt-d1/verify_retrieve.py'
        spec=importlib.util.spec_from_file_location('verify_retrieve',path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.verify()
    def test_frozen_golden_immutable(self):
        lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        import hashlib
        for row in lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/row["path"]).read_bytes()).hexdigest(),row["sha256"])
        self.assertNotEqual(self.pages["core2a.html"],(FROZEN/"snapshots/core2a.html").read_text())

if __name__=="__main__":unittest.main()
