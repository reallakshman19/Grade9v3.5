# scripts/fix_kinematics_math.py
"""
Batch converter for raw ASCII math, Greek letters, and physical expressions in question_bank_kinematics_grade9.v1.json.
Converts all math into LaTeX ($ ... $) for static DOM KaTeX pre-rendering and offline font-face rendering.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = REPO_ROOT / "TEST/physics-research/question_bank_kinematics_grade9.v1.json"

def fix_text_chunk(text: str) -> str:
    """Fix math outside of existing $...$ blocks in a string."""
    if not isinstance(text, str):
        return text

    parts = text.split('$')
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        
        # Specific full equations & formulas first
        chunk = re.sub(r'\bv_avg\s*=\s*2\*v1\*v2\s*/\s*\(v1\s*\+\s*v2\)', r'$v_{\\text{avg}} = \\frac{2 v_1 v_2}{v_1 + v_2}$', chunk)
        chunk = re.sub(r'\b\(v1\s*\+\s*v2\)\s*/\s*2\b', r'$\\frac{v_1 + v_2}{2}$', chunk)
        chunk = re.sub(r'\b2\*pi\*R\s*=\s*88\s*m\b', r'$2\\pi R = 88\\text{ m}$', chunk)
        chunk = re.sub(r'\bpi\*R\s*=\s*44\s*m\b', r'$\\pi R = 44\\text{ m}$', chunk)
        chunk = re.sub(r'\b2R\s*=\s*28\s*m\b', r'$2R = 28\\text{ m}$', chunk)
        chunk = re.sub(r'\b2\*pi\*R\b', r'$2\\pi R$', chunk)
        chunk = re.sub(r'\b2\s*pi\s*R\b', r'$2\\pi R$', chunk)
        chunk = re.sub(r'\bpi\*R\b', r'$\\pi R$', chunk)
        chunk = re.sub(r'\bpi\s*R\b', r'$\\pi R$', chunk)
        chunk = re.sub(r'\ba_rel\s*=\s*0\b', r'$a_{\\text{rel}} = 0$', chunk)
        chunk = re.sub(r'\bv\s*=\s*0\b', r'$v = 0$', chunk)
        chunk = re.sub(r'\ba\s*=\s*-g\b', r'$a = -g$', chunk)
        chunk = re.sub(r'\ba\s*=\s*0\b', r'$a = 0$', chunk)
        chunk = re.sub(r'\ba\s*=\s*-9\.8\s*m/s\^2\b', r'$a = -9.8\\text{ m/s}^2$', chunk)
        chunk = re.sub(r'\bg\s*=\s*9\.8\s*m/s\^2\b', r'$g = 9.8\\text{ m/s}^2$', chunk)
        chunk = re.sub(r'\bg\s*=\s*10\s*m/s\^2\b', r'$g = 10\\text{ m/s}^2$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*(\d+)\s*deg\b', r'$\\theta = \1^\\circ$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*(\d+)\s*degrees\b', r'$\\theta = \1^\\circ$', chunk)
        chunk = re.sub(r'(\d+)\s*deg\b', r'$\1^\\circ$', chunk)
        chunk = re.sub(r'(\d+)\s*degrees\b', r'$\1^\\circ$', chunk)

        # Numbers with units
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*m/s\^2\b', r'$\1\\text{ m/s}^2$', chunk)
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*m/s\b', r'$\1\\text{ m/s}$', chunk)
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*km/h\b', r'$\1\\text{ km/h}$', chunk)
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*knots\b', r'$\1\\text{ knots}$', chunk)

        # Mathematical and physical variables
        chunk = re.sub(r'\bv_avg\b', r'$v_{\\text{avg}}$', chunk)
        chunk = re.sub(r'\ba_avg\b', r'$a_{\\text{avg}}$', chunk)
        chunk = re.sub(r'\ba_rel\b', r'$a_{\\text{rel}}$', chunk)
        chunk = re.sub(r'\bv_rel\b', r'$v_{\\text{rel}}$', chunk)
        chunk = re.sub(r'\bH_max\b', r'$H_{\\max}$', chunk)
        chunk = re.sub(r'\bR_max\b', r'$R_{\\max}$', chunk)
        chunk = re.sub(r'\bt_up\b', r'$t_{\\text{up}}$', chunk)
        chunk = re.sub(r'\bt_down\b', r'$t_{\\text{down}}$', chunk)
        chunk = re.sub(r'\bt_apex\b', r'$t_{\\text{apex}}$', chunk)
        chunk = re.sub(r'\bt_tot\b', r'$t_{\\text{tot}}$', chunk)
        chunk = re.sub(r'\bDelta\s*t\b', r'$\\Delta t$', chunk)
        chunk = re.sub(r'\bDelta\s*x\b', r'$\\Delta x$', chunk)
        chunk = re.sub(r'\bDelta\s*v\b', r'$\\Delta v$', chunk)
        chunk = re.sub(r'\bDelta\s*r\b', r'$\\Delta r$', chunk)
        chunk = re.sub(r'\bDelta\s*s\b', r'$\\Delta s$', chunk)
        chunk = re.sub(r'\bDelta\b', r'$\\Delta$', chunk)
        chunk = re.sub(r'\btheta\b', r'$\\theta$', chunk)
        chunk = re.sub(r'\bomega\b', r'$\\omega$', chunk)
        chunk = re.sub(r'\bpi\b', r'$\\pi$', chunk)

        parts[i] = chunk

    res = '$'.join(parts)
    # Clean up empty or doubled math delimiters like $ $ or $$
    res = re.sub(r'\$\s*\$', '', res)
    return res

def process_node(node):
    if isinstance(node, str):
        return fix_text_chunk(node)
    elif isinstance(node, list):
        return [process_node(item) for item in node]
    elif isinstance(node, dict):
        return {k: process_node(v) for k, v in node.items()}
    else:
        return node

def main():
    print(f"Reading question bank: {BANK_PATH}")
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    print(f"Total questions: {len(questions)}")

    processed_questions = [process_node(q) for q in questions]
    data["questions"] = processed_questions

    with open(BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Successfully updated all questions in {BANK_PATH}")

if __name__ == "__main__":
    main()
