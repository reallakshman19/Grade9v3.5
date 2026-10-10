"""Negative-falsifier checks for research-only first SOF source Core2 pilot."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(ROOT))
from validate_core2_pilot_hold import (  # noqa: E402
    EVIDENCE, CENSUS, PilotHoldError, validate, no_copied_source_payload,
)


class Core2PilotHoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.census = json.loads(CENSUS.read_text(encoding="utf-8"))

    def rejects(self, change, census=False):
        packet = copy.deepcopy(self.packet)
        source = copy.deepcopy(self.census)
        change(source if census else packet)
        with self.assertRaises(PilotHoldError):
            validate(packet, source)

    def test_readonly_census_and_pilot_on_hold(self):
        r = validate(self.packet, self.census)
        self.assertEqual(r["pilot"], "SOF-IMO-G09-SAMPLE-2026-27-Q004")
        self.assertEqual((r["total_source_positions"],
                          r["core2_eligible"], r["core2_admitted"]), (68, 0, 0))
        self.assertEqual(r["status"], "SOURCE_CUSTODY_HOLD")

    def test_missing_one_of_68_rejected(self):
        self.rejects(lambda c: c["records"].pop(), census=True)

    def test_replaced_other_position_rejected(self):
        self.rejects(lambda c: c["records"][0].update(
            core2_eligible=True), census=True)

    def test_pilot_identity_swap_rejected(self):
        self.rejects(lambda p: p.update(
            pilot_question_id="SOF-IMO-G09-SAMPLE-2026-27-Q003"))

    def test_wrong_printed_page_rejected(self):
        self.rejects(lambda p: p["source"].update(
            pdf_page_index_zero_based=1))

    def test_swapped_source_key_rejected(self):
        self.rejects(lambda p: p["source"].update(
            printed_key_choice_sighted="C"))

    def test_unique_choice_from_derived_x_zero_witness(self):
        self.assertEqual(validate(self.packet, self.census)["core2_admitted"], 0)
        values = self.packet["math_check"]["distractor_exclusion_spotcheck"]
        self.assertEqual(values["witness_x"], 0)
        self.assertEqual(values["source_output_at_witness"], -1)
        self.assertTrue(all(v != -1 for v in
                            values["other_choice_outputs_at_witness"].values()))
        self.assertEqual(values["unique_matching_choice"], "B")

    def test_mutated_distractor_witness_rejected(self):
        self.rejects(lambda p: p["math_check"][
            "distractor_exclusion_spotcheck"].update(witness_x=1))

    def test_mutated_distractor_output_rejected(self):
        self.rejects(lambda p: p["math_check"][
            "distractor_exclusion_spotcheck"][
                "other_choice_outputs_at_witness"].update(C=-1))

    def test_extra_answer_choice_rejected(self):
        self.rejects(lambda p: p["math_check"][
            "distractor_exclusion_spotcheck"][
                "other_choice_outputs_at_witness"].update(E=5))

    def test_forged_unique_answer_choice_rejected(self):
        self.rejects(lambda p: p["math_check"][
            "distractor_exclusion_spotcheck"].update(unique_matching_choice="A"))

    def test_copied_source_option_text_claim_rejected(self):
        self.rejects(lambda p: p["math_check"][
            "distractor_exclusion_spotcheck"].update(
                original_source_option_text_copied=True))

    def test_fabricated_math_approval_rejected(self):
        self.rejects(lambda p: p["math_check"][
            "distractor_exclusion_spotcheck"].update(
                authority="INDEPENDENT_PUBLISHER_APPROVED"))

    def test_missing_visual_component_rejected(self):
        self.rejects(lambda p: p["observation"][
            "visual_component_sightings"].pop("captions"))

    def test_visual_options_status_cannot_become_publisher_option_text(self):
        self.rejects(lambda p: p["observation"][
            "visual_component_sightings"].update(
                options=["copied source choices"]))

    def test_visual_stem_status_is_not_copied_stem(self):
        # The typed component *name* is allowed; its value is a fixed status.
        packet = copy.deepcopy(self.packet)
        self.assertEqual(packet["observation"]["visual_component_sightings"]["stem"],
                         "SEEN_ON_RENDER_ONLY")
        self.assertEqual(validate(packet, self.census)["status"],
                         "SOURCE_CUSTODY_HOLD")

    def test_visual_stem_cannot_embed_publisher_stem_text(self):
        self.rejects(lambda p: p["observation"][
            "visual_component_sightings"].update(stem="Original question wording"))

    def test_standalone_payload_guard_rejects_source_stem_in_status(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["visual_component_sightings"]["stem"] = (
            "Unlicensed original source wording"
        )
        with self.assertRaises(PilotHoldError):
            no_copied_source_payload(packet)

    def test_standalone_payload_guard_rejects_original_option_list(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["visual_component_sightings"]["options"] = [
            "A", "B", "C", "D"
        ]
        with self.assertRaises(PilotHoldError):
            no_copied_source_payload(packet)

    def test_original_stem_payload_still_forbidden_outside_status_path(self):
        self.rejects(lambda p: p["source"].update(
            stem="Original question wording"))

    def test_original_option_list_still_forbidden_outside_status_path(self):
        self.rejects(lambda p: p["source"].update(
            options=["copied question choices"]))

    def test_visual_component_upgraded_without_bytes_rejected(self):
        self.rejects(lambda p: p["observation"][
            "visual_component_sightings"].update(stem="VERIFIED_WITH_SOURCE_BYTES"))

    def test_rendered_table_not_discarded_as_nonvisual(self):
        self.rejects(lambda p: p["observation"][
            "visual_component_sightings"].update(
                figures="NOT_PRESENT_ON_VIEWED_ITEM"))

    def test_key_sighting_cannot_claim_custody(self):
        self.rejects(lambda p: p["observation"][
            "visual_component_sightings"].update(
                answer_or_rubric="VERIFIED_IN_RESTRICTED_SOURCE"))

    def test_self_check_not_independent_principal(self):
        self.rejects(lambda p: p["observation"].update(
            principal_independence="INDEPENDENT"))

    def test_self_check_mode_not_external_signoff(self):
        self.rejects(lambda p: p["observation"].update(
            source_sighting_review_mode="THIRD_PARTY_APPROVED"))

    def test_visual_spotcheck_cannot_claim_durable_custody(self):
        self.rejects(lambda p: p["observation"].update(
            visual_component_custody_status="VERIFIED"))

    def test_modified_math_result_rejected(self):
        self.rejects(lambda p: p["math_check"].update(
            computed_output_values=[-3, -1, 2, 3]))

    def test_source_figure_bytes_rejected(self):
        self.rejects(lambda p: p.update(source_figure_bytes="fake-pixel-content"))

    def test_unknown_publication_field_rejected(self):
        self.rejects(lambda p: p["decision"].update(
            learner_route="/public/imo/fake-source-core2"))

    def test_unreviewed_rights_alias_rejected(self):
        self.rejects(lambda p: p["custody"].update(
            publisher_permission="AUTHORIZED"))

    def test_question_stem_reproduction_rejected(self):
        self.rejects(lambda p: p["source"].update(stem="unlicensed source"))

    def test_fabricated_pdf_digest_rejected(self):
        self.rejects(lambda p: p["custody"].update(
            retained_document_sha256="a" * 64))

    def test_fake_licence_rejected(self):
        self.rejects(lambda p: p["custody"].update(
            rights_to_reproduce="GRANTED"))

    def test_fake_external_reference_rejected(self):
        self.rejects(lambda p: p["custody"].update(
            external_reference_rights="AUTHORIZED"))

    def test_faked_independent_review_rejected(self):
        self.rejects(lambda p: p["custody"].update(
            independent_source_reviewer="claimed"))

    def test_faked_component_verified_rejected(self):
        self.rejects(lambda p: p["custody"].update(
            seven_component_custody_independently_verified=True))

    def test_premature_core2_admission_rejected(self):
        self.rejects(lambda p: p["decision"].update(core2_eligible=True))

    def test_unauthorized_learner_publication_rejected(self):
        self.rejects(lambda p: p["decision"].update(learner_published=True))

    def test_disposition_of_other_67_cannot_change(self):
        self.rejects(lambda p: p["decision"].update(all_other_67_positions="DONE"))

    def test_ledger_forged_digest_rejected(self):
        self.rejects(lambda c: c["records"][0].update(
            document_retained_sha256="a" * 64), census=True)

    def test_ledger_component_relabel_rejected(self):
        self.rejects(lambda c: c["records"][0]["component_verification"].update(
            complete_option_order="VERIFIED"), census=True)


if __name__ == "__main__":
    unittest.main()
