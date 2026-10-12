"""QRT EXPLAIN-D3: sole-rendered authored classification / golden / real Chromium gates.

Reviewer and Owner academic acceptance are explicitly NOT implied by passing these tests.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import unittest
from pathlib import Path

import jsonschema
from Shared.tools import core2_v2

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "TEST/imo-research/qrt-d3/explain.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-explain.manifest.json"
OUT = ROOT / "build/imo182-qrt/d3/explain"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
QID = "Q-TEST-QRT-EXPLAIN-D3-CLASSIFY"
W = "MOVE-EXPLAIN-D3-SIGN-LOSS"
ROLES = ["core1", "core1a", "core1b", "core2a", "core2b"]
BLUEPRINTS = {
  "core1": "BP-CORE1-ORIENTATION@1.1.0",
  "core1a": "BP-CORE1A-CONSTRUCTION@1.8.0",
  "core1b": "BP-CORE1B-RECONSTRUCTION@1.1.0",
  "core2a": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
  "core2b": "BP-CORE2B-TRANSFER@1.1.0"
}
SLOTS = {
  "core1": ["identity","orientation"],
  "core1a": ["identity","construction","repair_closure","repair_closure"],
  "core1b": ["identity","attempt","reconstruction"],
  "core2a": ["identity","attempt","reasoning","support"],
  "core2b": ["identity","attempt","post_attempt"]
}

def sq_candidates(): return [4,-1]
def original(x): return math.sqrt(x+5)==x-1
def changed(x): return math.sqrt(x+5)==abs(x-1)
def exit_check(z): return math.sqrt(z+6)==z

class ExplainD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(SOURCE.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.q = next(q for q in cls.pkg["questions"] if q["id"]==QID)

    def test_1_schema_and_primary_cognitive_demand(self):
        schema = json.loads((ROOT/"Shared/library/package.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self.pkg)
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"EXPLAIN")
        self.assertEqual(self.q["difficulty"]["band"],"D3")
        self.assertEqual(self.q["answer"]["crux_move_ref"],W)
        self.assertEqual(self.manifest["selection"]["core2"],[])
        self.assertEqual(self.manifest["output_roles"],[x.upper() for x in ROLES])
        self.assertEqual(self.manifest["selection"]["core2a"],[QID])
        self.assertEqual(len(self.pkg["questions"]),3)
        self.assertFalse(self.pkg["extensions"]["grade9v3:qrt_admitted"])

    def test_2_independent_original_equation_and_irreversibility(self):
        self.assertEqual(sq_candidates(),[4,-1])
        for x in sq_candidates():
            self.assertEqual(x+5,(x-1)**2)
        self.assertTrue(original(4))
        self.assertFalse(original(-1))
        self.assertEqual(math.sqrt(4),2)
        self.assertEqual(-1-1,-2)
        self.assertGreaterEqual(-1+5,0)  # domain is NOT why candidate fails
        self.assertEqual(3**2,(-3)**2)
        self.assertNotEqual(3,-3)
        self.assertIn("squaring loses sign",self.q["answer"]["summary"])

    def test_3_wrong_converse_and_independent_exit(self):
        self.assertEqual(math.sqrt(9),3)
        self.assertNotEqual(math.sqrt(9),-3)
        self.assertEqual(math.sqrt(9)**2,(-3)**2)
        for z in (3,-2):
            self.assertEqual(z+6,z*z)
        self.assertTrue(exit_check(3))
        self.assertFalse(exit_check(-2))
        self.assertEqual(math.sqrt(-2+6),2)

    def test_4_transfer_rhs_absolute_value_changes_solution_set(self):
        transfer=next(q for q in self.pkg["questions"] if q["id"].endswith("-BOUNDARY"))
        self.assertEqual({x for x in sq_candidates() if changed(x)},{-1,4})
        self.assertEqual({x for x in sq_candidates() if original(x)},{4})
        self.assertEqual(math.sqrt(-1+5),abs(-1-1))
        self.assertEqual(math.sqrt(4+5),abs(4-1))
        self.assertEqual(transfer["answer"]["crux_move_ref"],"MOVE-EXPLAIN-D3-ABS-TRANSFER")
        self.assertIn("Both t=-1 and t=4",transfer["answer"]["summary"])

    def test_5_h3_protected_logic_no_original_solution_leak(self):
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[W])
        self.assertEqual(plan["support_completions"],[{
          "support_ref":"scaffolds[2]",
          "completed_move_refs":[W],
          "availability":"AFTER_ATTEMPT"
        }])
        self.assertEqual([x["availability"] for x in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"EXPLAIN")
        for s in self.q["scaffolds"][:2]:
            self.assertNotIn("x=-1",s["text"])
            self.assertNotIn("x=4",s["text"])
            self.assertNotIn("x-1>=0",s["text"])
            self.assertNotIn("squaring loses sign",s["text"])
        for fig in (ROOT/"TEST/library/figures").glob("qrt-d3-explain-*.svg"):
            body=fig.read_text()
            for leak in ("x=-1","x=4","t=-1","t=4","only x=4","extraneous","x-1>=0","false root"):
                self.assertNotIn(leak,body,fig)

    def test_6_five_governed_roles_and_golden_technique_slots(self):
        receipt=json.loads((OUT/"render-receipt.json").read_text())
        self.assertFalse(receipt["gaps"],receipt["gaps"])
        self.assertEqual(set(receipt["pages"]),{r+".html" for r in ROLES}|{"index.html"})
        golden_lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        for row in golden_lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/row["path"]).read_bytes()).hexdigest(),row["sha256"])
        for role in ROLES:
            html=(OUT/(role+".html")).read_text()
            frozen=(FROZEN/"snapshots"/(role+".html")).read_text()
            self.assertIn('data-blueprint-ref="'+BLUEPRINTS[role]+'"',html)
            self.assertEqual(re.findall('data-blueprint-slot="([^"]+)"',html),SLOTS[role])
            self.assertEqual(re.findall('data-blueprint-slot="([^"]+)"',frozen),SLOTS[role])
            self.assertIn("data-g9-render-digest",html)
            self.assertNotEqual(html,frozen) # authored content is different; exact lock separate
        a=(OUT/"core2a.html").read_text()
        self.assertIn("data-g9-after-attempt-hint",a)
        ladder=a.split('data-g9-ladder-ref=',1)[1].split("</div>",1)[0]
        self.assertNotIn('data-g9-rung="3"',ladder)
        self.assertIn("data-g9-next-rung",ladder)
        self.assertIn("data-requires-attempt",a)
        b=(OUT/"core1b.html").read_text()
        self.assertIn('data-g9-attempt-stage="boundary"',b)
        self.assertIn("data-g9-commit",b)
        trans=(OUT/"core2b.html").read_text()
        self.assertIn("data-g9-commit",trans)
        self.assertIn("data-requires-attempt",trans)

    def test_7_actual_chromium_h3_and_independent_commit(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            for role in ("core2a","core2b","core1b"):
                page=browser.new_page()
                errors=[]
                page.on("pageerror",lambda e: errors.append(str(e)))
                page.goto((OUT/(role+".html")).resolve().as_uri())
                page.wait_for_load_state("domcontentloaded")
                self.assertGreater(page.locator("article[data-g9-unit]").count(),0)
                box=page.locator("article[data-g9-unit]").first
                commit=box.locator("[data-g9-commit]").first
                reveal=box.locator("details[data-requires-attempt]").first
                self.assertGreater(commit.count(),0)
                self.assertGreater(reveal.count(),0)
                reveal.locator("summary").click()
                self.assertFalse(reveal.evaluate("(e)=>e.open"))
                commit.click()
                self.assertNotEqual(box.get_attribute("data-attempted"),"1")
                box.locator("[data-g9-attempt]").first.fill("I wrote a classification with my own coordinate criteria, and justify it.")
                commit.click()
                self.assertEqual(box.get_attribute("data-attempted"),"1")
                self.assertFalse(errors,errors)
                if role=="core2a":
                    h3=box.locator("details[data-requires-attempt]").filter(
                        has=page.locator('summary:text-is("Hint 3 · after your attempt")'))
                    self.assertEqual(h3.count(),1)
                    self.assertFalse(page.locator("[data-g9-after-attempt-hint]").first.is_visible())
                    h3.locator("summary").click()
                    self.assertEqual(page.locator("[data-g9-after-attempt-hint]").count(),1)
                    self.assertTrue(page.locator("[data-g9-after-attempt-hint]").first.is_visible())
                page.close()
            browser.close()

if __name__=="__main__":
    unittest.main()
