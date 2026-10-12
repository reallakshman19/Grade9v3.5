"""Issue #182 Owner decision D-182-2-H3: third authored hint is AFTER_ATTEMPT.

Tests actual governed Core2A HTML from the shared renderer; never edits the
Owner's frozen 2026-10-12 HTML golden or assigns QRT academic acceptance.
"""
from __future__ import annotations
import json
import re
import unittest
from pathlib import Path

from Shared.tools import core2_v2, render_core

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "TEST/imo-research/pilots/imo182-core2b-transfer-pilot.v1.json"
BASE = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
MANIFEST = ROOT / "TEST/products/imo-182-five-core-integrated-review.manifest.json"
FROZEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots"
QID = "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"
W = "MOVE-TEST-CORE2A-WARRANT"
H3 = "Do not assume one factor supplies every divisor."
DIGEST = re.compile(r"[a-f0-9]{16}")

def question(path):
    data=json.loads(path.read_text(encoding="utf-8"))
    return next(q for q in data["questions"] if q["id"]==QID)

class Core2AH3AfterAttempt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = question(PILOT)
        cls.original = question(BASE)
        cls.pages, cls.gaps, cls.digest, _, _ = render_core.build_report(MANIFEST, "PAGES", held_to="REFERENCE")
        cls.html = cls.pages["core2a.html"]

    def test_both_authored_records_identify_exact_same_protected_w_and_h3_policy(self):
        for q in (self.pilot, self.original):
            with self.subTest(qid=q["id"]):
                plan=q["extensions"]["grade9v3:core2_support_plan"]
                self.assertEqual(plan["protected_move_refs"], [W])
                self.assertEqual(plan["support_completions"], [{
                    "support_ref":"scaffolds[2]",
                    "completed_move_refs":[W],
                    "availability":"AFTER_ATTEMPT",
                }])
                self.assertEqual(len(q["hint_ladder"]),3)
                self.assertEqual(q["hint_ladder"][2]["from"],"scaffolds[2]")
                projection=core2_v2.project_support(q)
                self.assertEqual([r["availability"] for r in projection],
                                 ["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])

    def test_actual_core2a_next_hint_exposes_only_precommit_h1_and_h2(self):
        h=self.html
        ladder=h.split('data-g9-ladder-ref="CORE2A-',1)[1].split("</div>",1)[0]
        self.assertIn('data-g9-next-rung',ladder)
        self.assertIn('data-g9-rung-payload',ladder)
        self.assertNotIn(H3,ladder)
        self.assertNotIn('data-g9-rung="3"',ladder)
        self.assertIn('Keep m arbitrary.',ladder)

    def test_actual_h3_is_only_in_inert_attempt_gated_template(self):
        h=self.html
        self.assertEqual(h.count(H3),1)
        self.assertIn('data-g9-after-attempt-hint',h)
        self.assertIn('data-g9-hint-order="3"',h)
        self.assertRegex(h, r'<details[^>]+data-requires-attempt[^>]*>\s*<summary>Hint 3')
        self.assertRegex(h, r'<template data-g9-payload="CORE2A-'
                            +re.escape(QID)+r'-after-attempt-hint-3">')
        h3_pos=h.index(H3)
        tmpl=h.rfind('<template data-g9-payload=',0,h3_pos)
        self.assertGreater(tmpl,0)
        self.assertNotIn('</template>',h[tmpl:h3_pos])
        # A separately committed attempt still protects the full answer.
        self.assertIn('data-requires-attempt',h[h.find(H3):])
        self.assertIn('Reasoning route and full solution',h)

    def test_missing_or_lying_authored_release_plan_fails_closed(self):
        bad=json.loads(json.dumps(self.pilot))
        bad["extensions"]["grade9v3:core2_support_plan"]["support_completions"][0]["support_ref"]="scaffolds[99]"
        with self.assertRaises(core2_v2.Core2SupportProjectionError):
            core2_v2.project_support(bad)
        bad=json.loads(json.dumps(self.pilot))
        bad["extensions"]["grade9v3:core2_support_plan"]["support_completions"][0]["availability"]="PRE_ATTEMPT_SAFE"
        with self.assertRaises(core2_v2.Core2SupportProjectionError):
            core2_v2.project_support(bad)

    def test_entire_five_role_baseline_keeps_existing_blueprints_and_no_depth_gaps(self):
        self.assertFalse(self.gaps,self.gaps)
        self.assertEqual(set(self.pages),{"core1.html","core1a.html","core1b.html",
                                         "core2a.html","core2b.html","index.html"})
        for role,expected in {
            "core1":"BP-CORE1-ORIENTATION@1.1.0",
            "core1a":"BP-CORE1A-CONSTRUCTION@1.8.0",
            "core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0",
            "core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
            "core2b":"BP-CORE2B-TRANSFER@1.1.0",
        }.items():
            with self.subTest(role=role):
                self.assertIn('data-blueprint-ref="'+expected+'"',self.pages[role+".html"])
        self.assertNotIn("core2.html", self.pages)

    def test_owner_frozen_golden_remains_unchanged_and_new_h3_needs_successor_review(self):
        # The old frozen HTML remains untouched, including its old 3-rung ladder.
        frozen=(FROZEN/"core2a.html").read_text(encoding="utf-8")
        self.assertIn(H3,frozen)
        self.assertNotIn('data-g9-after-attempt-hint',frozen)
        self.assertIn('data-g9-after-attempt-hint',self.html)
        self.assertNotEqual(frozen,self.html)
        self.assertEqual(self.html.count('data-g9-after-attempt-hint'),1)
        self.assertIn('data-g9-render-digest',self.html)

if __name__ == "__main__":
    unittest.main()
