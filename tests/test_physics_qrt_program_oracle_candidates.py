"""Known real Physics witnesses and deliberate false-result controls.

These are candidate oracles, NOT independently signed scientific acceptance.
"""
from __future__ import annotations
import math
import unittest
from Physics.adapter.qrt_oracle_candidates import (
    signed_quadrant_ii_components, ideal_horizontal_launch,
    vertical_magnet_force_balance, angled_static_friction_threshold,
)


class PhysicsCandidateOracleTests(unittest.TestCase):
    def test_vector_quadrant_ii_requires_correct_sign_not_just_magnitude(self):
        result = signed_quadrant_ii_components(15, 40)
        self.assertAlmostEqual(result["vx"], -15 * math.cos(math.radians(40)))
        self.assertAlmostEqual(result["vy"], 15 * math.sin(math.radians(40)))
        self.assertAlmostEqual(result["magnitude"], 15)
        # Negative x is essential; vector (|vx|, vy) still has length 15.
        wrong_x = abs(result["vx"])
        self.assertAlmostEqual(math.hypot(wrong_x, result["vy"]), 15)
        self.assertNotAlmostEqual(wrong_x, result["vx"])

    def test_horizontal_launch_uses_same_time_both_axes(self):
        result = ideal_horizontal_launch(ux=15, height=20, g=10)
        self.assertAlmostEqual(result["time"], 2)
        self.assertAlmostEqual(result["range"], 30)
        self.assertAlmostEqual(result["impact_vx"], 15)
        self.assertAlmostEqual(result["impact_vy"], -20)
        self.assertNotAlmostEqual(result["range"], 15)  # false 1-second x-clock
        with self.assertRaisesRegex(ValueError, "INVALID_IDEAL_PROJECTILE_INPUT"):
            ideal_horizontal_launch(ux=15, height=20, g=0)

    def test_vertical_magnet_body_ownership(self):
        result = vertical_magnet_force_balance(mass=0.1, g=10, magnetic_pull=3)
        f = result["forces_on_magnet"]
        self.assertAlmostEqual(f["earth_weight_down"], 1)
        self.assertAlmostEqual(f["door_magnetic_toward_wall"], 3)
        self.assertAlmostEqual(f["door_normal_away_from_wall"], 3)
        self.assertAlmostEqual(f["door_static_friction_up"], 1)
        self.assertAlmostEqual(result["net_vertical"], 0)
        self.assertAlmostEqual(result["net_horizontal"], 0)
        self.assertEqual(result["partners_on_magnet"], 0)

    def test_friction_unknown_pull_changes_normal(self):
        choices = [
            angled_static_friction_threshold(mass=10, g=10, mu_s=0.75, cosine=1, sine=0),
            angled_static_friction_threshold(mass=10, g=10, mu_s=0.75, cosine=0.8, sine=0.6),
            angled_static_friction_threshold(mass=10, g=10, mu_s=0.75, cosine=0.6, sine=0.8),
        ]
        self.assertEqual([round(x["minimum_pull"], 5) for x in choices], [75, 60, 62.5])
        self.assertEqual([x["minimum_pull"] <= 61 for x in choices], [False, True, False])
        for row in choices:
            self.assertAlmostEqual(row["horizontal_drive"], row["limiting_friction"])
        # False model: fixing N=mg gives a different threshold at 37 degrees.
        self.assertNotAlmostEqual(0.75 * 100 / 0.8, choices[1]["minimum_pull"])
        with self.assertRaisesRegex(ValueError, "TRIG_IDENTITY_MISMATCH"):
            angled_static_friction_threshold(mass=10, g=10, mu_s=0.75, cosine=1, sine=1)


if __name__ == "__main__":
    unittest.main()
