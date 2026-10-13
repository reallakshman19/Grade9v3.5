"""Held Index Laws subtopic route is a staged status view, not a product release."""
from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from Shared.tools import build_pages_site

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "TEST/imo-research/intake/imo-index-laws-route-staging.v1.json"
TOPIC = "mathematics/number-systems/index.html"
SUB = "mathematics/number-systems/index-laws/index.html"
HUB = "mathematics/index.html"
IMO = "mathematics/imo-grade9/index.html"
ROUTES = (HUB, IMO, TOPIC, SUB)


def source(relative: str) -> str:
    return (ROOT / "public" / relative).read_text(encoding="utf-8")


def target(relative: str) -> str:
    return (ROOT / "docs" / relative).read_text(encoding="utf-8")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in {"a", "link", "script"}:
            value = dict(attrs).get("href") or dict(attrs).get("src")
            if value is not None:
                self.links.append((tag, value))


class IndexLawsStage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = json.loads(STATE.read_text(encoding="utf-8"))

    def test_owner_staging_not_broad_academic_or_release_waiver(self):
        state = self.state
        self.assertEqual(state["status"], "DRAFT_NAVIGATION_STAGED_ACADEMIC_HOLD")
        self.assertEqual(state["user_permission"]["scope"], "STAGING_ON_DRAFT_BRANCH_ONLY")
        self.assertTrue(state["user_permission"]["does_not_replace_independent_academic_signoff"])
        self.assertFalse(state["release"]["owner_channel_authorized"])
        self.assertFalse(state["release"]["merged"])
        self.assertFalse(state["release"]["live_deployed"])
        self.assertEqual(state["subtopic_academic_status"], "PROVISIONAL_FROM_ATTACHMENT")
        self.assertIsNone(state["core1a"]["public_product_url"])
        self.assertFalse(state["core1a"]["canonical_accepted"])

    def test_product_roles_are_all_held_and_never_source_relabelled(self):
        self.assertEqual(self.state["core2"]["admitted"], 0)
        self.assertEqual(self.state["core2"]["source_positions_held"], 68)
        self.assertIsNone(self.state["core2"]["public_product_url"])
        self.assertIsNone(self.state["core2a"]["public_product_url"])
        self.assertIn("TEST_CANDIDATE", self.state["core1a"]["status"])
        self.assertIn("SOURCE_CUSTODY_AND_RIGHTS_HOLD", self.state["core2"]["status"])
        self.assertIn('data-imo-core-action-state="ALL_HELD"', source(SUB))
        self.assertIn('data-imo-release="ACADEMIC_HOLD"', source(SUB))
        self.assertIn('data-imo-release="ACADEMIC_HOLD"', source(TOPIC))
        self.assertIn("Authentic SOF source", source(SUB))
        self.assertIn("not an original SOF exam question", source(SUB))

    def test_hub_and_imo_discover_only_staged_status_pages(self):
        self.assertIn('href="number-systems/index.html"', source(HUB))
        self.assertIn('href="../number-systems/index-laws/index.html"', source(IMO))
        self.assertIn('href="index-laws/index.html"', source(TOPIC))
        self.assertIn('href="../index.html"', source(SUB))
        self.assertIn('href="../../imo-grade9/index.html"', source(SUB))

    def test_new_staged_pages_contain_no_unapproved_core_or_test_url(self):
        for page in (TOPIC, SUB):
            with self.subTest(page=page):
                html = source(page)
                parser = Links()
                parser.feed(html)
                destinations = [v for tag, v in parser.links if tag == "a"]
                self.assertTrue(destinations)
                for link in destinations:
                    self.assertNotRegex(link, r"/test/|core1a\.html|core2a?\.html|\.pdf|source-paper")
                    self.assertNotIn("#", link)
                self.assertNotIn("2y=6", html)
                self.assertNotIn("y=3", html)
                self.assertNotIn("MODEL_RESPONSE", html)
                self.assertIn('<meta name="robots" content="noindex">', html)

    def test_all_new_page_local_links_resolve_to_checked_in_repo_files(self):
        for page in (TOPIC, SUB):
            doc = Links()
            doc.feed(source(page))
            for _, value in doc.links:
                u = urlsplit(value)
                if u.scheme or u.netloc or u.path == "":
                    continue
                candidate = (ROOT / "public" / page).parent / u.path
                self.assertTrue(candidate.resolve().is_relative_to((ROOT / "public").resolve()))
                self.assertTrue(candidate.is_file(), (page, value))

    def test_all_mirrors_are_exact_generator_projections(self):
        # Links and CSS in the staged pages are already project-relative,
        # so they do not need a GitHub Pages root rewrite.
        for page in ROUTES:
            with self.subTest(page=page):
                desired = build_pages_site._public_payload(
                    page, (ROOT / "public" / page).read_bytes())
                self.assertEqual((ROOT / "docs" / page).read_bytes(), desired)

    def test_manifest_contains_exactly_one_row_per_stage_page(self):
        manifest = json.loads((ROOT / "docs/.pages-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["generator"], "Shared/tools/build_pages_site.py")
        for page in (TOPIC, SUB):
            self.assertEqual([r for r in manifest["files"] if r["target"] == page],
                             [{"source": "public/" + page, "target": page}])
        rows = [r["target"] for r in manifest["files"]]
        self.assertEqual(rows, sorted(set(rows)))

    def test_published_roles_require_named_separate_decisions(self):
        gates = self.state["required_before_release"]
        self.assertTrue(any("Independent Grade 9" in g for g in gates))
        self.assertTrue(any("Owner" in g for g in gates))
        self.assertTrue(any("V3.1" in g for g in gates))
        self.assertTrue(any("generator parity" in g for g in gates))
        self.assertIn("Owner", source(SUB))
        self.assertNotIn('data-imo-release="RELEASED"', source(SUB))


if __name__ == "__main__":
    unittest.main()
