"""R1: real authored JUSTIFY-D3 Core2A + existing Core1A, matrix/blueprint first.

These checks are about actual canonical-shaped content and renderer output, not
a publisher source Core2 claim or a declaration that QRT D3 has been accepted.
"""
from __future__ import annotations

import copy
import json
import re
import unittest
from html.parser import HTMLParser
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


class PreAttemptVisibleText(HTMLParser):
    """Browser-visible text excludes inert solution/rung templates and JS/CSS."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden_depth = 0
        self.script_depth = 0
        self.visible = []
        self.protected = []

    def handle_starttag(self, tag, attrs):
        if tag == "template":
            self.hidden_depth += 1
        if tag in ("script", "style"):
            self.script_depth += 1

    def handle_endtag(self, tag):
        if tag == "template":
            self.hidden_depth -= 1
        if tag in ("script", "style"):
            self.script_depth -= 1

    def handle_data(self, value):
        if self.script_depth:
            return
        (self.protected if self.hidden_depth else self.visible).append(value)


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
        self.assertEqual(manifest["output_roles"], ["CORE2A", "CORE1A"])
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
        self.assertEqual([stage["id"] for stage in rep["reveal_stages"]],
                         ["AUTHORED-001-FACTORS-ONLY", "AUTHORED-001-PARITY-OBSERVE",
                          "AUTHORED-001-RESIDUES-OBSERVE"])
        self.assertEqual(rep["scene_instances"][0]["datum_refs"],
                         ["DATUM-TEST-IMO-G9-AUTHORED-001-FACTORS"])
        datum = next(x for x in pkg["data"] if x["id"] ==
                     rep["scene_instances"][0]["datum_refs"][0])
        self.assertEqual(datum["symbol"], "n(n+1)(n+2)")
        asset = ROOT / rep["rendered_asset_refs"][0]
        svg = asset.read_text(encoding="utf-8")
        self.assertIn("AUTHORED-001-FACTORS-ONLY", svg)
        self.assertEqual(svg.count("data-g9-stage-id="), 3)
        self.assertIn("AUTHORED-001-PARITY-OBSERVE", svg)
        self.assertIn("AUTHORED-001-RESIDUES-OBSERVE", svg)
        self.assertIn(">n</text>", svg)
        self.assertIn(">n + 1</text>", svg)
        self.assertIn(">n + 2</text>", svg)
        self.assertNotIn(">m + 1</text>", svg)
        self.assertNotIn(">m + 2</text>", svg)
        self.assertNotIn(">m + 3</text>", svg)
        self.assertNotIn("gcd", svg.lower())
        self.assertNotIn("even factor", svg.lower())
        self.assertNotIn("multiple of three", svg.lower())
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
        self.assertTrue(all(v["review_state"] == "NOT_ACCEPTED" and
                            v["owner_acceptance"] is False and
                            len(v["observed_behavior"]) > 40
                            for v in mark["matrix_slots"].values()))
        self.assertEqual(mark["semantic_coverage"]["remaining_gaps"], [])
        self.assertEqual(mark["semantic_coverage"]["supported_candidate_slots"], 12)
        self.assertEqual(mark["semantic_coverage"]["owner_accepted_slots"], 0)
        self.assertEqual(
            [name for name, row in mark["matrix_slots"].items()
             if row["evidence_status"] == "GAP_NOT_IMPLEMENTED"], [])
        self.assertEqual(mark["learning_sequence"],
                         "AUTHOR_DIAGNOSTIC_ATTEMPT_FIRST_THEN_OPTIONAL_CORE1A_REPAIR")
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
        # W is the question-specific decisive action; the generic D3 policy
        # governs what scaffolds may expose, but is not literal W wording.
        self.assertEqual(review["slots"]["W"]["text"],
                         next(move["action"] for move in q["answer"]["reasoning_route"]
                              if move["id"] == q["answer"]["crux_move_ref"]))
        self.assertEqual(q["extensions"][REVIEW]["protected_work"],
                         matrix["band_policies"]["D3"]["protected_work"])

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
                         ["AUTHORED-001-FACTORS-ONLY", "AUTHORED-001-PARITY-OBSERVE",
                          "AUTHORED-001-RESIDUES-OBSERVE"])

    def test_qrt_m2_candidate_is_implemented_but_not_accepted(self):
        _, _, _, q = snapshot()
        evidence = q["extensions"][REVIEW]
        self.assertEqual(evidence["semantic_coverage"]["governing_asks_total"], 12)
        self.assertEqual(evidence["semantic_coverage"]["owner_accepted_slots"], 0)
        self.assertEqual(evidence["semantic_coverage"]["remaining_gaps"], [])
        self.assertIn("may collapse to recall",
                      evidence["semantic_coverage"]["risk"].lower().replace("_", " "))
        self.assertEqual(evidence["matrix_slots"]["M2"]["evidence_status"],
                         "SUPPORTED_CANDIDATE")
        self.assertEqual(evidence["matrix_slots"]["M2"]["review_state"],
                         "NOT_ACCEPTED")
        self.assertFalse(evidence["matrix_slots"]["M2"]["owner_acceptance"])
        self.assertIn("NOT YET VERIFIED",
                      evidence["semantic_coverage"]["evidence_limit"])

    def test_question_attempt_first_without_prelesson_proof_or_visual_leaks(self):
        pkg, manifest, _, q = snapshot()
        self.assertEqual(manifest["output_roles"][0], "CORE2A")
        self.assertEqual(len(q["scaffolds"]), 3)
        self.assertEqual(len(q["answer"]["reasoning_route"]), 5)
        self.assertEqual(q["answer"]["crux_move_ref"],
                         q["answer"]["reasoning_route"][3]["id"])
        rep = next(x for x in pkg["representations"]
                   if x["id"] == q["representation_roles"]["initial_ref"])
        svg = (ROOT / rep["rendered_asset_refs"][0]).read_text(encoding="utf-8")
        forbidden = ("even factor", "multiple of three", "factor of 2",
                     "divisible by 6", "the claim is true", "gcd")
        for item in forbidden:
            self.assertNotIn(item, svg.lower(), item)
        self.assertEqual(rep["reveal_stages"][0]["visible_elements"],
                         ["n,n+1,n+2"])

    def test_three_learner_stages_protect_qrt_d3_warrant(self):
        pkg, _, _, q = snapshot()
        rep = next(row for row in pkg["representations"] if row["id"] ==
                   q["representation_roles"]["initial_ref"])
        stages = rep["reveal_stages"]
        self.assertEqual(len(stages), 3)
        self.assertEqual(q["representation_roles"]["stage_refs"],
                         [stage["id"] for stage in stages])
        self.assertEqual(rep["extensions"]["grade9v3:stage_mode"], "REPLACE")
        self.assertIn("n,n+1,n+2", stages[0]["visible_elements"])
        self.assertIn("adjacent parity changes", stages[1]["visible_elements"])
        self.assertIn("n mod 3 in {0,1,2}", stages[2]["visible_elements"])
        text = " ".join(item["purpose"] for item in stages).lower()
        self.assertNotIn("gcd(2,3)", text)
        self.assertNotIn("6 divides", text)
        self.assertNotIn("claim is true", text)
        scores = q["extensions"][REVIEW]["matrix_slots"]
        self.assertEqual(scores["S1"]["evidence_status"], "SUPPORTED_CANDIDATE")
        self.assertEqual(scores["S2"]["evidence_status"], "SUPPORTED_CANDIDATE")
        self.assertEqual(scores["S3"]["evidence_status"], "SUPPORTED_CANDIDATE")
        self.assertEqual(scores["M2"]["evidence_status"], "SUPPORTED_CANDIDATE")
        self.assertTrue(all(score["owner_acceptance"] is False
                            for score in scores.values()))

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
        index_body = pages["index.html"].partition("<main>")[2].partition("</main>")[0]
        self.assertLess(index_body.find('href="core2a.html"'),
                        index_body.find('href="core1a.html"'))
        self.assertEqual(gaps, [], gaps)
        self.assertEqual(advice, [], advice)
        self.assertEqual(waivers, [], waivers)
        html = pages["core2a.html"]
        self.assertIn(q["id"], html)
        self.assertIn(q["stem"], html)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', html)
        self.assertIn('data-g9-print-layout="SINGLE_COLUMN_A4"', html)
        self.assertIn('article[data-g9-print-layout="SINGLE_COLUMN_A4"] .g9-split{display:block!important}', html)
        self.assertNotIn('data-g9-print-layout="SINGLE_COLUMN_A4"', pages["core1a.html"])
        self.assertIn("data-g9-attempt-box", html)
        self.assertIn("data-g9-commit", html)
        self.assertIn("data-requires-attempt", html)
        self.assertIn('data-g9-payload-ref="CORE2A-' + q["id"] + '-reasoning"', html)
        self.assertIn('<template data-g9-payload="CORE2A-' +
                      q["id"] + '-reasoning">', html)
        self.assertIn("AUTHORED", html)
        self.assertIn("core1a.html#CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF",
                      html)
        self.assertIn('data-g9-repair-ref="TC-03"', html)
        self.assertEqual(re.findall(
            r'<article\b[^>]*data-g9-role="([^"]+)"', html), ["CORE2A"])
        self.assertNotIn("SOF-IMO-G09-", html)
        self.assertIn("MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS",
                      pages["core1a.html"])

    def test_actual_render_keeps_proof_and_final_verdict_in_inert_template(self):
        _, _, _, q = snapshot()
        pages, gaps, _, _, _ = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(gaps, [], gaps)
        html = pages["core2a.html"]
        check = PreAttemptVisibleText()
        check.feed(html)
        check.close()
        visible = " ".join(check.visible)
        protected = " ".join(check.protected)
        # The learner sees the problem, may commit a free-response attempt,
        # and then chooses to inspect the reasoned proof in an inert template.
        self.assertIn(q["stem"], visible)
        self.assertNotIn(q["answer"]["summary"], visible)
        self.assertIn(q["answer"]["summary"], protected)
        self.assertNotIn("gcd(2,3)=1", visible)
        self.assertIn("gcd(2,3)=1", protected)
        self.assertNotIn("Claim true: 6 divides", visible)
        self.assertIn("data-g9-commit", html)
        self.assertIn("data-requires-attempt", html)
        self.assertIn('data-g9-payload-slot', html)


    def test_a4_print_preference_is_author_owned_and_scope_limited(self):
        pkg, _, _, q = snapshot()
        self.assertEqual(q["extensions"]["grade9v3:print_layout"],
                         "SINGLE_COLUMN_A4")
        other = [x for x in pkg["questions"] if x["id"] != q["id"]]
        self.assertTrue(all("grade9v3:print_layout" not in x.get("extensions", {})
                            for x in other))
        # A4 layout policy does not change the inherited canonical Core1A.
        self.assertEqual(pkg["microtopics"], load(BASE_PACKAGE)["microtopics"])

    def test_m2_probe_evidence_has_two_separate_signals_and_no_fake_grading(self):
        _, _, _, q = snapshot()
        probe = q["extensions"]["grade9v3:m2_probe"]
        self.assertEqual(probe["status"], "IMPLEMENTED_TEST_CANDIDATE_NOT_ACADEMICALLY_ACCEPTED")
        self.assertEqual([choice["id"] for choice in probe["reason_choices"]],
                         ["EXAMPLE_ONLY", "UNIVERSAL", "UNSURE"])
        self.assertEqual(probe["arithmetic_expected"], "120")
        self.assertEqual(probe["repair_ref"], q["repair_ref"])
        self.assertEqual(set(probe["feedback"]),
                         {"MISCONCEPTION", "SLIP", "NO_SIGNAL", "INCONCLUSIVE"})
        self.assertNotEqual(probe["feedback"]["MISCONCEPTION"], probe["feedback"]["SLIP"])
        self.assertIn("not grade", probe["feedback"]["NO_SIGNAL"].lower())
        self.assertIn("guessed selection", probe["limits"])

    def test_m2_probe_is_revealed_only_after_a_valid_attempt_in_runtime(self):
        _, _, _, q = snapshot()
        pages, gaps, _, _, _ = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(gaps, [], gaps)
        html = pages["core2a.html"]
        self.assertIn('data-g9-m2-probe hidden', html)
        self.assertIn('data-g9-m2-expected="120"', html)
        self.assertIn("data-g9-m2-reason", html)
        self.assertIn('data-g9-m2-arithmetic', html)
        self.assertIn('data-g9-m2-check', html)
        self.assertIn('role="status" aria-live="polite"', html)
        for key in ("MISCONCEPTION", "SLIP", "NO_SIGNAL", "INCONCLUSIVE"):
            self.assertIn('data-g9-m2-message="' + key + '"', html)
        self.assertIn('data-g9-repair-ref="TC-03"', html)
        self.assertIn('href="core1a.html#CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF"', html)
        self.assertIn("if(reason==='EXAMPLE_ONLY')outcome='MISCONCEPTION'", render_core.JS)
        self.assertIn("outcome=value===p.dataset.g9M2Expected?'NO_SIGNAL':'SLIP'",
                      render_core.JS)
        self.assertIn("const show=()=>{p.hidden=!a.dataset.attempted}", render_core.JS)
        # The diagnostic helps classify reasoning, but cannot claim to grade
        # the original free-response proof from a multiple-choice probe.
        self.assertNotIn("graded_correct", html)
        self.assertIn(q["stem"], html)

    def test_m2_malformed_evidence_fails_closed_as_render_gap(self):
        _, _, _, q = snapshot()
        invalid = copy.deepcopy(q)
        invalid["extensions"]["grade9v3:m2_probe"]["feedback"].pop("SLIP")
        ctx = render_core.Ctx(manifest={"product_id": "TEST-PROBE-BROKEN"},
                              packages=[load(PACKAGE)], bank=[], blueprints={})
        markup = render_core.authored_m2_probe(ctx, invalid)
        self.assertEqual(markup, "")
        self.assertEqual([gap["duty"] for gap in ctx.gaps], ["AUTHOR_M2_DIAGNOSTIC"])

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
