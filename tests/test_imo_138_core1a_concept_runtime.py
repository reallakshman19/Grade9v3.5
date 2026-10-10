"""#138: emitted TEST Core1A concept-first HTML contract, not a mastery assertion."""
import json
import importlib.util
import unittest
from pathlib import Path
from Shared.tools import render_core

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"


@unittest.skipUnless(importlib.util.find_spec("jsonschema") is not None,
                     "jsonschema absent; exact-head F02 focused CI installs and runs this dependency")
class TestConceptFirstHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.pages, cls.gaps, _, cls.advisories, cls.waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")

    def test_declared_test_role_projection(self):
        self.assertEqual((self.pkg["subject"], self.pkg["status"]), ("TEST", "CANDIDATE"))
        self.assertEqual(set(self.pages), {"index.html", "core1a.html", "core2a.html"})
        self.assertEqual(self.gaps, [])
        self.assertEqual(self.advisories, [])
        self.assertEqual(self.waivers, [])

    def test_concept_check_precedes_hidden_worked_example(self):
        html = self.pages["core1a.html"]
        self.assertIn('data-g9-concept-correct="FACTOR"', html)
        self.assertIn('data-g9-concept-option value="FACTOR"', html)
        self.assertIn('data-g9-concept-option value="ADD"', html)
        self.assertIn('data-g9-concept-reason', html)
        self.assertIn('data-g9-concept-feedback role="status" aria-live="polite"', html)
        self.assertLess(html.index('data-g9-concept-check'), html.index('data-g9-concept-target hidden'))
        self.assertIn('data-g9-concept-target hidden', html)
        self.assertIn('Formative teaching self-check only', html)

    def test_format_only_and_print_materialisation(self):
        html = self.pages["core1a.html"]
        self.assertIn("choice!==c.dataset.g9ConceptCorrect", html)
        self.assertIn("reason.length<15", html)
        self.assertIn("match(c.dataset.g9ReasonWords||'')", html)
        self.assertIn("match(c.dataset.g9RuleWords||'')", html)
        self.assertIn("article.dataset.g9ConceptCheckCompleted='formative_only'", html)
        self.assertIn("q('[data-g9-concept-target]',article).forEach(el=>{el.hidden=false})", html)
        self.assertIn("q('[data-g9-concept-target]').forEach(el=>el.hidden=false)", html)

    def test_no_false_core2_source_or_lesson_gate_on_question(self):
        self.assertNotIn('data-g9-concept-check', self.pages["core2a.html"])
        self.assertNotIn('data-g9-role="CORE2"', self.pages["core2a.html"])
        self.assertFalse(self.pkg["extensions"]["grade9v3:learner_published"])


if __name__ == "__main__":
    unittest.main()
