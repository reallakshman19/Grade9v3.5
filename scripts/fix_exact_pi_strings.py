# scripts/fix_exact_pi_strings.py
from pathlib import Path

target = Path("TEST/physics-research/question_bank_kinematics_grade9.v1.json")
text = target.read_text(encoding="utf-8")

replacements = [
    (r"curved arc path integral $\\\pi R from the vector end-to-end diameter 2R.",
     r"curved arc path integral $\\pi R$ from the vector end-to-end diameter $2R$."),
    
    (r"curved arc length $\\\pi R$ = 44\\text{ m}$",
     r"curved arc length $\\pi R = 44\\text{ m}$"),
    
    (r"full circle perimeter $2\\\pi R$ = 88\\text{ m}$",
     r"full circle perimeter $2\\pi R = 88\\text{ m}$"),
    
    (r'"Distance = $2\\\pi R = 88 m; Displacement = 0 m"',
     r'"Distance = $2\\pi R = 88\\text{ m}$; Displacement = $0\\text{ m}$"'),
    
    (r"curved path integral ($\\\pi R)",
     r"curved path integral ($\\pi R$)"),
    
    (r"Semicircle arc length = $\\\pi R = 50*\\pi m; elapsed time $\\",
     r"Semicircle arc length = $\\pi R = 50\\pi\\text{ m}$; elapsed time "),
    
    (r"curved arc path ($\\\pi R).",
     r"curved arc path ($\\pi R$).")
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"[REPLACED]: {old[:40]}...")
    else:
        print(f"[NOT FOUND]: {old[:40]}...")

target.write_text(text, encoding="utf-8")
print(f"[OK] Wrote updated text to {target}")
