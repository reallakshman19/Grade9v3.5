"""Proof falsifiers and governance holds for an alternative JUSTIFY-D3 authored trial.

This is deliberately not a Core2A page, a publisher source item, an Owner-
accepted QRT template, or a substitute for independent mathematics review.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET


REPO = Path(__file__).resolve().parents[1]
PROPOSAL = REPO / "TEST/imo-research/pilots/justify-d3-boundary-24.authored-proposal.v1.json"
INHERITED = REPO / "TEST/imo-research/pilots/core1a-qrt-justify-d3-authored.v1.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def p(n: int) -> int:
    return n * (n + 1) * (n + 2)


def q(n: int) -> int:
    return p(n) * (n + 3)


class Boundary24Trial(unittest.TestCase):
    def setUp(self):
        self.trial = read(PROPOSAL)

    def test_authored_distinct_from_d2_and_original_001_and_not_released(self):
        trial, package = self.trial, read(INHERITED)
        ids = {row["id"] for row in package["questions"]}
        self.assertNotIn(trial["question_id"], ids)
        self.assertIn("Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF", ids)
        self.assertIn("Q-TEST-IMO-G9-AUTHORED-001-JUSTIFY-D3", ids)
        self.assertEqual(trial["origin"], "AUTHORED_NEW_UNPUBLISHED_NOT_SOF")
        self.assertEqual(trial["status"], "RESEARCH_TRIAL_NOT_ADMITTED")
        self.assertFalse(trial["source_core2_admitted"])
        self.assertFalse(trial["core_learner_published"])
        self.assertFalse(trial["qrt_owner_accepted"])
        self.assertEqual(trial["band"], "D3_PROPOSED_NOT_CONFIRMED")
        self.assertNotIn("SOF-IMO-G09-", json.dumps(trial))
        self.assertEqual(trial["navigation_hold"]["route_status"],
                         "NO_PUBLIC_ROUTE_PENDING_ACADEMIC_SUBTOPIC_CLASSIFICATION")
        self.assertNotEqual(trial["navigation_hold"]["not_equal_to"], "")
        self.assertEqual(trial["navigation_hold"]["no_misfile_under"], "POLY-DIVISIBILITY")

    def test_new_mathematical_decisions_are_not_a_relabelled_d2_proof(self):
        t = self.trial
        compare = t["existing_d2_comparison"]
        self.assertEqual(compare["old_question_id"],
                         "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF")
        self.assertTrue(any("counterexample" in x.lower()
                            for x in compare["learner_owned_new_work"]))
        self.assertTrue(any("classif" in x.lower()
                            for x in compare["learner_owned_new_work"]))
        self.assertTrue(any("distinct" in x.lower()
                            for x in compare["learner_owned_new_work"]))
        self.assertFalse(compare["accepted_by_reviewer"])
        self.assertIn("classification", t["stem"].lower())
        self.assertIn("24", t["stem"])
        self.assertIn("12", t["stem"])
        self.assertIn("P(n)", t["stem"])
        self.assertIn("Q(n)", t["stem"])

    def test_a_universal_claim_is_false_and_counterexample_is_real(self):
        answer = self.trial["answer_for_review_only"]
        self.assertFalse(answer["a_universal"])
        witness = answer["a_counterexample"]["n"]
        self.assertEqual(witness, 1)
        self.assertEqual(p(witness), answer["a_counterexample"]["p"])
        self.assertEqual(p(witness) % 12, 6)
        self.assertEqual(answer["a_counterexample"]["not_divisible_by"], 12)
        # A single witness disproves a universal claim but never proves
        # the separate iff classification, which needs exhaustive classes.
        self.assertTrue(all(p(n) % 6 == 0 for n in range(1, 200)))

    def test_exact_if_and_only_if_classification_for_twelve(self):
        condition = self.trial["answer_for_review_only"]["a_exact_classification"]
        self.assertEqual(condition["holds_iff"], "n % 4 != 1")
        self.assertEqual(condition["exception_class"], "n ≡ 1 (mod 4)")
        # P(n) mod 12 depends on n mod 12, so these twelve classes are
        # exhaustive for every positive n; this is not finite sampling.
        for residue in range(12):
            self.assertEqual(p(residue) % 12 == 0, residue % 4 != 1,
                             f"residue {residue}")
        for n in range(1, 601):
            self.assertEqual(p(n) % 12 == 0, n % 4 != 1, n)
        # The exact obstruction is missing a second factor of 2, not 3.
        for residue in range(4):
            terms = (residue, residue + 1, residue + 2)
            self.assertEqual(any(v % 4 == 0 for v in terms)
                             or sum(v % 2 == 0 for v in terms) >= 2,
                             residue != 1)

    def test_four_consecutive_product_always_multiple_of_twenty_four(self):
        answer = self.trial["answer_for_review_only"]
        self.assertTrue(answer["b_universal"])
        # q(n) mod 24 depends on n mod 24, so this cycle covers ALL n.
        for residue in range(24):
            self.assertEqual(q(residue) % 24, 0, residue)
        for n in range(1, 601):
            self.assertEqual(q(n) % 24, 0, n)
            four = [n, n + 1, n + 2, n + 3]
            multiple_of_four = next(x for x in four if x % 4 == 0)
            self.assertTrue(any(x != multiple_of_four and x % 2 == 0
                                for x in four), n)
            self.assertTrue(any(x % 3 == 0 for x in four), n)
        warrant = " ".join(answer["b_general_warrant"]).lower()
        self.assertIn("distinct", warrant)
        self.assertIn("gcd(8,3)=1", warrant)

    def test_preattempt_hints_do_not_announce_truth_values_or_the_new_bridge(self):
        t = self.trial
        hints = t["pre_attempt_support"]
        self.assertEqual([x["id"] for x in hints], ["H1", "H2", "H3"])
        combined = " ".join(x["text"] for x in hints).lower()
        for leak in ("n ≡ 1", "n % 4 != 1", "q(n) is always",
                     "a is false", "8 divides", "distinct even"):
            self.assertNotIn(leak, combined)
        differentiators = " ".join(
            t["existing_d2_comparison"]["learner_owned_new_work"]).lower()
        self.assertIn("distinct", differentiators)
        self.assertIn("8-divisibility", differentiators)
        self.assertIn("independently decide", t["protected_work"].lower())

    def test_authored_staged_figure_matches_both_claims_without_answer_leak(self):
        figure = self.trial["pre_attempt_representation"]
        self.assertEqual(figure["status"], "AUTHOR_SOURCE_SAFE_REVIEW_ASSET_NOT_LIVE")
        self.assertFalse(figure["owner_acceptance"])
        self.assertEqual(figure["stage_mode"], "REPLACE")
        self.assertIn("NOT_YET_REVIEWED", figure["accessibility_status"])
        path = REPO / figure["asset_ref"]
        svg_text = path.read_text(encoding="utf-8")
        root = ET.fromstring(svg_text)
        stages = [g.attrib["data-g9-stage-id"]
                  for g in root.iter()
                  if "data-g9-stage-id" in g.attrib]
        self.assertEqual(stages, figure["stage_refs"])
        self.assertEqual(len(stages), 3)
        self.assertIn("n + 3", svg_text)
        self.assertIn("24 divides Q(n)", svg_text)
        self.assertIn("12 divides P(n)", svg_text)
        title = next(child.text for child in root
                     if child.tag.endswith("title"))
        self.assertIn("Authored boundary transfer", title)
        for forbidden in ("n ≡ 1", "n % 4 != 1", "8 divides Q",
                          "claim a is false", "claim b is true",
                          "gcd(8,3)=1", "factor of 4 and another even"):
            self.assertNotIn(forbidden.lower(), svg_text.lower())

    def test_every_review_slot_is_explicitly_not_accepted(self):
        t = self.trial
        self.assertEqual(set(t["review_matrix"]),
                         {"H1", "H2", "H3", "S1", "S2", "S3",
                          "P1", "P2", "P3", "M1", "M2", "M3"})
        for slot in t["review_matrix"].values():
            self.assertEqual(slot["review_state"], "NOT_ACCEPTED")
            self.assertFalse(slot["owner_acceptance"])
            self.assertEqual(slot["evidence_status"], "AWAITING_INDEPENDENT_REVIEW")
        self.assertIn("independent", " ".join(t["acceptance_gates"]).lower())


if __name__ == "__main__":
    unittest.main()
