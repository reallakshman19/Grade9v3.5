"""Original MODEL-D4 source/geometry and five registered role contracts. TEST only."""
import json,re,unittest
from pathlib import Path
from collections import deque
from jsonschema import Draft202012Validator
from Shared.tools import core2_v2,render_core

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d4/model-d4.package.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d4-model.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
QID="Q-D4-MODEL-MAIN"

def geometry(rows):
    """Independent exterior flood fill: no source package counts reused."""
    height=len(rows);width=len(rows[0])
    grid=[["."]*(width+2)]+[["."]+list(r)+["."] for r in rows]+[["."]*(width+2)]
    seen={(0,0)};q=deque([(0,0)])
    offsets=[(1,0),(-1,0),(0,1),(0,-1)]
    while q:
        r,c=q.popleft()
        for dr,dc in offsets:
            rr,cc=r+dr,c+dc
            if not 0<=rr<height+2 or not 0<=cc<width+2:continue
            if grid[rr][cc]=="#" or (rr,cc) in seen:continue
            seen.add((rr,cc));q.append((rr,cc))
    n=e=c=accessible=0
    for r in range(1,height+1):
        for col in range(1,width+1):
            if grid[r][col]!="#":continue
            n+=1
            for dr,dc in offsets:
                rr,cc=r+dr,col+dc
                if grid[rr][cc]=="#":
                    if dr==1 or dc==1:e+=1
                elif (rr,cc) in seen:accessible+=1
                else:c+=1
    assert 4*n-2*e-c==accessible
    return (n,e,c,accessible)

class ModelD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(SRC.read_text())
        cls.m=json.loads(MANIFEST.read_text())
        cls.q=next(x for x in cls.p["questions"] if x["id"]==QID)

    def test_schema_authorship_h3_and_safe_diagrams(self):
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
        self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.m["selection"]["core2"],[])
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["difficulty"]["band"],"D4")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"MODEL")
        self.assertFalse(self.p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.p["extensions"]["grade9v3:core2_source_custody_granted"])
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],["D4-MOD-MOVE-CAVITY"])
        self.assertEqual(plan["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        self.assertEqual([s["availability"] for s in core2_v2.project_support(self.q)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        for rep in self.p["representations"]:
            svg=(ROOT/rep["rendered_asset_refs"][0]).read_text()
            self.assertIn("data-g9-stage-id",svg)
            preamble=svg.split("</desc>",1)[0]
            for forbidden in ("A=16","A=24","chair count 16","chair count 24","n=12,e=12,c=8"):
                self.assertNotIn(forbidden,preamble)

    def test_independent_exterior_floodfill_on_closed_and_open_grids(self):
        self.assertEqual(geometry(["##","#."]),(3,2,0,8))
        self.assertEqual(geometry(["###","#.#","###"]),(8,8,4,12))
        self.assertEqual(geometry(["#.#","#.#","###"]),(7,6,0,16))
        self.assertEqual(geometry(["####","#..#","#..#","####"]),(12,12,8,16))
        self.assertEqual(geometry(["#.##","#..#","#..#","####"]),(11,10,0,24))
        # All 2^9 occupancy patterns independently exercise contact and cavity classification.
        for mask in range(512):
            rows=["".join("#" if mask&(1<<(r*3+c)) else "." for c in range(3)) for r in range(3)]
            n,e,c,a=geometry(rows)
            self.assertEqual(a,4*n-2*e-c)

    def test_five_registered_blueprints_zero_gaps_and_frozen_role_slots(self):
        pages,gaps,digest,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(gaps,[],str(gaps))
        self.assertEqual(set(pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        slot=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        for role,ref in refs.items():
            with self.subTest(role=role):
                actual=pages[role+".html"]
                golden=(GOLDEN/(role+".html")).read_text()
                self.assertIn('data-blueprint-ref="'+ref+'"',actual)
                self.assertEqual(re.findall(slot,actual),re.findall(slot,golden))
                self.assertNotEqual(actual,golden)
        html=pages["core2a.html"]
        self.assertIn("data-g9-after-attempt-hint",html)
        self.assertIn("data-requires-attempt",html)
        self.assertIn('data-g9-payload="CORE2A-'+QID+'-after-attempt-hint-3"',html)
        self.assertIn("Reasoning route and full solution",html)
        self.assertNotEqual(pages["core2a.html"],pages["core2b.html"])

if __name__=="__main__":
    unittest.main()
