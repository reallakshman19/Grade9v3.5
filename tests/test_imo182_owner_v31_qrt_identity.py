"""O2 prerequisite: identify the authored questions served by the Owner's O1 golden.

This contract only checks the ACTUAL frozen TEST source/manifest/page lineage.
It does not certify a QRT band, reviewer independence, accepted cell, print,
human learning, release rights, or future post-H3 successor golden.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
MANIFEST = ROOT / "TEST/products/imo-182-five-core-integrated-review.manifest.json"
RECORDS = ROOT / "TEST/imo-research/pilots/imo182-core2b-transfer-pilot.v1.json"
ROLES = ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
EXPECTED = {
    "CORE2A": "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF",
    "CORE2B": "Q-TEST-CORE2B-FOUR-FACTOR-48-BOUNDARY",
}
WORKED = "Q-TEST-CORE1A-QUAL-G9-WORKED-DIVISIBILITY"


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class OwnerV31QRTIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.records = json.loads(RECORDS.read_text(encoding="utf-8"))
        cls.lock = json.loads((GOLD / "snapshot-lock.json").read_text(encoding="utf-8"))
        cls.by_id = {q["id"]: q for q in cls.records["questions"]}
        cls.pages = {
            row["role"]: (GOLD / row["path"]).read_bytes()
            for row in cls.lock["snapshots"]
        }

    def test_one_exact_owner_golden_and_renderer_source_identity(self):
        self.assertEqual(self.lock["status"], "OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT")
        self.assertEqual(self.lock["renderer"], "render_core/2")
        self.assertEqual(self.lock["source_manifest"], MANIFEST.relative_to(ROOT).as_posix())
        self.assertEqual(self.manifest["package_refs"], [RECORDS.relative_to(ROOT).as_posix()])
        self.assertEqual(git_blob(RECORDS.read_bytes()), self.lock["source_records_sha"])
        self.assertEqual(git_blob((GOLD / "records.json").read_bytes()), self.lock["source_records_sha"])
        self.assertEqual(self.manifest["output_roles"], list(ROLES))
        self.assertEqual(tuple(self.pages), ROLES)
        self.assertEqual(self.manifest["selection"]["core2"], [])
        for row in self.lock["snapshots"]:
            with self.subTest(role=row["role"]):
                self.assertEqual(hashlib.sha256(self.pages[row["role"]]).hexdigest(), row["sha256"])
                self.assertEqual(git_blob(self.pages[row["role"]]), row["git_blob_sha"])

    def test_only_core2a_and_core2b_are_selected_question_bearing_roles(self):
        selected = self.manifest["selection"]
        self.assertEqual(selected["core2a"], [EXPECTED["CORE2A"]])
        self.assertEqual(selected["core2b"], [EXPECTED["CORE2B"]])
        self.assertEqual(len(selected["microtopics"]), 1)
        self.assertEqual(selected["microtopics"][0], "MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS")
        self.assertEqual(set(self.by_id), {WORKED, *EXPECTED.values()})
        worked = self.by_id[WORKED]
        self.assertEqual(worked["origin"], "AUTHORED")
        self.assertEqual([x["core"] for x in worked["exposure"]], ["CORE1A"])
        for role, qid in EXPECTED.items():
            with self.subTest(role=role):
                q = self.by_id[qid]
                self.assertEqual(q["origin"], "AUTHORED")
                self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"], "JUSTIFY")
                self.assertEqual([x["core"] for x in q["exposure"]], [role])
                self.assertTrue(q["answer"]["crux_move_ref"])
        # These are authored *proposed* labels. No Owner verdict is manufactured.

    def test_actual_frozen_pages_distinguish_question_from_support(self):
        for role, qid in EXPECTED.items():
            self.assertIn(qid.encode(), self.pages[role])
            self.assertIn(('data-g9-role="' + role + '"').encode(), self.pages[role])
        for role in ("CORE1", "CORE1A", "CORE1B"):
            with self.subTest(role=role):
                self.assertNotIn(EXPECTED["CORE2A"].encode(), self.pages[role])
                self.assertNotIn(EXPECTED["CORE2B"].encode(), self.pages[role])
                self.assertIn(('data-g9-role="' + role + '"').encode(), self.pages[role])
        self.assertIn(WORKED, self.by_id)
        self.assertIn(b'data-blueprint-ref="BP-CORE1A-CONSTRUCTION@1.8.0"', self.pages["CORE1A"])
        self.assertIn(b'data-blueprint-ref="BP-CORE1B-RECONSTRUCTION@1.1.0"', self.pages["CORE1B"])

    def test_cannot_confuse_frozen_candidate_with_the_seven_cell_d2_source(self):
        self.assertFalse(any(qid.startswith("Q-TEST-QRT-JUSTIFY-D2-") for qid in self.by_id))
        self.assertEqual(self.lock["qrt_accepted"], "0/28")
        self.assertIn("independent QRT review", self.lock["not_approved"])
        self.assertIn("D-182-2-H3", self.lock["not_approved"])


if __name__ == "__main__":
    unittest.main()
