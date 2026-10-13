"""Issue #182 AGENT-D4 EXPLAIN-D4; source and rendered TEST-only, no academic acceptance."""
import json, re, unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from Shared.tools import core2_v2, render_core

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d4/explain-d4.package.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d4-explain.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
FROZEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
QID="Q-D4-EXPLAIN-ROTATE1"

def rotate(n,L,k):
    s=str(n).zfill(L)
    return int(s[k:]+s[:k])

class ExplainD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(SRC.read_text())
        cls.m=json.loads(MANIFEST.read_text())
        cls.q=next(q for q in cls.p["questions"] if q["id"]==QID)

    def test_schema_provenance_and_protected_rung(self):
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
        self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.m["selection"]["core2"],[])
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["difficulty"]["band"],"D4")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"EXPLAIN")
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:core2_source_custody_granted"])
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],["D4-EXP-MOVE-CAUSE"])
        self.assertEqual(plan["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        self.assertEqual([x["availability"] for x in core2_v2.project_support(self.q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        for rep in self.p["representations"]:
            text=(ROOT/rep["rendered_asset_refs"][0]).read_text()
            self.assertIn("data-g9-stage-id",text)
            first=text.split("</desc>",1)[0]
            self.assertNotIn("even L",first)
            self.assertNotIn("A divisible",first)

    def test_actual_integer_rotation_mechanism_and_transfer(self):
        self.assertEqual(rotate(1210,4,1),2101)
        self.assertEqual(rotate(121,3,1),211)
        self.assertEqual(rotate(110,3,2),11)
        self.assertEqual(rotate(121,3,2),112)
        cases=0
        for L in range(2,7):
            first=10**(L-1)
            last=min(10**L, first+(10000 if L>4 else 900000))
            for n in range(first,last):
                if n%11: continue
                a=int(str(n)[0])
                k=1
                with self.subTest(L=L,n=n,k=k):
                    self.assertEqual(rotate(n,L,k)%11==0,L%2==0)
                if L>=3:
                    A=int(str(n)[:2])
                    with self.subTest(L=L,n=n,k=2):
                        self.assertEqual(rotate(n,L,2)%11==0,(L%2==0 or A%11==0))
                cases+=1
        self.assertGreater(cases,1000)
        for n in range(100,1000):
            a=n//100;b=(n//10)%10;c=n%10
            self.assertEqual(n%11==0,a-b+c in (0,11))
        self.assertEqual(209%11,0)

    def test_registered_render_zero_gaps_and_immutable_golden_role_anatomy(self):
        pages,gaps,digest,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(gaps,[],str(gaps))
        self.assertEqual(set(pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        expected={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        slot=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        for name,bp in expected.items():
            with self.subTest(role=name):
                actual=pages[name+".html"]
                golden=(FROZEN/(name+".html")).read_text()
                self.assertIn('data-blueprint-ref="'+bp+'"',actual)
                self.assertEqual(re.findall(slot,actual),re.findall(slot,golden))
                self.assertNotEqual(actual,golden)
        html=pages["core2a.html"]
        self.assertIn("data-g9-after-attempt-hint",html)
        self.assertIn("data-requires-attempt",html)
        self.assertIn('data-g9-payload="CORE2A-'+QID+'-after-attempt-hint-3"',html)
        self.assertIn("Reasoning route and full solution",html)
        ladder=html.split('data-g9-ladder-ref="CORE2A-',1)[1].split("</div>",1)[0]
        self.assertNotIn("After your written attempt is committed",ladder)
        self.assertIn("After your written attempt is committed",html)
        self.assertNotEqual(pages["core2a.html"],pages["core2b.html"])

if __name__=="__main__":
    unittest.main()
