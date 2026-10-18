import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
bank_path = REPO_ROOT / "TEST/physics-research/question_bank_vectors_grade9.v1.json"

with open(bank_path, "r", encoding="utf-8") as f:
    bank = json.load(f)

print(f"Auditing {len(bank['questions'])} questions in {bank_path.name}...")

issues = []
for i, q in enumerate(bank["questions"]):
    qid = q["question_id"]
    proof = q.get("model_proof", {})
    final_expr = proof.get("final_expression", "")
    dim_formula = q.get("independent_check", {}).get("dimensional_homogeneity", {}).get("formula", "")
    
    if final_expr.startswith("$") and final_expr.endswith("$"):
        issues.append(f"{qid}: final_expression has wrapping $ ({final_expr})")
    if dim_formula.startswith("$") and dim_formula.endswith("$"):
        issues.append(f"{qid}: dimensional_homogeneity.formula has wrapping $ ({dim_formula})")

    stem = q.get("stem", "")
    if stem.count("$") % 2 != 0:
        issues.append(f"{qid}: stem has unbalanced $ ({stem.count('$')})")
        
    for step in ["step_1_understand", "step_2_represent", "step_3_connect", "step_4_execute", "step_5_conclude"]:
        val = proof.get(step, "")
        if val.count("$") % 2 != 0:
            issues.append(f"{qid}: proof.{step} has unbalanced $ ({val.count('$')})")

    for opt_k, opt_v in q.get("options", {}).items():
        if opt_v.count("$") % 2 != 0:
            issues.append(f"{qid}: options.{opt_k} has unbalanced $ ({opt_v.count('$')})")

    for h in q.get("progressive_hints", []):
        prompt = h.get("prompt", "")
        reveal = h.get("reveal", "")
        if prompt.count("$") % 2 != 0:
            issues.append(f"{qid}: hint prompt has unbalanced $ ({prompt.count('$')})")
        if reveal.count("$") % 2 != 0:
            issues.append(f"{qid}: hint reveal has unbalanced $ ({reveal.count('$')})")

if not issues:
    print("ALL 25 QUESTIONS HAVE PERFECT LATEX DOLLAR PARITY AND CLEAN DISPLAY FORMULAS!")
else:
    print(f"Found {len(issues)} issues:")
    for iss in issues:
        print("  -", iss)
