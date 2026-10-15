"""Bounded false-pass controls for HOTS academic HOLD classification (synthetic)."""
import copy
import unittest

from Shared.tools.imo_qrt_hots_review import inspect, TARGETS

SHA = "a" * 40
DIGEST = "b" * 64


def sample():
    return [
        {
            "id": TARGETS[0],
            "stem": "In any general five-pointed star, find the total tip angle.",
            "figure_ref": None,
            "solution": {
                "derivation": "The nondegenerate convex pentagram turns twice."
            },
            "cognitive_classification": {
                "primary_demand": "JUSTIFY", "difficulty_band": "D4",
                "qrt_cell": "QRT-JUSTIFY-D4", "crux_move": "Show the turn invariant."
            },
        },
        {
            "id": TARGETS[1],
            "stem": "A cyclic quadrilateral has four sides; find diagonal product.",
            "figure_ref": None,
            "solution": {"derivation": "Use Ptolemy and substitute."},
            "cognitive_classification": {
                "primary_demand": "SYNTHESIZE", "difficulty_band": "D4",
                "qrt_cell": "QRT-SYNTHESIZE-D4",
                "crux_move": "Apply Ptolemy to the four sides."
            },
        },
    ]


def examine(rows):
    return inspect(rows, source_sha256=DIGEST, source_commit=SHA)


class AcademicHoldControls(unittest.TestCase):
    def test_qualified_star_argument_is_not_universal_source_proof(self):
        r = examine(sample())
        q = r["cases"][0]
        self.assertEqual(q["status"], "REVIEW_REQUIRED")
        self.assertTrue(q["evidence"]["broad_claim_in_stem"])
        self.assertTrue(q["evidence"]["bounded_warrant_declared"])
        self.assertFalse(q["evidence"]["authoritative_source_diagram_verified"])
        self.assertIn("Q024_BROAD_STEM_VS_BOUNDED_WARRANT", {f["code"] for f in q["findings"]})
        self.assertEqual(r["academic_approval"], "NOT_GRANTED")

    def test_qualified_proof_absent_still_held(self):
        rows = sample()
        rows[0]["solution"]["derivation"] = "In a regular example, sum is 180."
        q = examine(rows)["cases"][0]
        self.assertIn("Q024_PROOF_DOMAIN_QUALIFICATION_NOT_EVIDENCED",
                      {f["code"] for f in q["findings"]})
        self.assertEqual(q["academic_verdict"], "REVIEW_REQUIRED")

    def test_missing_authored_figure_is_a_source_hold_not_fake_svg(self):
        rows = sample()
        rows[0]["figure_ref"] = "synthetic.svg"
        q = examine(rows)["cases"][0]
        self.assertTrue(q["evidence"]["figure_reference_declared"])
        self.assertFalse(q["evidence"]["authoritative_source_diagram_verified"])
        self.assertIn("Q024_ORIGINAL_SOURCE_DIAGRAM_AND_SCOPE_UNVERIFIED",
                      {f["code"] for f in q["findings"]})

    def test_ptolemy_application_conflict_does_not_relabel(self):
        rows = sample()
        q = examine(rows)["cases"][1]
        self.assertTrue(q["evidence"]["direct_ptolemy_application_cue"])
        self.assertEqual(q["evidence"]["declared_cell"], "QRT-SYNTHESIZE-D4")
        self.assertFalse(q["evidence"]["classification_rewritten"])
        self.assertIn("Q035_APPLY_LANGUAGE_VS_SYNTHESIZE_PROPOSAL",
                      {f["code"] for f in q["findings"]})
        self.assertEqual(q["academic_verdict"], "REVIEW_REQUIRED")

    def test_fabricated_factors_cannot_claim_qrt_acceptance(self):
        rows = sample()
        rows[1]["cognitive_classification"]["difficulty_components"] = {
            "concept_model_selection": 2, "representation_translation": 2,
            "reasoning_chain_length": 2, "algebra_computational_load": 2,
            "trap_exception_sensitivity": 2,
        }
        result = examine(rows)
        self.assertTrue(result["cases"][1]["evidence"]["five_factor_object_complete"])
        self.assertEqual(result["qrt_classification_acceptance"], "NOT_GRANTED")
        self.assertEqual(result["cases"][1]["status"], "REVIEW_REQUIRED")

    def test_q035_relabel_requires_citation_not_auto_acceptance(self):
        rows = sample()
        cls = rows[1]["cognitive_classification"]
        cls["primary_demand"] = "APPLY"
        cls["qrt_cell"] = "QRT-APPLY-D4"
        q = examine(rows)["cases"][1]
        self.assertIn("Q035_CHANGED_CLASSIFICATION_NEEDS_CITED_ACCEPTANCE",
                      {f["code"] for f in q["findings"]})
        self.assertEqual(q["evidence"]["declared_demand"], "APPLY")
        self.assertEqual(q["status"], "REVIEW_REQUIRED")

    def test_missing_critical_question_fails_closed(self):
        r = examine(sample()[:1])
        self.assertEqual(r["status"], "FAIL")
        self.assertEqual(r["cases"][1]["findings"][0]["code"], "HOTS_TARGET_QUESTION_MISSING")

    def test_missing_reasoning_and_bad_qrttile_are_failures(self):
        rows = sample()
        rows[0]["solution"]["derivation"] = ""
        rows[1]["cognitive_classification"]["qrt_cell"] = "QRT-APPLY-D1"
        r = examine(rows)
        self.assertEqual(r["status"], "FAIL")
        self.assertIn("HOTS_STEM_OR_REASONING_MISSING",
                      {f["code"] for f in r["cases"][0]["findings"]})
        self.assertIn("HOTS_DECLARED_QRT_INCONSISTENT",
                      {f["code"] for f in r["cases"][1]["findings"]})

    def test_sha_and_duplicate_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "EXACT_SOURCE_COMMIT"):
            inspect(sample(), source_sha256=DIGEST, source_commit="main")
        with self.assertRaisesRegex(ValueError, "DUPLICATE_QUESTION_ID"):
            examine(sample() + [copy.deepcopy(sample()[0])])


if __name__ == "__main__":
    unittest.main()
