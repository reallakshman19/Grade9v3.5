import json, pathlib, unittest, jsonschema, re
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'TEST/imo-research/qrt-d2/explain.v1.json'
M=ROOT/'TEST/products/imo182-qrt-d2-explain.manifest.json'
class ExplainD2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads(P.read_text());cls.m=json.loads(M.read_text())
  cls.a=next(x for x in cls.p['questions'] if x['id']=='Q-TEST-QRT-EXPLAIN-D2-PRIMARY')
  cls.b=next(x for x in cls.p['questions'] if x['id']=='Q-TEST-QRT-EXPLAIN-D2-TRANSFER')
 def test_schema(self):
  jsonschema.Draft202012Validator(json.loads((ROOT/'Shared/library/package.schema.json').read_text())).validate(self.p)
 def test_manifest_roles_and_custody(self):
  self.assertEqual(self.m['output_roles'],['CORE1','CORE1A','CORE1B','CORE2A','CORE2B'])
  self.assertEqual(self.m['selection']['core2'],[])
  self.assertEqual(self.a['origin'],'AUTHORED')
  self.assertIn('positive integer',self.a['stem'])
 def test_after_attempt_h3(self):
  p=self.a['extensions']['grade9v3:core2_support_plan']
  self.assertEqual(p['protected_move_refs'],[self.a['answer']['crux_move_ref']])
  self.assertEqual(p['support_completions'][0]['availability'],'AFTER_ATTEMPT')
  self.assertEqual(p['support_completions'][0]['support_ref'],'scaffolds[2]')
  for rung in self.a['scaffolds'][:2]:self.assertNotIn('3×3^t',rung['text'])
 def test_independent_arithmetic(self):
  for t in range(1,12):
   self.assertEqual(3**(t+1),3*(3**t))
   self.assertEqual(7**(t+1),7*(7**t))
   self.assertEqual(2**(2*t),(2**t)**2)
  self.assertEqual(2**4,16)
  self.assertNotEqual(2**4,2*(2**2))
  self.assertNotEqual(3**2,3**1+3)
  self.assertEqual(2**2,2**3//2)
 def test_safe_figure(self):
  for name in ['primary','transfer']:
   s=(ROOT/'TEST/imo-research/qrt-d2/figures'/('explain-d2-'+name+'.svg')).read_text()
   readable=' '.join(re.findall(r'<(?:text|title|desc)[^>]*>([^<]*)</(?:text|title|desc)>',s)+re.findall(r'aria-label="([^"]*)"',s)).lower()
   for leaked in ['3×3^t','(2^k)^2','27','16','multiplication wins','t=1']:self.assertNotIn(leaked,readable)
if __name__=='__main__':unittest.main()
