"""Static contract checks for the QRT Blueprint Mapper custom agent.

These checks cannot establish the actual language model's academic competence;
run EVALUATION.md with an unseen question to assess that.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / ".github/agents/qrt-blueprint-mapper.agent.md"
A = ROOT / "agents/qrt-blueprint-mapper"


class BlueprintMapperAgentContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = PROFILE.read_text(encoding="utf-8")
        cls.playbook = (A / "PLAYBOOK.md").read_text(encoding="utf-8")
        cls.failures = (A / "FAILURE-CASES.md").read_text(encoding="utf-8")
        cls.evaluation = (A / "EVALUATION.md").read_text(encoding="utf-8")
        cls.template = json.loads((A / "EVIDENCE.template.json").read_text(encoding="utf-8"))

    def test_github_copilot_custom_agent_profile_format(self):
        self.assertTrue(self.profile.startswith("---\n"))
        parts = self.profile.split("---", 2)
        self.assertGreaterEqual(len(parts), 3)
        frontmatter, instructions = parts[1], parts[2]
        # Safe subset of documented YAML keys: no assumption of hidden agents.
        self.assertRegex(frontmatter, r"(?m)^name:\s*qrt-blueprint-mapper$")
        self.assertRegex(frontmatter, r"(?m)^description:\s*.+$")
        self.assertRegex(frontmatter, r"(?m)^tools:\s*\[")
        self.assertRegex(frontmatter, r"(?m)^user-invocable:\s*true$")
        self.assertRegex(frontmatter, r"(?m)^disable-model-invocation:\s*true$")
        self.assertLess(len(instructions), 30000)
        self.assertIn("agents/qrt-blueprint-mapper/PLAYBOOK.md", instructions)
        self.assertIn("agents/qrt-blueprint-mapper/FAILURE-CASES.md", instructions)

    def test_agent_reuses_actual_repository_contracts(self):
        for path in (
            "Shared/web/interactive-page-blueprints.v1.json",
            "Shared/quality/question-demand-matrix.v1.json",
            "Shared/quality/question-demand-templates.v1.json",
            "Shared/library/package.schema.json",
            "Shared/tools/render_core.py",
            "golden/INDEX.md",
            "golden/TECHNIQUES.md",
        ):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), f"Source contract missing: {path}")
                self.assertIn(path, self.profile + self.playbook)
        registry = json.loads((ROOT / "Shared/web/interactive-page-blueprints.v1.json").read_text())
        by_ref = {bp["id"]: bp["version"] for bp in registry["blueprints"]}
        for name in ("CORE1-ORIENTATION", "CORE1A-CONSTRUCTION", "CORE1B-RECONSTRUCTION",
                     "CORE2A-SUPPORTED-APPLICATION", "CORE2B-TRANSFER",
                     "CORE2-SOURCE-QUESTION"):
            self.assertTrue(any(name in bp for bp in by_ref), f"Missing native role {name}")

    def test_protected_work_and_fixture_semantics_explicit(self):
        for phrase in ("H1", "H2", "H3", "Core2B", "W", "render-receipt.json",
                       "index.html", "SHA-256", "T01", "T15",
                       "Owner", "qualified", "semantic"):
            self.assertIn(phrase, self.profile + self.playbook)
        self.assertIn("14px", self.failures)
        self.assertIn("cumulatively", self.failures)
        self.assertIn("SOURCE", self.profile.upper())
        self.assertIn("MODEL-D1", self.failures)
        self.assertIn("RETRIEVE-D1", self.failures)
        self.assertIn("SYNTHESIZE-D1", self.failures)
        self.assertIn("JUSTIFY-D1", self.failures)

    def test_evidence_template_cannot_pretend_unsigned_review_or_render(self):
        x = self.template
        self.assertEqual(x["schema"], "qrt-blueprint-mapper-evidence/v1")
        self.assertTrue(x["template"])
        self.assertEqual(x["status"], "NOT_RUN")
        self.assertEqual(x["qrt"]["primary_demand"], "UNCLASSIFIED")
        self.assertIsNone(x["qrt"]["W"])
        self.assertEqual({r["role"] for r in x["role_mapping"]},
                         {"CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"})
        self.assertFalse(x["core2_original_role"]["selected"])
        proof = x["evidence"]
        self.assertEqual(set(proof["six_page_sha256"]), {
            "core1.html", "core1a.html", "core1b.html",
            "core2a.html", "core2b.html", "index.html"})
        self.assertTrue(all(v is None for v in proof["six_page_sha256"].values()))
        self.assertFalse(proof["zero_gaps_verified"])
        self.assertFalse(proof["independent_sha_matches_receipt"])
        self.assertFalse(proof["browser"]["executed"])
        self.assertFalse(proof["browser"]["free_response_automatically_graded"])
        self.assertEqual(proof["golden"]["comparison_mode"], "UNDETERMINED")
        review = x["review"]
        self.assertTrue(all(review[k] is None for k in (
            "H1", "H2", "H3", "S1", "S2", "S3",
            "P1", "P2", "P3", "M1", "M2", "M3")))
        self.assertIsNone(review["qualified_academic_verdict"])
        self.assertIsNone(review["owner_qrt_decision_id"])
        self.assertEqual(review["owner_qrt_decision"], "PENDING")
        self.assertIsNone(review["owner_golden_decision_id"])
        self.assertIsNone(review["rights_decision_id"])
        self.assertIsNone(review["release_decision_id"])
        self.assertFalse(x["change_decision"]["merged"])
        self.assertFalse(x["change_decision"]["released"])

    def test_evaluation_explicitly_requires_live_trials(self):
        self.assertIn("Static repository CI", self.evaluation)
        for demand in ("MODEL", "RETRIEVE", "SYNTHESIZE", "JUSTIFY"):
            self.assertIn(demand, self.evaluation)
        self.assertIn("Unseen item", self.evaluation)
        self.assertIn("not", self.evaluation.lower())


if __name__ == "__main__":
    unittest.main()
