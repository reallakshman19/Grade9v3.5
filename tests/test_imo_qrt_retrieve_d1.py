"""Independent QRT-RETRIEVE-D1 fail-closed synthetic falsifiers."""
from __future__ import annotations
import unittest

from Shared.tools.imo_qrt_retrieve_d1 import answer_leaked, inspect_card, normalized


ID = "SYN-RETRIEVE-D1-001"


def record(*, score=0, answer="1/3", hint1="Recall equally likely outcomes.",
           hint2="Count favorable cases, then total cases."):
    return {"id": ID, "answer": {"choice": "A", "value": answer},
            "hint_ladder": {"hint1_conceptual_nudge": hint1,
                            "hint2_tactical_step": hint2},
            "cognitive_classification": {
                "primary_demand": "RETRIEVE", "difficulty_band": "D1",
                "difficulty_score": score,
                "qrt_cell": "QRT-RETRIEVE-D1",
                "difficulty_components": {
                    "concept_model_selection": 0, "representation_translation": 0,
                    "reasoning_chain_length": 0, "algebra_computational_load": 0,
                    "trap_exception_sensitivity": 0}}}


def html_card(*, reveal="", option_style="", band="D1", demand="RETRIEVE",
              hint2="Count favorable cases, then total cases.",
              global_link="jumpToCore1('probability')"):
    attrs = f' data-band="{band}" data-demand="{demand}"'
    body = f'''
    <div class="qb-badge-qrt">QRT-{demand}-{band}</div>
    <button onclick="{global_link}" class="qb-badge" data-core-unit-id="UNIT-Q">Core 1A/1B</button>
    <div class="qb-options-grid">
      <div class="qb-option-card" {option_style}>(A) 1/3</div>
      <div class="qb-option-card">(B) 1/2</div>
      <div class="qb-option-card">(C) 1/4</div>
      <div class="qb-option-card">(D) 2/3</div>
    </div>
    <div class="qb-attempt-box">
      <textarea id="att-{ID}"></textarea>
      <button id="commit-{ID}" aria-controls="sol-disc-{ID}"
              onclick="commitResearchAttempt('{ID}')">Commit</button>
      <p id="feedback-{ID}" aria-live="polite"></p>
    </div>
    <details id="hint1-{ID}"><summary>Tier 1</summary>Recall equally likely outcomes.</details>
    <details id="hint2-{ID}" {reveal}><summary>Tier 2</summary>{hint2}</details>
    <details id="diag-disc-{ID}" hidden inert>
      <summary>Diagnostic</summary><p>Wrong-route repair</p></details>
    <details id="sol-disc-{ID}" hidden inert>
      <summary>Teacher solution</summary><p>Verified Answer: Option (A) — 1/3</p></details>
    '''
    if not reveal:
        body = body.replace(f'id="hint2-{ID}" >', f'id="hint2-{ID}" hidden inert>')
    return attrs, body


CORE = {"same_inferential_jump_proven": False, "explicit_unit_ids": ["UNIT-Q"],
        "code": "EXPLICIT_UNIT_INFERENTIAL_JUMP_UNREVIEWED"}


class RetrieveD1Tests(unittest.TestCase):
    def inspect(self, question=None, *, core=CORE, global_guard=True, **kwargs):
        attrs, body = html_card(**kwargs)
        return inspect_card(question or record(), attrs, body, core_review=core,
                            global_guard=global_guard)

    def rules(self, result):
        return {f["rule"] for f in result["findings"]}

    def test_safe_synthetic_card_passes_structure_but_not_academically(self):
        row = self.inspect()
        self.assertEqual(row["verdict"], "PASS")
        self.assertEqual(row["numerical"]["consistency"], "MATCH")
        self.assertIn("V06_AUTHORED_FACTORS_ACADEMIC_UNREVIEWED", row["holds"])

    def test_score_mismatch_not_automatic_tile_fail_or_relabel(self):
        row = self.inspect(record(score=2))
        self.assertEqual(row["verdict"], "PASS")
        self.assertEqual(row["numerical"]["consistency"], "FINDING_ONLY_NO_SILENT_RECLASSIFICATION")
        self.assertEqual(row["source_cell"], "QRT-RETRIEVE-D1")

    def test_wrong_band_and_demand_fail_at_article_locator(self):
        row = self.inspect(band="D2", demand="APPLY")
        self.assertIn("T01_DECLARED_CELL_HTML_MISMATCH", self.rules(row))
        self.assertTrue(row["html_anchor"].startswith("#q-"))

    def test_pre_commit_second_tier_must_be_hidden_and_inert(self):
        row = self.inspect(reveal="open")
        self.assertIn("T06_PRECOMMIT_DISCLOSURE_UNLOCKED", self.rules(row))

    def test_empty_hint_is_not_exempt(self):
        q = record(hint2=" ")
        row = self.inspect(q, hint2=" ")
        self.assertIn("T10_EMPTY_HINT", self.rules(row))

    def test_short_fraction_answer_inside_hidden_but_available_hint_fails(self):
        q = record(hint2="Probability = 1/3.")
        row = self.inspect(q, hint2="Probability = 1/3.")
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", self.rules(row))

    def test_short_identity_zero_detection_without_incidental_zero(self):
        self.assertTrue(answer_leaked("The additive identity is always 0", "0"))
        self.assertFalse(answer_leaked("Evaluate 10+20 to see a pattern", "0"))

    def test_source_answer_is_leak_even_if_rendered_does_not_copy(self):
        q = record(answer="infinitely many solutions", hint1="Answer: Infinitely many solutions")
        row = self.inspect(q)
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", self.rules(row))

    def test_topic_only_link_fails_core_p2(self):
        row = self.inspect(core={"same_inferential_jump_proven": False,
                                 "code": "TOPIC_ONLY_NOT_CONCEPT_LINK"})
        self.assertIn("T12_CORE_P2_TOPIC_ONLY_NO_QUESTION_UNIT", self.rules(row))
        issue = next(f for f in row["findings"] if f["rule"].startswith("T12"))
        self.assertIn("jumpToCore1", issue["element"])

    def test_explicit_rendered_question_unit_can_pass_html_p2_without_academic_proof(self):
        attrs, body = html_card()
        body = body.replace('class="qb-badge">Core', 
                            'class="qb-badge" data-core-unit-id="UNIT-Q">Core')
        row = inspect_card(record(), attrs, body,
                           core_review={"code": "EXPLICIT_UNIT_INFERENTIAL_JUMP_UNREVIEWED",
                                        "explicit_unit_ids": ["UNIT-Q"],
                                        "same_inferential_jump_proven": False},
                           global_guard=True)
        self.assertEqual(row["verdict"], "PASS")
        self.assertIn("CORE_SAME_INFERENTIAL_JUMP_ACADEMIC_UNREVIEWED", row["holds"])

    def test_wrong_option_emphasis_fails(self):
        row = self.inspect(option_style='style="border-color: var(--success)"')
        self.assertIn("T03_PREATTEMPT_OPTION_STYLING", self.rules(row))

    def test_missing_offline_math_or_commit_guard_fails(self):
        row = self.inspect(global_guard=False)
        self.assertIn("T09_GLOBAL_GUARD_OR_MATH_VENDOR_MISSING", self.rules(row))

    def test_rendered_hint_leak_even_when_source_hint_is_safe(self):
        row = self.inspect(hint2="Probability equals 1/3.")
        self.assertIn("T11_PRECOMMIT_PROTECTED_W_LEAK", self.rules(row))

    def test_canonical_normalization_keeps_math_fraction(self):
        self.assertIn("1/3", normalized("Probability $= 1/3$."))

if __name__ == "__main__":
    unittest.main()
