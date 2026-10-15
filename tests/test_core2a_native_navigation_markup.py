"""Core1A real renderer navigation must close each <ul> and its containing block.

Regression for Agent B's #268 review: two native practice lanes previously
emitted '</ul' without the final '>', which other CI checks did not catch.
The TEST-only source lane below uses a synthetic identifier for STRUCTURE
ONLY. It is not an authentic exam question, mastery evidence, or QRT signoff.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from Shared.tools import render_core


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "TEST/products/core1b-authored-reconstruction-journey.manifest.json"
AUTHORED_QID = "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"
SOURCE_NAV_STUB = "Q-TEST-NAV-STRUCTURE-ONLY"
NAV_BLOCKS = ("practice_navigation", "authored_practice_navigation")


class _StrictNavList(HTMLParser):
    """Track paired list and wrapper tags; HTMLParser alone tolerates broken HTML."""

    TAGS = {"div", "h4", "ul", "li", "a"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.closed: list[str] = []
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.TAGS:
            self.stack.append(tag)
        if tag == "a":
            self.links.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag not in self.TAGS:
            return
        if not self.stack or self.stack[-1] != tag:
            raise AssertionError(f"unbalanced native navigation: closing {tag}, stack={self.stack}")
        self.stack.pop()
        self.closed.append(tag)


def _native_nav_block(page: str, name: str) -> str:
    """Isolate the emitted named block, not a hand-crafted substitute."""
    opening = re.search(
        r'<div class="g9-block" data-g9-block="' + re.escape(name) + r'">',
        page,
    )
    if opening is None:
        raise AssertionError(f"real Core1A HTML missing {name}")
    end = page.find("</div>", opening.end())
    if end < 0:
        raise AssertionError(f"real Core1A HTML has no closing wrapper for {name}")
    return page[opening.start():end + len("</div>")]


def _parse_balanced_navigation(fragment: str) -> _StrictNavList:
    parser = _StrictNavList()
    parser.feed(fragment)
    parser.close()
    if parser.stack or parser.closed.count("ul") != 1 or parser.closed.count("div") != 1:
        raise AssertionError(
            f"native list/wrapper not closed: remaining={parser.stack}, closes={parser.closed}"
        )
    if not parser.links or "li" not in parser.closed:
        raise AssertionError("Core1A navigation lost its actual question link")
    return parser


class Core2ANativeNavigationMarkupTests(unittest.TestCase):
    def test_real_core1a_authored_practice_navigation_is_balanced(self):
        """Parse the sole registered renderer's actual TEST learner page."""
        pages, gaps, _digest = render_core.build(MANIFEST, "PAGES")
        self.assertEqual(gaps, [], gaps)
        page = pages["core1a.html"]
        fragment = _native_nav_block(page, "authored_practice_navigation")
        parsed = _parse_balanced_navigation(fragment)
        self.assertEqual(len(parsed.links), 1)
        link = parsed.links[0]
        self.assertEqual(link.get("data-g9-question-ref"), AUTHORED_QID)
        self.assertEqual(link.get("href"), "core2a.html#" + AUTHORED_QID)

    def test_source_and_authored_navigation_from_native_renderer_are_balanced(self):
        """Both generated lanes must balance, including source-only link path."""
        ctx = render_core.context(MANIFEST)
        concept = ctx.selection_rows["microtopics"][0]
        ctx.selection_rows["core2"] = [{
            "id": SOURCE_NAV_STUB,
            "original_identifier": "Navigation-markup stub (not exam material)",
        }]
        join = {
            "microtopic_to_questions": {concept["id"]: [SOURCE_NAV_STUB]},
            "question_to_microtopics": {SOURCE_NAV_STUB: [concept["id"]]},
        }
        with patch.object(render_core, "_concept_join", return_value=join):
            native = render_core._core1a_practice_navigation(ctx, concept)
        self.assertTrue(native, "real renderer returned no navigation")
        for name in NAV_BLOCKS:
            with self.subTest(block=name):
                fragment = _native_nav_block(native, name)
                parsed = _parse_balanced_navigation(fragment)
                self.assertEqual(len(parsed.links), 1)
                self.assertEqual(
                    parsed.links[0].get("href", "").split("#", 1)[0],
                    "core2.html" if name == "practice_navigation" else "core2a.html",
                )

    def test_old_missing_angle_bracket_is_caught_by_parser(self):
        """Negative control recreates precisely the bug from frozen b34137e."""
        pages, gaps, _digest = render_core.build(MANIFEST, "PAGES")
        self.assertEqual(gaps, [], gaps)
        clean = _native_nav_block(pages["core1a.html"], "authored_practice_navigation")
        self.assertIn("</ul></div>", clean)
        malformed = clean.replace("</ul></div>", "</ul</div>", 1)
        with self.assertRaises(AssertionError):
            _parse_balanced_navigation(malformed)


if __name__ == "__main__":
    unittest.main()
