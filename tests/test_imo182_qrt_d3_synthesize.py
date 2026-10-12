"""QRT SYNTHESIZE-D3: sole-rendered authored digit/divisibility synthesis / golden / real Chromium gates.

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
SOURCE = ROOT / "TEST/imo-research/qrt-d3/synthesize.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-synthesize.manifest.json"
OUT = ROOT / "build/imo182-qrt/d3/synthesize"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
QID = "Q-TEST-QRT-SYNTHESIZE-D3-CLASSIFY"
W = "MOVE-SYNTHESIZE-D3-JOINT-COUNT"
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

def digit_ap(n:int)->bool:
    h,t,u=n//100,n//10%10,n%10
    return h+u==2*t

def census(divisor:int,odd_units:bool=False)->list[int]:
    return [n for n in range(100,1000)
            if digit_ap(n) and n%divisor==0
            and (not odd_units or (n%10)%2==1)]

class SynthesizeD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(SOURCE.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.q = next(q for q in cls.pkg["questions"] if q["id"]==QID)

    def test_1_schema_and_primary_cognitive_demand(self):
        schema = json.loads((ROOT/"Shared/library/package.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self.pkg)
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"SYNTHESIZE")
        self.assertEqual(self.q["difficulty"]["band"],"D3")
        self.assertEqual(self.q["answer"]["crux_move_ref"],W)
        self.assertEqual(self.manifest["selection"]["core2"],[])
        self.assertEqual(self.manifest["output_roles"],[x.upper() for x in ROLES])
        self.assertEqual(self.manifest["selection"]["core2a"],[QID])
        self.assertEqual(len(self.pkg["questions"]),3)
        self.assertFalse(self.pkg["extensions"]["grade9v3:qrt_admitted"])

    def test_2_independent_full_original_digit_enumeration(self):
        got=census(9)
        self.assertEqual(len(got),14)
        self.assertEqual(got,[135,234,333,369,432,468,531,567,630,666,765,864,963,999])
        by_middle={t:[n for n in got if n//10%10==t] for t in (3,6,9)}
        self.assertEqual({t:len(a) for t,a in by_middle.items()},{3:6,6:7,9:1})
        self.assertEqual(set(n//10%10 for n in got),{3,6,9})
        self.assertIn(630,got)
        self.assertEqual(self.q["answer"]["crux_move_ref"],W)

    def test_3_core1b_wrong_rule_and_independent_odd_units_exit(self):
        self.assertTrue(digit_ap(246))
        self.assertNotEqual(246%9,0)
        self.assertTrue(0+6==2*3) # 036 forms a word but not a three-digit integer
        self.assertNotIn(36,census(9))
        exit_numbers=census(9,odd_units=True)
        self.assertEqual(exit_numbers,[135,333,369,531,567,765,963,999])
        self.assertEqual(len(exit_numbers),8)
        self.assertIn("8",self.pkg["microtopics"][0]["exit_task"]["answer"]["summary"])

    def test_4_divisible_six_transfer_changes_binding_digit(self):
        got=census(6)
        self.assertEqual(got,[210,222,234,246,258,420,432,444,456,468,630,642,654,666,678,840,852,864,876,888])
        self.assertEqual(len(got),20)
        self.assertTrue(all(n%10%2==0 for n in got))
        self.assertEqual(len([n for n in got if n//10%10 not in (3,6,9)]),14)
        transfer=next(q for q in self.pkg["questions"] if q["id"].endswith("-BOUNDARY"))
        self.assertEqual(transfer["answer"]["crux_move_ref"],"MOVE-SYNTHESIZE-D3-SIX-TRANSFER")
        self.assertIn("20",transfer["answer"]["summary"])

    def test_5_h3_before_attempt_and_authored_svg_visible_nonleakage(self):
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[W])
        self.assertEqual(plan["support_completions"],[{
            "support_ref":"scaffolds[2]",
            "completed_move_refs":[W],
            "availability":"AFTER_ATTEMPT"
        }])
        self.assertEqual([s["availability"] for s in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"SYNTHESIZE")
        for hint in self.q["scaffolds"][:2]:
            for leak in ("T=3,6,9","6+7+1","14 numbers","k=-3"):
                self.assertNotIn(leak,hint["text"])
        for fig in (ROOT/"TEST/library/figures").glob("qrt-d3-synthesize-*.svg"):
            raw=fig.read_text()
            visible=" ".join(re.findall(
               r"<(?:text|title|desc)\b[^>]*>([^<]*)</(?:text|title|desc)>",raw
            ))
            aria=" ".join(re.findall(r'aria-label="([^"]*)"',raw))
            for banned in ("14 numbers","20 numbers","6+7+1","T=3,6,9","135,234"):
                self.assertNotIn(banned,visible+" "+aria,fig)
            self.assertIn("data-g9-stage-id",raw)

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
                box.locator("[data-g9-attempt]").first.fill("I combined the arithmetic-progression digit condition, divisibility and decimal bounds into my own case-count reasoning.")
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
