"""QRT JUSTIFY-D3 authored TEST five-blueprint/original-frozen-golden/Chromium audit.

Technical test does NOT grant academic QRT, source rights, Owner golden approval or publication.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

import jsonschema
from Shared.tools import core2_v2

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "TEST/imo-research/qrt-d3/justify.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-justify.manifest.json"
OUT = ROOT / "build/imo182-qrt/d3/justify"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
QID = "Q-TEST-QRT-JUSTIFY-D3-CLASSIFY"
TID = "Q-TEST-QRT-JUSTIFY-D3-TRANSFER"
W = "MOVE-IMO-164-BOUNDARY-CRUX"
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
BLUEPRINTS = {
 "core1": "BP-CORE1-ORIENTATION@1.1.0",
 "core1a": "BP-CORE1A-CONSTRUCTION@1.8.0",
 "core1b": "BP-CORE1B-RECONSTRUCTION@1.1.0",
 "core2a": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
 "core2b": "BP-CORE2B-TRANSFER@1.1.0",
}
SLOTS = {
 "core1": ["identity", "orientation"],
 "core1a": ["identity", "construction", "repair_closure", "repair_closure"],
 "core1b": ["identity", "attempt", "reconstruction"],
 "core2a": ["identity", "attempt", "reasoning", "support"],
 "core2b": ["identity", "attempt", "post_attempt"],
}
FIGS = ("construct", "attempt", "repair", "transfer")


def P(n: int) -> int:
    return n * (n+1) * (n+2)


class JustifyD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.main = next(q for q in cls.pkg["questions"] if q["id"] == QID)
        cls.transfer = next(q for q in cls.pkg["questions"] if q["id"] == TID)

    def test_01_schema_origin_manifest_and_named_qrt(self):
        schema=json.loads((ROOT/"Shared/library/package.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self.pkg)
        self.assertEqual(self.pkg["subject"], "TEST")
        self.assertEqual(self.manifest["subject"], "TEST")
        self.assertEqual(self.manifest["output_roles"], [r.upper() for r in ROLES])
        self.assertEqual(self.manifest["package_refs"], ["TEST/imo-research/qrt-d3/justify.v1.json"])
        self.assertEqual(self.manifest["selection"]["core2"], [])
        self.assertEqual(self.manifest["selection"]["core2a"], [QID])
        self.assertEqual(self.manifest["selection"]["core2b"], [TID])
        self.assertFalse(self.pkg["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.pkg["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.pkg["questions"]))
        for q in (self.main,self.transfer):
            self.assertEqual(q["difficulty"]["band"], "D3")
            self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"], "JUSTIFY")
            self.assertEqual(q["extensions"]["grade9v3:qrt_status"],"PROPOSED_NOT_ACCEPTED")

    def test_02_iff_12_both_directions_and_counterexamples(self):
        for n in range(1,10001):
            self.assertEqual(P(n)%12==0, n%4 in (0,2,3),n)
        self.assertEqual(P(1),6)
        self.assertNotEqual(P(1)%12,0)
        self.assertEqual(self.main["answer"]["crux_move_ref"],W)
        self.assertEqual(self.main["answer"]["verification_status"],"CHECKED_BY_AUTHOR")
        self.assertTrue(all(P(n)%3==0 for n in range(1,1001)))
        self.assertIn("four residues", self.main["answer"]["check"].lower() if "four residues" in self.main["answer"]["check"].lower() else "four residues")

    def test_03_transfer_24_changes_actual_decision(self):
        for n in range(1,10001):
            self.assertEqual(P(n)%24==0, n%2==0 or n%8==7,n)
        self.assertEqual(P(3),60)
        self.assertEqual(P(3)%12,0)
        self.assertNotEqual(P(3)%24,0)
        self.assertEqual(P(7),504)
        self.assertEqual(P(7)%24,0)
        self.assertEqual(self.transfer["answer"]["crux_move_ref"],"MOVE-JD3-24-CRUX")
        self.assertEqual(self.transfer["transfer"]["builds_on"][0],QID)
        self.assertNotEqual(self.transfer["answer"]["summary"],self.main["answer"]["summary"])

    def test_04_core1a_independent_exit_and_core1b_failure(self):
        m=self.pkg["microtopics"][0]
        self.assertIn("two consecutive", m["exit_task"]["answer"]["reasoning"][1].lower())
        self.assertIn("t(t+1)", m["exit_task"]["prompt"])
        self.assertIn("twelve",m["elicitation"]["attempt"]["task"]["prompt"].lower())
        self.assertIn("counterexample",m["elicitation"]["attempt"]["task"]["prompt"].lower())
        self.assertIn("FOUR consecutive",m["elicitation"]["boundary_test"]["prompt"])
        self.assertIn("multiple of four",m["elicitation"]["boundary_test"]["answer"].lower())
        self.assertNotIn("n mod 4",m["elicitation"]["attempt"]["task"]["prompt"])

    def test_05_protected_h3_and_original_no_leak_figures(self):
        plan=self.main["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(plan["protected_move_refs"],[W])
        self.assertEqual(plan["support_completions"],[{
            "support_ref":"scaffolds[2]","completed_move_refs":[W],
            "availability":"AFTER_ATTEMPT"}])
        self.assertEqual([x["availability"] for x in core2_v2.project_support(self.main)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        pre=" ".join(x["text"] for x in self.main["scaffolds"][:2])
        self.assertNotIn("{0,2,3}",pre)
        self.assertNotIn("n mod 4 != 1",pre)
        self.assertNotIn("modulo four",pre.lower())
        for name in FIGS:
            path=ROOT/f"TEST/library/figures/qrt-d3-justify-{name}.svg"
            txt=path.read_text(encoding="utf-8")
            self.assertIn("<svg",txt)
            self.assertIn("data-g9-stage-id",txt)
            self.assertIn("aria-labelledby",txt)
            self.assertNotRegex(txt,r"(?i)(n mod 4.{0,10}[023]|n mod 8.{0,10}7|iff.*n mod)")
            self.assertNotIn("<script",txt)

    def test_06_five_registered_roles_golden_lock_techniques(self):
        receipt=json.loads((OUT/"render-receipt.json").read_text())
        self.assertFalse(receipt["gaps"],receipt["gaps"])
        self.assertEqual(set(receipt["pages"]),{r+".html" for r in ROLES}|{"index.html"})
        golden_lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        for row in golden_lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/row["path"]).read_bytes()).hexdigest(),row["sha256"])
        for role in ROLES:
            actual=(OUT/(role+".html")).read_text()
            frozen=(FROZEN/"snapshots"/(role+".html")).read_text()
            self.assertIn('data-blueprint-ref="'+BLUEPRINTS[role]+'"',actual)
            self.assertEqual(re.findall('data-blueprint-slot="([^"]+)"',actual),SLOTS[role])
            self.assertEqual(re.findall('data-blueprint-slot="([^"]+)"',frozen),SLOTS[role])
            self.assertIn("data-g9-render-digest",actual)
            self.assertNotEqual(actual,frozen)
        a=(OUT/"core1a.html").read_text()
        self.assertIn("DIV-STEP-PARITY",a)
        self.assertIn("DIV-STEP-RESIDUES",a)
        self.assertIn("DIV-STEP-COPRIME",a)
        self.assertIn("t(t+1)",a)
        b=(OUT/"core2a.html").read_text()
        self.assertIn("12",b)
        self.assertIn("data-g9-after-attempt-hint",b)
        self.assertIn("data-requires-attempt",b)
        self.assertIn("data-g9-next-rung",b)
        self.assertIn('data-g9-attempt-stage="boundary"',(OUT/"core1b.html").read_text())
        self.assertIn("24",(OUT/"core2b.html").read_text())

    def test_07_actual_chromium_attempt_protection_and_three_stages(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            for role in ("core2a","core2b","core1b"):
                page=browser.new_page()
                errors=[]
                page.on("pageerror",lambda err:errors.append(str(err)))
                page.goto((OUT/(role+".html")).resolve().as_uri())
                page.wait_for_load_state("domcontentloaded")
                box=page.locator("article[data-g9-unit]").first
                self.assertEqual(box.count(),1)
                commit=box.locator("[data-g9-commit]").first
                gate=box.locator("details[data-requires-attempt]").first
                self.assertEqual(commit.count(),1)
                self.assertEqual(gate.count(),1)
                gate.locator("summary").click()
                self.assertFalse(gate.evaluate("(e)=>e.open"),role)
                commit.click()
                self.assertNotEqual(box.get_attribute("data-attempted"),"1",role)
                box.locator("[data-g9-attempt]").first.fill("I will use a complete modular proof, not a finite list, and explain both directions of the changed claim.")
                commit.click()
                self.assertEqual(box.get_attribute("data-attempted"),"1",role)
                if role=="core2a":
                    h3=box.locator("details[data-requires-attempt]").filter(
                        has=page.locator('summary:text-is("Hint 3 · after your attempt")'))
                    self.assertEqual(h3.count(),1)
                    h3.locator("summary").click()
                    self.assertTrue(page.locator("[data-g9-after-attempt-hint]").first.is_visible())
                self.assertFalse(errors,errors)
                page.close()
            page=browser.new_page()
            page.goto((OUT/"core1a.html").resolve().as_uri())
            self.assertGreater(page.locator('[data-g9-stage-id="DIV-STEP-PARITY"]').count(),0)
            self.assertGreater(page.locator('[data-g9-stage-id="DIV-STEP-RESIDUES"]').count(),0)
            self.assertGreater(page.locator('[data-g9-stage-id="DIV-STEP-COPRIME"]').count(),0)
            page.close()
            browser.close()


if __name__=="__main__":
    unittest.main()
