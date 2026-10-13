"""Issue #182, Tab7: authored JUSTIFY-D4 candidate; NOT academic acceptance."""
import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from Shared.tools import core2_v2, render_core

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "TEST/imo-research/qrt-d4/justify-d4.package.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d4-justify.manifest.json"
SCHEMA = ROOT / "Shared/library/package.schema.json"
ID = "Q-D4-JUSTIFY-24"

class AuthoredJustifyD4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.question = next(q for q in cls.data["questions"] if q["id"] == ID)

    def test_schema_and_custody(self):
        Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(self.data)
        self.assertEqual(self.question["origin"], "AUTHORED")
        self.assertFalse(self.data["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(self.data["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertEqual(self.manifest["selection"]["core2"], [])
        self.assertEqual(self.manifest["output_roles"], ["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
        self.assertEqual(self.question["extensions"]["grade9v3:cognitive_demand"]["primary"],"JUSTIFY")
        self.assertEqual(self.question["difficulty"]["band"], "D4")
        self.assertEqual(self.question["extensions"]["grade9v3:core2_support_plan"]["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        projections=core2_v2.project_support(self.question)
        self.assertEqual([x["availability"] for x in projections], ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])

    def test_integer_iff_and_independent_exit(self):
        qualifying24={n%24 for n in range(-10000,10001) if (n*n-1)%24 == 0}
        qualifying48={n%24 for n in range(-10000,10001) if (n*n-1)%48 == 0}
        self.assertEqual(qualifying24, {1,5,7,11,13,17,19,23})
        self.assertEqual(qualifying48, {1,7,17,23})
        for n in range(-10000,10001):
            with self.subTest(n=n):
                self.assertEqual((n*n-1)%24==0, n%6 in {1,5})
                self.assertEqual((n*n-1)%48==0, n%24 in {1,7,17,23})
                self.assertEqual((n*(n+2))%8==0, n%2==0)

    def test_rendered_blueprint_roles_and_h3_after_attempt(self):
        pages,gaps,digest,*_ = render_core.build_report(MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(gaps, [], str(gaps))
        self.assertEqual(set(pages), {"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        expected={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,bp in expected.items():
            with self.subTest(role=role):
                h=pages[role+".html"]
                self.assertIn('data-blueprint-ref="'+bp+'"',h)
                self.assertIn('data-g9-render-digest',h)
        # Golden comparison is role/slot semantics, not byte identity:
        # different authored questions must not be cloned from the frozen fixture.
        golden=ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
        slot_pattern=r'<section class="blueprint-slot (slot-[a-z_]+)"'
        for role in expected:
            with self.subTest(golden_role=role):
                fixture=(golden/(role+".html")).read_text(encoding="utf-8")
                produced=pages[role+".html"]
                self.assertEqual(re.findall(slot_pattern,produced),re.findall(slot_pattern,fixture))
                self.assertNotEqual(produced,fixture,"Author-only D4 must have distinct mathematical content.")
        h=pages["core2a.html"]
        self.assertIn('data-g9-after-attempt-hint',h)
        self.assertIn('data-requires-attempt',h)
        self.assertIn('data-g9-hint-order="3"',h)
        self.assertIn('data-g9-payload="CORE2A-'+ID+'-after-attempt-hint-3"',h)
        ladder=h.split('data-g9-ladder-ref="CORE2A-',1)[1].split("</div>",1)[0]
        self.assertNotIn("After recording your first attempt", ladder)
        self.assertIn("After recording your first attempt",h)
        self.assertIn("Reasoning route and full solution",h)
        self.assertNotEqual(pages["core2a.html"],pages["core2b.html"])

if __name__ == "__main__":
    unittest.main()
