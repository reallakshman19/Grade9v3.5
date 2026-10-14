"""r5-01 source-safe reconciliation invariants; technical evidence != acceptance."""
import json
import re
import unittest
from pathlib import Path

LEDGER = (
    Path(__file__).resolve().parents[1]
    / "TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json"
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
ROLES = {"core1.html", "core1a.html", "core1b.html", "core2a.html", "core2b.html", "index.html"}
DEMANDS = {"RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"}


class ReconciledNativeArtifactLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_unique_28_demand_band_cells(self):
        rows = self.doc["rows"]
        self.assertEqual(len(rows), 28)
        ids = {r["cell_id"] for r in rows}
        self.assertEqual(len(ids), 28)
        self.assertEqual(ids, {f"QRT-{d}-{b}" for d in DEMANDS for b in ("D1", "D2", "D3", "D4")})

    def test_exact_sources_and_all_six_html_hashes_are_present(self):
        rows = self.doc["rows"]
        for r in rows:
            with self.subTest(cell=r["cell_id"]):
                self.assertTrue(r["source"]["path"].startswith("TEST/"))
                self.assertTrue(r["manifest"]["path"].startswith("TEST/"))
                self.assertRegex(r["source"]["commit"], SHA1)
                self.assertRegex(r["source"]["git_blob_sha"], SHA1)
                self.assertRegex(r["manifest"]["git_blob_sha"], SHA1)
                shas = r["artifact"]["native_html_sha256"]
                self.assertEqual(set(shas), ROLES)
                self.assertTrue(all(SHA256.fullmatch(s) for s in shas.values()))
                self.assertEqual(r["frozen_golden"]["structural_roles_matching"], 5)
                self.assertEqual(r["renderer"]["gaps"], [])
                self.assertTrue(
                    r["renderer"]["receipt_shas_matching"] == 6
                    or r["renderer"].get("adoption_ledger_sha256_matching") == 6
                )

    def test_academic_and_owner_gates_are_not_silently_accepted(self):
        self.assertEqual(self.doc["summary"]["owner_accepted"], 0)
        for r in self.doc["rows"]:
            self.assertFalse(r["owner_qrta_accepted"])
            self.assertFalse(r["owner_golden_designated"])
            self.assertFalse(r["release_authorized"])
            self.assertEqual(r["academic_review"], "QUALIFIED_INDEPENDENT_REVIEW_PENDING")
            self.assertEqual(r["frozen_golden"]["semantic_technique_verdict"], "UNREVIEWED")

    def test_independent_reviewer_routing_remains_unassigned(self):
        counts = {211: 0, 214: 0, 234: 0}
        for r in self.doc["rows"]:
            expected = 234 if r["band"] != "D2" else (211 if r["demand"] in ("RETRIEVE", "MODEL") else 214)
            self.assertEqual(r["independent_reviewer_nomination_issue"], expected)
            self.assertIsNone(r["nominated_independent_reviewer"])
            self.assertIsNone(r["qualified_independent_signed_verdict_id"])
            counts[expected] += 1
        self.assertEqual(counts, {211: 2, 214: 5, 234: 21})
        self.assertEqual(sum(r["critical_educational_review_hold"] for r in self.doc["rows"]), 8)

    def test_d2_model_choice_repair_native_source_and_academic_hold(self):
        row = next(r for r in self.doc["rows"] if r["cell_id"] == "QRT-MODEL-D2")
        self.assertEqual(row["source"]["commit"], "d450d0f0cda25c51c0232db31e6592588634a90b")
        self.assertEqual(row["source"]["git_blob_sha"], "db87b5a4a7bc807e0680a64417f2c6ca5ca08cf3")
        self.assertEqual(row["manifest"]["git_blob_sha"], "313320473b91968f599424b30561f035e9089aa8")
        self.assertEqual(row["artifact"]["id"], 11872590321)
        self.assertEqual(row["artifact"]["run"], 38517197094)
        self.assertEqual(row["renderer"]["digest"], "0fb022852fc80858")
        self.assertEqual(row["renderer"]["semantic_digest"], "480f365c7fb96c57")
        self.assertTrue(row["critical_educational_review_hold"])
        self.assertIn("EDUCATIONAL_HOLD", row["technical_adoption_status"])
        self.assertIn("MODEL vs APPLY", row["educational_hold_reason"])
        self.assertEqual(row["independent_reviewer_nomination_issue"], 211)
        self.assertFalse(row["owner_qrta_accepted"])
        proof = row["model_d2_source_choice_repair_provenance"]
        self.assertEqual(proof["repair_pr"], 245)
        self.assertEqual(proof["prior_artifact_id"], 11773779616)
        self.assertEqual(proof["corrected_artifact_id"], row["artifact"]["id"])
        self.assertEqual(proof["source_repaired_blob"], row["source"]["git_blob_sha"])
        self.assertEqual(proof["manifest_unchanged_blob"], row["manifest"]["git_blob_sha"])
        self.assertEqual(set(proof["prior_six_html_sha256"]), ROLES)
        self.assertEqual(proof["corrected_six_html_sha256"], row["artifact"]["native_html_sha256"])
        self.assertTrue(all(proof["prior_six_html_sha256"][k] !=
                            row["artifact"]["native_html_sha256"][k] for k in ROLES))
        self.assertEqual(proof["qualified_review_status"], "PENDING_MODEL_D2_VS_APPLY")
        self.assertTrue(any("DO_NOT_QRT_ADOPT_PRIOR_MODEL_D2_ARTIFACT_11773779616" in n
                            for n in row["do_not_adopt_original_leaking_or_superseded"]))

    def test_d4_retrieve_corrected_native_and_qrt_qualification_hold(self):
        row = next(r for r in self.doc["rows"] if r["cell_id"] == "QRT-RETRIEVE-D4")
        self.assertEqual(row["source"]["commit"], "8ffa008e1bbd03898751af4380762178697fb715")
        self.assertEqual(row["source"]["git_blob_sha"], "b9de3db24eb414075a50d0b36298a6306f26056b")
        self.assertEqual(row["manifest"]["git_blob_sha"], "c4ed1576da7880c9aaf04cfb1cdb2c775e1f9d12")
        self.assertEqual(row["artifact"]["id"], 11842190265)
        self.assertEqual(row["artifact"]["run"], 38455006076)
        self.assertEqual(row["renderer"]["digest"], "431bd7078122a90d")
        self.assertTrue(row["critical_educational_review_hold"])
        self.assertIn("EDUCATIONAL_HOLD", row["technical_adoption_status"])
        self.assertIn("Y=UNKNOWN", row["educational_hold_reason"])
        self.assertTrue(any("DO_NOT_QRT_ADOPT_OLD_ARTIFACT_11823696124" in n
                            for n in row["do_not_adopt_original_leaking_or_superseded"]))
        old = row["d4_retrieve_leak_repair_provenance"]
        self.assertEqual(old["old_native_artifact_id"], 11823696124)
        self.assertEqual(old["corrected_native_artifact_id"], 11842190265)
        self.assertEqual(old["source_old_blob"], "27791fbd4735ecdbfda107b0087c16a68bfd8753")
        self.assertEqual(old["source_repaired_blob"], row["source"]["git_blob_sha"])
        self.assertEqual(old["manifest_unchanged_blob"], row["manifest"]["git_blob_sha"])
        self.assertEqual(set(old["old_native_six_html_sha256"]), ROLES)
        self.assertEqual(old["corrected_native_six_html_sha256"], row["artifact"]["native_html_sha256"])
        self.assertTrue(all(old["old_native_six_html_sha256"][k] !=
                            row["artifact"]["native_html_sha256"][k] for k in ROLES))
        self.assertEqual(old["qualified_review_status"], "PENDING_RETRIEVE_D4_Y_UNKNOWN")
        self.assertFalse(row["owner_qrta_accepted"])

    def test_justify_d2_ai_content_review_does_not_impersonate_qualified_signature(self):
        signed = [(r["cell_id"], r["ai_content_review"]) for r in self.doc["rows"]
                  if r.get("ai_content_review") is not None]
        self.assertEqual(len(signed), 1)
        cell, packet = signed[0]
        self.assertEqual(cell, "QRT-JUSTIFY-D2")
        self.assertEqual(packet["verdict"], "PASS_MATH_AND_COGNITIVE_D2")
        self.assertEqual(packet["human_academic_credentials"], "UNVERIFIED")
        self.assertEqual(packet["owner_qualification_ruling"], "PENDING")
        self.assertIsNone(packet["owner_cell_decision_id"])
        self.assertEqual(packet["reviewer_authored_or_fixed_cell"], False)
        self.assertTrue(packet["source"].startswith("https://github.com/reallakshman19/Common/"))
        self.assertTrue(all(r["qualified_independent_signed_verdict_id"] is None
                            for r in self.doc["rows"]))

    def test_question_first_d3_classification_holds_are_preserved(self):
        by_id = {r["cell_id"]: r for r in self.doc["rows"]}
        for cell in ("QRT-RETRIEVE-D3", "QRT-MODEL-D3"):
            row = by_id[cell]
            self.assertTrue(row["critical_educational_review_hold"])
            self.assertTrue(row.get("educational_hold_reason"))
            self.assertIn("EDUCATIONAL_HOLD", row["technical_adoption_status"])
            self.assertTrue(any("DO_NOT_QRT_ADOPT" in x for x in row["do_not_adopt_original_leaking_or_superseded"]))

    def test_synthesize_d3_adopts_full_source_exact_head_without_owner_approval(self):
        row = next(r for r in self.doc["rows"] if r["cell_id"] == "QRT-SYNTHESIZE-D3")
        self.assertFalse(row["critical_educational_review_hold"])
        self.assertEqual(row["source"]["commit"], "4d4a074d9f93e1eeac612679784224d4e250fb49")
        self.assertEqual(row["source"]["git_blob_sha"], "a8168bb41f7133e40e3bcaa1389562361d68901e")
        self.assertIn("TWO_FIELD_SOURCE_CORRECTED_NATIVE_SHA_VERIFIED", row["technical_adoption_status"])
        self.assertEqual(row["artifact"]["id"], 11862463956)
        self.assertEqual(row["artifact"]["run"], 38493751567)
        self.assertEqual(row["artifact"]["member_prefix"], "imo182-qrt/d3/synthesize/")
        self.assertEqual(row["artifact"]["scoped_native_artifact_id"], 11863710538)
        self.assertTrue(row["artifact"]["archive_role_sha_equal_to_intermediate"])
        self.assertFalse(row["owner_qrta_accepted"])
        self.assertEqual(row["academic_review"], "QUALIFIED_INDEPENDENT_REVIEW_PENDING")
        self.assertTrue(any("NOT_FULL_SOURCE_CORRECTION" in n for n in
                            row["do_not_adopt_original_leaking_or_superseded"]))
        watch = row["source_supersession_watch"]
        self.assertEqual(watch["archived_main_label_fixed_sha"],
                         "b852966af06a54b7a594f6ab12653af341f6d836")
        self.assertEqual(watch["successor_complete_source_sha"], row["source"]["git_blob_sha"])
        self.assertEqual(set(watch["corrected_fields"]), {
            "questions[1].family_exposure.closure",
            "questions[2].family_exposure.closure",
        })
        self.assertEqual(watch["transfer_closure_projection"], "NOT_RENDERED_IN_NATIVE_CORE2B")
        self.assertEqual(watch["new_successor_artifact_id"], 11862463956)
        self.assertEqual(watch["new_scoped_native_artifact_id"], 11863710538)
        self.assertEqual(watch["new_exact_head_verdict"], "SUCCESS_M3_AND_SCOPED_NATIVE_6_OF_6_RECOMPUTED")
        self.assertTrue(watch["identical_native_html_sha_as_intermediate"])
        self.assertFalse(watch["may_replace_archived_six_html_hashes"])

    def test_separate_d4_ledger_and_corrected_d3_supersession(self):
        self.assertEqual(
            sum(r["renderer"].get("adoption_ledger_sha256_matching", 0) for r in self.doc["rows"]),
            30,
        )
        synth = next(r for r in self.doc["rows"] if r["cell_id"] == "QRT-SYNTHESIZE-D3")
        self.assertEqual(synth["artifact"]["id"], 11862463956)
        self.assertTrue(any("SUPERSEDED" in note for note in synth["do_not_adopt_original_leaking_or_superseded"]))


if __name__ == "__main__":
    unittest.main()
