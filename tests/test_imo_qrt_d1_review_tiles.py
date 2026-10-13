"""Exact 7×4 QRT viewer contract: seven D1 real HTML receipts, zero forged acceptance."""
from __future__ import annotations
import json,re,unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TILES=ROOT/"TEST/imo-research/qrt-tiles"
INDEX=TILES/"q003-model-d2/index.html"
BANDS=TILES/"q003-model-d2/band-issues.v1.json"
DEMANDS=("RETRIEVE","EXPLAIN","APPLY","MODEL","REPRESENT","SYNTHESIZE","JUSTIFY")
ROLES=("core1.html","core1a.html","core1b.html","core2a.html","core2b.html","index.html")
ASKS=("H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3")
ARTIFACT_PREFIX="https://github.com/reallakshman19/Grade9v3.5/actions/runs/"

class Scripts(HTMLParser):
    def __init__(self):super().__init__();self.active=None;self.scripts={}
    def handle_starttag(self,tag,attrs):
        if tag=="script":self.active=dict(attrs).get("id")
    def handle_data(self,data):
        if self.active:self.scripts[self.active]=self.scripts.get(self.active,"")+data
    def handle_endtag(self,tag):
        if tag=="script":self.active=None

class D1EvidenceTiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=INDEX.read_text()
        scripts=Scripts();scripts.feed(cls.page)
        cls.viewer=json.loads(scripts.scripts["band-evidence"])
        cls.metadata=json.loads(scripts.scripts["metadata"])
        cls.band=json.loads(BANDS.read_text())
        cls.tiles={d:json.loads((TILES/"d1"/(d.lower()+".tile.v1.json")).read_text()) for d in DEMANDS}

    def test_q003_original_private_content_and_non_d1_matrix_unchanged(self):
        self.assertEqual(self.metadata["tile_id"],"Q003-MODEL-D2")
        self.assertFalse(self.metadata["source_content_embedded"])
        self.assertEqual(self.metadata["qrt"]["status"],"PROPOSED")
        self.assertIsNone(self.metadata["qrt"]["owner_decision_id"])
        self.assertEqual(self.metadata["golden"]["scope"],"OWNER_APPROVED_VISUAL_INTERACTION_REFERENCE_ONLY")
        cells=self.viewer["cells"];self.assertEqual(len(cells),28)
        self.assertEqual(len(set(x["id"] for x in cells)),28)
        self.assertEqual(len([x for x in cells if x["band"]!="D1"]),21)
        self.assertNotIn("Q003 protected stem",self.page)

    def test_all_d1_source_safe_records_have_immutable_exact_render_evidence(self):
        by_id={x["id"]:x for x in self.viewer["cells"]}
        band_map={x["cell_id"]:x for x in self.band["cells"]}
        for d in DEMANDS:
            with self.subTest(demand=d):
                t=self.tiles[d];id="QRT-"+d+"-D1";view=by_id[id];row=band_map[id]
                self.assertEqual(t["cell_id"],id)
                self.assertEqual(t["primary_demand"],d)
                self.assertEqual(t["schema"],"imo-qrt-cell-evidence/v1")
                self.assertEqual(t["source"]["custody"],"SOURCE_SAFE_AUTHORED_TEST")
                self.assertFalse(t["source"]["question_stem_embedded"])
                self.assertFalse(t["status_dimensions"]["owner_qrt_accepted"])
                self.assertFalse(t["status_dimensions"]["owner_golden_designated"])
                self.assertEqual(t["review"]["decision"],"PENDING")
                self.assertEqual(t["owner"]["qrt_decision"],"PENDING")
                self.assertIsNone(t["owner"]["qrt_decision_id"])
                self.assertTrue(all(t["review"][ask] is None for ask in ASKS))
                self.assertTrue(all(t["cognitive"][x] for x in "XYZW"))
                self.assertTrue(t["generation"]["six_html_sha_verified"])
                self.assertEqual(t["generation"]["gaps"],0)
                self.assertEqual(t["generation"]["renderer_version"],"render_core/2")
                self.assertEqual(t["generation"]["registry_version"],"1.17.0")
                self.assertEqual(t["generation"]["registry_blob_sha"],"591ba061b8771c30fdffc4506aa720ca9ba89335")
                self.assertEqual(len(t["blueprints"]),5)
                self.assertEqual({r["role"] for r in t["blueprints"]},{"CORE1","CORE1A","CORE1B","CORE2A","CORE2B"})
                self.assertEqual({r["filename"] for r in t["generation"]["html"]},set(ROLES))
                self.assertTrue(all(re.fullmatch("[0-9a-f]{64}",r["sha256"]) for r in t["generation"]["html"]))
                self.assertEqual(t["golden"]["comparison_kind"],"SEMANTIC_CROSS_QUESTION_NOT_BYTE_PARITY")
                self.assertEqual(t["golden"]["lock_git_blob_sha"],"888678554c41257e6d96c802f0009983ccbb5328")
                self.assertTrue(t["generation"]["artifact_url"].startswith(ARTIFACT_PREFIX))
                self.assertIn("/artifacts/",t["generation"]["artifact_url"])
                self.assertEqual(view["tile"],"../d1/"+d.lower()+".tile.v1.json")
                self.assertEqual(view["url"],t["generation"]["artifact_url"])
                self.assertEqual(view["ci"],t["generation"]["exact_head_ci_run"])
                self.assertEqual(view["head"],t["generation"]["repo_commit_sha"])
                self.assertEqual(dict(view["role_html_sha256"]),{r["filename"]:r["sha256"] for r in t["generation"]["html"]})
                self.assertEqual(view["owner_decision_id"],None)
                self.assertEqual(row["current_render_artifact"],view["url"])
                self.assertEqual(row["technical_status"],view["state"])
                self.assertEqual(row["qrt_acceptance"],"UNACCEPTED")
                self.assertIsNone(row["owner_decision_id"])

    def test_justify_manual_feedback_examples_do_not_misrepresent_grading(self):
        path=TILES/"d1/justify-reasoning-probes.v1.json"
        p=json.loads(path.read_text())
        self.assertEqual(p["cell_id"],"QRT-JUSTIFY-D1")
        self.assertEqual(p["scope"],"MANUAL_REVIEW_ONLY_NOT_AUTOGRADED_NOT_ACADEMIC_SIGNOFF")
        self.assertEqual(p["source_quality_hold"],"ALTITUDE_WORDING_CLARITY")
        self.assertIsNone(p["owner_decision_id"])
        self.assertEqual(p["academic_decision"],"PENDING")
        self.assertEqual(len(p["rubric"]),5)
        cases={c["id"]:c for c in p["cases"]}
        self.assertEqual(len(cases),16)
        self.assertEqual(cases["numeric_only"]["author_expected_manual_category"],"PARTIAL_OR_UNJUSTIFIED")
        self.assertEqual(cases["same_base_only"]["author_expected_manual_category"],"INCORRECT_REASONING")
        self.assertEqual(cases["valid_det"]["author_expected_manual_category"],"FULL_ALTERNATIVE_WARRANT")
        self.assertEqual(cases["wrong_slanted"]["author_expected_manual_category"],"INCORRECT_REASONING")
        self.assertEqual(cases["wrong_transfer"]["author_expected_manual_category"],"INCORRECT_CONVERSE")
        self.assertEqual(cases["valid_transfer"]["author_expected_manual_category"],"FULL_CONVERSE")
        self.assertTrue(all(c["reviewer_verdict"] is None for c in cases.values()))
        self.assertTrue(all(c["reviewer_name"] is None and c["conflict_declaration"] is None
                            for c in cases.values()))
        self.assertFalse(self.tiles["JUSTIFY"]["review"]["automatic_free_response_grading"])
        self.assertEqual(self.viewer["cells"][6]["feedback_review"],
                         "../d1/justify-reasoning-probes.v1.json")

    def test_84_specific_semantic_questions_without_forged_signoff(self):
        path=TILES/"d1/semantic-challenge-20261013.v1.json"
        r=json.loads(path.read_text())
        self.assertEqual(r["schema"],"imo-qrt-d1-semantic-challenge/v1")
        self.assertTrue(r["authorial_quality_review_only"])
        self.assertEqual(r["coverage"]["accepted_D1"],0)
        self.assertEqual(r["coverage"]["accepted_programme"],0)
        self.assertEqual(len(r["cells"]),7)
        asks=("H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3")
        for c in r["cells"]:
            self.assertEqual(set(c["semantic_asks"]),set(asks))
            self.assertTrue(all(c["semantic_asks"][a]["specific_test"] for a in asks))
            self.assertTrue(all(c["semantic_asks"][a]["qualified_reviewer_verdict"] is None for a in asks))
            self.assertIsNone(c["independent_review"]["academic_verdict"])
            self.assertIsNone(c["independent_review"]["reviewer"])
            self.assertIsNone(c["independent_review"]["owner_qrt_decision_id"])
        self.assertEqual(r["coverage"]["semantic_ask_count"],84)
        self.assertEqual(r["confirmed_defect"]["cell"],"QRT-RETRIEVE-D1")
        self.assertTrue(r["confirmed_defect"]["new_technical_evidence"]["all_six_sha_match"])
        self.assertIn("38412153491",r["confirmed_defect"]["new_technical_evidence"]["ci_run"])
        for c in self.viewer["cells"]:
            if c["band"]=="D1":
                self.assertEqual(c["semantic_challenge"],"../d1/semantic-challenge-20261013.v1.json")

    def test_retrieve_tile_points_at_repaired_actual_HTML_not_leaked_old_output(self):
        t=self.tiles["RETRIEVE"]
        self.assertEqual(t["status_dimensions"]["technical"],"REPAIRED_RENDERED_TEST")
        self.assertIn("38412153491",t["generation"]["exact_head_ci_run"])
        self.assertIn("11823141979",t["generation"]["artifact_url"])
        self.assertEqual(t["source"]["verified_sha"],"c372c0ae7b7d0c04ad2375c02b4e564f3c642936")
        self.assertEqual(t["evidence"]["measured_repair"]["type"],"CONFIRMED_AUTHORING_HINT_LEAK")
        self.assertTrue(t["evidence"]["measured_repair"]["six_html_sha_receipt_matches"])

    def test_repaired_model_and_actual_justify_not_obsolete_inventory(self):
        m=self.tiles["MODEL"];j=self.tiles["JUSTIFY"]
        self.assertIn("11802730066",m["generation"]["artifact_url"])
        self.assertIn("78645b0a6d",m["generation"]["repo_commit_sha"])
        self.assertEqual(m["status_dimensions"]["technical"],"REPAIRED_RENDERED_TEST")
        self.assertIn("11810416794",j["generation"]["artifact_url"])
        self.assertEqual(j["source"]["upstream_candidate_id"],"IMO-G9-ORIGINAL-PRACTICE-003")
        self.assertEqual(j["source"]["source_quality_hold"],"ALTITUDE_WORDING_CLARITY")
        self.assertEqual(j["status_dimensions"]["technical"],"NEW_FIVE_ROLE_RENDERED_TEST")
        self.assertIsNone(j["review"]["qualified_reviewer_name"])
        self.assertEqual(self.band["bands"]["D1"]["reported"]["academic_accepted"],0)
        self.assertEqual(self.band["bands"]["D1"]["reported"]["rendered"],7)
        self.assertEqual(self.band["bands"]["D1"]["historical_reported"]["unstarted"],1)

if __name__=="__main__":unittest.main()
