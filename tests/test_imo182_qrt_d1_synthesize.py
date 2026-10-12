"""SYNTHESIZE-D1 original source, five registered renderer outputs and frozen Owner fixture."""
from __future__ import annotations
import unittest,json,hashlib,importlib.util
from pathlib import Path
import jsonschema
from Shared.tools import render_core,core2_v2
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d1/synthesize.v1.json"
MAN=ROOT/"TEST/products/imo182-qrt-d1-synthesize.manifest.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"
class D1Synthesize(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads(SRC.read_text())
  cls.pages,cls.gaps,cls.digest,_,_=render_core.build_report(MAN,"PAGES",held_to="REFERENCE")
 def test_schema_and_authored(self):
  jsonschema.validate(self.source,json.loads((ROOT/"Shared/library/package.schema.json").read_text()))
  self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.source["questions"]))
  self.assertEqual(self.source["questions"][1]["extensions"]["grade9v3:cognitive_demand"]["primary"],"SYNTHESIZE")
  self.assertEqual(json.loads(MAN.read_text())["selection"]["core2"],[])
 def test_five_registered_roles_and_no_gaps(self):
  self.assertEqual(self.gaps,[])
  self.assertEqual(set(self.pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
  refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
  for role,v in refs.items():self.assertIn('data-blueprint-ref="'+v+'"',self.pages[role+".html"])
 def test_protected_w_h3_after_attempt(self):
  qa=self.source["questions"][1]
  self.assertEqual(qa["answer"]["crux_move_ref"],"SYN-D1-QA-ORDER")
  self.assertEqual([h["availability"] for h in core2_v2.project_support(qa)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
  self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])
 def test_original_svg_stages_no_early_answer(self):
  self.assertEqual(len(self.source["representations"]),4)
  for r in self.source["representations"]:
   for path in r["rendered_asset_refs"]:
    t=(ROOT/path).read_text()
    self.assertIn("<desc>",t);self.assertIn("data-g9-stage-id",t)
    self.assertNotIn("4×(3+2)=20",t)
    self.assertNotIn("20÷(3+2)=4",t)
  self.assertIn("ONE square",self.source["microtopics"][0]["elicitation"]["boundary_test"]["prompt"])
 def test_inverse_independent_and_math(self):
  a,b=self.source["questions"][1:]
  self.assertIn(a["id"],b["transfer"]["builds_on"])
  self.assertEqual(b["transfer"]["protected_move_ref"],"SYN-D1-QB-REVERSE")
  self.assertIn("4 whole blocks",b["answer"]["summary"])
  spec=importlib.util.spec_from_file_location("verify_synthesize",ROOT/"TEST/imo-research/qrt-d1/verify_synthesize.py")
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.verify()
 def test_owner_snapshot_immutable(self):
  lock=json.loads((GOLDEN/"snapshot-lock.json").read_text())
  for rec in lock["snapshots"]:self.assertEqual(hashlib.sha256((GOLDEN/rec["path"]).read_bytes()).hexdigest(),rec["sha256"])
  self.assertNotEqual(self.pages["core2a.html"],(GOLDEN/"snapshots/core2a.html").read_text())
if __name__=="__main__":unittest.main()
