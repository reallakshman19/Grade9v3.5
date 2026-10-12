"""AGENT-D4 QRT-APPLY-D4: source and role-level TEST, no acceptance."""
import json, re, unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from Shared.tools import core2_v2, render_core

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d4/apply-d4.package.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d4-apply.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
QID="Q-D4-APPLY-MAIN"

class ApplyD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(SRC.read_text())
        cls.m=json.loads(MANIFEST.read_text())
        cls.q=next(q for q in cls.p["questions"] if q["id"]==QID)

    def test_schema_rights_and_h3(self):
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
        self.assertEqual(self.m["selection"]["core2"],[])
        self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["difficulty"]["band"],"D4")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"APPLY")
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:core2_source_custody_granted"])
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],["D4-APP-MOVE-DECIDE"])
        self.assertEqual(plan["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        self.assertEqual([x["availability"] for x in core2_v2.project_support(self.q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        for rep in self.p["representations"]:
            svg=(ROOT/rep["rendered_asset_refs"][0]).read_text()
            self.assertIn("data-g9-stage-id",svg)
            given=svg.split("</desc>",1)[0]
            for private in ("209,389,569","353,533","no solution","x≡29","x≡173"):
                self.assertNotIn(private,given,"Pre-attempt visual leaks result")

    def test_compatible_incompatible_and_corrected_arithmetic(self):
        # Exhaust multiple full periods with positive/negative integers.
        n=0
        for x in range(-3600,3601):
            first=x%12==5 and x%18==11
            self.assertEqual(first,x%36==29)
            original=first and x%20==9
            changed=first and x%20==10
            corrected=first and x%20==13
            self.assertEqual(original,x%180==29)
            self.assertFalse(changed)
            self.assertEqual(corrected,x%180==173)
            self.assertEqual(x%8==1 and x%12==5,x%24==17)
            n+=1
        self.assertEqual(n,7201)
        in_window=lambda phase:[x for x in range(200,601) if x%12==5 and x%18==11 and x%20==phase]
        self.assertEqual(in_window(9),[209,389,569])
        self.assertEqual(in_window(10),[])
        self.assertEqual(in_window(13),[353,533])
        self.assertEqual([209%12,209%18,209%20],[5,11,9])
        self.assertEqual([353%12,353%18,353%20],[5,11,13])
        self.assertEqual([14%6,14%9],[2,5])
        self.assertFalse(any(x%6==2 and x%9==4 for x in range(-100,101)))
        self.assertEqual([24%10,24%15],[4,9])

    def test_registered_renderer_golden_anatomy_and_protected_answer(self):
        pages,gaps,digest,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(gaps,[],str(gaps))
        self.assertEqual(set(pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        roles={"core1":"BP-CORE1-ORIENTATION@1.1.0",
               "core1a":"BP-CORE1A-CONSTRUCTION@1.8.0",
               "core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0",
               "core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
               "core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        slots=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        for role,bp in roles.items():
            with self.subTest(role=role):
                actual=pages[role+".html"]
                frozen=(GOLDEN/(role+".html")).read_text()
                self.assertIn('data-blueprint-ref="'+bp+'"',actual)
                self.assertEqual(re.findall(slots,actual),re.findall(slots,frozen))
                self.assertNotEqual(actual,frozen)
        h=pages["core2a.html"]
        self.assertIn("data-g9-after-attempt-hint",h)
        self.assertIn("data-requires-attempt",h)
        self.assertIn('data-g9-payload="CORE2A-'+QID+'-after-attempt-hint-3"',h)
        self.assertIn("Reasoning route and full solution",h)
        ladder=h.split('data-g9-ladder-ref="CORE2A-',1)[1].split("</div>",1)[0]
        self.assertNotIn("Only AFTER your own attempt",ladder)
        self.assertIn("Only AFTER your own attempt",h)
        self.assertNotEqual(pages["core2a.html"],pages["core2b.html"])

if __name__=="__main__":
    unittest.main()
