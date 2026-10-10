"""Synthetic F04 E3 source/ledger denials; academic HOLD is never a test PASS."""
from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from Shared.tools.imo_f04_e3_held_observer import (
    DECLARED, QUESTION, MICROTOPIC, REQUIREMENTS, observe, main,
)


def example():
    m = {
        "subject": "TEST",
        "output_roles": ["CORE1A", "CORE2A"],
        "selection": {
            "core2a": [QUESTION], "microtopics": [MICROTOPIC],
            "core2": [], "core2b": [],
        },
    }
    p = {
        "subject": "TEST", "status": "CANDIDATE",
        "extensions": {
            "grade9v3:learner_published": False,
            "grade9v3:qrt_admitted": False,
            "grade9v3:core2_source_custody_granted": False,
        },
        "questions": [{"id": QUESTION, "origin": "AUTHORED"}],
    }
    g = {
        "status": "AUTHOR_REVIEW_FIXTURE_NOT_LEARNER_PRODUCT",
        "governance": {"academic_review": "NOT_GRANTED"},
    }
    e = {
        "schema": "imo-f02-e3-held-transfer-preflight/v1",
        "subject": "TEST",
        "existing_assisted_target": QUESTION,
        "already_disclosed_probes": list(DECLARED),
        "browser_local_trace_authority": "UNTRUSTED_NOT_CREDIT",
        "assessment_status": "REVIEW_ONLY_HOLD_NOT_ACCEPTED",
        "independent_mastery_verified": False,
        "credit_eligible": False,
        "new_item_provisioned": False,
        "errors": [],
        "findings": ["E3_INDEPENDENT_EVIDENCE_NOT_ESTABLISHED"],
        "requirements": [
            {"code": code, "status": "INDEPENDENT_EVIDENCE_NOT_PROVIDED"}
            for code in REQUIREMENTS
        ],
    }
    return m, p, g, e


class E3F04HoldObserverTests(unittest.TestCase):
    def test_safe_source_bound_ledger_cannot_award_credit(self):
        result = observe(*example())
        self.assertEqual(result["status"], "SOURCE_BOUND_DENIAL_ONLY")
        self.assertEqual(result["blocking_codes"], [])
        for name in (
            "source_core2_admitted", "new_unseen_item_provisioned",
            "first_unassisted_attempt_verified", "semantic_math_review_accepted",
            "independent_mastery_verified", "academic_accepted", "release_authorized",
        ):
            self.assertIs(result[name], False)
        self.assertEqual(result["required_review_codes"], list(REQUIREMENTS))

    def test_missing_or_forged_independent_evidence_never_passes(self):
        for field in ("independent_mastery_verified", "credit_eligible",
                      "new_item_provisioned"):
            with self.subTest(field=field):
                m,p,g,e=copy.deepcopy(example())
                e[field] = True
                self.assertIn("E3_F04_UNAUTHORIZED_TRANSFER_CREDIT",
                              observe(m,p,g,e)["blocking_codes"])
        m,p,g,e=copy.deepcopy(example())
        e["assessment_status"] = "ACCEPTED"
        self.assertIn("E3_F04_UNAUTHORIZED_TRANSFER_CREDIT",
                      observe(m,p,g,e)["blocking_codes"])

    def test_five_review_requirements_immutable_and_missing(self):
        for index in range(5):
            for replacement in (None, "ACCEPTED"):
                with self.subTest(index=index,replacement=replacement):
                    m,p,g,e=copy.deepcopy(example())
                    if replacement is None:
                        del e["requirements"][index]
                    else:
                        e["requirements"][index]["status"] = replacement
                    self.assertIn("E3_F04_INDEPENDENT_REVIEW_REQUIREMENTS_MISSING",
                                  observe(m,p,g,e)["blocking_codes"])
        m,p,g,e=copy.deepcopy(example())
        e["requirements"][0]["code"] = "UNSUPPORTED_SELF_REVIEW"
        self.assertIn("E3_F04_INDEPENDENT_REVIEW_REQUIREMENTS_MISSING",
                      observe(m,p,g,e)["blocking_codes"])

    def test_disclosed_exit_cannot_become_unseen(self):
        m,p,g,e=copy.deepcopy(example())
        e["already_disclosed_probes"] = []
        self.assertIn("E3_F04_SOURCE_LEDGER_INVALID",
                      observe(m,p,g,e)["blocking_codes"])
        e["already_disclosed_probes"] = list(DECLARED)
        e["existing_assisted_target"] = "UNTRUSTED_NOVEL_ITEM"
        self.assertIn("E3_F04_SOURCE_LEDGER_INVALID",
                      observe(m,p,g,e)["blocking_codes"])

    def test_mixed_or_forged_core2_and_released_package_denied(self):
        m,p,g,e=copy.deepcopy(example())
        m["selection"]["core2"] = [QUESTION]
        self.assertIn("E3_F04_UNAUTHORIZED_MANIFEST_SCOPE",
                      observe(m,p,g,e)["blocking_codes"])
        m,p,g,e=copy.deepcopy(example())
        p["extensions"]["grade9v3:qrt_admitted"]=True
        self.assertIn("E3_F04_UNAUTHORIZED_PACKAGE",
                      observe(m,p,g,e)["blocking_codes"])
        m,p,g,e=copy.deepcopy(example())
        g["governance"]["academic_review"]="GRANTED"
        self.assertIn("E3_F04_GOLDEN_EXPOSURE_BOUNDARY_UNVERIFIED",
                      observe(m,p,g,e)["blocking_codes"])

    def test_unsolicited_learner_answer_is_never_echoed(self):
        marker="SENSITIVE_LEARNER_RESPONSE_DO_NOT_EXPORT"
        m,p,g,e=copy.deepcopy(example())
        e["errors"]=[marker]
        e["learner_private_response"]=marker
        result=observe(m,p,g,e)
        self.assertIn("E3_F04_SOURCE_LEDGER_FINDINGS_UNSAFE",
                      result["blocking_codes"])
        self.assertNotIn(marker,json.dumps(result))

    def test_bad_shapes_and_unreadable_input_fail_closed(self):
        for index in range(4):
            with self.subTest(index=index):
                args=list(copy.deepcopy(example()))
                args[index] = None
                self.assertEqual(observe(*args)["status"],"BLOCKED")
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            files=[root/f"{i}.json" for i in range(4)]
            for file, data in zip(files,example()):
                file.write_text(json.dumps(data),encoding="utf-8")
            files[3].write_text('{"private":"not closed"',encoding="utf-8")
            stdout=io.StringIO()
            with redirect_stdout(stdout):
                rc=main(["--manifest",str(files[0]),"--package",str(files[1]),
                         "--golden",str(files[2]),"--e3-receipt",str(files[3]),
                         "--safe-output",str(root/"build"/"safe.json")])
            self.assertEqual(rc,1)
            self.assertIn("BLOCKED",stdout.getvalue())
            self.assertNotIn("private",stdout.getvalue())

    def test_strict_acceptance_always_denied_but_held_observer_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            files=[root/f"{i}.json" for i in range(4)]
            for file,data in zip(files,example()):
                file.write_text(json.dumps(data),encoding="utf-8")
            argv=["--manifest",str(files[0]),"--package",str(files[1]),
                  "--golden",str(files[2]),"--e3-receipt",str(files[3]),
                  "--safe-output",str(root/"build"/"safe.json")]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(argv),0)
                self.assertEqual(main(argv+["--require-independent-acceptance"]),1)
            result=json.loads((root/"build"/"safe.json").read_text())
            self.assertEqual(result["status"],"SOURCE_BOUND_DENIAL_ONLY")
            self.assertEqual(set(result["source_sha256"]),
                             {"manifest","package","golden","e3_receipt"})


if __name__ == "__main__":
    unittest.main()
