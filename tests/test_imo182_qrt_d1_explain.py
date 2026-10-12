"""Issue 182: original EXPLAIN-D1 five-role renderer and protected causal move."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
import jsonschema
from Shared.tools import render_core, core2_v2

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d1/explain.v1.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d1-explain.manifest.json"
FROZEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"

class ExplainD1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SRC.read_text())
        cls.pages,cls.gaps,cls.digest,_,_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")

    def test_schema_source_and_role_selection(self):
        jsonschema.validate(self.source,json.loads(SCHEMA.read_text()))
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.source["questions"]))
        manifest=json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["selection"]["core2"],[])
        self.assertEqual(manifest["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])

    def test_exact_blueprint_versions_five_roles_no_depth_gaps(self):
        self.assertEqual(self.gaps,[],self.gaps)
        self.assertEqual(set(self.pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,ref in refs.items():
            self.assertIn('data-blueprint-ref="'+ref+'"',self.pages[role+".html"])

    def test_protected_causal_explanation_not_sum_only(self):
        q=self.source["questions"][1]
        self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"],"EXPLAIN")
        self.assertEqual(q["difficulty"]["band"],"D1")
        self.assertEqual(sum(q["difficulty"]["components"].values()),q["difficulty"]["score"])
        self.assertEqual(q["answer"]["crux_move_ref"],"EXP-D1-QA-MECHANISM")
        self.assertIn("two lone counters pair",q["answer"]["summary"].lower())
        self.assertEqual(q["extensions"]["grade9v3:core2_support_plan"]["protected_move_refs"],["EXP-D1-QA-MECHANISM"])
        self.assertEqual([s["availability"] for s in core2_v2.project_support(q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])
        self.assertIn("data-requires-attempt",self.pages["core2a.html"])

    def test_original_visuals_and_distinct_repair_boundary(self):
        for rep in self.source["representations"]:
            for asset in rep["rendered_asset_refs"]:
                s=(ROOT/asset).read_text()
                self.assertIn("<desc>",s)
                self.assertIn("data-g9-stage-id",s)
                self.assertNotIn("7+9=16",s)
                self.assertNotIn("two lone counters pair together",s.lower())
        mic=self.source["microtopics"][0]
        self.assertIn("9 counters",mic["elicitation"]["boundary_test"]["prompt"])
        self.assertIn("4 counters",mic["elicitation"]["boundary_test"]["prompt"])
        self.assertIn("5+7",mic["elicitation"]["predict"]["prompt"])

    def test_inverse_transfer_is_new_causal_decision(self):
        qa=self.source["questions"][1]
        qb=self.source["questions"][2]
        self.assertEqual(qb["transfer"]["dimension"],"novelty")
        self.assertIn(qa["id"],qb["transfer"]["builds_on"])
        self.assertEqual(qb["transfer"]["protected_move_ref"],"EXP-D1-QB-INVERSE")
        self.assertIn("18 counters",qb["stem"])
        self.assertIn("11-counter",qb["answer"]["summary"])
        self.assertIn("EXP-D1-QB-GIVENS",self.pages["core2b.html"])

    def test_independent_math_and_owner_frozen_golden(self):
        spec=importlib.util.spec_from_file_location("verify_explain",ROOT/"TEST/imo-research/qrt-d1/verify_explain.py")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.verify()
        lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        for rec in lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/rec["path"]).read_bytes()).hexdigest(),rec["sha256"])
        self.assertNotEqual(self.pages["core1b.html"],(FROZEN/"snapshots/core1b.html").read_text())

if __name__=="__main__":
    unittest.main()
