"""R1: real authored JUSTIFY-D3 Core2A + existing Core1A, matrix/blueprint first.

These checks are about actual canonical-shaped content and renderer output, not
a publisher source Core2 claim or a declaration that QRT D3 has been accepted.
"""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

from Shared.tools import (
    product_coverage, product_manifest, question_review_matrix as qrt, render_core
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "TEST/imo-research/pilots/core1a-qrt-justify-d3-authored.v1.json"
MANIFEST = ROOT / "TEST/products/imo-g9-authored-justify-d3-connected.manifest.json"
ORIGINAL = ROOT / "TEST/imo-research/original-practice/seven-cell-original-problems.v1.json"
BASE_PACKAGE = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
ID = "Q-TEST-IMO-G9-AUTHORED-001-JUSTIFY-D3"
REVIEW = "grade9v3:qrt_review"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot():
    pkg = load(PACKAGE)
    manifest = load(MANIFEST)
    authored = load(ORIGINAL)["records"][0]
    question = next(q for q in pkg["questions"] if q["id"] == ID)
    return pkg, manifest, authored, question


class MatrixFirstAuthoredD3CoreTests(unittest.TestCase):
    def test_actual_original_authored_question_reused_not_reinvented(self):
        pkg, manifest, authored, q = snapshot()
        self.assertEqual(authored["id"], "IMO-G9-ORIGINAL-PRACTICE-001")
        self.assertEqual(q["original_identifier"], authored["id"])
        self.assertEqual(q["stem"], authored["question_text"])
        self.assertEqual(q["answer"]["summary"], authored["expected_answer"])
        self.assertEqual(q["origin"], "AUTHORED")
        self.assertEqual(pkg["subject"], "TEST")
        self.assertEqual(pkg["status"], "CANDIDATE")
        self.assertNotIn("SOF-IMO-G09-", json.dumps(q))
        self.assertEqual(manifest["selection"]["core2"], [])
        self.assertEqual(manifest["bank_refs"], [])
        self.assertEqual(manifest["selection"]["core2a"], [ID])
        self.assertEqual(manifest["output_roles"], ["CORE1A", "CORE2A"])
        self.assertEqual(pkg["extensions"]["grade9v3:review_reset"]["source_sof_admitted"], 0)
        self.assertEqual(pkg["extensions"]["grade9v3:review_reset"]["qrt_accepted"], 0)

    def test_existing_core1a_construction_is_reused_unchanged(self):
        pkg, _, _, q = snapshot()
        original = load(BASE_PACKAGE)
        for field in ("resources", "buckets", "capabilities", "microtopics",
                      "relations", "teaching_routes"):
            self.assertEqual(pkg[field], original[field], field)
        # Preserve old Core1A/D2 representations; add one correctly authored
        # visual for the *different* n,n+1,n+2 question instead of borrowing
        # the old offset diagram for m+1,m+2,m+3.
        self.assertEqual(pkg["representations"][:len(original["representations"])],
                         original["representations"])
        self.assertEqual(pkg["data"][:len(original["data"])], original["data"])
        self.assertEqual(pkg["questions"][:2], original["questions"])
        self.assertEqual(q["primary_capability_ref"], original["capabilities"][0]["id"])
        self.assertIn(q["family_ref"],
                      [f["id"] for f in original["question_families"]])
        self.assertIn(q["id"], pkg["question_families"][0]["item_refs"])

    def test_real_svg_carries_exact_authored_n_triple_not_d2_m_offset(self):
        pkg, _, _, q = snapshot()
        rep = next(x for x in pkg["representations"] if x["id"] ==
                   q["representation_roles"]["initial_ref"])
        self.assertEqual(rep["scene_instances"][0]["question_ref"], q["id"])
        self.assertEqual(rep["correspondence"][0]["symbol"], "n(n+1)(n+2)")
        self.assertEqual(rep["reveal_stages"][0]["id"],
                         "AUTHORED-001-FACTORS-ONLY")
        self.assertEqual(rep["scene_instances"][0]["datum_refs"],
                         ["DATUM-TEST-IMO-G9-AUTHORED-001-FACTORS"])
        datum = next(x for x in pkg["data"] if x["id"] ==
                     rep["scene_instances"][0]["datum_refs"][0])
        self.assertEqual(datum["symbol"], "n(n+1)(n+2)")
        asset = ROOT / rep["rendered_asset_refs"][0]
        svg = asset.read_text(encoding="utf-8")
        self.assertIn("AUTHORED-001-FACTORS-ONLY", svg)
        self.assertIn(">n</text>", svg)
        self.assertIn(">n + 1</text>", svg)
        self.assertIn(">n + 2</text>", svg)
        self.assertNotIn(">m + 1</text>", svg)
        self.assertNotIn(">m + 2</text>", svg)
        self.assertNotIn(">m + 3</text>", svg)
        self.assertNotIn("gcd", svg.lower())
        self.assertNotIn("divisible by 6", svg.lower())
        self.assertIn("n plus two", svg.lower())
        self.assertEqual(q["figure_refs"], [rep["id"]])

    def test_one_primary_qrt_cell_from_all_28_real_canonical_templates(self):
        pkg, manifest, authored, q = snapshot()
        self.assertEqual(qrt.check_paths(), [])
        matrix, vocab = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
        generated = qrt.generated_payload(matrix, vocab)
        self.assertEqual(len(generated["templates"]), 28)
        self.assertEqual(
            {(row["demand"], row["band"]) for row in generated["templates"]},
            {(d, band) for d in qrt.DEMANDS for band in qrt.BANDS})
        self.assertEqual(q["difficulty"]["band"], "D3")
        self.assertEqual(q["difficulty"]["score"], 6)
        self.assertEqual(q["difficulty"]["components"],
                         authored["qrt_proposal"]["five_factor_scores"])
        self.assertEqual(sum(q["difficulty"]["components"].values()), 6)
        self.assertEqual(q["extensions"]["grade9v3:cognitive_demand"]["primary"], "JUSTIFY")
        mark = q["extensions"][REVIEW]
        self.assertEqual(mark["status"], "PROPOSED_RESEARCH_NOT_ACCEPTED")
        self.assertEqual(mark["template_id"], "QRT-JUSTIFY-D3")
        self.assertEqual(mark["protected_work"], matrix["band_policies"]["D3"]["protected_work"])
        self.assertEqual(set(mark["matrix_slots"]), set(qrt.ASKS))
        self.assertTrue(all(v["review_state"] == "NOT_ACCEPTED"
                            for v in mark["matrix_slots"].values()))
        self.assertEqual(len(manifest["selection"]["core2a"]), 1)
        self.assertNotEqual(mark["d2_contrast"], "")

    def test_canonical_qrt_engine_actually_resolves_justify_d3_and_crux(self):
        _, _, _, q = snapshot()
        matrix, vocab = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
        profile = {"profile_id": "TEST-SYNTHETIC-UNKNOWN",
                   "provenance": "SYNTHETIC_TEST_ONLY", "held": {}}
        review = qrt.resolve_review(q, profile, matrix, vocab)
        self.assertEqual(review["template_id"], "QRT-JUSTIFY-D3")
        self.assertEqual(review["classification"]["demand"]["primary"], "JUSTIFY")
        self.assertEqual(review["classification"]["band"], "D3")
        self.assertEqual(review["classification"]["difficulty_score"], 6)
        self.assertEqual(review["classification"]["demand"]["primary_move_ref"],
                         q["answer"]["crux_move_ref"])
        self.assertEqual(tuple(review["review"]), qrt.ASKS)
        self.assertIn(matrix["band_policies"]["D3"]["protected_work"],
                      review["slots"]["W"]["text"])

    def test_d3_is_not_an_unexplained_relabel_of_preexisting_d2(self):
        pkg, _, original, q = snapshot()
        d2 = next(x for x in pkg["questions"] if x["id"] ==
                  "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF")
        self.assertEqual(d2["difficulty"]["band"], "D2")
        self.assertEqual(d2["extensions"]["grade9v3:cognitive_demand"]["primary"], "JUSTIFY")
        self.assertIn("prove that", d2["stem"].lower())
        self.assertIn("prove or disprove", q["stem"].lower())
        self.assertNotEqual(d2["answer"]["crux_move_ref"], q["answer"]["crux_move_ref"])
        self.assertIn("truth-value decision",
                      q["extensions"][REVIEW]["d2_contrast"])
        self.assertEqual(original["qrt_proposal"]["cell"], "QRT-JUSTIFY-D3")
        self.assertFalse(original["core_2_ready"])
        # More difficult is a proposal awaiting subject review, not a theorem.
        self.assertIn("provisional", q["difficulty"]["basis"])

    def test_reasoning_route_warrants_and_protected_bridge_are_real(self):
        _, _, _, q = snapshot()
        route = q["answer"]["reasoning_route"]
        self.assertEqual([move["kind"] for move in route],
                         ["REPRESENT", "CONNECT", "CONNECT", "DECIDE", "VERIFY"])
        ids = [move["id"] for move in route]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(q["answer"]["crux_move_ref"], ids[3])
        self.assertTrue(all(move["action"] and move["why_valid"]
                            and move["output"] for move in route))
        self.assertTrue(all(move["action"] != move["why_valid"] for move in route))
        self.assertIn("gcd(2,3)=1", route[3]["why_valid"])
        self.assertIn("modulo 6", route[4]["action"])
        self.assertIn("every possible starting", route[4]["why_valid"])
        self.assertIn("finite", q["failure_signal"])

    def test_pre_attempt_authored_scaffolds_do_not_finish_proof(self):
        _, _, _, q = snapshot()
        self.assertEqual(len(q["scaffolds"]), 3)
        self.assertEqual(len(q["hint_ladder"]), 3)
        self.assertEqual(
            [row["order"] for row in q["hint_ladder"]], [1, 2, 3])
        self.assertTrue(all(row["provenance"] == "AUTHORED_SCAFFOLD"
                            for row in q["hint_ladder"]))
        hints = " ".join(s["text"].lower() for s in q["scaffolds"])
        # Neither the truth value nor the decisive final combined warrant is
        # supplied before an attempt.
        for forbidden in ("claim is true", "6 divides", "coprime",
                          "gcd(2,3)", "proof is complete", "always gives a multiple"):
            self.assertNotIn(forbidden, hints, forbidden)
        self.assertTrue(all(s["supports_move_ref"] in {
            x["id"] for x in q["answer"]["reasoning_route"]
        } for s in q["scaffolds"]))
        self.assertEqual(q["representation_roles"]["stage_refs"],
                         ["AUTHORED-001-FACTORS-ONLY"])

    def test_manifest_is_real_product_selection_with_explicit_d2_omission(self):
        pkg, manifest, _, _ = snapshot()
        selected = product_manifest.validate_selection(manifest, [pkg], [])
        self.assertEqual([q["id"] for q in selected["core2a"]], [ID])
        product_coverage.validate(manifest, product_manifest.derivable([pkg], []))
        self.assertIn("Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF",
                      manifest["coverage"]["omitted"])

    def test_wrong_band_or_dangling_crux_fails_real_qrt_engine(self):
        _, _, _, q = snapshot()
        matrix, vocab = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
        profile = {"profile_id": "TEST-SYNTHETIC-UNKNOWN", "held": {},
                   "provenance": "SYNTHETIC_TEST_ONLY"}
        false_band = copy.deepcopy(q)
        false_band["difficulty"]["band"] = "D2"
        with self.assertRaisesRegex(qrt.QRTContractError,
                                    "QUESTION_DIFFICULTY_BAND_MISMATCH"):
            qrt.resolve_review(false_band, profile, matrix, vocab)
        false_move = copy.deepcopy(q)
        false_move["answer"]["crux_move_ref"] = "FAKE-MOVE"
        with self.assertRaisesRegex(qrt.QRTContractError,
                                    "COGNITIVE_DEMAND_CRUX_MOVE_UNRESOLVED"):
            qrt.resolve_review(false_move, profile, matrix, vocab)

    def test_real_blueprint_renderer_builds_connected_two_role_pages(self):
        _, manifest, _, q = snapshot()
        pages, gaps, _, advice, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(set(pages), {"index.html", "core1a.html", "core2a.html"})
        self.assertEqual(gaps, [], gaps)
        self.assertEqual(advice, [], advice)
        self.assertEqual(waivers, [], waivers)
        html = pages["core2a.html"]
        self.assertIn(q["id"], html)
        self.assertIn(q["stem"], html)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', html)
        self.assertIn("AUTHORED", html)
        self.assertIn("core1a.html#CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF",
                      html)
        self.assertIn('data-g9-repair-ref="TC-03"', html)
        self.assertEqual(re.findall(
            r'<article\b[^>]*data-g9-role="([^"]+)"', html), ["CORE2A"])
        self.assertNotIn("SOF-IMO-G09-", html)
        self.assertIn("MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS",
                      pages["core1a.html"])

    def test_no_source_core2_or_learner_promotion_via_authored_render(self):
        pkg, manifest, _, q = snapshot()
        self.assertNotIn("CORE2", manifest["output_roles"])
        self.assertEqual(manifest["selection"]["core2"], [])
        self.assertFalse(pkg["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertFalse(pkg["extensions"]["grade9v3:learner_published"])
        self.assertFalse(pkg["extensions"]["grade9v3:qrt_admitted"])
        self.assertEqual(q["exposure"][0]["core"], "CORE2A")
        self.assertIsNone(q["adaptation"])
        self.assertEqual(q["origin"], "AUTHORED")
        self.assertFalse(any("SOF-IMO-G09-" in line
                             for line in q["answer"]["reasoning"]))


if __name__ == "__main__":
    unittest.main()
