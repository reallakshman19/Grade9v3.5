"""#138: emitted TEST Core1A concept-first HTML contract, not a mastery assertion."""
import json
import re
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
        self.assertIn('data-g9-neutral-diagnostic data-g9-base="7" data-g9-exponent="2"', html)
        self.assertIn('data-g9-diagnostic-next autocomplete="off"', html)
        self.assertIn('data-g9-diagnostic-add autocomplete="off"', html)
        self.assertIn('data-g9-rule-check data-g9-rule-correct="FACTOR_LAW"', html)
        self.assertIn('data-g9-rule-option value="FACTOR_LAW"', html)
        self.assertIn('data-g9-rule-option value="ADD_BASE"', html)
        self.assertIn('data-g9-rule-option value="MULTIPLY_EXPONENT"', html)
        self.assertIn('data-g9-concept-feedback role="status" aria-live="polite"', html)
        self.assertLess(html.index('data-g9-concept-check'), html.index('data-g9-concept-target hidden'))
        self.assertIn('data-g9-concept-target hidden', html)
        self.assertIn('This reflection checks neither the meaning nor accuracy', html)

    def test_exact_tc02_fragment_is_unique_but_gated_until_guided_choice(self):
        core1a = self.pages["core1a.html"]
        core2a = self.pages["core2a.html"]
        step = 'id="TC-02" tabindex="-1" data-g9-step="TC-02"'
        self.assertEqual(core1a.count(step), 1, "exact authored step anchor must be unique")
        self.assertLess(core1a.index('data-g9-concept-target hidden'), core1a.index(step),
                        "deep-linked step must initially be inside the concealed construction")
        self.assertIn('data-g9-repair-ref="TC-02"', core2a)
        self.assertIn('data-g9-repair-target="TC-02" href="core1a.html?g9-return=', core2a)
        self.assertNotIn('data-g9-repair-target="CU-TEST-IMO-G9-EXPONENTIAL-RELATION"',
                         core2a)
        self.assertIn("window.location.hash==='#TC-02'", core1a)
        self.assertIn('The requested TC-02 repair step is behind this concept-first checkpoint',
                      core1a)
        self.assertIn("repair.focus();repair.scrollIntoView({block:'center'});", core1a)
        self.assertIn("guide.focus();", core1a)
        self.assertFalse(self.pkg["extensions"]["grade9v3:learner_published"])

    def test_author_selected_core2a_return_route_is_assisted_not_another_core2(self):
        core1a = self.pages["core1a.html"]
        core2a = self.pages["core2a.html"]
        question_id = "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01"
        concept_id = self.pkg["microtopics"][0]["id"]
        self.assertEqual(core1a.count("data-g9-authored-core2a-return"), 1)
        self.assertIn('href="core2a.html#' + question_id + '"', core1a)
        self.assertNotIn('href="core2.html#' + question_id + '"', core1a)
        self.assertIn('data-g9-question-ref="' + question_id + '"', core1a)
        self.assertIn('data-g9-concept-ref="' + concept_id + '"', core1a)
        self.assertIn('Returning after guided teaching is assisted practice', core1a)
        self.assertLess(core1a.index('data-g9-concept-target hidden'),
                        core1a.index("data-g9-authored-core2a-return"))
        self.assertIn('data-g9-concept-link data-g9-question-ref="' + question_id + '"',
                      core2a)
        self.assertIn('href="core1a.html?g9-return=' + question_id +
                      '&amp;g9-concept=' + concept_id + '#TC-02"', core2a)
        self.assertIn('const navReturn=navParams.get(\'g9-return\')', core1a)
        self.assertIn('const navConcept=navParams.get(\'g9-concept\')', core1a)
        self.assertFalse(self.pkg["extensions"]["grade9v3:learner_published"])

    def test_author_selected_return_fails_closed_on_wrong_custody_or_selection(self):
        from types import SimpleNamespace
        import copy

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        microtopic = self.pkg["microtopics"][0]
        authored = next(q for q in self.pkg["questions"]
                        if q["id"] == "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01")
        ctx = SimpleNamespace(manifest=manifest, selection_rows={"core2a": [authored]})
        self.assertEqual(render_core._f02_selected_authored_core2a(ctx, microtopic)["id"],
                         authored["id"])

        forged = copy.deepcopy(authored)
        forged["origin"] = "SOURCE"
        ctx.selection_rows["core2a"] = [forged]
        self.assertIsNone(render_core._f02_selected_authored_core2a(ctx, microtopic))

        ctx.selection_rows["core2a"] = [authored]
        ctx.manifest = copy.deepcopy(manifest)
        ctx.manifest["selection"]["core2a"] = []
        self.assertIsNone(render_core._f02_selected_authored_core2a(ctx, microtopic))

        ctx.manifest = manifest
        bad_topic = copy.deepcopy(microtopic)
        bad_topic["primary_capability_ref"] = "CAP-NOT-SELECTED"
        self.assertIsNone(render_core._f02_selected_authored_core2a(ctx, bad_topic))

    def test_authored_f02_local_trace_only_records_untrusted_event_markers(self):
        core1a = self.pages["core1a.html"]
        core2a = self.pages["core2a.html"]
        for name, html in (("Core1A", core1a), ("Core2A", core2a)):
            with self.subTest(page=name):
                self.assertEqual(html.count("data-g9-f02-trace-status"), 2,
                                 "one DOM note and one runtime selector")
                self.assertIn("F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1", html)
                self.assertIn("f02-trace:", html)
                self.assertIn("ATTEMPT_COMMIT", html)
                self.assertIn("REPAIR_NAV", html)
                self.assertIn("GUIDED_OPEN", html)
                self.assertIn("RETURN_CLICK", html)
                self.assertIn("Editable or missing local data never establishes independent mastery", html)
                self.assertNotIn("store.set(f02Key,JSON.stringify({value:", html)
        self.assertIn("if(box&&validAttempt(box))f02Event('ATTEMPT_COMMIT')", core2a)
        self.assertIn("if(value.invalid){f02Reflect(value,false);return}", core2a)
        self.assertIn("if(value.events.length>=32)value.overflow=true", core2a)
        self.assertIn("value.events.push({n:value.events.length+1,kind})", core2a)
        self.assertIn("events:value.events.map(e=>({n:e.n,kind:e.kind}))", core2a)
        self.assertIn("if(value.invalid){f02Reflect(value,false);return}", core1a)
        self.assertIn("if(!f02Key)return {invalid:true}", core1a)
        self.assertIn("value.assisted||value.invalid", core2a)
        self.assertIn("if(params.get('g9-return')===f02Question", core1a)
        self.assertIn("article?.dataset.g9ConceptAidExposure==='guided_study'", core1a)
        self.assertIn("returnKey=concept=>", render_core.JS)
        self.assertNotIn("F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1", render_core.JS)

    def test_trace_patch_stays_opt_in_and_rejects_ambiguous_generic_tail(self):
        self.assertEqual(render_core.f02_local_trace_js(render_core.JS).count(
            "F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1"), 1)
        with self.assertRaisesRegex(ValueError, "F02_LOCAL_TRACE_JS_PATCH_UNSAFE"):
            render_core.f02_local_trace_js(render_core.JS + "\n})();\n")
        self.assertFalse(self.pkg["extensions"]["grade9v3:learner_published"])

    def test_format_only_and_print_materialisation(self):
        html = self.pages["core1a.html"]
        self.assertIn("choice!==c.dataset.g9ConceptCorrect", html)
        self.assertIn("reason.length<8", html)
        # Keyword matching is not a validity check on free-form mathematical language.
        self.assertNotIn("g9ReasonWords", html)
        self.assertNotIn("g9RuleWords", html)
        self.assertIn("Your explanation has NOT been graded for correctness", html)
        self.assertIn("article.dataset.g9ConceptCheckCompleted='formative_only'", html)
        self.assertEqual(html.count("article.dataset.g9ConceptAidExposure='guided_study';"), 2,
                         "both approved-check reveal and guided bypass must mark non-independent exposure")
        self.assertIn("later responses on this page are assisted", html)
        self.assertIn("article.dataset.g9ConceptAidExposure==='guided_study'", html)
        self.assertIn("setProgress('needs_review'", html)
        self.assertIn("setProgress('needs_reflection'", html)
        self.assertIn("setProgress('needs_counterexample'", html)
        self.assertIn("setProgress('guided_without_check'", html)
        self.assertIn("repeated_additive_route_candidate", html)
        self.assertIn("choice_numeric_conflict", html)
        self.assertIn("possible_execution_slip_or_model_error", html)
        self.assertIn("mechanism_check_missing", html)
        self.assertIn("mechanism_route_conflict", html)
        self.assertIn("setProgress('needs_reasoning'", html)
        self.assertIn("warrantChoice!==rule.dataset.g9RuleCorrect", html)
        self.assertIn("aligned_structured_counterexample", html)
        self.assertIn("aligned_after_guided_exposure", html)
        self.assertIn("const previouslyGuided=article.dataset.g9ConceptAidExposure==='guided_study'", html)
        self.assertIn("previouslyGuided", html)
        self.assertIn("Your explanation has NOT been graded", html)
        self.assertEqual(html.count("delete article.dataset.g9ConceptCheckCompleted;"), 2,
                         "both re-submission and guided bypass must invalidate stale format evidence")
        self.assertEqual(html.count("delete article.dataset.g9DiagnosticPattern;"), 2,
                         "a later submission or guided bypass invalidates all prior diagnostic patterns")
        self.assertIn("data-g9-learning-progress", html)
        self.assertIn("data-g9-concept-review", html)
        microtopic_id = self.pkg["microtopics"][0]["id"]
        self.assertIn(f'id="{microtopic_id}-concept-reason"', html)
        self.assertIn(f'for="{microtopic_id}-concept-reason"', html)
        self.assertIn(f'id="{microtopic_id}-diagnostic-next"', html)
        self.assertIn(f'id="{microtopic_id}-diagnostic-add"', html)
        self.assertIn(f'for="{microtopic_id}-diagnostic-next"', html)
        self.assertIn(f'for="{microtopic_id}-diagnostic-add"', html)
        self.assertIn(f'aria-describedby="{microtopic_id}-concept-scope"', html)
        self.assertIn(f'id="{microtopic_id}-concept-scope"', html)
        self.assertIn("q('[data-g9-concept-target]',article).forEach(el=>{el.hidden=false})", html)
        self.assertIn("q('[data-g9-concept-target]').forEach(el=>el.hidden=false)", html)
        self.assertIn("window.matchMedia('print')", html)
        self.assertIn("printMode.addEventListener('change'", html)
        self.assertIn("window.addEventListener('beforeprint',refitPrintStages)", html)
        self.assertIn('[data-g9-neutral-diagnostic] input{display:block;box-sizing:border-box;', html)
        self.assertIn('max-width:100%;width:min(100%,18rem);min-height:48px', html)
        self.assertIn('[data-g9-concept-target][hidden]{display:block!important}', html)
        self.assertIn('[data-g9-concept-target] .g9-stage-controls{display:none!important}', html)
        self.assertIn("q('figure[data-g9-figure]',article).forEach(fitFigure)", html)

    def test_no_false_core2_source_or_lesson_gate_on_question(self):
        # Shared inline JS contains the concept-check handler on every role page.
        # The *learner DOM* must not include the opt-in TEST Core1A checkpoint.
        self.assertNotIn('<section class="g9-concept-first" data-g9-concept-check',
                         self.pages["core2a.html"])
        self.assertNotIn('<fieldset data-g9-neutral-diagnostic', self.pages["core2a.html"])
        self.assertNotIn('<fieldset data-g9-rule-check', self.pages["core2a.html"])
        self.assertNotIn('[data-g9-concept-target][hidden]{display:block!important}',
                         self.pages["core2a.html"])
        self.assertNotIn('[data-g9-concept-target] .g9-stage-controls{display:none!important}',
                         self.pages["core2a.html"])
        # Again, shared inline JS legitimately contains all role selectors.
        # Verify *rendered page/article* role rather than searching JS source.
        self.assertIsNone(re.search(r'<(?:html|article)[^>]*data-g9-role="CORE2"',
                                    self.pages["core2a.html"]))
        self.assertFalse(self.pkg["extensions"]["grade9v3:learner_published"])


if __name__ == "__main__":
    unittest.main()
