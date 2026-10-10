"""Synthetic local-only handoff tests: no acceptance, real student or SOF claim."""
import copy
import unittest
from Shared.tools.imo_handoff_preflight import check


def fixture():
    package = {
        'subject': 'TEST', 'status': 'CANDIDATE',
        'microtopics': [{'id': 'MIC-TEST-IMO-G9-COMMON-BASE-RELATION',
                         'primary_capability_ref': 'CAP-TEST-IMO-G9-COMMON-EXPONENTIAL-QUANTITY',
                         'teaching_path': [{'id': 'TC-01'}, {'id': 'TC-02'}, {'id': 'TC-03'}]}],
        'questions': [{'id': 'Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01',
                       'origin': 'AUTHORED', 'status': 'CANDIDATE',
                       'primary_capability_ref': 'CAP-TEST-IMO-G9-COMMON-EXPONENTIAL-QUANTITY',
                       'repair_ref': 'TC-02', 'exposure': [{'core': 'CORE2A'}]}],
    }
    manifest = {'schema': 'product-manifest/v1', 'subject': 'TEST',
                'package_refs': ['TEST/imo-research/candidates/candidate.json'], 'bank_refs': [],
                'output_roles': ['CORE1A', 'CORE2A'],
                'selection': {'microtopics': ['MIC-TEST-IMO-G9-COMMON-BASE-RELATION'],
                              'core2': [], 'core2b': [],
                              'core2a': ['Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01']}}
    pilot = {'scope': {'subtopic_id': 'NS-INDEX-LAWS', 'launch_authorized': False,
                       'source_core2_admitted': 0, 'learner_products_released': 0},
             'routing': {'core1a_product_url': None, 'core2a_authored_product_url': None,
                         'core2_source_product_url': None}}
    return package, manifest, pilot


class Preflight(unittest.TestCase):
    def test_consistent_candidate_is_explicitly_held(self):
        out = check(*fixture())
        self.assertEqual(out['state'], 'CANDIDATE_HELD_WELL_FORMED')
        self.assertEqual(out['repair_step_id'], 'TC-02')
        self.assertFalse(out['authorizes_learner_launch'])
        self.assertFalse(out['authorizes_academic_qrt_or_source'])

    def test_all_mutations_remain_nonreleasing_and_inconsistent(self):
        cases = [
            ('forged_launch', lambda p,m,s: s['scope'].__setitem__('launch_authorized', True), 'NO_LAUNCH_AUTHORITY'),
            ('fake_release', lambda p,m,s: s['scope'].__setitem__('learner_products_released', 1), 'LEARNER_PRODUCT_HELD'),
            ('test_url', lambda p,m,s: s['routing'].__setitem__('core1a_product_url', '/test/imo-grade9/core1a.html'), 'NO_LEARNER_PRODUCT_URL_WHILE_HELD'),
            ('source_core2', lambda p,m,s: m['selection'].__setitem__('core2', ['SOF-Q026']), 'SOURCE_CORE2_CANNOT_BE_SELECTED'),
            ('added_source_role', lambda p,m,s: m['output_roles'].append('CORE2'), 'ROLE_BOUNDARY'),
            ('question_replaced', lambda p,m,s: m['selection'].__setitem__('core2a', ['fake']), 'QUESTION_NOT_RESOLVED'),
            ('teaching_step_missing', lambda p,m,s: p['microtopics'][0].__setitem__('teaching_path', [{'id':'TC-01'}]), 'REPAIR_STEP_UNRESOLVED'),
            ('duplicate_step', lambda p,m,s: p['microtopics'][0]['teaching_path'].append({'id':'TC-02'}), 'TEACHING_STEPS_NOT_UNIQUE'),
            ('wrong_capability', lambda p,m,s: p['questions'][0].__setitem__('primary_capability_ref', 'WRONG'), 'CAPABILITY_MISMATCH'),
            ('source_claim', lambda p,m,s: p['questions'][0].__setitem__('origin', 'SOF'), 'SUPPORTED_PRACTICE_MUST_BE_AUTHORED_CANDIDATE'),
            ('source_role', lambda p,m,s: p['questions'][0]['exposure'].append({'core': 'CORE2'}), 'SOURCE_CORE2_EXPOSURE_FORBIDDEN'),
            ('fake_academic_accept', lambda p,m,s: p.__setitem__('status', 'ACCEPTED'), 'UNADMITTED_PACKAGE_REQUIRED'),
            ('duplicated_mic_id', lambda p,m,s: p['microtopics'].append(dict(p['microtopics'][0])), 'DUPLICATE_TEACHING_MICROTOPIC_ID'),
            ('duplicated_question_id', lambda p,m,s: p['questions'].append(dict(p['questions'][0])), 'DUPLICATE_AUTHORED_QUESTION_ID'),
            ('package_escape', lambda p,m,s: m.__setitem__('package_refs', ['../OTHER/package.json']), 'EXACT_ONE_PACKAGE_REF_REQUIRED'),
        ]
        for label, mutation, code in cases:
            with self.subTest(label=label):
                args = copy.deepcopy(fixture())
                mutation(*args)
                out = check(*args)
                self.assertEqual(out['state'], 'INCONSISTENT_CANDIDATE_HOLD')
                self.assertIn(code, out['errors'])
                self.assertFalse(out['authorizes_learner_launch'])


if __name__ == '__main__':
    unittest.main()
