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
    EVIDENCE, CENSUS, PilotHoldError, validate,
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
