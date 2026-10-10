"""Synthetic HTML falsifiers for the nonpublishing F04 roundtrip contract."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from Shared.tools.imo_roundtrip_contract import audit
from test_imo_handoff_preflight import fixture

Q = 'Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01'
M = 'MIC-TEST-IMO-G9-COMMON-BASE-RELATION'
T = 'TC-02'
PAYLOAD = f'CORE2A-{Q}-reasoning'


def html_fixture():
    practice = f'''<article id="{Q}" data-g9-role="CORE2A" data-g9-unit="{Q}">
      <p>Authored practice question; no answer shown yet</p>
      <div data-g9-attempt-box><textarea aria-label="Your attempt"></textarea><button data-g9-commit>Commit</button></div>
      <details data-requires-attempt data-g9-payload-ref="{PAYLOAD}"><summary>Reasoning route</summary><div data-g9-payload-slot></div></details>
      <template data-g9-payload="{PAYLOAD}">
        <p>Model solution is inert until attempt</p>
        <a data-g9-repair-ref="{T}" data-g9-concept-ref="{M}" data-g9-repair-target="{T}" href="core1a.html#{T}">Revisit exact step</a>
      </template>
    </article>'''
    concept = f'''<article id="{M}" data-g9-role="CORE1A" data-g9-unit="{M}">
       <ol><li id="{T}" data-g9-step="{T}">Teaching step</li></ol>
       <a data-g9-practice-link data-g9-concept-ref="{M}" data-g9-question-ref="{Q}" href="core2a.html#{Q}">Return to supported practice</a>
    </article>'''
    return practice, concept


class RoundTripContract(unittest.TestCase):
    def check(self, pkg=None, manifest=None, pilot=None, practice=None, concept=None):
        inputs = fixture()
        a, b = html_fixture()
        return audit(pkg if pkg is not None else inputs[0],
                     manifest if manifest is not None else inputs[1],
                     pilot if pilot is not None else inputs[2],
                     practice if practice is not None else a,
                     concept if concept is not None else b)

    def test_synthetic_connected_candidate_is_still_held(self):
        report = self.check()
        self.assertEqual(report['status'], 'STRUCTURAL_CANDIDATE_HELD', report['errors'])
        self.assertEqual(report['errors'], [])
        for prop in ('authorizes_learner_launch','authorizes_independent_credit',
                     'browser_behavior_verified','academic_qrt_source_approved'):
            self.assertFalse(report[prop])

    def test_negative_mutations_each_block_and_never_release(self):
        cases = [
            ('unprotected_link', 0, 'data-g9-payload-ref="'+PAYLOAD+'"', 'data-g9-payload-ref="WRONG"', 'CORE2A_POST_ATTEMPT_GATE_MISSING'),
            ('missing_template', 0, f'data-g9-payload="{PAYLOAD}"', 'data-g9-payload="OTHER"', 'CORE2A_REASONING_TEMPLATE_MISSING'),
            ('wrong_step', 0, 'data-g9-repair-ref="TC-02"', 'data-g9-repair-ref="TC-01"', 'REPAIR_STEP_REF_MISMATCH'),
            ('wrong_target', 0, 'data-g9-repair-target="TC-02"', 'data-g9-repair-target="'+M+'"', 'REPAIR_TARGET_NOT_EXACT_STEP'),
            ('wrong_repair_href', 0, 'href="core1a.html#TC-02"', 'href="core1a.html#'+M+'"', 'REPAIR_HREF_NOT_EXACT_STEP'),
            ('repair_wrong_concept', 0, f'data-g9-concept-ref="{M}"', 'data-g9-concept-ref="FAKE"', 'REPAIR_CONCEPT_REF_MISMATCH'),
            ('wrong_question', 0, f'id="{Q}"', 'id="FAKE"', 'CORE2A_EXACT_QUESTION_ARTICLE_MISSING'),
            ('missing_step', 1, f'data-g9-step="{T}"', 'data-g9-step="MISSING"', 'CORE1A_TEACHING_STEP_NOT_FOUND'),
            ('unaddressable_step', 1, f'id="{T}"', 'id="WRONG"', 'CORE1A_STEP_NOT_ADDRESSABLE'),
            ('wrong_return_role', 1, f'href="core2a.html#{Q}"', f'href="core2.html#{Q}"', 'RETURN_HREF_NOT_CORE2A'),
            ('wrong_return_qid', 1, f'data-g9-question-ref="{Q}"', 'data-g9-question-ref="ANOTHER"', 'CORE1A_EXACT_CORE2A_RETURN_MISSING'),
            ('duplicate_step_dom_id', 1, '</article>', f'<p id="{T}"></p></article>', 'CORE1A_DUPLICATE_DOM_IDS'),
            ('missing_return', 1, 'data-g9-practice-link', 'data-g9-other', 'CORE1A_EXACT_CORE2A_RETURN_MISSING'),
            ('base_href_override', 1, '</article>', '<base href="https://other.example/"></article>', 'BASE_URL_OVERRIDE_FORBIDDEN'),
            ('duplicate_link_attribute', 0, 'href="core1a.html#TC-02"', 'href="core1a.html#TC-02" href="other.html"', 'DUPLICATE_HTML_ATTRIBUTES'),
        ]
        for label, which, old, new, expected in cases:
            with self.subTest(label=label):
                pages = list(html_fixture())
                self.assertIn(old,pages[which])
                pages[which] = pages[which].replace(old,new,1)
                result = self.check(practice=pages[0],concept=pages[1])
                self.assertEqual(result['status'],'ROUNDTRIP_GAPS_HELD')
                self.assertIn(expected,result['errors'])
                self.assertFalse(result['authorizes_learner_launch'])

    def test_existing_renderer_shape_is_structurally_incomplete(self):
        # Source-reviewed approximation of render_core._repair() with the
        # current candidate construction unit, and Core2-only practice nav.
        # This fixture is NOT a rendered test of the actual Agent 2 product.
        practice, concept = html_fixture()
        unit = 'CU-TEST-IMO-G9-EXPONENTIAL-RELATION'
        practice = practice.replace('data-g9-repair-target="TC-02"',
                                    'data-g9-repair-target="'+unit+'"')
        practice = practice.replace('href="core1a.html#TC-02"',
                                    'href="core1a.html#'+unit+'"')
        concept = concept.replace('id="TC-02" data-g9-step="TC-02"',
                                  'data-g9-step="TC-02"')
        concept = concept.replace('data-g9-practice-link','data-g9-not-core2a-return')
        result = self.check(practice=practice,concept=concept)
        self.assertEqual(result['status'],'ROUNDTRIP_GAPS_HELD')
        self.assertTrue({'REPAIR_TARGET_NOT_EXACT_STEP',
                         'REPAIR_HREF_NOT_EXACT_STEP',
                         'CORE1A_STEP_NOT_ADDRESSABLE',
                         'CORE1A_EXACT_CORE2A_RETURN_MISSING'}.issubset(set(result['errors'])))

    def test_realistic_pre_attempt_link_outside_template_is_rejected(self):
        practice, concept = html_fixture()
        start = f'<a data-g9-repair-ref="{T}"'
        end = '</a>'
        beginning = practice.index(start)
        finish = practice.index(end,beginning)+len(end)
        link = practice[beginning:finish]
        exposed = practice[:beginning] + practice[finish:]
        exposed = exposed.replace('</template>', '</template>'+link)
        result = self.check(practice=exposed,concept=concept)
        self.assertIn('REPAIR_LEAKS_BEFORE_ATTEMPT',result['errors'])

    def test_cli_rejects_swapped_manifest_path(self):
        p,m,pilot = fixture()
        practice,concept = html_fixture()
        script = Path(__file__).resolve().parents[1]/'Shared/tools/imo_roundtrip_contract.py'
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = base / m['package_refs'][0]
            man = base/'manifest.json'
            pil = base/'pilot.json'
            a = base/'product/core2a.html'
            b = base/'product/core1a.html'
            for path,obj in ((pkg,p),(man,m),(pil,pilot)):
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(json.dumps(obj),encoding='utf-8')
            a.parent.mkdir(parents=True,exist_ok=True)
            a.write_text(practice,encoding='utf-8')
            b.write_text(concept,encoding='utf-8')
            cmd = [sys.executable,str(script),'--repo-root',str(base),'--package',str(pkg),
                   '--manifest',str(man),'--pilot',str(pil),'--core2a',str(a),'--core1a',str(b)]
            valid = subprocess.run(cmd,text=True,capture_output=True)
            self.assertEqual(valid.returncode,0,valid.stderr)
            self.assertFalse(json.loads(valid.stdout)['authorizes_learner_launch'])
            swapped = pkg.with_name('other.json')
            swapped.write_text(pkg.read_text(encoding='utf-8'),encoding='utf-8')
            cmd[cmd.index('--package')+1] = str(swapped)
            invalid = subprocess.run(cmd,text=True,capture_output=True)
            self.assertNotEqual(invalid.returncode,0)
            self.assertIn('MANIFEST_PACKAGE_REF_MISMATCH',json.loads(invalid.stdout)['errors'])
            alt_dir = base / 'other_product/core1a.html'
            alt_dir.parent.mkdir(parents=True,exist_ok=True)
            alt_dir.write_text(concept,encoding='utf-8')
            cmd[cmd.index('--package')+1] = str(pkg)
            cmd[cmd.index('--core1a')+1] = str(alt_dir)
            wrong_product = subprocess.run(cmd,text=True,capture_output=True)
            self.assertNotEqual(wrong_product.returncode,0)
            self.assertEqual(json.loads(wrong_product.stdout)['status'],'ROUNDTRIP_GAPS_HELD')


if __name__ == '__main__':
    unittest.main()
