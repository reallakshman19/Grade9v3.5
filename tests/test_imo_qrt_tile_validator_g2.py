"""Mutation checks for the validator's first tile. All samples are synthetic."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from Shared.tools.imo_qrt_tile_validator_g2 import (
    _article, _html_findings, _mechanical_source, _protected_w, _tag_attributes, inspect
)

SRC = Path(__file__).resolve().parents[1]
REVIEW = json.loads((SRC / "TEST/imo-qrt-tile/qrt-retrieve-d1-review.v1.json").read_text())
QID = "SYN-RETRIEVE-Q001"


def question():
    return {
        "id": QID, "stem": "What is the property?", "options":
            {"A": "alpha", "B": "beta", "C": "gamma", "D": "delta"},
        "answer": {"choice": "B", "value": "beta"},
        "solution": {"derivation": "A legitimate demonstration."},
        "paper_origin_locator": {"question_number": 1},
        "cognitive_classification": {
            "primary_demand": "RETRIEVE", "difficulty_band": "D1",
            "qrt_cell": "QRT-RETRIEVE-D1",
            "difficulty_score": 1, "crux_move": "Recall a property",
            "difficulty_components": {
                "concept_model_selection": 1, "representation_translation": 0,
                "reasoning_chain_length": 0, "algebra_computational_load": 0,
                "trap_exception_sensitivity": 0,
            }
        }
    }


def card(*, lock=True, mouse_only=False, band="D1", nav_override=None):
    lockattrs = " hidden inert" if lock else ""
    nav = ('<span onclick="jumpToCore1(&#x27;poly&#x27;)">Core</span>' if mouse_only else
           '<button type="button" class="qb-badge qb-core-nav" '
           'aria-label="Browse Core modules (topic only) for ' + QID +
           '" onclick="jumpToCore1(' + "'poly'" + ')">Core</button>')
    if nav_override is not None:
        nav = nav_override
    return f"""<article class="qb-question" id="q-{QID}" data-demand="RETRIEVE" data-band="{band}">
      <textarea id="att-{QID}"></textarea>
      <button id="commit-{QID}" type="button"></button>
      <details id="hint2-{QID}"{lockattrs}><summary>Hint 2</summary></details>
      <details id="diag-disc-{QID}"{lockattrs}><summary>diagnose</summary></details>
      <details id="sol-disc-{QID}"{lockattrs}><summary>solution</summary></details>
      {nav}
    </article>"""


def codes(items):
    return {x["code"] for x in items if x["verdict"] == "FAIL"}


class TileMutations(unittest.TestCase):
    def test_exact_tile_pass_shape_without_claiming_academics(self):
        self.assertEqual(codes(_html_findings(card(), question(), {})), set())

    def test_html_missing_card(self):
        self.assertIn("RENDERED_TILE_CARD_MISSING", codes(_html_findings("", question(), {})))

    def test_wrong_rendered_band(self):
        self.assertIn("RENDERED_TILE_ATTRIBUTE_MISMATCH",
                      codes(_html_findings(card(band="D2"), question(), {})))

    def test_solution_cannot_be_directly_openable(self):
        self.assertIn("PRECOMMIT_DISCLOSURE_NOT_LOCKED",
                      codes(_html_findings(card(lock=False), question(), {})))

    def test_core_navigation_must_be_keyboard_activatable(self):
        self.assertIn("CORE_NAV_MOUSE_ONLY_SPAN",
                      codes(_html_findings(card(mouse_only=True), question(), {})))

    def test_native_core_button_is_required(self):
        self.assertIn("CORE_NAV_NATIVE_BUTTON_MISSING",
                      codes(_html_findings(card(nav_override=""), question(), {})))

    def test_native_button_must_have_accessible_name(self):
        wrong = '<button type="button" class="qb-badge qb-core-nav" onclick="jumpToCore1(' + "'poly'" + ')">Core</button>'
        self.assertIn("CORE_NAV_ACCESSIBLE_BUTTON_INVALID",
                      codes(_html_findings(card(nav_override=wrong), question(), {})))

    def test_declared_direct_link_must_render_to_correct_core_unit(self):
        nav = ('<button type="button" class="qb-badge qb-core-nav" '
               'aria-label="Linked Core 1A/1B for test" '
               'onclick="jumpToCoreUnit(' + "'unit-a'" + ')">Core</button>')
        html = card(nav_override=nav)
        self.assertNotIn("CORE_EXPLICIT_LINK_NOT_RENDERED",
                         codes(_html_findings(html, question(), {}, linked_unit_ids=("unit-a",))))
        self.assertIn("CORE_EXPLICIT_LINK_NOT_RENDERED",
                      codes(_html_findings(html, question(), {}, linked_unit_ids=("unit-b",))))

    def test_false_direct_link_without_source_ref_fails(self):
        nav = ('<button type="button" class="qb-badge qb-core-nav" '
               'aria-label="Linked Core 1A/1B for test" '
               'onclick="jumpToCoreUnit(' + "'unit-a'" + ')">Core</button>')
        self.assertIn("CORE_NAV_FALSE_EXACT_LINK",
                      codes(_html_findings(card(nav_override=nav), question(), {})))

    def test_topic_fallback_must_label_itself_topic_only(self):
        nav = ('<button type="button" class="qb-badge qb-core-nav" '
               'aria-label="Exact concept bridge for test" '
               'onclick="jumpToCore1(' + "'poly'" + ')">Core</button>')
        self.assertIn("CORE_TOPIC_FALLBACK_NOT_DISCLOSED",
                      codes(_html_findings(card(nav_override=nav), question(), {})))

    def test_predecessor_disclosure_observation_used(self):
        a = {"affected_question_ids": {"PREATTEMPT_CORRECT_OPTION_EMPHASIZED": [QID]}}
        self.assertIn("PREATTEMPT_CORRECT_OPTION_EMPHASIZED",
                      codes(_html_findings(card(), question(), a)))

    def test_valid_factor_projection(self):
        self.assertEqual(_mechanical_source(question(), "synthetic.json"), [])

    def test_score_mismatch_fails_exact_question(self):
        q = question()
        q["cognitive_classification"]["difficulty_score"] = 2
        self.assertIn("FIVE_FACTOR_SCORE_MISMATCH", codes(_mechanical_source(q, "synthetic.json")))

    def test_witness_is_conservative_and_change_reopens_review(self):
        q = question()
        q["id"] = "SOF-IMO-G09-L1-2025-26-B-Q037"
        q["hint_ladder"] = {"hint2_tactical_step": "Probability $= 1/3$."}
        self.assertIn("HINT2_REVEALS_D1_PROTECTED_FINAL_DECISION", codes(_protected_w(q, REVIEW)))
        q["hint_ladder"]["hint2_tactical_step"] = "Count favorable outcomes."
        changed = _protected_w(q, REVIEW)
        self.assertEqual(codes(changed), set())
        self.assertIn("HINT2_CHANGED_PROTECTED_W_REVIEW_REQUIRED",
                      {x["code"] for x in changed if x["verdict"] == "REVIEW_REQUIRED"})

    def test_reject_nonsha_even_on_synthetic_input(self):
        with self.assertRaises(ValueError):
            inspect(SRC, source_sha="main")

    def test_reject_other_tile_labels(self):
        with self.assertRaises(ValueError):
            inspect(SRC, source_sha="a" * 40, tile="QRT-UNKNOWN-D4")

    def test_html_attributes_parse_hidden_and_inert(self):
        found = _tag_attributes(card(), "details", "sol-disc-" + QID)
        self.assertIsNotNone(found)
        self.assertIn("hidden", found)
        self.assertIn("inert", found)


if __name__ == "__main__":
    unittest.main()
