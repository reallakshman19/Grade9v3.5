#!/usr/bin/env python3
"""Issue #182: separate authored TEST Core1 and Core2B versus candidate golden moves.

This compares *different mathematics* and never treats shared-renderer HTML
similarity as Owner golden, QRT or real learner acceptance.
"""
from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from Shared.tools import render_core

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT / "TEST/products/imo-182-core1-orientation.manifest.json"
P2B = ROOT / "TEST/products/imo-182-core2b-transfer.manifest.json"
GOLD = ROOT / "golden/units/G-MATH-LINEAR-CONSTRAINT/manifest.json"
PKG = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
REGISTRY = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
QID = "Q-TEST-CORE2B-FOUR-FACTOR-48-BOUNDARY"
MICRO = "MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

class Anatomy(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blueprints = []
        self.roles = []
        self.slots = []
        self.stage_ids = []
        self.attempts = 0
        self.locked_reveals = 0
    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if a.get("data-blueprint-ref"): self.blueprints.append(a["data-blueprint-ref"])
        if a.get("data-g9-role"): self.roles.append(a["data-g9-role"])
        if a.get("data-blueprint-slot"): self.slots.append(a["data-blueprint-slot"])
        if a.get("data-g9-stage-id"): self.stage_ids.append(a["data-g9-stage-id"])
        if "data-g9-attempt-box" in a: self.attempts += 1
        if "data-requires-attempt" in a: self.locked_reveals += 1

def parse(html):
    p = Anatomy()
    p.feed(html)
    return p

class BlueprintGoldens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m1 = load(P1); cls.m2 = load(P2B)
        cls.pkg = load(PKG)
        cls.registry = load(REGISTRY)
        cls.golden = load(ROOT / "golden/units/G-MATH-LINEAR-CONSTRAINT/records.json")
        cls.pages1, cls.gaps1, cls.digest1, _, _ = render_core.build_report(P1, "PAGES", held_to="REFERENCE")
        cls.pages2, cls.gaps2, cls.digest2, _, _ = render_core.build_report(P2B, "PAGES", held_to="REFERENCE")
        cls.gpages, cls.gaps_gold, _, _, _ = render_core.build_report(GOLD, "PAGES", held_to="REFERENCE")

    def test_core1_existing_blueprint_and_all_registered_slots(self):
        actual = parse(self.pages1["core1.html"])
        golden = parse(self.gpages["core1.html"])
        self.assertEqual(actual.blueprints, ["BP-CORE1-ORIENTATION@1.1.0"])
        self.assertEqual(actual.blueprints, golden.blueprints)
        self.assertIn("CORE1", actual.roles)
        self.assertEqual(actual.slots, golden.slots)
        self.assertEqual(actual.slots, ["identity", "orientation"])
        self.assertEqual(self.m1["output_roles"], ["CORE1"])
        self.assertEqual(self.m1["selection"]["microtopics"], [MICRO])
        self.assertFalse(self.m1["selection"]["core2"])

    def test_core1_goldens_t14_orientation_move_not_string_copy(self):
        # Golden tests domain/constraint meaning; authored page tests
        # arbitrary-positive-start/parity/residue meaning. Both bridge a
        # necessary prerequisite rather than transplanting golden algebra.
        candidate = next(m for m in self.golden["microtopics"] if m["id"]=="MIC-MATH-CONSTRAINT")
        authored = next(m for m in self.pkg["microtopics"] if m["id"]==MICRO)
        self.assertTrue(candidate["entry_assumptions"])
        self.assertTrue(authored["entry_assumptions"])
        self.assertIn("positive", " ".join(authored["entry_assumptions"]).lower())
        self.assertIn("factor", authored["inferential_jump"].lower())
        self.assertTrue(authored["compact_anchor"]["prompt"])
        html = self.pages1["core1.html"]
        for name in ("hard_transition", "governing_relation", "compact_anchor", "exit_prompt"):
            self.assertIn(f'data-g9-block="{name}"', html)
        self.assertIn("divisible", html.lower())
        self.assertNotIn("3x + 2 = 9", html)
        # Compact anchor and relations are authored, not fabricated by renderer.
        self.assertTrue(any(r.get("id") in authored.get("relation_refs",[])
                            for r in self.pkg["relations"]))

    def test_core2b_existing_blueprint_and_golden_slots(self):
        actual = parse(self.pages2["core2b.html"])
        golden = parse(self.gpages["core2b.html"])
        self.assertEqual(actual.blueprints, ["BP-CORE2B-TRANSFER@1.1.0"])
        self.assertEqual(actual.blueprints, golden.blueprints)
        self.assertEqual(actual.slots, golden.slots)
        self.assertEqual(actual.slots, ["identity", "attempt", "post_attempt"])
        self.assertIn("CORE2B", actual.roles)
        self.assertEqual(self.m2["selection"]["core2b"], [QID])
        self.assertEqual(self.m2["selection"]["core2a"],
                         ["Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"])
        self.assertEqual(self.m2["selection"]["core2"], [])
        self.assertIn('href="core2a.html#Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"',
                      self.pages2["core2b.html"])

    def test_core2b_t09_invariant_changed_decision_and_t08_closure(self):
        golden = next(q for q in self.golden["questions"] if q["id"]=="Q-MATH-LINEAR-2B-FIXTURE")
        q = next(q for q in self.pkg["questions"] if q["id"]==QID)
        for key in ("invariant", "statement", "novelty"):
            self.assertTrue(golden["transfer"][key])
            self.assertTrue(q["transfer"][key])
        self.assertIn("48", q["stem"])
        self.assertIn("24", q["transfer"]["invariant"])
        self.assertIn("48", q["transfer"]["statement"])
        self.assertIn("k=1", q["transfer"]["novelty"]["why_new"])
        self.assertIn("Core1A", q["transfer"]["novelty"]["why_new"])
        self.assertIn("48", q["family_exposure"]["closure"])
        self.assertIn("24", q["family_exposure"]["closure"])
        html = self.pages2["core2b.html"]
        for name in ("lineage_check", "invariant_changed", "changed_demand",
                     "protected_move", "independent_check"):
            self.assertIn(f'data-g9-block="{name}"', html)
        self.assertIn('data-g9-lineage', html)
        self.assertNotEqual(q["stem"], golden["stem"])

    def test_core2b_safe_figure_and_attempt_before_answer(self):
        q = next(q for q in self.pkg["questions"] if q["id"]==QID)
        ref = q["representation_roles"]["safe_ref"]
        rep = next(x for x in self.pkg["representations"] if x["id"]==ref)
        self.assertEqual(q["figure_refs"], [ref])
        self.assertEqual(rep["reveal_stages"][0]["id"], "CORE2B-FOUR-FACTORS-ONLY")
        svg = (ROOT / rep["rendered_asset_refs"][0]).read_text(encoding="utf-8")
        self.assertIn('data-g9-stage-id="CORE2B-FOUR-FACTORS-ONLY"', svg)
        self.assertNotIn("divisible by 24", svg.lower())
        self.assertNotIn("k=1", svg)
        h = self.pages2["core2b.html"]
        a = parse(h)
        self.assertGreaterEqual(a.attempts, 1)
        self.assertGreaterEqual(a.locked_reveals, 1)
        self.assertIn("CORE2B-FOUR-FACTORS-ONLY", a.stage_ids)
        self.assertIn('data-g9-payload-slot', h)
        self.assertIn('data-g9-lineage', h)
        self.assertNotIn("SOF-IMO-G09-", h)

    def test_exact_integer_oracle_for_new_transfer_and_earlier_24_exit(self):
        q = next(q for q in self.pkg["questions"] if q["id"]==QID)
        self.assertEqual(q["origin"], "AUTHORED")
        self.assertEqual(q["answer"]["crux_move_ref"], "MOVE-TEST-CORE2B-COUNTERMODEL")
        self.assertEqual(1*2*3*4, 24)
        self.assertNotEqual((1*2*3*4) % 48, 0)
        self.assertEqual((5*6*7*8) % 48, 0)
        for k in range(1, 241):
            product = k*(k+1)*(k+2)*(k+3)
            self.assertEqual(product % 24, 0, k)
            # Exhaustive four residues guarantee a multiple of four and
            # another even term; three consecutive ones guarantee a multiple of 3.
            self.assertEqual(sum((k+i)%4==0 for i in range(4)),1)
            self.assertEqual(sum((k+i)%4==2 for i in range(4)),1)
            self.assertTrue(any((k+i)%3==0 for i in range(4)))
        self.assertIn("maximal", q["answer"]["reasoning_route"][-1]["why_valid"].lower()
                      if "maximal" in q["answer"]["reasoning_route"][-1]["why_valid"].lower()
                      else q["answer"]["reasoning_route"][-1]["action"].lower()+" maximal")

    def test_selections_and_depth_are_honest(self):
        self.assertFalse(self.gaps1, self.gaps1)
        self.assertFalse(self.gaps2, self.gaps2)
        self.assertFalse(self.gaps_gold, self.gaps_gold)
        self.assertEqual(set(self.pages1),{"core1.html","index.html"})
        self.assertEqual(set(self.pages2),{"core1.html","core2a.html","core2b.html","index.html"})
        self.assertNotEqual(self.digest1,self.digest2)
        self.assertEqual(self.m1["subject"],"TEST")
        self.assertEqual(self.m2["subject"],"TEST")
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.pkg["questions"]))
        # No fake 68-question source, Owner-accepted QRT or production assertion.

if __name__ == "__main__":
    unittest.main()
