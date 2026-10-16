"""Physics QRT reuse audit: source/ledger/registry controls, not scientific review."""
from __future__ import annotations
import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Physics.adapter.qrt_program.qrt_blueprint_reuse import (
    ACTIVE, ASKS, BANDS, DEMANDS, REGISTRY, ROLES, ROOT, TEMPLATES,
    WITNESSES, ReuseBlocked, map_reuse,
)
PACKAGE_PATHS = (
    "Physics/library/phy-vec-add-sub.v1.json",
    "Physics/library/phy-kin-2d-motion.v1.json",
    "Physics/library/phy-nlm-first-law.v1.json",
)

class PhysicsReuseTest(unittest.TestCase):
    def fixture(self):
        obj=tempfile.TemporaryDirectory()
        self.addCleanup(obj.cleanup)
        root=Path(obj.name)
        for path in (REGISTRY,TEMPLATES,WITNESSES,*PACKAGE_PATHS):
            target=root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,target)
        return root

    def rewrite(self,root,path,change):
        p=root/path
        data=json.loads(p.read_text(encoding="utf-8"))
        change(data)
        p.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")

    def test_actual_four_sources_reuse_shared_registries(self):
        result=map_reuse()
        self.assertEqual(result["schema"],"physics-qrt.shared-reuse-evidence/v1")
        self.assertEqual(result["summary"]["shared_qrt_semantic_templates"],28)
        self.assertEqual(result["summary"]["registered_core_blueprints"],7)
        self.assertEqual(result["summary"]["registered_role_links"],20)
        self.assertEqual(result["summary"]["actually_rendered_role_pages_proven_by_this_map"],0)
        self.assertEqual(result["summary"]["academically_accepted_physics_questions"],0)
        self.assertEqual(len(result["rows"]),4)
        self.assertFalse(result["new_renderer_created"])
        self.assertEqual(result["new_blueprints_created"],0)

    def test_only_nlm_review_is_active(self):
        report=map_reuse()
        active=[r for r in report["rows"] if r["review_scope"]=="ACTIVE_SINGLE_NLM_OPTION_A"]
        self.assertEqual(len(active),1)
        self.assertEqual(active[0]["question_id"],ACTIVE)
        self.assertEqual(len([x for x in report["rows"] if x["review_scope"].startswith("RESERVED_")]),3)

    def test_all_rows_refuse_premature_qrt_admission(self):
        for row in map_reuse()["rows"]:
            with self.subTest(question=row["question_id"]):
                self.assertIsNone(row["qrt_cell"])
                self.assertEqual(row["qrt_assignment_status"],"UNRESOLVED_COGNITIVE_DEMAND_HOLD")
                self.assertEqual(row["qrt_source_gate"]["state"],"BLOCKED")
                self.assertEqual(row["native_five_page_evidence"],"NOT_RECOMPUTED_BY_THIS_MAP")
                self.assertFalse(row["owner_accepted"])
                self.assertFalse(row["published"])
                self.assertEqual(tuple(row["review_asks"]),ASKS)
                self.assertTrue(all(v=="NOT_RUN_FOR_THIS_QUESTION" for v in row["review_asks"].values()))

    def test_all_role_mappings_are_registered_not_pages(self):
        for row in map_reuse()["rows"]:
            self.assertEqual(tuple(x["role"] for x in row["five_registered_role_blueprints"]),ROLES)
            self.assertTrue(all(x["availability"]=="REGISTERED_ONLY_NOT_RENDER_ATTESTATION"
                                for x in row["five_registered_role_blueprints"]))

    def test_output_source_identity_is_observed(self):
        report=map_reuse()
        self.assertEqual(report["canonical_pointers"]["blueprints"]["git_blob_sha"],
                         "591ba061b8771c30fdffc4506aa720ca9ba89335")
        for row in report["rows"]:
            current=(ROOT/row["source"]["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(current).hexdigest(),row["source"]["sha256"])

    def test_no_source_files_edited(self):
        before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                for p in (REGISTRY,TEMPLATES,WITNESSES,*PACKAGE_PATHS)}
        map_reuse()
        self.assertEqual(before,{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                                 for p in before})

    def test_wrong_actual_blob_blocks(self):
        root=self.fixture()
        self.rewrite(root,PACKAGE_PATHS[2],lambda x:x.update(title="modified physics source"))
        with self.assertRaisesRegex(ReuseBlocked,"SOURCE_ORIGINAL_BLOB_OR_CUSTODY_DRIFT"):
            map_reuse(root)

    def test_missing_package_blocks(self):
        root=self.fixture()
        (root/PACKAGE_PATHS[0]).unlink()
        with self.assertRaises(ValueError):
            map_reuse(root)

    def test_wrong_question_id_blocks(self):
        root=self.fixture()
        self.rewrite(root,WITNESSES,lambda w:w["cases"][0].update(question_id="Q-PHY-UNKNOWN"))
        with self.assertRaises(ReuseBlocked):
            map_reuse(root)

    def test_duplicate_question_blocks(self):
        root=self.fixture()
        self.rewrite(root,WITNESSES,lambda w:w["cases"][0].update(question_id=ACTIVE))
        with self.assertRaisesRegex(ReuseBlocked,"NLM_ONE_ACTIVE_PILOT_REQUIRED"):
            map_reuse(root)

    def test_wrong_owner_source_cut_blocks(self):
        root=self.fixture()
        self.rewrite(root,WITNESSES,lambda w:w.update(base_sha="0"*40))
        with self.assertRaisesRegex(ReuseBlocked,"WITNESS_CONTRACT_OR_SOURCE_CUT_DRIFT"):
            map_reuse(root)

    def test_fake_28th_template_missing_blocks(self):
        root=self.fixture()
        self.rewrite(root,TEMPLATES,lambda x:x["templates"].pop())
        with self.assertRaisesRegex(ReuseBlocked,"SHARED_28_QRT_CATALOGUE_DRIFT"):
            map_reuse(root)

    def test_duplicate_semantic_template_blocks(self):
        root=self.fixture()
        self.rewrite(root,TEMPLATES,lambda x:x["templates"].__setitem__(0,copy.deepcopy(x["templates"][1])))
        with self.assertRaisesRegex(ReuseBlocked,"SHARED_28_QRT_CATALOGUE_DRIFT"):
            map_reuse(root)

    def test_missing_review_objective_blocks(self):
        root=self.fixture()
        self.rewrite(root,TEMPLATES,lambda x:x["templates"][0]["review"].pop("P1"))
        with self.assertRaisesRegex(ReuseBlocked,"CANONICAL_12_ASKS_DRIFT"):
            map_reuse(root)

    def test_missing_protected_w_blocks(self):
        root=self.fixture()
        self.rewrite(root,TEMPLATES,lambda x:x["templates"][0]["slots"].pop("W"))
        with self.assertRaisesRegex(ReuseBlocked,"QRT_PROTECTED_WORK_MISSING"):
            map_reuse(root)

    def test_blueprint_change_without_source_authority_blocks(self):
        root=self.fixture()
        self.rewrite(root,REGISTRY,lambda x:x["blueprints"].pop())
        with self.assertRaisesRegex(ReuseBlocked,"REGISTERED_7_BLUEPRINTS_DRIFT"):
            map_reuse(root)

    def test_core2b_role_missing_blocks(self):
        root=self.fixture()
        self.rewrite(root,REGISTRY,lambda x:x["blueprints"][-2].update(core_roles=[]))
        with self.assertRaisesRegex(ReuseBlocked,"EXPECTED_CORE_ROLE_BLUEPRINTS_MISSING"):
            map_reuse(root)

    def test_fake_nonphysics_source_path_blocks(self):
        root=self.fixture()
        self.rewrite(root,WITNESSES,lambda x:x["cases"][0].update(package="../private/source.json"))
        with self.assertRaisesRegex(ReuseBlocked,"PHYSICS_LIBRARY_ONLY"):
            map_reuse(root)

    def test_candidate_map_not_blind_review_packet(self):
        report=map_reuse()
        self.assertEqual(report["kind"],"SOURCE_REFERENCED_CANDIDATE_ONLY_NOT_FOR_BLIND_PASS_A")
        self.assertEqual(report["scientific_acceptance"],"HOLD")
        self.assertEqual(report["qrt_semantic_acceptance"],"HOLD")
        self.assertEqual(report["owner_approval"],"NOT_GRANTED")
        self.assertEqual(report["release"],"HOLD")

if __name__=="__main__":
    unittest.main()
