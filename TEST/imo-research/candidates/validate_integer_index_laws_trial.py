#!/usr/bin/env python3
"""Deterministic integer-domain oracle for isolated authored Index Laws trial.

Research evidence only, not a source-paper key or mathematical reviewer signature.
"""
from __future__ import annotations

import json
from fractions import Fraction


def integer_solutions(base: int, constant: int, limit: int = 24) -> list[int]:
    """Solve base^(2n+1)=(base^2)^n + constant for integer 0<=n<=limit."""
    return [n for n in range(limit + 1)
            if base ** (2*n+1) == (base*base)**n + constant]


def validate() -> dict:
    worked = integer_solutions(3, 162)
    exit_a = integer_solutions(2, 64)
    exit_b = integer_solutions(2, 8)
    assert worked == [2], worked
    assert exit_a == [3], exit_a
    assert exit_b == [], exit_b

    # These finite searches are additional falsifiers; completeness is algebraic.
    # (base-1) * (base^2)^n = constant, base^2>1 for integer base>=2,
    # and a^k is strictly increasing over nonnegative integer k.
    assert 3**4 == 81 == 162 // (3-1)
    assert 2**6 == 64 == 64 // (2-1)
    assert 8 == 8 // (2-1)
    assert 2**3 == 8 and 3 % 2 == 1  # 2n=3 cannot hold for integer n.

    # Fraction is a proof of the real-only boundary, not floating tolerance.
    real_boundary = Fraction(3,2)
    assert 2 * real_boundary == 3
    assert 2**4 == 4**float(real_boundary) + 8 == 16
    assert 3**5 == 9**2 + 162 == 243
    assert 2**7 == 4**3 + 64 == 128

    return {
        "status": "AUTHOR_CHECKED_NOT_ACADEMIC_ACCEPTANCE",
        "domain": "NONNEGATIVE_INTEGER_EXPONENTS",
        "anchor_integer_solutions": worked,
        "exit_A_integer_solutions": exit_a,
        "exit_B_integer_solutions": exit_b,
        "boundary_real_solution": str(real_boundary),
        "source_core2_admitted": 0,
        "qrt_accepted": 0,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
