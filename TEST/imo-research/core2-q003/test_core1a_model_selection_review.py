#!/usr/bin/env python3
"""Source-safe MODEL-D2 academic proposal QA; no private original or renderer.

Run: python -m unittest discover -s TEST/imo-research/core2-q003 -p 'test_*.py' -v
This file is a *separate proposed* academic exercise, NOT a qualified QRT signoff.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

PROPOSAL = Path(__file__).with_name('core1a-model-selection-review.v1.json')


def outputs(model, xs):
    if model['kind'] == 'LINEAR':
        if model['formula'] != f"y = {model['slope']}x + {model['intercept']}":
            raise AssertionError('MODEL_FORMULA_DRIFT')
        return [model['slope'] * x + model['intercept'] for x in xs]
    if model['kind'] == 'SQUARE_OFFSET':
        if model['formula'] != f"y = x^2 + {model['offset']}":
            raise AssertionError('MODEL_FORMULA_DRIFT')
        return [x * x + model['offset'] for x in xs]
    raise AssertionError('MODEL_KIND_UNKNOWN')


def validate_case(case):
    assert case['origin'] == 'AUTHORED', 'NOT_AUTHORED'
    models = case['candidates']
    assert len(models) == 2 and len(set(m['id'] for m in models)) == 2, 'MODEL_PAIR_UNCLEAR'
    assert {m['kind'] for m in models} == {'LINEAR', 'SQUARE_OFFSET'}, 'CANDIDATE_FAMILIES_MISSING'
    pairs = case['pairs']
    assert len(pairs) == 4 and len(set(x for x, _ in pairs)) == 4, 'FOUR_DISTINCT_INPUTS_REQUIRED'
    xs = [x for x, _ in pairs]
    ys = [y for _, y in pairs]
    answer = case['teacher_answer']
    wins = []
    for model in models:
        got = outputs(model, xs)
        mid = model['id']
        assert got == answer['predicted_outputs'][mid], 'PREDICTION_DRIFT'
        fit = [i for i, (a, b) in enumerate(zip(got, ys)) if a == b]
        assert fit == answer['matched_indices'][mid], 'MATCH_INDICES_DRIFT'
        assert fit[:2] == [0, 1], 'FIRST_TWO_NOT_SHARED'
        if len(fit) == 3:
            wins.append(mid)
        elif len(fit) != 2:
            raise AssertionError('MODEL_EVIDENCE_NOT_DISCRIMINATING')
    assert len(wins) == 1 and wins[0] == answer['chosen_model_id'], 'MODEL_SELECTION_DRIFT'
    assert answer['first_discriminating_index'] == 2, 'THIRD_OBSERVATION_NOT_DECISIVE'
    assert answer['exception_index'] == 3, 'EXCEPTION_SLOT_DRIFT'
    assert 2 in answer['matched_indices'][wins[0]], 'WINNER_MISSES_DECISIVE_CASE'
    assert 3 not in answer['matched_indices'][wins[0]], 'WINNER_HAS_NO_EXCEPTION'
    prompt = case['student_prompt'].lower()
    assert 'select' in prompt or 'choose' in prompt, 'NO_INDEPENDENT_MODEL_CHOICE'
    assert 'compare' in prompt or 'candidates' in prompt or 'candidate' in prompt or 'relation' in prompt, 'NO_MODEL_COMPARISON'
    # A metadata-only model choice is impossible for a student who sees
    # only the prompt. Show both formulas, but neither the winning ID
    # nor the solved exception.
    assert all(model['formula'].lower() in prompt for model in models), 'CANDIDATE_FORMULA_MISSING'
    # Student-facing instruction must not supply winner ID or exception ordinal.
    assert answer['chosen_model_id'].lower() not in prompt, 'WINNER_SPOILED_IN_PROMPT'
    assert 'fourth pair is the exception' not in prompt, 'EXCEPTION_SPOILED_IN_PROMPT'
    return answer['chosen_model_id']


def validate_proposal(data):
    assert data['origin'] == 'AUTHORED', 'SOURCE_SCOPE'
    assert data['native_integration'] == 'NOT_CONNECTED', 'PREMATURE_NATIVE_ADMISSION'
    assert data['academic_status'] == 'PROVISIONAL_NOT_INDEPENDENTLY_REVIEWED', 'REVIEW_PRETENSE'
    assert data['owner_qrt_status'] == 'NOT_ACCEPTED', 'QRT_PRETENSE'
    assert data['source_rights_status'] == 'NOT_GRANTED', 'RIGHTS_PRETENSE'
    assert data['original_item_data_included'] is False, 'SOURCE_DATA_INCLUDED'
    assert data['intended_primary_demand'] == 'MODEL', 'WRONG_DEMAND'
    worked = data['worked_anchor']
    exit_case = data['independent_exit']
    assert worked['pairs'] != exit_case['pairs'], 'EXIT_NOT_NEW_CASE'
    a = validate_case(worked)
    b = validate_case(exit_case)
    assert a != b, 'SAME_MODEL_ALWAYS_WINS'
    assert worked['candidates'][0]['kind'] == exit_case['candidates'][0]['kind'], 'MAPPING_NOT_COMPARABLE'
    assert worked['candidates'][1]['kind'] == exit_case['candidates'][1]['kind'], 'MAPPING_NOT_COMPARABLE'
    return a, b


class Q003ModelSelectionProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PROPOSAL.read_text(encoding='utf-8'))

    def test_provisional_model_choice_correct(self):
        self.assertEqual(validate_proposal(self.data), ('W-SQUARE', 'E-LINEAR'))

    def test_math_prediction_corruption_rejected(self):
        bad = deepcopy(self.data)
        bad['independent_exit']['teacher_answer']['predicted_outputs']['E-LINEAR'][2] = 99
        with self.assertRaises(AssertionError):
            validate_proposal(bad)

    def test_wrong_winning_model_rejected(self):
        bad = deepcopy(self.data)
        bad['independent_exit']['teacher_answer']['chosen_model_id'] = 'E-SQUARE'
        with self.assertRaises(AssertionError):
            validate_proposal(bad)

    def test_no_distinguishing_third_observation_rejected(self):
        bad = deepcopy(self.data)
        bad['independent_exit']['pairs'][2][1] = 28
        with self.assertRaises(AssertionError):
            validate_proposal(bad)

    def test_both_candidate_formulas_must_be_visible(self):
        for case_name in ('worked_anchor', 'independent_exit'):
            bad = deepcopy(self.data)
            formula = bad[case_name]['candidates'][0]['formula']
            bad[case_name]['student_prompt'] = bad[case_name]['student_prompt'].replace(formula, '[omitted]')
            with self.subTest(case=case_name), self.assertRaisesRegex(
                    AssertionError, 'CANDIDATE_FORMULA_MISSING'):
                validate_proposal(bad)

    def test_leaked_winner_rejected(self):
        bad = deepcopy(self.data)
        bad['independent_exit']['student_prompt'] += ' E-LINEAR.'
        with self.assertRaisesRegex(AssertionError, 'WINNER_SPOILED'):
            validate_proposal(bad)

    def test_review_and_native_status_cannot_be_promoted(self):
        for key, value in (('owner_qrt_status', 'ACCEPTED'),
                           ('native_integration', 'CONNECTED'),
                           ('academic_status', 'QUALIFIED_REVIEWED'),
                           ('source_rights_status', 'GRANTED')):
            bad = deepcopy(self.data)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                validate_proposal(bad)

    def test_opposite_models_must_win(self):
        # A genuinely NEW independent set may still incorrectly reward
        # the same winning family; isolate that error from duplicate-pair QA.
        bad = deepcopy(self.data)
        case = deepcopy(self.data['worked_anchor'])
        case['pairs'] = [[2, 16], [4, 28], [6, 48], [8, 50]]
        case['candidates'] = [
            {'id': 'W-LINEAR', 'kind': 'LINEAR', 'formula': 'y = 6x + 4',
             'slope': 6, 'intercept': 4},
            {'id': 'W-SQUARE', 'kind': 'SQUARE_OFFSET',
             'formula': 'y = x^2 + 12', 'offset': 12},
        ]
        case['teacher_answer']['predicted_outputs'] = {
            'W-LINEAR': [16, 28, 40, 52],
            'W-SQUARE': [16, 28, 48, 76],
        }
        case['student_prompt'] = (
            'Choose between two rival relations for the new observations '
            '(2, 16), (4, 28), (6, 48), (8, 50). Compare y = 6x + 4 with y = x^2 + 12.')
        bad['independent_exit'] = case
        with self.assertRaisesRegex(AssertionError, 'SAME_MODEL_ALWAYS_WINS'):
            validate_proposal(bad)


if __name__ == '__main__':
    unittest.main()
