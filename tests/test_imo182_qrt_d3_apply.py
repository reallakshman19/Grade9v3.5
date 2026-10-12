"""QRT APPLY-D3: sole-rendered authored number-theory application / golden / real Chromium gates.

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
SOURCE = ROOT / "TEST/imo-research/qrt-d3/apply.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-apply.manifest.json"
OUT = ROOT / "build/imo182-qrt/d3/apply"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
QID = "Q-TEST-QRT-APPLY-D3-CLASSIFY"
W = "MOVE-APPLY-D3-VALUATION-BRIDGE"
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

def works(n:int,first:int,first_power:int,second:int,second_power:int)->bool:
    return n>0 and n**first_power%first==0 and n**second_power%second==0

def exhaustive_min(first:int,first_power:int,second:int,second_power:int)->int:
    return next(n for n in range(1,3000) if works(n,first,first_power,second,second_power))

def prime_valuation(n:int,p:int)->int:
    r=0
    while n%p==0:
        r+=1
        n//=p
    return r

class ApplyD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(SOURCE.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.q = next(q for q in cls.pkg["questions"] if q["id"]==QID)

    def test_1_schema_and_primary_cognitive_demand(self):
        schema = json.loads((ROOT/"Shared/library/package.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self.pkg)
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"APPLY")
        self.assertEqual(self.q["difficulty"]["band"],"D3")
        self.assertEqual(self.q["answer"]["crux_move_ref"],W)
        self.assertEqual(self.manifest["selection"]["core2"],[])
        self.assertEqual(self.manifest["output_roles"],[x.upper() for x in ROLES])
        self.assertEqual(self.manifest["selection"]["core2a"],[QID])
        self.assertEqual(len(self.pkg["questions"]),3)
        self.assertFalse(self.pkg["extensions"]["grade9v3:qrt_admitted"])

    def test_2_independent_original_divisibilities_and_minimality(self):
        self.assertEqual(exhaustive_min(72,2,135,3),60)
        self.assertEqual(72,2**3*3**2)
        self.assertEqual(135,3**3*5)
        self.assertEqual(60**2//72,50)
        self.assertEqual(60**3//135,1600)
        self.assertTrue(works(60,72,2,135,3))
        self.assertFalse(any(works(n,72,2,135,3) for n in range(1,60)))
        self.assertEqual({p:prime_valuation(60,p) for p in (2,3,5)},{2:2,3:1,5:1})
        self.assertIn("60",self.q["answer"]["summary"])

    def test_3_core1b_countercase_and_independent_exit(self):
        self.assertEqual(exhaustive_min(16,2,27,3),12)
        self.assertTrue(works(12,16,2,27,3))
        self.assertEqual(12**2//16,9)
        self.assertEqual(12**3//27,64)
        self.assertEqual(math.lcm(16,27),432)
        self.assertEqual(exhaustive_min(200,2,81,3),180)
        self.assertEqual(180**2//200,162)
        self.assertEqual(180**3//81,72000)
        self.assertFalse(any(works(n,200,2,81,3) for n in range(1,180)))

    def test_4_transfer_swapped_power_changes_bindings(self):
        q=next(q for q in self.pkg["questions"] if q["id"].endswith("-BOUNDARY"))
        self.assertEqual(exhaustive_min(72,3,135,2),90)
        self.assertEqual(90**3//72,10125)
        self.assertEqual(90**2//135,60)
        self.assertFalse(works(60,72,3,135,2))
        self.assertEqual({p:prime_valuation(90,p) for p in (2,3,5)},{2:1,3:2,5:1})
        self.assertEqual(q["answer"]["crux_move_ref"],"MOVE-APPLY-D3-SWAPPED-POWERS")
        self.assertIn("90",q["answer"]["summary"])

    def test_5_approved_h3_timing_and_precommit_nonleakage(self):
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[W])
        self.assertEqual(plan["support_completions"],[{
          "support_ref":"scaffolds[2]",
          "completed_move_refs":[W],
          "availability":"AFTER_ATTEMPT"
        }])
        self.assertEqual([s["availability"] for s in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"APPLY")
        for scaffold in self.q["scaffolds"][:2]:
            for banned in ("60","v2>=2","v3>=1","v5>=1","ceil(a/r)","maximum of", "take the max"):
                self.assertNotIn(banned,scaffold["text"])
        for fig in (ROOT/"TEST/library/figures").glob("qrt-d3-apply-*.svg"):
            raw=fig.read_text()
            for banned in ("60","90","180","1080","v2=2","v3=1","2²·3·5","least n is"):
                self.assertNotIn(banned,raw,fig)

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
                box.locator("[data-g9-attempt]").first.fill("I applied prime-exponent thresholds independently and wrote a leastness justification.")
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
