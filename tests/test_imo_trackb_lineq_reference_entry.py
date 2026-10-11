"""Research-only Track B LIN_EQ entry route: two variables != one variable."""
from __future__ import annotations

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE = "imo-linear-equations-two-variables"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


class TrackBLinearEquationsReferenceRoute(unittest.TestCase):
    def test_source_ids_and_browser_category_are_exact(self) -> None:
        data = json.loads((
            ROOT / "Mathematics/research/imo-g9-topic-browser.v1.json"
        ).read_text(encoding="utf-8"))
        source = {
            x["id"]: x for x in data["records"]
            if x["kind"] == "SOF_SOURCE_REFERENCE_ONLY"
            and x["topic_id"] == "LIN_EQ"
        }
        self.assertEqual(len(source), 7)
        self.assertTrue(all(
            not x["discrepancy_case"] and not x["core2_admitted"]
            for x in source.values()
        ))
        for mirror in ("public", "docs"):
            with self.subTest(mirror=mirror):
                path = ROOT / mirror / "mathematics" / PAGE / "index.html"
                page = path.read_text(encoding="utf-8")
                links = Links()
                links.feed(page)
                direct = [
                    x for x in links.hrefs
                    if x.startswith("../imo-grade9/index.html#SOF-IMO-")
                ]
                self.assertEqual(len(direct), 7)
                self.assertEqual(
                    set(direct),
                    {"../imo-grade9/index.html#" + x for x in source},
                )
                browser_path = ROOT / mirror / "mathematics/imo-grade9/index.html"
                browser = browser_path.read_text(encoding="utf-8")
                anchor = 'id="topic-lin_eq" data-topic="LIN_EQ"'
                self.assertIn(anchor, browser)
                section = browser.split(anchor, 1)[1].split("</section>", 1)[0]
                for href in direct:
                    source_id = urlsplit(href).fragment
                    self.assertIn(
                        f'id="{source_id}" data-kind="source"',
                        section,
                    )
                    target = (path.parent / urlsplit(href).path).resolve()
                    self.assertEqual(target, browser_path.resolve())
                self.assertIn(
                    "../imo-grade9/index.html#topic-lin_eq",
                    links.hrefs,
                )
                self.assertIn("question text and answers are not reproduced", page.casefold())
                self.assertIn("not verified or admitted canonical Core2", page)

    def test_topic_boundary_and_hub_route(self) -> None:
        for mirror in ("public", "docs"):
            with self.subTest(mirror=mirror):
                base = ROOT / mirror / "mathematics"
                page = (base / PAGE / "index.html").read_text(encoding="utf-8")
                one_variable = (base / "linear-equations/index.html").read_text(
                    encoding="utf-8"
                )
                self.assertIn("Linear Equations in Two Variables", page)
                self.assertIn("Linear Equations in One Variable", one_variable)
                self.assertNotIn("source-paper question-position references", one_variable)
                hub = (base / "index.html").read_text(encoding="utf-8")
                links = Links()
                links.feed(hub)
                href = PAGE + "/index.html"
                self.assertEqual(links.hrefs.count(href), 1)
                self.assertEqual((base / href).resolve(), (base / PAGE / "index.html").resolve())

    def test_docs_and_public_bytes_match(self) -> None:
        for path in (PAGE + "/index.html", "index.html"):
            with self.subTest(path=path):
                self.assertEqual(
                    (ROOT / "public/mathematics" / path).read_bytes(),
                    (ROOT / "docs/mathematics" / path).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
