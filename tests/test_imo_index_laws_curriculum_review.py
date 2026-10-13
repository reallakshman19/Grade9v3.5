"""Fail-closed academic domain scoping and source-role checks for the reviewer packet."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "TEST/imo-research/intake/imo-index-laws-core1a-curriculum-review-2026-27.v1.json"
EXISTING = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.test.manifest.json"
STAGED = ROOT / "TEST/imo-research/intake/imo-index-laws-route-staging.v1.json"
F01 = ROOT / "TEST/imo-research/intake/imo-index-laws-subtopic-pilot.v1.json"
HANDOFF = ROOT / "TEST/imo-research/intake/imo-index-laws-core1a-curriculum-review-2026-27.md"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


class CurriculumReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = read(REVIEW)
        cls.old = read(EXISTING)
        cls.manifest = read(MANIFEST)
        cls.stage = read(STAGED)
        cls.f01 = read(F01)

    def test_real_domain_and_integer_domain_are_not_equated(self):
        self.assertEqual(self.r["candidate"]["current_domain"], "REAL_UNKNOWN")
        self.assertIn("For real x", self.old["questions"][0]["stem"])
        self.assertIn("for real y", self.old["microtopics"][0]["exit_task"]["prompt"])
        integer = next(x for x in self.r["alternatives"] if x["option"].startswith("B_"))
        self.assertIn("non-negative integer n", integer["worked_stem"])
        self.assertIn("non-negative integer m", integer["independent_exit_stem"])
        self.assertIn("continuous inverse", " ".join(integer["merits"]).lower())

    def test_the_original_exponential_solution_is_exact(self):
        # For non-negative integers, compare integer powers; no logarithm needed.
        solutions = [n for n in range(0, 25)
                     if 3**(2*n+1) == 9**n + 162]
        self.assertEqual(solutions, [2])
        self.assertEqual(3**5, 9**2 + 162)
        self.assertEqual(3 * 3**4, 3**4 + 162)

    def test_integer_exit_is_independent_and_checks_at_original_equation(self):
        self.assertEqual([m for m in range(0, 30)
                          if 2**(2*m+1) == 4**m + 64], [3])
        self.assertEqual(2**7, 4**3 + 64)
        self.assertNotEqual(self.old["questions"][0]["stem"],
                            self.old["microtopics"][0]["exit_task"]["prompt"])

    def test_boundary_probe_is_integer_unsatisfiable_but_real_satisfiable(self):
        # The shared quantity must equal 8, not an even-integer power of 2.
        self.assertEqual([m for m in range(0, 35)
                          if 2**(2*m+1) == 4**m + 8], [])
        self.assertAlmostEqual(2**(2*1.5+1), 4**1.5 + 8)
        self.assertEqual(4**1.5, 8.0)
        probe = next(x for x in self.r["alternatives"]
                     if x["option"].startswith("B_"))["discriminating_boundary_probe"]
        self.assertFalse(probe["preattempt_release_allowed"])
        self.assertIn("no integer m", probe["protected_solution_for_reviewer_only"])

    def test_mathematical_prerequisite_scope_is_explicit(self):
        claims = self.r["analytic_distinctions"]
        self.assertIn("strictly increasing", claims["real_domain_extra_warrant"])
        self.assertIn("real-range coverage", claims["real_domain_extra_warrant"])
        self.assertIn("integer n>=0", claims["natural_domain_warrant"])
        self.assertIn("changes the mathematical statement", claims["risk"])

    def test_primary_authorities_do_not_claim_curriculum_admission(self):
        sources = self.r["primary_curriculum_sources"]
        self.assertEqual([x["id"] for x in sources],
                         ["CBSE-IX-2025-26", "CBSE-IX-2026-27", "SOF-IMO-CLASS-9-SYLLABUS"])
        self.assertTrue(all(x["url"].startswith("https://") for x in sources))
        self.assertEqual(len({x["url"] for x in sources}), 3)
        self.assertIn("integral", sources[0]["observation"].lower())
        self.assertIn("does not explicitly list", sources[1]["observation"].lower())
        self.assertIn("powers", sources[1]["observation"].lower())
        self.assertIn("topic level", sources[2]["observation"].lower())
        self.assertTrue(all(x["does_not_prove"] for x in sources))
        self.assertEqual(self.r["candidate"]["curricular_claim"],
                         "CANNOT_AUTO_ASSERT_AS_GRADE9_CORE1A")

    def test_independent_reviewer_signoff_is_genuinely_absent(self):
        d = self.r["decision"]
        self.assertEqual(d["status"], "AWAITING_NAMED_INDEPENDENT_SUBJECT_REVIEW")
        for key in ("human_reviewer_name", "human_reviewer_role", "reviewed_at_utc",
                    "reviewer_verification_url", "written_justification",
                    "accepted_capability_id", "accepted_microtopic_id"):
            self.assertIsNone(d[key])
        self.assertEqual(set(d["choices"]), {"D1", "D2", "D3", "D4", "D5"})
        self.assertTrue(all(value is None for value in d["choices"].values()))
        for row in self.r["reviewer_required_decisions"]:
            self.assertIn(row["id"], d["choices"])
            self.assertGreater(len(row["allowed_decisions"]), 1)

    def test_authored_variants_are_not_selected_or_publicly_released(self):
        self.assertEqual(self.r["route_and_release"]["stage_a_route"],
                         "mathematics/number-systems/index-laws/index.html")
        self.assertFalse(self.r["route_and_release"]["release_allowed"])
        self.assertFalse(self.r["route_and_release"]["current_manifest_alternative_selected"])
        self.assertIsNone(self.r["route_and_release"]["approved_core1a_public_product_url"])
        self.assertIsNone(self.r["route_and_release"]["named_owner_release_decision"])
        self.assertEqual(self.manifest["selection"]["core2a"], [])
        self.assertEqual(self.manifest["output_roles"], ["CORE1A"])
        self.assertEqual(self.stage["status"], "DRAFT_NAVIGATION_STAGED_ACADEMIC_HOLD")
        self.assertFalse(self.stage["core1a"]["canonical_accepted"])
        self.assertIsNone(self.stage["core1a"]["public_product_url"])
        self.assertEqual(self.f01["scope"]["subtopic_status"], "PROVISIONAL_FROM_ATTACHMENT")
        self.assertFalse(self.f01["scope"]["launch_authorized"])

    def test_authentic_soe_core2_rights_and_qrt_still_not_admitted(self):
        hold = self.r["route_and_release"]
        self.assertEqual(hold["rights_and_source_core2_admitted"], 0)
        self.assertEqual(hold["source_positions_held"], 68)
        self.assertEqual(hold["qrt_owner_accepted"], 0)
        self.assertTrue(hold["no_merge_or_publish_from_review_packet"])
        self.assertTrue(all(not s["source_core2_admitted"]
                            for s in self.f01["source_questions"]))
        self.assertEqual(self.r["document_kind"],
                         "INDEPENDENT_ACADEMIC_REVIEW_PACKET_NOT_APPROVAL")
        self.assertEqual(self.r["decision"]["reviewed_at_utc"], None)

    def test_reviewer_handoff_is_linked_and_does_not_distribute_source_paper(self):
        s = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("AWAITING NAMED INDEPENDENT SUBJECT REVIEW", s)
        self.assertIn("CBSE 2025", s)
        self.assertIn("CBSE 2026", s)
        self.assertIn("SOF Class 9", s)
        self.assertIn("0 authentic Core2 admissions", s)
        self.assertIn("D1", s)
        self.assertIn("D5", s)
        self.assertNotIn("SOF-IMO-G09-L1-2024-25-B-Q026", s)


if __name__ == "__main__":
    unittest.main()
