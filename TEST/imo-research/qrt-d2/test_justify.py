"""O1/O2 preflight for authored JUSTIFY-D2 TEST product; not academic acceptance."""
import json, unittest
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/'TEST/imo-research/qrt-d2/justify.v1.json'
MAN=ROOT/'TEST/products/imo182-qrt-d2-justify.manifest.json'
SCHEMA=ROOT/'Shared/library/package.schema.json'
FIG=ROOT/'TEST/imo-research/qrt-d2/figures/justify-d2-input.svg'

class TestJustifyD2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(PKG.read_text())
        cls.m=json.loads(MAN.read_text())
        cls.q=next(x for x in cls.p['questions'] if x['id']=='Q-TEST-QRT-JUSTIFY-D2-PROOF')
        cls.t=next(x for x in cls.p['questions'] if x['id']=='Q-TEST-QRT-JUSTIFY-D2-TRANSFER')
    def test_schema(self):
        jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.p)
    def test_manifest_five_and_rights(self):
        self.assertEqual(self.m['output_roles'],['CORE1','CORE1A','CORE1B','CORE2A','CORE2B'])
        self.assertEqual(self.m['selection']['core2'],[])
        self.assertEqual(self.m['selection']['core2a'],[self.q['id']])
        self.assertEqual(self.m['selection']['core2b'],[self.t['id']])
        self.assertEqual(self.m['package_refs'],['TEST/imo-research/qrt-d2/justify.v1.json'])
        self.assertEqual(self.q['origin'],'AUTHORED')
    def test_h3_after_written_attempt_policy(self):
        x=self.q['extensions']['grade9v3:core2_support_plan']
        self.assertIn(self.q['answer']['crux_move_ref'],x['protected_move_refs'])
        self.assertEqual(self.q['hint_ladder'][2]['from'],'scaffolds[2]')
        self.assertEqual(x['support_completions'][0]['availability'],'AFTER_ATTEMPT')
        self.assertEqual(x['support_completions'][0]['support_ref'],'scaffolds[2]')
        self.assertNotIn('m=2',self.q['scaffolds'][0]['text'])
        self.assertNotIn('m=2',self.q['scaffolds'][1]['text'])
    def test_safe_svg(self):
        svg=FIG.read_text()
        self.assertIn('PRACTICE-FACTORS-ONLY',svg)
        for forbidden in ('divisible by 6','coprime','parity','residue','m=2','60','factor of 3'):
            self.assertNotIn(forbidden,svg.lower())
    def test_counterexample_and_all_residues(self):
        self.assertEqual((3*4*5)%6,0)
        self.assertTrue(all(x%6 for x in (3,4,5)))
        for n in range(6):
            self.assertEqual(((n+1)*(n+2)*(n+3))%6,0)
        self.assertEqual((1*2*3*4)%48,24)
        for n in range(24):
            self.assertEqual((n*(n+1)*(n+2)*(n+3))%24,0)

if __name__=='__main__': unittest.main()
