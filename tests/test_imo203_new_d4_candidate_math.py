"""Issue #203 authored RETRIEVE and SYNTHESIZE mathematical oracle, no HTML promotion."""
import itertools
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "TEST/imo-research/qrt-tiles/d4-review"
DIGITS = (0, 1, 2, 3, 4, 8)


def load(name):
    return json.loads((DIR / (name + "-d4.candidate.json")).read_text())


def odd_square_classes(k):
    modulus = 1 << k
    return {x * x % modulus for x in range(1, modulus, 2)}


def numbers_with_moduli(*moduli):
    result = []
    for p in itertools.permutations(DIGITS):
        if p[0] == 0:
            continue
        n = int("".join(map(str, p)))
        if all(n % m == 0 for m in moduli):
            result.append(n)
    return sorted(result)


class NewD4CandidateMath(unittest.TestCase):
    def test_qrt_authorship_and_hold_gates(self):
        for demand in ("retrieve", "synthesize"):
            with self.subTest(demand=demand):
                d = load(demand)
                self.assertEqual(d["cell_id"], "QRT-" + demand.upper() + "-D4")
                self.assertEqual(d["primary_demand"], demand.upper())
                self.assertEqual(d["source"], "WHOLLY_AUTHORED_TEST_ONLY")
                self.assertEqual(d["stage"], "AUTHORED_SPEC_MATH_VERIFIED_NATIVE_HTML_PENDING")
                self.assertFalse(d["accepted"])
                self.assertIsNone(d["owner_qrt_decision_id"])
                self.assertIsNone(d["qualified_independent_reviewer"])
                self.assertEqual(d["html_status"], "NOT_GENERATED")
                self.assertEqual(d["selection_core2"], [])
                self.assertEqual(len(d["blueprint_refs"]), 5)
                self.assertEqual(len(d["review_requirements"]), 12)
                self.assertEqual(d["academic_status"], "PENDING_INDEPENDENT_REVIEW")
                self.assertIn("PROPOSED", d["difficulty_proposal"]["classification_hold"])

    def test_retrieve_all_odd_residues_and_exception_threshold(self):
        d = load("retrieve")
        for k in range(2, 11):
            modulus = 1 << k
            square_residues = odd_square_classes(k)
            expected = {
                a for a in range(1, modulus, 2)
                if (a % 4 == 1 if k == 2 else a % 8 == 1)
            }
            self.assertEqual(square_residues, expected, (k, modulus))
        examples = [9, 13, 17, 21, 33, 49]
        actual_yes = [a for a in examples if a % 128 in odd_square_classes(7)]
        actual_no = [a for a in examples if a not in actual_yes]
        self.assertEqual(actual_yes, d["core2a"]["expected"]["yes"])
        self.assertEqual(actual_no, d["core2a"]["expected"]["no"])
        self.assertTrue(all(a % 4 in odd_square_classes(2) for a in (5, 9, 13)))
        self.assertNotIn(5, odd_square_classes(3))

    def test_retrieve_constructive_lifting_step(self):
        # Given a root modulo 2^k, the optional high-bit shift flips its square
        # by 2^k modulo 2^(k+1), proving each admissible high bit can be lifted.
        for k in range(3, 10):
            m = 1 << (k + 1)
            for x in range(1, 1 << k, 2):
                shifted = x + (1 << (k - 1))
                self.assertEqual(((shifted * shifted - x * x) % m), 1 << k)

    def test_synthesize_complete_permutation_oracle_and_transfer(self):
        d = load("synthesize")
        original = numbers_with_moduli(4, 9, 11)
        changed = numbers_with_moduli(4, 9, 11, 7)
        self.assertEqual(original[0], d["core2a"]["expected"]["minimum"])
        self.assertEqual(len(original), d["core2a"]["expected"]["number_of_valid_permutations"])
        self.assertEqual(changed[0], d["core2b"]["correct_answer"])
        self.assertEqual([n for n in original if 100000 <= n < 130284], [120384, 128304])
        self.assertTrue(all(n % 7 != 0 for n in (120384, 128304)))
        self.assertEqual((130284 % 4, 130284 % 9, 130284 % 11, 130284 % 7), (0, 0, 0, 0))

    def test_synthesize_analytic_minimality_constraints(self):
        # Digit-sum condition is automatic; alternating-sum difference
        # must be 0 because it is even and has absolute value <=18.
        self.assertEqual(sum(DIGITS), 18)
        valid = numbers_with_moduli(4, 9, 11)
        for n in valid:
            places = list(map(int, str(n)))
            self.assertEqual(sum(places[::2]), 9)
            self.assertEqual(sum(places[1::2]), 9)
        self.assertFalse(any(str(n).startswith("10") for n in valid))
        prefix12 = [n for n in valid if str(n).startswith("12")]
        self.assertEqual(prefix12, [120384, 128304])
        self.assertEqual([n for n in numbers_with_moduli(4, 9, 11, 7)
                          if str(n).startswith("13")], [130284])


if __name__ == "__main__":
    unittest.main()
