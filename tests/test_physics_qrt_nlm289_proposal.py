"""Issue #289 source-preserving Physics correction proposal tests, never a grader.

This test creates only an in-memory proposed question. It must never write to
Physics/library, goldens, author branches, shared renderers or public pages.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "tools/physics_qrt_program/proposals/nlm289_candidate.v1.json"
SOURCE = ROOT / "Physics/library/phy-nlm-first-law.v1.json"
ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"
ORIGINAL_BLOB = "62b8df106e83db03ac80fbb4002a611ac3d6e49a"
ORIGINAL_QUESTION = "32c5a4447dfdccf0de457ed6d07a12c448f995869699b02adeed2997feb76f50"
PROTECTED_SOURCE_FIELDS = (
    "id","version","status","source_refs","evidence_refs","extensions",
    "origin","origin_ref","original_identifier","primary_capability_ref",
    "secondary_capability_refs","family_ref","adaptation","exposure",
    "transfer","repair_ref","representation_roles","family_exposure",
    "learner_question_type","difficulty"
)

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def compact_digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,
                                   separators=(",",":")).encode("utf-8")).hexdigest()

def originals():
    raw=SOURCE.read_bytes()
    if git_blob(raw)!=ORIGINAL_BLOB:
        raise AssertionError("ORIGINAL_SOURCE_BLOB_DRIFT")
    package=json.loads(raw)
    matches=[q for q in package["questions"] if q.get("id")==ID]
    if len(matches)!=1:
        raise AssertionError("ORIGINAL_QUESTION_ID_NOT_UNIQUE")
    if compact_digest(matches[0])!=ORIGINAL_QUESTION:
        raise AssertionError("ORIGINAL_QUESTION_CONTENT_DRIFT")
    return package,matches[0]

def candidate():
    proposal=json.loads(PROPOSAL.read_text(encoding="utf-8"))
    _,old=originals()
    q=copy.deepcopy(old)
    patch=proposal["patches"]
    for key in ("stem","conditions","hints","hint_ladder"):
        q[key]=copy.deepcopy(patch[key])
    for key,value in patch["answer"].items():
        q["answer"][key]=copy.deepcopy(value)
    return proposal,old,q

class NLM289ProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposal,cls.old,cls.new=candidate()

    def test_issue_lock_and_approval_false(self):
        p=self.proposal
        self.assertEqual(p["schema"],"physics-qrt.nlm289-candidate-proposal/v1")
        self.assertEqual(p["source"]["question_id"],ID)
        self.assertEqual(p["source"]["git_blob_sha"],ORIGINAL_BLOB)
        self.assertEqual(p["source"]["question_sha256"],ORIGINAL_QUESTION)
        auth=p["authority"]
        self.assertEqual(auth["source_writer"],"NOT_ASSIGNED")
        self.assertFalse(auth["source_write_authorized"])
        self.assertFalse(auth["editing_production_source"])
        self.assertEqual(auth["academic_human_review"],"PENDING")
        self.assertEqual(auth["approval"],"NOT_GRANTED")
        self.assertEqual(auth["release"],"HOLD")

    def test_real_current_source_has_before_attempt_directives(self):
        old=self.old
        conditions=" ".join(old["conditions"]).lower()
        hints=" ".join(h["text"] for h in old["hints"]).lower()
        self.assertIn("resolve each pull into horizontal and vertical",conditions)
        self.assertIn("do not take n = mg",conditions)
        self.assertIn("vertical balance",hints)
        self.assertEqual(old["answer"]["acceptable_alternatives"],[])

    def test_only_single_question_fields_proposed_not_executed(self):
        old,new=self.old,self.new
        self.assertEqual(old["id"],new["id"])
        self.assertEqual({k:old[k] for k in PROTECTED_SOURCE_FIELDS},
                         {k:new[k] for k in PROTECTED_SOURCE_FIELDS})
        altered={k for k in new if old.get(k)!=new.get(k)}
        self.assertEqual(altered,{"stem","conditions","hints","hint_ladder","answer"})
        self.assertEqual({k for k in new["answer"] if old["answer"].get(k)!=new["answer"].get(k)},
                         set(self.proposal["patches"]["answer"]))

    def test_other_questions_and_original_source_unchanged(self):
        before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        package,original=originals()
        self.assertGreater(len(package["questions"]),2)
        p,_,new=candidate()
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),before)
        self.assertNotEqual(compact_digest(original),compact_digest(new))
        self.assertEqual(original["id"],new["id"])

    def test_d1_no_decisive_equations_in_preattempt_text(self):
        q=self.new
        text=" ".join([q["stem"],*q["conditions"],
                        *(h["text"] for h in q["hints"]),
                        *(row.get("text","") for row in q["hint_ladder"])]).lower()
        for forbidden in ("n = mg","n=100","100 − p", "p cos",
                          "pcrit", "vertical balance","write n",
                          "37° pull needs the least", "only at 37"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,text)
        self.assertNotIn("resolve each pull into horizontal and vertical",
                         " ".join(q["conditions"]).lower())

    def test_d1_hint_ladder_has_valid_existing_schema(self):
        q=self.new
        self.assertEqual([x["order"] for x in q["hint_ladder"]],[1,2,3])
        for hint in q["hints"]:
            self.assertEqual(hint["reveals"],"CONCEPT")
        for row in q["hint_ladder"]:
            if "from" in row:
                self.assertIn(row["from"],("hints[0]","hints[1]"))
            else:
                self.assertTrue(row.get("text"))

    def test_d3_limit_and_strict_onset_not_conflated(self):
        q=self.new
        source=(q["stem"]+" "+" ".join(q["conditions"])).lower()
        self.assertIn("impending slip",source)
        self.assertIn("equality",source)
        check=q["answer"]["summary"].lower()
        self.assertIn("strictly above",check)
        self.assertIn("limiting static equilibrium",check)

    def test_d4_non_tipping_domain_declared(self):
        text=" ".join(self.new["conditions"]).lower()
        self.assertIn("non-tipping",text)
        self.assertIn("non-rotating",text)
        self.assertIn("floor contact",text)
        self.assertIn("direction remains fixed",text)

    def test_source_derived_critical_values_in_ideal_model(self):
        # Independent bounded physics sanity check; NOT a learner grader.
        g,m,mu=10.,10.,0.75
        pairs=((1.,0.,75.),(.8,.6,60.),(.6,.8,62.5))
        for c,s,expected in pairs:
            with self.subTest(direction=(c,s)):
                crit=mu*m*g/(c+mu*s)
                normal=m*g-crit*s
                self.assertGreater(normal,0)
                self.assertTrue(math.isclose(crit,expected,abs_tol=1e-10))
                self.assertTrue(math.isclose(crit*c,mu*normal,abs_tol=1e-10))
        self.assertTrue(60 < 61 < 62.5 < 75)

    def test_d2_positive_alternatives_are_explicit_not_grader(self):
        alts=self.new["answer"]["acceptable_alternatives"]
        self.assertGreaterEqual(len(alts),5)
        self.assertTrue(all(isinstance(s,str) and len(s)>40 for s in alts))
        positives=self.proposal["review_controls"]["positive_equivalents"]
        self.assertGreaterEqual(len(positives),4)
        self.assertEqual(len(set(x["id"] for x in positives)),len(positives))
        self.assertTrue(all(x["expected"]=="ACCEPT_BY_QUALIFIED_RUBRIC_REVIEW"
                            for x in positives))
        self.assertEqual(self.proposal["review_controls"]["execution"],
                         "PROPOSED_CORPUS_ONLY_NO_RUNNING_GRADER")
        self.assertEqual(self.proposal["review_controls"]["target_assessment_surface"],
                         "UNKNOWN_NEEDS_OWNER_SPECIFICATION")

    def test_d2_known_false_physics_models_are_not_positive_cases(self):
        falsifiers=self.proposal["review_controls"]["false_result_controls"]
        self.assertGreaterEqual(len(falsifiers),5)
        text=" ".join(x["claim"] for x in falsifiers).lower()
        for forbidden in ("n=mg", "53°", "pcosθ", "equality", "tipping"):
            self.assertIn(forbidden,text)
        self.assertTrue(all(x["expected"].startswith(("REJECT_","REJECT_OR_"))
                            for x in falsifiers))

    def test_d2_rubric_accepts_physics_not_one_formula_string(self):
        criteria=self.new["answer"]["rubric"]
        self.assertGreaterEqual(len(criteria),3)
        self.assertTrue(all(row.get("criterion") and row.get("evidence_of") for row in criteria))
        rubric=" ".join(row["evidence_of"] for row in criteria).lower()
        self.assertIn("equivalent",rubric)
        self.assertIn("sign",rubric)

    def test_d5_d6_held_even_if_patch_looks_better(self):
        ed=self.proposal["educational_checks"]
        self.assertIn("NOT_ESTABLISHED",ed["D5"])
        self.assertIn("HOLD",ed["D6"])
        self.assertEqual(self.proposal["authority"]["independent_transfer"],"NOT_ESTABLISHED")
        self.assertEqual(self.proposal["authority"]["canonical_cognitive_demand"],"NOT_CLASSIFIED")
        self.assertEqual(self.old["transfer"],self.new["transfer"])
        self.assertNotIn("grade9v3:cognitive_demand",self.new["extensions"])

    def test_no_shared_renderer_or_protected_snapshot_manipulated(self):
        auth=self.proposal["authority"]
        self.assertFalse(auth["editing_production_source"])
        self.assertNotIn("package",self.proposal["patches"])
        self.assertNotIn("renderer",self.proposal["patches"])
        self.assertNotIn("golden",self.proposal["patches"])

if __name__=="__main__":
    unittest.main()
