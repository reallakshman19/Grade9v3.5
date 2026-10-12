"""Issue #182: wholly authored REPRESENT-D1; technical-only five-role regression."""
from __future__ import annotations
import json
import re
import unittest
from pathlib import Path
from Shared.tools import render_core, core2_v2

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "TEST/imo-research/qrt-d1/represent.v1.json"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d1-represent.manifest.json"
GOLDEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
QUESTION = "Q-TEST-IMO182-D1-CORE2A-WORDS-TO-PAIR"

class RepresentD1Renderer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.pages, cls.gaps, cls.digest, _, _ = render_core.build_report(MANIFEST, "PAGES", held_to="REFERENCE")

    def test_five_registered_roles_without_reference_gaps(self):
        self.assertEqual(self.gaps, [], self.gaps)
        self.assertEqual(set(self.pages), {"index.html", "core1.html", "core1a.html", "core1b.html", "core2a.html", "core2b.html"})
        expected = {"core1":"BP-CORE1-ORIENTATION@1.1.0", "core1a":"BP-CORE1A-CONSTRUCTION@1.8.0", "core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0", "core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0", "core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,blueprint in expected.items():
            with self.subTest(role=role):
                self.assertIn('data-blueprint-ref="'+blueprint+'"', self.pages[role+".html"])
        self.assertNotIn("core2.html", self.pages)

    def test_authored_rights_and_protected_move(self):
        q = next(q for q in self.source["questions"] if q["id"]==QUESTION)
        self.assertEqual(q["origin"], "AUTHORED")
        self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"],"REPRESENT")
        self.assertEqual(q["difficulty"]["band"],"D1")
        self.assertEqual(q["answer"]["summary"].startswith("(4,−2)"), True)
        self.assertEqual(q["extensions"]["grade9v3:core2_support_plan"]["support_completions"][0]["availability"],"AFTER_ATTEMPT")
        stages = core2_v2.project_support(q)
        self.assertEqual([x["availability"] for x in stages],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertEqual(q["answer"]["crux_move_ref"], q["extensions"]["grade9v3:core2_support_plan"]["protected_move_refs"][0])

    def test_accessible_first_stage_assets_do_not_leak_target_answer(self):
        paths = [ROOT / p for r in self.source["representations"] for p in r["rendered_asset_refs"]]
        for path in paths:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("(4,−2)",content)
                self.assertNotIn("(4,-2)",content)
                self.assertIn('data-g9-stage-id=',content)
                self.assertIn("<desc>", content)
        core2a = self.pages["core2a.html"]
        self.assertIn("4 grid units EAST",core2a)
        self.assertIn("data-g9-after-attempt-hint",core2a)
        self.assertIn("data-requires-attempt",core2a)
        self.assertIn("Reasoning route and full solution",core2a)

    def test_reconstruction_and_transfer_are_changed_decisions(self):
        a=self.pages["core1b.html"]
        b=self.pages["core2b.html"]
        self.assertIn("two west and three south",a.lower())
        self.assertIn("two EAST and three SOUTH",a)
        self.assertIn("(−3,+5)",b)
        self.assertIn("rather than writing another pair",b)
        q=next(q for q in self.source["questions"] if q["id"].endswith("CORE2B-PAIR-TO-WORDS"))
        self.assertEqual(q["transfer"]["dimension"],"representation_translation")
        self.assertIn(QUESTION,q["transfer"]["builds_on"])
        self.assertEqual(q["answer"]["summary"],"Three units west and five units north.")

    def test_unchanged_owner_frozen_golden_is_not_rewritten(self):
        self.assertTrue((GOLDEN/"core1b.html").exists())
        self.assertNotEqual(self.pages["core1a.html"],(GOLDEN/"core1a.html").read_text(encoding="utf-8"))
        self.assertNotEqual(self.pages["core2a.html"],(GOLDEN/"core2a.html").read_text(encoding="utf-8"))

    def test_math_roundtrip_independent_cases(self):
        def encode(ew,ns):
            dx=(1 if ew[1]=="E" else -1)*ew[0]
            dy=(1 if ns[1]=="N" else -1)*ns[0]
            return dx,dy
        def decode(x,y):
            return ((abs(x),"E" if x>=0 else "W"),(abs(y),"N" if y>=0 else "S"))
        for x in range(-8,9):
            for y in range(-8,9):
                self.assertEqual(encode(*decode(x,y)),(x,y))
        self.assertEqual(encode((4,"E"),(2,"S")),(4,-2))
        self.assertEqual(decode(-3,5),((3,"W"),(5,"N")))

if __name__=="__main__": unittest.main()
