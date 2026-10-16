"""Candidate-only independently recalculated Physics witness results.

Pure numerical/force-diagram calculations for review; NO automatic QRT,
academic authority, source legitimacy, or learner mastery admission.
The expert Physics reviewer must approve the domain model before agents rely
on these computations to change production validator behavior.
"""
from __future__ import annotations
import math


def signed_quadrant_ii_components(magnitude: float, degrees_above_negative_x: float) -> dict:
    """Resolve signed x/y for an arrow above the negative x direction."""
    if not (math.isfinite(magnitude) and magnitude >= 0 and 0 <= degrees_above_negative_x <= 90):
        raise ValueError("INVALID_QUADRANT_II_INPUT")
    rad = math.radians(degrees_above_negative_x)
    x, y = -magnitude * math.cos(rad), magnitude * math.sin(rad)
    return {"vx": x, "vy": y, "magnitude": math.hypot(x, y)}


def ideal_horizontal_launch(*, ux: float, height: float, g: float) -> dict:
    """Only ideal near-Earth free flight, positive y upward, launch uy=0."""
    if not all(math.isfinite(x) for x in (ux, height, g)) or height <= 0 or g <= 0:
        raise ValueError("INVALID_IDEAL_PROJECTILE_INPUT")
    t = math.sqrt(2 * height / g)
    return {"time": t, "range": ux * t, "impact_vx": ux, "impact_vy": -g * t}


def vertical_magnet_force_balance(*, mass: float, g: float,
                                  magnetic_pull: float) -> dict:
    """At rest on a vertical wall: F_normal=F_magnetic; F_static=mg.

    These are forces ON the magnet. Third-law partners act ON other bodies and
    must not be included on the magnet's free-body diagram.
    """
    if not all(math.isfinite(x) for x in (mass, g, magnetic_pull)) or min(mass, g, magnetic_pull) <= 0:
        raise ValueError("INVALID_FBD_INPUT")
    weight = mass * g
    return {
        "forces_on_magnet": {
            "earth_weight_down": weight,
            "door_magnetic_toward_wall": magnetic_pull,
            "door_normal_away_from_wall": magnetic_pull,
            "door_static_friction_up": weight,
        },
        "net_vertical": weight - weight,
        "net_horizontal": magnetic_pull - magnetic_pull,
        "partners_on_magnet": 0,
        "partner_bodies": {"Earth", "fridge_door"},
    }


def angled_static_friction_threshold(*, mass: float, g: float,
                                     mu_s: float, cosine: float, sine: float) -> dict:
    """Pull P at angle above horizontal reduces normal reaction by P sin(theta).

    Valid at impending sliding, contact maintained, horizontal surface.
    """
    if not all(math.isfinite(x) for x in (mass, g, mu_s, cosine, sine)):
        raise ValueError("NONFINITE_FORCE_INPUT")
    if mass <= 0 or g <= 0 or mu_s < 0 or cosine < 0 or sine < 0:
        raise ValueError("INVALID_FORCE_INPUT")
    if not math.isclose(cosine * cosine + sine * sine, 1, abs_tol=1e-10):
        raise ValueError("TRIG_IDENTITY_MISMATCH")
    denominator = cosine + mu_s * sine
    if denominator <= 0:
        raise ValueError("NO_POSITIVE_THRESHOLD")
    pull = mu_s * mass * g / denominator
    normal = mass * g - pull * sine
    if normal <= 0:
        raise ValueError("CONTACT_ASSUMPTION_VIOLATED")
    return {"minimum_pull": pull, "normal_at_threshold": normal,
            "horizontal_drive": pull * cosine,
            "limiting_friction": mu_s * normal}
