import itertools,json,pathlib,re,unittest,jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'TEST/imo-research/qrt-d2/synthesize.v1.json'
M=ROOT/'TEST/products/imo182-qrt-d2-synthesize.manifest.json'
def choices(digits,fixed):
 return [int(''.join(map(str,(fixed,*p)))) for p in itertools.permutations((d for d in digits if d!=fixed),2)]
class SynthesizeD2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads(P.read_text());cls.manifest=json.loads(M.read_text())
  cls.a=next(q for q in cls.p['questions'] if q['id']=='Q-TEST-QRT-SYNTHESIZE-D2-PRIMARY')
  cls.b=next(q for q in cls.p['questions'] if q['id']=='Q-TEST-QRT-SYNTHESIZE-D2-TRANSFER')
 def test_schema(self):
  jsonschema.Draft202012Validator(json.loads((ROOT/'Shared/library/package.schema.json').read_text())).validate(self.p)
 def test_roles_rights_and_demand(self):
  self.assertEqual(self.manifest['output_roles'],['CORE1','CORE1A','CORE1B','CORE2A','CORE2B'])
  self.assertEqual(self.manifest['selection']['core2'],[])
  self.assertEqual(self.a['origin'],'AUTHORED')
  self.assertEqual(self.a['extensions']['grade9v3:cognitive_demand']['primary'],'SYNTHESIZE')
  self.assertEqual(self.a['difficulty']['score'],sum(self.a['difficulty']['components'].values()))
  self.assertEqual(self.b['difficulty']['score'],sum(self.b['difficulty']['components'].values()))
 def test_h3_only_after_attempt_and_safe_hints(self):
  pol=self.a['extensions']['grade9v3:core2_support_plan']
  self.assertEqual(pol['protected_move_refs'],[self.a['answer']['crux_move_ref']])
  self.assertEqual(pol['support_completions'][0]['availability'],'AFTER_ATTEMPT')
  for h in self.a['scaffolds'][:2]:
   for leaked in ['432','452','ones is 2','sum 9','tens is 3']:self.assertNotIn(leaked,h['text'])
 def test_primary_exhaustive_optimum(self):
  nums=choices([1,2,3,4,5],4)
  acceptable=[x for x in nums if x%6==0]
  self.assertEqual(acceptable,[432])
  self.assertEqual(max(acceptable),432)
  self.assertEqual(432//6,72)
  self.assertNotEqual(452%6,0)
 def test_worked_and_exit(self):
  self.assertEqual(max(x for x in choices([1,2,3,4],3) if x%6==0),342)
  self.assertEqual(max(x for x in choices([1,2,3,4,7],7) if x%6==0),732)
  self.assertNotEqual(734%6,0)
  self.assertNotEqual(742%6,0)
  self.assertEqual(732//6,122)
 def test_core1b_wrong_route_and_boundary(self):
  self.assertNotEqual(352%6,0)
  self.assertEqual(max(x for x in choices([1,2,3,4,5,6],6) if x%6==0),654)
  self.assertEqual(654//6,109)
  self.assertFalse(any(int('8'+str(t)+'5')%6==0 for t in [1,2,3]))
 def test_transfer_exhaustive_swaps(self):
  inp='534'
  swaps={tuple(sorted((i,j))):int(''.join((lambda a:(a.__setitem__(i,inp[j]),a.__setitem__(j,inp[i]),a)[2])(list(inp)))) for i,j in itertools.combinations(range(3),2)}
  self.assertEqual(set(swaps.values()),{354,435,543})
  valid=[v for v in swaps.values() if v<534 and v%6==0]
  self.assertEqual(valid,[354])
  self.assertTrue(all(sum(map(int,str(v)))==12 for v in swaps.values()))
  self.assertEqual(354//6,59)
 def test_figure_and_stage_rights(self):
  for i,r in enumerate(self.p['representations']):
   file=ROOT/r['rendered_asset_refs'][0]; svg=file.read_text()
   stages=set(re.findall(r'data-g9-stage-id="([^"]+)"',svg))
   self.assertTrue(set(x['id'] for x in r['reveal_stages'])<=stages)
   self.assertIn(r['scene_instances'][0]['datum_refs'][0],[d['id'] for d in self.p['data']])
  for name in ['synthesize-d2-primary.svg','synthesize-d2-transfer.svg']:
   s=(ROOT/'TEST/imo-research/qrt-d2/figures'/name).read_text()
   text=' '.join(re.findall(r'<(?:title|desc|text)[^>]*>([^<]*)</(?:title|desc|text)>',s)+re.findall(r'aria-label="([^"]*)"',s)).lower()
   for leaked in ['432','452','354','435','543','sum 9','tens 3','72 quotient','only valid','answer']:self.assertNotIn(leaked,text)
if __name__=='__main__':unittest.main()
