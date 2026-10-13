"""Static contract checks for the GitHub question-first QRT agent profile.

These tests verify discoverability, real repository references and operating
rules; they do NOT assert an AI has performed academic review or render CI.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".github/agents/qrt-blueprint-mapper.agent.md"
PLAYBOOK = ROOT / "docs/method/QRT-QUESTION-FIRST-AGENT.md"
MATRIX = ROOT / "Shared/quality/question-demand-matrix.v1.json"
BLUEPRINTS = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
ROLES = ("CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B")
DISPOSITIONS = (
    "REUSE_AS_IS",
    "REPAIR_AUTHORED_SOURCE",
    "AUTHOR_MISSING_CONTENT",
    "REQUEST_SEPARATE_BLUEPRINT_OR_RENDERER_CHANGE_WITH_REPRO",
    "SOURCE_RIGHTS_HOLD",
)


class QuestionFirstAgentContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = AGENT.read_text(encoding="utf-8")
        cls.playbook = PLAYBOOK.read_text(encoding="utf-8")
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.blueprints = json.loads(BLUEPRINTS.read_text(encoding="utf-8"))

    def test_github_custom_agent_profile_is_well_formed(self):
        self.assertTrue(self.agent.startswith("---\n"))
        parts = self.agent.split("\n---\n", 1)
        self.assertEqual(len(parts), 2)
        frontmatter = parts[0].removeprefix("---\n")
        self.assertRegex(frontmatter, r"(?m)^name:\s+qrt-blueprint-mapper$")
        self.assertRegex(frontmatter, r"(?m)^description:\s+\S+")
        # Omitting a target keeps this agent usable in both GitHub and VS Code.
        self.assertNotIn("\ntarget:", "\n" + frontmatter)
        self.assertLessEqual(len(parts[1]), 30000)
        self.assertGreater(len(parts[1]), 2000)

    def test_agent_resolves_actual_registered_contracts(self):
        refs = re.findall(r"\]\((\.\./\.\./[^)#]+)\)", self.agent)
        self.assertGreaterEqual(len(refs), 4)
        for ref in refs:
            with self.subTest(reference=ref):
                self.assertTrue((AGENT.parent / ref).resolve().exists(), ref)
        self.assertEqual(set(self.matrix["demands"]), {
            "RETRIEVE", "EXPLAIN", "APPLY", "MODEL",
            "REPRESENT", "SYNTHESIZE", "JUSTIFY",
        })
        self.assertEqual(set(self.matrix["band_policies"]), {"D1", "D2", "D3", "D4"})
        existing = {row["id"] for row in self.blueprints["blueprints"]}
        for role in ROLES:
            with self.subTest(role=role):
                self.assertTrue(any(bp.startswith("BP-" + role + "-") for bp in existing))
                self.assertIn(role, self.agent)

    def test_all_reuse_choices_and_owner_holds_are_explicit(self):
        for term in DISPOSITIONS:
            with self.subTest(disposition=term):
                self.assertIn(term, self.agent)
                self.assertIn(term, self.playbook)
        for marker in (
            "DEMONSTRATED", "UNKNOWN", "NO_PREATTEMPT_SCAFFOLD",
            "QRT-<DEMAND>-<D1..D4>", "cross-role", "precommit",
            "ACADEMIC_REVIEWED", "OWNER_QRT_ACCEPTED",
            "OWNER_GOLDEN_DESIGNATED", "RELEASED",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.agent)
        self.assertIn("not a new QRT cell", self.playbook)
        self.assertIn("never a new authoring source", self.agent)

    def test_playbook_links_and_three_real_counterexamples_exist(self):
        refs = re.findall(r"\]\(([^)#]+)\)", self.playbook)
        local = [ref for ref in refs if not re.match(r"https?://", ref)]
        self.assertTrue(local)
        for ref in local:
            with self.subTest(reference=ref):
                self.assertTrue((PLAYBOOK.parent / ref).resolve().exists(), ref)
        for marker in ("MODEL-D4", "RETRIEVE-D4", "SYNTHESIZE-D4"):
            self.assertIn(marker, self.playbook)
        self.assertIn("35/35", self.playbook)
        self.assertIn("not academic/QRT acceptance", self.playbook)
        self.assertIn("before any learner-page edits", self.playbook)

    def test_scope_does_not_edit_normative_qrt_or_blueprints(self):
        self.assertEqual(self.matrix["schema"], "question-demand-matrix/v1")
        self.assertEqual(len(self.matrix["demands"]) * len(self.matrix["band_policies"]), 28)
        self.assertIn("Blueprint", self.agent)
        self.assertIn("registered renderer", self.agent)


if __name__ == "__main__":
    unittest.main()
