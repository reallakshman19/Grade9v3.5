"""Frozen 28-question five-anchor blueprint proof: mechanical falsifier, not academic approval.

All proof quotes and decisions are sourced from the exact 90c85970 source tree;
Core2 research custody is NOT promoted by passing these tests.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from Shared.tools import question_difficulty, question_review_matrix

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "TEST/imo-qrt-repair/five_factor_blueprint_proof_28.v1.json"
KEYS = question_difficulty.COMPONENT_KEYS


def git_blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + bytes((0,)) + payload).hexdigest()


class BlueprintProof28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.items = {}
        cls.docs = {}
        for source in cls.ledger["source_files"]:
            payload = (ROOT / source["path"]).read_bytes()
            if git_blob_sha(payload) != source["blob_sha"]:
                raise AssertionError("SOURCE_DRIFT: " + source["path"])
            if source["path"].endswith(".core2.json"):
                source_json = json.loads(payload.decode("utf-8"))
                for question in source_json["questions"]:
                    if question["id"] in cls.items:
                        raise AssertionError("DUPLICATED_SOURCE_QUESTION: " + question["id"])
                    cls.items[question["id"]] = (source["path"], question)
            else:
                cls.docs[source["path"]] = payload.decode("utf-8")

        cls.meta = question_difficulty.metadata()
        cls.component_anchors = cls.meta["question_difficulty_component_rubric"]["components"]
        cls.matrix = question_review_matrix.load(question_review_matrix.MATRIX_PATH)
        cls.vocab = question_review_matrix.load(question_review_matrix.VOCAB_PATH)
        cls.templates = {
            row["template_id"]: row
            for row in question_review_matrix.compile_templates(cls.matrix, cls.vocab)
        }

    def test_denominator_source_pin_and_proof_status(self):
        ledger = self.ledger
        self.assertEqual(ledger["schema"], "imo-qrt-blueprint-proof/v1")
        self.assertEqual(ledger["source_commit"], "90c859705feb0dfcedc6d33a013d9e563b7cac9d")
        self.assertEqual(len(ledger["records"]), 28)
        self.assertEqual({r["packet"] for r in ledger["records"]}, {"3", "4"})
        self.assertEqual(
            {packet: sum(r["packet"] == packet for r in ledger["records"]) for packet in ("3", "4")},
            {"3": 13, "4": 15},
        )
        self.assertEqual(len({r["id"] for r in ledger["records"]}), 28)
        self.assertEqual(ledger["summary"]["score_differences"], 27)
        self.assertEqual(ledger["summary"]["invalid_factor"], 1)
        self.assertEqual(ledger["summary"]["overlapping_band_differences"], 6)
        for verdict in ("PROVEN", "UNPROVEN"):
            self.assertEqual(
                sum(r["result"] == verdict for r in ledger["records"]),
                ledger["summary"][verdict.lower()],
            )
        self.assertEqual(len(self.templates), 28)
        self.assertEqual(len(self.docs), 6)
        self.assertIn("Core2 is a preservation product", self.docs["Shared/roles/CORE2.md"])
        self.assertIn("familiar question-family demand", self.docs["Shared/roles/CORE2A.md"])
        self.assertIn("specified changed demand", self.docs["Shared/roles/CORE2B.md"])

    def test_every_anchor_and_exact_source_quote(self):
        for row in self.ledger["records"]:
            with self.subTest(id=row["id"]):
                file, question = self.items[row["id"]]
                classification = question["cognitive_classification"]
                self.assertEqual(row["source_file"], file)
                self.assertEqual(row["stored"], {
                    "score": classification["difficulty_score"],
                    "band": classification["difficulty_band"],
                    "qrt_cell": classification["qrt_cell"],
                    "primary_demand": classification["primary_demand"],
                    "components": classification["difficulty_components"],
                })
                self.assertEqual(len(row["factor_proofs"]), 5)
                self.assertEqual(tuple(f["key"] for f in row["factor_proofs"]), KEYS)
                for factor in row["factor_proofs"]:
                    with self.subTest(factor=factor["key"]):
                        key = factor["key"]
                        val = factor["proposed_value"]
                        self.assertIs(type(val), int)
                        self.assertIn(val, (0, 1, 2))
                        self.assertEqual(row["proposed"]["components"][key], val)
                        self.assertEqual(
                            factor["exact_rubric_anchor"],
                            self.component_anchors[key]["anchors"][str(val)],
                        )
                        passage = (
                            question["stem"]
                            if factor["evidence_source"] == "stem"
                            else (
                                question["solution"]["derivation"]
                                if isinstance(question.get("solution"), dict)
                                else question["solution"]
                            )
                        )
                        self.assertGreater(len(factor["exact_source_quote"]), 15)
                        self.assertIn(factor["exact_source_quote"], passage)
                        self.assertGreater(len(factor["justification"]), 20)
                        self.assertIn(factor["status"], ("SUPPORTED", "UNPROVEN", "REVIEW_REQUIRED"))

    def test_canonical_score_band_and_matrix_cell(self):
        changed_bands = 0
        observed_band_mismatches = 0
        source_invalid = 0
        for row in self.ledger["records"]:
            with self.subTest(id=row["id"]):
                s, p = row["stored"], row["proposed"]
                derived = question_difficulty.derive({
                    "components": p["components"], "score": p["score"], "band": p["band"],
                }, question_ref=row["id"])
                self.assertEqual((derived["score"], derived["band"]), (p["score"], p["band"]))
                self.assertEqual(p["qrt_cell"], f"QRT-{s['primary_demand']}-{p['band']}")
                self.assertIn(p["qrt_cell"], self.templates)
                template = self.templates[p["qrt_cell"]]
                self.assertEqual(row["qrt_blueprint"]["decisive_act_quote"], self.matrix["demands"][s["primary_demand"]]["decisive_act"])
                self.assertEqual(row["qrt_blueprint"]["protected_work_quote"], self.matrix["band_policies"][p["band"]]["protected_work"])
                self.assertEqual((template["demand"], template["band"]), (s["primary_demand"], p["band"]))
                self.assertEqual(template["band_policy"]["protected_work"], row["qrt_blueprint"]["protected_work_quote"])
                self.assertEqual(row["qrt_blueprint"]["current_cell"], s["qrt_cell"])
                self.assertEqual(row["qrt_blueprint"]["proposed_cell"], p["qrt_cell"])
                transition = "STAYS" if s["qrt_cell"] == p["qrt_cell"] else "MUST_MOVE"
                self.assertEqual(row["qrt_blueprint"]["cell_transition"], transition)
                changed_bands += transition == "MUST_MOVE"
                if any(type(v) is not int or not 0 <= v <= 2 for v in s["components"].values()):
                    source_invalid += 1
                    with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "COMPONENT_INVALID"):
                        question_difficulty.derive({
                            "components": s["components"], "score": s["score"], "band": s["band"]
                        }, question_ref=row["id"])
                else:
                    projected_source = sum(s["components"].values())
                    observed_band_mismatches += question_difficulty.band_for_score(projected_source) != s["band"]
                    with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "SCORE_MISMATCH"):
                        question_difficulty.derive({
                            "components": s["components"], "score": s["score"], "band": s["band"]
                        }, question_ref=row["id"])
        self.assertEqual(observed_band_mismatches, 6)
        self.assertEqual(source_invalid, 1)
        self.assertEqual(changed_bands, sum(r["qrt_blueprint"]["cell_transition"] == "MUST_MOVE" for r in self.ledger["records"]))

    def test_blueprint_role_and_undecided_holds_are_not_promoted(self):
        for row in self.ledger["records"]:
            with self.subTest(id=row["id"]):
                role = row["core_blueprint"]
                self.assertEqual(role["custody_role"], "CORE2_RESEARCH_CANDIDATE_UNADMITTED")
                self.assertEqual(role["application_role"], "CORE2A_FAMILIAR_ROUTE_CANDIDATE")
                self.assertEqual(role["transfer_role"], "CORE2B_NOT_SHOWN_NO_PRIOR_EXPOSURE_OR_CHANGED_DEMAND")
                self.assertEqual(role["crux_quote"], self.items[row["id"]][1]["cognitive_classification"]["crux_move"])
                if row["result"] == "PROVEN":
                    self.assertEqual(row["decisive_issue"], "all_five")
                    self.assertEqual(row["qrt_blueprint"]["semantic_gate"], "SUPPORT_CANDIDATE_ONLY")
                    self.assertTrue(all(f["status"] == "SUPPORTED" for f in row["factor_proofs"]))
                else:
                    self.assertEqual(row["result"], "UNPROVEN")
                    self.assertNotEqual(row["decisive_issue"], "all_five")
                    self.assertEqual(row["qrt_blueprint"]["semantic_gate"], "UNPROVEN")
                    self.assertTrue(any(f["status"] != "SUPPORTED" for f in row["factor_proofs"]))

    def test_falsification_controls_reject_wrong_projection_and_bad_anchor(self):
        row = self.ledger["records"][0]
        legitimate = row["proposed"]
        self.assertEqual(question_difficulty.derive({
            "components": legitimate["components"], "score": legitimate["score"], "band": legitimate["band"]
        })["score"], legitimate["score"])
        with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "SCORE_MISMATCH"):
            question_difficulty.derive({
                "components": legitimate["components"], "score": legitimate["score"] + 1, "band": legitimate["band"]
            })
        wrong_band = "D2" if legitimate["band"] != "D2" else "D1"
        with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "BAND_MISMATCH"):
            question_difficulty.derive({
                "components": legitimate["components"], "score": legitimate["score"], "band": wrong_band
            })
        with self.assertRaisesRegex(question_difficulty.DifficultyContractError, "COMPONENT_INVALID"):
            question_difficulty.derive({
                "components": {**legitimate["components"], "algebra_computational_load": 3},
                "score": legitimate["score"], "band": legitimate["band"],
            })
        factor = row["factor_proofs"][0]
        self.assertNotEqual(
            factor["exact_rubric_anchor"] + " CORRUPTED",
            self.component_anchors[factor["key"]]["anchors"][str(factor["proposed_value"])],
        )


if __name__ == "__main__":
    unittest.main()
