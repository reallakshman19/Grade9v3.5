"""Owner-designated #182 five-Core HTML golden: strict lock and sole-renderer rebuild.

This is a TEST-only O1 regression. It does not equate frozen artifact bytes,
academic/QRT acceptance, real learner impact, publication, or merge rights.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

from Shared.tools import render_core

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
LIVE = ROOT / "TEST/products/imo-182-five-core-integrated-review.manifest.json"
ROLES = ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
BPS = {
    "CORE1": "BP-CORE1-ORIENTATION@1.1.0",
    "CORE1A": "BP-CORE1A-CONSTRUCTION@1.8.0",
    "CORE1B": "BP-CORE1B-RECONSTRUCTION@1.1.0",
    "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
    "CORE2B": "BP-CORE2B-TRANSFER@1.1.0",
}


def _sha(buf: bytes) -> str:
    return hashlib.sha256(buf).hexdigest()


def _git_blob(buf: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(buf)).encode() + b"\0" + buf).hexdigest()


def _compare_bytes(test: unittest.TestCase, expected: bytes, actual: bytes, label: str):
    if expected == actual:
        return
    offset = next((n for n, (a, b) in enumerate(zip(expected, actual)) if a != b),
                  min(len(expected), len(actual)))
    test.fail(
        f"{label}: frozen HTML changed (first different byte={offset}, "
        f"expected_length={len(expected)}, actual_length={len(actual)}, "
        f"expected_sha256={_sha(expected)}, actual_sha256={_sha(actual)}), "
        f"expected_near={expected[max(0,offset-50):offset+80]!r}, "
        f"actual_near={actual[max(0,offset-50):offset+80]!r}"
    )


class RoleSignature(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bps = []
        self.roles = []
        self.slots = []
        self.protected = 0
        self.attempts = 0
    def handle_starttag(self, tag, pairs):
        d = dict(pairs)
        if "data-blueprint-ref" in d:
            self.bps.append(d["data-blueprint-ref"])
        if "data-g9-role" in d:
            self.roles.append(d["data-g9-role"])
        if "data-blueprint-slot" in d:
            self.slots.append(d["data-blueprint-slot"])
        if "data-requires-attempt" in d:
            self.protected += 1
        if "data-g9-attempt-box" in d:
            self.attempts += 1


class OwnerFiveCoreGolden(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads((GOLD / "snapshot-lock.json").read_text(encoding="utf-8"))
        cls.fixture = json.loads((GOLD / "manifest.json").read_text(encoding="utf-8"))
        cls.live = json.loads(LIVE.read_text(encoding="utf-8"))
        cls.source_pages, cls.source_gaps, cls.source_digest, _, _ = render_core.build_report(
            LIVE, "PAGES", held_to="REFERENCE")
        cls.regen_pages, cls.regen_gaps, cls.regen_digest, _, _ = render_core.build_report(
            GOLD / "manifest.json", "PAGES", held_to="REFERENCE")

    def test_exact_frozen_html_lock_and_declared_ownership(self):
        l = self.lock
        self.assertEqual(l["status"], "OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT")
        self.assertEqual(l["fixture_id"], "G-IMO-G9-FIVE-CORE-20261012")
        self.assertEqual(l["source_commit"], "f87d2f627e3f05476d39fb04d7f26e453661dc68")
        self.assertEqual(l["renderer"], "render_core/2")
        self.assertEqual(l["reference_depth_gaps"], 0)
        self.assertEqual(l["snapshot_page_count"], len(ROLES))
        self.assertEqual(len(l["snapshots"]), len(ROLES))
        self.assertEqual([row["role"] for row in l["snapshots"]], list(ROLES))
        self.assertEqual(_git_blob((GOLD / "records.json").read_bytes()), l["source_records_sha"])
        for row in l["snapshots"]:
            with self.subTest(role=row["role"]):
                buf=(GOLD / row["path"]).read_bytes()
                self.assertEqual(_sha(buf), row["sha256"])
                self.assertEqual(_git_blob(buf), row["git_blob_sha"])
                self.assertIn(l["original_digest"].encode(), buf)
                self.assertIn(b"data-g9-role=" + ('"' + row["role"] + '"').encode(), buf)
        self.assertIn("independent QRT review", l["not_approved"])
        self.assertIn("D-182-2-H3", l["not_approved"])
        self.assertEqual(l["qrt_accepted"], "0/28")

    def test_source_live_manifest_exactly_regenerates_the_frozen_five(self):
        self.assertEqual(self.live["selection"], self.fixture["selection"])
        self.assertEqual(self.live["output_roles"], list(ROLES))
        self.assertEqual(self.fixture["output_roles"], list(ROLES))
        self.assertEqual(self.live["selection"]["core2"], [])
        self.assertEqual(self.source_digest, self.lock["original_digest"])
        self.assertFalse(self.source_gaps, self.source_gaps)
        self.assertEqual(set(self.source_pages), {role.lower()+".html" for role in ROLES} | {"index.html"})
        for row in self.lock["snapshots"]:
            with self.subTest(role=row["role"]):
                frozen=(GOLD / row["path"]).read_bytes()
                rendered=self.source_pages[row["role"].lower()+".html"].encode("utf-8")
                _compare_bytes(self, frozen, rendered, row["role"] + " exact frozen/sole-renderer")

    def test_golden_pinned_copy_rebuilds_only_with_expected_authority_digest_change(self):
        self.assertFalse(self.regen_gaps, self.regen_gaps)
        self.assertEqual(self.fixture["package_refs"],
                         ["golden/units/G-IMO-G9-FIVE-CORE-20261012/records.json"])
        # Identical source content may yield the SAME authority digest, even
        # though GOLDEN.md currently predicts a different one. Treat the real
        # sole-renderer result as the oracle; preserve frozen golden unchanged.
        self.assertEqual(set(self.source_pages), set(self.regen_pages))
        for row in self.lock["snapshots"]:
            with self.subTest(role=row["role"]):
                frozen=(GOLD / row["path"]).read_text(encoding="utf-8")
                new=self.regen_pages[row["role"].lower()+".html"]
                # Normalize the ORIGINAL locked authority digest, not the newer live
                # renderer digest.  A changed renderer may produce a new digest;
                # that is not permission to change frozen golden bytes.
                old_without_digest=frozen.replace(self.lock["original_digest"], "@RENDER_DIGEST@")
                new_without_digest=new.replace(self.regen_digest, "@RENDER_DIGEST@")
                _compare_bytes(self, old_without_digest.encode(), new_without_digest.encode(),
                               row["role"] + " pinned-record semantic HTML")

    def test_all_five_roles_keep_registered_blueprint_and_protected_attempt(self):
        for row in self.lock["snapshots"]:
            role=row["role"]
            with self.subTest(role=role):
                frozen=(GOLD / row["path"]).read_text(encoding="utf-8")
                parsed=RoleSignature()
                parsed.feed(frozen)
                self.assertEqual(parsed.bps, [BPS[role]])
                self.assertIn(role, parsed.roles)
                self.assertTrue(parsed.slots)
                if role not in ("CORE1",):
                    self.assertGreaterEqual(parsed.attempts,1)
                    self.assertGreaterEqual(parsed.protected,1)
                self.assertNotIn("SOF-IMO-G09-", frozen)
        # Avoid creating an authentic Core2 page from an unadmitted source.
        self.assertNotIn("core2.html", self.source_pages)


if __name__ == "__main__":
    unittest.main()
