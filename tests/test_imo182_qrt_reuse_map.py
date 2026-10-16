"""Falsify unsupported reuse/acceptance claims in the source-first 28-cell map."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "TEST/imo-research/qrt-tiles/reconciliation/qrt_reuse_map.py"
spec = importlib.util.spec_from_file_location("qrt_reuse_map", FILE)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class ReuseMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = model.read(ROOT, model.TEMPLATE)
        cls.b = model.read(ROOT, model.BLUEPRINT)
        cls.l = model.read(ROOT, model.LEDGER)
        cls.sha = model.git_blob((ROOT / model.BLUEPRINT).read_bytes())

    def build(self, t=None, b=None, l=None, sha=None):
        return model.compile_map(copy.deepcopy(t if t is not None else self.t),
                                 copy.deepcopy(b if b is not None else self.b),
                                 copy.deepcopy(l if l is not None else self.l),
                                 self.sha if sha is None else sha)

    def test_real_28_tiles_reuse_only_five_registered_core_blueprints(self):
        rows = self.build()
        self.assertEqual(len(rows["cells"]), 28)
        self.assertEqual(rows["summary"]["recorded_core_html_files"], 140)
        self.assertEqual(rows["summary"]["recorded_index_html_files"], 28)
        self.assertEqual(rows["summary"]["elevated_educational_holds"], 8)
        self.assertEqual(rows["summary"]["qualified_or_owner_accepted"], 0)
        for r in rows["cells"]:
            with self.subTest(cell=r["cell"]):
                self.assertEqual(len(r["native_core_roles"]), 5)
                self.assertTrue(all(x["registered_blueprint"].startswith("BP-CORE")
                                    for x in r["native_core_roles"]))
                self.assertEqual(r["academic_review"], "QUALIFIED_INDEPENDENT_REVIEW_PENDING")
                self.assertEqual(r["owner_acceptance"], "NOT_GRANTED")
                self.assertIn("NOT_RESOLVED", r["question_specific_X_Y_Z_W"])

    def test_missing_template_fails(self):
        x = copy.deepcopy(self.t)
        x["templates"].pop()
        with self.assertRaisesRegex(model.MapBlocked, "28_TEMPLATE_IDS_REQUIRED"):
            self.build(t=x)

    def test_duplicate_cell_fails(self):
        x = copy.deepcopy(self.l)
        x["rows"][0] = copy.deepcopy(x["rows"][1])
        with self.assertRaisesRegex(model.MapBlocked, "28_LEDGER_ROWS_REQUIRED"):
            self.build(l=x)

    def test_drifted_blueprint_registry_fails(self):
        with self.assertRaisesRegex(model.MapBlocked, "BLUEPRINT_REGISTRY_STALE"):
            self.build(sha="f"*40)

    def test_missing_core_blueprint_fails(self):
        x = copy.deepcopy(self.b)
        x["blueprints"] = [row for row in x["blueprints"]
                           if "CORE2B" not in row["core_roles"]]
        with self.assertRaisesRegex(model.MapBlocked, "REQUIRED_REGISTERED_BLUEPRINT_MISSING"):
            self.build(b=x)

    def test_missing_native_hash_fails(self):
        x = copy.deepcopy(self.l)
        del x["rows"][0]["artifact"]["native_html_sha256"]["core1.html"]
        with self.assertRaisesRegex(model.MapBlocked, "SIX_HTML_DIGESTS_REQUIRED"):
            self.build(l=x)

    def test_false_approval_is_not_promoted(self):
        x = copy.deepcopy(self.l)
        x["rows"][0]["owner_qrta_accepted"] = True
        with self.assertRaisesRegex(model.MapBlocked, "UNSUPPORTED_OWNER_OR_ACADEMIC_APPROVAL"):
            self.build(l=x)

    def test_missing_review_question_fails(self):
        x = copy.deepcopy(self.t)
        x["templates"][0]["review"].pop("M3")
        with self.assertRaisesRegex(model.MapBlocked, "12_REVIEW_ASKS_REQUIRED"):
            self.build(t=x)


if __name__ == "__main__":
    unittest.main()
