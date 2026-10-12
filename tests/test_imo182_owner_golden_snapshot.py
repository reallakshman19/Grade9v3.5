#!/usr/bin/env python3
"""Owner-designated five-Core exact HTML golden byte lock (issue #182).

Golden snapshots freeze the already-previewed TEST PAGES bytes. The fixture's
regenerable manifest references a pinned authoring excerpt at another path, so
the authority digest changes, but learner HTML otherwise must be identical.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from Shared.tools import render_core

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "golden/units/G-IMO-G9-FIVE-CORE-20261012"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def without_authority_digest(html: str, digest: str) -> str:
    assert re.fullmatch(r"[0-9a-f]{16}", digest)
    # Remove only the documented exact 16-character authority identity, never
    # a mathematical expression or an authored content span.
    assert f'data-g9-render-digest="{digest}"' in html
    assert f'content="render_core/2 {digest}"' in html
    return (html
            .replace(f'data-g9-render-digest="{digest}"',
                     'data-g9-render-digest="[manifest-specific]"')
            .replace(f'content="render_core/2 {digest}"',
                     'content="render_core/2 [manifest-specific]"'))


class OwnerGoldenFiveCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = _json(ROOT / "snapshot-lock.json")
        cls.manifest = _json(ROOT / "manifest.json")

    def test_owner_scope_is_exactly_five_authored_test_cores(self):
        self.assertEqual(self.lock["status"], "OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT")
        self.assertEqual(self.lock["source_commit"],
                         "f87d2f627e3f05476d39fb04d7f26e453661dc68")
        self.assertEqual(self.lock["qrt_accepted"], "0/28")
        self.assertEqual(self.manifest["subject"], "TEST")
        self.assertEqual(self.manifest["output_roles"],
                         ["CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"])
        self.assertEqual(self.manifest["selection"]["core2"], [])
        self.assertEqual(self.manifest["bank_refs"], [])
        self.assertEqual(self.manifest["package_refs"],
                         ["golden/units/G-IMO-G9-FIVE-CORE-20261012/records.json"])
        self.assertEqual(len(self.lock["snapshots"]), 5)

    def test_exact_20261012_frozen_html_sha256_lock(self):
        expected = {"CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"}
        actual = {item["role"] for item in self.lock["snapshots"]}
        self.assertEqual(actual, expected)
        for item in self.lock["snapshots"]:
            with self.subTest(role=item["role"]):
                path = ROOT / item["path"]
                self.assertTrue(path.is_file())
                data = path.read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
                self.assertTrue(data.startswith(b"<!doctype html>\n"))
                self.assertTrue(data.rstrip().endswith(b"</html>"))
                self.assertIn(f'data-g9-role="{item["role"]}"'.encode(), data)
                self.assertIn(self.lock["original_digest"].encode(), data)

    def test_regenerated_pinned_golden_preserves_exact_role_html_semantics(self):
        pages, gaps, digest, _, _ = render_core.build_report(
            ROOT / "manifest.json", "PAGES", held_to="REFERENCE")
        self.assertFalse(gaps, gaps)
        self.assertEqual(set(pages),
                         {"core1.html", "core1a.html", "core1b.html",
                          "core2a.html", "core2b.html", "index.html"})
        for item in self.lock["snapshots"]:
            with self.subTest(role=item["role"]):
                stored=(ROOT / item["path"]).read_text(encoding="utf-8")
                name=item["role"].lower()+".html"
                self.assertEqual(
                    without_authority_digest(pages[name], digest),
                    without_authority_digest(stored, self.lock["original_digest"]))


if __name__ == "__main__":
    unittest.main()
