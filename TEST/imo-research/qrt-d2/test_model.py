import json, pathlib, unittest, jsonschema, re
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'TEST/imo-research/qrt-d2/model.v1.json'
M=ROOT/'TEST/products/imo182-qrt-d2-model.manifest.json'
class ModelD2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads(P.read_text());cls.m=json.loads(M.read_text())
  cls.a=next(q for q in cls.p['questions'] if q['id']=='Q-TEST-QRT-MODEL-D2-PRIMARY')
  cls.b=next(q for q in cls.p['questions'] if q['id']=='Q-TEST-QRT-MODEL-D2-TRANSFER')
 def test_schema(self):
  jsonschema.Draft202012Validator(json.loads((ROOT/'Shared/library/package.schema.json').read_text())).validate(self.p)
 def test_roles_source_and_demand(self):
  self.assertEqual(self.m['output_roles'],['CORE1','CORE1A','CORE1B','CORE2A','CORE2B'])
  self.assertEqual(self.m['selection']['core2'],[])
  self.assertEqual(self.a['origin'],'AUTHORED')
  self.assertEqual(self.a['extensions']['grade9v3:cognitive_demand']['primary'],'MODEL')
  self.assertIn('9 drinks',self.a['stem'])
 def test_h3_method_protected(self):
  policy=self.a['extensions']['grade9v3:core2_support_plan']
  self.assertEqual(policy['protected_move_refs'],[self.a['answer']['crux_move_ref']])
  self.assertEqual(policy['support_completions'][0]['availability'],'AFTER_ATTEMPT')
  for hint in self.a['scaffolds'][:2]:
   for leak in ['9−x','9-x','4(9','36+3','x=4']:self.assertNotIn(leak,hint['text'])
 def test_primary_and_other_roles(self):
  primary=[(x,9-x) for x in range(10) if 4*(9-x)+7*x==48]
  self.assertEqual(primary,[(4,5)])
  self.assertEqual([(x,6-x) for x in range(7) if 3*(6-x)+8*x==33],[(3,3)])
  self.assertEqual([(x,7-x) for x in range(8) if 5*(7-x)+9*x==47],[(3,4)])
  self.assertEqual([(x,8-x) for x in range(9) if 5*(8-x)+9*x==56],[(4,4)])
  self.assertEqual([(x,7-x) for x in range(8) if 5*(7-x)+9*x==49],[])
 def test_transfer_feasible_boundaries(self):
  possibles=[(x,11-x,5*(11-x)+9*x) for x in range(12)]
  self.assertNotIn(74,[t[2] for t in possibles])
  below=max(v[2] for v in possibles if v[2]<74)
  above=min(v[2] for v in possibles if v[2]>74)
  self.assertEqual((below,above),(71,75))
  self.assertEqual([(x,y) for x,y,v in possibles if v==71],[(4,7)])
  self.assertEqual([(x,y) for x,y,v in possibles if v==75],[(5,6)])
 def test_svg_pre_attempt(self):
  for fn in ['model-d2-primary.svg','model-d2-transfer.svg']:
   s=(ROOT/'TEST/imo-research/qrt-d2/figures'/fn).read_text()
   visible=' '.join(re.findall(r'<(?:title|desc|text)[^>]*>([^<]*)</(?:title|desc|text)>',s)+re.findall(r'aria-label="([^"]*)"',s)).lower()
   for leak in ['9−x','x=4','four large','5 small','71','75','impossible','19/4','4.75']:self.assertNotIn(leak,visible)
if __name__=='__main__':unittest.main()
