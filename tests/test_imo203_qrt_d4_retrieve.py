"""Native RETRIEVE-D4 TEST evidence. No QRT academic acceptance or public source rights."""
import json
import re
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from Shared.tools import render_core, core2_v2

ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/"TEST/imo-research/qrt-d4/retrieve-d4.package.json"
MANIFEST=ROOT/"TEST/products/imo203-qrt-d4-retrieve.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"


class RetrieveD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(PKG.read_text())
        cls.m=json.loads(MANIFEST.read_text())
        cls.q=next(q for q in cls.p["questions"] if q["id"]=="Q-D4-RETRIEVE-MAIN")

    def test_schema_source_rights_and_scaffold_release(self):
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
        self.assertEqual(self.p["extensions"]["grade9v3:qrt_cell"],"QRT-RETRIEVE-D4")
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:learner_published"])
        self.assertFalse(self.p["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.m["selection"]["core2"],[])
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"RETRIEVE")
        self.assertEqual(self.q["difficulty"]["band"],"D4")
        self.assertEqual(self.q["answer"]["crux_move_ref"],"D4-RET-MOVE-CRITERION")
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],["D4-RET-MOVE-CRITERION"])
        self.assertEqual(plan["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        self.assertEqual([h["availability"] for h in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        for hint in self.q["scaffolds"][:2]:
            self.assertNotIn("a≡1 mod8",hint["text"].lower())
            self.assertNotIn("9,17,33,49 yes",hint["text"].lower())
        for rep in self.p["representations"]:
            svg=(ROOT/rep["rendered_asset_refs"][0]).read_text()
            self.assertIn("data-g9-stage-id",svg)
            self.assertNotIn("Yes:9,17,33,49",svg)

    def test_independent_odd_square_classes_and_exception(self):
        for k in range(2,11):
            m=2**k
            roots={x*x%m for x in range(1,m,2)}
            expected={a for a in range(1,m,2) if (a%4==1 if k==2 else a%8==1)}
            self.assertEqual(roots,expected,k)
        roots128={x*x%128 for x in range(1,128,2)}
        self.assertEqual([a for a in (9,13,17,21,33,49) if a in roots128],[9,17,33,49])
        self.assertEqual([a for a in (9,13,17,21,33,49) if a not in roots128],[13,21])
        self.assertIn(5%4,{x*x%4 for x in range(1,4,2)})
        self.assertNotIn(5,{x*x%8 for x in range(1,8,2)})

    def test_actual_registered_renderer_semantic_slots(self):
        pages,gaps,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(gaps,[])
        self.assertEqual(set(pages),{"core1.html","core1a.html","core1b.html","core2a.html","core2b.html","index.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,ref in refs.items():
            with self.subTest(role=role):
                html=pages[role+".html"]
                self.assertIn('data-blueprint-ref="'+ref+'"',html)
                self.assertIn("blueprint-slot",html)
                if GOLDEN.exists():
                    golden=(GOLDEN/(role+".html")).read_text()
                    slot=r'<section class="blueprint-slot (slot-[a-z_]+)"'
                    self.assertEqual(re.findall(slot,html),re.findall(slot,golden))
        # Cross-role provenance audit: Core1B must not repeat the Core2A classification.
        for role in ("core1a.html","core1b.html"):
            html=pages[role]
            self.assertNotIn("9,17,33,49",html,role)
            self.assertNotIn("At modulus128, a=9",html,role)
        self.assertIn("D4-RET-MOVE-CRITERION",pages["core2a.html"])
        self.assertIn("data-g9-after-attempt-hint",pages["core2a.html"])
        self.assertIn("data-requires-attempt",pages["core2a.html"])


if __name__=="__main__":
    unittest.main()
