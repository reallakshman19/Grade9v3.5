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

    def test_synthesize_maths_equivalence_and_unresolved_demand_classification(self):
        t=self.tiles["SYNTHESIZE"]
        self.assertEqual(t["status_dimensions"]["technical"],"REPAIRED_RENDERED_TEST")
        self.assertIn("38427757190",t["generation"]["exact_head_ci_run"])
        self.assertIn("11828784099",t["generation"]["artifact_url"])
        self.assertEqual(t["source"]["verified_sha"],"f9008c6dc4642d45798d23ddd06a51a4a33f540b")
        self.assertEqual(t["evidence"]["measured_repair"]["type"],
                         "AUTHORING_HINT_AND_MATHEMATICAL_EQUIVALENCE")
        self.assertTrue(t["evidence"]["measured_repair"]["grouped_and_distributed_count_both_valid"])
        self.assertEqual(t["evidence"]["measured_repair"]["human_demand_verdict"],"PENDING")
        q=json.loads((TILES/"d1/semantic-challenge-20261013.v1.json").read_text())
        challenge=next(c for c in q["cells"] if c["cell_id"]=="QRT-SYNTHESIZE-D1")
        self.assertIn("reduces to MODEL equal-group",challenge["adjacent_band_and_demand_challenge"])
        self.assertIn("4×3+4×2",challenge["author_mathematical_crosscheck"])
        self.assertIsNone(challenge["independent_review"]["academic_verdict"])
        self.assertEqual(self.band["bands"]["D1"]["reported"]["academic_accepted"],0)

    def test_synthesize_contrast_is_unsigned_and_falsifiable(self):
        t=self.tiles["SYNTHESIZE"]
        contrast_path=TILES/"d1/synthesize-demand-contrast.v1.json"
        j=json.loads(contrast_path.read_text())
        self.assertEqual(j["schema"],"imo-qrt-d1-primary-demand-contrast/v1")
        self.assertEqual(j["cell_id"],"QRT-SYNTHESIZE-D1")
        self.assertIn("4×3+4×2=20",j["pinned_actual_evidence"]["valid_equal_counts"])
        self.assertEqual(j["pinned_actual_evidence"]["CI"],t["generation"]["exact_head_ci_run"])
        self.assertEqual(j["pinned_actual_evidence"]["html"],t["generation"]["artifact_url"])
        self.assertEqual(j["source_authority"]["template_id"],"QRT-SYNTHESIZE-D1")
        self.assertEqual(len(j["conflicting_hypotheses"]),3)
        self.assertTrue(all(x["reviewer_result"] is None for x in j["conflicting_hypotheses"]))
        self.assertEqual(len(j["falsifiable_review_protocol"]),6)
        self.assertIsNone(j["independent_review"]["primary_demand_verdict"])
        self.assertIsNone(j["independent_review"]["qualified_reviewer_name"])
        self.assertIsNone(j["owner"]["decision_id"])
        self.assertEqual(self.viewer["cells"][5]["demand_contrast"],
                         "../d1/synthesize-demand-contrast.v1.json")

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


    def test_synthesize_bridge_ablation_controls(self):
        j=json.loads((TILES/"d1/synthesize-bridge-ablation.v1.json").read_text())
        t=self.tiles["SYNTHESIZE"]
        x={c["id"]:c for c in j["conditions"]}
        self.assertEqual(j["baseline"]["source_blob"],t["source"]["verified_sha"])
        self.assertEqual(j["baseline"]["native_artifact"],t["generation"]["artifact_url"])
        self.assertEqual(len(x),5)
        a=x["A_CURRENT"]["values"];b=x["B_BRIDGE_SUPPLIED"]["values"]
        self.assertEqual(a["groups"]*(a["blue_per_group"]+a["red_per_group"]),20)
        self.assertEqual(b["groups"]*b["unit_total_given"],20)
        self.assertEqual(b["unit_total_given"],a["blue_per_group"]+a["red_per_group"])
        z=x["C_ALREADY_TAUGHT"]["values"]
        self.assertEqual(z["groups"]*(z["first_per_group"]+z["second_per_group"]),9)
        w=x["D_MISSING_COMPONENT_DIAGNOSIS"]
        self.assertEqual(3+2*4,w["values"]["wrong_count"])
        self.assertEqual(w["omitted_blue_count"],20-w["values"]["wrong_count"])
        e=x["E_CHANGED_COMPOSITION"]["values"]
        self.assertEqual(e["standard_units"]*(e["standard_blue"]+e["standard_red"])
                         +e["changed_blue"]+e["changed_red"],19)
        self.assertTrue(all(v is None or v==[] for v in j["review"].values()))
        self.assertEqual(j["owner"]["qrt_decision"],"PENDING")


    def test_justify_reasoning_feedback_manual_review_worksheet(self):
        """The 16 author probes are linked, not silently promoted to human verdicts."""
        p=json.loads((TILES/"d1/justify-reasoning-probes.v1.json").read_text())
        w=json.loads((TILES/"d1/justify-feedback-review-sheet.v1.json").read_text())
        tile=self.tiles["JUSTIFY"]
        self.assertEqual(w["schema"],"imo-qrt-justify-d1-manual-feedback-review/v1")
        self.assertEqual(w["scope"],
                         "REVIEW_WORKSHEET_ONLY_NO_AUTOGRADING_NO_LEARNER_TRIAL_NO_ACADEMIC_SIGNOFF")
        self.assertEqual(w["cell_id"],p["cell_id"])
        self.assertEqual(w["hold"],p["source_quality_hold"])
        self.assertEqual(w["protected_W"],tile["cognitive"]["W"])
        self.assertEqual(w["provenance"]["learner_source_blob_sha"],
                         tile["source"]["verified_sha"])
        self.assertEqual(w["provenance"]["existing_native_html_artifact"],
                         tile["generation"]["artifact_url"])
        self.assertEqual(w["provenance"]["owner_frozen_golden_blob"],
                         tile["golden"]["lock_git_blob_sha"])
        self.assertEqual(tile["review"]["manual_feedback_worksheet"],
                         "d1/justify-feedback-review-sheet.v1.json")
        self.assertEqual([x["id"] for x in w["criteria"]],
                         [x["id"] for x in p["rubric"]])
        cases={c["id"]:c for c in p["cases"]}
        rows={c["probe_id"]:c for c in w["case_reviews"]}
        self.assertEqual(len(rows),16)
        self.assertEqual(set(rows),set(cases))
        for key,row in rows.items():
            with self.subTest(probe=key):
                self.assertEqual(row["author_expected_category_reference"],
                                 cases[key]["author_expected_manual_category"])
                self.assertTrue(row["feedback_risk_to_check"])
                self.assertEqual(set(row["manual_review"]["rubric"]),
                                 {x["id"] for x in p["rubric"]})
                self.assertTrue(all(v is None for v in
                                    row["manual_review"]["rubric"].values()))
                self.assertTrue(all(v is None for k,v in
                                    row["manual_review"].items() if k!="rubric"))
        self.assertIsNone(w["comprehension_trials"]["actual_participant_count"])
        self.assertIsNone(w["comprehension_trials"]["observations"])
        self.assertTrue(all(v is None for k,v in w["reviewer"].items()
                            if k!="case_verdict_count"))
        self.assertEqual(w["reviewer"]["case_verdict_count"],0)
        self.assertEqual(w["owner"],{"qrt_decision":"PENDING","decision_id":None})
        self.assertEqual(p["academic_decision"],"PENDING")
        self.assertFalse(tile["review"]["automatic_free_response_grading"])


    def test_d1_evidence_freshness_detects_stale_or_forged_refs(self):
        """Cross-record consistency, not a new download/rehash of hosted ZIP bytes."""
        def errors(t,v,row):
            problems=[]
            def same(label,*values):
                if any(x!=values[0] for x in values[1:]):
                    problems.append(label)
            source=t["source"];gen=t["generation"];owner=t["owner"]
            code=gen["repo_commit_sha"]
            same("source-commit",source["source_code_commit"],code,
                 v["head"],row["current_render_exact_head"])
            same("source-path",v["source"],
                 "https://github.com/reallakshman19/Grade9v3.5/blob/"
                 +code+"/"+source["source_path"])
            same("manifest-path",v["manifest"],
                 "https://github.com/reallakshman19/Grade9v3.5/blob/"
                 +code+"/"+gen["manifest_path"])
            same("source-blob-format",
                 bool(re.fullmatch(r"[0-9a-f]{40}",source["verified_sha"])),True)
            run=re.search(r"/runs/([0-9]+)$",gen["exact_head_ci_run"])
            artifact=re.search(r"/runs/([0-9]+)/artifacts/([0-9]+)$",
                               gen["artifact_url"])
            if not run or not artifact or run.group(1)!=artifact.group(1):
                problems.append("run-artifact-identity")
            same("run-url",gen["exact_head_ci_run"],v["ci"],
                 row["current_renderer_ci_run"])
            same("artifact-url",gen["artifact_url"],v["url"],
                 row["current_render_artifact"])
            same("cell-identity",t["cell_id"],v["id"],row["cell_id"])
            same("technical-status",t["status_dimensions"]["technical"],
                 v["state"],row["technical_status"])
            role_shas={x["filename"]:x["sha256"] for x in gen["html"]}
            if (len(gen["html"])!=6 or set(role_shas)!=set(ROLES) or
                    not all(re.fullmatch(r"[0-9a-f]{64}",x)
                            for x in role_shas.values())):
                problems.append("six-role-digest-shape")
            same("html-shas",role_shas,dict(v["role_html_sha256"]),
                 {x["filename"]:x["sha256"]
                  for x in row["current_html_shas_sha256"]})
            same("verified-flags",gen["six_html_sha_verified"],
                 v["renderer_verified"],row["technical_sha6_verified"])
            same("registry",gen["registry_blob_sha"],v["registry_sha"])
            same("source-hold",source["source_quality_hold"],
                 v["source_quality_hold"])
            same("owner-id",owner["qrt_decision_id"],v["owner_decision_id"],
                 row["owner_decision_id"])
            accepted=t["status_dimensions"]["owner_qrt_accepted"]
            if accepted:
                if (not owner["qrt_decision_id"] or
                    owner["qrt_decision"]!="ACCEPT" or
                    row["qrt_acceptance"]!="ACCEPTED" or
                    not t["review"]["qualified_reviewer_name"] or
                    not t["review"]["conflict_declaration"]):
                    problems.append("ungated-acceptance")
            elif (owner["qrt_decision"]!="PENDING" or
                  row["qrt_acceptance"]!="UNACCEPTED" or
                  owner["qrt_decision_id"] is not None or
                  v["reviewer"] is not None or
                  t["review"]["decision"]!="PENDING"):
                problems.append("pending-disposition")
            return problems

        by_view={x["id"]:x for x in self.viewer["cells"]}
        by_band={x["cell_id"]:x for x in self.band["cells"]}
        for demand in DEMANDS:
            t=self.tiles[demand]
            v=by_view[t["cell_id"]];row=by_band[t["cell_id"]]
            with self.subTest(cell=t["cell_id"]):
                self.assertEqual(errors(t,v,row),[])

        # Deliberate corruptions must fail even if the old 'verified' flag is True.
        t=self.tiles["SYNTHESIZE"]
        v=by_view[t["cell_id"]];row=by_band[t["cell_id"]]
        def clone(x):
            return json.loads(json.dumps(x))
        stale=clone(t)
        stale["source"]["source_code_commit"]="0"*40
        self.assertIn("source-commit",errors(stale,v,row))
        wrong_run=clone(t)
        wrong_run["generation"]["artifact_url"]=(
            wrong_run["generation"]["artifact_url"].replace("38427757190",
                                                             "38427757191"))
        self.assertIn("run-artifact-identity",errors(wrong_run,v,row))
        bad_shas=clone(v)
        bad_shas["role_html_sha256"][0][1]="0"*64
        self.assertIn("html-shas",errors(t,bad_shas,row))
        forged_accept=clone(t)
        forged_accept["status_dimensions"]["owner_qrt_accepted"]=True
        forged_accept["owner"]["qrt_decision"]="ACCEPT"
        self.assertIn("ungated-acceptance",errors(forged_accept,v,row))


    def test_qualified_academic_handoff_is_source_pinned_and_unsigned(self):
        packet=TILES/"d1/QUALIFIED-REVIEW-HANDOFF-20261014.md"
        text=packet.read_text()
        self.assertIn("source-safe authored TEST review handoff",text)
        self.assertIn("QUALIFIED_REVIEWER_UNVERIFIED",text)
        self.assertIn("0/28",text)
        self.assertIn("## 3. SYNTHESIZE-D1",text)
        self.assertIn("## 4. JUSTIFY-D1",text)
        self.assertIn("synthesize-bridge-ablation.v1.json",text)
        self.assertIn("justify-feedback-review-sheet.v1.json",text)
        for demand in ("SYNTHESIZE","JUSTIFY"):
            with self.subTest(demand=demand):
                t=self.tiles[demand]
                self.assertEqual(t["review"]["qualified_reviewer_handoff"],
                                 "d1/QUALIFIED-REVIEW-HANDOFF-20261014.md")
                self.assertIn(t["source"]["verified_sha"],text)
                self.assertIn(t["generation"]["artifact_url"],text)
                self.assertIsNone(t["review"]["qualified_reviewer_name"])
                self.assertIsNone(t["owner"]["qrt_decision_id"])
                self.assertEqual(t["owner"]["qrt_decision"],"PENDING")

if __name__=="__main__":unittest.main()
