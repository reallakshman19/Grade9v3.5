"""QRT JUSTIFY-D1 native five-role, semantic staging and immutable golden checks."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
import jsonschema
from Shared.tools import render_core, core2_v2

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TEST/imo-research/qrt-d1/justify.v1.json"
MANIFEST=ROOT/"TEST/products/imo182-qrt-d1-justify.manifest.json"
SCHEMA=ROOT/"Shared/library/package.schema.json"
FROZEN=ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"

class JustifyD1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SRC.read_text())
        cls.pages,cls.gaps,cls.digest,_,_=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")

    def test_schema_and_adoption(self):
        jsonschema.validate(self.source,json.loads(SCHEMA.read_text()))
        self.assertEqual(self.source["extensions"]["grade9v3:imo_provenance"],"AUTHORED_TEST_FROM_ORIGINAL_PRACTICE_003")
        self.assertEqual(self.source["extensions"]["grade9v3:source_quality_hold"],"ALTITUDE_WORDING_CLARITY")
        self.assertTrue(all(q["origin"]=="AUTHORED" for q in self.source["questions"]))
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(m["selection"]["core2"],[])
        self.assertEqual(m["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])

    def test_native_roles_without_gaps(self):
        self.assertEqual(self.gaps,[],self.gaps)
        self.assertEqual(set(self.pages),{"index.html","core1.html","core1a.html","core1b.html","core2a.html","core2b.html"})
        refs={"core1":"BP-CORE1-ORIENTATION@1.1.0","core1a":"BP-CORE1A-CONSTRUCTION@1.8.0","core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0","core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0","core2b":"BP-CORE2B-TRANSFER@1.1.0"}
        for role,ref in refs.items():
            self.assertIn('data-blueprint-ref="'+ref+'"',self.pages[role+".html"])

    def test_justification_w_and_h3_after_attempt(self):
        qa=self.source["questions"][1]
        self.assertEqual(qa["extensions"]["grade9v3:cognitive_demand"]["primary"],"JUSTIFY")
        self.assertEqual(qa["difficulty"]["band"],"D1")
        self.assertEqual(qa["difficulty"]["score"],sum(qa["difficulty"]["components"].values()))
        self.assertEqual(qa["answer"]["crux_move_ref"],"JUS-D1-QA-WARRANT")
        self.assertEqual([x["availability"] for x in core2_v2.project_support(qa)],["PRE_ATTEMPT_SAFE","PRE_ATTEMPT_SAFE","AFTER_ATTEMPT"])
        self.assertIn("data-g9-after-attempt-hint",self.pages["core2a.html"])
        self.assertIn("data-requires-attempt",self.pages["core2a.html"])
        for scaffold in qa["scaffolds"][:2]:
            self.assertNotIn("42 cm²",scaffold["text"])
            self.assertNotIn("areas are equal",scaffold["text"].lower())

    def test_figure_stage_and_independent_exit(self):
        for r in self.source["representations"]:
            for name in r["rendered_asset_refs"]:
                svg=(ROOT/name).read_text()
                self.assertIn("<desc>",svg)
                self.assertIn("data-g9-stage-id",svg)
                self.assertNotIn("42 cm²",svg)
                self.assertNotIn("12×7/2",svg)
        mic=self.source["microtopics"][0]
        self.assertIn("8 cm",mic["elicitation"]["boundary_test"]["prompt"])
        self.assertIn("9 cm",mic["exit_task"]["prompt"])
        self.assertIn("perpendicular",mic["inferential_jump"])

    def test_accessible_altitude_wording_preserves_the_decision(self):
        # Research-intake wording hold: make the line/90-degree distance explicit,
        # but never treat this automated test as a learner accessibility signoff.
        qa=self.source["questions"][1]
        self.assertIn("extending the straight line through A and B",qa["stem"])
        self.assertIn("shortest distance",qa["stem"])
        self.assertIn("right angle (90°)",qa["stem"])
        self.assertIn("Must the triangles have equal areas?",qa["stem"])
        self.assertIn("grade9v3:wording_revision_status",self.source["extensions"])
        self.assertEqual(self.source["extensions"]["grade9v3:wording_revision_status"],
                         "AUTHOR_CANDIDATE_NOT_REVIEWED")
        self.assertEqual(self.source["extensions"]["grade9v3:source_quality_hold"],
                         "ALTITUDE_WORDING_CLARITY")
        # H2 must invite a warrant, not decide it on the learner's behalf.
        safe_hints=" ".join(h["text"] for h in qa["scaffolds"][:2]).lower()
        for forbidden in ("42 cm", "both areas equal", "sideways offset does not",
                          "guarantee equal area", "areas are the same"):
            self.assertNotIn(forbidden,safe_hints)
        from xml.etree import ElementTree as ET
        svg=ET.parse(ROOT/"TEST/imo-research/qrt-d1/figures/justify-core2a-triangles.v1.svg").getroot()
        ns="{http://www.w3.org/2000/svg}"
        desc=svg.find(ns+"desc")
        self.assertIsNotNone(desc)
        self.assertIn("90 degrees",desc.text)
        self.assertIn("extended through A and B",desc.text)
        self.assertNotIn("42",ET.tostring(svg,encoding="unicode"))
        self.assertNotIn("same area",desc.text.lower())
        # The native renderer uses a stage label for the accessible SVG name;
        # source SVG <desc> text alone is insufficient to prove that name survives.
        html=self.pages["core2a.html"]
        self.assertIn('aria-label="AB base 12 cm; each peak 7 cm at 90° to its extended line"',html)
        self.assertNotIn('aria-label="Both areas are equal',html)


    def test_cumulative_core1a_stages_do_not_redraw_geometry(self):
        # The sole renderer reveals SVG stages cumulatively, not exclusively.
        # Redrawing whole triangles in stages 2/3 superimposes labels/edges.
        from xml.etree import ElementTree as ET
        svg=ET.parse(ROOT/"TEST/imo-research/qrt-d1/figures/justify-area-stages.v1.svg").getroot()
        namespace="{http://www.w3.org/2000/svg}"
        groups=[g for g in svg.iter(namespace+"g") if g.get("data-g9-stage-id")]
        self.assertEqual([g.get("data-g9-stage-id") for g in groups],
                         ["JUS-STAGE-AREA-MEANING","JUS-STAGE-WORKED-10-4","JUS-STAGE-WORKED-CHECK"])
        self.assertTrue(any(e.tag in (namespace+"path",namespace+"line") for e in groups[0].iter()))
        for g in groups[1:]:
            self.assertFalse(any(e.tag in (namespace+"path",namespace+"line") for e in g.iter()),
                             "Incremental stages must add annotation, not duplicate full geometry")
        self.assertIn("20 cm²",ET.tostring(groups[2],encoding="unicode"))

    def test_core2b_converse_new_unknown(self):
        qa,qb=self.source["questions"][1:]
        self.assertEqual(qb["transfer"]["dimension"],"novelty")
        self.assertIn(qa["id"],qb["transfer"]["builds_on"])
        self.assertEqual(qb["transfer"]["protected_move_ref"],"JUS-D1-QB-INVERSE")
        self.assertIn("36 cm²",qb["stem"])
        self.assertIn("6 cm",qb["answer"]["summary"])

    def test_oracle_and_frozen_snapshot_lock(self):
        spec=importlib.util.spec_from_file_location("verify_justify",ROOT/"TEST/imo-research/qrt-d1/verify_justify.py")
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.verify()
        lock=json.loads((FROZEN/"snapshot-lock.json").read_text())
        for record in lock["snapshots"]:
            self.assertEqual(hashlib.sha256((FROZEN/record["path"]).read_bytes()).hexdigest(),record["sha256"])
        self.assertNotEqual(self.pages["core2a.html"],(FROZEN/"snapshots/core2a.html").read_text())

if __name__=="__main__":
    unittest.main()
