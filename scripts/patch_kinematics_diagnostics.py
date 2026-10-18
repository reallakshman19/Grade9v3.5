# scripts/patch_kinematics_diagnostics.py
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = REPO_ROOT / "TEST/physics-research/question_bank_kinematics_grade9.v1.json"

with open(BANK_PATH, "r", encoding="utf-8") as f:
    d = json.load(f)

for q in d["questions"]:
    qid = q["question_id"]
    if qid == "PHYS-KIN-013":
        q["distractor_diagnostics"]["A"]["diagnostic"] = (
            "Correct: In the relative frame, relative acceleration is identically zero ($\\vec{a}_{\\text{rel}} = \\vec{0}$). "
            "For horizontal collision at the same altitude, relative approach speed is "
            "$u_1 \\cos 30^\\circ + u_2 \\cos 30^\\circ = 20\\sqrt{3}\\text{ m/s}$. "
            "Collision time is $t = \\frac{100\\text{ m}}{20\\sqrt{3}\\text{ m/s}} = \\frac{5}{\\sqrt{3}}\\text{ s} \\approx 2.89\\text{ s}$."
        )
    elif qid == "PHYS-KIN-020":
        q["distractor_diagnostics"]["A"]["diagnostic"] = (
            "Correct: In Car B's frame, $\\vec{r}_{A/B}(0) = -30\\hat{j}\\text{ km}$ and "
            "$\\vec{v}_{A/B} = 40\\hat{i} - (-30\\hat{j}) = 40\\hat{i} + 30\\hat{j}\\text{ km/h}$. "
            "Distance of closest approach is the perpendicular distance: "
            "$d_{\\min} = \\frac{|\\vec{r}_{A/B}(0) \\times \\vec{v}_{A/B}|}{|\\vec{v}_{A/B}|} = "
            "\\frac{|(-30\\hat{j}) \\times (40\\hat{i} + 30\\hat{j})|}{50\\text{ km/h}} = \\frac{30 \\times 40}{50} = 24\\text{ km}$."
        )
    elif qid == "PHYS-KIN-023":
        q["distractor_diagnostics"]["A"]["diagnostic"] = (
            "Correct: Pre-impact speed $v_0 = \\sqrt{2gh} = 10\\text{ m/s}$. "
            "Incline components after elastic bounce: $v_{0x} = v_0 \\sin 30^\\circ = 5\\text{ m/s}$, "
            "$v_{0y} = v_0 \\cos 30^\\circ = 5\\sqrt{3}\\text{ m/s}$. "
            "Accelerations: $a_x = g \\sin 30^\\circ = 5\\text{ m/s}^2$, $a_y = -g \\cos 30^\\circ = -5\\sqrt{3}\\text{ m/s}^2$. "
            "Flight time between bounces: $T = \\frac{2v_{0y}}{g \\cos 30^\\circ} = 2\\text{ s}$. "
            "Distance along incline: $L = v_{0x} T + \\frac{1}{2} a_x T^2 = 5(2) + \\frac{1}{2}(5)(4) = 20\\text{ m}$."
        )

with open(BANK_PATH, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("[OK] Successfully updated diagnostics for PHYS-KIN-013, PHYS-KIN-020, and PHYS-KIN-023.")
