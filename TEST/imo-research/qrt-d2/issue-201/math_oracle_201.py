"""#201: independent-computation oracles for authored D2 examples.

These tests do NOT qualify as an independent academic review or confer a QRT
classification, golden designation, source right, or Owner decision.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import permutations
from math import gcd, isqrt
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "TEST/imo-research/qrt-d2"

def routes(a: int, b: int) -> tuple[int, int]:
    square = a*a + b*b
    diagonal = isqrt(square)
    assert diagonal*diagonal == square, "Non-integral route in fixture"
    return diagonal, a+b

def price(start: int, *factors: Fraction) -> Fraction:
    out = Fraction(start)
    for factor in factors:
        out *= factor
    return out

def revenues(n: int, low: int, high: int) -> dict[int, list[tuple[int, int]]]:
    result = {}
    for premium in range(n + 1):
        ordinary = n - premium
        result.setdefault(low*ordinary + high*premium, []).append((ordinary, premium))
    return result

def grid_unshaded(rows: int, cols: int, removed: set[tuple[int,int]]) -> int:
    universe = {(r,c) for r in range(rows) for c in range(cols)}
    assert removed <= universe
    return len(universe - removed)

def possible_three_digit(hundreds: int, digits: tuple[int, ...]) -> list[int]:
    return sorted((100*hundreds+10*tens+ones
        for tens,ones in permutations((d for d in digits if d != hundreds),2)
        if (hundreds+tens+ones)%3 == 0 and ones%2 == 0), reverse=True)

class MathD2Oracles(unittest.TestCase):
    def test_all_primary_and_transfer_answer_records_exist_and_are_authored(self):
        for demand in ("retrieve","explain","apply","model","represent","synthesize","justify"):
            with self.subTest(demand=demand):
                package = json.loads((SOURCE/f"{demand}.v1.json").read_text(encoding="utf-8"))
                q = package["questions"]
                principal = [a for a in q if "PRIMARY" in a["id"] or a["id"].endswith("-PROOF")]
                transfer = [a for a in q if a["id"].endswith("-TRANSFER")]
                self.assertEqual(len(principal),1)
                self.assertEqual(len(transfer),1)
                for a in (principal[0],transfer[0]):
                    self.assertEqual(a["origin"],"AUTHORED")
                    self.assertEqual(a["answer"]["verification_status"],"CHECKED_BY_AUTHOR")
                    self.assertTrue(a["answer"]["crux_move_ref"])
                manifest = json.loads((ROOT/f"TEST/products/imo182-qrt-d2-{demand}.manifest.json").read_text())
                self.assertEqual(manifest["selection"]["core2"],[])
                self.assertEqual(manifest["output_roles"],["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"])

    def test_retrieve_paths_and_access_boundary(self):
        self.assertEqual(routes(9,12),(15,21))
        self.assertTrue(15 <= 18 < 21)
        self.assertEqual(21-15,6)
        self.assertEqual(routes(6,8),(10,14))
        self.assertEqual(routes(8,15),(17,23))
        self.assertEqual(routes(12,16),(20,28))
        self.assertEqual(routes(5,12),(13,17))
        self.assertEqual(isqrt(13*13 - 5*5),12)
        self.assertEqual(17-13,4)
        self.assertFalse(23 <= 20) # Core1B diagonal CLOSED, cannot use 17.

    def test_explain_factors_and_doubled_exponent(self):
        for b in range(2,10):
            for t in range(1,11):
                self.assertEqual(b**(t+1),b*(b**t))
                self.assertEqual(b**(2*t),(b**t)**2)
        self.assertNotEqual(3**2, 3**1 + 3)
        self.assertNotEqual(3**3, 3**2 + 3)
        self.assertNotEqual(2**(2*2),2*2**2)
        # Important boundary: the wrong doubled-exponent rule COINCIDES at k=1.
        self.assertEqual(2**(2*1),2*2**1)

    def test_apply_exact_percent_references(self):
        self.assertEqual(price(960,Fraction(3,4),Fraction(9,10)),648)
        self.assertEqual(Fraction(960-648,960),Fraction(325,1000))
        self.assertEqual(price(1000,Fraction(4,5),Fraction(4,5)),640)
        self.assertEqual(price(500,Fraction(9,10),Fraction(4,5)),360)
        self.assertEqual(Fraction(500-360,500),Fraction(28,100))
        self.assertEqual(price(200,Fraction(3,4),Fraction(3,4)),Fraction(225,2))
        self.assertEqual(Fraction(200-Fraction(225,2),200),Fraction(7,16))
        self.assertEqual(price(100,Fraction(11,10),Fraction(9,10)),99)
        self.assertEqual(Fraction(1080,1)/(Fraction(6,5)*Fraction(9,10)),1000)
        self.assertEqual(Fraction(1080-1000,1000),Fraction(8,100))

    def test_model_integer_counts_and_nearest_receipts(self):
        self.assertEqual(revenues(9,4,7)[48],[(5,4)])
        self.assertEqual(revenues(6,3,8)[33],[(3,3)])
        self.assertEqual(revenues(7,5,9)[47],[(4,3)])
        self.assertEqual(revenues(8,5,9)[56],[(4,4)])
        self.assertNotIn(49,revenues(7,5,9)) # 3.5 premium is invalid
        possible = revenues(11,5,9)
        self.assertNotIn(74,possible)
        self.assertEqual(max(v for v in possible if v < 74),71)
        self.assertEqual(min(v for v in possible if v > 74),75)
        self.assertEqual(possible[71],[(7,4)])
        self.assertEqual(possible[75],[(6,5)])

    def test_represent_actual_unit_sets_and_reverse_area(self):
        shaded_left={(r,c) for r in range(5) for c in range(2)}
        shaded_top_right={(r,c) for r in range(2) for c in range(2,7)}
        self.assertFalse(shaded_left & shaded_top_right)
        self.assertEqual(grid_unshaded(5,7,shaded_left|shaded_top_right),15)
        self.assertEqual(35-2*5-2*5,3*5)
        self.assertEqual(35-2*5-2*7,11) # false route: overlaps four cells
        worked={(r,c) for r in range(2) for c in range(6)}
        worked|={(r,c) for r in range(2,6) for c in range(4,6)}
        self.assertEqual(grid_unshaded(6,6,worked),16)
        self.assertEqual(4*7-4-6,18) # concept independent exit
        self.assertEqual(5*8-8-4*3,20) # Core1B attempt
        self.assertEqual(7*4-14-4,10) # Core1B changed boundary
        row_lengths=(8,8,5,5,5,5)
        self.assertEqual(sum(row_lengths),36)
        self.assertEqual(6*8-4*3,36)
        self.assertNotEqual(6*8-6*3,36)

    def test_synthesize_exhaustive_maximality_and_one_swap(self):
        self.assertEqual(possible_three_digit(4,(1,2,3,4,5))[0],432)
        self.assertNotIn(452,possible_three_digit(4,(1,2,3,4,5)))
        self.assertEqual(possible_three_digit(3,(1,2,3,4))[0],342)
        self.assertEqual(possible_three_digit(7,(1,2,3,4,7))[0],732)
        self.assertEqual(possible_three_digit(6,(1,2,3,4,5,6))[0],654)
        self.assertTrue(all(n%6==0 for n in possible_three_digit(4,(1,2,3,4,5))))
        self.assertFalse(any((100*8+10*tens+5)%6==0 for tens in range(10)))
        digits=(5,3,4)
        swaps={(i,j):int("".join(map(str,
               (lambda ds: ds)([digits[k] if k not in (i,j)
                                else digits[j if k==i else i] for k in range(3)]))))
               for i,j in ((0,1),(0,2),(1,2))}
        self.assertEqual(swaps,{(0,1):354,(0,2):435,(1,2):543})
        self.assertEqual([v for v in swaps.values() if v<534 and v%6==0],[354])

    def test_justify_general_residues_and_greatest_divisor(self):
        triples=[n*(n+1)*(n+2) for n in range(1,241)]
        quads=[n*(n+1)*(n+2)*(n+3) for n in range(1,241)]
        self.assertTrue(all(v%6==0 for v in triples))
        self.assertTrue(all(v%24==0 for v in quads))
        self.assertEqual(gcd(*triples),6)
        self.assertEqual(gcd(*quads),24)
        self.assertEqual((3*4*5)%6,0)
        self.assertTrue(all(v%6 for v in (3,4,5))) # refutes the *reason*, not the claim
        self.assertEqual(quads[0],24)
        self.assertNotEqual(quads[0]%48,0)
        for n in range(1,49):
            f=(n,n+1,n+2,n+3)
            # One factor divisible by 4 and another even factor = at least 8.
            self.assertTrue(any(v%4==0 for v in f))
            self.assertGreaterEqual(sum(v%2==0 for v in f),2)
            self.assertTrue(any(v%3==0 for v in f))

if __name__=="__main__":
    unittest.main()
