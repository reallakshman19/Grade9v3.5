# scripts/clean_math_fields.py
import json
import re
from pathlib import Path

BANK_PATH = Path("TEST/physics-research/question_bank_kinematics_grade9.v1.json")
with open(BANK_PATH, "r", encoding="utf-8") as f:
    d = json.load(f)

for q in d["questions"]:
    # 1. Clean dimensional_formula
    df = q.get("independent_check", {}).get("dimensional_formula", "")
    if df:
        # Strip all $ from dimensional formula
        df_clean = df.replace("$", "").replace("\\$", "")
        # Clean up any leftover double slashes or broken tokens
        df_clean = re.sub(r'\s+', ' ', df_clean).strip()
        q["independent_check"]["dimensional_formula"] = df_clean

    # 2. Clean final_expression
    fe = q.get("model_proof", {}).get("final_expression", "")
    if fe:
        # Strip all $ from final_expression
        fe_clean = fe.replace("$", "").replace("\\$", "")
        fe_clean = re.sub(r'\s+', ' ', fe_clean).strip()
        q["model_proof"]["final_expression"] = fe_clean

with open(BANK_PATH, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("[OK] Cleaned dimensional_formula and final_expression across all 25 questions.")
