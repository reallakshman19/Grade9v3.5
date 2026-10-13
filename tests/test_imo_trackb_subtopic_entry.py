"""Scoped Track B source-reference navigation tests; original SOF text is not copied."""
from __future__ import annotations

import json
import re
import unittest
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
# These routes expose the already existing research browser, not canonical Core2.
TOPICS = (
    ("coordinate-geometry", "topic-coord", "COORD"),
    ("polynomials", "topic-poly", "POLY"),
    ("euclids-geometry", "topic-euclid", "EUCLID"),
)


class AnchorLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str | None, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            fields = dict(attrs)
            self.links.append((fields.get("href"), fields.get("aria-label")))


class TrackBSourceReferenceEntryTests(unittest.TestCase):
    def test_mathematics_topics_route_to_existing_imo_source_references(self) -> None:
        for mirror in ("public", "docs"):
            for workspace_name, anchor, category in TOPICS:
                with self.subTest(mirror=mirror, topic=workspace_name):
                    workspace = ROOT / mirror / "mathematics" / workspace_name / "index.html"
                    parser = AnchorLinks()
                    parser.feed(workspace.read_text(encoding="utf-8"))
                    route = f"../imo-grade9/index.html#{anchor}"
                    matches = [(href, label) for href, label in parser.links if href == route]
                    self.assertEqual(len(matches), 1, "exactly one source-reference link")
                    self.assertIn("source-paper references", matches[0][1] or "")

                    parts = urlsplit(matches[0][0])
                    target = (workspace.parent / parts.path).resolve()
                    expected = ROOT / mirror / "mathematics" / "imo-grade9" / "index.html"
                    self.assertEqual(target, expected.resolve())
                    self.assertEqual(parts.fragment, anchor)
                    html = target.read_text(encoding="utf-8")
                    marker = f'id="{anchor}" data-topic="{category}"'
                    self.assertIn(marker, html, "a real matched research-topic section")
                    group = html.split(marker, 1)[1].split("</section>", 1)[0]
                    self.assertIn('data-kind="source"', group, "topic has source references")
                    self.assertEqual(html.count('data-kind="source"'), 68)
                    self.assertEqual(html.count('data-kind="authored"'), 7)
                    self.assertIn("not reproduced", html)
                    self.assertIn("not official SOF questions", html)

    def test_subtopic_pages_list_only_grounded_original_paper_positions(self) -> None:
        positions = {
            "coordinate-geometry": (
                "SOF-IMO-G09-L1-2023-24-A-Q027",
                "SOF-IMO-G09-L1-2023-24-A-Q050",
                "SOF-IMO-G09-L1-2024-25-B-Q020",
                "SOF-IMO-G09-L1-2025-26-A-Q046",
            ),
            "polynomials": (
                "SOF-IMO-G09-L1-2023-24-A-Q028",
                "SOF-IMO-G09-L1-2025-26-A-Q045",
                "SOF-IMO-G09-SAMPLE-2026-27-Q007",
            ),
            "euclids-geometry": (
                "SOF-IMO-G09-L1-2023-24-A-Q033",
                "SOF-IMO-G09-L1-2024-25-B-Q031",
                "SOF-IMO-G09-SAMPLE-2026-27-Q006",
            ),
        }
        for mirror in ("public", "docs"):
            browser = (
                ROOT / mirror / "mathematics" / "imo-grade9" / "index.html"
            ).read_text(encoding="utf-8")
            for workspace_name, topic_anchor, category in TOPICS:
                with self.subTest(mirror=mirror, topic=workspace_name):
                    workspace = ROOT / mirror / "mathematics" / workspace_name / "index.html"
                    page = workspace.read_text(encoding="utf-8")
                    self.assertIn("question text and answers are not reproduced", page)
                    parser = AnchorLinks()
                    parser.feed(page)
                    item_links = [
                        href for href, _ in parser.links
                        if href and href.startswith("../imo-grade9/index.html#SOF-IMO-")
                    ]
                    expected = {
                        "../imo-grade9/index.html#" + item
                        for item in positions[workspace_name]
                    }
                    self.assertEqual(set(item_links), expected)
                    self.assertEqual(len(item_links), len(expected))
                    marker = f'id="{topic_anchor}" data-topic="{category}"'
                    group = browser.split(marker, 1)[1].split("</section>", 1)[0]
                    for source_id in positions[workspace_name]:
                        self.assertIn(
                            f'id="{source_id}" data-kind="source"', group,
                            "no fabricated or cross-topic question identifier"
                        )

    def test_topic_document_urls_match_frozen_research_references(self) -> None:
        """Prevent a real question ID from silently pointing to the wrong paper."""
        source_index = json.loads((
            ROOT / "Mathematics" / "research" / "imo-g9-topic-browser.v1.json"
        ).read_text(encoding="utf-8"))
        records = {
            item["id"]: item
            for item in source_index["records"]
            if item["kind"] == "SOF_SOURCE_REFERENCE_ONLY"
        }
        for mirror in ("public", "docs"):
            browser = (
                ROOT / mirror / "mathematics" / "imo-grade9" / "index.html"
            ).read_text(encoding="utf-8")
            for workspace_name, topic_anchor, category in TOPICS:
                with self.subTest(mirror=mirror, topic=workspace_name):
                    marker = f'id="{topic_anchor}" data-topic="{category}"'
                    self.assertIn(marker, browser)
                    group = browser.split(marker, 1)[1].split("</section>", 1)[0]
                    source_ids = re.findall(
                        r'<li class="imo-item imo-source" id="([^"]+)"',
                        group,
                    )
                    self.assertGreater(len(source_ids), 0)
                    self.assertEqual(
                        set(source_ids),
                        {id for id, item in records.items() if item["topic_id"] == category},
                    )
                    for id in source_ids:
                        card = group.split(
                            f'id="{id}" data-kind="source"', 1
                        )[1].split("</li>", 1)[0]
                        links = re.findall(r'<a href="([^"]+)"', card)
                        self.assertEqual(len(links), 1, id)
                        url = unescape(links[0])
                        self.assertEqual(url, records[id]["source_pdf_url"], id)
                        self.assertEqual(urlsplit(url).scheme, "https", id)
                        self.assertIn(
                            urlsplit(url).hostname,
                            {"iswkoman.com", "www.iswkoman.com", "sofworld.org"},
                            id,
                        )

    def test_each_topic_workspace_has_identical_public_and_docs_mirrors(self) -> None:
        for workspace_name, _, _ in TOPICS:
            with self.subTest(topic=workspace_name):
                public = ROOT / "public" / "mathematics" / workspace_name / "index.html"
                docs = ROOT / "docs" / "mathematics" / workspace_name / "index.html"
                self.assertEqual(public.read_bytes(), docs.read_bytes())


if __name__ == "__main__":
    unittest.main()
