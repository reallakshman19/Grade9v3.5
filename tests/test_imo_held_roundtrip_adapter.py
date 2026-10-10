"""No-publication synthetic fixtures for the opt-in held HTML adapter."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from Shared.tools.imo_held_roundtrip_adapter import adapt, AdaptationError
from Shared.tools.imo_roundtrip_contract import audit
from test_imo_roundtrip_contract import html_fixture, Q, M, T
from test_imo_handoff_preflight import fixture as _identity_fixture

def fixture():
    p, m, pilot = _identity_fixture()
    m['product_id'] = 'imo-r1-q26-authored-qrt-core2a-core1a'
    return p, m, pilot

CU='CU-TEST-IMO-G9-EXPONENTIAL-RELATION'

def legacy_fixture():
    a,b=html_fixture()
    a=a.replace('data-g9-repair-target="TC-02"',f'data-g9-repair-target="{CU}"')
    a=a.replace('href="core1a.html#TC-02"',f'href="core1a.html#{CU}"')
    b=b.replace(f'id="{T}" data-g9-step="{T}"',f'data-g9-step="{T}"')
    b=b.replace('data-g9-practice-link','data-g9-not-core2a-return')
    def document(role, article):
        return ('<!doctype html><html lang="en" data-g9-shell data-g9-role="'+role+'" '
                'data-g9-mode="PAGES" data-g9-product="imo-r1-q26-authored-qrt-core2a-core1a" '
                'data-g9-render-digest="test-digest"><head><meta name="g9-render" '
                'content="render_core/test"></head><body data-core="'+role+'">'
                +article+'</body></html>')
    return document('CORE2A',a),document('CORE1A',b)

class HeldAdapter(unittest.TestCase):
    def test_legacy_roundtrip_is_adapted_but_never_published(self):
        args=fixture()
        a,b=legacy_fixture()
        self.assertEqual(audit(*args,a,b)['status'],'ROUNDTRIP_GAPS_HELD')
        na,nb,report=adapt(*args,a,b)
        self.assertEqual(report['status'],'LOCAL_TEST_CANDIDATE_ADAPTED_NOT_PUBLISHED')
        self.assertIn(f'data-g9-repair-target="{T}" href="core1a.html#{T}"',na)
        self.assertIn(f'data-g9-step="{T}" id="{T}" tabindex="-1"',nb)
        self.assertIn('data-g9-held-step-focus',nb)
        self.assertIn('data-g9-held-adapter="true"',nb)
        self.assertIn('noindex,nofollow',na)
        self.assertEqual(report['input_sha256']['core2a.html'], hashlib.sha256(a.encode()).hexdigest())
        self.assertEqual(report['input_sha256']['core1a.html'], hashlib.sha256(b.encode()).hexdigest())
        self.assertEqual(report['adapted_sha256']['core2a.html'], hashlib.sha256(na.encode()).hexdigest())
        self.assertEqual(report['adapted_sha256']['core1a.html'], hashlib.sha256(nb.encode()).hexdigest())
        self.assertIn(f'href="core2a.html#{Q}"',nb)
        self.assertEqual(audit(*args,na,nb)['status'],'STRUCTURAL_CANDIDATE_HELD')
        for key in ['authorizes_learner_launch','authorizes_independent_credit','academic_qrt_approved',
                    'browser_behavior_verified','source_approved']:
            self.assertIs(report[key],False)
        # No data from the authored candidate is regraded, rewritten or replaced.
        self.assertIn('Authored practice question; no answer shown yet',na)
        self.assertIn('Teaching step',nb)

    def test_fail_closed_mutations(self):
        cases=[
          ('missing_product',0,'data-g9-product="imo-r1-q26-authored-qrt-core2a-core1a"','data-g9-product="wrong"'),
          ('wrong_role_shell',1,'data-core="CORE1A"','data-core="CORE2"'),
          ('missing_digest',0,'data-g9-render-digest="test-digest"','data-g9-render-digest=""'),
          ('missing_render_meta',0,'name="g9-render"','name="invalid"'),
          ('double_html_role',0,'data-g9-role="CORE2A"','data-g9-role="CORE2A" data-g9-role="CORE1A"'),
          ('missing_commit',0,'data-g9-commit','data-g9-other'),
          ('missing_gate',0,'data-g9-payload-ref="CORE2A-'+Q+'-reasoning"','data-g9-payload-ref="OTHER"'),
          ('foreign_href',0,f'href="core1a.html#{CU}"','href="https://attacker.example/"'),
          ('unmatched_repair',0,'data-g9-repair-ref="TC-02"','data-g9-repair-ref="BAD"'),
          ('wrong_article',0,f'id="{Q}"','id="BAD"'),
          ('missing_teaching_step',1,f'data-g9-step="{T}"','data-g9-step="WRONG"'),
          ('duplicate_repair_link',0,'</template>',f'<a data-g9-repair-ref="{T}"></a></template>'),
          ('preexposed_link',0,'</template>',f'</template><a data-g9-repair-ref="{T}"></a>'),
          ('malicious_base',1,'</article>','<base href="https://attacker.example/"></article>'),
        ]
        for label,side,old,new in cases:
            with self.subTest(label=label):
                pages=list(legacy_fixture())
                self.assertIn(old,pages[side])
                pages[side]=pages[side].replace(old,new,1)
                with self.assertRaises(AdaptationError):
                    adapt(*fixture(),pages[0],pages[1])

    def test_html_fragments_and_wrong_manifest_product_rejected(self):
        a,b=legacy_fixture()
        with self.assertRaises(AdaptationError):
            adapt(*fixture(),a.split('<body ',1)[1].split('>',1)[1].split('</body>')[0],b)
        p,m,s=fixture()
        m['product_id']='wrong-product'
        with self.assertRaises(AdaptationError):
            adapt(p,m,s,a,b)

    def test_role_identity_mutation_fails(self):
        p,m,s=fixture()
        s['scope']['launch_authorized']=True
        with self.assertRaises(AdaptationError):
            adapt(p,m,s,*legacy_fixture())

    def test_adapter_cannot_be_applied_twice(self):
        p,m,s=fixture()
        a,b,_=adapt(p,m,s,*legacy_fixture())
        with self.assertRaises(AdaptationError):
            adapt(p,m,s,a,b)

    def test_cli_does_not_write_into_public_or_over_original(self):
        p,m,s=fixture()
        a,b=legacy_fixture()
        script=Path(__file__).resolve().parents[1] / 'Shared/tools/imo_held_roundtrip_adapter.py'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            pkg=root/m['package_refs'][0]
            man=root/'test-manifest.json'
            pil=root/'pilot.json'
            product=root/'draft/product'
            product.mkdir(parents=True)
            paths=[(pkg,p),(man,m),(pil,s)]
            for path,obj in paths:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(json.dumps(obj),encoding='utf-8')
            (product/'core2a.html').write_text(a)
            (product/'core1a.html').write_text(b)
            cmd=[sys.executable,str(script),'--repo-root',str(root),'--package',str(pkg),
                '--manifest',str(man),'--pilot',str(pil),'--core2a',str(product/'core2a.html'),
                '--core1a',str(product/'core1a.html'),'--output-dir',str(root/'build/adapted')]
            proc=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(json.loads(proc.stdout)['authorizes_learner_launch'],False)
            self.assertTrue((root/'build/adapted/core2a.html').is_file())
            self.assertTrue((root/'build/adapted/core1a.html').is_file())
            report=json.loads((root/'build/adapted/local-held-report.json').read_text())
            self.assertEqual(report['adapted_sha256']['core1a.html'],
                             hashlib.sha256((root/'build/adapted/core1a.html').read_bytes()).hexdigest())
            cmd[-1]=str(root/'build')
            proc=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            cmd[-1]=str(root/'unscoped/adapted')
            proc=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertFalse((root/'unscoped/adapted').exists())
            cmd[-1]=str(root/'public/adapted')
            proc=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertFalse((root/'public/adapted').exists())
            cmd[-1]=str(root/'build/production-input-test')
            cmd[cmd.index('--core2a')+1]=str(root/'public/core2a.html')
            (root/'public').mkdir(exist_ok=True)
            (root/'public/core2a.html').write_text(a)
            proc=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertFalse((root/'build/production-input-test').exists())
            cmd[cmd.index('--core2a')+1]=str(product/'core2a.html')
            cmd[-1]=str(product)
            proc=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertEqual((product/'core2a.html').read_text(),a)

if __name__=='__main__':
    unittest.main()
