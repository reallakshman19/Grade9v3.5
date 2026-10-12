"""Independent authored REPRESENT-D4 mathematical oracle, source schema, blueprint and five frozen role slots."""
import json
import re
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from Shared.tools import render_core, core2_v2

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d4/represent-d4.package.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d4-represent.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
MAIN_HOLES={(1,4),(2,3),(3,2),(3,3),(4,6),(5,1)}
TRANSFER_HOLES=(MAIN_HOLES-{(2,3)})|{(6,5)}
WITNESS={(1,1),(2,2),(1,3)}
NEIGHBORS={(2,1),(1,2)}
PAIRS=[
((1,2),(2,2)),((1,6),(1,5)),((2,1),(1,1)),((2,3),(1,3)),((2,5),(3,5)),
((3,4),(2,4)),((3,6),(2,6)),((4,1),(3,1)),((4,3),(5,3)),((4,5),(5,5)),
((5,2),(4,2)),((5,4),(4,4)),((5,6),(6,6)),((6,1),(6,2)),((6,3),(6,4))
]

def cells(holes):
    return {(r,c) for r in range(1,7) for c in range(1,7)}-holes

def possible_neighbors(cell, other):
    r,c=cell
    return {(r+dr,c+dc) for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)) if (r+dr,c+dc) in other}

def max_matching(holes):
    surviving=cells(holes)
    black=sorted(x for x in surviving if sum(x)%2==0)
    white={x for x in surviving if sum(x)%2==1}
    matching={}
    def augment(x,seen):
        for y in sorted(possible_neighbors(x,white)):
            if y in seen: continue
            seen.add(y)
            if y not in matching or augment(matching[y],seen):
                matching[y]=x
                return True
        return False
    return sum(augment(x,set()) for x in black)

class RepresentD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(SRC.read_text())
        cls.m=json.loads(MANIFEST.read_text())
        cls.q=next(x for x in cls.p["questions"] if x["id"]=="Q-D4-REPRESENT-MAIN")

    def test_schema_custody_and_after_attempt_policy(self):
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
        self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.m["selection"]["core2"],[])
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["difficulty"]["band"],"D4")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"REPRESENT")
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:core2_source_custody_granted"])
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],["D4-REP-MOVE-LOCAL"])
        self.assertEqual(plan["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        self.assertEqual([x["availability"] for x in core2_v2.project_support(self.q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        for rep in self.p["representations"]:
            svg=(ROOT/rep["rendered_asset_refs"][0]).read_text()
            self.assertIn("data-g9-stage-id",svg)
            preamble=svg.split("</desc>",1)[0]
            for forbidden in ("r1c1,r2c2,r1c3","r2c1,r1c2","matching size","no tiling","15 domino"):
                self.assertNotIn(forbidden,preamble)

    def test_independent_graph_oracle_and_transfer(self):
        old=cells(MAIN_HOLES);new=cells(TRANSFER_HOLES)
        self.assertEqual(len(old),30);self.assertEqual(len(new),30)
        for survivors in (old,new):
            self.assertEqual(sum(sum(x)%2==0 for x in survivors),15)
            self.assertEqual(sum(sum(x)%2==1 for x in survivors),15)
        blacks={x for x in old if sum(x)%2==0}
        whites=old-blacks
        self.assertTrue(WITNESS<=blacks)
        self.assertEqual(set().union(*(possible_neighbors(x,whites) for x in WITNESS)),NEIGHBORS)
        self.assertEqual(max_matching(MAIN_HOLES),14)
        self.assertEqual(max_matching(TRANSFER_HOLES),15)
        used=set()
        for a,b in PAIRS:
            self.assertIn(a,new);self.assertIn(b,new)
            self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)
            self.assertNotIn(a,used);self.assertNotIn(b,used)
            used.update((a,b))
        self.assertEqual(used,new)

    def test_five_registered_roles_golden_slots_zero_gaps(self):
        pages,gaps,digest,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(gaps,[],str(gaps))
        self.assertEqual(set(pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        pattern=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        for role,ref in refs.items():
            with self.subTest(role=role):
                actual=pages[role+".html"]
                golden=(GOLDEN/(role+".html")).read_text()
                self.assertIn('data-blueprint-ref="'+ref+'"',actual)
                self.assertEqual(re.findall(pattern,actual),re.findall(pattern,golden))
                self.assertNotEqual(actual,golden)
        html=pages["core2a.html"]
        self.assertIn("data-g9-after-attempt-hint",html)
        self.assertIn("data-requires-attempt",html)
        self.assertIn('data-g9-payload="CORE2A-Q-D4-REPRESENT-MAIN-after-attempt-hint-3"',html)
        self.assertIn("Reasoning route and full solution",html)
        self.assertNotEqual(html,pages["core2b.html"])

if __name__=="__main__":
    unittest.main()
