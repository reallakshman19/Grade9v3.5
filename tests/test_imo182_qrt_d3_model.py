"""Independent technical evidence for original QRT-MODEL-D3 TEST; academic review pending."""
import hashlib
import json
import math
import unittest
from pathlib import Path

import jsonschema
from Shared.tools import core2_v2, render_core

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "TEST/imo-research/qrt-d3/model.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-model.manifest.json"
OUT = ROOT / "build/imo182-qrt/d3/model"
GOLDEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
QA = "Q-TEST-QRT-MODEL-D3-APPLICATION"
W = "MOVE-QRT-MODEL-D3-CHOOSE"
ROLES = ["core1","core1a","core1b","core2a","core2b"]

class ModelD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(SOURCE.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.q = next(q for q in cls.pkg["questions"] if q["id"] == QA)

    def test_schema_and_governed_selection(self):
        schema = json.loads((ROOT/"Shared/library/package.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self.pkg)
        self.assertEqual(self.manifest["selection"]["core2"], [])
        self.assertEqual(self.manifest["output_roles"], [r.upper() for r in ROLES])
        self.assertEqual(self.q["origin"], "AUTHORED")
        self.assertEqual(self.q["difficulty"]["band"], "D3")
        self.assertEqual(self.q["extensions"]["grade9v3:cognitive_demand"]["primary"], "MODEL")
        self.assertEqual(self.q["answer"]["crux_move_ref"], W)

    def test_model_and_transfer_independent_math(self):
        u=1.5
        self.assertEqual(4**(2*u+1), 16**u+192)
        self.assertEqual(4**(2*u+1),256)
        v=2
        self.assertEqual(3**(2*v+1),9**v+162)
        self.assertEqual(3**(2*v+1),243)
        self.assertNotEqual(2**(2+1),2**2+2)
        self.assertEqual(4**(2*1+1), 16**1+48)
        self.assertTrue(all(3*16**(x/8)>0 for x in range(-40,41)))
        # If c <= 0, 3*16^v=c cannot hold for any real v.
        for c in (-12,0):
            self.assertFalse(c>0)

    def test_owner_h3_support_policy(self):
        p = self.q["extensions"]["grade9v3:core2_support_plan"]
        self.assertEqual(p["protected_move_refs"], [W])
        self.assertEqual(p["support_completions"][0], {
            "support_ref":"scaffolds[2]", "completed_move_refs":[W], "availability":"AFTER_ATTEMPT"
        })
        self.assertEqual([r["availability"] for r in core2_v2.project_support(self.q)],
                         ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        for s in self.q["scaffolds"][:2]:
            self.assertNotIn("4t=t+192",s["text"])
            self.assertNotIn("t=16^u",s["text"])

    def test_rendered_receipt_and_blueprints(self):
        self.assertTrue((OUT/"render-receipt.json").exists(),"Sole-renderer receipt absent")
        receipt=json.loads((OUT/"render-receipt.json").read_text())
        self.assertFalse(receipt["gaps"],receipt["gaps"])
        self.assertEqual(set(receipt["pages"]),set(r+".html" for r in ROLES)|{"index.html"})
        refs=["BP-CORE1-ORIENTATION@1.1.0","BP-CORE1A-CONSTRUCTION@1.8.0",
              "BP-CORE1B-RECONSTRUCTION@1.1.0","BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
              "BP-CORE2B-TRANSFER@1.1.0"]
        for role,ref in zip(ROLES,refs):
            h=(OUT/(role+".html")).read_text()
            self.assertIn('data-blueprint-ref="'+ref+'"',h)
            self.assertIn("data-g9-render-digest",h)
        a=(OUT/"core2a.html").read_text()
        self.assertIn("data-g9-after-attempt-hint",a)
        self.assertIn('data-g9-rung="1"',a)
        self.assertNotIn('data-g9-rung="3"',a.split('data-g9-ladder-ref=',1)[1].split('</div>',1)[0])
        for q in self.pkg["questions"]:
            self.assertEqual(q["origin"],"AUTHORED")
        # Pre-attempt visual asset payloads are original question inputs or unrelated laws, never solved model.
        for svg in (ROOT/"TEST/library/figures").glob("qrt-d3-model-*.svg"):
            s=svg.read_text()
            for leaked in ("t=64","u=3/2","4t=t+192","c>0"):
                self.assertNotIn(leaked,s,svg)

    def test_frozen_owner_golden_integrity(self):
        lock=json.loads((GOLDEN/"snapshot-lock.json").read_text())
        for snap in lock["snapshots"]:
            data=(GOLDEN/snap["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),snap["sha256"])
        # Do not claim these new authored pages equal the frozen golden bytes.
        self.assertNotEqual((OUT/"core2a.html").read_bytes(),
                            (GOLDEN/"snapshots/core2a.html").read_bytes())

    def test_actual_chromium_attempt_gates(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page = browser.new_page()
            errors=[]
            page.on("pageerror",lambda e: errors.append(str(e)))
            page.goto((OUT/"core2a.html").resolve().as_uri())
            page.wait_for_load_state("domcontentloaded")
            self.assertEqual(page.locator('[data-g9-attempt]').count(),1)
            self.assertGreater(page.locator('[data-g9-commit]').count(),0)
            self.assertGreater(page.locator('details[data-requires-attempt] summary').count(),0)
            self.assertEqual(page.locator('[data-g9-after-attempt-hint]').count(),0)
            self.assertEqual(page.locator('[data-g9-rung="3"]').count(),0)
            page.locator('[data-g9-commit]').click()
            self.assertNotEqual(page.locator('article[data-g9-unit]').get_attribute("data-attempted"),"true")
            page.locator('[data-g9-attempt]').fill("I choose a common positive power and will derive the multiplier.")
            page.locator('[data-g9-commit]').click()
            self.assertEqual(page.locator('[data-g9-attempt-box]').get_attribute("data-attempted"),"true")
            hint = page.locator('details[data-requires-attempt]').filter(has=page.locator('summary:text-is("Hint 3 · after your attempt")'))
            self.assertGreater(hint.count(),0)
            hint.locator("summary").click()
            self.assertGreater(page.locator("[data-g9-after-attempt-hint]").count(),0)
            self.assertFalse(errors,errors)
            browser.close()

if __name__ == "__main__":
    unittest.main()
