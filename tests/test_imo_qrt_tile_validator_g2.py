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


def card(*, lock=True, mouse_only=False, band="D1"):
    lockattrs = " hidden inert" if lock else ""
    nav = '<span onclick="jumpToCore1(&#x27;poly&#x27;)">Core</span>' if mouse_only else '<button onclick="jumpToCore1(&#x27;poly&#x27;)">Core</button>'
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
        self.assertEqual(_protected_w(q, REVIEW), [])

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
