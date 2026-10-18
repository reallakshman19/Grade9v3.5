# scripts/fix_planar_motion_math.py
"""
Batch converter for raw ASCII math, LaTeX expressions, and physical units in question_bank_planar_motion_grade9.v1.json.
Formats all math into valid LaTeX ($ ... $) for static DOM KaTeX pre-rendering and ensures 100% dollar parity.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = REPO_ROOT / "TEST/physics-research/question_bank_planar_motion_grade9.v1.json"

def format_ladder_step(text):
    if not isinstance(text, str) or "$" in text:
        return text
    if " - " in text:
        formula, explanation = text.rsplit(" - ", 1)
        return f"${formula.strip()}$ — {explanation.strip()}"
    return f"${text.strip()}$"

def format_derivation_step(text):
    if not isinstance(text, str) or "$" in text:
        return text
    if "): " in text:
        prefix, rest = text.split("): ", 1)
        if " [" in rest and rest.endswith("]"):
            formula, note = rest.rsplit(" [", 1)
            return f"{prefix}): ${formula.strip()}$ [{note}"
        return f"{prefix}): ${rest.strip()}$"
    return f"${text.strip()}$"

def fix_prose_math(text: str) -> str:
    if not isinstance(text, str):
        return text

    parts = text.split("$")
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        
        # Specific full expressions & equations
        chunk = re.sub(r'\ba_c\s*=\s*v\^2\s*/\s*R\b', r'$a_c = v^2/R$', chunk)
        chunk = re.sub(r'\bv_rel\s*=\s*0\b', r'$v_{\\text{rel}} = 0$', chunk)
        chunk = re.sub(r'\ba_rel\s*=\s*0\b', r'$a_{\\text{rel}} = 0$', chunk)
        chunk = re.sub(r'\bv_y\s*=\s*0\b', r'$v_y = 0$', chunk)
        chunk = re.sub(r'\bv_x\s*=\s*u\s*\\cos\s*\\theta\b', r'$v_x = u\\cos\\theta$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*45\s*deg\b', r'$\\theta = 45^\\circ$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*30\s*deg\b', r'$\\theta = 30^\\circ$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*60\s*deg\b', r'$\\theta = 60^\\circ$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*90\s*deg\b', r'$\\theta = 90^\\circ$', chunk)
        chunk = re.sub(r'\btheta\s*=\s*0\s*deg\b', r'$\\theta = 0^\\circ$', chunk)
        chunk = re.sub(r'(\d+)\s*deg\b', r'$\1^\\circ$', chunk)
        chunk = re.sub(r'(\d+)\s*degrees\b', r'$\1^\\circ$', chunk)

        # Numbers with units
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*m/s\^2\b', r'$\1\\text{ m/s}^2$', chunk)
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*m/s\b', r'$\1\\text{ m/s}$', chunk)
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*km/h\b', r'$\1\\text{ km/h}$', chunk)
        chunk = re.sub(r'(\d+(?:\.\d+)?)\s*knots\b', r'$\1\\text{ knots}$', chunk)

        # Mathematical and physical variables
        chunk = re.sub(r'\bv_rel\b', r'$v_{\\text{rel}}$', chunk)
        chunk = re.sub(r'\ba_rel\b', r'$a_{\\text{rel}}$', chunk)
        chunk = re.sub(r'\bH_max\b', r'$H_{\\max}$', chunk)
        chunk = re.sub(r'\bR_max\b', r'$R_{\\max}$', chunk)
        chunk = re.sub(r'\bt_apex\b', r'$t_{\\text{apex}}$', chunk)
        chunk = re.sub(r'\bt_fall\b', r'$t_{\\text{fall}}$', chunk)
        chunk = re.sub(r'\bt_min\b', r'$t_{\\min}$', chunk)
        chunk = re.sub(r'\ba_c\b', r'$a_c$', chunk)
        chunk = re.sub(r'\ba_t\b', r'$a_t$', chunk)
        chunk = re.sub(r'\ba_n\b', r'$a_n$', chunk)
        chunk = re.sub(r'\bDelta\s*t\b', r'$\\Delta t$', chunk)
        chunk = re.sub(r'\bDelta\s*x\b', r'$\\Delta x$', chunk)
        chunk = re.sub(r'\bDelta\s*y\b', r'$\\Delta y$', chunk)
        chunk = re.sub(r'\bDelta\s*r\b', r'$\\Delta r$', chunk)
        chunk = re.sub(r'\bDelta\b', r'$\\Delta$', chunk)
        chunk = re.sub(r'\btheta\b', r'$\\theta$', chunk)
        chunk = re.sub(r'\bomega\b', r'$\\omega$', chunk)
        chunk = re.sub(r'\bpi\b', r'$\\pi$', chunk)

        parts[i] = chunk

    res = "$".join(parts)
    res = re.sub(r'\$\s*\$', '', res)
    return res

def main():
    print(f"Reading planar motion question bank: {BANK_PATH}")
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    print(f"Total questions: {len(questions)}")

    for q in questions:
        # 1. Format model_proof
        proof = q.get("model_proof", {})
        ladder = proof.get("reasoning_ladder", {})
        for step_k in ["understand", "represent", "connect", "calculate", "interpret"]:
            if step_k in ladder:
                ladder[step_k] = format_ladder_step(ladder[step_k])
        
        steps = proof.get("derivation_steps", [])
        proof["derivation_steps"] = [format_derivation_step(s) for s in steps]
        
        # Clean final_expression (pure LaTeX, no $)
        fe = proof.get("final_expression", "")
        if fe:
            proof["final_expression"] = fe.replace("$", "").replace("\\$", "").strip()

        # 2. Clean dimensional_formula (pure LaTeX, no $)
        check = q.get("independent_check", {})
        df = check.get("dimensional_formula", "")
        if df:
            check["dimensional_formula"] = df.replace("$", "").replace("\\$", "").strip()
        
        # Prose fields in independent_check
        if "quick_check" in check:
            check["quick_check"] = fix_prose_math(check["quick_check"])
        if "watch_out" in check:
            check["watch_out"] = fix_prose_math(check["watch_out"])
        for lc in check.get("limiting_cases", []):
            if "condition" in lc:
                lc["condition"] = fix_prose_math(lc["condition"])
            if "expected" in lc:
                lc["expected"] = fix_prose_math(lc["expected"])

        # 3. Clean distractor_diagnostics
        distractors = q.get("distractor_diagnostics", {})
        for opt_k, opt_d in distractors.items():
            if "diagnostic" in opt_d:
                opt_d["diagnostic"] = fix_prose_math(opt_d["diagnostic"])

        # 4. Clean progressive_hints
        for h in q.get("progressive_hints", []):
            if "prompt_question" in h:
                h["prompt_question"] = fix_prose_math(h["prompt_question"])
            if "reveal_text" in h:
                h["reveal_text"] = fix_prose_math(h["reveal_text"])

        # 5. Clean stem and options
        if "stem" in q:
            q["stem"] = fix_prose_math(q["stem"])
        options = q.get("options", {})
        for opt_k in options:
            options[opt_k] = fix_prose_math(options[opt_k])

    # Check dollar sign parity across all questions
    odd_count = 0
    for q in questions:
        qid = q["question_id"]
        s = json.dumps(q)
        c = s.count("$")
        if c % 2 != 0:
            print(f"[WARN] {qid} has odd dollar count: {c}")
            odd_count += 1

    if odd_count == 0:
        print("[OK] All 25 questions have 100% matched dollar parity!")

    with open(BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Successfully saved updated questions to {BANK_PATH}")

if __name__ == "__main__":
    main()
