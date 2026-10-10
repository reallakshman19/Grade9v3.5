"""IMO F04 release-aware navigation is fail-closed against forged UI and receipts."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from Shared.tools import imo_subtopic_route_guard as guard

ROOT = Path(__file__).resolve().parents[1]


class IMOReleaseRouteGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "public" / guard.PAGE).read_text(encoding="utf-8")
        cls.pilot = json.loads((ROOT / guard.PILOT).read_text(encoding="utf-8"))

    def check(self, text=None, pilot=None, repo=None):
        return guard.findings(repo or ROOT, pilot or self.pilot, text or self.html)

    def test_real_held_route_is_consistent_with_research_pilot(self):
        self.assertEqual(self.check(), [])

    def test_forged_launch_flag_fails(self):
        wrong = self.html.replace('data-g9-launch-authorized="false"',
                                  'data-g9-launch-authorized="true"', 1)
        self.assertTrue(self.check(text=wrong))

    def test_held_role_hidden_anchor_fails(self):
        wrong = self.html.replace("<h3>Core 1A · Learn the concept</h3>",
                                  '<h3>Core 1A · Learn the concept</h3><a href="CORE1A.html">Study</a>')
        self.assertIn("CORE1A: held role contains an interactive product action", self.check(text=wrong))

    def test_fake_release_label_fails_even_if_held(self):
        wrong = self.html.replace('data-g9-authority="CANDIDATE_NOT_PUBLISHED"',
                                  'data-g9-authority="RELEASED"', 1)
        self.assertIn("CORE1A: held authority label is incorrect", self.check(text=wrong))

    def test_direct_test_candidate_link_outside_role_fails(self):
        wrong = self.html.replace("</main>", '<a href="../../../test/imo-grade9/core1a.html">Launch test</a></main>')
        self.assertIn("unprotected Core product/TEST link outside a role card", self.check(text=wrong))

    def test_duplicate_role_fails(self):
        wrong = self.html.replace('data-g9-role="CORE2A"', 'data-g9-role="CORE1A"')
        self.assertIn("duplicate, unsupported or missing role", self.check(text=wrong))

    def test_pilot_flag_cannot_self_authorize_without_receipt(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["scope"]["launch_authorized"] = True
        pilot["routing"]["core1a_product_url"] = "/mathematics/number-systems/index-laws/CORE1A.html"
        wrong = self.html.replace('data-g9-role="CORE1A" data-g9-authority="CANDIDATE_NOT_PUBLISHED" data-g9-launch-authorized="false"',
                                  'data-g9-role="CORE1A" data-g9-authority="RELEASED" data-g9-launch-authorized="true"')
        wrong = wrong.replace("<h3>Core 1A · Learn the concept</h3>",
                              '<h3>Core 1A · Learn the concept</h3><a href="CORE1A.html">Study</a>')
        self.assertTrue(any("no safe committed release receipt" in x for x in self.check(text=wrong, pilot=pilot)))

    def test_invalid_receipt_path_and_cross_site_targets(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["scope"]["launch_authorized"] = True
        pilot["routing"]["core1a_product_url"] = "/mathematics/number-systems/index-laws/CORE1A.html"
        wrong = self.html.replace('data-g9-role="CORE1A" data-g9-authority="CANDIDATE_NOT_PUBLISHED" data-g9-launch-authorized="false"',
                                  'data-g9-role="CORE1A" data-g9-authority="RELEASED" data-g9-launch-authorized="true" data-g9-release-receipt="../../secret.json"')
        wrong = wrong.replace("<h3>Core 1A · Learn the concept</h3>",
                              '<h3>Core 1A · Learn the concept</h3><a href="CORE1A.html">Study</a>')
        self.assertTrue(any("no safe committed release receipt" in x for x in self.check(text=wrong, pilot=pilot)))
        self.assertIsNone(guard._safe_target("https://bad.example/CORE1A.html"))
        self.assertIsNone(guard._safe_target("../../../../test/imo-grade9/core1a.html"))
        self.assertIsNone(guard._safe_target("CORE1A.html?unsafe=1"))

    def test_current_receipt_must_match_role_and_exact_published_bytes(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["scope"]["launch_authorized"] = True
        target = "/mathematics/number-systems/index-laws/CORE1A.html"
        pilot["routing"]["core1a_product_url"] = target
        wrong = self.html.replace('data-g9-role="CORE1A" data-g9-authority="CANDIDATE_NOT_PUBLISHED" data-g9-launch-authorized="false"',
                                  'data-g9-role="CORE1A" data-g9-authority="RELEASED" data-g9-launch-authorized="true" data-g9-release-receipt="Releases/receipts/REL-TEST.json"')
        wrong = wrong.replace("<h3>Core 1A · Learn the concept</h3>",
                              '<h3>Core 1A · Learn the concept</h3><a href="CORE1A.html">Study</a>')
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            receipt_file = repo / "Releases/receipts/REL-TEST.json"
            receipt_file.parent.mkdir(parents=True)
            release = {
                "subject": "Mathematics", "plan": {"products": ["CORE1A"]},
                "validation": {"state": "RELEASED"},
                "publication": {
                    "path": "Mathematics/content/demo/publication",
                    "learner_visible_files": [{"path": "CORE1A.html"}]
                }, "source_receipt": None
            }
            receipt_file.write_text(json.dumps(release))
            pub = repo / "Mathematics/content/demo/publication/CORE1A.html"
            pub.parent.mkdir(parents=True)
            pub.write_bytes(b"<main>approved fixture</main>")
            page = repo / "public" / target.lstrip("/")
            page.parent.mkdir(parents=True)
            page.write_bytes(pub.read_bytes())
            mirror = repo / "docs" / target.lstrip("/")
            mirror.parent.mkdir(parents=True)
            mirror.write_bytes(pub.read_bytes())

            with patch.object(guard.release_authority, "verify_receipt",
                              return_value={"verified": False, "findings": []}):
                self.assertTrue(any("not current/verified" in x for x in self.check(wrong, pilot, repo)))
            with patch.object(guard.release_authority, "verify_receipt",
                              return_value={"verified": True, "findings": []}):
                self.assertEqual(self.check(wrong, pilot, repo), [])
                page.write_bytes(b"<main>tampered bytes</main>")
                self.assertTrue(any("differs from approved publication bytes" in x
                                    for x in self.check(wrong, pilot, repo)))

    def test_core2_cannot_launch_with_custody_hold_even_if_receipt_is_mocked(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["scope"]["launch_authorized"] = True
        pilot["scope"]["source_core2_admitted"] = 1
        pilot["routing"]["core2_source_product_url"] = "/mathematics/number-systems/index-laws/CORE2.html"
        # Even a forged accepted research crosswalk plus a mocked receipt
        # cannot replace the independent source-custody ledger.
        pilot["source_questions"][0]["source_core2_admitted"] = True
        pilot["source_questions"][0]["source_core2_eligible"] = True
        pilot["source_questions"][0]["rights_status"] = "RIGHTS_CLEARED"
        question_id = pilot["source_questions"][0]["question_id"]
        wrong = self.html.replace('data-g9-role="CORE2" data-g9-authority="SOURCE_CUSTODY_AND_RIGHTS_HOLD" data-g9-launch-authorized="false"',
                                  'data-g9-role="CORE2" data-g9-authority="RELEASED" data-g9-launch-authorized="true" data-g9-release-receipt="Releases/receipts/REL-TEST.json" data-g9-source-question-id="' + question_id + '"')
        wrong = wrong.replace("<h3>Core 2 · Authentic source question</h3>",
                              '<h3>Core 2 · Authentic source question</h3><a href="CORE2.html">Attempt</a>')
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            receipt_file = repo / "Releases/receipts/REL-TEST.json"
            receipt_file.parent.mkdir(parents=True)
            receipt_file.write_text(json.dumps({
                "subject": "Mathematics", "plan": {"products": ["CORE2"]},
                "validation": {"state": "RELEASED"},
                "publication": {
                    "path": "Mathematics/content/demo/publication",
                    "learner_visible_files": [{"path": "CORE2.html"}]},
                "source_receipt": {"receipt_id": "fake"}
            }))
            pub = repo / "Mathematics/content/demo/publication/CORE2.html"
            pub.parent.mkdir(parents=True)
            pub.write_bytes(b"<main>mock</main>")
            for folder in ("public", "docs"):
                p = repo / folder / "mathematics/number-systems/index-laws/CORE2.html"
                p.parent.mkdir(parents=True)
                p.write_bytes(pub.read_bytes())
            with patch.object(guard.release_authority, "verify_receipt",
                              return_value={"verified": True, "findings": []}):
                self.assertTrue(any("source identity" in x for x in self.check(wrong, pilot, repo)))


if __name__ == "__main__":
    unittest.main()
