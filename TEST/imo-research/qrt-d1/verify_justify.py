"""Independent math oracle for source-safe QRT-JUSTIFY-D1 authored practice."""
from fractions import Fraction
from itertools import product

def area_by_determinant(a, b, c):
    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    return Fraction(abs((x2-x1)*(y3-y1)-(y2-y1)*(x3-x1)), 2)

def verify():
    # Vary base, height, and BOTH horizontal peak offsets, including outside AB.
    checks = 0
    for base, height, u, v in product((3, 9, 12, 21), (1, 4, 6, 7), (-8, -1, 0, 2, 10, 25), (-7, 0, 5, 20)):
        expected = Fraction(base*height, 2)
        a, b = (0, 0), (base, 0)
        assert area_by_determinant(a, b, (u, height)) == expected
        assert area_by_determinant(a, b, (v, height)) == expected
        checks += 1
    assert area_by_determinant((0,0), (12,0), (2,7)) == 42
    assert area_by_determinant((0,0), (12,0), (10,7)) == 42
    assert area_by_determinant((0,0), (8,0), (2,5)) == 20
    assert area_by_determinant((0,0), (8,0), (2,4)) == 16
    assert 20 != 16  # Equal base alone is not the warrant.
    assert Fraction(2*36, 12) == 6
    assert Fraction(12*6, 2) == 36
    assert area_by_determinant((0,0), (9,0), (2,6)) == 27
    assert area_by_determinant((0,0), (9,0), (7,6)) == 27
    print(f"JUSTIFY-D1 independent determinant/inverse oracle: {checks} shifted-peak cases PASS")

if __name__ == "__main__":
    verify()
