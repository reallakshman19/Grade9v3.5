"""Original SYNTHESIZE D4 mathematics, governed five-role rendering, source hold."""
from itertools import permutations
import json
import re
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from Shared.tools import core2_v2, render_core

ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/"TEST/imo-research/qrt-d4/synthesize-d4.package.json"
MANIFEST=ROOT/"TEST/products/imo203-qrt-d4-synthesize.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
GOLDEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"

def eligible(*divisors):
    digits=(0,1,2,3,4,8)
    found=[]
    for order in permutations(digits):
        if not order[0]:
            continue
        value=int("".join(map(str,order)))
        if all(value % d == 0 for d in divisors):
            found.append(value)
    return sorted(found)


class SynthesizeD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(PKG.read_text())
        cls.m=json.loads(MANIFEST.read_text())
        cls.q=next(x for x in cls.p["questions"] if x["id"]=="Q-D4-SYNTHESIZE-MAIN")

    def test_schema_authorship_and_protected_h3(self):
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
        self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.m["selection"]["core2"],[])
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"SYNTHESIZE")
        self.assertEqual(self.q["difficulty"]["band"],"D4")
        for key in ("grade9v3:qrt_admitted","grade9v3:core2_source_custody_granted","grade9v3:learner_published"):
            self.assertFalse(self.p["extensions"][key])
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],["D4-SYN-MOVE-ORDER"])
        self.assertEqual(plan["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        self.assertEqual([s["availability"] for s in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertTrue(all("120384" not in s["text"] for s in self.q["scaffolds"][:2]))
        for rep in self.p["representations"]:
            svg=(ROOT/rep["rendered_asset_refs"][0]).read_text()
            self.assertIn("data-g9-stage-id",svg)
            self.assertNotIn("120384",svg)
            self.assertNotIn("130284",svg)

    def test_independent_permutation_oracle_and_minimality(self):
        original=eligible(4,9,11)
        changed=eligible(4,9,11,7)
        self.assertEqual(len(original),24)
        self.assertEqual(original[0],120384)
        self.assertEqual(changed[0],130284)
        self.assertEqual([n for n in original if str(n).startswith("12")],[120384,128304])
        self.assertFalse(any(str(n).startswith("10") for n in original))
        self.assertEqual([n for n in changed if str(n).startswith("13")],[130284])
        self.assertTrue(all(n%7!=0 for n in (120384,128304)))
        self.assertEqual((130284%4,130284%9,130284%11,130284%7),(0,0,0,0))
        for n in original:
            digits=list(map(int,str(n)))
            self.assertEqual(sum(digits[::2]),9)
            self.assertEqual(sum(digits[1::2]),9)

    def test_registered_five_role_semantic_blueprint_slots(self):
        pages,gaps,*_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(gaps,[])
        self.assertEqual(set(pages),{"core1.html","core1a.html","core1b.html","core2a.html","core2b.html","index.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        slot=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        for role,ref in refs.items():
            with self.subTest(role=role):
                html=pages[role+".html"]
                self.assertIn('data-blueprint-ref="'+ref+'"',html)
                if GOLDEN.exists():
                    self.assertEqual(re.findall(slot,html),re.findall(slot,(GOLDEN/(role+".html")).read_text()))
        self.assertIn("data-g9-after-attempt-hint",pages["core2a.html"])
        self.assertIn("data-requires-attempt",pages["core2a.html"])
        self.assertNotEqual(pages["core2a.html"],pages["core2b.html"])

if __name__=="__main__":
    unittest.main()
