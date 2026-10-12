import json, pathlib, unittest, jsonschema, re
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'TEST/imo-research/qrt-d2/represent.v1.json'
M=ROOT/'TEST/products/imo182-qrt-d2-represent.manifest.json'
class RepresentD2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads(P.read_text());cls.m=json.loads(M.read_text())
  cls.a=next(q for q in cls.p['questions'] if q['id']=='Q-TEST-QRT-REPRESENT-D2-PRIMARY')
  cls.b=next(q for q in cls.p['questions'] if q['id']=='Q-TEST-QRT-REPRESENT-D2-TRANSFER')
 def test_schema(self):
  jsonschema.Draft202012Validator(json.loads((ROOT/'Shared/library/package.schema.json').read_text())).validate(self.p)
 def test_registered_roles_and_authored_source(self):
  self.assertEqual(self.m['output_roles'],['CORE1','CORE1A','CORE1B','CORE2A','CORE2B'])
  self.assertEqual(self.m['selection']['core2'],[])
  self.assertEqual(self.a['origin'],'AUTHORED')
  self.assertEqual(self.a['extensions']['grade9v3:cognitive_demand']['primary'],'REPRESENT')
  self.assertIn('5-ROW',self.a['stem'])
 def test_h3_after_attempt_and_stage_cross_refs(self):
  pol=self.a['extensions']['grade9v3:core2_support_plan']
  self.assertEqual(pol['support_completions'][0]['availability'],'AFTER_ATTEMPT')
  self.assertEqual(pol['protected_move_refs'],[self.a['answer']['crux_move_ref']])
  for hint in self.a['scaffolds'][:2]:
   for leaked in ['35−','3×5','15 unshaded','upper-right 5×2']:self.assertNotIn(leaked,hint['text'])
  for i,r in enumerate(self.p['representations']):
   asset=ROOT/r['rendered_asset_refs'][0]
   s=asset.read_text()
   stages=set(re.findall(r'data-g9-stage-id="([^"]+)"',s))
   self.assertTrue(set(st['id'] for st in r['reveal_stages'])<=stages)
   self.assertIn(r['scene_instances'][0]['datum_refs'][0],[d['id'] for d in self.p['data']])
 def test_primary_partition_and_invariant(self):
  cells={(r,c) for r in range(5) for c in range(7)}
  left={(r,c) for r,c in cells if c<2}
  upper_right={(r,c) for r,c in cells if c>=2 and r<2}
  remain=cells-left-upper_right
  self.assertFalse(left & upper_right)
  self.assertEqual((len(cells),len(left),len(upper_right),len(remain)),(35,10,10,15))
  self.assertEqual([sum((r,c) in remain for c in range(7)) for r in range(5)],[0,0,5,5,5])
  self.assertEqual(35-2*5-2*5,3*5)
  self.assertNotEqual(35-2*5-2*7,15)
 def test_worked_exit_misconception_boundary(self):
  self.assertEqual(6*6-2*6-2*4,4*4)
  self.assertEqual(4*7-1*4-1*6,3*6)
  self.assertEqual(5*8-1*8-3*4,4*5)
  self.assertEqual(7*4-2*7-2*2,2*5)
  self.assertNotEqual(7*4-2*7-2*4,10)
 def test_reverse_transfer(self):
  lengths=[8,8,5,5,5,5]
  self.assertEqual(sum(lengths),36)
  self.assertEqual(2*8+4*5,36)
  self.assertEqual(6*8-4*3,36)
  self.assertNotEqual(6*8-6*3,36)
  self.assertEqual([(r,c) for r in range(6) for c in range(8) if c>=lengths[r]],[(r,c) for r in range(2,6) for c in range(5,8)])
 def test_figure_pre_attempt_no_solution(self):
  for fn in ['represent-d2-primary.svg','represent-d2-transfer.svg']:
   text=(ROOT/'TEST/imo-research/qrt-d2/figures'/fn).read_text()
   visible=' '.join(re.findall(r'<(?:title|desc|text)[^>]*>([^<]*)</(?:title|desc|text)>',text)+re.findall(r'aria-label="([^"]*)"',text)).lower()
   for leak in ['3×5','35−','15 unshaded','answer 15','36 squares','4×3','notch 4','missing 3','row bands 16']:self.assertNotIn(leak,visible)
if __name__=='__main__':unittest.main()
