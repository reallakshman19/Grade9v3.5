"""QRT REPRESENT-D3: sole-rendered authored lattice representations / golden / real Chromium gates.

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
SOURCE = ROOT / "TEST/imo-research/qrt-d3/represent.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-represent.manifest.json"
OUT = ROOT / "build/imo182-qrt/d3/represent"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
QID = "Q-TEST-QRT-REPRESENT-D3-CLASSIFY"
W = "MOVE-REPRESENT-D3-OVERLAP"
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

def count_paths(size:int, points:tuple[tuple[int,int],tuple[int,int]])->dict[str,int]:
    result={"total":0,"through_first":0,"through_second":0,"both":0,"avoid":0}
    def visit(x:int,y:int,visited:int)->None:
        if (x,y)==(size,size):
            result["total"]+=1
            if visited&1: result["through_first"]+=1
            if visited&2: result["through_second"]+=1
            if visited==3: result["both"]+=1
            if visited==0: result["avoid"]+=1
            return
        for xx,yy in ((x+1,y),(x,y+1)):
            if xx>size or yy>size: continue
            mark=0
            for i,pt in enumerate(points):
                if (xx,yy)==pt: mark|=1<<i
            visit(xx,yy,visited|mark)
    visit(0,0,0)
    return result

class RepresentD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(SOURCE.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.q = next(q for q in cls.pkg["questions"] if q["id"]==QID)

    def test_1_schema_and_primary_cognitive_demand(self):
        schema = json.loads((ROOT/"Shared/library/package.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self.pkg)
        self.assertEqual(self.q["origin"],"AUTHORED")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"REPRESENT")
        self.assertEqual(self.q["difficulty"]["band"],"D3")
        self.assertEqual(self.q["answer"]["crux_move_ref"],W)
        self.assertEqual(self.manifest["selection"]["core2"],[])
        self.assertEqual(self.manifest["output_roles"],[x.upper() for x in ROLES])
        self.assertEqual(self.manifest["selection"]["core2a"],[QID])
        self.assertEqual(len(self.pkg["questions"]),3)
        self.assertFalse(self.pkg["extensions"]["grade9v3:qrt_admitted"])

    def test_2_exhaustive_four_by_four_original_path_families(self):
        result=count_paths(4,((1,2),(3,2)))
        self.assertEqual(result,{
            "total":70,"through_first":30,"through_second":30,
            "both":9,"avoid":19
        })
        self.assertEqual(70-30-30+9,19)
        self.assertIn("19",self.q["answer"]["summary"])
        self.assertEqual(self.q["answer"]["crux_move_ref"],W)

    def test_3_core1b_changed_grid_and_independent_exit(self):
        result=count_paths(3,((1,1),(2,2)))
        self.assertEqual(result,{
            "total":20,"through_first":12,"through_second":12,
            "both":8,"avoid":4
        })
        self.assertEqual(20-12-12+8,4)
        self.assertLess(20-12-12,0)  # diagnose naive subtract-only
        exit_task=self.pkg["microtopics"][0]["exit_task"]
        self.assertIn("4",exit_task["answer"]["summary"])

    def test_4_changed_marker_coordinate_order_transfer(self):
        moved=count_paths(4,((1,2),(2,1)))
        self.assertEqual(moved,{
            "total":70,"through_first":30,"through_second":30,
            "both":0,"avoid":10
        })
        self.assertEqual(moved["avoid"],70-30-30)
        self.assertEqual(moved["both"],0)
        transfer=next(q for q in self.pkg["questions"] if q["id"].endswith("-BOUNDARY"))
        self.assertEqual(transfer["answer"]["crux_move_ref"],"MOVE-REPRESENT-D3-DISJOINT")
        self.assertIn("10",transfer["answer"]["summary"])

    def test_5_h3_safe_before_attempt_and_authored_grid_nonleakage(self):
        plan=self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[W])
        self.assertEqual(plan["support_completions"],[{
            "support_ref":"scaffolds[2]",
            "completed_move_refs":[W],
            "availability":"AFTER_ATTEMPT"
        }])
        self.assertEqual([s["availability"] for s in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"],"REPRESENT")
        for scaffold in self.q["scaffolds"][:2]:
            for banned in ("70-30-30+9","19","through both 9","three segments S->P->Q"):
                self.assertNotIn(banned,scaffold["text"])
        for fig in (ROOT/"TEST/library/figures").glob("qrt-d3-represent-*.svg"):
            svg=fig.read_text()
            visible=" ".join(re.findall(
                r"<(?:text|title|desc)\b[^>]*>([^<]*)</(?:text|title|desc)>",svg
            ))
            aria=" ".join(re.findall(r'aria-label="([^"]*)"',svg))
            for banned in ("19 paths","10 paths","9 paths","intersection 9","70-30-30+9"):
                self.assertNotIn(banned,visible+" "+aria,fig)
            self.assertIn("data-g9-stage-id",svg)

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
                box.locator("[data-g9-attempt]").first.fill("I represented forbidden path families and reasoned about their intersection before counting.")
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
