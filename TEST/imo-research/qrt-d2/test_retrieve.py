"""Independent source/math/rights and figure/gate tests for authored QRT-RETRIEVE-D2."""
import json,pathlib,re,math,unittest,jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[3]
SOURCE=ROOT/"TEST/imo-research/qrt-d2/retrieve.v1.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d2-retrieve.manifest.json"
def routes(a,b,limit):
 direct=math.isqrt(a*a+b*b)
 assert direct*direct==a*a+b*b
 edge=a+b
 return direct,edge,edge-direct, direct<=limit,edge<=limit
class RetrieveD2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads(SOURCE.read_text())
  cls.m=json.loads(MANIFEST.read_text())
  cls.w,cls.a,cls.b=cls.p["questions"]
 def test_package_schema(self):
  schema=json.loads((ROOT/"Shared/library/package.schema.json").read_text())
  jsonschema.Draft202012Validator(schema).validate(self.p)
 def test_manifest_rights_and_roles(self):
  self.assertEqual(self.m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])
  self.assertEqual(self.m["selection"]["core2"],[])
  self.assertEqual(self.m["selection"]["microtopics"],[self.p["microtopics"][0]["id"]])
  self.assertEqual(self.a["origin"],"AUTHORED")
  self.assertEqual(self.a["extensions"]["grade9v3:cognitive_demand"]["primary"],"RETRIEVE")
  self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.p["questions"]))
 def test_worked_math(self):
  self.assertEqual(routes(6,8,12),(10,14,4,True,False))
 def test_primary_two_step_and_cap(self):
  self.assertEqual(routes(9,12,18),(15,21,6,True,False))
  self.assertEqual(self.a["difficulty"]["score"],sum(self.a["difficulty"]["components"].values()))
  self.assertEqual(self.b["difficulty"]["score"],sum(self.b["difficulty"]["components"].values()))
 def test_exit_independent(self):
  self.assertEqual(routes(8,15,20),(17,23,6,True,False))
 def test_core1b_wrong_route_independent_and_second_boundary(self):
  self.assertEqual(6*6+8*8,100)
  self.assertEqual(math.isqrt(100),10)
  self.assertEqual(routes(12,16,23),(20,28,8,True,False))
  # Direct path mathematically within cap but inaccessible; permitted path fails.
  self.assertEqual(routes(8,15,20),(17,23,6,True,False))
  self.assertIn("CLOSED",self.p["microtopics"][0]["elicitation"]["boundary_test"]["prompt"])
 def test_transfer_inverse_and_changed_direction(self):
  other2=13*13-5*5
  self.assertEqual(other2,144)
  self.assertEqual(math.isqrt(other2),12)
  self.assertEqual(routes(5,12,15),(13,17,4,True,False))
  self.assertIn("IN REVERSE",self.b["stem"])
  self.assertNotEqual(self.a["answer"]["crux_move_ref"],self.b["answer"]["crux_move_ref"])
 def test_support_gate_preserved(self):
  sp=self.a["extensions"]["grade9v3:core2_support_plan"]
  self.assertEqual(sp["protected_move_refs"],[self.a["answer"]["crux_move_ref"]])
  self.assertEqual(sp["support_completions"][0]["availability"],"AFTER_ATTEMPT")
  self.assertEqual(sp["support_completions"][0]["support_ref"],"scaffolds[2]")
  for scaffold in self.a["scaffolds"][:2]:
   text=scaffold["text"].lower()
   for leaked in ("15m","21m","saving6","225","only direct","diagonal=15"):
    self.assertNotIn(leaked,text)
 def test_figures_stages_and_references(self):
  for rep in self.p["representations"]:
   path=ROOT/rep["rendered_asset_refs"][0]
   svg=path.read_text()
   stages=set(re.findall(r'data-g9-stage-id="([^"]+)"',svg))
   self.assertTrue({x["id"] for x in rep["reveal_stages"]}<=stages)
   self.assertIn(rep["scene_instances"][0]["datum_refs"][0],{d["id"] for d in self.p["data"]})
  for name in ("retrieve-d2-primary.svg","retrieve-d2-transfer.svg"):
   svg=(ROOT/"TEST/imo-research/qrt-d2/figures"/name).read_text()
   text=" ".join(re.findall(r'<(?:title|desc|text)[^>]*>([^<]*)</(?:title|desc|text)>',svg)+re.findall(r'aria-label="([^"]*)"',svg)).lower()
   for leaked in ("15m diagonal","21m","saving6","other side12m","17m boundary","only direct","answer:"):
    self.assertNotIn(leaked,text)
 def test_cross_refs(self):
  objs=[*self.p["resources"],*self.p["buckets"],*self.p["capabilities"],*self.p["microtopics"],*self.p["relations"],*self.p["representations"],*self.p["question_families"],*self.p["questions"],*self.p["teaching_routes"],*self.p["data"]]
  ids={o["id"] for o in objs}
  for q in self.p["questions"]:
   self.assertIn(q["family_ref"],ids)
   self.assertIn(q["primary_capability_ref"],ids)
   for fid in q["figure_refs"]:self.assertIn(fid,ids)
  self.assertIn(self.p["microtopics"][0]["id"],ids)
 def test_authored_primary_not_plain_D1(self):
  self.assertIn("18m",self.a["stem"])
  self.assertIn("BOTH",self.a["stem"])
  self.assertIn("13m",self.b["stem"])
  self.assertIn("limit",self.b["stem"].lower())
  self.assertNotEqual(self.a["stem"],self.w["stem"])
if __name__=="__main__":unittest.main()
