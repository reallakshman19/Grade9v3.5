"""Scoped Track B source-reference navigation checks, without copied SOF questions."""
from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE_LINK = "../imo-grade9/index.html#topic-coord"
TARGET_TOPIC = "topic-coord"


class AnchorLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str | None, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            attributes = dict(attrs)
            self.links.append((attributes.get("href"), attributes.get("aria-label")))


class TrackBSourceReferenceEntryTests(unittest.TestCase):
    def test_coordinate_page_routes_to_real_imo_topic_for_each_mirror(self) -> None:
        for mirror in ("public", "docs"):
            with self.subTest(mirror=mirror):
                workspace = ROOT / mirror / "mathematics" / "coordinate-geometry" / "index.html"
                text = workspace.read_text(encoding="utf-8")
                parser = AnchorLinks()
                parser.feed(text)
                matches = [(href, label) for href, label in parser.links if href == SOURCE_LINK]
                self.assertEqual(len(matches), 1, "one explicit source-reference route")
                self.assertIn("source-paper references", matches[0][1] or "")

                ref = urlsplit(matches[0][0])
                target = (workspace.parent / ref.path).resolve()
                expected = ROOT / mirror / "mathematics" / "imo-grade9" / "index.html"
                self.assertEqual(target, expected.resolve())
                html = target.read_text(encoding="utf-8")
                self.assertEqual(ref.fragment, TARGET_TOPIC)
                self.assertIn('id="topic-coord"', html)
                self.assertIn('data-topic="COORD"', html)
                self.assertEqual(html.count('data-kind="source"'), 68)
                self.assertEqual(html.count('data-kind="authored"'), 7)
                self.assertIn("not reproduced", html)
                self.assertIn("not official SOF questions", html)

    def test_coordinate_page_mirrors_remain_byte_identical(self) -> None:
        public = ROOT / "public" / "mathematics" / "coordinate-geometry" / "index.html"
        docs = ROOT / "docs" / "mathematics" / "coordinate-geometry" / "index.html"
        self.assertEqual(public.read_bytes(), docs.read_bytes())


if __name__ == "__main__":
    unittest.main()
