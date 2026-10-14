#!/usr/bin/env python3
"""Mutation controls for IMO #182 P0: proof of rejection, NOT a QRT verdict."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

from qrt_intent_contract import (  # noqa: E402
    BANDS, DEMANDS, ROLES, REVIEWS, ContractError,
    canonical, validate_payload
)


class IntentContractMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix, cls.templates, _ = canonical(ROOT)
        bank = json.loads((HERE / "qrt-intent-witnesses-pilot.v1.json")
                          .read_text(encoding="utf-8"))
        cls.witnesses = {x["cell_id"]: x for x in bank["witnesses"]}

    def fixture(self, cell: str = "QRT-MODEL-D2"):
        witness = copy.deepcopy(self.witnesses[cell])
        template = next(t for t in self.templates["templates"]
                        if t["template_id"] == cell)
        _, demand, band = cell.split("-")
        def q(qid, crux):
            return {
                "id": qid,
                "stem": "Original TEST task with independently described givens.",
                "extensions": {
                    "grade9v3:cognitive_demand": {
                        "primary": demand,
                        "secondary": [witness["strongest_rival"]]
                    }
                },
                "difficulty": {
                    "band": band, "score": 4,
                    "components": {
                        "concept_model_selection": 1,
                        "representation_translation": 1,
                        "reasoning_chain_length": 1,
                        "algebra_computational_load": 1,
                        "trap_exception_sensitivity": 0
                    }
                },
                "answer": {
                    "crux_move_ref": crux,
                    "reasoning_route": [{
                        "id": crux, "kind": "DECIDE",
                        "action": "Learner owns the source-bound protected inference"
                    }]
                }
            }
        source = {
            "subject": "TEST", "status": "CANDIDATE",
            "microtopics": [{"id": "M1"}],
            "questions": [
                q(witness["primary_question_id"],
                  witness["primary_crux_move_ref"]),
                q(witness["transfer_question_id"],
                  witness["transfer_crux_move_ref"]),
            ]
        }
        manifest = {
            "output_roles": list(ROLES),
            "selection": {
                "core2": [], "microtopics": ["M1"],
                "core2a": [witness["primary_question_id"]],
                "core2b": [witness["transfer_question_id"]],
            },
        }
        if cell == "QRT-RETRIEVE-D2":
            source["questions"][0]["stem"] = (
                "A rectangle has perpendicular sides 9m and 12m. "
                "Retrieve the right-triangle distance relation and compute "
                "both routes; compare them."
            )
        return source, manifest, template, witness

    def checked(self, cell="QRT-MODEL-D2"):
        args = self.fixture(cell)
        return validate_payload(args[0], args[1],
                                self.matrix, args[2], args[3])

    def rejects(self, code, args):
        with self.assertRaisesRegex(ContractError, "^" + code + ":"):
            validate_payload(args[0], args[1],
                             self.matrix, args[2], args[3])

    def test_canonical_matrix_is_exact_seven_by_four(self):
        cells = {x["template_id"] for x in self.templates["templates"]}
        self.assertEqual(cells, {f"QRT-{d}-{b}"
                                for d in DEMANDS for b in BANDS})
        self.assertEqual(len(REVIEWS), 12)

    def test_validated_intent_never_auto_awards_role_or_owner_acceptance(self):
        for cell in self.witnesses:
            if cell in ("QRT-MODEL-D1", "QRT-SYNTHESIZE-D1"):
                # These actual pinned source questions declare NO secondary
                # demand; intentionally never fabricate one to make a PASS.
                continue
            with self.subTest(cell=cell):
                c = self.checked(cell)
                self.assertEqual(c["technical_contract"],
                                 "VALIDATED_PROPOSAL")
                self.assertEqual(c["semantic_review"],
                                 "HOLD_REVIEW_REQUIRED")
                self.assertEqual(c["qualified_academic_review"],
                                 "PENDING")
                self.assertEqual(c["owner_qrt_acceptance"], "PENDING")
                self.assertEqual(c["whole_journey_W"]["status"], "NOT_RUN")
                self.assertEqual(len(c["roles"]), 5)
                self.assertEqual(len(c["semantic_objectives"]), 12)
                self.assertTrue(all(v["verdict"] == "NOT_RUN"
                                    for v in c["semantic_objectives"].values()))

    def test_missing_rival_fails_closed(self):
        args = list(self.fixture())
        args[3]["strongest_rival"] = ""
        self.rejects("RIVAL_REQUIRED", args)

    def test_unresolved_source_crux_fails_closed(self):
        args = list(self.fixture())
        args[0]["questions"][0]["answer"]["crux_move_ref"] = "NOT-AN-EXISTING-MOVE"
        self.rejects("UNRESOLVED_CRUX", args)

    def test_witness_crux_drift_fails_closed(self):
        args = list(self.fixture())
        args[3]["primary_crux_move_ref"] = "OTHER-MOVE"
        self.rejects("WITNESS_CRUX_DRIFT", args)

    def test_missing_success_evidence_fails_closed(self):
        args = list(self.fixture())
        args[3]["success_evidence"] = ""
        self.rejects("SUCCESS_EVIDENCE_REQUIRED", args)

    def test_generic_w_without_question_specificity_fails_closed(self):
        args = list(self.fixture())
        args[3]["question_specific_W"] = "choose a model"
        self.rejects("QUESTION_SPECIFIC_W_REQUIRED", args)

    def test_missing_falsifier_fails_closed(self):
        args = list(self.fixture())
        args[3]["falsifier"] = {}
        self.rejects("FALSIFIER_REQUIRED", args)

    def test_band_drift_fails_closed(self):
        args = list(self.fixture())
        args[0]["questions"][0]["difficulty"]["band"] = "D4"
        self.rejects("QUESTION_BAND_DRIFT", args)

    def test_rival_must_be_grounded_in_source(self):
        args = list(self.fixture())
        args[0]["questions"][0]["extensions"][
            "grade9v3:cognitive_demand"]["secondary"] = []
        self.rejects("RIVAL_NOT_GROUNDED_IN_SOURCE", args)

    def test_manifest_primary_drift_fails_closed(self):
        args = list(self.fixture())
        args[1]["selection"]["core2a"] = ["WRONG"]
        self.rejects("WITNESS_SELECTION_DRIFT", args)

    def test_cued_retrieve_is_observed_but_cannot_be_accepted(self):
        c = self.checked("QRT-RETRIEVE-D2")
        self.assertTrue(c["falsifier"]["specific_source_cue_observed"])
        self.assertEqual(c["semantic_review"], "HOLD_REVIEW_REQUIRED")
        self.assertEqual(c["strongest_rival"], "APPLY")

    def test_known_retrieve_method_cue_mutation_is_detected(self):
        args = list(self.fixture("QRT-RETRIEVE-D2"))
        args[0]["questions"][0]["stem"] = (
            "A rectangle has perpendicular sides 9m and 12m. "
            "Choose an appropriate relationship, calculate the two routes."
        )
        self.rejects("METHOD_CUE_EXPECTATION_DRIFT", args)

    def test_high_risk_source_rival_declaration_gaps_fail_closed(self):
        for cell in ("QRT-MODEL-D1", "QRT-SYNTHESIZE-D1"):
            with self.subTest(cell=cell):
                args = list(self.fixture(cell))
                args[0]["questions"][0]["extensions"][
                    "grade9v3:cognitive_demand"]["secondary"] = []
                self.rejects("RIVAL_NOT_GROUNDED_IN_SOURCE", args)

    def test_three_additional_elevated_holds_remain_unaccepted(self):
        for cell in ("QRT-JUSTIFY-D1", "QRT-RETRIEVE-D3",
                     "QRT-MODEL-D3"):
            with self.subTest(cell=cell):
                result = self.checked(cell)
                self.assertEqual(result["semantic_review"],
                                 "HOLD_REVIEW_REQUIRED")
                self.assertEqual(result["qualified_academic_review"],
                                 "PENDING")
                self.assertEqual(result["owner_qrt_acceptance"], "PENDING")

    def test_d4_prior_knowledge_is_not_artificially_certified(self):
        c = self.checked("QRT-RETRIEVE-D4")
        self.assertEqual(c["learner_prior_knowledge_status"],
                         "UNKNOWN_AND_REQUIRES_QUALIFIED_REVIEW")
        self.assertEqual(c["roles"]["CORE1A"]["semantic"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
