import unittest,json,pathlib,re,decimal,jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'TEST/imo-research/qrt-d2/apply.v1.json'
M=ROOT/'TEST/products/imo182-qrt-d2-apply.manifest.json'
class ApplyD2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pkg=json.loads(P.read_text()); cls.manifest=json.loads(M.read_text())
  cls.primary=next(q for q in cls.pkg['questions'] if q['id']=='Q-TEST-QRT-APPLY-D2-PRIMARY')
  cls.transfer=next(q for q in cls.pkg['questions'] if q['id']=='Q-TEST-QRT-APPLY-D2-TRANSFER')
 def test_schema(self):
  jsonschema.Draft202012Validator(json.loads((ROOT/'Shared/library/package.schema.json').read_text())).validate(self.pkg)
 def test_manifest_rights_and_roles(self):
  self.assertEqual(self.manifest['output_roles'],['CORE1','CORE1A','CORE1B','CORE2A','CORE2B'])
  self.assertEqual(self.manifest['selection']['core2'],[])
  self.assertEqual(self.primary['origin'],'AUTHORED')
  self.assertIn('REDUCED',self.primary['stem'])
  self.assertEqual(self.primary['extensions']['grade9v3:cognitive_demand']['primary'],'APPLY')
 def test_h3_after_attempt_and_W(self):
  protect=self.primary['extensions']['grade9v3:core2_support_plan']
  self.assertEqual(protect['support_completions'][0]['availability'],'AFTER_ATTEMPT')
  self.assertEqual(protect['protected_move_refs'],[self.primary['answer']['crux_move_ref']])
  for h in self.primary['scaffolds'][:2]:
   for forbidden in ['720','648','32.5','multiply the 720']:self.assertNotIn(forbidden,h['text'])
 def test_exact_multistage_and_inverse(self):
  D=decimal.Decimal
  self.assertEqual(D(960)*D('0.75')*D('0.90'),D(648))
  self.assertEqual((D(960)-D(648))/D(960)*100,D('32.5'))
  self.assertNotEqual(D(960)*D('0.65'),D(648))
  self.assertEqual(D(500)*D('0.9')*D('0.8'),D(360))
  self.assertEqual((D(500)-D(360))/D(500)*100,D(28))
  self.assertEqual(D(200)*D('0.75')**2,D('112.5'))
  self.assertEqual(D(100)*D('1.1')*D('0.9'),D(99))
  self.assertEqual(D(1080)/(D('1.2')*D('0.9')),D(1000))
  self.assertEqual(D(1000)*D('1.2')*D('0.9'),D(1080))
  self.assertEqual((D(1080)-D(1000))/D(1000)*100,D(8))
 def test_svg_pre_attempt_no_answer(self):
  for f in ['apply-d2-primary.svg','apply-d2-transfer.svg']:
   s=(ROOT/'TEST/imo-research/qrt-d2/figures'/f).read_text()
   visible=' '.join(re.findall(r'<(?:text|title|desc)[^>]*>([^<]*)</(?:text|title|desc)>',s)+re.findall(r'aria-label="([^"]*)"',s)).lower()
   for leak in ['720','648','32.5','1000 credits','final 1000','net 8%','1.08']:self.assertNotIn(leak,visible)
if __name__=='__main__':unittest.main()
