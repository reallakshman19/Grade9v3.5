"""Scoped Track B source-reference navigation tests; original SOF text is not copied."""
from __future__ import annotations

import unittest
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

    def test_each_topic_workspace_has_identical_public_and_docs_mirrors(self) -> None:
        for workspace_name, _, _ in TOPICS:
            with self.subTest(topic=workspace_name):
                public = ROOT / "public" / "mathematics" / workspace_name / "index.html"
                docs = ROOT / "docs" / "mathematics" / workspace_name / "index.html"
                self.assertEqual(public.read_bytes(), docs.read_bytes())


if __name__ == "__main__":
    unittest.main()
