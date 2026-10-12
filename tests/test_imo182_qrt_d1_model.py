"""Five-role original MODEL-D1 equal-groups renderer and frozen golden guard."""
from __future__ import annotations
import hashlib, importlib.util, json, unittest
from pathlib import Path
import jsonschema
from Shared.tools import render_core, core2_v2
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d1/model.v1.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d1-model.manifest.json"
FROZEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"
class ModelD1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SRC.read_text())
        cls.pages,cls.gaps,cls.digest,_,_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
    def test_source_schema_original_and_selection(self):
        jsonschema.validate(self.source,json.loads(SCHEMA.read_text()))
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.source["questions"]))
        self.assertEqual(self.source["questions"][1]["extensions"]["grade9v3:cognitive_demand"]["primary"],"MODEL")
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(m["selection"]["core2"],[])
        self.assertEqual(m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
    def test_five_blueprints_and_zero_reference_gaps(self):
        self.assertEqual(self.gaps,[],self.gaps)
        self.assertEqual(set(self.pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        expected={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,ref in expected.items():self.assertIn('data-blueprint-ref="'+ref+'"',self.pages[role+".html"])
    def test_model_choice_is_protected_h3_after_attempt(self):
        q=self.source["questions"][1]
        self.assertEqual(q["difficulty"]["band"],"D1")
        self.assertEqual(q["difficulty"]["score"],sum(q["difficulty"]["components"].values()))
        self.assertEqual(q["answer"]["crux_move_ref"],"MOD-D1-QA-CHOOSE")
        self.assertIn("6×4=24",q["answer"]["summary"])
        plan=q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[q["answer"]["crux_move_ref"]])
        self.assertEqual([x["availability"] for x in core2_v2.project_support(q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])
        self.assertIn("data-requires-attempt",self.pages["core2a.html"])
    def test_safe_svg_and_changed_boundary(self):
        for r in self.source["representations"]:
            for path in r["rendered_asset_refs"]:
                s=(ROOT/path).read_text()
                self.assertIn("<desc>",s)
                self.assertIn("data-g9-stage-id",s)
                self.assertNotIn("6×4=24",s)
                self.assertNotIn("24÷4=6",s)
        mic=self.source["microtopics"][0]
        self.assertIn("two separate bags",mic["elicitation"]["boundary_test"]["prompt"])
        self.assertIn("4 shelves",mic["elicitation"]["predict"]["prompt"])
    def test_core2b_inverse_has_new_unknown(self):
        qa,qb=self.source["questions"][1:]
        self.assertEqual(qb["transfer"]["dimension"],"novelty")
        self.assertIn(qa["id"],qb["transfer"]["builds_on"])
        self.assertEqual(qb["transfer"]["protected_move_ref"],"MOD-D1-QB-INVERSE")
        self.assertIn("24 seedlings",qb["stem"])
        self.assertIn("6 trays",qb["answer"]["summary"])
    def test_mathematical_oracle_and_frozen_original_golden(self):
        sp=importlib.util.spec_from_file_location("verify_model",ROOT/"TEST/imo-research/qrt-d1/verify_model.py")
        mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);mod.verify()
        lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        for rec in lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/rec["path"]).read_bytes()).hexdigest(),rec["sha256"])
        self.assertNotEqual(self.pages["core2a.html"],(FROZEN/"snapshots/core2a.html").read_text())
if __name__=="__main__":unittest.main()
